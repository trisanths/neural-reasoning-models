"""Build tagged shards from the regime A parquet corpus.

The text is copied through untouched. Each document is tagged, tokenized
with offsets, and appended with one <|eot|> whose tag is plain, exactly the
layout scripts/render_regime_a.py writes, so the token stream of a tagged
build and a plain build of the same rows is identical and only the sidecar
is new.

Work splits by parquet row group. Worker k writes chunks/chunk-XXXXX with
its own index, then drops a .done marker holding its stats; a restart skips
finished chunks and wipes partial ones. The top level index.json names every
chunk shard by its relative path, so ShardReader and TaggedShardReader open
the output directory with no merge pass over the data.

Usage:

    uv run python -m src.lossmask.build \
        --parquet-dir ~/data/parquet --tokenizer ~/data/tokenizer_v2.json \
        --out ~/data/lossmask/train --procs 32 --max-tokens 1200000000
"""

import argparse
import json
import multiprocessing as mp
import os
import shutil
import time
from pathlib import Path

import numpy as np

from src.lossmask.shards import TaggedShardWriter, write_index
from src.lossmask.tagger import encode_with_tags
from src.train.tokenizer import load_tokenizer

CHUNKS_SUBDIR = "chunks"

_G: dict = {}


def _init_worker(tokenizer_path: str):
    _G["tokenizer"] = load_tokenizer(tokenizer_path)


def render_document(text: str, tokenizer, eot_id: int):
    """(ids, tags) for one document plus its closing <|eot|>."""
    ids, tags = encode_with_tags(text, tokenizer)
    ids.append(eot_id)
    tags.append(0)
    return ids, tags


def _render_chunk(job: dict) -> dict:
    import pyarrow.parquet as pq

    out_dir = Path(job["chunk_dir"])
    marker = Path(str(out_dir) + ".done")
    if marker.exists():
        return json.loads(marker.read_text())
    if out_dir.exists():
        shutil.rmtree(out_dir)
    tokenizer = _G["tokenizer"]
    eot = tokenizer.special_ids["<|eot|>"]
    writer = TaggedShardWriter(out_dir, shard_size=job["shard_size"])
    started = time.time()
    n_docs = 0
    handle = pq.ParquetFile(job["parquet"])
    for group in job["row_groups"]:
        table = handle.read_row_group(group, columns=["text"])
        for value in table.column("text"):
            text = value.as_py()
            if not text:
                continue
            ids, tags = render_document(text, tokenizer, eot)
            writer.write(ids, tags)
            n_docs += 1
    index = writer.close()
    stats = {
        "chunk": job["chunk"],
        "parquet": os.path.basename(job["parquet"]),
        "row_groups": [job["row_groups"][0], job["row_groups"][-1]],
        "n_docs": n_docs,
        "total_tokens": index["total_tokens"],
        "tag_histogram": index["tag_histogram"],
        "shards": index["shards"],
        "seconds": round(time.time() - started, 1),
    }
    marker.write_text(json.dumps(stats))
    return stats


def plan_jobs(parquet_files, out_dir: Path, groups_per_chunk: int,
              shard_size: int, max_row_groups: int | None = None) -> list:
    import pyarrow.parquet as pq

    jobs = []
    for path in parquet_files:
        n_groups = pq.ParquetFile(path).metadata.num_row_groups
        if max_row_groups is not None:
            n_groups = min(n_groups, max_row_groups)
        for start in range(0, n_groups, groups_per_chunk):
            groups = list(range(start, min(start + groups_per_chunk, n_groups)))
            chunk = len(jobs)
            jobs.append({
                "chunk": chunk,
                "parquet": str(path),
                "row_groups": groups,
                "chunk_dir": str(out_dir / CHUNKS_SUBDIR / f"chunk-{chunk:05d}"),
                "shard_size": shard_size,
            })
    return jobs


