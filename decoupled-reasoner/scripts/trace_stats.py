"""Measure the retrieval trace protocol over freshly generated episodes.

For each question the planner either produces a verified plan, meaning every
derivation hop has a query whose supporting document ranks top-1 under the
oracle BM25 retriever, or drops the question. This script generates held-out
episodes (default start index matches the regime C held-out range so the
measurement never touches training indices) and reports:

  - fraction of derivation questions with all hops supported at top-1
  - drop rate over all questions
  - mean hops per rendered derivation question
  - per-domain breakdown

With --tokenizer it also renders every episode and reports tokens per episode.

Usage:

    uv run python -m scripts.trace_stats --episodes 300 --seed 20260824 \
        [--tokenizer ~/runs/tokenizer_v2/tokenizer_v2.json]
"""

import argparse
import json
import os
import time

from src.train.retrieval import plan_episode_traces, render_episode_retrieval
from src.worldgen.domains import DOMAIN_ORDER
from src.worldgen.engine import generate_episodes

HELDOUT_INDEX_BASE = 1_000_000_000


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m scripts.trace_stats")
    parser.add_argument("--episodes", type=int, default=300)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--start-index", type=int, default=HELDOUT_INDEX_BASE)
    parser.add_argument("--domains", default=",".join(DOMAIN_ORDER))
    parser.add_argument("--contradiction-rate", type=float, default=0.15)
    parser.add_argument("--filler-rate", type=float, default=0.25)
    parser.add_argument("--tokenizer", default=None)
    parser.add_argument("--max-doc-tokens", type=int, default=None)
    parser.add_argument("--json", action="store_true",
                        help="print the summary as one JSON object")
    args = parser.parse_args(argv)

    tok = None
    if args.tokenizer is not None:
        from src.train.tokenizer import load_tokenizer
        tok = load_tokenizer(os.path.expanduser(args.tokenizer))

    domains = [d.strip() for d in args.domains.split(",") if d.strip()]
    totals = {"questions": 0, "rendered": 0, "dropped": 0,
              "no_derivation": 0, "hops": 0}
    per_domain: dict[str, dict] = {}
    total_tokens = 0
    t0 = time.time()
    for episode in generate_episodes(
        args.seed, args.episodes, domains=domains,
        contradiction_rate=args.contradiction_rate,
        filler_rate=args.filler_rate, start_index=args.start_index,
    ):
        _, stats = plan_episode_traces(episode)
        domain = episode["world"]["domain"]
        bucket = per_domain.setdefault(domain, dict.fromkeys(totals, 0))
        for key in totals:
            totals[key] += stats[key]
            bucket[key] += stats[key]
        if tok is not None:
            total_tokens += len(render_episode_retrieval(
                episode, tok, max_doc_tokens=args.max_doc_tokens))
    elapsed = time.time() - t0

    def derived(stats: dict) -> dict:
        # Dropped questions always have a derivation, so the derivation
        # question count is questions minus zero-hop rendered ones.
        with_deriv = stats["questions"] - stats["no_derivation"]
        supported = stats["rendered"] - stats["no_derivation"]
        return {
            **stats,
            "derivation_questions": with_deriv,
            "all_hops_top1": round(supported / with_deriv, 4)
            if with_deriv else 1.0,
            "drop_rate": round(stats["dropped"] / stats["questions"], 4)
            if stats["questions"] else 0.0,
            "mean_hops": round(stats["hops"] / supported, 3)
            if supported else 0.0,
        }

    summary = {
        "episodes": args.episodes,
        "seed": args.seed,
        "start_index": args.start_index,
        "overall": derived(totals),
        "per_domain": {d: derived(s) for d, s in sorted(per_domain.items())},
        "seconds": round(elapsed, 2),
    }
    if tok is not None:
        summary["total_tokens"] = total_tokens
        summary["tokens_per_episode"] = round(total_tokens / args.episodes, 1)

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        o = summary["overall"]
        print(f"episodes {args.episodes} questions {o['questions']} "
              f"derivation_questions {o['derivation_questions']}")
        print(f"all_hops_top1 {o['all_hops_top1']:.4f} "
              f"drop_rate {o['drop_rate']:.4f} mean_hops {o['mean_hops']:.3f} "
              f"no_derivation {o['no_derivation']}")
        for d, s in sorted(per_domain.items()):
            ds = derived(s)
            print(f"  {d}: q {ds['questions']} top1 {ds['all_hops_top1']:.4f} "
                  f"drop {ds['drop_rate']:.4f} hops {ds['mean_hops']:.3f}")
        if tok is not None:
            print(f"tokens_per_episode {summary['tokens_per_episode']}")
        print(f"seconds {summary['seconds']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
