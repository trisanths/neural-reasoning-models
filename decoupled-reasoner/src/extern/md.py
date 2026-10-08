"""Fill src/extern/LIQUID.tmpl.md from results/extern/report.json.

The template holds the prose and named holes; every number comes from the
report, so a table here cannot disagree with the record file it was built
from. This is the arrangement `src/norm/opdoc.py` uses and it is here for the
same reason.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
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
         "prefill": "worked + assistant turn prefilled",
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


# ------------------------------------------------- the hand written verdict

CHECK_FENCE = "```verdict-checks"
CHECK_SPLIT = "<!--checks-->"

# A numeral is a run of digits with no letter against either end and no digit
# across a decimal point, so the 2.5 and the 350 of `LFM2.5-350M` are not
# numerals, `n=400` is, and so is a figure that ends a sentence.
NUM = re.compile(r"(?<![A-Za-z0-9])(?<![0-9]\.)"
                 r"\d[\d,]*(?:\.\d+)?(?![A-Za-z0-9])(?!\.\d)")


def prose_numbers(text: str):
    return [m.group(0).replace(",", "") for m in NUM.finditer(text)]


def wilson(k, n, z=1.959964):
    if not n:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


DERIVED = re.compile(r"^#(count|rate|wilson_lo|wilson_hi)\(([^,]+),([^)]+)\)$")


def resolve(doc, field: str):
    """One value out of a record file, by dotted path or derived metric.

    The derived forms read the per item records of one arm of an arm-per-decode
    file, which is the shape `src/extern/cell2.py` writes, and count the event
    itself rather than inferring it from a stop reason.
    """
    m = DERIVED.match(field)
    if m:
        kind, arm, name = m.group(1), m.group(2).strip(), m.group(3).strip()
        arms = doc.get("arms") or {}
        if arm not in arms:
            raise KeyError(f"no arm {arm!r}; have {sorted(arms)}")
        recs = [r for r in arms[arm]["records"] if "error" not in r]
        n = len(recs)
        k = sum(r[name] for r in recs)
        if kind == "count":
            return k
        if kind == "rate":
            return k / n if n else 0.0
        return wilson(k, n)[0 if kind == "wilson_lo" else 1]
    cur = doc
    for part in field.split("."):
        cur = cur[part]
    return cur


def read_checks(text: str, path: str):
    """The claim block at the foot of the verdict, one claim per line."""
    if CHECK_FENCE not in text:
        raise SystemExit(
            f"{path} carries no {CHECK_FENCE} block. Hand written prose is "
            "spliced into a generated document, so every numeral in it has to "
            "name the record file it came from.")
    body = text.split(CHECK_FENCE, 1)[1].split("```", 1)[0]
    out = []
    for i, line in enumerate(body.splitlines()):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 2)
        if len(parts) != 3:
            raise SystemExit(f"{path}: check line {i} is not "
                             f"'value artifact field': {line!r}")
        out.append(tuple(parts))
    if not out:
        raise SystemExit(f"{path}: the check block is empty")
    return out


def check_verdict(path: str):
    """Refuse to splice hand written prose that disagrees with the records.

    Three ways this raises rather than pasting, because a retracted claim that
    is copied into a generated report on every run does not decay, it
    propagates. A stated value that the record file does not hold. A numeral in
    the prose that no line here accounts for. A claim whose record file is
    newer than the prose quoting it, which is how a report goes stale without
    anyone touching it.
    """
    if not os.path.exists(path):
        raise SystemExit(f"no verdict at {path}; write one or pass --verdict")
    raw = open(path).read()
    prose = raw.split(CHECK_SPLIT, 1)[0].strip()
    if not prose:
        raise SystemExit(f"{path}: no prose above {CHECK_SPLIT}")
    checks = read_checks(raw, path)
    tokens = prose_numbers(prose)
    vt = os.path.getmtime(path)
    seen, bad, docs, arts = [], [], {}, {}
    for value, art, field in checks:
        seen.append(value)
        if art == "literal":
            continue
        if not os.path.exists(art):
            bad.append(f"{value} cites {art}, which does not exist")
            continue
        arts[art] = os.path.getmtime(art)
        if art not in docs:
            docs[art] = json.load(open(art))
        try:
            got = resolve(docs[art], field)
        except Exception as exc:                       # noqa: BLE001
            bad.append(f"{value}: {art} has no {field} ({type(exc).__name__}: "
                       f"{exc})")
            continue
        dec = len(value.split(".")[1]) if "." in value else 0
        want = float(value)
        if round(float(got), dec) != round(want, dec):
            bad.append(f"{field} of {art} is {got}, the verdict says {value}")
        if value.lstrip("0") not in [t.lstrip("0") for t in tokens]:
            bad.append(f"{value} is claimed here and appears nowhere in the "
                       "prose, so the claim block has drifted from the text")
    for art, mt in sorted(arts.items()):
        if mt > vt:
            bad.append(f"{art} is newer than {path}; the prose was written "
                       "against an older run of it")
    for tok in prose_numbers(prose):
        if tok in seen:
            continue
        if "." in tok or len(tok) > 1:
            bad.append(f"the prose says {tok} and no check line accounts "
                       "for it")
    if bad:
        raise SystemExit(f"{path} disagrees with the record files:\n  - "
                         + "\n  - ".join(sorted(set(bad))))
    n_lit = sum(1 for _, a, _ in checks if a == "literal")
    stamp = ", ".join(f"`{os.path.basename(a)}` "
                      + time.strftime("%Y-%m-%d %H:%M UTC",
                                      time.gmtime(m))
                      for a, m in sorted(arts.items()))
    note = (f"Every numeral in the verdict above was checked against "
            f"its record file when this document was built: {len(checks)} "
            f"claims over {len(arts)} files, {n_lit} of them a stated "
            f"constant rather than a measurement. Sources and their write "
            f"times: {stamp}. The check is in "
            f"`src/extern/md.py:check_verdict` and it raises rather than "
            f"warns.")
    return prose + "\n\n" + note


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", default="results/extern/report.json")
    ap.add_argument("--ours", default="results/extern/ours_oneshot.json")
    ap.add_argument("--tmpl", default="src/extern/LIQUID.tmpl.md")
    ap.add_argument("--out", default="src/extern/LIQUID.md")
    ap.add_argument("--verdict", default="results/extern/verdict.md")
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
        "n_sel": max([d["all"]["n"] for d in rep["selection"].values()]
                     or [0]),
        "verdict": check_verdict(a.verdict),
    }
    for k, v in holes.items():
        txt = txt.replace("{" + k + "}", str(v))
    open(a.out, "w").write(txt)
    print("wrote", a.out, len(txt), "chars")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
