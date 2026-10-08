"""Is A's zero a harness artefact or the checkpoint's behaviour.

Three conditions on the same items: retrieval with the world header (the gated
path), the same with the pages already in context as documents, and the same
again with an answer marker forced so the model cannot spend its budget
elsewhere. Split by question form, because the checkpoint trained on one.
"""
from __future__ import annotations
import collections, json, torch
from src.evals.interactive import make_checkpoint_step_fn, generate_with_retrieval
from src.train.data import render_world_preamble
from src.train.tokenizer import load_tokenizer
from src.norm.cmpwork.runa import CKPT, TOK, load_items
from src.norm.cmpwork.grade import forced

SHAPES = ("lookup", "lookup_general", "classify")


def qform(fid):
    return fid.split(".")[3]


def main():
    items = [it for it in load_items("results/norm/compare/items.jsonl.gz", 0)
             if it["shape"] in SHAPES and it["split"] == "train"]
    by = collections.defaultdict(list)
    for it in items:
        by[qform(it["fid"])].append(it)
    probe = {k: v[:16] for k, v in by.items()}
    print("qforms:", {k: len(v) for k, v in probe.items()})

    tok = load_tokenizer(TOK)
    step_fn, model, _s = make_checkpoint_step_fn(CKPT, "cuda")
    sid = tok.special_ids
    head = [sid["<|world|>"], *tok.encode(render_world_preamble({"domain": "skill_exception_rule"}))]

    def greedy_plain(ids, n=32):
        out = []
        cur = list(ids)
        for _ in range(n):
            x = torch.tensor([cur[-model.cfg.max_seq_len:]], dtype=torch.long, device="cuda")
            with torch.no_grad():
                lg, _ = model(x)
            t = int(lg[0, -1].argmax())
            if t in set(sid.values()):
                break
            out.append(t); cur.append(t)
        return tok.decode(out)

    rep = {}
    for qf, ps in sorted(probe.items()):
        cells = {}
        for cond in ("retrieval", "in_context", "in_context_forced_a"):
            rounds = hit = none = 0
            for it in ps:
                chunks = [{"text": p, "reliability": 1.0} for p in it["pages"]]
                if cond == "retrieval":
                    prompt = head + [sid["<|q|>"], *tok.encode(it["question"])]
                    r = generate_with_retrieval(step_fn, tok, chunks, prompt,
                                                max_rounds=6, max_new_tokens=256, seed=0)
                    ans, nr = r["answer_text"], r["n_rounds"]
                else:
                    body = []
                    for p in it["pages"]:
                        body += [sid["<|doc|>"], *tok.encode(p)]
                    prompt = head + body + [sid["<|q|>"], *tok.encode(it["question"])]
                    if cond == "in_context_forced_a":
                        prompt = prompt + [sid["<|a|>"]]
                        ans, nr = greedy_plain(prompt), 0
                    else:
                        r = generate_with_retrieval(step_fn, tok, chunks, prompt,
                                                    max_rounds=6, max_new_tokens=256, seed=0)
                        ans, nr = r["answer_text"], r["n_rounds"]
                g = forced(ans, it["options"], it["gold"])
                rounds += nr; hit += g["strict_correct"]; none += g["named_none"]
            n = len(ps)
            cells[cond] = {"n": n, "rounds": round(rounds / n, 2),
                           "strict": round(hit / n, 4), "none": round(none / n, 4)}
        rep[qf] = cells
        print(qf, json.dumps(cells), flush=True)
    with open("results/norm/compare/a_diagnostic.json", "w") as fh:
        json.dump(rep, fh, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
