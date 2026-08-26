"""Tokenize regime A parquet files into uint16 training shards.

Each document encodes to its BPE tokens followed by one <|eot|>. Files are
processed in sorted name order and rows in stored order, so the output is
deterministic for a given tokenizer.

With --procs 1 the render is the original single streaming pass that writes
shards directly into --out. With --procs N each parquet file becomes one
numbered chunk rendered by a worker pool into <out>/chunks/chunk-XXXXX
directories with adjacent .done markers, following the pattern in
render_regime_c.py. A merge step then concatenates the chunk streams in file
order into final shards in --out, cutting at the first document boundary at
or past --max-tokens. The merged shard files are byte identical to a single
process render with the same arguments. A restart skips chunks whose marker
exists and re-renders partial chunk directories, so the multiprocess path is
resumable after a kill at any point.

Usage:

    uv run python -m scripts.render_regime_a \
        --parquet-dir ~/data/regime_a/parquet \
        --tokenizer ~/runs/tokenizer_v2/tokenizer_v2.json \
        --out ~/data/regime_a/shards \
        [--max-tokens 7000000000] [--procs 8]
"""

import argparse
import json
import multiprocessing as mp
import os
import shutil
import time
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

from src.train.data import ShardWriter
from src.train.tokenizer import load_tokenizer

PROGRESS_EVERY = 100_000_000
CHUNKS_SUBDIR = "chunks"
MERGE_BLOCK_BYTES = 1 << 26

_G: dict = {}


def chunk_paths(out_dir, chunk_id: int) -> tuple[Path, Path]:
    d = Path(out_dir) / CHUNKS_SUBDIR / f"chunk-{chunk_id:05d}"
    return d, Path(str(d) + ".done")


def _atomic_json(path: Path, payload: dict) -> None:
    tmp = Path(str(path) + ".tmp")
    with open(tmp, "w") as fh:
        json.dump(payload, fh, indent=2)
        fh.write("\n")
    os.replace(tmp, path)


def _init_worker(tokenizer_path: str, params: dict) -> None:
    # Each worker encodes serially; pool processes supply the parallelism.
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    _G["tok"] = load_tokenizer(tokenizer_path)
    _G["params"] = params


def _render_chunk(chunk_id: int) -> dict:
    p = _G["params"]
    tok = _G["tok"]
    chunk_dir, marker = chunk_paths(p["out_dir"], chunk_id)
    src = Path(p["files"][chunk_id])
    if marker.exists():
        with open(marker) as fh:
            stats = json.load(fh)
        if stats.get("file") != src.name:
            raise SystemExit(
                f"chunk {chunk_id:05d} marker is for {stats.get('file')} "
                f"but the listing now has {src.name}")
        return stats
    shutil.rmtree(chunk_dir, ignore_errors=True)
    t0 = time.time()
    eot = tok.special_ids["<|eot|>"]
    writer = ShardWriter(str(chunk_dir), shard_size=p["shard_size"])
    tokens = 0
    docs = 0
    next_mark = PROGRESS_EVERY
    pf = pq.ParquetFile(src)
    for batch in pf.iter_batches(batch_size=p["batch_rows"],
                                 columns=["text"]):
        texts = [v.as_py() for v in batch.column("text")]
        for enc in tok.tokenizer.encode_batch(texts):
            writer.write(enc.ids + [eot])
            tokens += len(enc.ids) + 1
            docs += 1
        if tokens >= next_mark:
            rate = tokens / max(1e-9, time.time() - t0)
            print(f"chunk {chunk_id:05d} progress {tokens:,} tokens, "
                  f"{rate:,.0f} tok/s ({src.name})", flush=True)
            next_mark += PROGRESS_EVERY
    writer.close()
    stats = {
        "id": chunk_id,
        "file": src.name,
        "docs": docs,
        "tokens": tokens,
        "seconds": round(time.time() - t0, 3),
    }
    _atomic_json(marker, stats)
    return stats


