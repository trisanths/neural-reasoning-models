"""Write one per-run training config derived from a base yaml.

The trainer takes seed, micro batch, accumulation, checkpoint interval, and
the compile switch from the config file, not from CLI flags, so every run
gets its own generated config. The global batch (batch_size *
grad_accum_steps) must stay identical to the base config so all runs see the
same optimizer step size; pass --allow-global-change only for throwaway
tests.

Block 4 adds the looped-depth dial. When the base config carries a
model.recurrent block, --loops, --loop-sampling, --backprop-last-k, and
--grad-checkpoint override its fields, and the printed line reports the
effective depth (prelude + core * loops + coda) at the default loop count and
at both ends of the sampling range. Passing any of those flags against a base
config with no recurrent block is an error rather than a silent no-op.

Run under uv from the repo directory (needs pyyaml):
  uv run python make_run_config.py --base configs/350m.yaml \
      --out /home/ec2-user/runs/killtest-a-101/config.yaml --seed 101 \
      --micro-batch 8 --grad-accum 8 --ckpt-interval 1000 --compile 1

  uv run python make_run_config.py --base configs/350m-loop.yaml \
      --out /home/ec2-user/runs/curve-350me3loop-711/config.yaml --seed 711 \
      --micro-batch 8 --grad-accum 8 --ckpt-interval 1050 --compile 1 \
      --max-steps 26700 --loops 4 --loop-sampling 1,8 --backprop-last-k 2
"""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml


def parse_range(text: str):
    """'1,8' -> [1, 8]; 'none' -> None."""
    if text.lower() in ("none", "null", "off"):
        return None
    parts = [p for p in text.replace(":", ",").split(",") if p.strip()]
    if len(parts) != 2:
        raise SystemExit(f"--loop-sampling wants 'lo,hi' or 'none', got {text!r}")
    lo, hi = int(parts[0]), int(parts[1])
    if lo < 1 or hi < lo:
        raise SystemExit(f"--loop-sampling range must satisfy 1 <= lo <= hi, got {text!r}")
    return [lo, hi]


def parse_opt_int(text: str):
    """'2' -> 2; 'none' -> None."""
    if text.lower() in ("none", "null", "off"):
        return None
    return int(text)


def effective_depth(rec: dict, loops: int) -> int:
    return (int(rec["prelude_layers"]) + int(rec["core_layers"]) * loops
            + int(rec["coda_layers"]))


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
    ap.add_argument("--loops", type=int, default=None,
                    help="default loop count for a recurrent base config")
    ap.add_argument("--loop-sampling", default=None,
                    help="'lo,hi' to sample the loop count per step, or 'none'")
    ap.add_argument("--backprop-last-k", default=None,
                    help="run all but the last K iterations under no_grad, or 'none'")
    ap.add_argument("--grad-checkpoint", type=int, default=None, help="1 or 0")
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

    rec_flags = (args.loops, args.loop_sampling, args.backprop_last_k,
                 args.grad_checkpoint)
    rec = cfg.get("model", {}).get("recurrent")
    if any(f is not None for f in rec_flags) and not rec:
        raise SystemExit(
            f"recurrent flags given but {args.base} has no model.recurrent block"
        )
    if rec:
        if args.loops is not None:
            if args.loops < 1:
                raise SystemExit("--loops must be at least 1")
            rec["loops"] = args.loops
        if args.loop_sampling is not None:
            rec["train_loop_sampling"] = parse_range(args.loop_sampling)
        if args.backprop_last_k is not None:
            rec["backprop_last_k"] = parse_opt_int(args.backprop_last_k)
        if args.grad_checkpoint is not None:
            rec["grad_checkpoint"] = bool(args.grad_checkpoint)
        unique = (int(rec["prelude_layers"]) + int(rec["core_layers"])
                  + int(rec["coda_layers"]))
        if unique != int(cfg["model"]["n_layers"]):
            raise SystemExit(
                f"prelude+core+coda is {unique} but model.n_layers is "
                f"{cfg['model']['n_layers']}"
            )

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
    line = (
        f"wrote {out}: seed {cfg['train']['seed']}, "
        f"micro {cfg['train']['batch_size']} x accum {cfg['train']['grad_accum_steps']} "
        f"= global {new_global} seqs, max_steps {cfg['schedule']['max_steps']}, "
        f"budget {tokens:,} tokens, compile {cfg['train'].get('compile', False)}, "
        f"ckpt_interval {cfg['train']['ckpt_interval']}"
    )
    if rec:
        loops = int(rec["loops"])
        samp = rec.get("train_loop_sampling")
        depth = f"depth {effective_depth(rec, loops)} at {loops} loops"
        if samp:
            depth += (f", sampled {samp[0]}-{samp[1]} loops "
                      f"= depth {effective_depth(rec, samp[0])}-"
                      f"{effective_depth(rec, samp[1])}")
        line += (f", recurrent {rec['prelude_layers']}+{rec['core_layers']}x"
                 f"{loops}+{rec['coda_layers']}, {depth}, "
                 f"backprop_last_k {rec.get('backprop_last_k')}, "
                 f"grad_checkpoint {rec.get('grad_checkpoint')}")
    print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
