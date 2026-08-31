"""Fill src/extern/LIQUID.tmpl.md from results/extern/report.json.

The template holds the prose and named holes; every number comes from the
report, so a table here cannot disagree with the record file it was built
from. This is the arrangement `src/norm/opdoc.py` uses and it is here for the
same reason.
"""
from __future__ import annotations

import argparse
import json
import os
import time

FAMS = ["a2c1", "a3c1", "a2c2", "a3c2"]
FAMNAME = {"a2c1": "two directories, one clause",
           "a3c1": "three directories, one clause",
           "a2c2": "two directories, two clauses",
           "a3c2": "three directories, two clauses"}
SHORT = {"LiquidAI/LFM2.5-350M": "LFM2.5-350M",
         "LiquidAI/LFM2.5-1.2B-Instruct": "LFM2.5-1.2B-Instruct",
         "LiquidAI/LFM2.5-1.2B-Thinking": "LFM2.5-1.2B-Thinking",
         "LiquidAI/LFM2.5-8B-A1B": "LFM2.5-8B-A1B",
         "Qwen/Qwen3.5-9B": "Qwen3.5-9B"}
VNAME = {"bare": "bare", "reader": "reader", "worked": "worked",
         "options": "worked + options shown"}


def f4(x):
    return "-" if x is None else f"{x:.4f}"


def tbl(head, rows):
    if not rows:
        return "(no rows)"
    w = [len(str(h)) for h in head]
    for r in rows:
        for i, c in enumerate(r):
            w[i] = max(w[i], len(str(c)))
    o = ["| " + " | ".join(str(h).ljust(w[i]) for i, h in enumerate(head))
         + " |",
         "| " + " | ".join("-" * w[i] for i in range(len(head))) + " |"]
    for r in rows:
        o.append("| " + " | ".join(str(c).ljust(w[i])
                                   for i, c in enumerate(r)) + " |")
    return "\n".join(o)


def t_models(rep):
    rows = []
    for m, d in sorted(rep["models"].items(),
                       key=lambda kv: kv[1].get("params_total") or 0):
        rows.append([SHORT.get(m, m),
                     f"{d['params_total']:,}" if d.get("params_total") else "-",
                     f"{d['params_non_embedding']:,}"
                     if d.get("params_non_embedding") else "-",
                     (d.get("architectures") or ["-"])[0],
                     d.get("quantization") or "none"])
    return tbl(["model", "parameters, counted from the checkpoint",
                "non embedding", "architecture", "quantisation"], rows)


def t_verify(rep):
    rows = []
    for m, d in sorted(rep["verify"].items()):
        ok = sum(1 for c in d["controls"][:5]
                 if c["single"].strip())
        rows.append([SHORT.get(m, m), f"{d['pad_agree']}/{d['n']}",
                     f"{ok}/5"])
    return tbl(["model", "batched matches unbatched",
                "control questions answered"], rows)


def t_selection(rep):
    rows = []
    for k, d in sorted(rep["selection"].items()):
        c = d["all"]
        rows.append([SHORT.get(d["model"], d["model"]),
                     VNAME.get(d["variant"], d["variant"]),
                     "yes" if d["options_shown"] else "no",
                     c["n"], f4(c["floor"]), f4(c["strict"]),
                     f4(c["lenient"]), f4(c["hedge"]), f4(c["none"]),
                     f4(c["unparseable"]), c["tok"]])
    return tbl(["model", "prompt", "options shown", "n", "floor", "strict",
                "lenient", "hedge", "no option named", "unparseable",
                "mean new tokens"], rows)


def t_oneshot(rep, ours):
    """One page, per family, external models beside the project's systems."""
    rows = []
    for f in FAMS:
        o = ours.get(f, {})
        rows.append([FAMNAME[f], o.get("n", "-"), f4(o.get("floor")),
                     "library, one page", f4(o.get("L")), "-", "-", "-", "-"])
        rows.append([FAMNAME[f], o.get("n", "-"), f4(o.get("floor")),
                     "project reader, 45.5M, no gradient",
                     f4(o.get("N")), f4(o.get("N")), "-",
                     f4(o.get("N_declined")), "-"])
        for k, d in sorted(rep["full"].items()):
            if not k.endswith("_p1"):
                continue
            c = d["by_family"].get(f)
            if not c:
                continue
            rows.append([FAMNAME[f], c["n"], f4(c["floor"]),
                         SHORT.get(d["model"], d["model"]),
                         f4(c["strict"]), f4(c["lenient"]), f4(c["hedge"]),
                         f4(c["none"]), f4(c["unparseable"])])
    return tbl(["operation family", "n", "floor", "system", "strict",
                "lenient", "hedge", "no option named", "unparseable"], rows)


