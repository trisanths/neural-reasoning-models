"""Command line entry point for episode generation.

Example:

    uv run python -m src.worldgen.cli --episodes 2000 --seed 1234 \
        --out data/worlds.jsonl

Writes one JSON object per line following the SPEC.md episode schema, plus a
<out>.meta.json describing the run.
"""

import argparse
import json
import os

from src.worldgen.domains import DOMAIN_ORDER
from src.worldgen.engine import generate_episodes, validate_episode


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="python -m src.worldgen.cli",
        description="Generate synthetic world episodes as JSONL.",
    )
    parser.add_argument("--episodes", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--out", type=str, required=True)
    parser.add_argument("--domains", type=str, default=",".join(DOMAIN_ORDER),
                        help="comma separated domain names")
    parser.add_argument("--contradiction-rate", type=float, default=0.15)
    parser.add_argument("--filler-rate", type=float, default=0.25)
    parser.add_argument("--start-index", type=int, default=0,
                        help="index of the first episode id")
    parser.add_argument("--validate", action="store_true",
                        help="run the validator on every episode")
    args = parser.parse_args(argv)

    domains = [d.strip() for d in args.domains.split(",") if d.strip()]
    out_dir = os.path.dirname(os.path.abspath(args.out))
    os.makedirs(out_dir, exist_ok=True)

    counts = {d: 0 for d in domains}
    n_questions = 0
    with open(args.out, "w", encoding="utf-8") as fh:
        for episode in generate_episodes(
            args.seed, args.episodes, domains=domains,
            contradiction_rate=args.contradiction_rate,
            filler_rate=args.filler_rate, start_index=args.start_index,
        ):
            if args.validate:
                problems = validate_episode(episode)
                if problems:
                    raise SystemExit(
                        f"{episode['episode_id']} failed validation: {problems}")
            counts[episode["world"]["domain"]] += 1
            n_questions += len(episode["questions"])
            fh.write(json.dumps(episode) + "\n")

    meta = {
        "episodes": args.episodes,
        "seed": args.seed,
        "domains": domains,
        "contradiction_rate": args.contradiction_rate,
        "filler_rate": args.filler_rate,
        "start_index": args.start_index,
        "episodes_per_domain": counts,
        "total_questions": n_questions,
    }
    with open(args.out + ".meta.json", "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)
        fh.write("\n")

    print(f"wrote {args.episodes} episodes to {args.out}")
    print(f"questions total {n_questions}, per domain {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
