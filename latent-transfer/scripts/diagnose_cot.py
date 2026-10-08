"""Learnability probe: can a model learn the task with explicit chain-of-thought?

Explicit CoT is the easiest form of the task -- every reasoning step is written
out, so each step is a single-hop lookup. If a model cannot learn this, it
cannot possibly do the same reasoning latently, and any latent result would be
measuring the wrong thing. Reports accuracy per epoch so the curve is visible.
"""

import argparse
import os
import sys

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.coconut import Coconut  # noqa: E402
from src.data import load  # noqa: E402
from src.tasks import get_tokenizer  # noqa: E402
from src.dataset import CurriculumConfig, iterate_batches  # noqa: E402
from src.engine import evaluate, get_device  # noqa: E402
from src.model import ModelConfig, TinyLM  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from train_baseline import PRESETS  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--preset", default="big")
    p.add_argument("--task", default="prosqa", choices=["prosqa", "compose"])
    p.add_argument("--data", default="data")
    p.add_argument("--n_train", type=int, default=16000)
    p.add_argument("--n_val", type=int, default=300)
    p.add_argument("--epochs", type=int, default=8)
    p.add_argument("--batch_size", type=int, default=32)
    p.add_argument("--lr", type=float, default=6e-4)
    p.add_argument("--stage", type=int, default=0, help="0=CoT, 99=full latent")
    p.add_argument("--seed", type=int, default=0)
    a = p.parse_args()

    torch.manual_seed(a.seed)
    dev = get_device()
    tok = get_tokenizer(a.task)
    train_ex = load(f"{a.data}/train.json")[: a.n_train]
    val_ex = load(f"{a.data}/val.json")[: a.n_val]
    cur = CurriculumConfig(max_latent_stage=5, c_thought=1, cot_only=(a.stage == 0))

    model = TinyLM(ModelConfig(vocab_size=len(tok), max_len=320, **PRESETS[a.preset])).to(dev)
    coco = Coconut(model)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=0.01, betas=(0.9, 0.95))
    total = (len(train_ex) // a.batch_size + 1) * a.epochs
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=a.lr, total_steps=total, pct_start=0.05)

    print(f"{a.preset} params={model.n_params() / 1e6:.2f}M stage={a.stage} "
          f"n_train={len(train_ex)} device={dev}", flush=True)
    step = 0
    for ep in range(a.epochs):
        model.train()
        run, cnt = 0.0, 0
        for batch in iterate_batches(train_ex, tok, a.stage, cur, a.batch_size, shuffle=True, seed=ep):
            loss, _, _ = coco(batch.to(dev))
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            sched.step()
            opt.zero_grad(set_to_none=True)
            run += loss.item()
            cnt += 1
            step += 1
        m = evaluate(coco, val_ex, tok, cur, dev, stage=a.stage)
        print(f"epoch {ep} loss {run / max(cnt, 1):.4f} "
              f"val exact={m['exact']:.3f} concept={m['concept']:.3f}", flush=True)


if __name__ == "__main__":
    main()
