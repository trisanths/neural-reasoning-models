"""The closed book table, with the published figures beside the reproduction.

PUBLISHED holds what Liquid publish for the LFM2 generation. They are quoted
here so a reproduction can be read against them in the same row, and they are
labelled with the model they belong to: the numbers in the LFM2 table are not
LFM2.5 numbers and putting an LFM2.5 result under a 43.43 that belongs to
LFM2-350M would be the kind of mismatch an external reader finds first.

`results/extern/bench` now holds three different record shapes. The closed book
runs written by `src/extern/bench.py` carry `acc` and `floor`; the retrieval
cells written by `src/extern/cell2.py` and `src/extern/retrieval_mmlu.py` carry
per arm records and no top level accuracy; the GSM8K runs written by
`src/extern/gsm4.py` carry per arm records too. This builder reads the first
shape, and it names the files of the other two in the document instead of
skipping them in silence, because the failure this file has already had was a
row going missing without anyone noticing.

That failure is worth stating plainly at the top of the source, since it is the
reason for the shape checks below. The generated table stopped regenerating and
sat for 152 commits holding only the two uncalibrated LFM2-350M configurations,
0.3950 chat and 0.3550 completion without a bos token, and not the calibrated
0.4300. Anyone quoting it put the external baseline up to 7.9 points below its
calibrated value, which narrows the gap in this project's favour on the one
comparison the thesis turns on.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import time

# Liquid's published figures for the LFM2 generation, as supplied to this lane.
PUBLISHED = {
    ("LiquidAI/LFM2-350M", "mmlu"): 43.43,
    ("LiquidAI/LFM2-350M", "gsm8k"): 30.1,
    ("LiquidAI/LFM2-1.2B", "mmlu"): 55.23,
    ("LiquidAI/LFM2-1.2B", "gsm8k"): 58.3,
}

# What the LFM2.5 cards publish instead. No MMLU or GSM8K figure appears on
# them, so those cells have no published counterpart and are left empty rather
# than compared against a different generation's number.
LFM25_CARD = {
    "LiquidAI/LFM2.5-350M": {"GPQA Diamond": 30.64, "MMLU-Pro": 20.01,
                             "IFEval": 76.96},
}

# The configuration that reproduces the model's published MMLU figure, and so
# the only row any comparison against LFM2-350M may use. Named here rather than
# inferred, so that a row losing its bos flag cannot quietly become the
# calibrated one.
CALIBRATED = ("LiquidAI/LFM2-350M", "mmlu", "completion", True)

# Fields a closed book row cannot be built without.
NEED = ("model", "task", "n", "floor")


def tbl(head, rows):
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


def accuracy(d):
    """The accuracy field this record shape uses, with the label for it."""
    if "acc" in d:
        return d["acc"], (f"norm {d['acc_norm']:.4f}" if "acc_norm" in d
                          else "-")
    if "strict_match" in d:
        return d["strict_match"], (f"flexible {d['flexible_extract']:.4f}"
                                   if "flexible_extract" in d else "-")
    return None, None


def row_for(path):
    """One table row, or the reason this file does not make one."""
    try:
        d = json.load(open(path))
    except (ValueError, OSError) as exc:                    # noqa: BLE001
        return None, f"{type(exc).__name__}: {exc}"
    if not isinstance(d, dict):
        return None, "not a JSON object"
    missing = [k for k in NEED if k not in d]
    acc, extra = accuracy(d)
    if acc is None:
        missing.append("acc or strict_match")
    if missing:
        have = "arms" if "arms" in d else ("records" if "records" in d
                                           else "no per item block")
        return None, ("carries no " + ", ".join(missing) + f"; holds {have}")
    pub = PUBLISHED.get((d["model"], d["task"]))
    fmt = d.get("fmt", "-")
    bos = d.get("bos")
    cal = (d["model"], d["task"], fmt, bool(bos)) == CALIBRATED
    return [
        d["model"], d["task"], fmt, d.get("shots", "-"),
        {True: "yes", False: "no", None: "-"}[bos],
        d["n"], f"{d['floor']:.4f}", f"{acc:.4f}", f"{acc * 100:.2f}",
        f"{pub:.2f}" if pub else "-",
        f"{acc * 100 - pub:+.2f}" if pub else "-", extra,
        f"{d.get('params_total', 0):,}" if d.get("params_total") else "-",
        "calibrated" if cal else "",
        os.path.basename(path),
        time.strftime("%Y-%m-%d %H:%M UTC",
                      time.gmtime(os.path.getmtime(path))),
    ], None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="results/extern/bench")
    ap.add_argument("--out", default="results/extern/bench_summary.md")
    a = ap.parse_args()
    rows, other = [], []
    files = sorted(glob.glob(f"{a.dir}/*.json"))
    if not files:
        raise SystemExit(f"no record files under {a.dir}")
    for f in files:
        r, why = row_for(f)
        if r is None:
            other.append((os.path.basename(f), why))
        else:
            rows.append(r)
    if not rows:
        raise SystemExit(
            f"{len(files)} record files under {a.dir} and not one of them "
            "makes a closed book row. Writing an empty table here is how this "
            "file understated the external baseline for 152 commits, so this "
            "is an error. Reasons: "
            + "; ".join(f"{n}: {w}" for n, w in other))
    if not any(r[13] == "calibrated" for r in rows):
        raise SystemExit(
            "no row reproduces LFM2-350M's published MMLU figure, so every "
            "comparison this table feeds would be against an uncalibrated "
            "baseline. Expected a record with model, task, fmt and bos of "
            f"{CALIBRATED}; found "
            + ", ".join(sorted({f"{r[0]} {r[1]} {r[2]} bos={r[4]}"
                                for r in rows})))
    head = ["model", "task", "format", "shots", "bos", "n", "floor", "acc",
            "acc %", "published", "delta", "other", "parameters", "note",
            "record file", "written"]
    md = ["# Public benchmarks, closed book", "",
          f"Built {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} by "
          "`src/extern/bench_report.py` from every record file under "
          f"`{a.dir}`. Every cell states its own n and chance floor. Nothing "
          "is pooled across benchmarks. `published` is Liquid's figure for "
          "the model named in that row and is blank where that model's card "
          "publishes no such figure.", "",
          "The `bos` column is the one to read before quoting any LFM2-350M "
          "number, and a dash in it means the run did not record the flag "
          "rather than that the token was absent. The bos token is worth 7.5 "
          "points at n=200 on this benchmark, and the row marked calibrated "
          "is the only one that reproduces the 43.43 the model card "
          "publishes. The other two MMLU rows for that model are "
          "measurements of a prompt format, not of the model, and neither "
          "may stand in for it in a comparison.", "",
          tbl(head, rows), ""]
    if other:
        md += ["## Record files that do not make a closed book row", "",
               "These are measurements of something else, and they are named "
               "here rather than dropped so that a file going missing from "
               "the table above is visible.", "",
               tbl(["record file", "why not"],
                   [[n, w] for n, w in other]), ""]
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w").write("\n".join(md) + "\n")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
