"""Stage 0: train a single model standalone (Coconut / CoT / no-CoT).

These runs provide the floor and ceiling that the cross-model pipeline is
measured against, and produce the frozen backbones the pipeline reuses.
"""

import argparse
import json
import os
import sys

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.coconut import Coconut  # noqa: E402
from src.data import load  # noqa: E402
from src.tasks import get_tokenizer  # noqa: E402
from src.dataset import CurriculumConfig  # noqa: E402
from src.engine import (  # noqa: E402
    FINAL_STAGE,
    TrainConfig,
    evaluate,
    get_device,
    train_curriculum,
)
from src.model import ModelConfig, TinyLM  # noqa: E402

PRESETS = {
    # Deliberately depth-starved: fewer layers than the task has hops, so it
    # cannot chain the lookups regardless of how long it trains.
    "xs": dict(d_model=64, n_layers=2, n_heads=4),
    "small": dict(d_model=128, n_layers=4, n_heads=4),
    "mid": dict(d_model=256, n_layers=8, n_heads=8),
    "big": dict(d_model=256, n_layers=10, n_heads=8),
    "xl": dict(d_model=384, n_layers=12, n_heads=6),
}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--preset", default="small", choices=list(PRESETS))
    p.add_argument("--task", default="prosqa", choices=["prosqa", "compose"])
    p.add_argument("--mode", default="coconut", choices=["coconut", "cot", "nocot"])
    p.add_argument("--data", default="data")
    p.add_argument("--out", required=True)
    p.add_argument("--n_train", type=int, default=12000)
    p.add_argument("--epochs_per_stage", type=int, default=3)
    p.add_argument("--batch_size", type=int, default=32)
    p.add_argument("--lr", type=float, default=3e-4)
    p.add_argument("--max_latent_stage", type=int, default=5)
    p.add_argument("--c_thought", type=int, default=1)
    p.add_argument("--n_val", type=int, default=500)
    p.add_argument(
        "--final_only",
        type=int,
        default=0,
        help="skip the curriculum and train only at the full-latent stage; the "
             "curriculum bootstraps from CoT ability, so it is wasted compute "
             "when the model never learns the explicit chain",
    )
    p.add_argument("--seed", type=int, default=0)
    a = p.parse_args()

    torch.manual_seed(a.seed)
    os.makedirs(a.out, exist_ok=True)
    dev = get_device()
    tok = get_tokenizer(a.task)

    train_ex = load(f"{a.data}/train.json")[: a.n_train]
    val_ex = load(f"{a.data}/val.json")[: a.n_val]
    test_ex = load(f"{a.data}/test.json")

    cur = CurriculumConfig(
        max_latent_stage=a.max_latent_stage,
        c_thought=a.c_thought,
        no_cot=(a.mode == "nocot"),
        cot_only=(a.mode == "cot"),
    )
    model = TinyLM(
        ModelConfig(vocab_size=len(tok), max_len=320, **PRESETS[a.preset])
    ).to(dev)
    coco = Coconut(model)

    log_path = os.path.join(a.out, "log.txt")
    logf = open(log_path, "a")

    def log(msg: str) -> None:
        print(msg, flush=True)
        logf.write(msg + "\n")
        logf.flush()

    log(f"=== {a.preset}/{a.mode} params={model.n_params() / 1e6:.2f}M device={dev} ===")
    log(f"train={len(train_ex)} val={len(val_ex)} test={len(test_ex)}")

    tc = TrainConfig(
        epochs_per_stage=a.epochs_per_stage, batch_size=a.batch_size, lr=a.lr
    )
    # CoT and no-CoT have no curriculum: a single stage trained for the same
    # total number of epochs as the Coconut run, for a fair comparison.
    if a.mode == "coconut" and a.final_only:
        stages = [FINAL_STAGE]
        tc.epochs_per_stage = a.epochs_per_stage * (a.max_latent_stage + 2)
    elif a.mode == "coconut":
        stages = list(range(a.max_latent_stage + 1)) + [FINAL_STAGE]
    else:
        stages = [0]
        tc.epochs_per_stage = a.epochs_per_stage * (a.max_latent_stage + 2)

    res = train_curriculum(coco, train_ex, val_ex, tok, cur, tc, dev, stages=stages, log=log)

    eval_stage = FINAL_STAGE if a.mode == "coconut" else 0
    metrics = evaluate(coco, test_ex, tok, cur, dev, stage=eval_stage)
    log(f"TEST exact={metrics['exact']:.4f} concept={metrics['concept']:.4f}")

    torch.save(
        {
            "model": model.state_dict(),
            "cfg": PRESETS[a.preset] | {"vocab_size": len(tok), "max_len": 320},
            "args": vars(a),
        },
        os.path.join(a.out, "model.pt"),
    )
    with open(os.path.join(a.out, "metrics.json"), "w") as f:
        json.dump({"test": metrics, "train": res}, f, indent=2)
    log(f"saved -> {a.out}")


if __name__ == "__main__":
    main()
