"""Tables and facts for THRESHOLD.md, read off the record files.

Every number in the report comes through here from a summary.json or a
records file on disk, and the prose is a template whose placeholders this
fills. A placeholder with no fact behind it is an error rather than a blank,
so a number cannot reach the document without an artifact behind it.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import re
from collections import Counter, defaultdict

RUNGS = ("l45", "xl93", "xxl167", "xxxl355")
GROUPS = ("train_frames_eval", "qframe", "lexicon", "mode", "mixed")
GROUP_LABEL = {"train_frames_eval": "train", "qframe": "qframe",
               "lexicon": "lexicon", "mode": "mode", "mixed": "mixed"}
SHAPES = ("lookup", "lookup_general", "classify", "inverse", "compose",
          "iterate", "pair", "priority", "exclusion", "lookup_then_band",
          "band_then_lookup", "sum_chain", "apply_n", "precedence")


def load(path):
    if not os.path.exists(path):
        return None
    with open(path) as fh:
        return json.load(fh)


def g(summary, group, mode):
    return summary["splits"][group]["modes"][mode]


def f4(x):
    return "n/a" if x is None else f"{x:.4f}"


def rung_table(sums, mode, field):
    """One field of one decode mode, rungs down, frame groups across."""
    rows = ["| rung | params | " + " | ".join(GROUP_LABEL[k] for k in GROUPS)
            + " |",
            "| --- | ---: | " + " | ".join("---:" for _ in GROUPS) + " |"]
    for r in RUNGS:
        s = sums.get(r)
        if s is None:
            continue
        cells = []
        for k in GROUPS:
            try:
                cells.append(f4(g(s, k, mode)["pooled_do_not_headline"][field]))
            except KeyError:
                cells.append("n/a")
        rows.append(f"| {r} | {s['params']['total']:,} | "
                    + " | ".join(cells) + " |")
    return "\n".join(rows)


def shape_table(sums, group, mode, field="exact"):
    """Per shape, rungs across, for one frame group. Never pooled."""
    have = [r for r in RUNGS if sums.get(r)]
    head = ("| shape | n | parser | modal/shape | "
            + " | ".join(have) + " |")
    rule = "| --- | ---: | ---: | ---: | " + " | ".join("---:" for _ in have) \
        + " |"
    rows = [head, rule]
    ref = sums[have[0]]
    by = g(ref, group, mode)["by_shape"]
    for sh in SHAPES:
        if sh not in by:
            continue
        r0 = by[sh]
        par = g(ref, group, "greedy")["by_shape"][sh]["parser_exact"]
        cells = []
        for r in have:
            b = g(sums[r], group, mode)["by_shape"].get(sh)
            cells.append(f4(b[field]) if b else "n/a")
        rows.append(f"| {sh} | {r0['n']} | {f4(par)} | "
                    f"{f4(r0['modal_shape_exact'])} | "
                    + " | ".join(cells) + " |")
    return "\n".join(rows)


def safety_table(sums, mode):
    """Refused and malformed against wrong-but-executable, per group."""
    rows = ["| rung | group | exact | malformed | refused | wrong | "
            "safe/unsafe |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: |"]
    for r in RUNGS:
        s = sums.get(r)
        if s is None:
            continue
        for k in GROUPS:
            try:
                p = g(s, k, mode)["pooled_do_not_headline"]
            except KeyError:
                continue
            safe = p["malformed"] + p["refused"]
            ratio = "inf" if p["wrong"] == 0 else f"{safe / p['wrong']:.3f}"
            rows.append(f"| {r} | {GROUP_LABEL[k]} | {f4(p['exact'])} | "
                        f"{f4(p['malformed'])} | {f4(p['refused'])} | "
                        f"{f4(p['wrong'])} | {ratio} |")
    return "\n".join(rows)


def shapes_at_one(s, group, mode):
    by = g(s, group, mode)["by_shape"]
    return sum(1 for sh in by if by[sh]["exact"] >= 1.0), len(by)


def facts(sums, extra) -> dict:
    out = dict(extra)
    for r in RUNGS:
        s = sums.get(r)
        if s is None:
            continue
        out[f"{r}_params"] = f"{s['params']['total']:,}"
        out[f"{r}_nonemb"] = f"{s['params']['non_embedding']:,}"
        out[f"{r}_steps"] = str(s["steps"])
        for k in GROUPS:
            for mode in ("greedy", "sampled"):
                try:
                    p = g(s, k, mode)["pooled_do_not_headline"]
                except KeyError:
                    continue
                pre = f"{r}_{GROUP_LABEL[k]}_{mode}"
                out[f"{pre}_exact"] = f4(p["exact"])
                out[f"{pre}_malformed"] = f4(p["malformed"])
                out[f"{pre}_refused"] = f4(p["refused"])
                out[f"{pre}_wrong"] = f4(p["wrong"])
                out[f"{pre}_n"] = str(p["n"])
            ones, tot = shapes_at_one(s, k, "greedy")
            out[f"{r}_{GROUP_LABEL[k]}_shapes_exact"] = f"{ones} of {tot}"
            by = g(s, k, "greedy")["by_shape"]
            lo = min(by, key=lambda sh: by[sh]["exact"])
            hi = max(by, key=lambda sh: by[sh]["exact"])
            out[f"{r}_{GROUP_LABEL[k]}_lo"] = f4(by[lo]["exact"])
            out[f"{r}_{GROUP_LABEL[k]}_lo_shape"] = lo
            out[f"{r}_{GROUP_LABEL[k]}_hi"] = f4(by[hi]["exact"])
            out[f"{r}_{GROUP_LABEL[k]}_hi_shape"] = hi
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval", default="results/system/eval")
    ap.add_argument("--out", default="results/system")
    ap.add_argument("--template", default="src/system/THRESHOLD.tmpl.md")
    ap.add_argument("--doc", default="src/system/THRESHOLD.md")
    ap.add_argument("--extra", default="results/system/extra_facts.json")
    a = ap.parse_args()

    sums = {}
    for r in RUNGS:
        s = load(os.path.join(a.eval, r, "summary.json"))
        if s:
            sums[r] = s
    if not sums:
        raise SystemExit("no rung summaries yet")

    parts = ["## Structure exact match, greedy",
             rung_table(sums, "greedy", "exact"),
             "", "## Structure exact match, sampled",
             rung_table(sums, "sampled", "exact"), ""]
    for grp in GROUPS:
        parts += [f"## Per shape, {GROUP_LABEL[grp]}, greedy exact",
                  shape_table(sums, grp, "greedy"), ""]
    parts += ["## Safe failure against wrong executable structure, greedy",
              safety_table(sums, "greedy"), ""]
    os.makedirs(a.out, exist_ok=True)
    tables = "\n".join(parts)
    with open(os.path.join(a.out, "tables.md"), "w") as fh:
        fh.write(tables)

    extra = load(a.extra) or {}
    fx = facts(sums, extra)
    with open(os.path.join(a.out, "facts.json"), "w") as fh:
        json.dump(fx, fh, indent=1, sort_keys=True)
    print(f"{len(fx)} facts, {len(sums)} rungs")

    if os.path.exists(a.template):
        tmpl = open(a.template).read()
        tmpl = tmpl.replace("{{TABLES}}", tables)
        for grp in GROUPS:
            for mode in ("greedy", "sampled"):
                key = f"{{{{SHAPES_{GROUP_LABEL[grp]}_{mode}}}}}"
                if key in tmpl:
                    tmpl = tmpl.replace(key, shape_table(sums, grp, mode))
        for key in ("greedy", "sampled"):
            tmpl = tmpl.replace(f"{{{{RUNGS_{key}}}}}",
                                rung_table(sums, key, "exact"))
            tmpl = tmpl.replace(f"{{{{SAFETY_{key}}}}}",
                                safety_table(sums, key))
        for k, v in fx.items():
            tmpl = tmpl.replace("{{" + k + "}}", str(v))
        left = sorted(set(re.findall(r"\{\{[A-Za-z0-9_]+\}\}", tmpl)))
        if left:
            raise SystemExit("unresolved placeholders: " + ", ".join(left))
        with open(a.doc, "w") as fh:
            fh.write(tmpl)
        print("wrote", a.doc)


if __name__ == "__main__":
    main()
