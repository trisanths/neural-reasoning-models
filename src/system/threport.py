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



FID_AXES = ("lexicon", "mode", "key_pos", "qform", "scope_pos")


def axis_table(sums, group, mode, axis):
    """Rungs down, one frame axis across, inside one frame group.

    `src/norm/nreport.py:by_axis` computed these off the same records the
    exactness came from. The cells of one axis partition that group and are
    not pooled with any other group.
    """
    have = [r for r in RUNGS if sums.get(r)]
    if not have:
        return ""
    keys = sorted(g(sums[have[0]], group, mode)["by_axis"].get(axis, {}))
    if len(keys) < 2:
        return ""
    rows = ["| rung | " + " | ".join(f"{k} (n)" for k in keys) + " |",
            "| --- | " + " | ".join("---:" for _ in keys) + " |"]
    for r in have:
        by = g(sums[r], group, mode)["by_axis"].get(axis, {})
        cells = [f"{f4(by[k]['exact'])} ({by[k]['n']})" if k in by else "n/a"
                 for k in keys]
        rows.append(f"| {r} | " + " | ".join(cells) + " |")
    return "\n".join(rows)


def shape_by_axis(sums, group, mode, axis):
    """One rung's shapes against one axis, counted off the records file.

    The 45M rung is exact on several shapes of the held-out sentence mode at
    a rate that matches the key-first share of that group exactly, so the
    cross tabulation is in the document rather than left as a coincidence.
    """
    import gzip
    ai = FID_AXES.index(axis)
    have = [r for r in RUNGS if sums.get(r)]
    blocks = []
    for r in have:
        try:
            path = g(sums[r], group, mode)["records"]
        except KeyError:
            continue
        if not os.path.exists(path):
            continue
        cells = defaultdict(Counter)
        vals = set()
        with gzip.open(path, "rt") as fh:
            for line in fh:
                rec = json.loads(line)
                v = rec["fid"].split(".")[ai]
                vals.add(v)
                c = cells[(rec["shape"], v)]
                c["n"] += 1
                c["exact"] += bool(rec["exact"])
        vals = sorted(vals)
        rows = [f"| shape | " + " | ".join(vals) + " |",
                "| --- | " + " | ".join("---:" for _ in vals) + " |"]
        for sh in SHAPES:
            if not any((sh, v) in cells for v in vals):
                continue
            out = []
            for v in vals:
                c = cells.get((sh, v))
                out.append(f"{c['exact'] / c['n']:.4f} ({c['n']})"
                           if c else "n/a")
            rows.append(f"| {sh} | " + " | ".join(out) + " |")
        blocks.append(f"### {r}\n\n" + "\n".join(rows))
    return "\n\n".join(blocks)


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



QUICK = ("train_frames_eval", "qframe", "lexicon", "mode")


def last_quick_eval(rung):
    """The rung's own final in-training eval, 700 items, the same prefix.

    `src/system/strain.py` evaluates on `neval.load_eval(path, 700)`, which is
    the first 700 items of the same file `src/system/sreport.py` reads, so the
    fine tuned checkpoint scored at 700 and the rung scored at 700 are the same
    denominator on the same items.
    """
    path = train_log(rung)
    if not os.path.exists(path):
        return None
    last = None
    for line in open(path):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("event") == "eval":
            last = r
    return last


def ft_cost_table(evaldir):
    """What 1,024 grids of a new page shape cost the groups already read."""
    rows = ["| rung | frame group | n | before the fine tune | after |",
            "| --- | --- | ---: | ---: | ---: |"]
    seen = 0
    for r in RUNGS:
        before = last_quick_eval(r)
        after = load(os.path.join(evaldir, f"ft{r}", "summary.json"))
        if before is None or after is None:
            continue
        for k in QUICK:
            try:
                a = g(after, k, "greedy")["pooled_do_not_headline"]
            except KeyError:
                continue
            b = before.get(k)
            rows.append(f"| {r} | {GROUP_LABEL[k]} | {a['n']} | "
                        f"{f4(b) if b is not None else 'n/a'} | "
                        f"{f4(a['exact'])} |")
            seen += 1
    return "\n".join(rows) if seen else ""


