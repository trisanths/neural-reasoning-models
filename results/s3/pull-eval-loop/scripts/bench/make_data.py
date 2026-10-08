"""Wrap a raw procgen .bin stream into uint16 training shards for benchmarks.

The stream comes from src.procgen.cli. load_procgen_bin shifts the raw symbol
ids into the reserved vocabulary range [7, 263), so the shards are valid
input for any config with the standard 32768 vocabulary.

Usage:

    uv run python -m scripts.bench.make_data --bin ~/data/bench/proc.bin \
        --out ~/data/bench/shards
"""

import argparse

from src.train.data import ShardWriter, load_procgen_bin


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m scripts.bench.make_data")
    parser.add_argument("--bin", required=True, help="raw procgen .bin stream")
    parser.add_argument("--out", required=True, help="shard directory")
    parser.add_argument("--shard-size", type=int, default=1 << 24)
    args = parser.parse_args(argv)

    tokens = load_procgen_bin(args.bin)
    writer = ShardWriter(args.out, shard_size=args.shard_size)
    writer.write(tokens)
    writer.close()
    print(f"wrote {tokens.size:,} tokens to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
