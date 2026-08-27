"""Advantages, loss masking, and the update step."""

import copy

import numpy as np
import pytest
import torch
import torch.nn.functional as F

from src.rl.env import EnvConfig, EpisodeEnv
from src.rl.grpo import (GRPOConfig, GRPOTrainer, group_advantages, grpo_loss,
                         pad_batch, token_logprobs)
from src.rl.sampler import ScriptedPolicy
from src.rl.tests.conftest import first_task, make_scripted_step_fn


def test_group_advantages_center_and_scale():
    rewards = [1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0]
    adv = group_advantages(rewards, 4)
    assert adv.shape == (8,)
    # First group: one winner above the mean, three losers below.
    assert adv[0] > 0 and all(a < 0 for a in adv[1:4])
    assert adv[:4].sum() == pytest.approx(0.0, abs=1e-9)
    # Second group has no spread, so it carries no signal at all.
    assert list(adv[4:]) == [0.0, 0.0, 0.0, 0.0]


def test_group_advantages_unnormalized_is_plain_centering():
    adv = group_advantages([1.0, 0.0], 2, normalize=False)
    assert list(adv) == [0.5, -0.5]


def test_group_advantages_scale_is_unit_std():
    adv = group_advantages([1.0, 0.0], 2, eps=0.0)
    assert adv[0] == pytest.approx(1.0)
    assert adv[1] == pytest.approx(-1.0)


def test_group_advantages_rejects_ragged_input():
    with pytest.raises(ValueError):
        group_advantages([1.0, 0.0, 1.0], 2)


def _two_rollouts(tok):
    env = EpisodeEnv(tok, EnvConfig(max_rounds=2, max_new_tokens=48,
                                    query_max_tokens=8, max_len=512))
    from src.worldgen.engine import generate_episodes
    episodes = list(generate_episodes(1717, 2))
    tasks = [first_task(env, ep, tok) for ep in episodes]
    rolls = []
    for t in tasks:
        fn = make_scripted_step_fn(tok, t.question, t.gold, target_rounds=1)
        rolls.append(env.rollout(ScriptedPolicy(fn), [t])[0])
    return rolls


def test_pad_batch_shifts_targets_and_carries_the_mask(tok):
    rolls = _two_rollouts(tok)
    inputs, targets, mask = pad_batch(rolls, torch.device("cpu"))
    width = max(len(r.tokens) for r in rolls)
    assert inputs.shape == targets.shape == mask.shape == (2, width - 1)
    for i, r in enumerate(rolls):
        assert inputs[i, :len(r.tokens) - 1].tolist() == r.tokens[:-1]
        assert targets[i, :len(r.tokens) - 1].tolist() == r.tokens[1:]
        assert mask[i, :len(r.tokens) - 1].tolist() == [float(m)
                                                        for m in r.mask[1:]]
        # Padding past the end of a short rollout never enters the loss.
        assert mask[i, len(r.tokens) - 1:].sum().item() == 0.0


def test_retrieved_chunk_positions_receive_zero_gradient(tok, tiny_model):
    rolls = _two_rollouts(tok)
    inputs, targets, mask = pad_batch(rolls, torch.device("cpu"))
    model = copy.deepcopy(tiny_model)

    logits, _ = model(inputs)
    logits.retain_grad()
    logp = -F.cross_entropy(logits.reshape(-1, logits.shape[-1]).float(),
                            targets.reshape(-1), reduction="none")
    logp = logp.view(targets.shape)
    frozen = logp.detach()
    cfg = GRPOConfig(kl_coef=0.0)
    adv = torch.tensor([1.0, -1.0])
    loss, _ = grpo_loss(logp, frozen, frozen, adv, mask, cfg)
    loss.backward()

    grad = logits.grad.abs().sum(dim=-1)
    assert torch.all(grad[mask == 0] == 0.0)
    assert torch.any(grad[mask == 1] > 0.0)

    # And specifically: every token of every served chunk is masked out.
    result_id = tok.special_ids["<|result|>"]
    for i, roll in enumerate(rolls):
        positions = [p for p, t in enumerate(roll.tokens) if t == result_id]
        for pos, round_ in zip(positions, roll.rounds):
            # Chunk tokens sit right after the <|result|> marker; the grad
            # index for token p is p - 1, since position t predicts t + 1.
            for p in range(pos + 1, pos + 1 + round_["n_chunk_tokens"]):
                assert grad[i, p - 1].item() == 0.0


