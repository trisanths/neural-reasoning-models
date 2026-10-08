"""Build every table and every fit in PLANHEADS_AR.md from the result files.

Nothing in the document is typed by hand. This writes a json file of named
markdown blocks and `ar_doc.py` splices them into the prose, so a number in the
report and a number in `results/ar/*.json` cannot drift apart.

Two shapes are fitted to every depth curve and both are reported with their
residual sums, because the difference between them is the finding:

  geometric   acc(d) = a * r**d       accumulating per step error
  cliff       acc(d) = p up to D,     a fixed budget of sequential decisions
              q past D                that runs out at D

A head fitted better by the cliff has a budget. One fitted better by the
geometric decay loses a constant fraction per step. A head that moved D from
four to eight and then died is a different result from one that went flat, and
the two residuals are what separate them.
"""

from __future__ import annotations

import json
import math
import sys

TEMPS = ("@T0", "@T0.8", "@T1")
GRIDKINDS = ("sequential", "sequential_paren", "novel", "breadth",
             "same_page_pair", "units")
COND = ("plan_execute", "oracle_ops", "oracle_plan")


def fit_geometric(depths, accs):
    pts = [(d, a) for d, a in zip(depths, accs) if a > 0]
    if len(pts) < 3:
        return None
    xs = [d for d, _ in pts]
    ys = [math.log(a) for _, a in pts]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return None
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den
    a = math.exp(my - b * mx)
    sse = sum((acc - a * math.exp(b * d)) ** 2 for d, acc in zip(depths, accs))
    return {"a": round(a, 4), "per_step_factor": round(math.exp(b), 4),
            "half_life_steps": round(math.log(0.5) / b, 2) if b < 0 else None,
            "sse": round(sse, 5), "fitted_on": len(pts), "of": len(depths)}


def fit_cliff(depths, accs):
    best = None
    for i in range(len(depths)):
        D = depths[i]
        hi = [a for d, a in zip(depths, accs) if d <= D]
        lo = [a for d, a in zip(depths, accs) if d > D]
        p = sum(hi) / len(hi)
        q = sum(lo) / len(lo) if lo else 0.0
        sse = sum((a - p) ** 2 for a in hi) + sum((a - q) ** 2 for a in lo)
        if best is None or sse < best["sse"]:
            best = {"cliff_depth": D, "plateau": round(p, 4),
                    "floor": round(q, 4), "sse": round(sse, 5)}
    return best


def crossings(depths, accs, thresholds=(0.5, 0.25, 0.1)):
    out = {}
    for t in thresholds:
        hit = None
        for d, a in zip(depths, accs):
            if a < t:
                hit = d
                break
        out[str(t)] = hit
    return out


def cells(res, cond, kind):
    return res.get(cond, {}).get(kind, {})


def depths_of(res, cond, kind):
    return sorted(cells(res, cond, kind), key=int)


def curve(res, cond, kind):
    b = cells(res, cond, kind)
    ds = sorted(b, key=int)
    return [int(d) for d in ds], [b[d]["acc"] for d in ds]


def fmt(v, f):
    if v is None:
        return "-"
    return f.format(v)


