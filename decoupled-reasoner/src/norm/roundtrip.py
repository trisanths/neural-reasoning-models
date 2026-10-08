"""The round trip gate: structure -> render -> structure, over every frame.

Four things are checked on every item and all four must hold for the item to
count as a round trip.

    parsed      the reference parser read the text at all
    identical   the recovered structure equals the one that was rendered,
                by structural equality of the whole program: definitions,
                their entries in order, the inputs, the plan and the answer
    rerender    re-rendering the recovered structure in the same frame gives
                back the same bytes. This is the check that does not go
                through anything the generator and the parser share, so a
                parser that guessed a plan from the shape alone would fail it
    executes    the interpreter returns the same answer for both structures

The JSON persistence is round tripped on every item as well, so the record
file holds structures that reload to what was measured.

Nothing is pooled across shape. The summary reports one row per shape, and
the frame axes separately.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import random
import time
from collections import Counter, defaultdict

from src.norm.gen import make_for
from src.norm.interp import run
from src.norm.lang import program_json, program_load
from src.norm.parse import parse
from src.norm.render import SHAPES, frames, render


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def one(fid: str, shape: str, seed: int, preamble: int) -> dict:
    rec = {"fid": fid, "shape": shape, "seed": seed, "preamble": preamble}
    p = make_for(fid, shape, seed)
    pj = program_json(p)
    rec["json_roundtrip"] = program_load(json.loads(json.dumps(pj))) == p
    rec["program"] = pj
    r = render(p, fid, preamble_level=preamble)
    text = r["text"]
    rec["text_sha"] = sha(text)
    rec["text_len"] = len(text)
    rec["n_defs"] = len(p.defs)
    rec["n_steps"] = len(p.steps)
    got = parse(text, fid)
    rec["parsed"] = got.ok
    rec["reason"] = got.reason
    rec["shape_read"] = got.shape
    if not got.ok:
        rec["identical"] = rec["rerender"] = rec["executes"] = False
        rec["ok"] = False
        return rec
    q = got.program
    rec["identical"] = (q == p)
    try:
        text2 = render(q, fid, preamble_level=preamble)["text"]
        rec["rerender"] = (text2 == text)
    except Exception as exc:
        rec["rerender"] = False
        rec["reason"] = f"rerender: {type(exc).__name__}: {exc}"
    a, b = run(p), run(q)
    rec["answer"] = a.text
    rec["answer_ok"] = a.ok
    rec["executes"] = (a.ok and b.ok and a.value == b.value)
    if not a.ok:
        rec["reason"] = rec["reason"] or f"interpreter refused: {a.reason}"
    rec["ok"] = bool(rec["identical"] and rec["rerender"]
                     and rec["executes"] and rec["json_roundtrip"])
    if not rec["identical"]:
        rec["recovered"] = program_json(q)
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/norm/roundtrip")
    ap.add_argument("--per-frame", type=int, default=1,
                    help="structures per (frame, shape) cell")
    ap.add_argument("--seed", type=int, default=20260830)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    fr, bank = frames()
    rng = random.Random(args.seed)

    t0 = time.time()
    per_shape = defaultdict(Counter)
    per_axis = {ax: defaultdict(Counter) for ax in
                ("lexicon", "mode", "key_pos", "qform", "scope_pos")}
    reasons = Counter()
    failures = []
    n = 0
    recpath = os.path.join(args.out, "records.jsonl.gz")
    with gzip.open(recpath, "wt") as sink:
        for fi, f in enumerate(fr):
            for si, shape in enumerate(SHAPES):
                for rep in range(args.per_frame):
                    seed = args.seed + fi * 1000 + si * 37 + rep
                    pre = rng.randrange(0, 13)
                    rec = one(f.fid, shape, seed, pre)
                    n += 1
                    c = per_shape[shape]
                    for k in ("parsed", "identical", "rerender", "executes",
                              "json_roundtrip", "ok"):
                        c[k] += int(rec[k])
                    c["n"] += 1
                    for ax in per_axis:
                        per_axis[ax][getattr(f, ax)]["ok"] += int(rec["ok"])
                        per_axis[ax][getattr(f, ax)]["n"] += 1
                    if not rec["ok"]:
                        reasons[rec["reason"][:120]] += 1
                        if len(failures) < 40:
                            failures.append(rec)
                    sink.write(json.dumps(rec) + "\n")
    dt = time.time() - t0

    shapes_out = {}
    for shape in SHAPES:
        c = per_shape[shape]
        shapes_out[shape] = {
            "n": c["n"],
            "parsed": round(c["parsed"] / c["n"], 6),
            "identical": round(c["identical"] / c["n"], 6),
            "rerender": round(c["rerender"] / c["n"], 6),
            "executes": round(c["executes"] / c["n"], 6),
            "round_trip": round(c["ok"] / c["n"], 6),
        }
    total_ok = sum(per_shape[s]["ok"] for s in SHAPES)
    summary = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "bank": bank,
        "n_frames": len(fr),
        "n_structures": n,
        "per_frame_shape": args.per_frame,
        "seconds": round(dt, 1),
        "round_trip_all": round(total_ok / n, 6),
        "per_shape": shapes_out,
        "per_axis": {ax: {k: {"n": v["n"], "round_trip": round(v["ok"] / v["n"], 6)}
                          for k, v in sorted(d.items())}
                     for ax, d in per_axis.items()},
        "failure_reasons": reasons.most_common(20),
        "records": os.path.abspath(recpath),
    }
    with open(os.path.join(args.out, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    if failures:
        with open(os.path.join(args.out, "failures.json"), "w") as fh:
            json.dump(failures, fh, indent=2)
    print(json.dumps({k: v for k, v in summary.items()
                      if k != "per_axis"}, indent=2)[:6000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