def test_token_logprobs_match_log_softmax_gather(tok, tiny_model):
    rolls = _two_rollouts(tok)
    inputs, targets, _ = pad_batch(rolls, torch.device("cpu"))
    logp, entropy = token_logprobs(tiny_model, inputs, targets,
                                   want_entropy=True, autocast=False)
    with torch.no_grad():
        logits, _ = tiny_model(inputs)
        ref = F.log_softmax(logits.float(), dim=-1)
        want = ref.gather(-1, targets.unsqueeze(-1)).squeeze(-1)
        want_ent = -(ref.exp() * ref).sum(-1)
    assert torch.allclose(logp, want, atol=1e-5)
    assert torch.allclose(entropy, want_ent, atol=1e-5)


def test_loss_is_zero_without_advantage_or_divergence(tok, tiny_model):
    rolls = _two_rollouts(tok)
    inputs, targets, mask = pad_batch(rolls, torch.device("cpu"))
    logp, _ = token_logprobs(tiny_model, inputs, targets, autocast=False)
    frozen = logp.detach()
    cfg = GRPOConfig(kl_coef=0.5)
    adv = torch.zeros(2)
    loss, stats = grpo_loss(logp, frozen, frozen, adv, mask, cfg)
    assert float(loss) == pytest.approx(0.0, abs=1e-5)
    assert stats["kl_sum"] == pytest.approx(0.0, abs=1e-5)


def test_kl_term_is_positive_when_the_reference_disagrees(tok, tiny_model):
    rolls = _two_rollouts(tok)
    inputs, targets, mask = pad_batch(rolls, torch.device("cpu"))
    logp, _ = token_logprobs(tiny_model, inputs, targets, autocast=False)
    ref = logp.detach() - 0.5
    cfg = GRPOConfig(kl_coef=1.0)
    _, stats = grpo_loss(logp, logp.detach(), ref, torch.zeros(2), mask, cfg)
    assert stats["kl_sum"] > 0.0


def test_select_groups_drops_flat_groups(tiny_model, tmp_path):
    cfg = GRPOConfig(group_size=2)
    trainer = GRPOTrainer(copy.deepcopy(tiny_model), cfg, str(tmp_path),
                          device="cpu")
    rolls = list(range(6))
    adv = np.array([1.0, -1.0, 0.0, 0.0, 0.5, -0.5])
    kept, kept_adv, dropped = trainer.select_groups(rolls, adv)
    assert dropped == 1
    assert kept == [0, 1, 4, 5]
    assert list(kept_adv) == [1.0, -1.0, 0.5, -0.5]


def test_update_takes_a_step_and_checkpoints_round_trip(tok, tiny_model, tmp_path):
    rolls = _two_rollouts(tok)
    cfg = GRPOConfig(group_size=2, micro_batch_size=2, kl_coef=0.1,
                     lr=1e-3, warmup_steps=0, max_steps=4, min_lr_ratio=1.0)
    model = copy.deepcopy(tiny_model)
    before = model.lm_head.weight.detach().clone()
    trainer = GRPOTrainer(model, cfg, str(tmp_path), device="cpu")
    adv = group_advantages([1.0, 0.0], 2)
    stats = trainer.update(rolls, adv)
    assert not stats["skipped"]
    assert trainer.step == 1
    assert np.isfinite(stats["loss"])
    assert stats["train_tokens"] > 0
    assert not torch.allclose(before, model.lm_head.weight)

    model_config = {"model": {"vocab_size": model.cfg.vocab_size,
                              "d_model": model.cfg.d_model,
                              "n_layers": model.cfg.n_layers,
                              "n_heads": model.cfg.n_heads,
                              "d_ff": model.cfg.d_ff,
                              "max_seq_len": model.cfg.max_seq_len}}
    path = trainer.save_checkpoint(model_config)
    assert path.exists() and (tmp_path / "latest.pt").exists()

    revived = GRPOTrainer(copy.deepcopy(tiny_model), cfg, str(tmp_path),
                          device="cpu")
    revived.load_checkpoint(tmp_path / "latest.pt")
    assert revived.step == 1
    assert torch.allclose(revived.model.lm_head.weight, model.lm_head.weight)


def test_update_skips_when_every_group_is_flat(tok, tiny_model, tmp_path):
    rolls = _two_rollouts(tok)
    cfg = GRPOConfig(group_size=2, micro_batch_size=2)
    trainer = GRPOTrainer(copy.deepcopy(tiny_model), cfg, str(tmp_path),
                          device="cpu")
    stats = trainer.update(rolls, np.zeros(2))
    assert stats["skipped"]
    assert trainer.step == 0
