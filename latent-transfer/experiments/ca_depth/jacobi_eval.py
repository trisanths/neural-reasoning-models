"""Speculative cognition on the token arm, eval only.

The oo_tok trace is serial: k states x 21 tokens, one forward per token. Two ways to
buy back wall-clock without touching accuracy:

  JACOBI     initialise the whole k-step trace, run the model over it in ONE parallel pass,
             replace every position with its (type-constrained) argmax, repeat to a fixed
             point. For a causal model the fixed point is the greedy trajectory, so the
             only question is how many parallel passes it takes. passes / serial_length is
             the speedup ceiling and measures how parallelisable the reasoning is.

  DRAFT+VERIFY  draft the trace with a weaker checkpoint, verify with the strong one in a
             single teacher-forced pass, accept the prefix up to the first disagreement.
             Accepted fraction is speculative decoding's figure of merit, on reasoning steps.

Usage (from /home/ec2-user/ca):
  python jacobi_eval.py --ckpt results_v3/ropex40kfix_mixedk_oo_tok_s0.pt \
      --draft results_v3/ropex40k_mixedk_oo_tok_s1.pt --ks 1,2,4,8 --n 2000 --out results_v3/jacobi_s0.json
"""
import argparse, json, sys, time
import torch, torch.nn as nn, torch.nn.functional as F
sys.path.insert(0, ".")
from ca_arms import make_batch, encode_prior, build_models, W, T, SEP, VOCAB  # noqa: E402

dev = "cuda"

def load(path):
    st = torch.load(path, map_location=dev)
    GPT, VQ, RecCell, BitDecoder = build_models(torch, nn, F, pos=st.get("pos", "abs"), block=st.get("block", "seq"))
    g = GPT().to(dev); g.load_state_dict(st["gpt"]); g.eval()
    return g

def tied(g, h):
    return (g.wte.weight @ h.transpose(-1, -2)).transpose(-1, -2)

def constrain(logits, is_sep):
    # type-constrained argmax: bits over {0,1}; SEP forced at SEP slots
    b = logits[..., :2].argmax(-1)
    return torch.where(is_sep, torch.full_like(b, SEP), b)

@torch.no_grad()
def serial(g, ids, k):
    L = k * (W + 1); B = ids.shape[0]
    is_sep = (torch.arange(L, device=dev) % (W + 1)) == W
    h, past = g(ids); out = []
    nxt = constrain(tied(g, h[:, -1]), is_sep[0].expand(B))
    for j in range(L):
        out.append(nxt)
        if j < L - 1:
            h, past = g(nxt[:, None], past=past)
            nxt = constrain(tied(g, h[:, -1]), is_sep[j + 1].expand(B))
    return torch.stack(out, 1)                                        # (B, L)

@torch.no_grad()
def jacobi(g, ids, k, max_iters=None):
    L = k * (W + 1); B = ids.shape[0]; P = ids.shape[1]
    is_sep = ((torch.arange(L, device=dev) % (W + 1)) == W)[None].expand(B, L)
    x = torch.where(is_sep, torch.full((B, L), SEP, device=dev), torch.zeros(B, L, dtype=torch.long, device=dev))
    conv_iter = torch.full((B,), -1, device=dev)
    last_changed = torch.zeros((B,), dtype=torch.long, device=dev)   # last pass at which the final state changed
    prev_last = x[:, -(W + 1):-1].clone()
    it = 0; cap = max_iters or L + 1
    while it < cap:
        full = torch.cat([ids, x], 1)
        h, _ = g(full[:, :-1])
        new = constrain(tied(g, h[:, P - 1:]), is_sep)                 # (B, L) predictions for x
        same = (new == x).all(-1)
        conv_iter = torch.where((conv_iter < 0) & same, torch.full_like(conv_iter, it), conv_iter)
        cur_last = new[:, -(W + 1):-1]
        changed = (cur_last != prev_last).any(-1)
        last_changed = torch.where(changed, torch.full_like(last_changed, it + 1), last_changed)
        prev_last = cur_last.clone()
        x = new; it += 1
        if bool(same.all()):
            break
    conv_iter = torch.where(conv_iter < 0, torch.full_like(conv_iter, it), conv_iter)
    # passes needed for the FINAL state to reach its final value (>= 1)
    return x, conv_iter, last_changed.clamp(min=1)

