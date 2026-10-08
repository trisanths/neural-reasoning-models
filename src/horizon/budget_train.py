"""Train one ceiling arm with the optimizer budget and the run seed exposed.

`scripts/ceiling_train.py` fixes both. It runs 8000 steps and it draws every
arm from the same stream shuffle and the same batch permutation, so the eight
published arms are one run each with no replicate and no budget variation.
Two things this lane needs are therefore not reachable from it.

  --steps       the optimizer budget. The trade-off claim is that depth is
                bought against induction at a fixed budget, so the budget has
                to move.
  --replicate   a genuine run-to-run replicate. The trainer's `--seed` does
                nothing on the opgraph arm: the stream shuffle is hardcoded to
                17 and the batch permutation to 1234. `--replicate k` offsets
                both, so k=0 reproduces the published arm exactly and k>0 is
                the same distribution drawn a different way.

Nothing else changes. The model, the optimizer, the schedule, the masking and
the checkpoint format all come from `scripts/opgraph_train.py`, and the stream
comes from `src/ceiling/stream.py`, both imported rather than copied. The one
exception is `batches`, which had to be copied to make its permutation seed
reachable; `--check-batch-parity` asserts the copy reproduces the original
batch for batch at replicate 0, and the assertion runs by default.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import torch

import scripts.opgraph_train as trainer
from src.ceiling.stream import build_ceiling_stream, check_parity, stream_stats
from src.opgraph.data import IGNORE, encode_example

STREAM_SEED = 17
BATCH_SEED = 1234


def batches(pool, tok, max_len, batch_size, encode=None, seed=BATCH_SEED):
    """`scripts.opgraph_train.batches` with the permutation seed reachable.

    Copied deliberately and checked against the original rather than edited in
    place, because that module is shared with other lanes.
    """
    encode = encode or (lambda ex: encode_example(tok, ex[0], ex[1], max_len))
    encoded = []
    dropped = 0
    for ex in pool:
        e = encode(ex)
        if e is None:
            dropped += 1
        else:
            encoded.append(e)
    if not encoded:
        raise SystemExit("no examples fit inside max_len")
    print(json.dumps({"examples": len(pool), "encoded": len(encoded),
                      "dropped_over_max_len": dropped}), flush=True)
    encoded.sort(key=lambda x: len(x[0]))
    groups = [encoded[i:i + batch_size] for i in range(0, len(encoded), batch_size)]
    order = list(range(len(groups)))
    rng = torch.Generator().manual_seed(seed)
    while True:
        perm = torch.randperm(len(groups), generator=rng).tolist()
        for gi in perm:
            g = groups[order[gi]]
            width = max(len(ids) for ids, _ in g)
            ids = torch.zeros(len(g), width, dtype=torch.long)
            lab = torch.full((len(g), width), IGNORE, dtype=torch.long)
            for i, (a, b) in enumerate(g):
                ids[i, :len(a)] = torch.tensor(a)
                lab[i, :len(b)] = torch.tensor(b)
            yield ids, lab


def check_batch_parity(tok, n_worlds=400, n_batches=6) -> bool:
    """The copied batcher must reproduce the original at replicate 0."""
    from src.opgraph.data import build_stream
    pool = build_stream(range(n_worlds), "opgraph", rng_seed=STREAM_SEED)
    a = trainer.batches(pool, tok, 1024, 8)
    b = batches(pool, tok, 1024, 8, seed=BATCH_SEED)
    for _ in range(n_batches):
        ia, la = next(a)
        ib, lb = next(b)
        if not (torch.equal(ia, ib) and torch.equal(la, lb)):
            return False
    return True


def _flag(rest, name):
    for i, a in enumerate(rest):
        if a == name and i + 1 < len(rest):
            return rest[i + 1]
        if a.startswith(name + "="):
            return a.split("=", 1)[1]
    return None


def main() -> int:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--max-depth", type=int, default=3)
    ap.add_argument("--max-symbols", type=int, default=1)
    ap.add_argument("--replicate", type=int, default=0,
                    help="0 reproduces the published arm; k>0 redraws the "
                         "stream shuffle and the batch permutation")
    ap.add_argument("--no-parity-check", action="store_true")
    mine, rest = ap.parse_known_args()

    stream_seed = STREAM_SEED + 1000 * mine.replicate
    batch_seed = BATCH_SEED + 1000 * mine.replicate

    if not mine.no_parity_check:
        tok_path = _flag(rest, "--tokenizer")
        from src.train.tokenizer import load_tokenizer
        tok = load_tokenizer(tok_path)
        if not check_batch_parity(tok):
            raise SystemExit("batch parity failed: the copied batcher no "
                             "longer reproduces the original")
        print("[parity] copied batcher reproduces the original", flush=True)
        if (mine.max_depth == 3 and mine.max_symbols == 1
                and mine.replicate == 0):
            if not check_parity(200):
                raise SystemExit("stream parity failed")
            print("[parity] default ceiling reproduces the original stream",
                  flush=True)

    out = _flag(rest, "--out")

    def patched_stream(seeds, arm, rng_seed=0):
        pool = build_ceiling_stream(seeds, arm, rng_seed=stream_seed,
                                    max_depth=mine.max_depth,
                                    max_symbols=mine.max_symbols)
        stats = stream_stats(pool)
        stats.update({"max_depth": mine.max_depth,
                      "max_symbols": mine.max_symbols, "arm": arm,
                      "replicate": mine.replicate,
                      "stream_seed": stream_seed, "batch_seed": batch_seed,
                      "steps": int(_flag(rest, "--steps") or 0)})
        print("[stream] " + json.dumps(stats), flush=True)
        if out:
            os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
            with open(out + ".stream.json", "w") as fh:
                json.dump(stats, fh, indent=1)
        return pool

    def patched_batches(pool, tok, max_len, batch_size, encode=None):
        return batches(pool, tok, max_len, batch_size, encode, seed=batch_seed)

    trainer.build_stream = patched_stream
    trainer.batches = patched_batches
    sys.argv = [sys.argv[0]] + rest
    return trainer.main()


if __name__ == "__main__":
    raise SystemExit(main())
