"""The project's own checkpoints on the public benchmarks.

The prompts are built by `src/extern/bench.py`, the same strings the Liquid
models are scored on, so the only thing that differs between the two sides of
a row is the model and its tokenizer. Scoring is the same log likelihood over
the candidate continuations, so a model that cannot produce an answer format
is not penalised for it: the question is only which candidate it prefers.

These checkpoints have no chat template, which is not a gap in the harness. A
base language model is scored in the completion format and that is the format
published numbers for base models come from.
"""
from __future__ import annotations

import argparse
import json
import os
import time

import torch

from src.extern.bench import TASKS, build_mc


class OursTokShim:
    """Enough of the HF tokenizer surface for `build_mc` to run."""

    def __init__(self, tok):
        self.tok = tok
        self.pad_token_id = 0

    def __call__(self, text, add_special_tokens=False):
        return {"input_ids": self.tok.encode(text)}

    def apply_chat_template(self, *a, **k):
        raise RuntimeError("these checkpoints have no chat template")


@torch.no_grad()
def score_item(model, tok, pairs, device, max_seq):
    """Sum log probability of each candidate continuation."""
    out = []
    ctx_cache = {}
    for ctx, cont in pairs:
        if ctx not in ctx_cache:
            ctx_cache[ctx] = tok.encode(ctx)
        a = ctx_cache[ctx]
        full = a + tok.encode(cont)
        if len(full) > max_seq:
            full = full[-max_seq:]
            a = a[-(max_seq - (len(full) - len(a))):]
        idx = torch.tensor([full], dtype=torch.long, device=device)
        logits = model(idx)[0].float()
        lp = torch.log_softmax(logits[0], dim=-1)
        n_cont = len(full) - len(a)
        tot = 0.0
        for t in range(n_cont):
            pos = len(full) - n_cont + t - 1
            tot += float(lp[pos, full[len(a) + t]])
        out.append((tot, n_cont))
    return out


@torch.no_grad()
def score_item_fast(model, tok, pairs, device, max_seq):
    """One forward when the candidates are one token over a shared context."""
    ctxs = {p[0] for p in pairs}
    if len(ctxs) != 1:
        return None
    ids = [tok.encode(p[1]) for p in pairs]
    if any(len(i) != 1 for i in ids):
        return None
    a = tok.encode(pairs[0][0])[-max_seq:]
    idx = torch.tensor([a], dtype=torch.long, device=device)
    lp = torch.log_softmax(model(idx)[0].float()[0, -1], dim=-1)
    return [(float(lp[i[0]]), 1) for i in ids]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--task", required=True, choices=list(TASKS))
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--root", default="data/extern")
    ap.add_argument("--tokenizer", default="/home/ec2-user/data/tokenizer_v2.json")
    ap.add_argument("--out", required=True)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--no-fast-path", action="store_true")
    a = ap.parse_args()

    from src.evals.mc import load_checkpoint_model
    from src.train.tokenizer import load_tokenizer

    tok = load_tokenizer(a.tokenizer)
    shim = OursTokShim(tok)
    model, state = load_checkpoint_model(a.ckpt, a.device)
    max_seq = model.cfg.max_seq_len
    n_params = sum(p.numel() for p in model.parameters())

    rows = TASKS[a.task](a.root, a.n, a.seed)
    t0 = time.time()
    recs, too_long = [], 0
    for k, row in enumerate(rows):
        pairs, kind = build_mc(row, a.task, "completion", shim)
        if len(tok.encode(pairs[0][0])) > max_seq:
            too_long += 1
        sc = None
        if kind == "letter" and not a.no_fast_path:
            sc = score_item_fast(model, tok, pairs, a.device, max_seq)
        if sc is None:
            sc = score_item(model, tok, pairs, a.device, max_seq)
        raw = [s for s, _ in sc]
        norm = [s / max(n, 1) for s, n in sc]
        recs.append({"id": row["id"], "subject": row["subject"],
                     "gold": row["gold"], "n_choices": len(pairs),
                     "pred": int(max(range(len(raw)), key=lambda i: raw[i])),
                     "pred_norm": int(max(range(len(norm)),
                                          key=lambda i: norm[i])),
                     "logp": raw})
        if (k + 1) % 25 == 0:
            el = time.time() - t0
            print(f"{k+1}/{len(rows)} {el:.0f}s "
                  f"eta {el/(k+1)*(len(rows)-k-1):.0f}s", flush=True)

    n = len(recs)
    res = {"model": f"ours:{a.tag}", "ckpt": os.path.abspath(a.ckpt),
           "task": a.task, "fmt": "completion", "n": n, "seed": a.seed,
           "params_total": n_params, "max_seq_len": max_seq,
           "prompts_over_context": too_long,
           "cfg": state["config"]["model"],
           "acc": round(sum(r["pred"] == r["gold"] for r in recs) / n, 4),
           "acc_norm": round(sum(r["pred_norm"] == r["gold"]
                                 for r in recs) / n, 4),
           "floor": round(sum(1.0 / r["n_choices"] for r in recs) / n, 4),
           "shots": 5 if a.task == "mmlu" else 0,
           "seconds": round(time.time() - t0, 1), "records": recs}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "records"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