def _prefix_reached(done_stats: dict, max_tokens) -> bool:
    """True when the consecutive done prefix already covers max_tokens.

    The merge consumes chunks 0..k in order, so only a gap free prefix
    counts toward the cap. Checking the prefix instead of the raw total
    guarantees the merge never hits a missing chunk.
    """
    if max_tokens is None:
        return False
    total = 0
    cid = 0
    while cid in done_stats:
        total += done_stats[cid]["tokens"]
        if total >= max_tokens:
            return True
        cid += 1
    return False


def merge_chunks(out_dir: Path, num_chunks: int, shard_size: int,
                 max_tokens, eot: int) -> int:
    """Concatenate chunk streams into final shards under out_dir.

    Mirrors the single process cap semantics: documents are whole, and the
    stream ends at the first <|eot|> whose end position reaches max_tokens.
    Returns the merged token total.
    """
    out_dir = Path(out_dir)
    for stale in out_dir.glob("shard-*.bin"):
        stale.unlink()
    writer = ShardWriter(str(out_dir), shard_size=shard_size)
    total = 0
    done = False
    for cid in range(num_chunks):
        if done:
            break
        chunk_dir, marker = chunk_paths(out_dir, cid)
        if not marker.exists():
            raise SystemExit(
                f"merge needs chunk {cid:05d} but it is not done; "
                f"rerun the render to fill the gap")
        index = json.loads((chunk_dir / "index.json").read_text())
        for entry in index["shards"]:
            with open(chunk_dir / entry["file"], "rb") as fh:
                while True:
                    buf = fh.read(MERGE_BLOCK_BYTES)
                    if not buf:
                        break
                    arr = np.frombuffer(buf, dtype=np.uint16)
                    if max_tokens is None or total + arr.size < max_tokens:
                        writer.write(arr)
                        total += arr.size
                        continue
                    # The cap lands in this block. Cut after the first
                    # document end at or past max_tokens.
                    start = max(0, max_tokens - total - 1)
                    hits = np.flatnonzero(arr[start:] == eot)
                    if hits.size == 0:
                        writer.write(arr)
                        total += arr.size
                        continue
                    cut = start + int(hits[0]) + 1
                    writer.write(arr[:cut])
                    total += cut
                    done = True
                    break
            if done:
                break
    writer.close()
    return total


def verify_out(out_dir: Path) -> int:
    """Check index.json against the shard files on disk."""
    out_dir = Path(out_dir)
    index = json.loads((out_dir / "index.json").read_text())
    total = 0
    for entry in index["shards"]:
        path = out_dir / entry["file"]
        want = entry["num_tokens"] * 2
        have = path.stat().st_size
        if have != want:
            raise SystemExit(f"verify failed: {path} is {have} bytes, "
                             f"index says {want}")
        total += entry["num_tokens"]
    if total != index["total_tokens"]:
        raise SystemExit(f"verify failed: shard sum {total} != index total "
                         f"{index['total_tokens']}")
    return total


def render_single(args, files) -> int:
    tok = load_tokenizer(os.path.expanduser(args.tokenizer))
    eot = tok.special_ids["<|eot|>"]
    writer = ShardWriter(args.out, shard_size=args.shard_size)
    total = 0
    next_mark = PROGRESS_EVERY
    start = time.time()
    done = False
    for path in files:
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
    return total


