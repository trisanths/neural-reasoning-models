"""Command line entry point for the external comparison harness.

Run from the repo root in module mode so the src package resolves.
Direction one, a public HuggingFace model on our suites:

    uv run python -m scripts.run_public_bench --backend hf \
        --hf-model Qwen/Qwen3-0.6B --suites naturalized \
        --n-items 30 --seed 0 --out runs/public_bench/qwen3-0.6b

Direction two, one of our checkpoints on public QA:

    uv run python -m scripts.run_public_bench --backend ours \
        --ckpt runs/smoke-001/latest.pt \
        --tokenizer runs/smoke-001/tokenizer.json \
        --suites squad_v2 --n-items 200 --out runs/public_bench/ours

Writes public_bench_report.json to the output directory and prints one
summary line per suite. Suites may be mixed freely; both backends can
run every suite because they meet at the same predict_fn interface.
"""

import argparse
import json
from pathlib import Path

from src.evals.public_bench import (
    PUBLIC_DATASETS,
    make_hf_predict_fn,
    make_ours_predict_fn,
    run_heldout_bench,
    run_naturalized_bench,
    run_public_qa,
)

SUITE_CHOICES = ["naturalized", "heldout"] + sorted(PUBLIC_DATASETS)


def build_predict_fn(args):
    if args.backend == "hf":
        if not args.hf_model:
            raise SystemExit("--hf-model is required with --backend hf")
        return make_hf_predict_fn(
            args.hf_model, device=args.device, dtype=args.dtype,
            max_new_tokens=args.max_new_tokens,
            prompt_style=args.prompt_style, seed=args.seed)
    if not args.ckpt or not args.tokenizer:
        raise SystemExit("--ckpt and --tokenizer are required with --backend ours")
    return make_ours_predict_fn(
        args.ckpt, args.tokenizer, device=args.device, mode=args.ours_mode,
        max_rounds=args.max_rounds, max_new_tokens=args.max_new_tokens,
        chunk_words=args.chunk_words, seed=args.seed)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python scripts/run_public_bench.py")
    parser.add_argument("--backend", required=True, choices=["hf", "ours"])
    parser.add_argument("--suites", nargs="+", required=True,
                        choices=SUITE_CHOICES)
    parser.add_argument("--out", required=True, help="report output directory")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--device", default=None,
                        help="cuda or cpu, default auto")
    parser.add_argument("--n-items", type=int, default=None,
                        help="subsample size for naturalized and public QA")
    parser.add_argument("--heldout-episodes", type=int, default=20)
    parser.add_argument("--heldout-seed", type=int, default=999)
    parser.add_argument("--cache-dir", default=None,
                        help="public dataset cache, default ~/data/public_bench")
    parser.add_argument("--max-new-tokens", type=int, default=None,
                        help="decode budget, default 32 for hf and 128 for ours")
    parser.add_argument("--no-predictions", action="store_true",
                        help="leave per item predictions out of the report")
    hf = parser.add_argument_group("hf backend")
    hf.add_argument("--hf-model", default=None,
                    help="HuggingFace model name or local path")
    hf.add_argument("--prompt-style", default="auto",
                    choices=["auto", "chat", "plain"])
    hf.add_argument("--dtype", default="auto")
    ours = parser.add_argument_group("ours backend")
    ours.add_argument("--ckpt", default=None, help="trainer checkpoint .pt")
    ours.add_argument("--tokenizer", default=None, help="tokenizer.json")
    ours.add_argument("--ours-mode", default="retrieval",
                      choices=["retrieval", "context"])
    ours.add_argument("--max-rounds", type=int, default=4)
    ours.add_argument("--chunk-words", type=int, default=60)
    args = parser.parse_args(argv)

    if args.max_new_tokens is None:
        args.max_new_tokens = 32 if args.backend == "hf" else 128

    predict_fn = build_predict_fn(args)
    keep = not args.no_predictions

    results = {}
    for suite in args.suites:
        if suite == "naturalized":
            results[suite] = run_naturalized_bench(
                predict_fn, n_items=args.n_items, seed=args.seed,
                keep_predictions=keep)
        elif suite == "heldout":
            results[suite] = run_heldout_bench(
                predict_fn, n_episodes=args.heldout_episodes,
                seed=args.heldout_seed, keep_predictions=keep)
        else:
            results[suite] = run_public_qa(
                predict_fn, dataset=suite, n_items=args.n_items,
                seed=args.seed, cache_dir=args.cache_dir,
                keep_predictions=keep)
        res = results[suite]
        print(f"{suite}: em {res['em']:.4f} contains {res['contains']:.4f} "
              f"(n {res['n']})")

    report = {
        "meta": {
            "backend": args.backend,
            "suites": args.suites,
            "seed": args.seed,
            "n_items": args.n_items,
            **getattr(predict_fn, "metadata", {}),
        },
        "results": results,
    }
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "public_bench_report.json"
    with open(path, "w") as fh:
        json.dump(report, fh, indent=2)
        fh.write("\n")
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
