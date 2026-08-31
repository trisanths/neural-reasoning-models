"""System A: the RL checkpoint, through the gated harness.

The prompt is the world header, then the question, exactly as
`src/primitives/framecheck.py:make_trained_answer_fn` builds it, which is
`src/rl/env.py:build_prompt` with no in-context documents. Pages reach the
model only through retrieval, which is the condition it was trained in.
`src/evals/interactive.py:generate_with_retrieval` serves them. Without the
header this checkpoint issues no retrieval rounds at all, so the header is not
optional here, and `hdr.py` records what four different domain strings in that
header are worth.

`generate_with_retrieval` decodes greedily and nothing in it is configurable.
The sampled companion therefore leaves that loop untouched and sharpens the
step function instead: the wrapper samples from the real logits at the given
temperature and returns a vector whose argmax is the sampled token, so the
loop's own retrieval handling, stop conditions and trace are the same code
running over a sampled trajectory.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import time

import numpy as np

CKPT = "/home/ec2-user/rlckpt/rlsimple-503-921-final.pt"
TOK = "/home/ec2-user/data/tokenizer_v2.json"
DOMAIN = "skill_exception_rule"


def load_items(path, cap_per_cell=0):
    rows = []
    seen = {}
    with gzip.open(path, "rt") as fh:
        for line in fh:
            r = json.loads(line)
            k = (r["split"], r["shape"])
            seen[k] = seen.get(k, 0) + 1
            if cap_per_cell and seen[k] > cap_per_cell:
                continue
            rows.append(r)
    return rows


def sampled_step(step_fn, temperature: float, top_k: int, seed: int):
    rng = np.random.default_rng(seed)

    def step(token_ids):
        lg = np.asarray(step_fn(token_ids), dtype=np.float64)
        z = lg / max(temperature, 1e-6)
        if top_k and top_k < z.size:
            cut = np.partition(z, -top_k)[-top_k]
            z = np.where(z >= cut, z, -np.inf)
        z = z - z.max()
        p = np.exp(z)
        p = p / p.sum()
        pick = int(rng.choice(z.size, p=p))
        out = np.full(z.size, -1e9, dtype=np.float64)
        out[pick] = 0.0
        return out

    return step


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", default="results/norm/compare/items.jsonl.gz")
    ap.add_argument("--out", default="")
    ap.add_argument("--mode", default="greedy", choices=("greedy", "sampled"))
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--top-k", type=int, default=50)
    ap.add_argument("--cap", type=int, default=0)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--max-new-tokens", type=int, default=256)
    ap.add_argument("--max-rounds", type=int, default=6)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args()

    from src.evals.interactive import (generate_with_retrieval,
                                       make_checkpoint_step_fn)
    from src.train.data import render_world_preamble
    from src.train.tokenizer import load_tokenizer

    out = a.out or f"results/norm/compare/a_{a.mode}.jsonl.gz"
    items = load_items(a.items, a.cap)
    if a.limit:
        items = items[:a.limit]

    tok = load_tokenizer(TOK)
    raw_step, _model, state = make_checkpoint_step_fn(CKPT, a.device)
    step = raw_step if a.mode == "greedy" else sampled_step(
        raw_step, a.temperature, a.top_k, a.seed)
    sid = tok.special_ids
    head = [sid["<|world|>"],
            *tok.encode(render_world_preamble({"domain": DOMAIN}))]

    os.makedirs(os.path.dirname(out), exist_ok=True)
    t0 = time.time()
    rounds = []
    with gzip.open(out, "wt") as fh:
        for k, it in enumerate(items, 1):
            chunks = [{"text": p, "reliability": 1.0} for p in it["pages"]]
            prompt = head + [sid["<|q|>"], *tok.encode(it["question"])]
            r = generate_with_retrieval(step, tok, chunks, prompt,
                                        max_rounds=a.max_rounds,
                                        max_new_tokens=a.max_new_tokens,
                                        seed=a.seed)
            rounds.append(r["n_rounds"])
            fh.write(json.dumps({
                "id": it["id"], "split": it["split"], "shape": it["shape"],
                "fid": it["fid"], "gold": it["gold"], "options": it["options"],
                "raw": r["answer_text"], "rounds": r["n_rounds"],
                "stop": r["stop_reason"], "n_generated": r["n_generated"]}) + "\n")
            if k % 100 == 0:
                el = time.time() - t0
                print(f"{k}/{len(items)} {el:.0f}s {el/k:.2f}s/item "
                      f"rounds={sum(rounds)/len(rounds):.2f}", flush=True)
    el = time.time() - t0
    meta = {"n": len(items), "mode": a.mode, "temperature": a.temperature,
            "top_k": a.top_k, "seed": a.seed, "domain": DOMAIN,
            "max_new_tokens": a.max_new_tokens, "max_rounds": a.max_rounds,
            "seconds": round(el, 1), "per_item": round(el / max(len(items), 1), 3),
            "mean_rounds": round(sum(rounds) / max(len(rounds), 1), 3),
            "ckpt": CKPT, "step": int(state.get("step", -1)), "out": out}
    with open(out.replace(".jsonl.gz", ".meta.json"), "w") as fh:
        json.dump(meta, fh, indent=2)
    print(json.dumps(meta))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
