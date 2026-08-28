"""Run the eight-level benchmark and the acquisition battery.

One model callable is scored through four presentations of the same problem,
and the result is printed per level and per condition. Nothing is pooled: the
whole point of the per level split is that a family sitting at zero stays
visible instead of being carried by a family that is not.

Three ways to supply the model.

  --fake reader   a scripted model that answers when the statements it needs
                  are in front of it. Oracle should land near one and closed
                  book near the majority baseline. This checks the harness.
  --fake parrot   a scripted model that always answers with the library's
                  most frequent number. It should score zero everywhere. This
                  checks the guard.
  --checkpoint    a trainer checkpoint plus --tokenizer, sampled.

Examples.

  python scripts/run_math_bench.py --fake reader --seeds 400:412 --out /tmp/b
  python scripts/run_math_bench.py --checkpoint runs/x/final.pt \\
      --tokenizer data/tokenizer_v2.json --seeds 400:404 --out /tmp/b
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mathgen.battery import (battery_report, probes_for, run_battery,
                                 scripted_learner)
from src.mathgen.bench import (CONDITIONS, build_problem_set, score,
                               scripted_parrot, scripted_reader)
from src.mathgen.interface import LEVELS, load_universe, validate_universe


def parse_seeds(spec: str) -> list[int]:
    if ":" in spec:
        lo, hi = spec.split(":")
        return list(range(int(lo), int(hi)))
    return [int(t) for t in spec.split(",") if t]


def checkpoint_model(ckpt: str, tokenizer_path: str, temperature: float,
                     max_new_tokens: int, seed: int):
    """Adapt a trainer checkpoint to the plain prompt-in, text-out callable."""
    import numpy as np
    import torch

    from src.evals.interactive import make_checkpoint_step_fn
    from src.train.tokenizer import load_tokenizer

    device = "cuda" if torch.cuda.is_available() else "cpu"
    step_fn, model, _ = make_checkpoint_step_fn(ckpt, device)
    tok = load_tokenizer(tokenizer_path)
    max_len = model.cfg.max_seq_len
    rng = np.random.default_rng(seed)
    newline = tok.encode("\n")

    def generate(prompt: str) -> str:
        ids = tok.encode(prompt)[-(max_len - max_new_tokens - 1):]
        out: list[int] = []
        for _ in range(max_new_tokens):
            logits = step_fn(ids + out)
            if temperature <= 0:
                nxt = int(np.argmax(logits))
            else:
                z = logits.astype(np.float64) / temperature
                z -= z.max()
                p = np.exp(z)
                p /= p.sum()
                nxt = int(rng.choice(len(p), p=p))
            out.append(nxt)
            if newline and nxt == newline[-1] and len(out) > 1:
                break
        return tok.decode(out)

    return generate


def print_block(title: str, rows: dict) -> None:
    print(f"\n{title}")
    for name, entry in rows.items():
        bits = " ".join(
            f"{k} {v:.4f}" if isinstance(v, float) else f"{k} {v}"
            for k, v in entry.items() if not isinstance(v, dict))
        print(f"  {name:<28} {bits}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="400:404",
                    help="universe seeds, lo:hi or a comma list")
    ap.add_argument("--per-level", type=int, default=4)
    ap.add_argument("--levels", default=",".join(str(v) for v in LEVELS))
    ap.add_argument("--conditions", default=",".join(CONDITIONS))
    ap.add_argument("--universe-module", default=None,
                    help="module exposing build_universe, from the mathgen agent")
    ap.add_argument("--rag-k", type=int, default=4)
    ap.add_argument("--max-rounds", type=int, default=4)
    ap.add_argument("--fake", choices=["reader", "parrot", "learner"], default=None)
    ap.add_argument("--competence", type=float, default=1.0)
    ap.add_argument("--checkpoint", default=None)
    ap.add_argument("--tokenizer", default=None)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--max-new-tokens", type=int, default=24)
    ap.add_argument("--battery-seeds", default=None,
                    help="universe seeds for the battery, defaults to the first")
    ap.add_argument("--skip-battery", action="store_true")
    ap.add_argument("--require-valid", action="store_true",
                    help="stop when the universe fails the contract check")
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    seeds = parse_seeds(args.seeds)
    levels = tuple(int(v) for v in args.levels.split(","))
    conditions = tuple(c for c in args.conditions.split(",") if c)

    probe = load_universe(seeds[0], module=args.universe_module)
    report = validate_universe(probe, levels=levels)
    print(f"universe {probe.universe_id} contract ok {report['ok']}")
    for line in report["problems"]:
        print(f"  contract: {line}")
    if args.require_valid and not report["ok"]:
        raise SystemExit("universe does not satisfy the contract")

    ps = build_problem_set(seeds, per_level=args.per_level, levels=levels,
                           universe_module=args.universe_module,
                           rng_seed=args.seed)
    print(f"universes {len(ps.universes)} problems {len(ps.problems)} "
          f"levels {levels}")
    print_block("discards per level", ps.discards)
    print_block("majority baseline per level", ps.baselines)

    if args.fake == "reader":
        model = scripted_reader(ps, competence=args.competence, seed=args.seed)
        model_name = f"scripted_reader(c={args.competence})"
    elif args.fake == "parrot":
        model = scripted_parrot(ps, seed=args.seed)
        model_name = "scripted_parrot"
    elif args.fake == "learner":
        model = scripted_learner(next(iter(ps.universes.values())),
                                 competence=args.competence, seed=args.seed)
        model_name = "scripted_learner"
    elif args.checkpoint:
        if not args.tokenizer:
            raise SystemExit("--checkpoint needs --tokenizer")
        model = checkpoint_model(args.checkpoint, args.tokenizer,
                                 args.temperature, args.max_new_tokens,
                                 args.seed)
        model_name = args.checkpoint
    else:
        raise SystemExit("pass --fake or --checkpoint")

    record: list = []
    result = score(model, ps, conditions=conditions, rag_k=args.rag_k,
                   max_rounds=args.max_rounds, record=record)

    for cond in conditions:
        print_block(f"accuracy per level, condition {cond}",
                    result["per_level"][cond])
    for cond in conditions:
        print_block(f"accuracy per target chapter, condition {cond}",
                    result["per_chapter"][cond])
    if "acquisition" in conditions:
        rates = result["acquisition_search_rate"]
        print("\nfraction of agent rollouts that issued a query")
        for name, rate in rates.items():
            print(f"  {name:<28} {rate:.4f}")

    battery: dict = {}
    if not args.skip_battery:
        bseeds = parse_seeds(args.battery_seeds) if args.battery_seeds else seeds[:1]
        rows = []
        for s in bseeds:
            u = load_universe(s, module=args.universe_module)
            taker = model
            if args.fake == "reader" and probes_for(u):
                # The reader answers from text in the prompt, and the battery
                # hides the text, so it would only ever score zero. The
                # learner is the taker that exercises the grading, and it
                # exists only for universes that have probes.
                taker = scripted_learner(u, competence=args.competence,
                                         seed=args.seed)
            rows.extend(run_battery(taker, u, seed=args.seed + s))
        battery = battery_report(rows)
        if not rows:
            print("\nacquisition battery: no probes for this universe, so no "
                  "battery was run. A probe fits a reconstructed rule back "
                  "onto a reference implementation and is written per family.")
        else:
            print_block("acquisition battery per test", battery["per_test"])
            print(f"  acquired per item: {json.dumps(battery['acquired'])}")

    payload = {
        "model": model_name,
        "seeds": seeds,
        "levels": list(levels),
        "conditions": list(conditions),
        "universe_module": args.universe_module or "src.mathgen.refuniverse",
        "n_problems": len(ps.problems),
        "contract": report,
        "results": result,
        "battery": battery,
    }
    with open(os.path.join(args.out, "math_bench.json"), "w") as fh:
        json.dump(payload, fh, indent=2)
    with open(os.path.join(args.out, "math_bench_samples.jsonl"), "w") as fh:
        for row in record:
            fh.write(json.dumps(row) + "\n")

    cb = result["per_level"].get("closed_book", {})
    if cb:
        worst = " ".join(f"{k}:{v['accuracy']:.3f}" for k, v in cb.items())
        print(f"\nCLOSED_BOOK {worst}")
        base = " ".join(f"{k}:{v['majority']:.3f}" for k, v in ps.baselines.items())
        print(f"MAJORITY    {base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
