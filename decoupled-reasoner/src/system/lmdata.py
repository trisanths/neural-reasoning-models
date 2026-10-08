"""The same normalizer task, written as text for the 350M language model.

The encoder-decoder rungs read `src/norm/ntok.py` ids and write a closed target
vocabulary. The corpus checkpoint reads `data/tokenizer_v2.json` and writes
text, so the task has to be restated in text without being changed. Three
rules keep it the same task:

    the page text is the page text `src/norm/render.py` wrote, with each
    invented word replaced in place by its numbered copy slot, which is what
    `src/norm/ntok.py:InputVocab.encode` hands the encoder-decoder. Same
    information, same spelling burden, and punctuation and layout untouched.

    the target is the token sequence `src/norm/ntok.py:serialize` produces,
    joined by single spaces. Splitting it on whitespace recovers the token
    list `deserialize` consumes, so both systems are graded by the same
    `src/norm/neval.py:classify_emission` against the same gold program.

    the frames are `src/norm/ndata.py:split_frames`, unchanged, and the
    evaluation items are the ones already on disk under `data/norm/`.

The prompt carries the world header. Without it this checkpoint issues no
retrieval round and runs to the token cap, which the harness gate reproduces.
There is no retrieval here because the page is in the prompt, so the trace is
the flat prompt-and-target shape `src/corpus/sft.py:flat_trace` uses for the
plan component: header, question marker, page, answer marker, structure, end.
"""

from __future__ import annotations

import argparse
import json
import os
import time

import numpy as np

from src.norm import ndata, ntok
from src.norm.lang import program_load

_TOKENIZER_REPO = "data/tokenizer_v2.json"
_TOKENIZER_BOX = "/home/ec2-user/data/tokenizer_v2.json"
# The repo copy is preferred and the box copy is where it actually lives here.
# src/system/lmeval.py takes this as its default, and a relative path that
# does not exist made it die on the tokenizer rather than on anything it was
# measuring.
TOKENIZER = (_TOKENIZER_REPO if os.path.exists(_TOKENIZER_REPO)
             else _TOKENIZER_BOX)


def slotted(text: str, slots) -> str:
    """The page with every invented word replaced by its slot name."""
    iv, _ = ndata._vocab()
    index = {s.lower(): i for i, s in enumerate(slots)}
    out, last = [], 0
    for m in ntok.WORD_RE.finditer(text):
        t = m.group(0)
        if not iv.is_nonce(t):
            continue
        k = index.get(t.lower())
        if k is None:
            raise ntok.TokenizeError(f"{t!r} is not a slot of the text")
        out.append(text[last:m.start()])
        out.append(f"W{k}")
        last = m.end()
    out.append(text[last:])
    return "".join(out)


def target_text(prog, slots) -> str:
    return " ".join(ntok.serialize(prog, slots))


def encode_example(tok, prog, text: str, slots, max_len: int):
    """(token ids, loss mask) for one item, or None if it does not fit."""
    sid = tok.special_ids
    from src.train.data import render_world_preamble
    head = [sid["<|world|>"], *tok.encode(render_world_preamble({}))]
    q = [sid["<|q|>"], *tok.encode(slotted(text, slots))]
    t = [*tok.encode(" " + target_text(prog, slots)), sid["<|eot|>"]]
    ids = head + q + [sid["<|a|>"]] + t
    if len(ids) > max_len:
        return None
    mask = [0] * (len(ids) - len(t)) + [1] * len(t)
    return ids, mask


def prompt_ids(tok, text: str, slots):
    """Everything up to and including the answer marker."""
    from src.train.data import render_world_preamble
    sid = tok.special_ids
    return ([sid["<|world|>"], *tok.encode(render_world_preamble({}))]
            + [sid["<|q|>"], *tok.encode(slotted(text, slots))]
            + [sid["<|a|>"]])


def roundtrip_gate(tok, items, limit: int = 400) -> dict:
    """Does the tokenizer give the target back unchanged.

    Exact match is scored on the tokens the model writes. If the tokenizer
    cannot return the target string it was handed, the ceiling is the
    tokenizer's and not the model's, and every number below would be a
    tokenizer bug wearing a model's name.
    """
    from src.norm.lang import Program
    bad, n, lens = [], 0, []
    for it in items[:limit]:
        t = target_text(it["prog"], it["slots"])
        back = tok.decode(tok.encode(" " + t)).strip()
        n += 1
        if back != t:
            bad.append({"want": t[:180], "got": back[:180]})
        else:
            try:
                p = ntok.deserialize(back.split(), it["slots"])
                if p != it["prog"]:
                    bad.append({"want": "program", "got": "deserialize differs"})
            except Exception as exc:
                bad.append({"want": "program", "got": f"{type(exc).__name__}"})
        e = encode_example(tok, it["prog"], it["text"], it["slots"], 1 << 20)
        lens.append(len(e[0]))
    return {"n": n, "bad": len(bad), "examples": bad[:5],
            "len_mean": round(float(np.mean(lens)), 1),
            "len_p50": int(np.percentile(lens, 50)),
            "len_p95": int(np.percentile(lens, 95)),
            "len_p99": int(np.percentile(lens, 99)),
            "len_max": int(np.max(lens))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/system/lm")
    ap.add_argument("--tokenizer", default=TOKENIZER)
    ap.add_argument("--n", type=int, default=300000)
    ap.add_argument("--procs", type=int, default=8)
    ap.add_argument("--seed", type=int, default=20260830)
    ap.add_argument("--max-len", type=int, default=1536)
    ap.add_argument("--gate-only", action="store_true")
    a = ap.parse_args()

    from src.train.tokenizer import load_tokenizer
    from src.norm import neval
    tok = load_tokenizer(a.tokenizer)
    os.makedirs(a.out, exist_ok=True)

    gate = {}
    for sp in ("train_frames_eval", "qframe", "lexicon", "mode", "mixed"):
        items = neval.load_eval(os.path.join("data/norm", sp), 400)
        gate[sp] = roundtrip_gate(tok, items)
        print(sp, json.dumps(gate[sp]), flush=True)
    with open(os.path.join(a.out, "gate.json"), "w") as fh:
        json.dump(gate, fh, indent=1)
    if a.gate_only:
        return

    groups = ndata.split_frames()
    t0 = time.time()
    rows, dropped = ndata.generate(groups["train"], a.n, a.seed, a.procs,
                                   keep_text=True, stratify=False)
    print(json.dumps({"generated": len(rows), "dropped": dropped,
                      "sec": round(time.time() - t0, 1)}), flush=True)

    toks, masks, off = [], [], [0]
    long = 0
    for r in rows:
        e = encode_example(tok, program_load(r["prog"]), r["text"], r["slots"],
                           a.max_len)
        if e is None:
            long += 1
            continue
        toks.extend(e[0])
        masks.extend(e[1])
        off.append(len(toks))
    np.savez(os.path.join(a.out, "train.npz"),
             toks=np.asarray(toks, dtype=np.uint16),
             mask=np.asarray(masks, dtype=np.uint8),
             off=np.asarray(off, dtype=np.int64))
    man = {"n": len(off) - 1, "dropped_generation": dropped,
           "dropped_too_long": long, "max_len": a.max_len,
           "tokens": len(toks), "seed": a.seed,
           "frames_train": len(groups["train"]),
           "loss_tokens": int(np.sum(masks)),
           "sec": round(time.time() - t0, 1)}
    with open(os.path.join(a.out, "manifest.json"), "w") as fh:
        json.dump(man, fh, indent=1)
    print(json.dumps(man), flush=True)


if __name__ == "__main__":
    main()
