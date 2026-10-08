"""Command line entry point for the NRM task benchmark.

Builds the three suites, runs one checkpoint through every condition, and
writes results json plus a readable report:

    uv run python -m scripts.run_nrm_bench \
        --ckpt ~/runs/webdemo/ckpt-curve-350md-401.pt \
        --tokenizer ~/runs/tokenizer_v2/tokenizer_v2.json \
        --out-dir ~/runs/nrm-bench/dry \
        --model-name curve-350md-401 \
        --parquet-dir ~/data/regime_a/parquet \
        --n-synthetic 40 --n-scrubbed 24 --n-real 30 --api-budget 300

Suite construction is seeded and held out from training: worldgen episodes
come from a base seed outside the render seeds, and scrubbed-web bundles
are drawn and scrubbed under their own seed. Real-web questions are the
authored file under src/evals/data/nrm_bench.

Rows stream to <out-dir>/rows-<model>.jsonl as they finish, so a killed
run keeps whatever it paid for; live searches are disk cached in the same
directory and capped by --api-budget, counted against every earlier run
that shared the cache.
"""

import argparse
import json
import time
from pathlib import Path

from src.evals.nrm_bench import (BudgetedSearchClient, RunnerContext,
                                 build_scrubbed_web_suite,
                                 build_synthetic_suite, format_report,
                                 load_real_web_suite, make_web_index_factory,
                                 reaggregate, run_bench, subsample)

HELDOUT_WORLDGEN_SEED = 20260901
HELDOUT_SCRUB_SEED = 20260901
BUNDLE_DOCS = 14
BUNDLE_DOC_CHARS = 1200
MIN_DOC_CHARS = 200


def parquet_bundles(parquet_dir: str, n_bundles: int, seed: int,
                    docs_per_bundle: int = BUNDLE_DOCS,
                    doc_chars: int = BUNDLE_DOC_CHARS) -> list:
    """Scrubbed document bundles drawn from the regime A parquet corpus.

    A seeded (file, row group) pick is read whole and consumed in stored
    order, the same walk render_regime_e uses, and every document is
    scrubbed under a seed derived from its bundle position, so the bundles
    are reproducible and hold no real entity facts.
    """
    import numpy as np
    import pyarrow.parquet as pq

    from scripts.render_regime_e import clip_passage
    from src.scrub.scrubber import scrub_text

    files = sorted(str(p) for p in Path(parquet_dir).glob("*.parquet"))
    if not files:
        raise SystemExit(f"no parquet files under {parquet_dir}")
    handles: dict = {}
    row_groups = []
    for i, path in enumerate(files):
        handles[i] = pq.ParquetFile(path)
        row_groups.append(handles[i].num_row_groups)

    rng = np.random.default_rng((int(seed), 7))
    buf: list = []

    def next_doc() -> str:
        while not buf:
            fi = int(rng.integers(len(files)))
            gi = int(rng.integers(row_groups[fi]))
            column = handles[fi].read_row_group(
                gi, columns=["text"]).column("text")
            texts = [t for t in column.to_pylist()
                     if isinstance(t, str) and len(t) >= MIN_DOC_CHARS]
            buf.extend(reversed(texts))
        return buf.pop()

    bundles = []
    for b in range(n_bundles):
        docs = []
        for j in range(docs_per_bundle):
            raw = clip_passage(next_doc(), doc_chars)
            docs.append(scrub_text(raw, (int(seed), b, 23, j)).text)
        bundles.append(docs)
    return bundles


def prior_live_calls(usage_path: Path) -> int:
    total = 0
    if usage_path.exists():
        with open(usage_path) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    total += json.loads(line).get("live_calls", 0)
    return total


