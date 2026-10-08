import itertools

import torch

from src.train.model import ModelConfig, TransformerLM
from src.train.trainer import Trainer


def test_tiny_model_overfits_fixed_batch(tmp_path):
    cfg = {
        "optimizer": {"lr": 1.0e-2, "weight_decay": 0.0, "beta1": 0.9, "beta2": 0.95},
        "schedule": {"warmup_steps": 10, "max_steps": 200, "min_lr_ratio": 0.1},
        "train": {
            "batch_size": 4,
            "grad_accum_steps": 1,
            "grad_clip": 1.0,
            "seed": 7,
            "log_interval": 50,
            "ckpt_interval": 0,
        },
    }
    model_cfg = ModelConfig(
        vocab_size=128, d_model=64, n_layers=2, n_heads=4, d_ff=176, max_seq_len=32
    )
    model = TransformerLM(model_cfg)
    trainer = Trainer(model, cfg, tmp_path, device="cpu")

    gen = torch.Generator().manual_seed(3)
    tokens = torch.randint(0, model_cfg.vocab_size, (4, 33), generator=gen)
    batch = (tokens[:, :-1].contiguous(), tokens[:, 1:].contiguous())
    losses = trainer.train(itertools.cycle([batch]))

    assert len(losses) == 200
    assert losses[-1] < 0.1, f"final loss {losses[-1]} did not reach near zero"
    assert losses[-1] < losses[0]
    assert (tmp_path / "loss.jsonl").exists()
    assert (tmp_path / "latest.pt").exists()
