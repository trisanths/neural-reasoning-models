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


def shape_table(sums, group, mode, field="exact", rungs=RUNGS):
    """Per shape, rungs across, for one frame group. Never pooled."""
    have = [r for r in rungs if sums.get(r)]
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



TP_CATS = ("exact", "key_order_canonical", "malformed", "other")


def tpose_table(dirpath):
    """The transposed-operand census, per rung, per version, never pooled.

    Categories are disjoint and exhaustive and come from
    `src/norm/cmpwork/xmode.py`. `key_order_canonical` is the failure the
    45M reader shows: the page's nine values in the page's order, laid on the
    key layout an untransposed grid would have.
    """
    rows = ["| rung | grids seen | version | n | exact | keys in the "
            "untransposed order | malformed | other |",
            "| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |"]
    seen = 0
    for r in RUNGS:
        rep = load(os.path.join(dirpath, f"xmode_{r}.json"))
        if rep is None:
            continue
        for run in rep["runs"].values():
            ft = run.get("finetune") or {}
            k = ft.get("k", "n/a")
            for ver in ("original", "transposed"):
                cells = {key.split("|")[1]: v for key, v in
                         run["counts"].items() if key.startswith(ver + "|")}
                n = sum(cells.values())
                if not n:
                    continue
                out = []
                for cat in TP_CATS:
                    v = cells.get(cat, 0)
                    out.append(f"{v} / {n} = {v / n:.4f}")
                rows.append(f"| {r} | {k} | {ver} | {n} | "
                            + " | ".join(out) + " |")
                seen += 1
    return "\n".join(rows) if seen else ""


def lm_table(sums, field="exact"):
    """The 350M arm on the same grader the rungs go through.

    `params` is a count rather than the rungs' breakdown, because this arm is
    a decoder-only checkpoint and not one of the ladder's encoder-decoders.
    """
    rows = ["| checkpoint | mode | " + " | ".join(GROUP_LABEL[k]
                                                  for k in GROUPS) + " |",
            "| --- | --- | " + " | ".join("---:" for _ in GROUPS) + " |"]
    seen = 0
    for tag, s in sums.items():
        for mode in ("greedy", "sampled"):
            cells = []
            hit = False
            for k in GROUPS:
                try:
                    cells.append(f4(g(s, k, mode)["pooled_do_not_headline"]
                                    [field]))
                    hit = True
                except KeyError:
                    cells.append("n/a")
            if hit:
                rows.append(f"| {tag} | {mode} | " + " | ".join(cells) + " |")
                seen += 1
    return "\n".join(rows) if seen else ""


