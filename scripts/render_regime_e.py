"""Render regime E training data: scrubbed natural text, extractive QA
traces over scrubbed passages, worldgen retrieval episodes, and procgen.

Four token sources feed one interleaved uint16 stream:

  natural   documents read from the regime A parquet raw text, scrubbed
            through src/scrub so no real-world entity or figure survives,
            tokenized fresh, capped at --natural-window tokens, and closed
            with <|eot|>,
  qa        extractive QA traces from src/scrub/extractive_qa over scrubbed
            passages of the same parquet text, laid out with the worldgen
            special-token format (<|world|> domain marker, <|doc|> passage,
            <|q|> question <|a|> answer <|eot|>) so the C-style elicitation
            applies,
  worldgen  episodes rendered with multi-hop retrieval traces through
            src/train/retrieval.py, the regime C machinery,
  procgen   procedural examples in the reserved vocab range.

Default mix by tokens: 70 percent natural, 15 percent qa, 10 percent
worldgen, 5 percent procgen. Within a chunk the next segment always comes
from the source furthest below its target share, exactly as in regime B.

Work is split into numbered chunks. Chunk k draws worldgen episode indices
from [k * episode_stride, (k + 1) * episode_stride) under one base seed, and
every other source gets rngs seeded by (base_seed, k), so any chunk is
reproducible in isolation. Natural and qa documents come from seeded random
parquet row groups read whole and consumed in stored order. Each chunk
writes shards plus index.json into its own directory, then a .done marker
holding its stats. A restart skips chunks with markers and wipes partial
chunk directories, so the pipeline is resumable after a kill at any point.
Every run ends by writing manifest.json and a merged top level index.json
over all finished chunks; ShardReader can open the output directory
directly through that merged index.

Usage:

    uv run python -m scripts.render_regime_e \
        --out ~/data/regime_e \
        --parquet-dir ~/data/regime_a/parquet \
        --tokenizer ~/runs/tokenizer_v2/tokenizer_v2.json \
        --seed 20260826 --target-tokens 7000000000 --procs 4

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
from collections import deque
from pathlib import Path

import numpy as np

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import pyarrow.parquet as pq

from scripts.render_regime_b import ProcgenSampler, WorldgenSampler
from src.procgen.cli import DEFAULT_MIX as PROCGEN_DEFAULT_MIX
from src.procgen.cli import parse_mix as parse_procgen_mix
from src.scrub.extractive_qa import (DEFAULT_TYPE_MIX, generate_qa,
                                     render_qa_trace)
from src.scrub.scrubber import scrub_text
from src.train.data import INDEX_NAME, ShardReader, ShardWriter
from src.train.tokenizer import load_tokenizer
from src.worldgen.domains import DOMAIN_ORDER

MANIFEST_NAME = "manifest.json"
HELDOUT_INDEX_BASE = 1_000_000_000
SOURCE_NAMES = ("natural", "qa", "worldgen", "procgen")
ENCODE_BATCH = 32

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


def normalize_mix(weights: dict) -> dict:
    """Return name to positive normalized weight; zero weight sources drop."""
    for name, w in weights.items():
        if w < 0:
            raise ValueError(f"mix weight for {name} must be nonnegative")
    total = sum(weights.values())
    if total <= 0:
        raise ValueError("mix weights sum to zero")
    return {name: w / total for name, w in weights.items() if w > 0}


def parse_type_mix(spec: str) -> dict:
    """Parse name=weight,... into a normalized QA type mix."""
    weights = {}
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        name, _, value = part.partition("=")
        weights[name.strip()] = float(value)
    unknown = set(weights) - set(DEFAULT_TYPE_MIX)
    if unknown:
        raise ValueError(f"unknown question types {sorted(unknown)}")
    return normalize_mix(weights)


def clip_passage(text: str, max_chars: int) -> str:
    """Cut text at the last sentence end before max_chars, or hard cut when
    no boundary lands in the second half of the budget."""
    if len(text) <= max_chars:
        return text
    cut = max(text.rfind(t, 0, max_chars) for t in (". ", "! ", "? "))
    if cut < max_chars // 2:
        return text[:max_chars]
    return text[:cut + 1]


class ParquetDocStream:
    """Deterministic stream of raw document texts from parquet files.

    Picks a seeded random (file, row group), reads that group's text column
    once, and yields its usable rows in stored order before picking again.
    """

    def __init__(self, files: list, row_groups: list, rng, min_chars: int):
        self.files = files
        self.row_groups = row_groups
        self.rng = rng
        self.min_chars = min_chars
        self.buf: list = []
        self.handles: dict = {}

    def _file(self, i: int):
        if i not in self.handles:
            self.handles[i] = pq.ParquetFile(self.files[i])
        return self.handles[i]

    def next_doc(self) -> str:
        while not self.buf:
            fi = int(self.rng.integers(len(self.files)))
            gi = int(self.rng.integers(self.row_groups[fi]))
            col = self._file(fi).read_row_group(
                gi, columns=["text"]).column("text")
            texts = [t for t in col.to_pylist()
                     if isinstance(t, str) and len(t) >= self.min_chars]
            self.buf = texts[::-1]
        return self.buf.pop()


class ScrubbedNaturalSampler:
    """Whole scrubbed parquet documents, tokenized fresh, window capped,
    <|eot|> terminated. Documents are scrubbed one by one but encoded in
    batches for tokenizer throughput."""

    def __init__(self, tok, files, row_groups, base_seed: int, chunk_id: int,
                 window: int, min_chars: int):
        self.tok = tok
        self.base_seed = base_seed
        self.chunk_id = chunk_id
        self.window = window
        self.eot = tok.special_ids["<|eot|>"]
        self.stream = ParquetDocStream(
            files, row_groups,
            np.random.default_rng((base_seed, chunk_id, 1)), min_chars)
        self.docs = 0
        self.queue: deque = deque()

    def next_segment(self) -> list[int]:
        if not self.queue:
            texts = []
            for i in range(ENCODE_BATCH):
                seed = (self.base_seed, self.chunk_id, 11, self.docs + i)
                texts.append(scrub_text(self.stream.next_doc(), seed).text)
            self.docs += len(texts)
            for enc in self.tok.tokenizer.encode_batch(texts):
                self.queue.append(enc.ids[:self.window] + [self.eot])
        return self.queue.popleft()


class QATraceSampler:
    """Extractive QA traces over scrubbed parquet passages, rendered in the
    worldgen special-token layout."""

    def __init__(self, tok, files, row_groups, base_seed: int, chunk_id: int,
                 per_passage: int, passage_chars: int, type_mix: dict,
                 min_chars: int):
        self.tok = tok
        self.base_seed = base_seed
        self.chunk_id = chunk_id
        self.per_passage = per_passage
        self.passage_chars = passage_chars
        self.type_mix = type_mix
        self.stream = ParquetDocStream(
            files, row_groups,
            np.random.default_rng((base_seed, chunk_id, 3)), min_chars)
        self.attempts = 0
        self.traces = 0
        self.pairs = 0

    def next_segment(self) -> list[int]:
        while True:
            i = self.attempts
            self.attempts += 1
            passage = clip_passage(self.stream.next_doc(), self.passage_chars)
            scrubbed = scrub_text(
                passage, (self.base_seed, self.chunk_id, 13, i)).text
            qas = generate_qa(scrubbed, (self.base_seed, self.chunk_id, 17, i),
                              self.per_passage, mix=self.type_mix)
            if not qas:
                continue
            self.traces += 1
            self.pairs += len(qas)
            return render_qa_trace(scrubbed, qas, self.tok)


def _init_worker(tokenizer_path: str, params: dict) -> None:
    _G["tok"] = load_tokenizer(tokenizer_path)
    _G["params"] = params
    _G["procgen_mix"] = parse_procgen_mix(params["procgen_mix"])
    _G["type_mix"] = parse_type_mix(params["qa_type_mix"])


def _render_chunk(chunk_id: int) -> dict:
    p = _G["params"]
    tok = _G["tok"]
    chunk_dir, marker = chunk_paths(p["out_dir"], chunk_id)
    if marker.exists():
        with open(marker) as fh:
            return json.load(fh)
    shutil.rmtree(chunk_dir, ignore_errors=True)
    t0 = time.time()

    mix = p["mix"]
    files = p["parquet_files"]
    row_groups = p["parquet_row_groups"]
    samplers = {}
    if "natural" in mix:
        samplers["natural"] = ScrubbedNaturalSampler(
            tok, files, row_groups, p["base_seed"], chunk_id,
            p["natural_window"], p["min_doc_chars"])
    if "qa" in mix:
        samplers["qa"] = QATraceSampler(
            tok, files, row_groups, p["base_seed"], chunk_id,
            p["qa_per_passage"], p["qa_passage_chars"], _G["type_mix"],
            p["min_doc_chars"])
    if "worldgen" in mix:
        samplers["worldgen"] = WorldgenSampler(
            tok, p["base_seed"], chunk_id, p["episode_stride"],
            p["domains"], p["contradiction_rate"], p["filler_rate"],
            p["max_doc_tokens"], retrieval=True)
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
        "natural_docs": samplers["natural"].docs
        if "natural" in samplers else 0,
        "qa_traces": samplers["qa"].traces if "qa" in samplers else 0,
        "qa_pairs": samplers["qa"].pairs if "qa" in samplers else 0,
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
        "regime": "e",
        "base_seed": params["base_seed"],
        "mix": params["mix"],
        "parquet_dir": params["parquet_dir"],
        "natural_window": params["natural_window"],
        "min_doc_chars": params["min_doc_chars"],
        "qa_per_passage": params["qa_per_passage"],
        "qa_passage_chars": params["qa_passage_chars"],
        "qa_type_mix": params["qa_type_mix"],
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
        "total_natural_docs": sum(c["natural_docs"] for c in chunks),
        "total_qa_traces": sum(c["qa_traces"] for c in chunks),
        "total_qa_pairs": sum(c["qa_pairs"] for c in chunks),
        "total_worldgen_episodes": sum(
            c["worldgen_episodes"] for c in chunks),
    }
    _atomic_json(Path(out_dir) / MANIFEST_NAME, manifest)
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="python -m scripts.render_regime_e",
        description="Render regime E shards: scrubbed natural text plus "
                    "extractive QA traces plus worldgen retrieval episodes "
                    "plus procgen, resumable by chunk.",
    )
    parser.add_argument("--out", required=True, help="output directory")
    parser.add_argument("--tokenizer", required=True)
    parser.add_argument("--parquet-dir", required=True,
                        help="regime A raw parquet directory")
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
    parser.add_argument("--mix-natural", type=float, default=0.70)
    parser.add_argument("--mix-qa", type=float, default=0.15)
    parser.add_argument("--mix-worldgen", type=float, default=0.10)
    parser.add_argument("--mix-procgen", type=float, default=0.05)
    parser.add_argument("--natural-window", type=int, default=4096,
                        help="token cap per scrubbed natural document")
    parser.add_argument("--min-doc-chars", type=int, default=200,
                        help="parquet rows shorter than this are skipped")
    parser.add_argument("--qa-per-passage", type=int, default=6)
    parser.add_argument("--qa-passage-chars", type=int, default=4000)
    parser.add_argument("--qa-type-mix",
                        default=",".join(f"{k}={v}"
                                         for k, v in DEFAULT_TYPE_MIX.items()),
                        help="name=weight,... mix over question types")
    parser.add_argument("--procgen-mix", default=PROCGEN_DEFAULT_MIX,
                        help="name=weight,... mix inside the procgen share")
    parser.add_argument("--episode-stride", type=int, default=100_000,
                        help="worldgen episode index range reserved per chunk")
    parser.add_argument("--max-doc-tokens", type=int, default=None,
                        help="per episode document budget for the worldgen "
                             "share; default keeps every document in context")
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
    mix = normalize_mix({
        "natural": args.mix_natural,
        "qa": args.mix_qa,
        "worldgen": args.mix_worldgen,
        "procgen": args.mix_procgen,
    })
    parse_type_mix(args.qa_type_mix)
    parse_procgen_mix(args.procgen_mix)
    domains = [d.strip() for d in args.domains.split(",") if d.strip()]
    out_dir = Path(os.path.expanduser(args.out))
    out_dir.mkdir(parents=True, exist_ok=True)
    tokenizer_path = os.path.expanduser(args.tokenizer)

    parquet_dir = Path(os.path.expanduser(args.parquet_dir))
    files = sorted(parquet_dir.glob("*.parquet"))
    if not files:
        raise SystemExit(f"no parquet files under {parquet_dir}")
    row_groups = [pq.ParquetFile(f).num_row_groups for f in files]

    max_chunks = args.num_chunks
    chunk_cap = HELDOUT_INDEX_BASE // args.episode_stride
    if max_chunks is not None and max_chunks > chunk_cap:
        parser.error("worldgen index range would reach the held-out range")

    params = {
        "out_dir": str(out_dir),
        "base_seed": args.seed,
        "mix": mix,
        "parquet_dir": str(parquet_dir),
        "parquet_files": [str(f) for f in files],
        "parquet_row_groups": row_groups,
        "natural_window": args.natural_window,
        "min_doc_chars": args.min_doc_chars,
        "qa_per_passage": args.qa_per_passage,
        "qa_passage_chars": args.qa_passage_chars,
        "qa_type_mix": args.qa_type_mix,
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
    print(f"render_regime_e start seed {args.seed} mix {mix} "
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
