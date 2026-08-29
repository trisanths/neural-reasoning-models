"""CPU only: the parser baseline on every wording, every depth, and the swap."""

from __future__ import annotations

import json
import sys
from collections import Counter

from src.audit import pageparser
from src.audit.surfaces import restyle_world, transpose_world
from src.opgraph.data import eval_worlds, make_item
from src.opgraph.invent import copyable
from src.opgraph.plan import answer_text, run_plan

DEPTHS = [1, 2, 3, 4, 5, 6, 7, 8]
N = 150


def main() -> int:
    base = eval_worlds("sequential", N, breadth=3, style=0)
    out: dict = {"n": N, "depths": DEPTHS}
    for tag, style in (("s0", 0), ("s2", 2), ("s3", 3), ("s4", 4)):
        worlds = [restyle_world(w, style) for w in base]
        for name, styles in (("parser_all_wordings", (0, 2, 3, 4)),
                             ("parser_trained_wording", (0,))):
            for d in DEPTHS:
                items = [make_item("sequential", w, d, i)
                         for i, w in enumerate(worlds)]
                ok, refused = pageparser.score(items, styles)
                out.setdefault(name, {}).setdefault(tag, {})[str(d)] = {
                    "n": len(ok), "acc": round(sum(ok) / len(ok), 4),
                    "refused": refused}
                print(f"[{name}] {tag} d={d} acc={sum(ok) / len(ok):.3f} "
                      f"refused={refused}", flush=True)

    # the operand swap, read by the same parser
    tworlds = [transpose_world(w) for w in base]
    for d in DEPTHS:
        ctrl = [make_item("sequential", w, d, i) for i, w in enumerate(base)]
        n_page = n_train = kept = 0
        drop = Counter()
        for it, tw in zip(ctrl, tworlds):
            page_gold = answer_text(run_plan(it.plan, tw.ops))
            if page_gold == it.gold:
                drop["indistinguishable"] += 1
                continue
            if copyable(page_gold, it.text):
                drop["copyable"] += 1
                continue
            kept += 1
            try:
                got = pageparser.answer(tw.context(), it.text, (0,))
            except Exception:
                got = ""
            n_page += got == page_gold
            n_train += got == it.gold
        out.setdefault("parser_transposed", {})[str(d)] = {
            "n": kept, "acc_page": round(n_page / kept, 4),
            "acc_train": round(n_train / kept, 4), "dropped": dict(drop)}
        print(f"[parser_transposed] d={d} page={n_page / kept:.3f} "
              f"train={n_train / kept:.3f} n={kept} dropped={dict(drop)}",
              flush=True)

    with open(sys.argv[1] if len(sys.argv) > 1 else "results/audit_parser.json",
              "w") as fh:
        json.dump(out, fh, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
