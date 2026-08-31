"""Aggregation over the rollout files, one cell at a time and never pooled.

Every table this writes carries, for its own cell: the denominator, the chance
floor computed from that cell's own option count, a strict forced-choice score
beside any lenient one, the hedge rate, the fraction of answers naming no
candidate, and the emitted structure. Emitted structure is not optional: the
plan-length ceiling was invisible in accuracy and obvious in emitted length.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict

# ------------------------------------------------------------------ helpers


def corrected(acc: float, chance: float) -> float:
    return (acc - chance) / (1.0 - chance) if chance < 1.0 else 0.0


def macro_both_orders(cells):
    """(accuracy, chance) pairs, aggregated both ways, with the formulas."""
    if not cells:
        return {"cells": 0}
    ma = sum(a for a, _ in cells) / len(cells)
    mc = sum(c for _, c in cells) / len(cells)
    return {"cells": len(cells), "macro_accuracy": ma, "macro_chance": mc,
            "order_A_corrected_macro": corrected(ma, mc),
            "order_B_mean_of_corrected":
                sum(corrected(a, c) for a, c in cells) / len(cells),
            "formula_A": "(mean_i acc_i - mean_i c_i) / (1 - mean_i c_i)",
            "formula_B": "mean_i [ (acc_i - c_i) / (1 - c_i) ]"}


def read(path):
    with open(path) as fh:
        for line in fh:
            if line.strip():
                yield json.loads(line)


# -------------------------------------------------------------- transposed


def named_numbers(answer: str, candidates):
    hits = []
    for c in candidates:
        m = re.search(rf"(?<!\d){re.escape(str(c))}(?!\d)", answer)
        if m:
            hits.append((m.start(), str(c)))
    hits.sort()
    seen, out = set(), []
    for _, c in hits:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def cmd_transposed(args) -> int:
    cells = defaultdict(list)
    for r in read(args.rolls):
        cells[(r.get("decode", "?"), int(r.get("depth", 0)))].append(r)
    rows = []
    for key in sorted(cells):
        rs = cells[key]
        n = len(rs)
        page = train = other = none = hedge = 0
        fpage = ftrain = 0
        rounds = gen = 0.0
        served = 0
        for r in rs:
            if r["decode"] == "mc":
                hits = [str(r["choice"])]
            else:
                hits = named_numbers(r.get("answer", ""), r["candidates"])
                rounds += r.get("n_rounds", 0)
                gen += r.get("n_generated", 0)
                served += int(bool(r.get("chunks")))
            if not hits:
                none += 1
            elif len(hits) > 1:
                hedge += 1
            elif hits[0] == str(r["page_answer"]):
                page += 1
            elif hits[0] == str(r["train_answer"]):
                train += 1
            else:
                other += 1
            if hits and hits[0] == str(r["page_answer"]):
                fpage += 1
            if hits and hits[0] == str(r["train_answer"]):
                ftrain += 1
        chance = sum(1.0 / len(r["candidates"]) for r in rs) / n
        rows.append({"decode": key[0], "depth": key[1], "n": n,
                     "chance": round(chance, 4),
                     "forced_page": round(page / n, 4),
                     "forced_train": round(train / n, 4),
                     "forced_other": round(other / n, 4),
                     "first_page": round(fpage / n, 4),
                     "first_train": round(ftrain / n, 4),
                     "hedge": round(hedge / n, 4), "none": round(none / n, 4),
                     "mean_rounds": round(rounds / n, 3),
                     "served_rate": round(served / n, 3),
                     "mean_generated": round(gen / n, 1)})
    for dec in sorted({r["decode"] for r in rows}):
        sel = [r for r in rows if r["decode"] == dec]
        tot = sum(r["n"] for r in sel)
        agg = {"decode": dec, "depth": "all", "n": tot,
               "chance": round(sum(r["chance"] * r["n"] for r in sel) / tot, 4)}
        for k in ("forced_page", "forced_train", "forced_other", "first_page",
                  "first_train", "hedge", "none", "mean_rounds", "served_rate",
                  "mean_generated"):
            agg[k] = round(sum(r[k] * r["n"] for r in sel) / tot, 4)
        agg["macro_over_depth_page"] = macro_both_orders(
            [(r["forced_page"], r["chance"]) for r in sel])
        rows.append(agg)
    with open(args.out, "w") as fh:
        json.dump(rows, fh, indent=1)
    hdr = ("%-7s %-5s %5s %7s %8s %8s %8s %6s %6s %7s %7s"
           % ("decode", "depth", "n", "chance", "fc_page", "fc_train",
              "fc_other", "hedge", "none", "rounds", "gen"))
    print(hdr)
    for r in rows:
        print("%-7s %-5s %5d %7.3f %8.3f %8.3f %8.3f %6.3f %6.3f %7.2f %7.1f"
              % (r["decode"], r["depth"], r["n"], r["chance"],
                 r["forced_page"], r["forced_train"], r["forced_other"],
                 r["hedge"], r["none"], r["mean_rounds"], r["mean_generated"]))
    print(f"wrote {args.out}")
    return 0


# -------------------------------------------------------------------- plan

_STEP = re.compile(r"\bt\d+\s*=\s*(\S+)")


def emitted_structure(text: str) -> dict:
    """Step count and distinct symbols, read off the text without parsing.

    A plan the shipped parser rejects still has an emitted length, and that
    length is the measurement. Counting it only after a successful parse would
    hide exactly the failure this is looking for.
    """
    syms = _STEP.findall(text or "")
    return {"emitted_steps": len(syms),
            "emitted_symbols": len(set(syms)),
            "emitted_symbol_list": sorted(set(syms))}


def cmd_plan(args) -> int:
    from src.corpus.plans import numeric_ops
    from src.opgraph.invent import make_world
    from src.opgraph.plan import parse_plan, run_plan

    rows = []
    worlds: dict = {}
    for r in read(args.rolls):
        text = r.get("emitted", "")
        st = emitted_structure(text)
        parsed = None
        answer = ""
        try:
            parsed = parse_plan(text)
        except Exception:
            parsed = None
        if parsed is not None:
            seed = int(r["seed"])
            if seed not in worlds:
                worlds[seed] = numeric_ops(make_world(seed, breadth=3))
            try:
                answer = str(run_plan(parsed, worlds[seed]))
            except Exception:
                answer = ""
        rows.append({**{k: r[k] for k in
                        ("decode", "seed", "n_steps", "n_symbols", "band", "determinate", "qframe")
                        if k in r},
                     "required_steps": int(r["n_steps"]),
                     "required_symbols": int(r["n_symbols"]),
                     "gold": r.get("answer", ""),
                     "executed": answer,
                     "correct": bool(answer) and answer == str(r.get("answer", "")),
                     "parsed": parsed is not None,
                     "parsed_steps": len(parsed.steps) if parsed else 0,
                     "gold_plan_correct": text.strip() == str(r.get("target", "")).strip(),
                     **st})
    def step_table(rows):
        cells = defaultdict(list)
        for r in rows:
            cells[(r["decode"], r["required_steps"])].append(r)
        return cells

    cells = step_table(rows)
    table = []
    for key in sorted(cells):
        rs = cells[key]
        n = len(rs)
        table.append({
            "decode": key[0], "required_steps": key[1], "n": n,
            "chance": 0.0,
            "accuracy": round(sum(r["correct"] for r in rs) / n, 4),
            "parse_rate": round(sum(r["parsed"] for r in rs) / n, 4),
            "emitted_steps_mean": round(sum(r["emitted_steps"] for r in rs) / n, 3),
            "emitted_steps_max": max(r["emitted_steps"] for r in rs),
            "emitted_steps_hist": dict(Counter(r["emitted_steps"] for r in rs).most_common(6)),
            "long_enough": round(sum(r["emitted_steps"] >= r["required_steps"]
                                     for r in rs) / n, 4),
            "emitted_symbols_mean": round(sum(r["emitted_symbols"] for r in rs) / n, 3),
            "required_symbols_mean": round(sum(r["required_symbols"] for r in rs) / n, 3),
            "no_plan_rate": round(sum(r["emitted_steps"] == 0 for r in rs) / n, 4),
        })
    def sym_table(rows):
        cells = defaultdict(list)
        for r in rows:
            cells[(r["decode"], r["required_symbols"])].append(r)
        return cells

    scells = sym_table(rows)
    stable = []
    for key in sorted(scells):
        rs = scells[key]
        n = len(rs)
        stable.append({
            "decode": key[0], "required_symbols": key[1], "n": n,
            "chance": 0.0,
            "accuracy": round(sum(r["correct"] for r in rs) / n, 4),
            "parse_rate": round(sum(r["parsed"] for r in rs) / n, 4),
            "emitted_symbols_mean": round(sum(r["emitted_symbols"] for r in rs) / n, 3),
            "enough_symbols": round(sum(r["emitted_symbols"] >= r["required_symbols"]
                                        for r in rs) / n, 4),
            "emitted_symbols_hist": dict(Counter(r["emitted_symbols"] for r in rs).most_common(6)),
            "emitted_steps_mean": round(sum(r["emitted_steps"] for r in rs) / n, 3),
            "no_plan_rate": round(sum(r["emitted_steps"] == 0 for r in rs) / n, 4),
        })
    # The determinate subset. `src/corpus/plans.py:render_tree` writes a
    # binary expression for any node with more than two children, so an item
    # using the arity-four `score` loses two operands in its own question and
    # no reader can recover the gold plan from it. Those items are counted
    # apart rather than dropped, and the rate is reported.
    det = [r for r in rows if r.get("determinate")]
    det_steps, det_syms = [], []
    for key in sorted(step_table(det)):
        rs = step_table(det)[key]
        n = len(rs)
        det_steps.append({
            "decode": key[0], "required_steps": key[1], "n": n,
            "accuracy": round(sum(r["correct"] for r in rs) / n, 4),
            "parse_rate": round(sum(r["parsed"] for r in rs) / n, 4),
            "emitted_steps_mean": round(sum(r["emitted_steps"] for r in rs) / n, 3),
            "emitted_steps_max": max(r["emitted_steps"] for r in rs),
            "long_enough": round(sum(r["emitted_steps"] >= r["required_steps"]
                                     for r in rs) / n, 4),
            "no_plan_rate": round(sum(r["emitted_steps"] == 0 for r in rs) / n, 4)})
    for key in sorted(sym_table(det)):
        rs = sym_table(det)[key]
        n = len(rs)
        det_syms.append({
            "decode": key[0], "required_symbols": key[1], "n": n,
            "accuracy": round(sum(r["correct"] for r in rs) / n, 4),
            "emitted_symbols_mean": round(sum(r["emitted_symbols"] for r in rs) / n, 3),
            "enough_symbols": round(sum(r["emitted_symbols"] >= r["required_symbols"]
                                        for r in rs) / n, 4)})
    out = {"by_required_steps": table, "by_required_symbols": stable,
           "determinate_by_required_steps": det_steps,
           "determinate_by_required_symbols": det_syms,
           "determinate_rate": round(len(det) / max(1, len(rows)), 4),
           "determinate_note": "an item is determinate when a parser reading "
                               "only the question recovers the gold plan "
                               "exactly; the rest use an arity-four symbol "
                               "whose operands the question does not print",
           "n_rows": len(rows),
           "chance_note": "the answer is an open integer; the generator "
                          "excludes gold from the prompt literals, from the "
                          "leaves and from every intermediate, so the floor "
                          "for guessing is 0.000"}
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1)
    if args.records_out:
        with open(args.records_out, "w") as fh:
            for r in rows:
                fh.write(json.dumps(r) + "\n")
    print("%-7s %8s %5s %7s %7s %9s %8s %9s %8s"
          % ("decode", "req_step", "n", "acc", "parse", "emit_mean",
             "emit_max", "long_enuf", "noplan"))
    for r in table:
        print("%-7s %8d %5d %7.3f %7.3f %9.2f %8d %9.3f %8.3f"
              % (r["decode"], r["required_steps"], r["n"], r["accuracy"],
                 r["parse_rate"], r["emitted_steps_mean"],
                 r["emitted_steps_max"], r["long_enough"], r["no_plan_rate"]))
    print()
    print("%-7s %8s %5s %7s %11s %10s"
          % ("decode", "req_syms", "n", "acc", "emit_syms", "enough"))
    for r in stable:
        print("%-7s %8d %5d %7.3f %11.3f %10.3f"
              % (r["decode"], r["required_symbols"], r["n"], r["accuracy"],
                 r["emitted_symbols_mean"], r["enough_symbols"]))
    print()
    print("determinate subset only, rate %.3f" % out["determinate_rate"])
    print("%-7s %8s %5s %7s %9s %8s %9s"
          % ("decode", "req_step", "n", "acc", "emit_mean", "emit_max",
             "long_enuf"))
    for r in det_steps:
        print("%-7s %8d %5d %7.3f %9.2f %8d %9.3f"
              % (r["decode"], r["required_steps"], r["n"], r["accuracy"],
                 r["emitted_steps_mean"], r["emitted_steps_max"],
                 r["long_enough"]))
    print("%-7s %8s %5s %7s %11s %10s"
          % ("decode", "req_syms", "n", "acc", "emit_syms", "enough"))
    for r in det_syms:
        print("%-7s %8d %5d %7.3f %11.3f %10.3f"
              % (r["decode"], r["required_symbols"], r["n"], r["accuracy"],
                 r["emitted_symbols_mean"], r["enough_symbols"]))
    print(f"wrote {args.out}")
    return 0


# ---------------------------------------------------------------- relation


def cmd_relation(args) -> int:
    """Corpus relation families, per family, never pooled."""
    from src.frames import score as sc

    cells = defaultdict(list)
    for r in read(args.rolls):
        fam = r.get("episode_family") or r.get("family") or "?"
        cells[(r.get("decode", "?"), fam)].append(r)
    records = {}
    print(sc.HEADER)
    for key in sorted(cells):
        rows = cells[key]
        for r in rows:
            r.setdefault("candidates", [])
            r["served"] = bool(r.get("chunks")) and any(
                re.search(rf"(?<![A-Za-z]){re.escape(str(r['gold']))}(?![A-Za-z])",
                          c, re.I) for c in r["chunks"])
        vocab = sc.nonce_vocab(rows)
        s = sc.summarize(rows, vocab)
        can = sc.summarize(sc.canary_rows(rows), vocab)
        if can["acc_forced"] != 0.0:
            raise SystemExit(f"HEDGING CANARY FAILED on {key}")
        s["canary_forced"] = can["acc_forced"]
        s["mean_generated"] = sum(r.get("n_generated", 0) for r in rows) / len(rows)
        s["mean_rounds"] = sum(r.get("n_rounds", 0) for r in rows) / len(rows)
        records["|".join(map(str, key))] = s
        print(sc.row_line(key[0], key[1][:18], s))
    macro = {}
    for dec in sorted({k[0] for k in cells}):
        macro[dec] = sc.macro_both_orders(
            [(records["|".join(map(str, k))]["acc_forced"],
              records["|".join(map(str, k))]["chance_cand"])
             for k in sorted(cells) if k[0] == dec])
    with open(args.out, "w") as fh:
        json.dump({"records": records, "macro_over_families": macro,
                   "note": "families are never pooled; the macro is over "
                           "families within one decode and both aggregation "
                           "orders are given"}, fh, indent=1)
    print("\nmacro over families, both orders:")
    for dec, mv in macro.items():
        print("  %-8s cells=%d macroAcc=%.3f macroChance=%.3f A=%.3f B=%.3f"
              % (dec, mv["cells"], mv["macro_accuracy"], mv["macro_chance"],
                 mv["order_A_corrected_macro"], mv["order_B_mean_of_corrected"]))
    print(f"wrote {args.out}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("transposed", cmd_transposed), ("plan", cmd_plan),
                     ("relation", cmd_relation)):
        p = sub.add_parser(name)
        p.add_argument("--rolls", required=True)
        p.add_argument("--out", required=True)
        if name == "plan":
            p.add_argument("--records-out", default="")
        p.set_defaults(fn=fn)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
