"""Render real-document episodes into the training pack layout.

The pack is the one `src/corpus/sft.py` writes and reads: three flat arrays
and one index line per example. Writing the same layout means the mixing and
the training pass are that module's audited code with no change, and the
only thing this file decides is what goes in an example.

The example is the trace the environment writes for a correct rollout, the
shape `src/rl/env.py` replays at evaluation time:

    <|world|> preamble <|q|> question
    [ <|retrieve|> query <|result|> page ] x rounds
    <|a|> answer <|eot|>

The prompt comes from `src/rl/env.py:build_prompt`, so the world header is
there. Without it this checkpoint issues no retrieval round, emits no answer
marker and runs to the token cap, which has cost this project two results.

Loss falls on the markers, the query and the answer. The served page carries
none, which is how `src/rl/grpo.py` masks it and how the corpus pack is
built. Two loss terms normalised separately, so a long page cannot change
how hard the answer is trained.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import time

import numpy as np


def pick(total: int, want: int, seed: int) -> set:
    """Which line numbers a quota of `want` out of `total` takes.

    A seeded sample over the whole range, not a stride and not a prefix. A
    stride of one degenerates to reading the head of the file, which is
    exactly the mistake that has produced two wrong numbers on this project,
    and it degenerates silently whenever the quota is more than half the file.
    """
    if want >= total:
        return set(range(total))
    return set(random.Random(seed).sample(range(total), want))


class Pack:
    """Three flat arrays and one index line per example.

    Byte-for-byte the layout `src/corpus/sft.py:Pack` writes, so a pack from
    here and a pack from there merge and train through that module unchanged.
    """

    def __init__(self, out_prefix: str):
        self.tok_f = open(out_prefix + ".tokens.u16", "wb")
        self.msk_f = open(out_prefix + ".mask.u8", "wb")
        self.amk_f = open(out_prefix + ".amask.u8", "wb")
        self.idx_f = open(out_prefix + ".index.jsonl", "w")
        self.offset = 0
        self.n = 0

    def add(self, tr: dict, meta: dict) -> None:
        t = np.asarray(tr["tokens"], dtype=np.uint16)
        self.tok_f.write(t.tobytes())
        self.msk_f.write(np.asarray(tr["mask"], dtype=np.uint8).tobytes())
        self.amk_f.write(np.asarray(tr["amask"], dtype=np.uint8).tobytes())
        row = {"off": self.offset, "len": int(t.size),
               "sup": int(sum(tr["mask"])), "ans": int(sum(tr["amask"])),
               "rounds": tr["rounds"], "served_gold": tr["served_gold"], **meta}
        self.idx_f.write(json.dumps(row) + "\n")
        self.offset += int(t.size)
        self.n += 1

    def close(self) -> dict:
        for f in (self.tok_f, self.msk_f, self.amk_f, self.idx_f):
            f.close()
        return {"n": self.n, "tokens": self.offset}


def episode_trace(ep: dict, q: dict, tok, max_prompt_tokens: int,
                  max_len: int):
    from src.rl.env import build_prompt

    sid = tok.special_ids
    prompt = build_prompt(ep, q, tok)
    if len(prompt) > max_prompt_tokens:
        return None, "prompt"
    texts = [d["text"] for d in ep["documents"]]
    tokens, mask, amask = list(prompt), [0] * len(prompt), [0] * len(prompt)
    for pair in q["plan"]:
        query, doc = pair[0], int(pair[1])
        qt = tok.encode(query)
        ct = tok.encode(texts[doc])
        tokens.append(sid["<|retrieve|>"]); mask.append(1); amask.append(0)
        tokens.extend(qt); mask.extend([1] * len(qt)); amask.extend([0] * len(qt))
        tokens.append(sid["<|result|>"]); mask.append(1); amask.append(0)
        tokens.extend(ct); mask.extend([0] * len(ct)); amask.extend([0] * len(ct))
    at = tok.encode(" " + str(q["answer"]))
    tokens.append(sid["<|a|>"]); mask.append(1); amask.append(1)
    tokens.extend(at); mask.extend([1] * len(at)); amask.extend([1] * len(at))
    tokens.append(sid["<|eot|>"]); mask.append(1); amask.append(1)
    if len(tokens) > max_len:
        return None, "length"
    return {"tokens": tokens, "mask": mask, "amask": amask,
            "rounds": len(q["plan"]), "served_gold": True}, "ok"


def cmd_build(args) -> int:
    from src.train.tokenizer import load_tokenizer

    tok = load_tokenizer(args.tokenizer)
    total = sum(1 for _ in open(args.episodes))
    want = args.take or total
    chosen = pick(total, want, args.seed)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    pack = Pack(args.out)
    drops = {"prompt": 0, "length": 0}
    kept = 0
    rounds_hist: dict = {}
    t0 = time.time()
    with open(args.episodes) as fh:
        for line_no, line in enumerate(fh):
            if line_no not in chosen:
                continue
            ep = json.loads(line)
            q = ep["questions"][0]
            tr, why = episode_trace(ep, q, tok, args.max_prompt_tokens,
                                    args.max_len)
            if tr is None:
                drops[why] += 1
                continue
            pack.add(tr, {"component": ep["source"], "source": ep["source"],
                          "qid": ep.get("qid"), "hash": ep.get("hash"),
                          "hops": ep.get("hops"), "kind": ep.get("kind"),
                          "level": ep.get("level"),
                          "yesno": ep.get("yesno", False),
                          "misses": ep.get("misses", 0), "line": line_no})
            kept += 1
            rounds_hist[tr["rounds"]] = rounds_hist.get(tr["rounds"], 0) + 1
            if kept and kept % 20000 == 0:
                print(f"{args.out}: {kept} kept, {time.time() - t0:.0f}s",
                      flush=True)
    stats = pack.close()
    summary = {"episodes": args.episodes, "total_lines": total,
               "selected": len(chosen), "seed": args.seed,
               "take": args.take, "kept": kept,
               "drops": drops, "tokens": stats["tokens"],
               "rounds_hist": {str(k): v for k, v in sorted(rounds_hist.items())},
               "mean_len": round(stats["tokens"] / max(1, kept), 1),
               "seconds": round(time.time() - t0, 1)}
    with open(args.out + ".summary.json", "w") as fh:
        json.dump(summary, fh, indent=1)
    print(json.dumps(summary), flush=True)
    return 0


def cmd_subsample(args) -> int:
    """A sample of an existing pack, written as a pack.

    `src/corpus/sft.py merge` takes whole packs, and the synthetic side of
    the mixture is half of one. The sample is drawn over the whole index
    rather than off its head, so the component proportions survive whatever
    order the source pack happens to be in.
    """
    toks = np.memmap(args.pack + ".tokens.u16", dtype=np.uint16, mode="r")
    msk = np.memmap(args.pack + ".mask.u8", dtype=np.uint8, mode="r")
    amk = np.memmap(args.pack + ".amask.u8", dtype=np.uint8, mode="r")
    index = [json.loads(l) for l in open(args.pack + ".index.jsonl")]
    chosen = sorted(pick(len(index), args.take, args.seed))
    out = Pack(args.out)
    counts: dict = {}
    for i in chosen:
        r = index[i]
        a, b = r["off"], r["off"] + r["len"]
        tr = {"tokens": toks[a:b].tolist(), "mask": msk[a:b].tolist(),
              "amask": amk[a:b].tolist(), "rounds": r.get("rounds", 0),
              "served_gold": r.get("served_gold", False)}
        meta = {k: v for k, v in r.items()
                if k not in ("off", "len", "sup", "ans", "rounds",
                             "served_gold")}
        out.add(tr, meta)
        counts[r.get("component")] = counts.get(r.get("component"), 0) + 1
    stats = out.close()
    summary = {"pack": args.pack, "source_n": len(index),
               "selected": len(chosen), "seed": args.seed,
               "take": args.take, "n": stats["n"], "tokens": stats["tokens"],
               "per_component": counts}
    with open(args.out + ".summary.json", "w") as fh:
        json.dump(summary, fh, indent=1)
    print(json.dumps(summary), flush=True)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("subsample")
    s.add_argument("--pack", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("--take", type=int, required=True)
    s.add_argument("--seed", type=int, default=5150)
    s.set_defaults(fn=cmd_subsample)
    b = sub.add_parser("build")
    b.add_argument("--episodes", required=True)
    b.add_argument("--out", required=True)
    b.add_argument("--tokenizer", default="/home/ec2-user/data/tokenizer_v2.json")
    b.add_argument("--take", type=int, default=0)
    b.add_argument("--seed", type=int, default=5150)
    b.add_argument("--max-prompt-tokens", type=int, default=384)
    b.add_argument("--max-len", type=int, default=1024)
    b.set_defaults(fn=cmd_build)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
