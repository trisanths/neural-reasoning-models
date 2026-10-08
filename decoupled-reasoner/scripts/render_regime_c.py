"""Render regime C training data at scale: multiprocess episode generation
plus retrieval trace rendering into uint16 shards.

Work is split into numbered chunks with disjoint episode index ranges under
one base seed, so any subset of chunks is reproducible in isolation. Chunk k
covers episode indices [k * episodes_per_chunk, (k + 1) * episodes_per_chunk).
Each chunk writes its shards and index.json into its own directory, then an
adjacent .done marker holding its stats. A restart skips chunks whose marker
exists and wipes and re-renders partial chunk directories, so the pipeline is
resumable after a kill at any point.

A disjoint held-out index range starting at HELDOUT_INDEX_BASE feeds the eval
JSONL and can never collide with training chunks, which are capped below it.

Usage:

    uv run python -m scripts.render_regime_c \
        --out ~/data/regime_c \
        --tokenizer ~/runs/tokenizer_v2/tokenizer_v2.json \
        --seed 20260824 --episodes-per-chunk 1000 --num-chunks 100 \
        --procs 4 --heldout 5000

Stop conditions: all planned chunks done, --target-tokens reached, or
--max-seconds elapsed. In-flight chunks always finish, so the run always
ends cleanly with a DONE line. Progress lines go to stdout.
"""

import argparse
import json
import multiprocessing as mp
import os
import shutil
import time
from pathlib import Path

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

from src.train.data import ShardWriter
from src.train.retrieval import render_episode_retrieval
from src.train.tokenizer import load_tokenizer
from src.worldgen.domains import DOMAIN_ORDER
from src.worldgen.engine import generate_episodes, validate_episode

MANIFEST_NAME = "manifest.json"
HELDOUT_INDEX_BASE = 1_000_000_000

_G: dict = {}


def chunk_paths(out_dir, chunk_id: int) -> tuple[Path, Path]:
    d = Path(out_dir) / f"chunk-{chunk_id:05d}"
    return d, Path(str(d) + ".done")


def _atomic_json(path: Path, payload: dict) -> None:
    tmp = Path(str(path) + ".tmp")
    with open(tmp, "w") as fh:
        json.dump(payload, fh, indent=2)
        fh.write("\n")
    os.replace(tmp, path)


def _init_worker(tokenizer_path: str, params: dict) -> None:
    _G["tok"] = load_tokenizer(tokenizer_path)
    _G["params"] = params


def _render_chunk(chunk_id: int) -> dict:
    p = _G["params"]
    tok = _G["tok"]
    chunk_dir, marker = chunk_paths(p["out_dir"], chunk_id)
    if marker.exists():
        with open(marker) as fh:
            return json.load(fh)
    shutil.rmtree(chunk_dir, ignore_errors=True)
    t0 = time.time()
    writer = ShardWriter(str(chunk_dir), shard_size=p["shard_size"])
    episodes = 0
    tokens = 0
    start_index = chunk_id * p["episodes_per_chunk"]
    for episode in generate_episodes(
        p["base_seed"],
        p["episodes_per_chunk"],
        domains=p["domains"],
        contradiction_rate=p["contradiction_rate"],
        filler_rate=p["filler_rate"],
        start_index=start_index,
    ):
        ids = render_episode_retrieval(
            episode, tok, max_doc_tokens=p["max_doc_tokens"]
        )
        writer.write(ids)
        episodes += 1
        tokens += len(ids)
    writer.close()
    stats = {
        "id": chunk_id,
        "start_index": start_index,
        "episodes": episodes,
        "tokens": tokens,
        "seconds": round(time.time() - t0, 3),
    }
    _atomic_json(marker, stats)
    return stats


def scan_done(out_dir) -> list[dict]:
    stats = []
    for marker in Path(out_dir).glob("chunk-*.done"):
        with open(marker) as fh:
            stats.append(json.load(fh))
    return sorted(stats, key=lambda s: s["id"])


