"""Render worldgen episodes into uint16 token shards for training.

Usage:

    uv run python -m scripts.render_shards --worlds data/worlds.jsonl \
        --tokenizer runs/smoke-001/tokenizer.json --out data/shards \
        [--mode retrieval-trace]

Mode plain renders world, documents, and question-answer pairs. Mode
retrieval-trace additionally writes an oracle retrieval loop after each
question, per SPEC.md section 2.
"""

import argparse

from src.train.data import render_jsonl_to_shards
from src.train.retrieval import render_jsonl_to_shards_retrieval
from src.train.tokenizer import load_tokenizer


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m scripts.render_shards")
    parser.add_argument("--worlds", required=True)
    parser.add_argument("--tokenizer", required=True)
    parser.add_argument("--out", required=True, help="shard directory")
    parser.add_argument("--mode", choices=["plain", "retrieval-trace"],
                        default="plain")
    parser.add_argument("--max-doc-tokens", type=int, default=None)
    parser.add_argument("--shard-size", type=int, default=1 << 24)
    args = parser.parse_args(argv)

    tokenizer = load_tokenizer(args.tokenizer)
    render = (render_jsonl_to_shards_retrieval if args.mode == "retrieval-trace"
              else render_jsonl_to_shards)
    total = render(
        args.worlds, tokenizer, args.out,
        max_doc_tokens=args.max_doc_tokens, shard_size=args.shard_size)
    print(f"rendered {total:,} tokens to {args.out} (mode {args.mode})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