def build_items(args, tokenizer) -> list:
    """The three suites, each cut to its requested size.

    Caps go through subsample rather than a head slice so a smaller run
    still holds every task family and category the full suite has, the
    unanswerable items included.
    """
    from src.worldgen.engine import generate_episodes

    items = []
    if "synthetic" in args.suites:
        episodes = list(generate_episodes(args.worldgen_seed,
                                          args.n_episodes))
        items.extend(subsample(build_synthetic_suite(episodes),
                               args.n_synthetic, seed=args.seed))
    if "scrubbed" in args.suites:
        bundles = parquet_bundles(args.parquet_dir, args.n_bundles,
                                  args.scrub_seed)
        items.extend(subsample(
            build_scrubbed_web_suite(bundles, seed=args.scrub_seed),
            args.n_scrubbed, seed=args.seed))
    if "real" in args.suites:
        items.extend(subsample(load_real_web_suite(args.real_web_path),
                               args.n_real, seed=args.seed))
    return items


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m scripts.run_nrm_bench")
    parser.add_argument("--ckpt")
    parser.add_argument("--tokenizer")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--rescore-from", default=None,
                        help="rebuild the metric blocks and the report from "
                             "an existing results json, no model needed")
    parser.add_argument("--model-name", default="model")
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--suites", nargs="+",
                        default=["synthetic", "scrubbed", "real"],
                        choices=["synthetic", "scrubbed", "real"])
    parser.add_argument("--conditions", nargs="+",
                        default=["retrieval", "no_retrieval",
                                 "oracle_context"])
    parser.add_argument("--n-episodes", type=int, default=40)
    parser.add_argument("--n-synthetic", type=int, default=0,
                        help="cap on synthetic items, 0 for all")
    parser.add_argument("--n-bundles", type=int, default=12)
    parser.add_argument("--n-scrubbed", type=int, default=0)
    parser.add_argument("--n-real", type=int, default=0)
    parser.add_argument("--parquet-dir", default="")
    parser.add_argument("--real-web-path", default=None)
    parser.add_argument("--worldgen-seed", type=int,
                        default=HELDOUT_WORLDGEN_SEED)
    parser.add_argument("--scrub-seed", type=int, default=HELDOUT_SCRUB_SEED)
    parser.add_argument("--max-rounds", type=int, default=3)
    parser.add_argument("--max-new-tokens", type=int, default=96)
    parser.add_argument("--chunk-tokens", type=int, default=256)
    parser.add_argument("--num-results", type=int, default=5)
    parser.add_argument("--api-budget", type=int, default=300)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args(argv)

    out_dir = Path(args.out_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.rescore_from:
        with open(Path(args.rescore_from).expanduser()) as fh:
            results = reaggregate(json.load(fh), tuple(args.conditions))
        name = results.get("model", args.model_name)
        with open(out_dir / f"results-{name}.json", "w") as fh:
            json.dump(results, fh, indent=1)
        report = format_report(results)
        with open(out_dir / f"report-{name}.txt", "w") as fh:
            fh.write(report + "\n")
        print(report)
        return 0

    if not args.ckpt or not args.tokenizer:
        raise SystemExit("--ckpt and --tokenizer are required to run a model")
    if "scrubbed" in args.suites and not args.parquet_dir:
        raise SystemExit("--parquet-dir is required for the scrubbed suite")
    rows_path = out_dir / f"rows-{args.model_name}.jsonl"
    usage_path = out_dir / "exa-usage.jsonl"
    cache_path = out_dir / "exa-cache.json"

    from src.evals.interactive import make_checkpoint_step_fn
    from src.train.tokenizer import load_tokenizer

    tokenizer = load_tokenizer(str(Path(args.tokenizer).expanduser()))
    items = build_items(args, tokenizer)
    print(f"built {len(items)} items across {args.suites}", flush=True)

    client = None
    factory = None
    if any(item.web for item in items):
        from src.retrieval_web.exa import ExaClient

        client = BudgetedSearchClient(
            ExaClient(), cache_path, budget=args.api_budget,
            prior_calls=prior_live_calls(usage_path))
        factory = make_web_index_factory(
            client, tokenizer, chunk_tokens=args.chunk_tokens,
            num_results=args.num_results)

    t0 = time.monotonic()
    step_fn, _model, state = make_checkpoint_step_fn(
        str(Path(args.ckpt).expanduser()), args.device)
    print(f"loaded {args.model_name} step {state.get('step')} in "
          f"{time.monotonic() - t0:.1f}s", flush=True)

    ctx = RunnerContext(
        step_fn=step_fn, tokenizer=tokenizer, max_rounds=args.max_rounds,
        max_new_tokens=args.max_new_tokens, seed=args.seed,
        web_index_factory=factory, label=args.model_name)

    sink = open(rows_path, "w")
    done = {"n": 0}

    def on_record(record):
        sink.write(json.dumps(record) + "\n")
        sink.flush()
        done["n"] += 1
        if done["n"] % 20 == 0:
            print(f"  {done['n']} records, "
                  f"{time.monotonic() - t0:.0f}s elapsed", flush=True)

    try:
        results = run_bench(items, ctx, conditions=tuple(args.conditions),
                            on_record=on_record)
    finally:
        sink.close()

    results["items"] = [item.to_dict() for item in items]
    results["checkpoint"] = {"path": str(args.ckpt),
                             "step": state.get("step")}
    results["suite_config"] = {
        "suites": args.suites, "n_episodes": args.n_episodes,
        "worldgen_seed": args.worldgen_seed, "scrub_seed": args.scrub_seed,
        "n_bundles": args.n_bundles, "chunk_tokens": args.chunk_tokens,
        "num_results": args.num_results,
    }
    if client is not None:
        results["exa_usage"] = client.usage()
        with open(usage_path, "a") as fh:
            fh.write(json.dumps({"model": args.model_name,
                                 **client.usage()}) + "\n")

    results_path = out_dir / f"results-{args.model_name}.json"
    with open(results_path, "w") as fh:
        json.dump(results, fh, indent=1)
    report = format_report(results)
    with open(out_dir / f"report-{args.model_name}.txt", "w") as fh:
        fh.write(report + "\n")
    print(report)
    print(f"wrote {results_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
