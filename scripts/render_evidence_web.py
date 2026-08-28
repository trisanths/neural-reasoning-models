"""Pre-render scrubbed-web episodes as JSONL for the evidence-bank data path.

The evidence cross-attention lane trains on (question, evidence bank, answer)
triples from two sources. Worldgen episodes are generated on the fly inside
the data stream, because src.worldgen.engine is cheap and index addressable.
Scrubbed-web episodes are not: each bundle needs a parquet read, a scrub pass
over a dozen documents, and a BM25 verification of every candidate question,
which is far too much CPU to run beside a training step. So they are rendered
once here and shipped as a file the lane reads.

Each output line is one episode in the shape src.train.evidence_data
.examples_from_web_episode expects: a world block, a document list, and
questions carrying a verified retrieval plan whose last hop names the
document holding the answer span.

    uv run python -m scripts.render_evidence_web \
        --parquet ~/b4work/parquet/013_00000.parquet \
        --out ~/data/evidence_web/episodes.jsonl --episodes 20000 --seed 4731

Deterministic in (seed, parquet file order, knobs). Episodes whose candidate
questions all fail verification are dropped and counted; the run fails if the
drop rate says the corpus cannot support verified traces at all.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

from scripts.render_regime_e import ParquetDocStream, clip_passage
from src.scrub.name_pool import harvest_pool
from src.scrub.scrubber import scrub_text
from src.scrub.web_retrieval import build_web_episode, verify_web_episode

# Consecutive failed bundles before we call the corpus unusable. The same
# bound render_regime_e puts on its webret sampler, for the same reason: a
# corpus that cannot support one verified trace in fifty is a broken input,
# not a slow one.
MAX_CONSECUTIVE_FAILURES = 50


def build_argparser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="scripts.render_evidence_web")
    ap.add_argument("--parquet", nargs="+", required=True,
                    help="one or more parquet files with a text column")
    ap.add_argument("--out", required=True, help="output jsonl path")
    ap.add_argument("--episodes", type=int, required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--min-docs", type=int, default=12)
    ap.add_argument("--max-docs", type=int, default=30)
    ap.add_argument("--doc-chars", type=int, default=1200)
    ap.add_argument("--min-doc-chars", type=int, default=600)
    ap.add_argument("--questions", type=int, default=4)
    ap.add_argument("--two-hop", type=float, default=0.25)
    ap.add_argument("--context-docs", type=int, default=3)
    ap.add_argument("--query-first", type=float, default=0.0,
                    help="share of episodes with no in-context prefix")
    ap.add_argument("--entity-policy", default="shuffle",
                    choices=("invent", "shuffle"))
    ap.add_argument("--pool-docs", type=int, default=400,
                    help="documents harvested for the name pool under shuffle")
    ap.add_argument("--pool-max-forms", type=int, default=20000)
    ap.add_argument("--pool-min-count", type=int, default=2)
    ap.add_argument("--verify", action="store_true",
                    help="re-check every episode with verify_web_episode")
    ap.add_argument("--progress-every", type=int, default=500)
    return ap


def open_stream(files: list, seed_material: tuple, min_chars: int) -> ParquetDocStream:
    row_groups = [pq.ParquetFile(f).num_row_groups for f in files]
    return ParquetDocStream(files, row_groups,
                            np.random.default_rng(seed_material), min_chars)


def main(argv: list[str] | None = None) -> int:
    args = build_argparser().parse_args(argv)
    files = [str(Path(p).expanduser()) for p in args.parquet]
    for path in files:
        if not Path(path).exists():
            raise SystemExit(f"parquet file {path} does not exist")

    pool = None
    if args.entity_policy == "shuffle":
        pool_stream = open_stream(files, (args.seed, 5), args.min_doc_chars)
        pool = harvest_pool(
            [pool_stream.next_doc() for _ in range(args.pool_docs)],
            max_forms=args.pool_max_forms, min_count=args.pool_min_count)

    stream = open_stream(files, (args.seed, 7), args.min_doc_chars)
    rng = np.random.default_rng((args.seed, 19))
    state: dict = {}

    out_path = Path(args.out).expanduser()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_name(out_path.name + ".tmp")

    written = 0
    attempts = 0
    dropped_questions = 0
    failures = 0
    verify_failures = 0
    n_questions = 0
    n_hops = 0
    query_first_written = 0
    start = time.time()

    with open(tmp_path, "w") as fh:
        while written < args.episodes:
            i = attempts
            attempts += 1
            n_docs = int(rng.integers(args.min_docs, args.max_docs + 1))
            docs = []
            for j in range(n_docs):
                raw = clip_passage(stream.next_doc(), args.doc_chars)
                docs.append(scrub_text(
                    raw, (args.seed, 23, i, j),
                    entity_policy=args.entity_policy, pool=pool).text)
            query_first = bool(query_first_written < args.query_first * (written + 1))
            episode = build_web_episode(
                docs, (args.seed, 29, i), n_questions=args.questions,
                two_hop_share=args.two_hop, query_first=query_first,
                n_context=args.context_docs, state=state)
            dropped_questions += episode["stats"]["dropped"]
            if not episode["questions"]:
                failures += 1
                if failures >= MAX_CONSECUTIVE_FAILURES:
                    raise SystemExit(
                        f"{failures} consecutive bundles produced no verified "
                        f"question; the corpus does not support retrieval traces")
                continue
            if args.verify:
                problems = verify_web_episode(episode)
                if problems:
                    verify_failures += 1
                    failures += 1
                    continue
            failures = 0
            episode["episode_id"] = f"web-{written:06d}"
            episode.pop("stats", None)
            fh.write(json.dumps(episode) + "\n")
            written += 1
            n_questions += len(episode["questions"])
            n_hops += sum(len(q["plan"]) for q in episode["questions"])
            if query_first:
                query_first_written += 1
            if args.progress_every and written % args.progress_every == 0:
                rate = written / max(1e-9, time.time() - start)
                print(f"{written}/{args.episodes} episodes, "
                      f"{rate:.1f}/s, {attempts} bundles tried", flush=True)

    tmp_path.replace(out_path)
    meta = {
        "episodes": written,
        "bundles_tried": attempts,
        "questions": n_questions,
        "questions_per_episode": round(n_questions / max(1, written), 3),
        "hops": n_hops,
        "hops_per_question": round(n_hops / max(1, n_questions), 3),
        "dropped_questions": dropped_questions,
        "verify_failures": verify_failures,
        "query_first": query_first_written,
        "seed": args.seed,
        "parquet": files,
        "knobs": {
            "min_docs": args.min_docs, "max_docs": args.max_docs,
            "doc_chars": args.doc_chars, "min_doc_chars": args.min_doc_chars,
            "questions": args.questions, "two_hop": args.two_hop,
            "context_docs": args.context_docs,
            "entity_policy": args.entity_policy,
        },
        "seconds": round(time.time() - start, 1),
        "bytes": out_path.stat().st_size,
    }
    with open(str(out_path) + ".meta.json", "w") as fh:
        json.dump(meta, fh, indent=2)
    print(json.dumps(meta, indent=2))
    print(f"wrote {written} episodes to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