def tpose_table(dirpath, suffix=""):
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
        rep = load(os.path.join(dirpath, f"xmode_{r}{suffix}.json"))
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


def tpose_group_table(dirpath, suffix=""):
    """The same census inside each frame group, 150 pages per cell."""
    rows = ["| rung | version | frame group | n | exact | keys in the "
            "untransposed order | malformed | other |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |"]
    seen = 0
    for r in RUNGS:
        rep = load(os.path.join(dirpath, f"xmode_{r}{suffix}.json"))
        if rep is None:
            continue
        for run in rep["runs"].values():
            by = run.get("counts_by_group")
            if not by:
                continue
            groups = []
            for key in by:
                sp = key.split("|")[1]
                if sp not in groups:
                    groups.append(sp)
            for ver in ("original", "transposed"):
                for sp in groups:
                    cells = {k.split("|")[2]: v for k, v in by.items()
                             if k.startswith(f"{ver}|{sp}|")}
                    n = sum(cells.values())
                    if not n:
                        continue
                    out = [f"{cells.get(cat, 0)} / {n} = "
                           f"{cells.get(cat, 0) / n:.4f}" for cat in TP_CATS]
                    rows.append(f"| {r} | {ver} | {sp} | {n} | "
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




CONTROLS = ("xl93lr40",)
TRAIN_LOG = {"l45": "results/norm/train/log_l.jsonl"}


def train_log(rung):
    return TRAIN_LOG.get(rung, f"results/system/train/log_{rung}.jsonl")


def fit_of(rung):
    """The rung's own training loss at the steps every rung logged.

    A rung that fits its training file worse than a smaller rung is not a
    capacity measurement, so the fit sits beside the exactness rather than
    behind it.
    """
    path = train_log(rung)
    if not os.path.exists(path):
        return None
    at, last, peak, lr = {}, None, None, None
    for line in open(path):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("event") == "start":
            lr = r.get("lr")
        if r.get("event") == "step":
            last = r
            if r["step"] in (8000, 15000, 30000):
                at[r["step"]] = r["loss"]
            if r.get("gb"):
                peak = max(peak or 0, r["gb"])
    if last is None:
        return None
    return {"lr": lr, "at": at, "final": last["loss"], "peak_gb": peak}


def fit_table(rungs):
    rows = ["| rung | peak lr | loss at 8,000 | at 15,000 | at 30,000 | "
            "peak GB |",
            "| --- | ---: | ---: | ---: | ---: | ---: |"]
    seen = 0
    for r in rungs:
        f = fit_of(r)
        if f is None:
            continue
        a = f["at"]
        rows.append(f"| {r} | {f['lr']} | "
                    + " | ".join(str(a.get(k, "n/a"))
                                 for k in (8000, 15000, 30000))
                    + f" | {f['peak_gb'] if f['peak_gb'] else 'n/a'} |")
        seen += 1
    return "\n".join(rows) if seen else ""


def rung_cfg_table(sums):
    """What each rung is, read off the checkpoint the summary was written from."""
    rows = ["| rung | d_model | heads | layers | parameters | non-embedding "
            "| steps |",
            "| --- | ---: | ---: | --- | ---: | ---: | ---: |"]
    for r in RUNGS:
        s = sums.get(r)
        if s is None:
            continue
        c = s.get("cfg") or {}
        rows.append(
            f"| {r} | {c.get('d_model', '?')} | {c.get('n_head', '?')} | "
            f"{c.get('n_enc', '?')}+{c.get('n_dec', '?')} | "
            f"{s['params']['total']:,} | {s['params']['non_embedding']:,} | "
            f"{s['steps']} |")
    return "\n".join(rows)


def artifacts_table(paths):
    """Every file the document reports from, with the time it was written."""
    rows = ["| artifact | bytes | written |",
            "| --- | ---: | --- |"]
    for p in paths:
        if not p or not os.path.exists(p):
            continue
        rows.append(f"| `{os.path.relpath(p, os.getcwd())}` | "
                    f"{os.path.getsize(p):,} | {_t(os.path.getmtime(p))} |")
    return "\n".join(rows)


def collect_artifacts(a, sums, lms):
    out = []
    for r in RUNGS:
        p = os.path.join(a.eval, r, "summary.json")
        if os.path.exists(p):
            out.append(p)
            s = load(p)
            for sp in s["splits"].values():
                for m in sp["modes"].values():
                    out.append(m.get("records"))
        p = os.path.join(a.eval, f"ft{r}", "summary.json")
        if os.path.exists(p):
            out.append(p)
        p = os.path.join(a.tpose, f"xmode_{r}.json")
        if os.path.exists(p):
            out.append(p)
        p = os.path.join("results/system/train", f"log_{r}.jsonl")
        if os.path.exists(p):
            out.append(p)
    for tag, s in lms.items():
        out.append(os.path.join(a.lmeval, tag, "summary.json"))
        for sp in s["splits"].values():
            for m in sp["modes"].values():
                out.append(m.get("records"))
    for p in ("results/system/lmframe/corpus_before_greedy.json",
              "results/system/lmframe/corpus_after_greedy.json",
              "results/system/gate/strict_gate_base.json",
              "results/system/lm/train.jsonl",
              "results/norm/compare/x_items.jsonl.gz",
              "data/norm/grid_train.npz", "data/norm/manifest.json"):
        out.append(p)
    seen, uniq = set(), []
    for p in out:
        if p and p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq





ZERO_ON_VALUE_FIRST = ("lookup", "inverse", "iterate", "compose", "exclusion",
                       "sum_chain", "precedence")


def keypos_draw_table(path):
    """Key position per shape in the training draw the network actually saw."""
    d = load(path)
    if d is None:
        return ""
    rows = ["| shape | key_first | value_first | value_first share | "
            "scores 0.0000 on value_first |",
            "| --- | ---: | ---: | ---: | --- |"]
    for r in d["per_shape"]:
        rows.append(f"| {r['shape']} | {r['key_first']:,} | "
                    f"{r['value_first']:,} | {r['value_first_share']:.4f} | "
                    + ("yes" if r["scores_zero_on_value_first"] else "") + " |")
    return "\n".join(rows)


def keypos_mode_table(path):
    """Value-first items per trained sentence mode, for the seven shapes."""
    d = load(path)
    if d is None:
        return ""
    modes = d["modes"]
    by = d["seven_shapes_by_mode_keypos"]
    rows = ["| shape | " + " | ".join(modes) + " |",
            "| --- | " + " | ".join("---:" for _ in modes) + " |"]
    for sh in ZERO_ON_VALUE_FIRST:
        cells = [f"{by.get(f'{sh}|{m}|value_first', 0):,}" for m in modes]
        rows.append(f"| {sh} | " + " | ".join(cells) + " |")
    return "\n".join(rows)


def grid_order_table(order_path, overlap_path):
    """Operand order in the two grid draws, and their overlap with the test."""
    o = load(order_path)
    v = load(overlap_path)
    if o is None:
        return ""
    rows = ["| draw | pages | row-major key order | another key order |",
            "| --- | ---: | ---: | ---: |"]
    for name, c in o["counts"].items():
        tot = sum(c.values())
        rows.append(f"| `{name}` | {tot:,} | {c.get('canonical', 0):,} | "
                    f"{c.get('other', 0):,} |")
    if v:
        rows.append("")
        rows.append("| pair | shared pages |")
        rows.append("| --- | ---: |")
        for k, lab in (("overlap_both_train", "`grid_both` and `grid_train`"),
                       ("overlap_train_transposed",
                        "`grid_train` and the transposed items"),
                       ("overlap_both_transposed",
                        "`grid_both` and the transposed items"),
                       ("overlap_both_original",
                        "`grid_both` and the original items")):
            if k in v:
                rows.append(f"| {lab} | {v[k]} |")
    return "\n".join(rows)


def draw_facts(keypos_path, mode_path, order_path) -> dict:
    out = {}
    d = load(keypos_path)
    if d:
        seven = [r for r in d["per_shape"] if r["scores_zero_on_value_first"]]
        if seven:
            out["keypos_seven_vf_min"] = f"{min(r['value_first'] for r in seven):,}"
            out["keypos_seven_vf_max"] = f"{max(r['value_first'] for r in seven):,}"
            out["keypos_seven_share_min"] = \
                f"{min(r['value_first_share'] for r in seven):.4f}"
            out["keypos_seven_share_max"] = \
                f"{max(r['value_first_share'] for r in seven):.4f}"
        out["draw_n"] = f"{d['n_training_items']:,}"
    m = load(mode_path)
    if m:
        by = m["seven_shapes_by_mode_keypos"]
        vals = [v for k, v in by.items() if k.endswith("|value_first")]
        if vals:
            out["keypos_seven_per_mode_min"] = f"{min(vals):,}"
            out["keypos_seven_per_mode_max"] = f"{max(vals):,}"
        out["trained_modes"] = ", ".join(f"`{x}`" for x in m["modes"])
        out["n_trained_modes"] = str(len(m["modes"]))
    o = load(order_path)
    if o:
        for name, c in o["counts"].items():
            tot = sum(c.values())
            out[f"{name}_pages"] = f"{tot:,}"
            out[f"{name}_canonical"] = f"{c.get('canonical', 0):,}"
            out[f"{name}_other"] = f"{c.get('other', 0):,}"
    return out




def parser_keypos_table(path):
    """The reference parser on the same items, split by key position."""
    d = load(path)
    if d is None:
        return ""
    rows = ["| frame group | key position | n | parser exact |",
            "| --- | --- | ---: | ---: |"]
    for split, c in d["splits"].items():
        for kp in ("key_first", "value_first"):
            n = c.get(f"{kp}|n")
            ex = c.get(f"{kp}|exact")
            if not n:
                continue
            rows.append(f"| {GROUP_LABEL.get(split, split)} | {kp} | {n} | "
                        f"{ex} / {n} = {ex / n:.4f} |")
    return "\n".join(rows)


def parser_keypos_facts(path) -> dict:
    d = load(path)
    if d is None:
        return {}
    out = {}
    for split, c in d["splits"].items():
        lab = GROUP_LABEL.get(split, split)
        for kp in ("key_first", "value_first"):
            n, ex = c.get(f"{kp}|n"), c.get(f"{kp}|exact")
            if n:
                out[f"parser_{lab}_{kp}"] = f"{ex} of {n}"
        for sh in ZERO_ON_VALUE_FIRST:
            n = c.get(f"{sh}|value_first|n")
            ex = c.get(f"{sh}|value_first|exact")
            if n:
                out[f"parser_{lab}_{sh}_value_first"] = f"{ex} of {n}"
    return out


def keypos_group_table(path):
    """Key position inside every frame group, from the same records.

    The held-out sentence mode is the only group where the two positions come
    apart. On the groups whose sentence mode training contained, the reader is
    within a point of itself on both.
    """
    d = load(path)
    if d is None:
        return ""
    rows = ["| rung | frame group | key_first | value_first |",
            "| --- | --- | ---: | ---: |"]
    for tag, groups in d["cells"].items():
        for sp, c in groups.items():
            rows.append(f"| {tag} | {GROUP_LABEL.get(sp, sp)} | "
                        f"{c['key_first']['exact']:.4f} "
                        f"({c['key_first']['n']}) | "
                        f"{c['value_first']['exact']:.4f} "
                        f"({c['value_first']['n']}) |")
    return "\n".join(rows)


def keypos_group_facts(path) -> dict:
    d = load(path)
    if d is None:
        return {}
    out = {}
    for tag, groups in d["cells"].items():
        for sp, c in groups.items():
            base = f"kp_{tag}_{GROUP_LABEL.get(sp, sp)}"
            out[f"{base}_key_first"] = f"{c['key_first']['exact']:.4f}"
            out[f"{base}_value_first"] = f"{c['value_first']['exact']:.4f}"
            out[f"{base}_key_first_n"] = str(c["key_first"]["n"])
            out[f"{base}_value_first_n"] = str(c["value_first"]["n"])
    return out


def safety_facts(sums) -> dict:
    """The extreme cells of the safe-to-unsafe ratio, so prose can cite them.

    The ratio is (malformed + refused) / wrong. A cell at 0.000 means every
    failure in it is a structure the interpreter accepted and ran.
    """
    cells = []
    for r in RUNGS:
        s = sums.get(r)
        if s is None:
            continue
        for k in GROUPS:
            try:
                p = g(s, k, "greedy")["pooled_do_not_headline"]
            except KeyError:
                continue
            if p["wrong"] == 0:
                continue
            cells.append((("%s %s" % (r, GROUP_LABEL[k])),
                          (p["malformed"] + p["refused"]) / p["wrong"]))
    if not cells:
        return {}
    hi = max(cells, key=lambda c: c[1])
    zero = [c[0] for c in cells if c[1] == 0.0]
    return {"safe_unsafe_max": f"{hi[1]:.3f}",
            "safe_unsafe_max_cell": hi[0],
            "safe_unsafe_cells": str(len(cells)),
            "safe_unsafe_below_one": str(sum(1 for c in cells if c[1] < 1.0)),
            "safe_unsafe_zero_cells": ("none" if not zero
                                       else ", ".join(zero))}


def tpose_facts(dirpath, suffix="") -> dict:
    """Every cell of the transposed census as a fact, so prose can cite one.

    Keys are tp_RUNG_VERSION_GROUP_CATEGORY and the value is the count over
    that cell's own denominator. A category with no items in a cell is 0 over
    that denominator rather than absent, so a citation cannot silently become
    a blank.
    """
    out = {}
    for r in RUNGS:
        rep = load(os.path.join(dirpath, f"xmode_{r}{suffix}.json"))
        if rep is None:
            continue
        for run in rep["runs"].values():
            by = run.get("counts_by_group") or {}
            groups = []
            for key in by:
                sp = key.split("|")[1]
                if sp not in groups:
                    groups.append(sp)
            for ver in ("original", "transposed"):
                for sp in groups:
                    cells = {k.split("|")[2]: v for k, v in by.items()
                             if k.startswith(f"{ver}|{sp}|")}
                    n = sum(cells.values())
                    if not n:
                        continue
                    for cat in TP_CATS:
                        v = cells.get(cat, 0)
                        out[f"tp_{r}_{ver}_{sp}_{cat}"] = \
                            f"{v} of {n}"
                        out[f"tp_{r}_{ver}_{sp}_{cat}_rate"] = f"{v / n:.4f}"
            c = run["counts"]
            for ver in ("original", "transposed"):
                cells = {k.split("|")[1]: v for k, v in c.items()
                         if k.startswith(ver + "|")}
                n = sum(cells.values())
                if not n:
                    continue
                for cat in TP_CATS:
                    v = cells.get(cat, 0)
                    out[f"tp_{r}_{ver}_all_{cat}"] = f"{v} of {n}"
                    out[f"tp_{r}_{ver}_all_{cat}_rate"] = f"{v / n:.4f}"
    return out


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

    ctl = {}
    for c in CONTROLS:
        s2 = load(os.path.join(a.eval, c, "summary.json"))
        if s2:
            ctl[c] = s2

    parts = ["## Structure exact match, greedy",
             rung_table(sums, "greedy", "exact"),
             "", "## Structure exact match, sampled",
             rung_table(sums, "sampled", "exact"), ""]
    for grp in GROUPS:
        parts += [f"## Per shape, {GROUP_LABEL[grp]}, greedy exact",
                  shape_table(sums, grp, "greedy"), ""]
    parts += ["## Safe failure against wrong executable structure, greedy",
              safety_table(sums, "greedy"), ""]

    for ax in ("key_pos", "qform", "scope_pos", "lexicon"):
        t = axis_table(sums, "mode", "greedy", ax)
        if t:
            parts += [f"## The held-out sentence mode by {ax}, greedy exact",
                      t, ""]
    sba = shape_by_axis(sums, "mode", "greedy", "key_pos")
    if sba:
        parts += ["## The held-out sentence mode, shape against key position",
                  sba, ""]

    fit = fit_table(list(RUNGS) + list(ctl))
    if fit:
        parts += ["## What each rung did to its own training file", fit, ""]
    if ctl:
        parts += ["## The learning rate control",
                  lm_table({**{r: sums[r] for r in RUNGS if r in sums}, **ctl}),
                  ""]

    kpg = keypos_group_table("results/system/keypos_by_group.json")
    if kpg:
        parts += ["## Key position inside every frame group", kpg, ""]
    pkp = parser_keypos_table("results/system/parser_by_keypos.json")
    if pkp:
        parts += ["## The reference parser on the same split", pkp, ""]
    kpd = keypos_draw_table("results/system/keypos_train_draw.json")
    kpm = keypos_mode_table("results/system/keypos_by_mode.json")
    gro = grid_order_table("results/system/grid_key_order.json",
                           "results/system/grid_overlap.json")
    if kpd:
        parts += ["## Key position in the training draw", kpd, ""]
    if kpm:
        parts += ["## Value-first items per trained sentence mode", kpm, ""]
    if gro:
        parts += ["## Operand order in the grid draws", gro, ""]

    tp = tpose_table(a.tpose)
    tpg = tpose_group_table(a.tpose)
    if tp:
        parts += ["## The transposed operand test", tp, ""]
    if tpg:
        parts += ["## The transposed operand test, per frame group", tpg, ""]
    tpb = tpose_table(a.tpose, "_both")
    tpbg = tpose_group_table(a.tpose, "_both")
    if tpb:
        parts += ["## The same test after a fine tune that showed both "
                  "operand orders", tpb, ""]
    if tpbg:
        parts += ["## That test per frame group", tpbg, ""]
    ftc = ft_cost_table(a.eval)
    if ftc:
        parts += ["## What the 1,024 grids cost the groups already read",
                  ftc, ""]

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
    fx.update(tpose_facts(a.tpose))
    fx.update(safety_facts(sums))
    KP = "results/system/keypos_train_draw.json"
    KM = "results/system/keypos_by_mode.json"
    GO = "results/system/grid_key_order.json"
    GV = "results/system/grid_overlap.json"
    fx.update(draw_facts(KP, KM, GO))
    fx.update(keypos_group_facts("results/system/keypos_by_group.json"))
    fx.update(parser_keypos_facts("results/system/parser_by_keypos.json"))
    fx.update({("tpb" + k[2:]): v for k, v in
               tpose_facts(a.tpose, "_both").items()})
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
        tmpl = tmpl.replace("{{RUNG_CFG}}", rung_cfg_table(sums))
        tmpl = tmpl.replace("{{FIT}}", fit)
        tmpl = tmpl.replace("{{CONTROL}}", lm_table(
            {**{r: sums[r] for r in RUNGS if r in sums}, **ctl}) if ctl else "")
        tmpl = tmpl.replace("{{ARTIFACTS}}", artifacts_table(
            collect_artifacts(a, sums, lms)))
        for ax, ph in (("qform", "QFORM"), ("scope_pos", "SCOPEPOS")):
            tmpl = tmpl.replace("{{" + ph + "}}",
                                axis_table(sums, "mode", "greedy", ax))
        tmpl = tmpl.replace("{{KEYPOS}}",
                            axis_table(sums, "mode", "greedy", "key_pos"))
        tmpl = tmpl.replace("{{SHAPE_KEYPOS}}", sba)
        tmpl = tmpl.replace("{{KEYPOS_GROUP}}", kpg)
        tmpl = tmpl.replace("{{PARSER_KEYPOS}}", pkp)
        tmpl = tmpl.replace("{{TPOSE_BOTH}}", tpb)
        tmpl = tmpl.replace("{{TPOSE_BOTH_GROUP}}", tpbg)
        tmpl = tmpl.replace("{{KEYPOS_DRAW}}", kpd)
        tmpl = tmpl.replace("{{KEYPOS_MODE}}", kpm)
        tmpl = tmpl.replace("{{GRID_ORDER}}", gro)
        tmpl = tmpl.replace("{{TPOSE}}", tp)
        tmpl = tmpl.replace("{{TPOSE_GROUP}}", tpg)
        tmpl = tmpl.replace("{{FT_COST}}", ftc)
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
