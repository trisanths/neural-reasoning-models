"""Run the latent-retrieval conditions and write one JSON per condition.

    python scripts/latentret_run.py --out results/latentret --steps 3000

The conditions, and what each one is there to rule out:

    latent        the mechanism. Query projected from the recurrent state.
    decoded       the same run with the query built from the model's own output
                  distribution instead of its hidden state. This is the "decode
                  a text query" arm, made generous: real decoding takes an
                  argmax and passes no gradient, the soft top-k here does.
    question      the query is the question tokens through the document
                  encoder. No recurrent state at all: the preprocessing
                  retriever every earlier result in this project used.
    uniform       no query. The injection still runs, over a flat distribution
                  across all six pages. Separates "retrieval found the page"
                  from "cross-attending to a pile of pages helps".
    latent_notask the retrieval term removed (alpha = 0), so the gate and the
                  query are driven by the task loss alone. If retrieval only
                  works when it is directly supervised, that is worth knowing
                  and is the honest way to find out.
    latent_easy   distractors keep their own invented name instead of the gold
                  system's, so the name in the question picks out exactly one
                  page. The gap to the hard run is what the name was worth.
    latent_lm     generation instead of selection: the answer has to come out
                  of the vocabulary head with no copy path. The answers are
                  invented words, so this is the arm that says whether a
                  failure to answer is a failure to retrieve or a failure to
                  say what was retrieved.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import sys

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.latentret.loss import LossWeights          # noqa: E402
from src.latentret.train import RunConfig, train_one  # noqa: E402
from src.latentret.vocab import get_vocab           # noqa: E402

CONDITIONS = {
    "latent": dict(query_mode="latent"),
    "decoded": dict(query_mode="decoded"),
    "question": dict(query_mode="question"),
    "uniform": dict(query_mode="none"),
    "latent_notask": dict(query_mode="latent", weights=LossWeights(alpha=0.0)),
    "latent_easy": dict(query_mode="latent", hard=False),
    "latent_lm": dict(query_mode="latent", readout="lm"),
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/latentret")
    ap.add_argument("--steps", type=int, default=3000)
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--batch-size", type=int, default=48)
    ap.add_argument("--gamma", type=float, default=None,
                    help="retrieval budget weight, overrides the condition default")
    ap.add_argument("--alpha", type=float, default=None)
    ap.add_argument("--d-model", type=int, default=None)
    ap.add_argument("--core", type=int, default=None)
    ap.add_argument("--loops", type=int, default=None)
    ap.add_argument("--lr", type=float, default=None)
    ap.add_argument("--readout", default=None, choices=["lm", "copy", "both"])
    ap.add_argument("--tag", default="")
    ap.add_argument("--conditions", default=",".join(CONDITIONS))
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    print(f"vocab {len(get_vocab())} types, device {args.device}", flush=True)
    for name in args.conditions.split(","):
        name = name.strip()
        if not name:
            continue
        overrides = dict(CONDITIONS[name])
        if args.gamma is not None or args.alpha is not None:
            w = overrides.get("weights", LossWeights())
            w = LossWeights(alpha=args.alpha if args.alpha is not None else w.alpha,
                            beta=w.beta,
                            gamma=args.gamma if args.gamma is not None else w.gamma,
                            lam_prior=w.lam_prior)
            overrides["weights"] = w
        for flag, field in (("d_model", "d_model"), ("core", "core"),
                            ("loops", "loops"), ("lr", "lr"),
                            ("readout", "readout")):
            value = getattr(args, flag)
            if value is not None:
                overrides[field] = value
        cfg = RunConfig(name=name, steps=args.steps, seed=args.seed,
                        batch_size=args.batch_size, **overrides)
        path = os.path.join(args.out, f"{name}{args.tag}_seed{args.seed}.json")
        if os.path.exists(path):
            print(f"skip {name}, {path} exists", flush=True)
            continue
        result = train_one(cfg, args.device)
        with open(path, "w") as fh:
            json.dump(result, fh, indent=2, default=lambda o:
                      dataclasses.asdict(o) if dataclasses.is_dataclass(o) else str(o))
        f = result["final"]
        print(f"DONE {name}: acc {f['acc_final']:.3f} hit_any {f['hit_any']:.3f} "
              f"gate_auc {f['gate_auc']:.3f} -> {path}", flush=True)


if __name__ == "__main__":
    main()