def lm_safety(sums):
    rows = ["| checkpoint | group | n | exact | malformed | refused | wrong "
            "| safe/unsafe |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    seen = 0
    for tag, s in sums.items():
        for k in GROUPS:
            try:
                p = g(s, k, "greedy")["pooled_do_not_headline"]
            except KeyError:
                continue
            safe = p["malformed"] + p["refused"]
            ratio = "inf" if p["wrong"] == 0 else f"{safe / p['wrong']:.3f}"
            rows.append(f"| {tag} | {GROUP_LABEL[k]} | {p['n']} | "
                        f"{f4(p['exact'])} | {f4(p['malformed'])} | "
                        f"{f4(p['refused'])} | {f4(p['wrong'])} | {ratio} |")
            seen += 1
    return "\n".join(rows) if seen else ""


def frame_table(before, after):
    """Forced choice on held-out frames, the same checkpoint before and after.

    Each cell carries its own chance floor, which is the mean over that cell's
    items of one over that item's option count, and the strict score, which
    requires exactly one option named and it the gold one.
    """
    rows = ["| split | n | floor | strict, before | corrected, before | "
            "strict, after | corrected, after |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    if not before:
        return ""
    b = before["cells"]
    aft = (after or {}).get("cells", {})
    for key in sorted(b):
        if not key.endswith("|ALL_SHAPES"):
            continue
        cb = b[key]
        ca = aft.get(key)
        rows.append(f"| {key.split('|')[0]} | {cb['n']} | {cb['floor']:.4f} | "
                    f"{cb['strict']:.4f} | {f4(cb['corrected'])} | "
                    + (f"{ca['strict']:.4f} | {f4(ca['corrected'])} |"
                       if ca else "n/a | n/a |"))
    return "\n".join(rows)


def freshness(sums, extra_reports=()):
    """Every records file older than the summary that reports it.

    A rescore that reads records written by a different run produces a
    document whose numbers came from two gradings. The check is cheap and the
    failure it catches is silent, so it raises.
    """
    rows = ["| report | written | records | newest record | ok |",
            "| --- | --- | ---: | --- | --- |"]
    bad = []
    for tag, path in extra_reports:
        s = load(path)
        if s is None:
            continue
        sm = os.path.getmtime(path)
        recs = []
        for sp in s.get("splits", {}).values():
            for m in sp.get("modes", {}).values():
                if m.get("records") and os.path.exists(m["records"]):
                    recs.append(m["records"])
        if not recs:
            continue
        newest = max(os.path.getmtime(r) for r in recs)
        ok = newest <= sm
        if not ok:
            bad.append(tag)
        rows.append(f"| {tag} | {_t(sm)} | {len(recs)} | {_t(newest)} | "
                    f"{'yes' if ok else 'NO'} |")
    if bad:
        raise SystemExit("records newer than the report beside them: "
                         + ", ".join(bad))
    return "\n".join(rows)


def _t(ts):
    import datetime
    return datetime.datetime.fromtimestamp(
        ts, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")


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
    ap.add_argument("--tpose", default="results/system/tpose")
    ap.add_argument("--lmeval", default="results/system/lmeval")
    ap.add_argument("--lmframe", default="results/system/lmframe")
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

    tp = tpose_table(a.tpose)
    if tp:
        parts += ["## The transposed operand test", tp, ""]

    lms = {}
    for tag in ("corpus_nosft", "lm350"):
        s2 = load(os.path.join(a.lmeval, tag, "summary.json"))
        if s2:
            lms[tag] = s2
    if lms:
        parts += ["## The 350M arm, structure exact match", lm_table(lms), "",
                  "## The 350M arm, safe failure, greedy", lm_safety(lms), ""]
        for tag, s2 in lms.items():
            for grp in GROUPS:
                parts += [f"## Per shape, {tag}, {GROUP_LABEL[grp]}, greedy "
                          "exact",
                          shape_table({tag: s2}, grp, "greedy",
                                      rungs=(tag,)), ""]

    fb = load(os.path.join(a.lmframe, "corpus_before_greedy.json"))
    fa = load(os.path.join(a.lmframe, "corpus_after_greedy.json"))
    ft = frame_table(fb, fa)
    if ft:
        parts += ["## Held-out frames, forced choice, before and after the "
                  "structure fine tune", ft, ""]

    reports = [(r, os.path.join(a.eval, r, "summary.json")) for r in RUNGS]
    reports += [(f"ft{r}", os.path.join(a.eval, f"ft{r}", "summary.json"))
                for r in RUNGS]
    reports += [(t, os.path.join(a.lmeval, t, "summary.json")) for t in lms]
    parts += ["## Records against the reports beside them",
              freshness(sums, reports), ""]
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
        tmpl = tmpl.replace("{{TPOSE}}", tp)
        tmpl = tmpl.replace("{{LM_EXACT}}", lm_table(lms) if lms else "")
        tmpl = tmpl.replace("{{LM_SAFETY}}", lm_safety(lms) if lms else "")
        tmpl = tmpl.replace("{{FRAMES}}", ft)
        tmpl = tmpl.replace("{{FRESHNESS}}", freshness(sums, reports))
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
