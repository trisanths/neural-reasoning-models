"""Dry-run check: build every block-4 lane's model and report its shape."""
import sys

import torch
import yaml

from src.train.model import ModelConfig, TransformerLM


def report(tag, path):
    cfg = yaml.safe_load(open(path))["model"]
    m = TransformerLM(ModelConfig(**cfg))
    total = sum(p.numel() for p in m.parameters())
    rec = cfg.get("recurrent")
    loops = rec["loops"] if rec else 1
    depth = (cfg["n_layers"] if not rec else
             rec["prelude_layers"] + rec["core_layers"] * loops + rec["coda_layers"])
    print(f"{tag:26s} total {total:,}  "
          f"d_model {cfg['d_model']}  unique_layers {cfg['n_layers']}  "
          f"loops {loops}  effective_depth {depth}")
    if rec:
        lo, hi = rec["train_loop_sampling"]
        for L in sorted({lo, loops, hi}):
            with torch.no_grad():
                x = torch.randint(0, cfg["vocab_size"], (1, 16))
                out = m(x, loops=L)
            logits = out[0] if isinstance(out, tuple) else out
            d = rec["prelude_layers"] + rec["core_layers"] * L + rec["coda_layers"]
            print(f"    forward at loops={L:2d} depth={d:3d} "
                  f"logits {tuple(logits.shape)}")
        print(f"    backprop_last_k {rec['backprop_last_k']}  "
              f"grad_checkpoint {rec['grad_checkpoint']}  "
              f"sampling [{lo},{hi}]")
    del m
    return total


base = report("350m standard (control)", "configs/350m.yaml")
a = report("711 looped, default 4", sys.argv[1])
b = report("712 looped, default 2", sys.argv[2])
report("721 700m standard", sys.argv[3])
# 711 and 712 differ by exactly the loop conditioning table, which is sized by
# the top of the sampling range: 8 rows against 4, at 2 * d_model each, so
# 10,240 parameters or 0.003 percent. Everything else is shared.
print(f"711 minus 712: {a - b:,} parameters "
      f"(the loop_film table, {a - b} = 4 extra rows x 2 x 1280)")
print(f"711 vs standard 350m drift: {(a - base) / base:+.4%}")
print(f"712 vs standard 350m drift: {(b - base) / base:+.4%}")
assert abs(a - b) / a < 0.001
assert abs(a - base) / base < 0.01
assert abs(b - base) / base < 0.01
print("DRY_MODELS_OK")
