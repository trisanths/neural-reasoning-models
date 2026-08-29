"""Check 7 on the currently shipped checkpoint.

The re-wording collapse in AUDIT_SEMANTICS.md was measured on `runs/opgraph.pt`,
the checkpoint the audited table came from. The shipped report is built from
`runs/opgraph2.pt`, which reads the associativity sentence and scores better
under the shipped paraphrase. So the question the audit leaves open is whether
the second checkpoint also loses the page when the prose is re-rendered.

Same worlds, same seeds, same operators, same questions, same gold plans, same
gold answers as check 7. Only the checkpoint moves.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.expanduser("~/opg"))

import torch  # noqa: E402

from src.audit.run78 import (DEPTHS, SURFACE_TAGS, build,  # noqa: E402
                             induction_stats, planned_values, record)
from src.opgraph.run import Generator, induce_worlds, load_model  # noqa: E402
from src.train.tokenizer import load_tokenizer  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="runs/opgraph2.pt")
    ap.add_argument("--tokenizer", default="/home/ec2-user/data/tokenizer_v2.json")
    ap.add_argument("--out", default="results/verify_c7_opgraph2.json")
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--batch-size", type=int, default=24)
    args = ap.parse_args()

    tok = load_tokenizer(args.tokenizer)
    sets, golds, drop, base, _ = build(args.n)
    model, _ = load_model(args.ckpt)
    gen = Generator(model, tok, batch_size=args.batch_size)

    res: dict = {"ckpt": args.ckpt, "dropped": drop}
    for tag in SURFACE_TAGS:
        worlds = {it.world.seed: it.world
                  for d in DEPTHS for it in sets[(tag, d)]}
        induced = induce_worlds(gen, worlds)
        res.setdefault("induction", {})[tag] = induction_stats(
            induced, list(worlds.values()))
        print(f"[induction {tag}]", json.dumps(res["induction"][tag]), flush=True)
        for d in DEPTHS:
            items = sets[(tag, d)]
            gp, gt = golds[(tag, d)]
            for name, gplan in (("plan_execute", False), ("oracle_plan", True)):
                vals, _texts, _why = planned_values(gen, items, induced, gplan, False)
                record(res, name, tag, d, vals, gp, gt)
        with open(args.out, "w") as fh:
            json.dump(res, fh, indent=1)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
