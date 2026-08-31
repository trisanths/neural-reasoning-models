"""The interpreter against the hand-written parsers already on record.

Same episode files, same gold, same grader. The files are the ones
`src/frames/cli.py frames` wrote for the published sweep, 13 frames by 3
families by 100 episodes by 6 questions. `src/frames/parsers.py` is re-run over
them unchanged, and the numbers it produces are the ones to beat.

What this lane runs instead of a regex is the full pipeline: read the text into
a `src/norm/lang.py` structure, then execute the structure with
`src/norm/interp.py`. Two differences from the published parser, both in the
harder direction:

    the published frame-aware parser is handed the question's key. This one
    parses the key out of the question with the frame's own question template.

    the published parser is handed the `src/skillacq/simple.py` system object,
    so it knows the system's name and its fallback word before it reads. This
    one is handed only the frame, and reads the system name, the fallback, the
    table, the general rule and the exception off the page.

It also builds the whole structure rather than the one row the question asks
about, so the same read answers any question about that system.

Grading is `src/frames/score.py` unchanged: forced choice is the headline,
`first` is the lenient tie-break beside it, and the hedge rate, the none rate
and both chance floors travel with every cell. The hedging canary is run on the
same rows and must score 0.000 forced. Nothing is pooled across family or frame.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from collections import Counter

from src.frames import score as sc
from src.frames.forms import (EXC_GENERAL, EXC_QUESTIONS, EXC_SPECIAL,
                              SUB_LAYOUTS, SUB_QUESTIONS, SUB_STATEMENTS,
                              THR_QUESTIONS, THR_STATEMENTS)
from src.frames.generate import FRAMES
from src.frames.parsers import run_parsers
from src.norm.interp import run
from src.norm.lang import Bands, Rule, Table
from src.norm.parse import INT, SCOPE, WORD, compile_template, _named
from src.norm.shapes import assemble

FAMILIES = ("substitution_rule", "exception_rule", "threshold_rule")


class Stub:
    """Stands in for a system object so a frame will build its slot table.

    Every attribute it supplies is overwritten by a capture group before the
    pattern is used, so nothing about the actual system reaches the reader.
    """

    name = "Xx"
    rng_default = "xx"
    general = special_key = special = "xx"
    attr = high = low = "xx"
    limit = 0


_P: dict = {}


def frame_patterns(fname: str) -> dict:
    if fname in _P:
        return _P[fname]
    fr = FRAMES[fname]
    sh = fr.shape
    s = Stub()
    sub, exc, thr = fr._sub_slots(s), fr._exc_slots(s), fr._thr_slots(s)
    _P[fname] = {
        "sub_row": compile_template(SUB_STATEMENTS[sh.sub_stmt], sub,
                                    {"N": SCOPE, "k": WORD, "v": WORD}),
        "sub_fb": compile_template(SUB_LAYOUTS[sh.sub_layout][3], sub,
                                   {"D": WORD}),
        "sub_q": compile_template(SUB_QUESTIONS[sh.sub_q], sub,
                                  {"N": SCOPE, "q": WORD}),
        "exc_gen": compile_template(EXC_GENERAL[sh.exc_gen], exc,
                                    {"N": SCOPE, "G": WORD}),
        "exc_spc": compile_template(EXC_SPECIAL[sh.exc_spc], exc,
                                    {"N": SCOPE, "SK": WORD, "SP": WORD}),
        "exc_q": compile_template(EXC_QUESTIONS[sh.exc_q], exc,
                                  {"N": SCOPE, "q": WORD}),
        "thr_rule": compile_template(THR_STATEMENTS[sh.thr_stmt], thr,
                                     {"N": SCOPE, "ATTR": WORD, "L": INT,
                                      "HI": WORD, "LO": WORD}),
        "thr_q": compile_template(THR_QUESTIONS[sh.thr_q], thr,
                                  {"N": SCOPE, "ATTR": WORD, "q": INT}),
    }
    return _P[fname]


def _scan(pat, lines):
    out = []
    for ln in lines:
        got = _named(pat[0], pat[1], ln)
        if got is not None:
            out.append(got)
    return out


def read_structure(fname: str, family: str, pages: str, question: str):
    """Text to structure. Returns (program, reason) with one of them None."""
    P = frame_patterns(fname)
    lines = [ln for ch in pages.split("\n\n") for ln in ch.split("\n") if ln]
    if family == "substitution_rule":
        q = _named(*P["sub_q"], question)
        if q is None:
            return None, "the question does not read in this frame"
        rows = _scan(P["sub_row"], lines)
        if not rows:
            return None, "no routing row on the pages"
        fb = _scan(P["sub_fb"], lines)
        name = q.get("N") or (rows[0].get("N") if rows else None)
        if name is None:
            return None, "nothing names the system"
        t = Table(name, tuple((r["k"], r["v"]) for r in rows),
                  fb[0]["D"] if fb else None)
        return assemble("lookup", tables=[t], inputs=(("x", q["q"]),)), None
    if family == "exception_rule":
        q = _named(*P["exc_q"], question)
        if q is None:
            return None, "the question does not read in this frame"
        gen = _scan(P["exc_gen"], lines)
        spc = _scan(P["exc_spc"], lines)
        if not gen:
            return None, "no general rule on the pages"
        if len({g["G"] for g in gen}) > 1:
            return None, "the pages state two general rules"
        r = Rule(q["N"], gen[0]["G"],
                 tuple((s["SK"], s["SP"]) for s in spc))
        return assemble("lookup_general", rule=r,
                        inputs=(("x", q["q"]),)), None
    if family == "threshold_rule":
        q = _named(*P["thr_q"], question)
        if q is None:
            return None, "the question does not read in this frame"
        rules = _scan(P["thr_rule"], lines)
        if not rules:
            return None, "no threshold rule on the pages"
        if len(rules) > 1:
            return None, "the pages state two thresholds"
        r = rules[0]
        b = Bands(q["N"], q["ATTR"], (int(r["L"]) + 1,), (r["LO"], r["HI"]))
        return assemble("classify", bands=b,
                        inputs=(("x", int(q["q"])),)), None
    return None, f"no reader for {family}"


def determinacy(prog, family: str, gold: str) -> str:
    """Whether the served page states exactly one answer to the question.

    Read off the recovered structure and the gold, never off the generator.

    page_ambiguous        the page states two different values for the key the
                          question asks about, so the text has two answers and
                          any single answer is a guess
    gold_contradicts_page the page states exactly one value for that key and
                          the recorded gold is a different word
    clean                 the page states one answer and the gold agrees
    """
    if prog is None:
        return "unread"
    if family != "substitution_rule":
        return "clean"
    t = prog.defs[0]
    key = prog.inputs[0][1]
    hits = [v for k, v in t.entries if k == key]
    if len(set(hits)) > 1:
        return "page_ambiguous"
    stated = hits[0] if hits else t.default
    return "clean" if stated == gold else "gold_contradicts_page"


def norm_rows(episodes, family, fname):
    rows, reasons = [], Counter()
    for i, ep in enumerate(episodes):
        pages = "\n\n".join(d["text"] for d in ep["documents"])
        for q in ep["questions"]:
            prog, why = read_structure(fname, family, pages, q["text"])
            if prog is None:
                ans, reason = "", why
            else:
                r = run(prog)
                ans = r.text
                reason = "" if r.ok else r.reason
            if reason:
                reasons[reason[:90]] += 1
            rows.append({"ep": i, "qid": q["qid"], "family": family,
                         "gold": q["answer"], "candidates": ep["candidates"],
                         "twin_candidates": ep.get("twin_candidates", []),
                         "chunks": [d["text"] for d in ep["documents"]],
                         "served": True, "answer": ans, "reason": reason,
                         "determinacy": determinacy(prog, family,
                                                    q["answer"])})
    return rows, reasons


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--eps", default="/home/ec2-user/frames/eps")
    ap.add_argument("--out", default="results/norm/baselines")
    ap.add_argument("--problems", type=int, default=6)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    manifest = json.load(open(os.path.join(args.eps, "manifest.json")))
    cells, allreasons = [], Counter()
    t0 = time.time()
    reccount = 0
    with open(os.path.join(args.out, "records.jsonl"), "w") as sink:
        for m in manifest:
            if m["condition"] != "textbook":
                continue
            eps = [json.loads(l) for l in open(m["path"])]
            fam, fname = m["family"], m["frame"]
            rows, reasons = norm_rows(eps, fam, fname)
            allreasons += reasons
            vocab = sc.nonce_vocab(rows)
            interp = sc.summarize(rows, vocab, "answer")
            canary = sc.summarize(sc.canary_rows(rows), vocab, "answer")
            det = Counter(r["determinacy"] for r in rows)
            clean = [r for r in rows if r["determinacy"] == "clean"]
            cell = {"frame": fname, "lexicon": m["lexicon"],
                    "shape": m["shape"], "family": fam,
                    "interpreter": interp,
                    "canary_forced": canary["acc_forced"],
                    "canary_hedge": canary["hedge_rate"],
                    "declined": sum(1 for r in rows if r["reason"]) / len(rows),
                    "determinacy": dict(det),
                    "interpreter_on_clean": sc.summarize(
                        clean, sc.nonce_vocab(clean), "answer") if clean else None}
            if fam in ("substitution_rule", "exception_rule"):
                prows = run_parsers(eps, fam, fname, args.problems)
                pv = sc.nonce_vocab(prows)
                cell["frame_aware_parser"] = sc.summarize(
                    prows, pv, "answer_frame_aware")
                cell["native_tuned_parser"] = sc.summarize(
                    prows, pv, "answer_native_tuned")
                keys = {(r["ep"], r["qid"]) for r in clean}
                pclean = [r for r in prows if (r["ep"], r["qid"]) in keys]
                cell["frame_aware_parser_on_clean"] = sc.summarize(
                    pclean, sc.nonce_vocab(pclean),
                    "answer_frame_aware") if pclean else None
            cells.append(cell)
            for r in rows:
                sink.write(json.dumps({k: v for k, v in r.items()
                                       if k != "chunks"}) + "\n")
                reccount += 1
    out = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "episodes_dir": args.eps,
        "n_cells": len(cells), "n_items": reccount,
        "seconds": round(time.time() - t0, 1),
        "grader": "src/frames/score.py, unchanged",
        "cells": cells,
        "decline_reasons": allreasons.most_common(20),
        "records": os.path.abspath(os.path.join(args.out, "records.jsonl")),
    }
    with open(os.path.join(args.out, "summary.json"), "w") as fh:
        json.dump(out, fh, indent=2)

    print("%-22s %-18s %5s %7s %7s %6s %6s %7s %7s %8s %8s %6s %8s %8s"
          % ("frame", "family", "n", "forced", "first", "hedge", "none",
             "chance", "chncPg", "parserFA", "declined", "nClean",
             "interpCln", "parserCln"))
    for c in cells:
        s = c["interpreter"]
        fa = c.get("frame_aware_parser", {}).get("acc_forced")
        ic = c.get("interpreter_on_clean") or {}
        pc = c.get("frame_aware_parser_on_clean") or {}
        print("%-22s %-18s %5d %7.3f %7.3f %6.3f %6.3f %7.3f %7.3f %8s %8.3f "
              "%6d %8s %8s"
              % (c["frame"], c["family"], s["n"], s["acc_forced"],
                 s["acc_first"], s["hedge_rate"], s["none_rate"],
                 s["chance_cand"], s["chance_page"],
                 "n/a" if fa is None else f"{fa:.3f}", c["declined"],
                 ic.get("n", 0),
                 f"{ic['acc_forced']:.3f}" if ic else "n/a",
                 f"{pc['acc_forced']:.3f}" if pc else "n/a"))
    print("determinacy totals:",
          dict(sum((Counter(c["determinacy"]) for c in cells), Counter())))
    print("canary forced (must be 0):",
          sorted({round(c["canary_forced"], 6) for c in cells}))
    print("decline reasons:", allreasons.most_common(6))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