def write_heldout(args, params) -> dict:
    path = Path(args.heldout_out or Path(args.out) / "heldout.jsonl")
    marker = Path(str(path) + ".done")
    if marker.exists():
        with open(marker) as fh:
            info = json.load(fh)
        print(f"heldout already done: {info['count']} episodes at {path}",
              flush=True)
        return info
    t0 = time.time()
    n_questions = 0
    with open(path, "w", encoding="utf-8") as fh:
        for episode in generate_episodes(
            params["base_seed"],
            args.heldout,
            domains=params["domains"],
            contradiction_rate=params["contradiction_rate"],
            filler_rate=params["filler_rate"],
            start_index=HELDOUT_INDEX_BASE,
        ):
            problems = validate_episode(episode)
            if problems:
                raise SystemExit(
                    f"heldout {episode['episode_id']} failed validation: "
                    f"{problems}")
            n_questions += len(episode["questions"])
            fh.write(json.dumps(episode) + "\n")
    info = {
        "path": str(path),
        "count": args.heldout,
        "index_base": HELDOUT_INDEX_BASE,
        "base_seed": params["base_seed"],
        "total_questions": n_questions,
        "seconds": round(time.time() - t0, 3),
    }
    _atomic_json(Path(str(path) + ".meta.json"), info)
    _atomic_json(marker, info)
    print(f"heldout wrote {args.heldout} episodes to {path} "
          f"in {info['seconds']}s", flush=True)
    return info