def build(parquet_files, tokenizer_path: str, out_dir: str, procs: int = 8,
          groups_per_chunk: int = 4, shard_size: int = 1 << 24,
          max_tokens: int | None = None, max_row_groups: int | None = None,
          log=print) -> dict:
    out = Path(os.path.expanduser(out_dir))
    (out / CHUNKS_SUBDIR).mkdir(parents=True, exist_ok=True)
    jobs = plan_jobs(parquet_files, out, groups_per_chunk, shard_size,
                     max_row_groups=max_row_groups)
    log(f"{len(jobs)} chunks over {len(parquet_files)} parquet files, "
        f"{procs} workers")

    results: dict = {}
    started = time.time()
    if procs <= 1:
        _init_worker(tokenizer_path)
        for job in jobs:
            results[job["chunk"]] = _render_chunk(job)
    else:
        with mp.get_context("fork").Pool(
                procs, initializer=_init_worker,
                initargs=(tokenizer_path,)) as pool:
            done = 0
            for stats in pool.imap_unordered(_render_chunk, jobs):
                results[stats["chunk"]] = stats
                done += 1
                if done % 20 == 0 or done == len(jobs):
                    total = sum(r["total_tokens"] for r in results.values())
                    log(f"  {done}/{len(jobs)} chunks, {total:,} tokens, "
                        f"{round(time.time() - started)}s")

    shards = []
    histogram: dict = {}
    total = 0
    for chunk in sorted(results):
        stats = results[chunk]
        if max_tokens is not None and total >= max_tokens:
            break
        rel = f"{CHUNKS_SUBDIR}/chunk-{chunk:05d}"
        for shard in stats["shards"]:
            shards.append({
                "file": f"{rel}/{shard['file']}",
                "num_tokens": shard["num_tokens"],
                "tag_file": f"{rel}/{shard['tag_file']}",
            })
            total += shard["num_tokens"]
        for tag, count in stats["tag_histogram"].items():
            histogram[tag] = histogram.get(tag, 0) + count
    index = write_index(out, shards, histogram)
    log(f"index over {len(shards)} shards, {index['total_tokens']:,} tokens")
    return index


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m src.lossmask.build")
    parser.add_argument("--parquet-dir", required=True)
    parser.add_argument("--tokenizer", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--procs", type=int, default=8)
    parser.add_argument("--groups-per-chunk", type=int, default=4)
    parser.add_argument("--shard-size", type=int, default=1 << 24)
    parser.add_argument("--max-tokens", type=int, default=None,
                        help="stop the top level index at this many tokens; "
                             "whole shards only, so the cut lands past it")
    parser.add_argument("--skip-files", type=int, default=0,
                        help="drop this many parquet files off the front, so "
                             "a held out build reads rows the training build "
                             "never saw")
    parser.add_argument("--limit-files", type=int, default=None)
    parser.add_argument("--max-row-groups", type=int, default=None,
                        help="read only this many row groups per file, for "
                             "building a small held out set")
    args = parser.parse_args(argv)

    parquet_dir = Path(os.path.expanduser(args.parquet_dir))
    files = sorted(parquet_dir.glob("*.parquet"))[args.skip_files:]
    if args.limit_files is not None:
        files = files[:args.limit_files]
    if not files:
        raise SystemExit(f"no parquet files under {parquet_dir}")

    index = build(files, os.path.expanduser(args.tokenizer), args.out,
                  procs=args.procs, groups_per_chunk=args.groups_per_chunk,
                  shard_size=args.shard_size, max_tokens=args.max_tokens,
                  max_row_groups=args.max_row_groups)
    total = index["total_tokens"]
    from src.lossmask.tags import TAG_NAMES

    print(f"total {total:,} tokens")
    for tag, count in sorted(index.get("tag_histogram", {}).items(),
                             key=lambda kv: int(kv[0])):
        name = TAG_NAMES.get(int(tag), tag)
        print(f"  {name:8s} {count:>14,}  {100 * count / max(1, total):5.2f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
