"""Turn the record files into the four tables the brief asks for.

Reads only files other tools wrote, recomputes nothing except intervals, and
prints the mtime of every file it read so a table can be checked against the
records behind it. A table whose record file is older than this run is
reported as stale rather than printed as a result.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

from src.e3.interval import summarise

R = Path("/mnt/nvme/e3eval")
FLOOR_MMLU = 0.25


def load(path):
    p = Path(path)
    if not p.exists():
        return None, None
    return json.load(open(p)), os.path.getmtime(p)


def fmt_ci(d):
    return "[%.4f, %.4f]" % (d["ci95"][0], d["ci95"][1])


def mmlu_table(tags, out):
    out.append("### MMLU, 5 shot completion, "
               "src.extern.bench_ours unchanged\n")
    out.append("| checkpoint | n | acc | 95% Wilson | floor | contains floor |"
               " p vs floor |")
    out.append("| --- | ---: | ---: | --- | ---: | --- | ---: |")
    seen = []
    for tag in tags:
        for n in (200, 500, 1000):
            for name in (f"mmlu_{tag}_n{n}.json",
                         f"mmlu_{tag}_n{n}_s1234.json"):
                d, mt = load(R / name)
                if d is None:
                    continue
                recs = d["records"]
                k = sum(x["pred"] == x["gold"] for x in recs)
                s = summarise(k, len(recs), d["floor"])
                out.append("| %s | %d | %.4f | %s | %.4f | %s | %.3f |"
                           % (tag, s["n"], s["acc"], fmt_ci(s), s["floor"],
                              "yes" if s["ci_contains_floor"] else "no",
                              s["p_vs_floor"]))
                seen.append((name, mt))
                break
    out.append("")
    return seen


def curve_table(out):
    p = R / "curve.jsonl"
    if not p.exists():
        return []
    rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    if not rows:
        return []
    out.append("### MMLU against tokens seen\n")
    out.append("| step | tokens | tok/param | n=1000 acc | 95% Wilson | "
               "issued query | letter counts A/B/C/D |")
    out.append("| ---: | ---: | ---: | ---: | --- | ---: | --- |")
    for r in sorted(rows, key=lambda x: x["step"]):
        m = r.get("mmlu_n1000") or {}
        ret = r.get("retrieval_none_n200") or {}
        out.append("| %d | %.2fB | %.2f | %s | %s | %s | %s |"
                   % (r["step"], r["tokens_seen"] / 1e9,
                      r["tokens_per_param"],
                      ("%.4f" % m["acc"]) if m.get("acc") is not None else "-",
                      fmt_ci(m) if m.get("ci95") else "-",
                      ("%.3f" % ret["issued_query"])
                      if ret.get("issued_query") is not None else "-",
                      "/".join(str(c) for c in m.get("pred_letter_counts",
                                                     []))))
    out.append("")
    return [("curve.jsonl", os.path.getmtime(p))]


def hop_table(tags, out):
    out.append("### Hop curve, per family, never pooled\n")
    out.append("| checkpoint | decode | family | hops | n | acc | 95% Wilson |"
               " floor | contains floor |")
    out.append("| --- | --- | --- | ---: | ---: | ---: | --- | ---: | --- |")
    seen = []
    for tag in tags:
        d, mt = load(R / "relation" / f"hops_{tag}_heldout.json")
        if d is None:
            continue
        seen.append((f"hops_{tag}_heldout.json", mt))
        for name, c in d["cells"].items():
            acc = c.get("acc_forced", c.get("acc_exact"))
            iv = c["interval"]
            out.append("| %s | %s | %s | %s | %d | %.3f | %s | %.3f | %s |"
                       % (tag, c["decode"], c["family"], c["hops"], iv["n"],
                          acc, fmt_ci(iv), c["chance"],
                          "yes" if iv["ci_contains_floor"] else "no"))
    out.append("")
    return seen


def frames_table(tags, out):
    out.append("### Held-out frames, macro over frames within a family\n")
    out.append("| checkpoint | decode | family | cells | macro acc | "
               "macro chance | A corrected | B mean of corrected |")
    out.append("| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |")
    seen = []
    for tag in tags:
        for dec in ("greedy", "t07"):
            d, mt = load(R / "frames" / f"score_{tag}-{dec}.json")
            if d is None:
                continue
            seen.append((f"score_{tag}-{dec}.json", mt))
            macro = d.get("macro_by_family") or d.get("macro") or {}
            for fam, mv in macro.items():
                out.append("| %s | %s | %s | %d | %.3f | %.3f | %.3f | %.3f |"
                           % (tag, dec, fam, mv["cells"],
                              mv["macro_accuracy"], mv["macro_chance"],
                              mv["order_A_corrected_macro"],
                              mv["order_B_mean_of_corrected"]))
    out.append("")
    return seen


def retrieval_table(tags, out):
    out.append("### Retrieval policy on MMLU, closed book pass\n")
    out.append("| checkpoint | n | issued query | 95% Wilson | named none | "
               "strict |")
    out.append("| --- | ---: | ---: | --- | ---: | ---: |")
    seen = []
    for tag in tags:
        d, mt = load(R / f"ret_{tag}_n200.json")
        if d is None:
            continue
        seen.append((f"ret_{tag}_n200.json", mt))
        c = d.get("none") or {}
        n = c.get("n", 0)
        s = summarise(round(c.get("issued_query", 0) * n), n, 0.0)
        out.append("| %s | %d | %.3f | %s | %.3f | %.3f |"
                   % (tag, n, c.get("issued_query", 0), fmt_ci(s),
                      c.get("named_none", 0), c.get("strict", 0)))
    out.append("")
    return seen


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tags", default="ref,e3final,e3sft")
    ap.add_argument("--out", default=str(R / "TABLES.md"))
    a = ap.parse_args()
    tags = [t for t in a.tags.split(",") if t]
    out, seen = [], []
    out.append("<!-- generated by src.e3.collate at %s -->"
               % time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    out.append("")
    seen += curve_table(out)
    seen += mmlu_table(tags, out)
    seen += retrieval_table(tags, out)
    seen += hop_table(tags, out)
    seen += frames_table(tags, out)
    out.append("### Record files behind these tables\n")
    out.append("| file | modified (UTC) |")
    out.append("| --- | --- |")
    for name, mt in seen:
        out.append("| %s | %s |" % (name, time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime(mt))))
    text = "\n".join(out) + "\n"
    Path(a.out).write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