def t_curve(rep, ours):
    rows = []
    for f in FAMS:
        o = ours.get(f, {})
        rows.append([FAMNAME[f], o.get("n", "-"), f4(o.get("floor")),
                     "library", f4(o.get("L")), f4(o.get("L2")),
                     f4(o.get("L4"))])
        seen = set()
        for k, d in sorted(rep["full"].items()):
            mo = d["model"]
            if mo in seen:
                continue
            seen.add(mo)
            got = {}
            for pg in (1, 2, 4):
                dd = rep["full"].get(f"{k.rsplit('_p', 1)[0]}_p{pg}")
                if dd and dd["by_family"].get(f):
                    got[pg] = dd["by_family"][f]["strict"]
            rows.append([FAMNAME[f], o.get("n", "-"), f4(o.get("floor")),
                         SHORT.get(mo, mo), f4(got.get(1)), f4(got.get(2)),
                         f4(got.get(4))])
    return tbl(["operation family", "n", "floor", "system", "1 page",
                "2 pages", "4 pages"], rows)


def t_general(rep):
    rows = []
    og = rep.get("ours_general")
    if og:
        rows.append(["project reader, 45.5M", og["n"], f4(og["floor"]),
                     f4(og["strict"]), f4(og["lenient"]), "-", "-", "-"])
    for k, d in sorted(rep["general"].items()):
        c = d["all"]
        bf = d["by_family"]
        rows.append([SHORT.get(d["model"], d["model"]), c["n"],
                     f4(c["floor"]), f4(c["strict"]), f4(c["lenient"]),
                     f4(bf["fact"]["strict"]) if bf.get("fact") else "-",
                     f4(bf["num"]["strict"]) if bf.get("num") else "-",
                     f4(bf["reason"]["strict"]) if bf.get("reason") else "-"])
    return tbl(["system", "n", "floor", "strict", "lenient", "factual",
                "numeric", "commonsense"], rows)


def t_samples(rep):
    out = []
    for k, samp in sorted(rep["samples"].items()):
        if not k.endswith("_p1"):
            continue
        d = rep["full"][k]
        out.append(f"\n{SHORT.get(d['model'], d['model'])}, "
                   f"prompt {VNAME.get(d['variant'], d['variant'])}:\n")
        for s in samp[:3]:
            raw = s["raw"].replace("\n", " ")[:300]
            out.append(f"    item {s['id']}  gold {s['gold']}  "
                       f"options {s['options']}\n"
                       f"    state {s['state']}  graded span "
                       f"{s['span']!r}\n"
                       f"    output {raw!r}\n")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", default="results/extern/report.json")
    ap.add_argument("--ours", default="results/extern/ours_oneshot.json")
    ap.add_argument("--tmpl", default="src/extern/LIQUID.tmpl.md")
    ap.add_argument("--out", default="src/extern/LIQUID.md")
    a = ap.parse_args()
    rep = json.load(open(a.report))
    ours = json.load(open(a.ours)) if os.path.exists(a.ours) else {}
    txt = open(a.tmpl).read()
    holes = {
        "built": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()),
        "t_models": t_models(rep), "t_verify": t_verify(rep),
        "t_selection": t_selection(rep), "t_oneshot": t_oneshot(rep, ours),
        "t_curve": t_curve(rep, ours), "t_general": t_general(rep),
        "t_samples": t_samples(rep),
        "n_records": len(rep["records"]),
    }
    for k, v in holes.items():
        txt = txt.replace("{" + k + "}", str(v))
    open(a.out, "w").write(txt)
    print("wrote", a.out, len(txt), "chars")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
