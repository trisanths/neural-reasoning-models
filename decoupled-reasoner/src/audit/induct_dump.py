"""What the induction step actually writes, next to the operator the page means.

The depth curve is read as "the model induces operators from pages", so it is
worth printing a few of them. The comparison is the one the package itself uses:
`_same_text` and `_same_behaviour` from src.opgraph.run, both of which require
the associativity to agree, and a body-only comparison added here so the two can
be told apart.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter

import torch

sys.path.insert(0, os.path.expanduser("~/opg"))

from src.opgraph.data import eval_worlds, induce_prompt  # noqa: E402
from src.opgraph.opdef import (OpError, parse_operators, serialize,  # noqa: E402
                               serialize_expr)
from src.opgraph.plan import signature_line  # noqa: E402
from src.opgraph.run import Generator, load_model  # noqa: E402
from src.train.tokenizer import load_tokenizer  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="runs/opgraph.pt")
    ap.add_argument("--tokenizer", default="/home/ec2-user/data/tokenizer_v2.json")
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--out", default="results/audit_induction.json")
    args = ap.parse_args()

    tok = load_tokenizer(args.tokenizer)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, _ = load_model(args.ckpt, device)
    gen = Generator(model, tok, device, batch_size=32)

    worlds = eval_worlds("sequential", args.n, breadth=3)
    jobs = []
    for w in worlds:
        for p in w.shuffled_pages():
            if p.key.startswith("binop:"):
                jobs.append((w, p))
    outs = gen.generate([induce_prompt(p.text) for _, p in jobs], max_new=288)

    stats = Counter()
    samples = []
    sig_rows = []
    for (w, p), text in zip(jobs, outs):
        gold = p.ops[0]
        stats["pages"] += 1
        try:
            got = parse_operators(text)[0]
        except (OpError, IndexError):
            stats["unparseable"] += 1
            continue
        stats["parsed"] += 1
        body_same = serialize_expr(got.body) == serialize_expr(gold.body)
        stats["body_exact"] += int(body_same)
        stats["assoc_present"] += int(got.assoc is not None)
        stats["assoc_correct"] += int(got.assoc == gold.assoc)
        stats["params_same"] += int(got.params == gold.params)
        stats["full_exact"] += int(body_same and got.assoc == gold.assoc
                                   and got.params == gold.params)
        if len(samples) < 6:
            samples.append({"page_assoc": gold.assoc,
                            "gold_op": serialize(gold),
                            "induced_op": serialize(got),
                            "raw": text[:400]})
        if len(sig_rows) < 6:
            sig_rows.append({
                "gold_signature": signature_line({gold.symbol: gold}),
                "induced_signature": signature_line({got.symbol: got})})

    print(json.dumps(dict(stats), indent=1))
    for s in samples[:3]:
        print("\npage says assoc:", s["page_assoc"])
        print("  gold:   ", s["gold_op"][:220])
        print("  induced:", s["induced_op"][:220])
    print("\nsignature lines the planner is shown:")
    for s in sig_rows[:3]:
        print("  gold ops:   ", s["gold_signature"])
        print("  induced ops:", s["induced_signature"])
    with open(args.out, "w") as fh:
        json.dump({"ckpt": args.ckpt, "stats": dict(stats),
                   "samples": samples, "signatures": sig_rows}, fh, indent=1)
    print(f"\n[written] {args.out}")


if __name__ == "__main__":
    main()
