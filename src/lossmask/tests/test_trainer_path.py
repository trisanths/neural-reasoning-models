"""The trainer's third tensor, end to end on a tiny model."""

import numpy as np
import torch

from src.lossmask.shards import (TaggedShardReader, TaggedShardWriter,
                                 WeightedBatchLoader)
from src.lossmask.tags import TAG_ENTITY, weight_table
from src.train.data import BatchLoader, ShardReader
from src.train.model import ModelConfig, TransformerLM
from src.train.trainer import Trainer

CFG = {
    "model": {"vocab_size": 64, "d_model": 32, "n_layers": 2, "n_heads": 4,
              "d_ff": 64, "max_seq_len": 16},
    "optimizer": {"lr": 1e-3},
    "schedule": {"warmup_steps": 0, "max_steps": 3, "min_lr_ratio": 0.1},
    "train": {"batch_size": 2, "global_batch_size": 2, "grad_accum_steps": 1,
              "seed": 5, "ckpt_interval": 0, "log_interval": 100},
}


def corpus(tmp_path, n=400):
    rng = np.random.default_rng(0)
    tokens = rng.integers(0, 64, size=n)
    tags = np.zeros(n, dtype=np.uint8)
    tags[::7] = TAG_ENTITY
    writer = TaggedShardWriter(tmp_path, shard_size=128)
    writer.write(tokens, tags)
    writer.close()
    return tokens, tags


def make_trainer(tmp_path):
    torch.manual_seed(0)
    model = TransformerLM(ModelConfig(**CFG["model"]))
    return Trainer(model, CFG, str(tmp_path / "run"), device="cpu")


def test_all_ones_weights_train_exactly_like_the_plain_path(tmp_path):
    corpus(tmp_path / "data")

    plain = make_trainer(tmp_path / "a")
    plain_losses = plain.train(
        BatchLoader(ShardReader(tmp_path / "data"), 2, 16, seed=1),
        save_at_end=False)

    weighted = make_trainer(tmp_path / "b")
    weighted_losses = weighted.train(
        WeightedBatchLoader(TaggedShardReader(tmp_path / "data"), 2, 16,
                            weight_table(None), seed=1),
        save_at_end=False)

    assert len(plain_losses) == len(weighted_losses) == 3
    for a, b in zip(plain_losses, weighted_losses):
        assert abs(a - b) < 1e-5
    for a, b in zip(plain.model.parameters(), weighted.model.parameters()):
        assert torch.allclose(a, b, atol=1e-5)


def test_masking_changes_the_weights_it_learns(tmp_path):
    corpus(tmp_path / "data")
    reader = TaggedShardReader(tmp_path / "data")

    control = make_trainer(tmp_path / "c")
    control.train(WeightedBatchLoader(reader, 2, 16, weight_table(None),
                                      seed=1), save_at_end=False)
    masked = make_trainer(tmp_path / "d")
    masked.train(WeightedBatchLoader(reader, 2, 16,
                                     weight_table({"entity": 0.0}), seed=1),
                 save_at_end=False)

    diffs = [not torch.allclose(a, b, atol=1e-7) for a, b in
             zip(control.model.parameters(), masked.model.parameters())]
    assert any(diffs), "masking entity tokens must move the weights"