def write_manifest(out_dir, params, tokenizer_path, heldout_info) -> dict:
    chunks = scan_done(out_dir)
    manifest = {
        "base_seed": params["base_seed"],
        "domains": params["domains"],
        "contradiction_rate": params["contradiction_rate"],
        "filler_rate": params["filler_rate"],
        "episodes_per_chunk": params["episodes_per_chunk"],
        "max_doc_tokens": params["max_doc_tokens"],
        "shard_size": params["shard_size"],
        "tokenizer": str(tokenizer_path),
        "heldout_index_base": HELDOUT_INDEX_BASE,
        "chunks": chunks,
        "total_episodes": sum(c["episodes"] for c in chunks),
        "total_tokens": sum(c["tokens"] for c in chunks),
        "heldout": heldout_info,
    }
    _atomic_json(Path(out_dir) / MANIFEST_NAME, manifest)
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="python -m scripts.render_regime_c",
        description="Render regime C episodes with retrieval traces "
                    "into uint16 shards, resumable by chunk.",
    )
    parser.add_argument("--out", required=True, help="output directory")
    parser.add_argument("--tokenizer", required=True)
    parser.add_argument("--seed", type=int, required=True, help="base seed")
    parser.add_argument("--episodes-per-chunk", type=int, default=1000)
    parser.add_argument("--num-chunks", type=int, default=None,
                        help="total planned chunks; chunk ids are "
                             "[0, num_chunks)")
    parser.add_argument("--target-tokens", type=int, default=None,
                        help="stop submitting chunks once completed tokens "
                             "reach this")
    parser.add_argument("--procs", type=int, default=1)
    parser.add_argument("--max-doc-tokens", type=int, default=None)
    parser.add_argument("--shard-size", type=int, default=1 << 24)
    parser.add_argument("--heldout", type=int, default=5000,
                        help="held-out episodes to emit as JSONL; 0 skips")
    parser.add_argument("--heldout-out", default=None,
                        help="held-out JSONL path, default <out>/heldout.jsonl")
    parser.add_argument("--domains", default=",".join(DOMAIN_ORDER))
    parser.add_argument("--contradiction-rate", type=float, default=0.15)
    parser.add_argument("--filler-rate", type=float, default=0.25)
    parser.add_argument("--max-seconds", type=float, default=None,
                        help="stop submitting new chunks after this many "
                             "seconds; in-flight chunks finish")
    args = parser.parse_args(argv)

    if args.num_chunks is None and args.target_tokens is None:
        parser.error("need --num-chunks or --target-tokens")
    domains = [d.strip() for d in args.domains.split(",") if d.strip()]
    out_dir = Path(os.path.expanduser(args.out))
    out_dir.mkdir(parents=True, exist_ok=True)
    tokenizer_path = os.path.expanduser(args.tokenizer)

    params = {
        "out_dir": str(out_dir),
        "base_seed": args.seed,
        "episodes_per_chunk": args.episodes_per_chunk,
        "domains": domains,
        "contradiction_rate": args.contradiction_rate,
        "filler_rate": args.filler_rate,
        "max_doc_tokens": args.max_doc_tokens,
        "shard_size": args.shard_size,
    }

    max_chunks = args.num_chunks
    if max_chunks is not None:
        top_index = max_chunks * args.episodes_per_chunk
        if top_index > HELDOUT_INDEX_BASE:
            parser.error("training index range would reach the held-out range")

    done = scan_done(out_dir)
    done_ids = {c["id"] for c in done}
    total_eps = sum(c["episodes"] for c in done)
    total_tokens = sum(c["tokens"] for c in done)
    print(f"render_regime_c start seed {args.seed} "
          f"episodes_per_chunk {args.episodes_per_chunk} "
          f"num_chunks {max_chunks} target_tokens {args.target_tokens} "
          f"procs {args.procs} out {out_dir}", flush=True)
    if done:
        print(f"resuming past {len(done)} done chunks, "
              f"{total_eps:,} episodes, {total_tokens:,} tokens", flush=True)

    heldout_info = None
    if args.heldout > 0:
        heldout_info = write_heldout(args, params)

    def pending_ids():
        i = 0
        while max_chunks is None or i < max_chunks:
            if i not in done_ids:
                yield i
            i += 1

    run_start = time.time()
    run_eps = 0
    run_tokens = 0
    run_chunks = 0
    stop_reason = "all_chunks"

    def should_stop() -> str | None:
        if args.target_tokens is not None and total_tokens >= args.target_tokens:
            return "target_reached"
        if (args.max_seconds is not None
                and time.time() - run_start >= args.max_seconds):
            return "deadline"
        return None

    def note(stats: dict) -> None:
        nonlocal total_eps, total_tokens, run_eps, run_tokens, run_chunks
        total_eps += stats["episodes"]
        total_tokens += stats["tokens"]
        run_eps += stats["episodes"]
        run_tokens += stats["tokens"]
        run_chunks += 1
        elapsed = max(1e-9, time.time() - run_start)
        print(f"chunk {stats['id']:05d} eps {stats['episodes']} "
              f"tokens {stats['tokens']:,} in {stats['seconds']}s | "
              f"total eps {total_eps:,} tokens {total_tokens:,} | "
              f"run {run_eps / elapsed:.1f} eps/s "
              f"{run_tokens / elapsed:,.0f} tok/s", flush=True)

    ids = pending_ids()
    if args.procs <= 1:
        _init_worker(tokenizer_path, params)
        for cid in ids:
            reason = should_stop()
            if reason:
                stop_reason = reason
                break
            note(_render_chunk(cid))
        else:
            stop_reason = "all_chunks"
    else:
        ctx = mp.get_context("fork")
        with ctx.Pool(args.procs, initializer=_init_worker,
                      initargs=(tokenizer_path, params)) as pool:
            inflight: dict[int, object] = {}
            exhausted = False
            stopping = False
            while True:
                reason = should_stop()
                if reason and not stopping:
                    stop_reason = reason
                    stopping = True
                while (not stopping and not exhausted
                       and len(inflight) < args.procs):
                    cid = next(ids, None)
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
                for cid in ready:
                    note(inflight.pop(cid).get())
                reason = should_stop()
                if reason and not stopping:
                    stop_reason = reason
                    stopping = True
            if not stopping:
                stop_reason = "all_chunks"
            pool.close()
            pool.join()

    manifest = write_manifest(out_dir, params, tokenizer_path, heldout_info)
    elapsed = time.time() - run_start
    print(f"this run: {run_chunks} chunks, {run_eps:,} episodes, "
          f"{run_tokens:,} tokens in {elapsed:.1f}s "
          f"({run_eps / max(1e-9, elapsed):.2f} eps/s, "
          f"{run_tokens / max(1e-9, elapsed):,.0f} tok/s)", flush=True)
    print(f"DONE reason {stop_reason} chunks {len(manifest['chunks'])} "
          f"episodes {manifest['total_episodes']:,} "
          f"tokens {manifest['total_tokens']:,}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
