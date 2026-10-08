"""The train and eval split, and the leakage audit over it.

The split is the datasets' own: training episodes come from their train
files and evaluation episodes from their validation files. That is the
control that actually holds, because the dataset authors kept the two apart
at the document level and not only at the question level.

This module is the audit on top of it. Every question carries a content
hash over its normalised text and its normalised answer, so two questions
that differ only in punctuation or casing collide. The check counts hashes
present on both sides and names them. It also counts documents shared
across the split, which is a weaker signal: a Wikipedia paragraph appearing
in both a training bundle and an evaluation bundle is normal for a
Wikipedia-derived corpus and is not leakage of the answer, but the count
belongs in the record rather than out of it.

The evaluation set itself is written here as a seeded sample of the
validation file rather than its head. The validation files arrive in dataset
order, which is not random, and reading the first N lines of an ordered file
has twice produced a wrong number on this project.
"""

from __future__ import annotations

import argparse
import json
import os
import random

from src.realret.sources import norm


def hashes(path: str) -> dict:
    out: dict = {}
    with open(path) as fh:
        for n, line in enumerate(fh):
            ep = json.loads(line)
            out.setdefault(ep["hash"], []).append((path, n, ep.get("qid")))
    return out


def doc_keys(path: str, stride: int = 1) -> set:
    keys = set()
    with open(path) as fh:
        for n, line in enumerate(fh):
            if n % stride:
                continue
            ep = json.loads(line)
            for d in ep["documents"]:
                keys.add(norm(d["text"])[:160])
    return keys


def cmd_sample(args) -> int:
    """Write the evaluation episodes as a seeded sample of a validation file.

    A sample over the whole file, not its head. The validation files arrive
    in dataset order, which is not random, and reading the first N lines of
    an ordered file has twice produced a wrong number on this project.
    """
    total = sum(1 for _ in open(args.episodes))
    keep = (set(range(total)) if args.take >= total
            else set(random.Random(args.seed).sample(range(total), args.take)))
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    kept = 0
    with open(args.episodes) as fh, open(args.out, "w") as sink:
        for n, line in enumerate(fh):
            if n not in keep:
                continue
            sink.write(line)
            kept += 1
    summary = {"in": args.episodes, "lines": total, "seed": args.seed,
               "take": args.take, "kept": kept, "out": os.path.abspath(args.out)}
    with open(args.out + ".summary.json", "w") as fh:
        json.dump(summary, fh, indent=1)
    print(json.dumps(summary), flush=True)
    return 0


def cmd_check(args) -> int:
    res = {"pairs": {}}
    for pair in args.pairs:
        train, evalp = pair.split(",", 1)
        th = hashes(train)
        eh = hashes(evalp)
        shared = sorted(set(th) & set(eh))
        tdocs = doc_keys(train, args.doc_stride)
        edocs = doc_keys(evalp, 1)
        res["pairs"][f"{os.path.basename(train)}|{os.path.basename(evalp)}"] = {
            "train_episodes": sum(len(v) for v in th.values()),
            "eval_episodes": sum(len(v) for v in eh.values()),
            "train_distinct_hashes": len(th),
            "eval_distinct_hashes": len(eh),
            "shared_hashes": len(shared),
            "shared_fraction_of_eval": round(len(shared) / max(1, len(eh)), 6),
            "shared_examples": [
                {"hash": h, "train": th[h][:2], "eval": eh[h][:2]}
                for h in shared[:20]],
            "train_doc_keys_sampled": len(tdocs),
            "train_doc_stride": args.doc_stride,
            "eval_doc_keys": len(edocs),
            "shared_doc_keys": len(tdocs & edocs),
            "shared_doc_fraction_of_eval": round(
                len(tdocs & edocs) / max(1, len(edocs)), 6),
        }
        print(json.dumps({pair: res["pairs"][
            f"{os.path.basename(train)}|{os.path.basename(evalp)}"]},
            indent=1)[:1500], flush=True)
    with open(args.out, "w") as fh:
        json.dump(res, fh, indent=1)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sample")
    s.add_argument("--episodes", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("--take", type=int, required=True)
    s.add_argument("--seed", type=int, default=8412)
    s.set_defaults(fn=cmd_sample)
    c = sub.add_parser("check")
    c.add_argument("--pairs", nargs="+", required=True,
                   help="train.jsonl,eval.jsonl per source")
    c.add_argument("--out", required=True)
    c.add_argument("--doc-stride", type=int, default=5)
    c.set_defaults(fn=cmd_check)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
