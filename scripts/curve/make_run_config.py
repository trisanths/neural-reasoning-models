"""Write one per-run training config derived from a base yaml.

The trainer takes seed, micro batch, accumulation, checkpoint interval, and
the compile switch from the config file, not from CLI flags, so every run
gets its own generated config. The global batch (batch_size *
grad_accum_steps) must stay identical to the base config so all six runs see
the same optimizer step size; pass --allow-global-change only for throwaway
tests.

Run under uv from the repo directory (needs pyyaml):
  uv run python make_run_config.py --base configs/350m.yaml \
      --out /home/ec2-user/runs/killtest-a-101/config.yaml --seed 101 \
      --micro-batch 8 --grad-accum 8 --ckpt-interval 1000 --compile 1
"""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml


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
    ap.add_argument("--allow-global-change", action="store_true")
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