def render_multi(args, files, out_dir: Path) -> int:
    tokenizer_path = os.path.expanduser(args.tokenizer)
    params = {
        "out_dir": str(out_dir),
        "files": [str(f) for f in files],
        "shard_size": args.shard_size,
        "batch_rows": args.batch_rows,
    }
    (out_dir / CHUNKS_SUBDIR).mkdir(parents=True, exist_ok=True)

    done_stats: dict[int, dict] = {}
    for cid, src in enumerate(files):
        _, marker = chunk_paths(out_dir, cid)
        if marker.exists():
            with open(marker) as fh:
                stats = json.load(fh)
            if stats.get("file") != src.name:
                raise SystemExit(
                    f"chunk {cid:05d} marker is for {stats.get('file')} but "
                    f"the listing now has {src.name}; the parquet dir "
                    f"changed, wipe {out_dir / CHUNKS_SUBDIR} to re-render")
            done_stats[cid] = stats
    if done_stats:
        print(f"resuming past {len(done_stats)} done chunks, "
              f"{sum(s['tokens'] for s in done_stats.values()):,} tokens",
              flush=True)

    run_start = time.time()
    run_tokens = 0
    run_chunks = 0

    def note(stats: dict) -> None:
        nonlocal run_tokens, run_chunks
        run_tokens += stats["tokens"]
        run_chunks += 1
        elapsed = max(1e-9, time.time() - run_start)
        total = sum(s["tokens"] for s in done_stats.values())
        print(f"chunk {stats['id']:05d} {stats['file']} "
              f"tokens {stats['tokens']:,} in {stats['seconds']}s | "
              f"done {len(done_stats)}/{len(files)} chunks, "
              f"total {total:,} | run {run_tokens / elapsed:,.0f} tok/s",
              flush=True)

    ctx = mp.get_context("fork")
    with ctx.Pool(args.procs, initializer=_init_worker,
                  initargs=(tokenizer_path, params)) as pool:
        pending = iter([cid for cid in range(len(files))
                        if cid not in done_stats])
        inflight: dict[int, object] = {}
        exhausted = False
        stopping = _prefix_reached(done_stats, args.max_tokens)
        while True:
            while (not stopping and not exhausted
                   and len(inflight) < args.procs):
                cid = next(pending, None)
                if cid is None:
                    exhausted = True
                    break
                inflight[cid] = pool.apply_async(_render_chunk, (cid,))
            if not inflight:
                break
            ready = [c for c, r in inflight.items() if r.ready()]
            if not ready:
                time.sleep(0.2)
                continue
            for cid in sorted(ready):
                stats = inflight.pop(cid).get()
                done_stats[cid] = stats
                note(stats)
            if _prefix_reached(done_stats, args.max_tokens):
                stopping = True
        pool.close()
        pool.join()

    tok = load_tokenizer(tokenizer_path)
    eot = tok.special_ids["<|eot|>"]
    total = merge_chunks(out_dir, len(files), args.shard_size,
                         args.max_tokens, eot)
    verified = verify_out(out_dir)
    if verified != total:
        raise SystemExit(f"merge wrote {total} tokens but the index "
                         f"verifies to {verified}")
    print(f"merged {total:,} tokens into {out_dir}", flush=True)
    if not args.keep_chunks:
        shutil.rmtree(out_dir / CHUNKS_SUBDIR)
        print("removed chunk directories after verified merge", flush=True)
    return total


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m scripts.render_regime_a")
    parser.add_argument("--parquet-dir", required=True)
    parser.add_argument("--tokenizer", required=True)
    parser.add_argument("--out", required=True, help="shard directory")
    parser.add_argument("--max-tokens", type=int, default=None)
    parser.add_argument("--shard-size", type=int, default=1 << 27)
    parser.add_argument("--batch-rows", type=int, default=1024)
    parser.add_argument("--procs", type=int, default=1,
                        help="worker processes; each renders one parquet "
                             "file per chunk, so parallelism is capped by "
                             "the file count")
    parser.add_argument("--keep-chunks", action="store_true",
                        help="keep chunk directories after the merge "
                             "instead of deleting them")
    args = parser.parse_args(argv)

    parquet_dir = Path(os.path.expanduser(args.parquet_dir))
    files = sorted(parquet_dir.glob("*.parquet"))
    if not files:
        raise SystemExit(f"no parquet files under {parquet_dir}")

    if args.procs <= 1:
        total = render_single(args, files)
    else:
        out_dir = Path(os.path.expanduser(args.out))
        total = render_multi(args, files, out_dir)
    print(f"REGIME_A_RENDER_DONE total {total:,} tokens in {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
