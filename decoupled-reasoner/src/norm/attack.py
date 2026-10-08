"""Attacks on the round trip number, because a 1.000 is a bug until it is not.

Five of them. Each one is a way the round trip could read 1.000 without the
parser reading anything.

    mutate      change one value word in the rendered text. The recovered
                structure must change with it and must not equal the original.
                A parser that reconstructed the structure from the shape alone
                would return the original and fail here.
    delete      remove one rule line. The recovered structure must differ or
                the parse must refuse. Silently returning the original is the
                failure.
    crossframe  read frame A's text with frame B's patterns. Refusing is
                fine. Returning a structure that is not the original one is
                the failure being counted.
    truncate    cut the text off before the question. Must refuse.
    equality    two structures differing in one entry must compare unequal,
                so `identical` is testing something.

The mutation and deletion attacks are applied to the last rule line of the
first page, which every shape has.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import time
from collections import Counter

from src.norm.gen import make_for
from src.norm.lang import Table
from src.norm.parse import parse, patterns
from src.norm.render import SHAPES, frames, render


def _rule_lines(text: str):
    """Index of the block holding the first page's rule lines, and its lines."""
    chunks = text.split("\n\n")
    # the block before the next head, which is the first block whose lines all
    # come from one page: take the block just before the second head or the
    # question. The rule block is never the head and never the notes, and the
    # notes are one paragraph, so the block at index 1 or 2 is it.
    for i in (2, 1):
        if i < len(chunks) - 1:
            return i, chunks[i].split("\n"), chunks
    return None, None, chunks


def mutate(text: str, rng) -> str | None:
    i, lines, chunks = _rule_lines(text)
    if i is None:
        return None
    words = sorted({w for ln in lines for w in re.findall(r"\b[a-z][a-z]{5,}\b", ln)})
    if not words:
        return None
    w = rng.choice(words)
    swapped = "zzq" + w[3:] if len(w) > 4 else "zzqxa"
    chunks[i] = chunks[i].replace(w, swapped)
    return "\n\n".join(chunks)


def delete(text: str, rng):
    """Drop one line of the first page's rule block. Returns (text, line)."""
    i, lines, chunks = _rule_lines(text)
    if i is None or len(lines) < 2:
        return None, None
    j = rng.randrange(len(lines))
    chunks[i] = "\n".join(lines[:j] + lines[j + 1:])
    return "\n\n".join(chunks), lines[j]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/norm/attack/summary.json")
    ap.add_argument("--frames", type=int, default=96)
    ap.add_argument("--seed", type=int, default=20260830)
    args = ap.parse_args()
    fr, bank = frames()
    rng = random.Random(args.seed)
    step = max(1, len(fr) // args.frames)
    used = fr[::step]

    c = Counter()
    examples = []
    t0 = time.time()
    for fi, f in enumerate(used):
        for si, shape in enumerate(SHAPES):
            seed = args.seed + fi * 131 + si
            p = make_for(f.fid, shape, seed)
            text = render(p, f.fid, preamble_level=rng.randrange(0, 13))["text"]

            m = mutate(text, rng)
            if m is not None and m != text:
                c["mutate_n"] += 1
                got = parse(m, f.fid)
                if got.ok and got.program == p:
                    c["mutate_unchanged"] += 1
                    if len(examples) < 8:
                        examples.append({"attack": "mutate", "shape": shape,
                                         "fid": f.fid})
                elif got.ok:
                    c["mutate_changed"] += 1
                else:
                    c["mutate_refused"] += 1

            d, dropped = delete(text, rng)
            if d is not None and d != text:
                c["delete_n"] += 1
                got = parse(d, f.fid)
                header = patterns(f.fid)["header"]
                if got.ok and got.program == p:
                    if header is not None and dropped == header:
                        # The table header carries no structure, so dropping
                        # it must leave the structure alone. That is the
                        # attack passing, not failing.
                        c["delete_header_unchanged"] += 1
                    else:
                        c["delete_unchanged"] += 1
                        if len(examples) < 8:
                            examples.append({"attack": "delete",
                                             "shape": shape, "fid": f.fid,
                                             "line": dropped})
                elif got.ok:
                    c["delete_changed"] += 1
                else:
                    c["delete_refused"] += 1

            other = fr[(fi * 7 + si * 13 + 1) % len(fr)]
            if other.fid != f.fid:
                c["crossframe_n"] += 1
                got = parse(text, other.fid)
                if not got.ok:
                    c["crossframe_refused"] += 1
                elif got.program == p:
                    # Two frames can write byte identical text for a given
                    # structure, and then reading it with either is right.
                    try:
                        twin = render(p, other.fid, preamble_level=0)["text"]
                        base = render(p, f.fid, preamble_level=0)["text"]
                    except Exception:
                        twin, base = None, ""
                    key = ("crossframe_same_text" if twin == base
                           else "crossframe_same_leak")
                    c[key] += 1
                else:
                    c["crossframe_other"] += 1

            c["truncate_n"] += 1
            cut = "\n\n".join(text.split("\n\n")[:-1])
            if not parse(cut, f.fid).ok:
                c["truncate_refused"] += 1

            if shape in ("lookup", "inverse") and p.defs[0].kind == "table":
                t = p.defs[0]
                ent = list(t.entries)
                ent[0] = (ent[0][0], ent[0][1] + "x")
                q = type(p)(tuple([Table(t.name, tuple(ent), t.default,
                                         t.ordered)] + list(p.defs[1:])),
                            p.inputs, p.steps, p.answer)
                c["equality_n"] += 1
                c["equality_distinguished"] += int(q != p)

    out = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "bank": bank, "frames_used": len(used), "seconds": round(time.time() - t0, 1),
        "mutate": {"n": c["mutate_n"], "structure_changed": c["mutate_changed"],
                   "refused": c["mutate_refused"],
                   "silently_unchanged": c["mutate_unchanged"]},
        "delete": {"n": c["delete_n"], "structure_changed": c["delete_changed"],
                   "refused": c["delete_refused"],
                   "dropped_the_table_header_no_structure_to_change":
                       c["delete_header_unchanged"],
                   "silently_unchanged": c["delete_unchanged"]},
        "crossframe": {"n": c["crossframe_n"], "refused": c["crossframe_refused"],
                       "returned_the_original_and_both_frames_write_the_same_text":
                           c["crossframe_same_text"],
                       "returned_the_original_on_text_the_other_frame_would_not_write":
                           c["crossframe_same_leak"],
                       "returned_something_else": c["crossframe_other"]},
        "truncate": {"n": c["truncate_n"], "refused": c["truncate_refused"]},
        "equality": {"n": c["equality_n"],
                     "distinguished": c["equality_distinguished"]},
        "examples_of_silent_pass": examples,
    }
    import os
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
