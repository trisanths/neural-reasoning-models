"""Train tokenizer v2 on a mixed sample: regime A natural text plus rendered
worldgen episodes. The v1 tokenizer saturated at 18k merges because the
synthetic sample has limited surface diversity; mixing in FineWeb-Edu text
reaches the full 32768 vocabulary, per the SMOKE.md note.

Usage:

    uv run python -m scripts.train_tokenizer_v2 \
        --worlds ~/data/worlds.jsonl --parquet-dir ~/data/regime_a/parquet \
        --out ~/runs/tokenizer_v2/tokenizer_v2.json
"""

import argparse
import json
import tempfile
from pathlib import Path

import pyarrow.parquet as pq

from src.train.data import render_world_preamble
from src.train.tokenizer import DEFAULT_VOCAB_SIZE, train_tokenizer


def write_worldgen_sample(fh, worlds_path: str, sample_episodes: int) -> int:
    n = 0
    with open(worlds_path) as worlds:
        for line in worlds:
            if n >= sample_episodes:
                break
            episode = json.loads(line)
            fh.write(render_world_preamble(episode["world"]) + "\n")
            for doc in episode["documents"]:
                fh.write(doc["text"] + "\n")
            for q in episode["questions"]:
                fh.write(q["text"] + " " + q["answer"] + "\n")
            n += 1
    return n


def write_parquet_sample(fh, parquet_dir: str, num_docs: int) -> int:
    """Stream text rows from the parquet files in sorted name order."""
    written = 0
    for path in sorted(Path(parquet_dir).glob("*.parquet")):
        pf = pq.ParquetFile(path)
        for batch in pf.iter_batches(batch_size=1024, columns=["text"]):
            for value in batch.column("text"):
                if written >= num_docs:
                    return written
                fh.write(value.as_py().replace("\r", "") + "\n")
                written += 1
    return written


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m scripts.train_tokenizer_v2")
    parser.add_argument("--worlds", required=True, help="episodes JSONL")
    parser.add_argument("--parquet-dir", required=True,
                        help="directory of regime A parquet files")
    parser.add_argument("--out", required=True, help="tokenizer json path")
    parser.add_argument("--sample-episodes", type=int, default=2000)
    parser.add_argument("--parquet-docs", type=int, default=100000)
    parser.add_argument("--vocab-size", type=int, default=DEFAULT_VOCAB_SIZE)
    args = parser.parse_args(argv)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as sample:
        n_eps = write_worldgen_sample(sample, args.worlds, args.sample_episodes)
        n_docs = write_parquet_sample(sample, args.parquet_dir, args.parquet_docs)
        sample_path = sample.name

    tok = train_tokenizer([sample_path], out_path=args.out,
                          vocab_size=args.vocab_size)
    print(f"trained tokenizer v2 on {n_eps} episodes and {n_docs} natural "
          f"documents, vocab {tok.vocab_size}, saved to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
