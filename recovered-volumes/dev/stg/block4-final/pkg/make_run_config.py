"""Write one per-run training config derived from a base yaml.

The trainer takes seed, micro batch, accumulation, checkpoint interval, and
the compile switch from the config file, not from CLI flags, so every run
gets its own generated config. The global batch (batch_size *
grad_accum_steps) must stay identical to the base config so all runs see the
same optimizer step size; pass --allow-global-change only for throwaway
tests.

Recurrent configs carry a model.recurrent block. Two extra dials reach into
it: --loops sets the default depth, and --loop-sampling sets or clears the
per-step depth draw. Clearing it ("off") is what turns the sampled-depth
lane into a fixed-depth one, which is the only way two looped lanes differ
at train time; with sampling on, model.recurrent.loops only affects eval and
generate, so two sampled lanes with different loops train identically.

Unless --no-params is passed the generated config is instantiated on the
meta device and the parameter count and effective depth are printed. That
costs no memory and it is the preflight that catches a config which cannot
build a model at all.

Run under uv from the repo directory (needs pyyaml and torch):
  uv run python make_run_config.py --base configs/350m.yaml \
      --out /home/ec2-user/runs/killtest-a-101/config.yaml --seed 101 \
      --micro-batch 8 --grad-accum 8 --ckpt-interval 1000 --compile 1
"""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml


def parse_loop_sampling(raw: str):
    """"off" clears the draw; "lo,hi" sets it."""
    if raw.strip().lower() in ("off", "none", "null"):
        return None
    parts = [p for p in raw.replace(":", ",").split(",") if p.strip()]
    if len(parts) != 2:
        raise SystemExit(
            f"--loop-sampling wants 'off' or 'lo,hi', got {raw!r}"
        )
    lo, hi = int(parts[0]), int(parts[1])
    if lo < 1 or hi < lo:
        raise SystemExit(f"--loop-sampling needs 1 <= lo <= hi, got {lo},{hi}")
    return [lo, hi]


def report_params(cfg: dict) -> None:
    """Instantiate on the meta device and print the shape of the model.

    This script is run from the repo directory but lives outside it, in the
    block-4 package, so python's sys.path[0] is the package and not the repo.
    Put the working directory in front so `src` imports resolve.
    """
    import os
    import sys

    cwd = os.getcwd()
    if os.path.isdir(os.path.join(cwd, "src", "train")):
        if cwd not in sys.path:
            sys.path.insert(0, cwd)
    else:
        raise SystemExit(
            f"--no-params was not passed but {cwd} is not the repo root "
            "(no src/train); run this from the repo directory"
        )

    import torch

    from src.train.model import ModelConfig, TransformerLM

    with torch.device("meta"):
        model = TransformerLM(ModelConfig(**cfg["model"]))
    total = model.num_params(non_embedding=False)
    non_emb = model.num_params()
    line = f"  params {total:,} total, {non_emb:,} non embedding"
    if model.cfg.recurrent is not None:
        info = model.describe()
        rec = model.cfg.recurrent
        line += (
            f"; recurrence on: {model.cfg.n_layers} unique layers"
            f" (prelude {rec.prelude_layers}, core {rec.core_layers},"
            f" coda {rec.coda_layers}), loops {info['loops']},"
            f" effective depth {info['effective_depth']},"
            f" loop_slots {rec.loop_slots},"
            f" train_loop_sampling {rec.train_loop_sampling}"
        )
    print(line)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--micro-batch", type=int, default=None)
    ap.add_argument("--grad-accum", type=int, default=None)
    ap.add_argument("--ckpt-interval", type=int, default=None)
    ap.add_argument("--compile", type=int, default=None, help="1 or 0")
    ap.add_argument("--max-steps", type=int, default=None)
    ap.add_argument("--loops", type=int, default=None,
                    help="model.recurrent.loops, needs a recurrent base")
    ap.add_argument("--loop-sampling", default=None,
                    help="'off' or 'lo,hi' for model.recurrent.train_loop_sampling")
    ap.add_argument("--allow-global-change", action="store_true")
    ap.add_argument("--no-params", action="store_true",
                    help="skip the meta-device instantiation and its report")
    args = ap.parse_args()

    with open(args.base) as fh:
        cfg = yaml.safe_load(fh)

    base_global = cfg["train"]["batch_size"] * cfg["train"]["grad_accum_steps"]
    cfg["train"]["seed"] = args.seed
    if args.micro_batch is not None:
        cfg["train"]["batch_size"] = args.micro_batch
    if args.grad_accum is not None:
        cfg["train"]["grad_accum_steps"] = args.grad_accum
    if args.ckpt_interval is not None:
        cfg["train"]["ckpt_interval"] = args.ckpt_interval
    if args.compile is not None:
        cfg["train"]["compile"] = bool(args.compile)
    if args.max_steps is not None:
        cfg["schedule"]["max_steps"] = args.max_steps

    if args.loops is not None or args.loop_sampling is not None:
        rec = cfg["model"].get("recurrent")
        if not rec:
            raise SystemExit(
                f"{args.base} has no model.recurrent block; --loops and "
                "--loop-sampling need a recurrent config"
            )
        if args.loops is not None:
            if args.loops < 1:
                raise SystemExit("--loops must be at least 1")
            rec["loops"] = args.loops
        if args.loop_sampling is not None:
            rec["train_loop_sampling"] = parse_loop_sampling(args.loop_sampling)
        # loop_slots sizes the loop embedding table. Left implicit it follows
        # max(loops, sampling high), which would silently change the
        # parameter count between a sampled lane and a fixed-depth one. Pin
        # it to the base config's span so the lanes stay parameter matched.
        if rec.get("loop_slots") is None:
            base_rec = yaml.safe_load(open(args.base))["model"]["recurrent"]
            span = base_rec.get("train_loop_sampling")
            base_slots = max(int(base_rec.get("loops", 1)),
                             int(span[1]) if span else 1)
            rec["loop_slots"] = base_slots

    new_global = cfg["train"]["batch_size"] * cfg["train"]["grad_accum_steps"]
    if new_global != base_global and not args.allow_global_change:
        raise SystemExit(
            f"global batch changed: base {base_global}, new {new_global}; "
            "pass --allow-global-change if that is intended"
        )

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as fh:
        yaml.safe_dump(cfg, fh, sort_keys=True)
    tokens = new_global * cfg["model"]["max_seq_len"] * cfg["schedule"]["max_steps"]
    print(
        f"wrote {out}: seed {cfg['train']['seed']}, "
        f"micro {cfg['train']['batch_size']} x accum {cfg['train']['grad_accum_steps']} "
        f"= global {new_global} seqs, max_steps {cfg['schedule']['max_steps']}, "
        f"budget {tokens:,} tokens, compile {cfg['train'].get('compile', False)}, "
        f"ckpt_interval {cfg['train']['ckpt_interval']}"
    )
    if not args.no_params:
        report_params(cfg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
