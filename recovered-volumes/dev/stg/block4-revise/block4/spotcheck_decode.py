"""Decode a random window from each training dataset for eyeball checking.

Run from the repo directory under uv so the repo and its deps import:
  uv run python ~/killtest/spotcheck_decode.py \
      --tokenizer ~/data/tokenizer_v2.json \
      regime_a=~/data/regime_a/shards regime_c=~/data/regime_c/flat \
      warmup=~/data/proc_warmup_15m.bin

A name=path argument pointing at a directory is read through ShardReader
(flat shard dir with index.json); a .bin file is read as a raw procgen
stream. The window offset is random per invocation and printed, so a bad
sample can be reproduced with --offset name=N.
"""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "decoupled-reasoner"))
sys.path.insert(0, ".")

from src.train.data import ArraySource, ShardReader, load_procgen_bin  # noqa: E402
from src.train.tokenizer import load_tokenizer  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--window", type=int, default=400, help="tokens per sample")
    ap.add_argument("--offset", action="append", default=[],
                    help="name=N fixed offset instead of a random one")
    ap.add_argument("datasets", nargs="+", help="name=path (shard dir or .bin)")
    args = ap.parse_args()

    tokenizer = load_tokenizer(str(Path(args.tokenizer).expanduser()))
    fixed = dict(kv.split("=", 1) for kv in args.offset)

    for spec in args.datasets:
        name, raw_path = spec.split("=", 1)
        path = Path(raw_path).expanduser()
        if path.is_dir():
            source = ShardReader(str(path))
        else:
            source = ArraySource(load_procgen_bin(str(path)))
        window = min(args.window, source.total_tokens)
        if name in fixed:
            offset = int(fixed[name])
        else:
            offset = random.randrange(0, source.total_tokens - window + 1)
        ids = source.get_slice(offset, window).tolist()
        text = tokenizer.decode(ids)
        print(f"----- {name} | {path} | total_tokens {source.total_tokens:,} "
              f"| offset {offset:,} | window {window} -----")
        if text.strip():
            print(text)
        else:
            print(f"decode produced no visible text; raw ids: {ids[:100]}")
        print(f"----- end {name} -----\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
