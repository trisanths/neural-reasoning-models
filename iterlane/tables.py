"""Every table in the report, generated from the persisted result files.

Nothing here recomputes a number. Each table names the file it read, so a value
in the report can be traced back to the artifact it came from.
"""
from __future__ import annotations
import glob, json, os, sys
from iterlane.shape import shape, se

R = "results/iter"
DEPTHS = [1, 2, 3, 4, 5, 6, 8, 12, 16, 32]


def load(p):
    return json.load(open(p)) if os.path.exists(p) else None


def cell(r, cond, kind, d):
    return r.get(cond, {}).get(kind, {}).get(str(d))


def row(vals, w=None):
    return "| " + " | ".join(str(v) for v in vals) + " |"


def hdr(cols):
    return row(cols) + "\n" + "|" + "|".join("---" for _ in cols) + "|"


def fmt(x, nd=3):
    return "-" if x is None else f"{x:.{nd}f}"


def depth_table(r, kind, conds, field="acc", depths=None):
    depths = depths or DEPTHS
    cols = ["depth", "n"] + [c[0] for c in conds]
    lines = [hdr(cols)]
    for d in depths:
        first = None
        vals = []
        for _, key in conds:
            c = cell(r, key, kind, d)
            if c and first is None:
                first = c
            vals.append(fmt(c[field]) if c else "-")
        if first is None:
            continue
        lines.append(row([d, first["n"]] + vals))
    return "\n".join(lines)


def diag_table(r, cond, kind, depths=None):
    depths = depths or DEPTHS
    cols = ["depth", "n", "acc", "se", "parse", "well typed", "exact gold plan",
            "parses but wrong"]
    lines = [hdr(cols)]
    for d in depths:
        c = cell(r, cond, kind, d)
        if not c:
            continue
        lines.append(row([d, c["n"], fmt(c["acc"]), fmt(se(c["acc"], c["n"])),
                          fmt(c["parse_rate"]), fmt(c["well_typed_rate"]),
                          fmt(c["exact_gold_plan_rate"]),
                          fmt(c["parsed_but_wrong_rate"])]))
    return "\n".join(lines)


def compute_table(r, cond, kind, depths=None):
    depths = depths or DEPTHS
    cols = ["depth", "n", "forward passes", "slot decisions", "position evals"]
    lines = [hdr(cols)]
    for d in depths:
        c = cell(r, cond, kind, d)
        if not c:
            continue
        lines.append(row([d, c["n"], fmt(c["fwd_passes_mean"], 1),
                          fmt(c["slot_decisions_mean"], 1),
                          fmt(c["position_evals_mean"], 1)]))
    return "\n".join(lines)


def codec_table(r, kind="sequential"):
    cols = ["depth", "n", "gold plan fits the array", "first error"]
    lines = [hdr(cols)]
    for d in DEPTHS:
        c = r.get("codec", {}).get(kind, {}).get(str(d))
        if not c:
            continue
        lines.append(row([d, c["n"], fmt(c["codec_rate"]),
                          c["first_error"] or "-"]))
    return "\n".join(lines)


def iters_table(r, temp="0"):
    its = sorted({int(k.split("@it")[1]) for k in r if k.startswith("plan_execute@T" + temp + "@")})
    ds = sorted({int(d) for k in r if k.startswith("plan_execute@T" + temp + "@")
                 for d in r[k].get("sequential", {})})
    cols = ["depth"] + [f"it {i}" for i in its]
    lines = [hdr(cols)]
    for d in ds:
        vals = []
        for i in its:
            c = cell(r, f"plan_execute@T{temp}@it{i}", "sequential", d)
            vals.append(fmt(c["acc"]) if c else "-")
        lines.append(row([d] + vals))
    return "\n".join(lines), its


def revision_table(r, temp="0"):
    its = sorted({int(k.split("@it")[1]) for k in r if k.startswith("plan_execute@T" + temp + "@")})
    cols = ["passes", "depth", "slots filled before the last pass",
            "value changed later", "returned to MASK", "final differs from first",
            "items with any revision"]
    lines = [hdr(cols)]
    for i in its:
        for d in [1, 3, 4, 6, 12]:
            c = cell(r, f"plan_execute@T{temp}@it{i}", "sequential", d)
            if not c or "revision" not in c:
                continue
            v = c["revision"]
            lines.append(row([i, d, fmt(v["slots_committed_early_per_item"], 1),
                              fmt(v["value_changed_rate"], 4),
                              fmt(v["returned_to_mask_rate"], 4),
                              fmt(v["final_differs_from_first_rate"], 4),
                              fmt(v["items_with_any_revision_rate"], 3)]))
    return "\n".join(lines)


