import itertools
import math
from pathlib import Path

import pytest
import torch
import yaml

from src.train.model import ModelConfig, TransformerLM
from src.train.trainer import Trainer

REPO_ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.skipif(not torch.cuda.is_available(), reason="cuda is not available")
def test_smoke_config_10_steps_on_cuda(tmp_path):
    with open(REPO_ROOT / "configs" / "smoke.yaml") as fh:
        cfg = yaml.safe_load(fh)
    cfg["schedule"]["max_steps"] = 10
    cfg["schedule"]["warmup_steps"] = 2
    cfg["train"]["ckpt_interval"] = 0
    cfg["train"]["log_interval"] = 1

    model_cfg = ModelConfig(**cfg["model"])
    model = TransformerLM(model_cfg)
    trainer = Trainer(model, cfg, tmp_path, device="cuda")

    gen = torch.Generator().manual_seed(2)
    batch_size = int(cfg["train"]["batch_size"])
    tokens = torch.randint(
        0, model_cfg.vocab_size, (batch_size, model_cfg.max_seq_len + 1), generator=gen
    )
    batch = (tokens[:, :-1].contiguous(), tokens[:, 1:].contiguous())
    losses = trainer.train(itertools.cycle([batch]), until_step=10)

    assert len(losses) == 10
    assert all(math.isfinite(v) for v in losses)
    assert losses[-1] < losses[0], f"loss did not decrease: {losses}"
