"""Tokenize regime A parquet files into uint16 training shards.

Each document encodes to its BPE tokens followed by one <|eot|>. Files are
processed in sorted name order and rows in stored order, so the output is
deterministic for a given tokenizer.

Usage:

    uv run python -m scripts.render_regime_a \
        --parquet-dir ~/data/regime_a/parquet \
        --tokenizer ~/runs/tokenizer_v2/tokenizer_v2.json \
        --out ~/data/regime_a/shards [--max-tokens 7000000000]
"""

import argparse
import time
from pathlib import Path

import pyarrow.parquet as pq

from src.train.data import ShardWriter
from src.train.tokenizer import load_tokenizer

PROGRESS_EVERY = 100_000_000


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m scripts.render_regime_a")
    parser.add_argument("--parquet-dir", required=True)
    parser.add_argument("--tokenizer", required=True)
    parser.add_argument("--out", required=True, help="shard directory")
    parser.add_argument("--max-tokens", type=int, default=None)
    parser.add_argument("--shard-size", type=int, default=1 << 27)
    parser.add_argument("--batch-rows", type=int, default=1024)
    args = parser.parse_args(argv)

    tok = load_tokenizer(args.tokenizer)
    eot = tok.special_ids["<|eot|>"]
    writer = ShardWriter(args.out, shard_size=args.shard_size)
    total = 0
    next_mark = PROGRESS_EVERY
    start = time.time()
    done = False
    for path in sorted(Path(args.parquet_dir).glob("*.parquet")):
        if done:
            break
        pf = pq.ParquetFile(path)
        for batch in pf.iter_batches(batch_size=args.batch_rows,
                                     columns=["text"]):
            texts = [v.as_py() for v in batch.column("text")]
            for enc in tok.tokenizer.encode_batch(texts):
                writer.write(enc.ids + [eot])
                total += len(enc.ids) + 1
                if args.max_tokens is not None and total >= args.max_tokens:
                    done = True
                    break
            if total >= next_mark:
                rate = total / max(1e-9, time.time() - start)
                print(f"progress {total:,} tokens, {rate:,.0f} tok/s "
                      f"({path.name})", flush=True)
                next_mark += PROGRESS_EVERY
            if done:
                break
        print(f"finished {path.name}, running total {total:,}", flush=True)
    writer.close()
    print(f"REGIME_A_RENDER_DONE total {total:,} tokens in {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