@torch.no_grad()
def verify(g, ids, draft, k):
    # one teacher-forced pass of the verifier over the draft; accepted prefix = tokens before first disagreement
    L = k * (W + 1); B = ids.shape[0]; P = ids.shape[1]
    is_sep = ((torch.arange(L, device=dev) % (W + 1)) == W)[None].expand(B, L)
    full = torch.cat([ids, draft], 1)
    h, _ = g(full[:, :-1])
    pred = constrain(tied(g, h[:, P - 1:]), is_sep)
    mism = (pred != draft)
    first = torch.where(mism.any(-1), mism.float().argmax(-1), torch.full((B,), L, device=dev))
    return first                                                     # accepted tokens per row

def final_state(trace, k):
    return trace.view(trace.shape[0], k, W + 1)[:, -1, :W]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True); ap.add_argument("--draft", default="")
    ap.add_argument("--ks", default="1,2,4,8"); ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--chunk", type=int, default=250); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    g = load(a.ckpt); gd = load(a.draft) if a.draft else None
    gen = torch.Generator(device=dev); gen.manual_seed(a.seed)
    res = {"ckpt": a.ckpt, "draft": a.draft, "n": a.n, "per_k": {}}
    for k in [int(x) for x in a.ks.split(",")]:
        L = k * (W + 1); t0 = time.time()
        acc_ser = acc_jac = agree = 0; iters = []; last_iters = []; acc_tok = []; acc_states = []
        done = 0
        while done < a.n:
            m = min(a.chunk, a.n - done)
            prior, target, _ = make_batch(m, k, "test", gen, torch, dev)
            ids = encode_prior(prior, torch); gold = target[:, -1]
            s = serial(g, ids, k)
            j, ci, lsi = jacobi(g, ids, k)
            acc_ser += (final_state(s, k) == gold).all(-1).float().sum().item()
            acc_jac += (final_state(j, k) == gold).all(-1).float().sum().item()
            agree += (s == j).all(-1).float().sum().item()
            iters += ci.tolist(); last_iters += lsi.tolist()
            if gd is not None:
                d = serial(gd, ids, k)
                first = verify(g, ids, d, k)
                acc_tok += (first.float() / L).tolist(); acc_states += (first // (W + 1)).tolist()
            done += m
        import statistics as S
        row = {"L": L, "serial_exact": acc_ser / a.n, "jacobi_exact": acc_jac / a.n, "jacobi_agrees_with_serial": agree / a.n,
               "jacobi_iters_mean": S.mean(iters), "jacobi_iters_median": S.median(iters),
               "jacobi_iters_p90": sorted(iters)[int(0.9 * len(iters)) - 1],
               "final_state_settled_pass_mean": S.mean(last_iters),
               "speedup_ceiling_full": L / S.mean(iters), "speedup_ceiling_finalstate": L / max(S.mean(last_iters), 1e-9),
               "sec": time.time() - t0}
        if gd is not None:
            row.update({"draft_accepted_frac_mean": S.mean(acc_tok), "draft_accepted_states_mean": S.mean(acc_states),
                        "draft_accepted_states_median": S.median(acc_states)})
        res["per_k"][k] = row
        print(f"k={k} L={L}: serial={row['serial_exact']:.3f} jacobi={row['jacobi_exact']:.3f} agree={row['jacobi_agrees_with_serial']:.3f} "
              f"iters mean/med/p90={row['jacobi_iters_mean']:.1f}/{row['jacobi_iters_median']:.0f}/{row['jacobi_iters_p90']} "
              f"final_settled={row['final_state_settled_pass_mean']:.1f} ceiling={row['speedup_ceiling_full']:.1f}x/{row['speedup_ceiling_finalstate']:.1f}x"
              + (f" | draft accepted {row['draft_accepted_frac_mean']:.2f} of trace, {row['draft_accepted_states_mean']:.2f} states" if gd else ""), flush=True)
    json.dump(res, open(a.out, "w"), indent=1)

if __name__ == "__main__":
    main()
