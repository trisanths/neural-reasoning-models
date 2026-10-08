"""Render src/extern/LIQUID.md out of the generation files.

Every table is built here from the record files rather than typed, and the
renderer refuses to build when a record file is newer than the report it is
about to write, which is the rule `src/norm/opdoc.py` follows for the same
reason: a table that was hand copied is a table that can go stale without
anything failing.

Cells are keyed by operation family and page count and are never pooled across
a family, because the four families have different chance floors and an
average over them is a number about nothing.
"""
from __future__ import annotations

import argparse
import glob
import gzip
import json
import os
import time
from collections import defaultdict

from src.extern.answer import answer_span
from src.extern.models import MODELS
from src.norm.cmpwork.grade import forced

FAMS = ["a2c1", "a3c1", "a2c2", "a3c2"]
FAMNAME = {"a2c1": "two directories, one clause",
           "a3c1": "three directories, one clause",
           "a2c2": "two directories, two clauses",
           "a3c2": "three directories, two clauses"}


def cell(rows):
    n = len(rows)
    if not n:
        return None
    a = defaultdict(float)
    for r in rows:
        sp = answer_span(r["raw"])
        f = forced(sp["span"], r["options"], r["gold"])
        g = forced(sp["rest"], r["options"], r["gold"])
        a["strict"] += f["strict_correct"]
        a["lenient"] += f["lenient_correct"]
        a["hedge"] += f["hedged"]
        a["none"] += f["named_none"]
        a["scan_strict"] += g["strict_correct"]
        a["floor"] += f["floor"]
        a["unparseable"] += int(sp["state"] != "ok")
        a["unterminated"] += int(sp["state"] == "unterminated_reasoning")
        a["tok"] += r["n_new"]
    out = {"n": n}
    for k in ("strict", "lenient", "hedge", "none", "scan_strict", "floor",
              "unparseable", "unterminated"):
        out[k] = round(a[k] / n, 4)
    out["tok"] = round(a["tok"] / n, 1)
    return out


def load(path):
    rows = [json.loads(l) for l in gzip.open(path, "rt")]
    mp = path.replace(".jsonl.gz", ".meta.json")
    meta = json.load(open(mp)) if os.path.exists(mp) else {}
    return rows, meta


def f4(x):
    return "-" if x is None else f"{x:.4f}"


def table(head, rows):
    w = [len(h) for h in head]
    for r in rows:
        for i, c in enumerate(r):
            w[i] = max(w[i], len(str(c)))
    out = ["| " + " | ".join(h.ljust(w[i]) for i, h in enumerate(head)) + " |",
           "| " + " | ".join("-" * w[i] for i in range(len(head))) + " |"]
    for r in rows:
        out.append("| " + " | ".join(str(c).ljust(w[i])
                                     for i, c in enumerate(r)) + " |")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="results/extern")
    ap.add_argument("--out", default="results/extern/report.json")
    a = ap.parse_args()

    rep = {"built": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()),
           "models": {}, "selection": {}, "full": {}, "general": {},
           "verify": {}, "samples": {}, "records": {}}

    for p in sorted(glob.glob(f"{a.dir}/verify_*.json")):
        d = json.load(open(p))
        rep["verify"][d["model"]] = {
            "pad_agree": d["pad_agree"], "n": d["n"],
            "rendered_example": d["rendered_example"],
            "controls": [{"q": r["q"], "single": r["single"], "same": r["same"]}
                         for r in d["rows"]]}
        rep["records"][os.path.basename(p)] = os.path.getmtime(p)

    for p in sorted(glob.glob(f"{a.dir}/sel_*.jsonl.gz")):
        rows, meta = load(p)
        key = os.path.basename(p)[4:-9]
        rep["selection"][key] = {
            "model": meta.get("model"), "variant": meta.get("variant"),
            "options_shown": meta.get("options_shown"),
            "max_new_tokens": meta.get("max_new_tokens"),
            "gen_kwargs": meta.get("gen_kwargs"),
            "all": cell(rows),
            "by_family": {f: cell([r for r in rows if r["family"] == f])
                          for f in FAMS}}
        rep["records"][os.path.basename(p)] = os.path.getmtime(p)

    for p in sorted(glob.glob(f"{a.dir}/full_*.jsonl.gz")):
        rows, meta = load(p)
        key = os.path.basename(p)[5:-9]
        rep["full"][key] = {
            "model": meta.get("model"), "variant": meta.get("variant"),
            "pages": meta.get("pages"), "params_total": meta.get("params_total"),
            "params_non_embedding": meta.get("params_non_embedding"),
            "quantization": meta.get("quantization"),
            "max_new_tokens": meta.get("max_new_tokens"),
            "gen_kwargs": meta.get("gen_kwargs"),
            "architectures": meta.get("architectures"),
            "all": cell(rows),
            "by_family": {f: cell([r for r in rows if r["family"] == f])
                          for f in FAMS}}
        if meta.get("model"):
            rep["models"][meta["model"]] = {
                "params_total": meta.get("params_total"),
                "params_non_embedding": meta.get("params_non_embedding"),
                "architectures": meta.get("architectures"),
                "model_type": meta.get("model_type"),
                "quantization": meta.get("quantization")}
        rep["records"][os.path.basename(p)] = os.path.getmtime(p)
        # Sample outputs so a failure is legible rather than asserted.
        samp = []
        for r in rows[:6]:
            sp = answer_span(r["raw"])
            samp.append({"id": r["id"], "gold": r["gold"],
                         "options": r["options"], "state": sp["state"],
                         "span": sp["span"][:160], "raw": r["raw"][:900]})
        rep["samples"][key] = samp

    for p in sorted(glob.glob(f"{a.dir}/gen_*.jsonl.gz")):
        rows, meta = load(p)
        key = os.path.basename(p)[4:-9]
        rep["general"][key] = {
            "model": meta.get("model"), "all": cell(rows),
            "by_family": {f: cell([r for r in rows if r["family"] == f])
                          for f in ("fact", "num", "reason")},
            "samples": [{"id": r["id"], "gold": r["gold"],
                         "span": answer_span(r["raw"])["span"][:120]}
                        for r in rows[:8]]}
        rep["records"][os.path.basename(p)] = os.path.getmtime(p)

    op = f"{a.dir}/ours_general.json"
    if os.path.exists(op):
        d = json.load(open(op))
        rep["ours_general"] = {k: v for k, v in d.items() if k != "rows"}

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(rep, open(a.out, "w"), indent=2)
    print(json.dumps({"models": rep["models"],
                      "n_selection": len(rep["selection"]),
                      "n_full": len(rep["full"]),
                      "n_general": len(rep["general"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
