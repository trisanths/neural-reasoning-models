"""Score the loss masking arms: knowledge probes, naturalized reading, and
held out language modelling loss.

Three measures, because the first two answer different halves of the
question and the third keeps the second honest.

  probes        src/evals/probes.py, four way multiple choice over real
                world facts, chance 0.25. This is the memorization we are
                trying to suppress, so lower is the goal.
  naturalized   src/evals/naturalized.py through the plain prose
                elicitation scripts/eval_battery.py uses for models trained
                on raw natural text. This is the language competence corpus
                scrubbing destroyed, so higher is the goal.
  heldout loss  mean cross entropy over natural text from parquet files no
                arm trained on, every token weighted one in every arm. The
                naturalized suite is a few hundred greedy decodes and moves
                in visible steps; this is millions of tokens and moves in
                thousandths, so it says whether an arm reads worse when the
                suite is too blunt to tell.

Usage:

    uv run python -m scripts.lossmask_eval \
        --runs ~/runs/lm-a ~/runs/lm-b ~/runs/lm-c ~/runs/lm-d \
        --tokenizer ~/data/tokenizer_v2.json \
        --heldout ~/data/lossmask/heldout --out ~/results/lossmask
"""

import argparse
import json
import math
import time
from pathlib import Path

import torch


def resolve_checkpoint(path: str) -> str:
    p = Path(path)
    if p.is_file():
        return str(p)
    ckpts = sorted(p.glob("ckpt-*.pt"))
    if ckpts:
        return str(ckpts[-1])
    latest = p / "latest.pt"
    if latest.is_file():
        return str(latest)
    raise FileNotFoundError(f"no checkpoint under {p}")


def heldout_loss(model, shard_dir: str, device: str, seq_len: int,
                 batch_size: int, n_batches: int, seed: int) -> dict:
    """Uniform mean cross entropy over held out natural text.

    Every arm is scored with the same offsets under the same seed, and with
    every weight at one whatever the arm trained with, so the number is one
    yardstick rather than four.
    """
    from src.train.data import BatchLoader, ShardReader

    from contextlib import nullcontext

    loader = BatchLoader(ShardReader(shard_dir), batch_size, seq_len, seed=seed)
    autocast = (torch.autocast(device_type="cuda", dtype=torch.bfloat16)
                if device.startswith("cuda") else nullcontext())
    total = 0.0
    tokens = 0
    model.eval()
    for _ in range(n_batches):
        inputs, targets = loader.next_batch()
        inputs = inputs.to(device)
        targets = targets.to(device)
        with torch.no_grad(), autocast:
            logits, _ = model(inputs)
            loss = torch.nn.functional.cross_entropy(
                logits.float().view(-1, logits.shape[-1]), targets.reshape(-1),
                reduction="sum")
        total += float(loss)
        tokens += int(targets.numel())
    mean = total / max(1, tokens)
    return {"loss": round(mean, 5), "perplexity": round(math.exp(mean), 4),
            "tokens": tokens}


def evaluate(run: str, tokenizer, args) -> dict:
    from src.evals.interactive import make_model_step_fn
    from src.evals.mc import load_checkpoint_model
    from src.evals.probes import run_probes

    from scripts.eval_battery import make_prose_predict_fn, score_naturalized

    ckpt = resolve_checkpoint(run)
    model, state = load_checkpoint_model(ckpt, args.device)
    cfg = state["config"]
    started = time.time()

    probes = run_probes(model, tokenizer, args.device)
    step_fn = make_model_step_fn(model, args.device)
    nat = score_naturalized(
        args.nat_items,
        make_prose_predict_fn(step_fn, tokenizer, args.nat_max_new))
    held = heldout_loss(model, args.heldout, args.device,
                        int(cfg["model"]["max_seq_len"]), args.heldout_batch,
                        args.heldout_batches, args.heldout_seed)

    del model
    if args.device.startswith("cuda"):
        torch.cuda.empty_cache()
    return {
        "run": str(run),
        "checkpoint": ckpt,
        "step": int(state.get("step", -1)),
        "lossmask": cfg.get("lossmask"),
        "train_tokens": int(state.get("step", 0)) *
        int(cfg["train"]["global_batch_size"]) *
        int(cfg["model"]["max_seq_len"]),
        "probe_accuracy": round(probes["accuracy"], 4),
        "probe_chance": probes["chance"],
        "probe_n": probes.get("n", probes.get("n_probes")),
        "probe_leakage_flag": probes.get("leakage_flag"),
        "naturalized_em": nat["em"],
        "naturalized_contains": nat["contains"],
        "naturalized_n": nat["n"],
        "heldout": held,
        "eval_seconds": round(time.time() - started, 1),
        "probes_detail": probes,
        "naturalized_detail": nat,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m scripts.lossmask_eval")
    parser.add_argument("--runs", nargs="+", required=True)
    parser.add_argument("--tokenizer", required=True)
    parser.add_argument("--heldout", required=True,
                        help="shard dir of natural text no arm trained on")
    parser.add_argument("--out", required=True)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--nat-n", type=int, default=0,
                        help="0 runs the whole suite")
    parser.add_argument("--nat-max-new", type=int, default=24)
    parser.add_argument("--heldout-batch", type=int, default=8)
    parser.add_argument("--heldout-batches", type=int, default=64)
    parser.add_argument("--heldout-seed", type=int, default=777)
    args = parser.parse_args(argv)

    from src.evals.naturalized import load_suite
    from src.train.tokenizer import load_tokenizer

    from scripts.eval_battery import stratified_subset

    tokenizer = load_tokenizer(args.tokenizer)
    suite = load_suite()
    args.nat_items = (suite["items"] if args.nat_n <= 0
                      else stratified_subset(suite["items"], args.nat_n))
    print(f"naturalized suite {suite['metadata']['version']}, "
          f"{len(args.nat_items)} items")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    results = []
    for run in args.runs:
        row = evaluate(run, tokenizer, args)
        results.append(row)
        with open(out / f"{Path(run).name}.json", "w") as fh:
            json.dump(row, fh, indent=2)
        print(f"{Path(run).name}: probe {row['probe_accuracy']:.4f} "
              f"(chance {row['probe_chance']:.2f})  "
              f"nat_contains {row['naturalized_contains']:.4f}  "
              f"nat_em {row['naturalized_em']:.4f}  "
              f"heldout_loss {row['heldout']['loss']:.4f}", flush=True)

    with open(out / "results.json", "w") as fh:
        json.dump({"results": results}, fh, indent=2)
    print(f"wrote {out / 'results.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