def table(header, rows):
    out = ["| " + " | ".join(str(h) for h in header) + " |",
           "|" + "|".join(["---"] * len(header)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def acc_table(res_by_head, kind, style, temp):
    hdr, rows = None, []
    for h in sorted(res_by_head):
        r = res_by_head[h]
        for cond in COND:
            name = cond + temp + style
            ds = depths_of(r, name, kind)
            if not ds:
                continue
            hdr = hdr or ["head, condition"] + ds
            b = cells(r, name, kind)
            rows.append([f"{h} {cond}"] + [fmt(b[d]["acc"], "{:.3f}") for d in ds])
        name = "oracle_both" + style
        ds = depths_of(r, name, kind)
        if ds:
            b = cells(r, name, kind)
            rows.append([f"{h} oracle_both"] + [fmt(b[d]["acc"], "{:.3f}") for d in ds])
    if not hdr:
        return "(no cells)"
    ns = set()
    for h in sorted(res_by_head):
        for cond in COND:
            for d, c in cells(res_by_head[h], cond + temp + style, kind).items():
                ns.add(c["n"])
    return table(hdr, rows) + f"\n\nn = {sorted(ns)} per cell."


DIAG = [("acc", "{:.3f}"), ("parse_rate", "{:.3f}"), ("well_typed_rate", "{:.3f}"),
        ("exact_gold_plan_rate", "{:.3f}"), ("parsed_but_wrong_rate", "{:.3f}"),
        ("emitted_steps_mean", "{:.3f}"), ("emitted_steps_eq_gold_rate", "{:.3f}"),
        ("prefix_of_gold_rate", "{:.3f}"), ("first_step_correct_rate", "{:.3f}"),
        ("matched_prefix_len_mean", "{:.3f}"), ("fwd_passes_mean", "{:.1f}"),
        ("position_evals_mean", "{:.1f}"), ("gen_tokens_mean", "{:.1f}"),
        ("at_generation_cap", "{:.0f}"), ("n", "{:.0f}")]


def diag_table(res, kind, cond="plan_execute@T0", style=""):
    name = cond + style
    ds = depths_of(res, name, kind)
    if not ds:
        return "(no cells)"
    b = cells(res, name, kind)
    rows = [[f] + [fmt(b[d].get(f), s) for d in ds] for f, s in DIAG]
    return table(["metric"] + ds, rows)


def fit_block(res_by_head, kind="sequential"):
    rows = []
    for h in sorted(res_by_head):
        r = res_by_head[h]
        for style, sname in (("", "original"), ("@para", "paraphrase")):
            for temp in TEMPS:
                for cond in ("plan_execute", "oracle_plan"):
                    ds, accs = curve(r, cond + temp + style, kind)
                    if not ds:
                        continue
                    g = fit_geometric(ds, accs)
                    c = fit_cliff(ds, accs)
                    x = crossings(ds, accs)
                    span = max(accs) - min(accs)
                    if span < 0.15:
                        shape = "flat"
                    elif c and (g is None or c["sse"] < g["sse"]):
                        shape = f"cliff at {c['cliff_depth']}"
                    else:
                        shape = "geometric decay"
                    rows.append([
                        h, cond, temp.replace("@T", "T="), sname, shape,
                        f"{c['cliff_depth']}" if c else "-",
                        fmt(c["plateau"] if c else None, "{:.3f}"),
                        fmt(c["floor"] if c else None, "{:.3f}"),
                        fmt(c["sse"] if c else None, "{:.4f}"),
                        fmt(g["per_step_factor"] if g else None, "{:.3f}"),
                        fmt(g["sse"] if g else None, "{:.4f}"),
                        x["0.5"] if x["0.5"] is not None else "never",
                        x["0.1"] if x["0.1"] is not None else "never",
                    ])
    return table(["head", "condition", "temp", "wording", "shape", "cliff D", "plateau",
                  "floor", "cliff SSE", "geometric r", "geometric SSE",
                  "first d below 0.5", "first d below 0.1"], rows)


def example_block(res_by_head, kind="sequential", depths=("3", "4", "8", "32")):
    """The plan each head actually wrote, beside the plan the question needed."""
    from src.opgraph.data import eval_worlds, make_item
    from src.opgraph.plan import serialize_plan
    lines = []
    for d in depths:
        b = int(d) if kind == "breadth" else 3
        ws = eval_worlds(kind, 1, breadth=b, style=0)
        it = make_item(kind, ws[0], int(d), 0)
        lines.append(f"question depth {d}")
        lines.append(f"  question  {it.text}")
        lines.append(f"  gold      {serialize_plan(it.plan)}")
        for h in sorted(res_by_head):
            c = cells(res_by_head[h], "plan_execute@T0", kind).get(d, {})
            lines.append(f"  {h} wrote   {c.get('sample', '')}")
        lines.append("")
    return "```\n" + "\n".join(lines).rstrip() + "\n```"


def compute_block(res_by_head, temp="@T0", style=""):
    """Forward passes, symbols committed and positions evaluated, every cell.

    For a causal text head a forward pass is one cached decode step, so the
    count charged to an item is the prompt pass plus the tokens it generated
    before its own end of text, and `position_evals` is the prompt width plus
    those tokens.
    """
    rows = []
    for h in sorted(res_by_head):
        r = res_by_head[h]
        for kind in ("sequential", "sequential_paren", "novel", "breadth",
                     "same_page_pair", "units"):
            b = cells(r, "plan_execute" + temp + style, kind)
            for d in sorted(b, key=int):
                c = b[d]
                rows.append([h, kind, d, c["n"],
                             fmt(c["fwd_passes_mean"], "{:.1f}"),
                             fmt(c["slot_decisions_mean"], "{:.1f}"),
                             fmt(c["position_evals_mean"], "{:.1f}")])
    return table(["head", "kind", "depth", "n", "forward passes",
                  "symbols committed", "positions evaluated"], rows)


def wording_block(res_by_head):
    """Is oracle_ops really identical between the two page wordings?

    The plan prompt holds the operator signature line and the question and never
    the page text, and the question is generated from the world's glyphs, which
    the paraphrase does not change. So a condition that supplies gold operators
    should see the same input under both wordings. That is a prediction about
    the harness, so it is checked rather than asserted.
    """
    rows = []
    for h in sorted(res_by_head):
        r = res_by_head[h]
        for temp in TEMPS:
            worst = 0.0
            n = 0
            for kind in GRIDKINDS:
                a = cells(r, "oracle_ops" + temp, kind)
                b = cells(r, "oracle_ops" + temp + "@para", kind)
                for d in a:
                    if d in b:
                        n += 1
                        worst = max(worst, abs(a[d]["acc"] - b[d]["acc"]))
            rows.append([h, temp.replace("@T", "T="), n, f"{worst:.4f}"])
    return table(["head", "temperature", "cells compared",
                  "largest accuracy difference between wordings"], rows)


def harness_block(res_by_head):
    rows, bad = [], []
    for h in sorted(res_by_head):
        r = res_by_head[h]
        for name in ("oracle_both", "oracle_both@para",
                     "oracle_both_roundtrip", "oracle_both_roundtrip@para"):
            n = tot = 0
            worst = 1.0
            for kind, cs in r.get(name, {}).items():
                for d, c in cs.items():
                    n += 1
                    tot += c["n"]
                    worst = min(worst, c["acc"])
                    if c["acc"] != 1.0:
                        bad.append(f"{h} {name} {kind} d={d} acc={c['acc']}")
            rows.append([h, name, n, tot, f"{worst:.4f}"])
    t = table(["head", "condition", "cells", "items", "min accuracy over cells"], rows)
    if bad:
        t += "\n\nHARNESS BROKEN:\n" + "\n".join("  " + b for b in bad)
    return t


def counter_block(res_by_head):
    rows = []
    for h in sorted(res_by_head):
        for k, v in (res_by_head[h].get("counter_check") or {}).items():
            rows.append([h, k, v["reported"], v["observed"], v["ok"]])
    return table(["head", "run", "reported forward passes", "observed at the model",
                  "match"], rows)


def induction_block(res_by_head):
    rows = []
    for h in sorted(res_by_head):
        r = res_by_head[h]
        for tag, w in (("induction", "original"), ("induction@para", "paraphrase")):
            v = r.get(tag)
            if not v:
                continue
            rows.append([h, w, v["worlds"], v["pages"],
                         f"{v['pages_parsed'] / max(1, v['pages']):.3f}",
                         v["gold_ops"], v["induced_ops"],
                         f"{v['exact_text'] / max(1, v['gold_ops']):.3f}",
                         f"{v['behavioural'] / max(1, v['gold_ops']):.3f}"])
    return table(["head", "wording", "worlds", "pages", "page parse rate",
                  "gold operators", "induced operators", "exact text rate",
                  "behavioural match rate"], rows)


def train_block(res_by_head):
    rows = []
    for h in sorted(res_by_head):
        a = res_by_head[h].get("train_args") or {}
        ho = res_by_head[h].get("holdout") or {}
        dr = res_by_head[h].get("dropped") or {}
        rows.append([h, a.get("steps"), a.get("batch_size"), a.get("worlds"),
                     a.get("lr"), a.get("max_len"), a.get("seed"),
                     ho.get("plans"), json.dumps(ho.get("depth_histogram")),
                     ho.get("max_distinct_operator_symbols"),
                     dr.get("induce"), dr.get("plan")])
    return table(["head", "steps", "batch", "worlds", "lr", "max_len", "seed",
                  "training plans", "plan depth histogram",
                  "max distinct operator symbols", "induction seqs dropped",
                  "plan seqs dropped"], rows)


def steps_hist_block(res_by_head, kind="sequential", temp="@T0", style=""):
    rows = []
    for h in sorted(res_by_head):
        b = cells(res_by_head[h], "plan_execute" + temp + style, kind)
        for d in sorted(b, key=int):
            hist = b[d].get("emitted_steps_hist") or {}
            top = sorted(hist.items(), key=lambda kv: -kv[1])[:4]
            rows.append([h, d, b[d]["gold_steps"],
                         fmt(b[d].get("emitted_steps_mean"), "{:.3f}"),
                         ", ".join(f"{k}:{v}" for k, v in top)])
    return table(["head", "question depth", "gold plan steps",
                  "mean steps written", "steps written, count"], rows)


def sampling_block(res_by_head):
    """Does any amount of sampling ever make a head write a fourth step?

    A greedy zero on this project has been a false zero before, so the question
    is not whether the argmax plan is short but whether the policy has any mass
    on a longer one. Every item at every question depth past the depth three
    holdout is counted, over all three temperatures.
    """
    rows = []
    for h in sorted(res_by_head):
        r = res_by_head[h]
        for temp in TEMPS:
            for style, sname in (("", "original"), ("@para", "paraphrase")):
                tot = over = 0
                longest = 0
                for kind in ("sequential", "sequential_paren", "novel"):
                    b = cells(r, "plan_execute" + temp + style, kind)
                    for d in b:
                        if int(d) <= 3:
                            continue
                        tot += b[d]["n"]
                        for k, v in (b[d].get("emitted_steps_hist") or {}).items():
                            if int(k) > 3:
                                over += v
                            longest = max(longest, int(k))
                rows.append([h, temp.replace("@T", "T="), sname, tot, over,
                             f"{over / max(1, tot):.4f}", longest])
    return table(["head", "temperature", "wording",
                  "items at question depth above three",
                  "items whose plan had more than three steps", "rate",
                  "longest plan written, in steps"], rows)


def convergence_block(conv, full):
    rows = []
    for h in sorted(full):
        for tag, src in (("4000 steps", conv), ("8000 steps", full)):
            if h not in src:
                continue
            for style, sname in (("", "original"), ("@para", "paraphrase")):
                ds, accs = curve(src[h], "plan_execute@T0" + style, "sequential")
                if not ds:
                    continue
                rows.append([h, tag, sname] + [f"{a:.3f}" for a in accs])
    ds, _ = curve(full[sorted(full)[0]], "plan_execute@T0", "sequential")
    return table(["head", "budget", "wording"] + ds, rows)


def main():
    out_path = sys.argv[1]
    res, conv = {}, {}
    for p in sys.argv[2:]:
        with open(p) as fh:
            r = json.load(fh)
        (conv if "s4000" in p else res)[r["head"]] = r

    blocks = {
        "harness": harness_block(res),
        "wording": wording_block(res),
        "compute": compute_block(res),
        "examples": example_block(res),
        "examples_novel": example_block(res, "novel", ("2", "3", "6")),
        "examples_breadth": example_block(res, "breadth", ("3", "4", "6")),
        "counter": counter_block(res),
        "induction": induction_block(res),
        "training": train_block(res),
        "convergence": convergence_block(conv, res),
        "sampling": sampling_block(res),
        "fits": fit_block(res),
        "steps_hist": steps_hist_block(res),
        "steps_hist_para": steps_hist_block(res, style="@para"),
    }
    for kind in ("sequential", "sequential_paren", "novel", "breadth"):
        for style, sname in (("", "orig"), ("@para", "para")):
            for temp in TEMPS:
                key = f"acc_{kind}_{sname}_{temp.replace('@T', 't').replace('.', '')}"
                blocks[key] = acc_table(res, kind, style, temp)
    for h in sorted(res):
        for kind in ("sequential", "novel", "breadth"):
            blocks[f"diag_{h}_{kind}"] = diag_table(res[h], kind)
            blocks[f"diag_{h}_{kind}_para"] = diag_table(res[h], kind, style="@para")
    with open(out_path, "w") as fh:
        json.dump(blocks, fh, indent=1)
    for k in sorted(blocks):
        print(f"\n<<<{k}>>>\n{blocks[k]}")


if __name__ == "__main__":
    main()
