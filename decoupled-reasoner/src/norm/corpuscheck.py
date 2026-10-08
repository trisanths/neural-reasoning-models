"""The interpreter against the corpus's own gold, read off the corpus's text.

Nothing in this file builds a structure. `src/corpus/relations.py` builds the
instance, the corpus frame writes the pages and the question, and the corpus
records the gold answer. The only thing this lane supplies is a reader and an
interpreter: `src/norm/parse.py` turns the text into a `src/norm/lang.py`
program and `src/norm/interp.py` executes it. An answer is scored against the
gold the corpus wrote for that question.

That makes it a coverage test of the representation rather than of the
generator. If a corpus family does not appear here at 1.000 then the language
cannot say what that family says, whoever wrote the words.

A distractor instance of another family is served on the same store, as the
corpus serves one, and half the items serve it before the answering pages.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import random
import time
from collections import Counter, defaultdict

from src.corpus import relations
from src.corpus.build import structurally_ok
from src.corpus.frames import global_reserved
from src.corpus.lexicon import Lexicon, reserved_words
from src.norm.interp import run
from src.norm.parse import parse
from src.norm.render import frame_by_id, frames

DEPTHS = (1, 2, 3, 4, 6, 8)
_RESERVED: dict = {}
_GLOBAL = None


def lex_for(fid, rng):
    global _GLOBAL
    fr, _ = frames()
    if _GLOBAL is None:
        _GLOBAL = global_reserved(fr)
    if fid not in _RESERVED:
        _RESERVED[fid] = reserved_words(frame_by_id(fid))
    return Lexicon(rng, _RESERVED[fid], _GLOBAL)


def instance(family, fid, seed, depth, n_problems=6):
    rng = random.Random(seed * 7919 + 13)
    lex = lex_for(fid, random.Random(seed * 104729 + 7))
    kw = {"n_problems": n_problems}
    if family in relations.DEPTH_STRUCTURES:
        kw["depth"] = depth
    return relations.STRUCTURES[family](rng, lex, **kw)


def items(family, fid, seed, depth, preamble, distractor_first):
    """(question, text) for one corpus instance in one frame."""
    fr = frame_by_id(fid)
    inst = instance(family, fid, seed, depth)
    others = [f for f in relations.STRUCTURES if f != family]
    dfam = others[seed % len(others)]
    dkw = {"depth": min(depth, 2)} if dfam in relations.DEPTH_STRUCTURES else {}
    dinst = relations.STRUCTURES[dfam](
        random.Random(seed * 7919 + 61_000_000),
        lex_for(fid, random.Random(seed * 104729 + 61_000_000)),
        n_problems=1, **dkw)
    own = [fr.page(s, f, preamble) for s, f in inst.pages]
    other = [fr.page(s, f, preamble) for s, f in dinst.pages]
    pages = (other + own) if distractor_first else (own + other)
    out = []
    for q in inst.questions:
        out.append((q, inst, "\n\n".join(pages + [fr.question(q)])))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/norm/corpus")
    ap.add_argument("--stride", type=int, default=1,
                    help="use every Nth frame")
    ap.add_argument("--seed", type=int, default=20260830)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    fr, bank = frames()
    used = fr[::args.stride]
    rng = random.Random(args.seed)

    cells = defaultdict(Counter)
    reasons = Counter()
    fails = []
    t0 = time.time()
    n = 0
    recpath = os.path.join(args.out, "records.jsonl.gz")
    with gzip.open(recpath, "wt") as sink:
        for fi, f in enumerate(used):
            for family in sorted(relations.STRUCTURES):
                depths = DEPTHS if family in relations.DEPTH_STRUCTURES else (0,)
                for depth in depths:
                    seed = args.seed + fi * 977 + depth
                    pre = rng.randrange(0, 13)
                    dfirst = bool(rng.getrandbits(1))
                    try:
                        got = items(family, f.fid, seed, depth, pre, dfirst)
                    except Exception as exc:
                        cells[(family, depth)]["build_error"] += 1
                        reasons[f"build {family}: {exc}"[:120]] += 1
                        continue
                    for q, inst, text in got:
                        n += 1
                        c = cells[(family, depth)]
                        c["n"] += 1
                        keep = structurally_ok(q, inst)
                        c["kept"] += int(keep)
                        p = parse(text, f.fid)
                        c["parsed"] += int(p.ok)
                        rec = {"family": family, "depth": depth,
                               "fid": f.fid, "qid": q.qid, "kept": keep,
                               "gold": str(q.answer), "parsed": p.ok,
                               "reason": p.reason, "shape_read": p.shape}
                        if p.ok:
                            r = run(p.program)
                            rec["executed"] = r.ok
                            rec["answer"] = r.text
                            rec["correct"] = bool(r.ok and r.text == str(q.answer))
                            c["executed"] += int(r.ok)
                            c["correct"] += int(rec["correct"])
                            c["kept_correct"] += int(rec["correct"] and keep)
                            if not rec["correct"]:
                                reasons[f"{family}: "
                                        f"{r.reason or 'wrong answer'}"[:120]] += 1
                        else:
                            rec["executed"] = rec["correct"] = False
                            reasons[f"{family}: {p.reason}"[:120]] += 1
                        if not rec["correct"] and len(fails) < 60:
                            fails.append(dict(rec, text=text[:1200]))
                        sink.write(json.dumps(rec) + "\n")
    dt = time.time() - t0

    rows = {}
    for (family, depth), c in sorted(cells.items()):
        if not c["n"]:
            continue
        rows[f"{family}@d{depth}" if depth else family] = {
            "n": c["n"], "kept": c["kept"],
            "parsed": round(c["parsed"] / c["n"], 6),
            "executed": round(c["executed"] / c["n"], 6),
            "exact": round(c["correct"] / c["n"], 6),
            "exact_on_kept": (round(c["kept_correct"] / c["kept"], 6)
                              if c["kept"] else None),
        }
    summary = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "bank": bank, "frames_used": len(used), "stride": args.stride,
        "n_items": n, "seconds": round(dt, 1),
        "note": ("gold is the corpus's own answer for that question; the text "
                 "is the corpus frame's own rendering; a distractor instance "
                 "of another family is served alongside"),
        "per_family_depth": rows,
        "reasons": reasons.most_common(25),
        "records": os.path.abspath(recpath),
    }
    with open(os.path.join(args.out, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    if fails:
        with open(os.path.join(args.out, "failures.json"), "w") as fh:
            json.dump(fails, fh, indent=2)
    print(json.dumps({k: v for k, v in summary.items()
                      if k not in ("per_family_depth",)}, indent=2))
    for k, v in rows.items():
        print(f"{k:26s} n={v['n']:6d} parsed={v['parsed']:.4f} "
              f"exact={v['exact']:.4f} kept={v['kept']:6d} "
              f"exact_on_kept={v['exact_on_kept']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
