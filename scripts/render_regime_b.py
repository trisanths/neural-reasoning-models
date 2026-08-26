"""Render regime B training data: natural language plus synthetic reasoning
mixed, the additive control from SPEC.md section 1.

Three token sources feed one interleaved uint16 stream:

  natural   fixed length windows resampled from already rendered regime A
            shards (no re-tokenization of parquet),
  worldgen  episodes rendered without retrieval traces, so every document
            and the question answer pairs sit in context,
  procgen   procedural warm-up examples mapped into the reserved vocab
            range [PROCGEN_OFFSET, PROCGEN_OFFSET + 256).

Default mix by tokens: 80 percent natural, 15 percent worldgen, 5 percent
procgen. Within a chunk the next segment always comes from the source
furthest below its target share, so the realized mix tracks the target
tightly and deterministically.

Work is split into numbered chunks. Chunk k draws worldgen episode indices
from [k * episode_stride, (k + 1) * episode_stride) under one base seed and
gets its own natural and procgen rngs seeded by (base_seed, k), so any chunk
is reproducible in isolation. Each chunk writes shards plus index.json into
its own directory, then a .done marker holding its stats. A restart skips
chunks with markers and wipes partial chunk directories, so the pipeline is
resumable after a kill at any point. Every run ends by writing manifest.json
and a merged top level index.json over all finished chunks; ShardReader can
open the output directory directly through that merged index.

Usage:

    uv run python -m scripts.render_regime_b \
        --out ~/data/regime_b \
        --natural-shards ~/data/regime_a/shards \
        --tokenizer ~/runs/tokenizer_v2/tokenizer_v2.json \
        --seed 20260825 --target-tokens 7000000000 --procs 4

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

import numpy as np

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

from src.procgen.cli import DEFAULT_MIX as PROCGEN_DEFAULT_MIX
from src.procgen.cli import GENERATORS as PROCGEN_GENERATORS
from src.procgen.cli import parse_mix as parse_procgen_mix
from src.train.data import INDEX_NAME, ShardReader, ShardWriter, render_episode
from src.train.tokenizer import PROCGEN_OFFSET, load_tokenizer
from src.worldgen.domains import DOMAIN_ORDER
from src.worldgen.engine import generate_episodes

MANIFEST_NAME = "manifest.json"
HELDOUT_INDEX_BASE = 1_000_000_000
SOURCE_NAMES = ("natural", "worldgen", "procgen")

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


def normalize_mix(natural: float, worldgen: float, procgen: float) -> dict:
    """Return name to positive normalized weight; zero weight sources drop."""
    raw = dict(zip(SOURCE_NAMES, (natural, worldgen, procgen)))
    for name, w in raw.items():
        if w < 0:
            raise ValueError(f"mix weight for {name} must be nonnegative")
    total = sum(raw.values())
    if total <= 0:
        raise ValueError("mix weights sum to zero")
    return {name: w / total for name, w in raw.items() if w > 0}


class NaturalSampler:
    """Yields seeded random windows from a rendered shard directory."""

    def __init__(self, reader: ShardReader, window: int, rng):
        if reader.total_tokens < window:
            raise ValueError(
                f"natural shards hold {reader.total_tokens} tokens, "
                f"fewer than one window of {window}")
        self.reader = reader
        self.window = window
        self.rng = rng
        self.windows = 0

    def next_segment(self) -> np.ndarray:
        start = int(self.rng.integers(
            0, self.reader.total_tokens - self.window, endpoint=True))
        self.windows += 1
        return self.reader.get_slice(start, self.window)


class WorldgenSampler:
    """Yields whole episodes rendered without retrieval traces."""

    def __init__(self, tok, base_seed: int, chunk_id: int, stride: int,
                 domains, contradiction_rate: float, filler_rate: float,
                 max_doc_tokens):
        self.tok = tok
        self.index_base = chunk_id * stride
        self.stride = stride
        self.max_doc_tokens = max_doc_tokens
        self.episodes = 0
        self.stream = generate_episodes(
            base_seed, stride, domains=domains,
            contradiction_rate=contradiction_rate, filler_rate=filler_rate,
            start_index=self.index_base)

    def next_segment(self) -> list[int]:
        episode = next(self.stream, None)
        if episode is None:
            raise RuntimeError(
                f"chunk exhausted its worldgen index stride of {self.stride}; "
                f"raise --episode-stride")
        self.episodes += 1
        return render_episode(episode, self.tok,
                              max_doc_tokens=self.max_doc_tokens)


class ProcgenSampler:
    """Yields single procgen examples shifted into the reserved vocab range.

    Generator choice inside the procgen share follows the same deficit rule
    as the top level source mix.
    """

    def __init__(self, mix: dict, rng):
        self.mix = mix
        self.names = sorted(mix)
        self.rng = rng
        self.token_counts = {name: 0 for name in self.names}
        self.examples = 0

    def next_segment(self) -> np.ndarray:
        name = min(self.names,
                   key=lambda n: (self.token_counts[n] / self.mix[n], n))
        example = np.asarray(PROCGEN_GENERATORS[name](self.rng),
                             dtype=np.uint16)
        self.token_counts[name] += int(example.size)
        self.examples += 1
        return example + PROCGEN_OFFSET


def _init_worker(tokenizer_path: str, params: dict) -> None:
    _G["tok"] = load_tokenizer(tokenizer_path)
    _G["params"] = params
    _G["natural_reader"] = ShardReader(params["natural_shards"])
    _G["procgen_mix"] = parse_procgen_mix(params["procgen_mix"])


def _render_chunk(chunk_id: int) -> dict:
    p = _G["params"]
    chunk_dir, marker = chunk_paths(p["out_dir"], chunk_id)
    if marker.exists():
        with open(marker) as fh:
            return json.load(fh)
    shutil.rmtree(chunk_dir, ignore_errors=True)
    t0 = time.time()

    mix = p["mix"]
    samplers = {}
    if "natural" in mix:
        samplers["natural"] = NaturalSampler(
            _G["natural_reader"], p["natural_window"],
            np.random.default_rng((p["base_seed"], chunk_id, 1)))
    if "worldgen" in mix:
        samplers["worldgen"] = WorldgenSampler(
            _G["tok"], p["base_seed"], chunk_id, p["episode_stride"],
            p["domains"], p["contradiction_rate"], p["filler_rate"],
            p["max_doc_tokens"])
    if "procgen" in mix:
        samplers["procgen"] = ProcgenSampler(
            _G["procgen_mix"],
            np.random.default_rng((p["base_seed"], chunk_id, 2)))

    writer = ShardWriter(str(chunk_dir), shard_size=p["shard_size"])
    counts = {name: 0 for name in samplers}
    order = sorted(samplers)
    total = 0
    while total < p["chunk_tokens"]:
        name = min(order, key=lambda n: (counts[n] / mix[n], n))
        segment = samplers[name].next_segment()
        writer.write(segment)
        counts[name] += len(segment)
        total += len(segment)
    writer.close()

    stats = {
        "id": chunk_id,
        "tokens": total,
        "source_tokens": counts,
        "natural_windows": samplers["natural"].windows
        if "natural" in samplers else 0,
        "worldgen_episodes": samplers["worldgen"].episodes
        if "worldgen" in samplers else 0,
        "worldgen_index_base": samplers["worldgen"].index_base
        if "worldgen" in samplers else None,
        "procgen_examples": samplers["procgen"].examples
        if "procgen" in samplers else 0,
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


def write_merged_index(out_dir) -> dict:
    """Merge every finished chunk's index into one top level index.json that
    ShardReader can open directly on the output directory."""
    shards = []
    for stats in scan_done(out_dir):
        chunk_dir, _ = chunk_paths(out_dir, stats["id"])
        with open(chunk_dir / INDEX_NAME) as fh:
            chunk_index = json.load(fh)
        for shard in chunk_index["shards"]:
            shards.append({
                "file": f"{chunk_dir.name}/{shard['file']}",
                "num_tokens": shard["num_tokens"],
            })
    index = {
        "dtype": "uint16",
        "shards": shards,
        "total_tokens": int(sum(s["num_tokens"] for s in shards)),
    }
    _atomic_json(Path(out_dir) / INDEX_NAME, index)
    return index


def write_manifest(out_dir, params, tokenizer_path) -> dict:
    chunks = scan_done(out_dir)
    totals = {name: 0 for name in SOURCE_NAMES}
    for chunk in chunks:
        for name, n in chunk["source_tokens"].items():
            totals[name] += n
    manifest = {
        "regime": "b",
        "base_seed": params["base_seed"],
        "mix": params["mix"],
        "natural_shards": params["natural_shards"],
        "natural_window": params["natural_window"],
        "procgen_mix": params["procgen_mix"],
        "domains": params["domains"],
        "contradiction_rate": params["contradiction_rate"],
        "filler_rate": params["filler_rate"],
        "episode_stride": params["episode_stride"],
        "chunk_tokens": params["chunk_tokens"],
        "max_doc_tokens": params["max_doc_tokens"],
        "shard_size": params["shard_size"],
        "tokenizer": str(tokenizer_path),
        "chunks": chunks,
        "total_tokens": sum(c["tokens"] for c in chunks),
        "total_source_tokens": totals,
        "total_worldgen_episodes": sum(
            c["worldgen_episodes"] for c in chunks),
    }
    _atomic_json(Path(out_dir) / MANIFEST_NAME, manifest)
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="python -m scripts.render_regime_b",
        description="Render regime B shards: natural windows resampled from "
                    "regime A plus worldgen QA episodes plus procgen "
                    "streams, resumable by chunk.",
    )
    parser.add_argument("--out", required=True, help="output directory")
    parser.add_argument("--tokenizer", required=True)
    parser.add_argument("--natural-shards", required=True,
                        help="rendered regime A shard directory")
    parser.add_argument("--seed", type=int, required=True, help="base seed")
    parser.add_argument("--chunk-tokens", type=int, default=1 << 25,
                        help="minimum tokens per chunk; the final segment "
                             "may overshoot slightly")
    parser.add_argument("--num-chunks", type=int, default=None,
                        help="total planned chunks; chunk ids are "
                             "[0, num_chunks)")
    parser.add_argument("--target-tokens", type=int, default=None,
                        help="stop submitting chunks once completed tokens "
                             "reach this")
    parser.add_argument("--procs", type=int, default=1)
    parser.add_argument("--mix-natural", type=float, default=0.80)
    parser.add_argument("--mix-worldgen", type=float, default=0.15)
    parser.add_argument("--mix-procgen", type=float, default=0.05)
    parser.add_argument("--natural-window", type=int, default=4096,
                        help="tokens per resampled natural window")
    parser.add_argument("--procgen-mix", default=PROCGEN_DEFAULT_MIX,
                        help="name=weight,... mix inside the procgen share")
    parser.add_argument("--episode-stride", type=int, default=100_000,
                        help="worldgen episode index range reserved per chunk")
    parser.add_argument("--max-doc-tokens", type=int, default=None,
                        help="per episode document budget; default keeps "
                             "every document in context")
    parser.add_argument("--shard-size", type=int, default=1 << 24)
    parser.add_argument("--domains", default=",".join(DOMAIN_ORDER))
    parser.add_argument("--contradiction-rate", type=float, default=0.15)
    parser.add_argument("--filler-rate", type=float, default=0.25)
    parser.add_argument("--max-seconds", type=float, default=None,
                        help="stop submitting new chunks after this many "
                             "seconds; in-flight chunks finish")
    args = parser.parse_args(argv)

    if args.num_chunks is None and args.target_tokens is None:
        parser.error("need --num-chunks or --target-tokens")
    mix = normalize_mix(args.mix_natural, args.mix_worldgen, args.mix_procgen)
    domains = [d.strip() for d in args.domains.split(",") if d.strip()]
    out_dir = Path(os.path.expanduser(args.out))
    out_dir.mkdir(parents=True, exist_ok=True)
    tokenizer_path = os.path.expanduser(args.tokenizer)
    natural_shards = os.path.expanduser(args.natural_shards)
    parse_procgen_mix(args.procgen_mix)

    max_chunks = args.num_chunks
    chunk_cap = HELDOUT_INDEX_BASE // args.episode_stride
    if max_chunks is not None and max_chunks > chunk_cap:
        parser.error("worldgen index range would reach the held-out range")

    params = {
        "out_dir": str(out_dir),
        "base_seed": args.seed,
        "mix": mix,
        "natural_shards": natural_shards,
        "natural_window": args.natural_window,
        "procgen_mix": args.procgen_mix,
        "domains": domains,
        "contradiction_rate": args.contradiction_rate,
        "filler_rate": args.filler_rate,
        "episode_stride": args.episode_stride,
        "chunk_tokens": args.chunk_tokens,
        "max_doc_tokens": args.max_doc_tokens,
        "shard_size": args.shard_size,
    }

    done = scan_done(out_dir)
    done_ids = {c["id"] for c in done}
    total_tokens = sum(c["tokens"] for c in done)
    print(f"render_regime_b start seed {args.seed} mix {mix} "
          f"chunk_tokens {args.chunk_tokens} num_chunks {max_chunks} "
          f"target_tokens {args.target_tokens} procs {args.procs} "
          f"out {out_dir}", flush=True)
    if done:
        print(f"resuming past {len(done)} done chunks, "
              f"{total_tokens:,} tokens", flush=True)

    def pending_ids():
        i = 0
        while max_chunks is None or i < max_chunks:
            if i >= chunk_cap:
                raise RuntimeError(
                    "chunk id would push worldgen indices into the "
                    "held-out range")
            if i not in done_ids:
                yield i
            i += 1

    run_start = time.time()
    run_tokens = 0
    run_chunks = 0
    stop_reason = "all_chunks"

    def should_stop() -> str | None:
        if (args.target_tokens is not None
                and total_tokens >= args.target_tokens):
            return "target_reached"
        if (args.max_seconds is not None
                and time.time() - run_start >= args.max_seconds):
            return "deadline"
        return None

    def note(stats: dict) -> None:
        nonlocal total_tokens, run_tokens, run_chunks
        total_tokens += stats["tokens"]
        run_tokens += stats["tokens"]
        run_chunks += 1
        elapsed = max(1e-9, time.time() - run_start)
        src = " ".join(f"{k} {v:,}"
                       for k, v in sorted(stats["source_tokens"].items()))
        print(f"chunk {stats['id']:05d} tokens {stats['tokens']:,} "
              f"({src}) in {stats['seconds']}s | "
              f"total tokens {total_tokens:,} | "
              f"run {run_tokens / elapsed:,.0f} tok/s", flush=True)

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

    manifest = write_manifest(out_dir, params, tokenizer_path)
    index = write_merged_index(out_dir)
    elapsed = time.time() - run_start
    totals = manifest["total_source_tokens"]
    grand = max(1, manifest["total_tokens"])
    shares = " ".join(f"{k} {totals[k] / grand:.4f}"
                      for k in SOURCE_NAMES if totals[k])
    print(f"this run: {run_chunks} chunks, {run_tokens:,} tokens "
          f"in {elapsed:.1f}s "
          f"({run_tokens / max(1e-9, elapsed):,.0f} tok/s)", flush=True)
    print(f"DONE reason {stop_reason} chunks {len(manifest['chunks'])} "
          f"tokens {manifest['total_tokens']:,} "
          f"index_tokens {index['total_tokens']:,} "
          f"shares {shares}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
