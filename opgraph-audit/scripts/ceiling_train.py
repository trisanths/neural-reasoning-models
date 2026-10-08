"""Fine tune one plan arm with the training ceiling set explicitly.

This is `scripts/opgraph_train.py` with the training stream swapped and
nothing else. The optimizer, the schedule, the batching, the masking and the
checkpoint format all come from that module, so an arm trained here differs
from an arm trained there only in which questions the stream contains.

  --max-depth    largest number of steps a training plan may have
  --max-symbols  largest number of distinct operator symbols in one plan

At --max-depth 3 --max-symbols 1 the stream is asserted byte-identical to the
original before training starts.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import scripts.opgraph_train as trainer
from src.ceiling.stream import build_ceiling_stream, check_parity, stream_stats


def main() -> int:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--max-depth", type=int, default=3)
    ap.add_argument("--max-symbols", type=int, default=1)
    ap.add_argument("--no-parity-check", action="store_true")
    mine, rest = ap.parse_known_args()

    if mine.max_depth == 3 and mine.max_symbols == 1 and not mine.no_parity_check:
        if not check_parity(200):
            raise SystemExit("parity check failed: the default ceiling no "
                             "longer rebuilds the original stream")
        print("[parity] default ceiling reproduces the original stream",
              flush=True)

    def patched(seeds, arm, rng_seed=0):
        pool = build_ceiling_stream(seeds, arm, rng_seed=rng_seed,
                                    max_depth=mine.max_depth,
                                    max_symbols=mine.max_symbols)
        stats = stream_stats(pool)
        stats.update({"max_depth": mine.max_depth,
                      "max_symbols": mine.max_symbols, "arm": arm})
        print("[stream] " + json.dumps(stats), flush=True)
        out = _out_path(rest)
        if out:
            os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
            with open(out + ".stream.json", "w") as fh:
                json.dump(stats, fh, indent=1)
        return pool

    trainer.build_stream = patched
    sys.argv = [sys.argv[0]] + rest
    return trainer.main()


def _out_path(rest):
    for i, a in enumerate(rest):
        if a == "--out" and i + 1 < len(rest):
            return rest[i + 1]
        if a.startswith("--out="):
            return a.split("=", 1)[1]
    return None


if __name__ == "__main__":
    raise SystemExit(main())
