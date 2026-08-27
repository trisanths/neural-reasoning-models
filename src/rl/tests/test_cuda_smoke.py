"""Five real optimization steps on a GPU, from a checkpoint on disk.

Skipped without cuda. By default the checkpoint is the tiny one the test
fixtures write, so the smoke runs anywhere a GPU exists; point
RL_SMOKE_CKPT and RL_SMOKE_TOKENIZER at a trained checkpoint to run the
same path on the real policy.
"""

import os

import numpy as np
import pytest
import torch

from src.evals.mc import load_checkpoint_model
from src.rl.env import EnvConfig, EpisodeEnv, load_tasks, make_service
from src.rl.grpo import GRPOConfig, GRPOTrainer, group_advantages
from src.rl.sampler import CachedPolicy
from src.train.tokenizer import load_tokenizer

pytestmark = pytest.mark.skipif(not torch.cuda.is_available(),
                                reason="needs cuda")


def test_five_optimization_steps_on_cuda(tiny_ckpt, tok, episodes_jsonl,
                                         tmp_path):
    ckpt = os.environ.get("RL_SMOKE_CKPT", tiny_ckpt)
    tok_path = os.environ.get("RL_SMOKE_TOKENIZER")
    tokenizer = load_tokenizer(tok_path) if tok_path else tok
    episodes = os.environ.get("RL_SMOKE_EPISODES", episodes_jsonl)

    device = "cuda"
    model, state = load_checkpoint_model(ckpt, device)
    env_cfg = EnvConfig(max_rounds=2, max_new_tokens=48, query_max_tokens=12,
                        max_len=min(512, model.cfg.max_seq_len))
    env = EpisodeEnv(tokenizer, env_cfg)
    tasks = load_tasks(episodes, tokenizer, limit_episodes=8,
                       questions_per_episode=2,
                       max_prompt_tokens=env_cfg.max_len // 2)
    assert tasks, "no tasks loaded for the smoke"

    group = 4
    cfg = GRPOConfig(group_size=group, prompts_per_step=2, micro_batch_size=4,
                     kl_coef=0.02, lr=1e-6, warmup_steps=1, max_steps=5,
                     drop_zero_variance_groups=False)
    trainer = GRPOTrainer(model, cfg, str(tmp_path), device=device)
    policy = CachedPolicy(model, device, max_len=env_cfg.max_len,
                          temperature=1.0, seed=0)

    rng = np.random.default_rng(0)
    for _ in range(5):
        picked = [tasks[int(rng.integers(len(tasks)))] for _ in range(2)]
        batch = [t for t in picked for _ in range(group)]
        rolls = env.rollout(policy, batch, [make_service(t.documents)
                                            for t in batch])
        assert len(rolls) == len(batch)
        assert all(len(r.mask) == len(r.tokens) for r in rolls)
        adv = group_advantages([r.reward for r in rolls], group)
        stats = trainer.update(rolls, adv)
        assert not stats["skipped"]
        assert np.isfinite(stats["loss"])
        assert np.isfinite(stats["grad_norm"])

    assert trainer.step == 5
    path = trainer.save_checkpoint(state["config"])
    assert path.exists()
