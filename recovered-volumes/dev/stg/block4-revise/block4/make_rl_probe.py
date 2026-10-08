"""Write a one-step probe copy of an RL config.

The block-4 RL lanes run 256 rollouts per optimizer step, which is eight
times the width that was measured on the L40S. Rather than discover an
out-of-memory failure hours into a 24 hour block, resume4.sh runs one real
optimizer step at the full shape first and falls back to the narrow config if
that step dies. This script writes the probe config: identical to the real
one everywhere that touches memory, with the periodic work switched off so
the probe costs a step and not an eval sweep.

  uv run python make_rl_probe.py --base configs/rl-350m-block.yaml \
      --out /home/ec2-user/runs/.rlprobe-x/config.yaml

Only max_steps, eval_every, sample_every, and ckpt_every change. group_size,
prompts_per_step, micro_batch_size, and every env field are copied through
untouched, because those are what the probe exists to test.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

MEMORY_KEYS = ("group_size", "prompts_per_step", "micro_batch_size", "inner_epochs")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--steps", type=int, default=2)
    args = ap.parse_args()

    with open(args.base) as fh:
        cfg = yaml.safe_load(fh)

    cfg.setdefault("grpo", {})["max_steps"] = args.steps
    cfg["grpo"]["warmup_steps"] = min(int(cfg["grpo"].get("warmup_steps", 0)), args.steps)
    run = cfg.setdefault("run", {})
    run["eval_every"] = 0
    run["sample_every"] = 0
    run["ckpt_every"] = 0
    run["max_iteration_factor"] = 40

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as fh:
        yaml.safe_dump(cfg, fh, sort_keys=True)
    shape = ", ".join(f"{k} {cfg['grpo'][k]}" for k in MEMORY_KEYS if k in cfg["grpo"])
    rollouts = cfg["grpo"]["group_size"] * cfg["grpo"]["prompts_per_step"]
    print(f"wrote {out}: {args.steps} step probe of {args.base}, {shape}, "
          f"{rollouts} rollouts per step, max_len {cfg['env']['max_len']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
