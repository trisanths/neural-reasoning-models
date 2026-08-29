"""CPU analysis of the dumped induced operators.

For every wording and for the transposition, this answers three questions about
the binary operator the sequential question needs:

  was a parseable operator produced for that symbol at all
  does its body agree with the page in front of it
  does its body agree with the identity the operator had during training

and, for the transposition, whether the induced operator carries the page's own
worked-example lines while contradicting them.
"""

from __future__ import annotations

import json
import sys
from collections import Counter

from src.audit.surfaces import transpose_world
from src.opgraph.data import eval_worlds
from src.opgraph.opdef import OpError, parse_operator

PROBES = [(7, 4), (12, 5), (3, 9), (11, 2), (2, 11), (0, 6), (5, 1), (1, 5)]


def _vals(op):
    out = []
    for a in PROBES:
        try:
            out.append(op(*a))
        except OpError:
            out.append("__err__")
    return out


def main() -> int:
    dump = json.load(open(sys.argv[1]))
    base = eval_worlds("sequential", 150, breadth=3, style=0)
    train_ops = {}
    for w in base:
        for p in w.pages:
            if p.key.startswith("binop:"):
                train_ops[(str(w.seed), p.ops[0].symbol)] = p.ops[0]
    out = {}
    for tag, worlds in dump.items():
        c = Counter()
        for seed, rec in worlds.items():
            for sym, gtext in rec["gold_binops"].items():
                c["symbols"] += 1
                gold = parse_operator(gtext)
                itext = rec["induced"].get(sym)
                if itext is None:
                    c["absent"] += 1
                    continue
                c["present"] += 1
                got = parse_operator(itext)
                vg, vp = _vals(got), _vals(gold)
                if vg == vp:
                    c["body_matches_page"] += 1
                else:
                    c["body_wrong"] += 1
                if got.assoc == gold.assoc:
                    c["assoc_matches_page"] += 1
                elif got.assoc is None:
                    c["assoc_missing"] += 1
                tr = train_ops.get((seed, sym))
                if tr is not None and tag == "perm":
                    vt = _vals(tr)
                    if vt == vp:
                        c["indistinguishable"] += 1
                    elif vg == vt:
                        c["body_matches_training"] += 1
                # does the induced operator copy the page's worked examples?
                if got.examples and got.examples == gold.examples:
                    c["examples_copied"] += 1
                    ok = all(_safe(got, a) == r for a, r in got.examples)
                    c["examples_copied_and_body_agrees" if ok
                      else "examples_copied_and_body_contradicts"] += 1
        out[tag] = dict(c)
        print(tag, json.dumps(dict(c)), flush=True)
    with open(sys.argv[2], "w") as fh:
        json.dump(out, fh, indent=1)
    return 0


def _safe(op, args):
    try:
        return op(*args)
    except OpError:
        return "__err__"


if __name__ == "__main__":
    raise SystemExit(main())
