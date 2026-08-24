"""Render worldgen episodes into uint16 token shards for training.

Usage:

    uv run python -m scripts.render_shards --worlds data/worlds.jsonl \
        --tokenizer runs/smoke-001/tokenizer.json --out data/shards
"""

import argparse

from src.train.data import render_jsonl_to_shards
from src.train.tokenizer import load_tokenizer


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m scripts.render_shards")
    parser.add_argument("--worlds", required=True)
    parser.add_argument("--tokenizer", required=True)
    parser.add_argument("--out", required=True, help="shard directory")
    parser.add_argument("--max-doc-tokens", type=int, default=None)
    parser.add_argument("--shard-size", type=int, default=1 << 24)
    args = parser.parse_args(argv)

    tokenizer = load_tokenizer(args.tokenizer)
    total = render_jsonl_to_shards(
        args.worlds, tokenizer, args.out,
        max_doc_tokens=args.max_doc_tokens, shard_size=args.shard_size)
    print(f"rendered {total:,} tokens to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
