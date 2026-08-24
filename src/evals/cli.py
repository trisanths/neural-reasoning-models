"""Command line entry point for the evaluation suites.

Example:

    uv run python -m src.evals.cli --ckpt runs/smoke-001/latest.pt \
        --tokenizer runs/smoke-001/tokenizer.json --out runs/smoke-001 \
        --heldout-episodes 40 --heldout-seed 999

Runs the knowledge probes and the held out worlds suite against the
checkpoint and writes eval_report.json and eval_report.md to the output
directory.
"""

import argparse

import torch

from src.evals.heldout import run_heldout
from src.evals.mc import load_checkpoint_model
from src.evals.probes import run_probes
from src.evals.report import build_report, write_report
from src.train.tokenizer import load_tokenizer
from src.worldgen.engine import generate_episodes


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m src.evals.cli")
    parser.add_argument("--ckpt", required=True, help="trainer checkpoint .pt")
    parser.add_argument("--tokenizer", required=True, help="tokenizer.json")
    parser.add_argument("--out", required=True, help="report output directory")
    parser.add_argument("--heldout-episodes", type=int, default=40)
    parser.add_argument("--heldout-seed", type=int, default=999)
    parser.add_argument("--device", default=None, help="cuda or cpu, default auto")
    args = parser.parse_args(argv)

    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    model, state = load_checkpoint_model(args.ckpt, device)
    tokenizer = load_tokenizer(args.tokenizer)

    episodes = list(generate_episodes(args.heldout_seed, args.heldout_episodes))
    heldout = run_heldout(model, tokenizer, episodes, device,
                          seed=args.heldout_seed)
    probes = run_probes(model, tokenizer, device)

    meta = {
        "checkpoint": args.ckpt,
        "step": int(state.get("step", -1)),
        "heldout_seed": args.heldout_seed,
        "device": device,
    }
    json_path, md_path = write_report(build_report(heldout, probes, meta), args.out)
    print(f"heldout accuracy {heldout['accuracy']:.4f} "
          f"(chance {heldout['chance']:.4f}, n {heldout['n_questions']})")
    print(f"probe accuracy {probes['accuracy']:.4f} "
          f"(chance {probes['chance']:.2f}, leakage flag {probes['leakage_flag']})")
    print(f"wrote {json_path} and {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