def conv_table(head):
    files = sorted(glob.glob(f"{R}/conv_{head}_s*.json") + glob.glob(f"{R}/conv_{head}.json"),
                   key=lambda p: json.load(open(p)).get("train_step", 0))
    ds = [1, 2, 3, 4, 6, 8, 12]
    cols = ["training steps"] + [f"d{d}" for d in ds]
    lines = [hdr(cols)]
    for f in files:
        r = json.load(open(f))
        vals = []
        for d in ds:
            c = cell(r, "plan_execute@T0@it8", "sequential", d)
            vals.append(fmt(c["acc"]) if c else "-")
        lines.append(row([r.get("train_step")] + vals))
    return "\n".join(lines)


def shape_block(r, cond, kind="sequential", max_depth=12):
    pts = []
    for d in DEPTHS:
        if d > max_depth:
            continue
        c = cell(r, cond, kind, d)
        if c:
            pts.append((d, c["acc"]))
    if len(pts) < 3:
        return None
    return shape(pts)


def main():
    out = []
    W = out.append
    for head in ("p3", "p4"):
        m = load(f"{R}/main_{head}.json")
        if not m:
            W(f"\n### {head}: main results file missing\n")
            continue
        W(f"\n<!-- ===================== {head} ===================== -->")
        W(f"\n#### {head}: source files")
        W(f"`{R}/main_{head}.json`, train log `runs/iter/{head}.pt.log.json`, "
          f"checkpoint `runs/iter/{head}.pt`, training steps {m.get('train_step')}, "
          f"schema nodes {m.get('schema_nodes')}, slots {m.get('n_slots')}")
        W(f"\n#### {head}: can the array hold the gold plan at all")
        W(codec_table(m))
        W(f"\n#### {head}: harness checks, sequential")
        W(depth_table(m, "sequential",
                      [("oracle_both", "oracle_both"),
                       ("oracle_both round trip", "oracle_both_roundtrip")]))
        W(f"\n#### {head}: sequential depth, both wordings, greedy and sampled")
        W(depth_table(m, "sequential",
                      [("original T0", "plan_execute@T0@it8"),
                       ("original T0.8", "plan_execute@T0.8@it8"),
                       ("paraphrase T0", "plan_execute@T0@it8@para"),
                       ("paraphrase T0.8", "plan_execute@T0.8@it8@para")]))
        W(f"\n#### {head}: the four conditions, sequential, original wording, greedy")
        W(depth_table(m, "sequential",
                      [("plan_execute", "plan_execute@T0@it8"),
                       ("oracle_ops", "oracle_ops@T0@it8"),
                       ("oracle_plan", "oracle_plan@T0@it8"),
                       ("oracle_both", "oracle_both")]))
        W(f"\n#### {head}: the four conditions, sequential, paraphrase, greedy")
        W(depth_table(m, "sequential",
                      [("plan_execute", "plan_execute@T0@it8@para"),
                       ("oracle_ops", "oracle_ops@T0@it8@para"),
                       ("oracle_plan", "oracle_plan@T0@it8@para"),
                       ("oracle_both", "oracle_both@para")]))
        for kind, label in (("novel", "novel composition"),
                            ("breadth", "relational breadth"),
                            ("sequential_paren", "parenthesised sequential")):
            W(f"\n#### {head}: {label}, four conditions, original wording, greedy")
            W(depth_table(m, kind,
                          [("plan_execute", "plan_execute@T0@it8"),
                           ("oracle_ops", "oracle_ops@T0@it8"),
                           ("oracle_plan", "oracle_plan@T0@it8"),
                           ("oracle_both", "oracle_both")],
                          depths=[1, 2, 3, 4, 5, 6]))
            W(f"\n#### {head}: {label}, plan diagnostics, plan_execute, greedy")
            W(diag_table(m, "plan_execute@T0@it8", kind, depths=[1, 2, 3, 4, 5, 6]))
        W(f"\n#### {head}: plan diagnostics, sequential, plan_execute, greedy, original")
        W(diag_table(m, "plan_execute@T0@it8", "sequential"))
        W(f"\n#### {head}: plan diagnostics, sequential, plan_execute, greedy, paraphrase")
        W(diag_table(m, "plan_execute@T0@it8@para", "sequential"))
        W(f"\n#### {head}: compute spent constructing one plan, sequential")
        W(compute_table(m, "plan_execute@T0@it8", "sequential"))
        W(f"\n#### {head}: induction quality on the eval worlds")
        for tag in ("induction", "induction@para"):
            if tag in m:
                W(f"`{tag}`: " + json.dumps(m[tag]))
        if "counter_check" in m:
            W(f"\n#### {head}: reported forward passes against the model")
            W("```\n" + json.dumps(m["counter_check"], indent=1) + "\n```")
        sh = shape_block(m, "plan_execute@T0@it8")
        if sh:
            W(f"\n#### {head}: fitted shape, sequential, plan_execute, greedy, depth 1 to 12")
            W("```\n" + json.dumps(sh, indent=1) + "\n```")
        shp = shape_block(m, "plan_execute@T0@it8@para")
        if shp:
            W(f"\n#### {head}: fitted shape, paraphrase")
            W("```\n" + json.dumps(shp, indent=1) + "\n```")

        it = load(f"{R}/iters_{head}.json")
        if it:
            W(f"\n#### {head}: accuracy against refinement passes, greedy (`{R}/iters_{head}.json`)")
            t, its = iters_table(it, "0")
            W(t)
            W(f"\n#### {head}: accuracy against refinement passes, sampled T0.8")
            t2, _ = iters_table(it, "0.8")
            W(t2)
            W(f"\n#### {head}: does a later pass rewrite an earlier slot, greedy")
            W(revision_table(it, "0"))
            W(f"\n#### {head}: does a later pass rewrite an earlier slot, sampled T0.8")
            W(revision_table(it, "0.8"))

        c = conv_table(head)
        if c.count("\n") > 1:
            W(f"\n#### {head}: convergence check, sequential accuracy by training step")
            W(c)

        pk = load(f"{R}/peaked_{head}.json")
        if pk:
            W(f"\n#### {head}: how peaked the policy is (`{R}/peaked_{head}.json`)")
            cols = ["depth", "n", "mean max prob", "min max prob",
                    "slots above 0.999", "mean hamming greedy vs sampled",
                    "items identical"]
            lines = [hdr(cols)]
            for d, v in sorted(pk["cells"].items(), key=lambda x: int(x[0])):
                lines.append(row([d, v["n"], fmt(v["mean_max_prob"], 5),
                                  fmt(v["min_max_prob"], 5),
                                  fmt(v["frac_slots_above_0.999"], 4),
                                  fmt(v["mean_hamming_greedy_vs_sampled"], 2),
                                  v["items_identical"]]))
            W("\n".join(lines))

        cp = load(f"{R}/cond_{head}.json")
        if cp:
            W(f"\n#### {head}: does one pass read its own slot array (`{R}/cond_{head}.json`)")
            W("```\n" + json.dumps(cp, indent=1)[:3000] + "\n```")

        wd = load(f"{R}/wide_{head}.json")
        if wd:
            W(f"\n#### {head}: widened array, 32 plan nodes (`{R}/wide_{head}.json`)")
            W(f"slots {wd.get('n_slots')}, training steps {wd.get('train_step')}")
            W(codec_table(wd))
            W(depth_table(wd, "sequential",
                          [("oracle_both", "oracle_both"),
                           ("round trip", "oracle_both_roundtrip"),
                           ("plan_execute T0", "plan_execute@T0@it8"),
                           ("plan_execute T0.8", "plan_execute@T0.8@it8"),
                           ("paraphrase T0", "plan_execute@T0@it8@para"),
                           ("oracle_plan", "oracle_plan@T0@it8")]))
            W(f"\n#### {head}: widened array, plan diagnostics")
            W(diag_table(wd, "plan_execute@T0@it8", "sequential"))
            W(f"\n#### {head}: widened array, compute")
            W(compute_table(wd, "plan_execute@T0@it8", "sequential"))
            for kind in ("novel", "breadth"):
                W(f"\n#### {head}: widened array, {kind}")
                W(depth_table(wd, kind,
                              [("plan_execute", "plan_execute@T0@it8"),
                               ("oracle_plan", "oracle_plan@T0@it8"),
                               ("oracle_both", "oracle_both")],
                              depths=[1, 2, 3, 4, 5, 6]))
            shw = shape_block(wd, "plan_execute@T0@it8", max_depth=32)
            if shw:
                W(f"\n#### {head}: widened array, fitted shape to depth 32")
                W("```\n" + json.dumps(shw, indent=1) + "\n```")
    text = "\n".join(out)
    with open(sys.argv[1] if len(sys.argv) > 1 else "iterlane/TABLES.md", "w") as fh:
        fh.write(text + "\n")
    print("wrote", sys.argv[1] if len(sys.argv) > 1 else "iterlane/TABLES.md",
          len(text), "chars")


if __name__ == "__main__":
    main()
