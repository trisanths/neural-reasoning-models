"""The step 3 tables: accuracy by contamination cell, never pooled.

Reads the two scored arms and the published cell 4, prints every cell with
its n, its measured chance floor and a Wilson interval, and pairs the two
new arms item by item, since they were scored on the same items with the
same pages and differ only in which characters reached the model.
"""
from __future__ import annotations

import argparse
import json


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return [round((c - h) / d, 3), round((c + h) / d, 3)]


def cells(recs, labeller):
    out = {}
    for lab in ("verbatim", "answer", "neither", "all"):
        sub = recs if lab == "all" else [r for r in recs
                                         if labeller(r) == lab]
        if not sub:
            out[lab] = {"n": 0}
            continue
        k = sum(r["pred"] == r["gold"] for r in sub)
        out[lab] = {"n": len(sub), "correct": k, "acc": round(k / len(sub), 4),
                    "floor": round(sum(1.0 / r["n_choices"] for r in sub)
                                   / len(sub), 4),
                    "ci": wilson(k, len(sub))}
    return out


def show(name, c):
    print(f"\n{name}")
    print(f"  {'cell':10} {'n':>4} {'floor':>7} {'acc':>7}  95% CI")
    for lab in ("all", "verbatim", "answer", "neither"):
        d = c[lab]
        if not d.get("n"):
            print(f"  {lab:10} {0:4d}       -       -")
            continue
        print(f"  {lab:10} {d['n']:4d} {d['floor']:7.4f} {d['acc']:7.4f}  "
              f"[{d['ci'][0]:.3f}, {d['ci'][1]:.3f}]")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", default="results/extern/bench/"
                                     "cell4b_lfm2_mmlu_passages_n200.json")
    ap.add_argument("--ctrl", default="results/extern/bench/"
                                      "cell4c_lfm2_mmlu_seq5_n200.json")
    ap.add_argument("--published", default="results/extern/bench/"
                                           "cell4_lfm2_mmlu_retrieval_n200.json")
    ap.add_argument("--closed", default="results/extern/bench/"
                                        "lfm2_350m_mmlu_completion_bos.json")
    ap.add_argument("--out", default="results/extern/retreport.json")
    a = ap.parse_args()

    def lab_token(r):
        f = r["flags"]
        return "verbatim" if f["stem"] else ("answer" if f["token"]
                                             else "neither")

    def lab_chars(r):
        f = r["flags"]
        return "verbatim" if f["stem"] else ("answer" if f["chars"]
                                             else "neither")

    new = json.load(open(a.new))
    ctrl = json.load(open(a.ctrl))
    pub = json.load(open(a.published))

    pub_cells = {}
    for lab in ("verbatim", "answer", "neither"):
        d = pub["by_contamination"][lab]
        pub_cells[lab] = d | {"ci": wilson(round(d["acc"] * d["n"]), d["n"]),
                              "correct": round(d["acc"] * d["n"])}
    d = pub["all"]
    pub_cells["all"] = d | {"ci": wilson(round(d["acc"] * d["n"]), d["n"]),
                            "correct": round(d["acc"] * d["n"])}

    show("published cell 4: question query, 5 results, sequential packing",
         pub_cells)
    show("control arm: same new pages, sequential packing, top 5",
         cells(ctrl["records"], lab_token))
    show("new arm: question plus options, 20 results, passage packing",
         cells(new["records"], lab_token))
    show("new arm, published character detector for comparability",
         cells(new["records"], lab_chars))

    print("\nanswer present rate in the context the model read")
    for nm, d in (("published", pub), ("control", ctrl), ("new", new)):
        if nm == "published":
            print(f"  {nm:10} chars {d['by_contamination']['answer']['n']}/200 "
                  f"= {d['by_contamination']['answer']['n']/200:.3f} "
                  f"(answer label), verbatim "
                  f"{d['by_contamination']['verbatim']['n']}/200")
            continue
        recs = d["records"]
        n = len(recs)
        tok = sum(r["flags"]["token"] for r in recs)
        stem = sum(r["flags"]["stem"] for r in recs)
        ans = sum(r["flags"]["token"] and not r["flags"]["stem"] for r in recs)
        soft = sum(r["flags"]["soft"] for r in recs)
        print(f"  {nm:10} token {tok}/{n} = {tok/n:.3f}  answer label "
              f"{ans}/{n} = {ans/n:.3f} {wilson(ans, n)}  stem {stem}/{n}  "
              f"soft {soft}/{n}")

    base = {r["id"]: r for r in ctrl["records"]}
    b = c = 0
    for r in new["records"]:
        o = base.get(r["id"])
        if o is None:
            continue
        x = o["pred"] == o["gold"]
        y = r["pred"] == r["gold"]
        b += x and not y
        c += y and not x
    print(f"\npaired accuracy, new arm against control arm on the same items: "
          f"control only correct b={b}, new only correct c={c}, net={c-b:+d}")

    # Within the new arm, does a context that also carries every distractor
    # behave like one that carries only the answer.
    ans = [r for r in new["records"]
           if r["flags"]["token"] and not r["flags"]["stem"]]
    for tag, sub in (("answer, distractors < 3",
                      [r for r in ans if r["flags"]["n_distractors"] < 3]),
                     ("answer, all distractors too",
                      [r for r in ans if r["flags"]["n_distractors"] >= 3])):
        if not sub:
            print(f"  {tag}: n=0")
            continue
        k = sum(r["pred"] == r["gold"] for r in sub)
        print(f"  {tag}: n={len(sub)} acc={k/len(sub):.4f} "
              f"{wilson(k, len(sub))}")

    # The comparison the contamination split cannot make on its own. An item
    # whose answer is findable on the web is also an item this model tends to
    # know, so a cell where the page carries the answer is a cell of easier
    # items. Scoring the same items closed book separates the two.
    closed = {r["id"]: (r["pred"] == r["gold"])
              for r in json.load(open(a.closed))["records"]}

    def mcnemar(b, c):
        from math import comb
        nd = b + c
        if nd == 0:
            return 1.0
        return min(1.0, 2 * sum(comb(nd, i)
                                for i in range(0, min(b, c) + 1)) / 2 ** nd)

    def against_closed(recs, labeller):
        out = {}
        tb = tc = 0
        for lab in ("verbatim", "answer", "neither", "all"):
            sub = recs if lab == "all" else [r for r in recs
                                             if labeller(r) == lab]
            if not sub:
                out[lab] = {"n": 0}
                continue
            n = len(sub)
            k = sum(r["pred"] == r["gold"] for r in sub)
            kc = sum(closed[r["id"]] for r in sub)
            b = sum(1 for r in sub
                    if closed[r["id"]] and r["pred"] != r["gold"])
            c = sum(1 for r in sub
                    if not closed[r["id"]] and r["pred"] == r["gold"])
            if lab != "all":
                tb, tc = tb + b, tc + c
            out[lab] = {"n": n, "retrieval": round(k / n, 4),
                        "retrieval_ci": wilson(k, n),
                        "closed_book_same_items": round(kc / n, 4),
                        "closed_book_ci": wilson(kc, n),
                        "closed_only": b, "retrieval_only": c,
                        "mcnemar_p": round(mcnemar(b, c), 4)}
        return out

    print("\nretrieval against closed book on the same items, per cell")
    arms = (("published", pub["records"],
             lambda r: r["contamination"]),
            ("control", ctrl["records"], lab_token),
            ("new", new["records"], lab_token))
    vs_closed = {}
    for nm, recs, lb in arms:
        vs_closed[nm] = against_closed(recs, lb)
        print(f"  {nm}")
        for lab in ("all", "verbatim", "answer", "neither"):
            d = vs_closed[nm][lab]
            if not d.get("n"):
                continue
            print(f"    {lab:9} n={d['n']:3d} retrieval={d['retrieval']:.4f} "
                  f"closed_book_same_items={d['closed_book_same_items']:.4f} "
                  f"closed_only={d['closed_only']} "
                  f"retrieval_only={d['retrieval_only']} "
                  f"p={d['mcnemar_p']:.3f}")

    out = {"published": pub_cells, "vs_closed_book": vs_closed,
           "control_token": cells(ctrl["records"], lab_token),
           "new_token": cells(new["records"], lab_token),
           "new_chars": cells(new["records"], lab_chars),
           "paired_vs_control": {"control_only": b, "new_only": c},
           "new_cfg": new["cfg"], "new_packer": new["packer"],
           "new_keep": new["keep"],
           "new_live_searches": new["live_searches"],
           "control_packer": ctrl["packer"], "control_keep": ctrl["keep"]}
    json.dump(out, open(a.out, "w"), indent=1)
    print(f"\nwrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
