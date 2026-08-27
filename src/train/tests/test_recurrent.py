"""Depth recurrence: disabled mode bit identity, gradient flow at every
backprop setting, the loop count dial, and training end to end.

The references under data/ were produced by scripts/make_recurrent_reference.py
running the pre recurrence model.py out of git.
"""

import itertools
import math
import os
from pathlib import Path

import pytest
import torch
import yaml

from src.train.model import ModelConfig, RecurrentConfig, TransformerLM
from src.train.trainer import Trainer

REPO_ROOT = Path(__file__).resolve().parents[3]
REF_TINY = Path(__file__).resolve().parent / "data" / "ref_disabled_tiny.pt"
REF_350M = Path(os.environ.get("REF_350M", Path.home() / "runs" / "ref350" / "ref_350m.pt"))

TINY = {
    "vocab_size": 128,
    "d_model": 64,
    "n_heads": 4,
    "d_ff": 176,
    "max_seq_len": 64,
}


def recurrent_model(prelude=1, core=2, coda=1, loops=2, seed=0, **rec_kwargs):
    torch.manual_seed(seed)
    rec = {
        "prelude_layers": prelude,
        "core_layers": core,
        "coda_layers": coda,
        "loops": loops,
    }
    rec.update(rec_kwargs)
    cfg = ModelConfig(n_layers=prelude + core + coda, recurrent=rec, **TINY)
    return TransformerLM(cfg)


def fixed_batch(vocab, batch=2, seq_len=16, seed=5):
    gen = torch.Generator().manual_seed(seed)
    tokens = torch.randint(0, vocab, (batch, seq_len + 1), generator=gen)
    return tokens[:, :-1].contiguous(), tokens[:, 1:].contiguous()


# ---------------- disabled mode bit identity ----------------


def test_disabled_mode_reproduces_saved_logits():
    ref = torch.load(REF_TINY, map_location="cpu", weights_only=False)
    model = TransformerLM(ModelConfig(**ref["model_config"]))
    assert model.cfg.recurrent is None
    missing = model.load_state_dict(ref["state_dict"], strict=True)
    assert not missing.missing_keys and not missing.unexpected_keys
    model.eval()
    with torch.no_grad():
        logits, _ = model(ref["input"])
    assert torch.equal(logits, ref["logits"]), (
        f"max abs diff {(logits - ref['logits']).abs().max().item()}"
    )


def test_disabled_mode_reproduces_saved_init_stream():
    """Adding recurrence must not perturb the init RNG stream, or every seeded
    run in the project would drift even with recurrence off."""
    ref = torch.load(REF_TINY, map_location="cpu", weights_only=False)
    torch.manual_seed(ref["seed"])
    model = TransformerLM(ModelConfig(**ref["model_config"]))
    fresh = model.state_dict()
    assert set(fresh) == set(ref["state_dict"])
    for name, tensor in ref["state_dict"].items():
        assert torch.equal(fresh[name], tensor), name


@pytest.mark.skipif(not REF_350M.exists(), reason=f"no 350m reference at {REF_350M}")
def test_disabled_mode_bit_identical_at_350m():
    ref = torch.load(REF_350M, map_location="cpu", weights_only=False)
    model = TransformerLM(ModelConfig(**ref["model_config"]))
    model.load_state_dict(ref["state_dict"], strict=True)
    model.eval()
    with torch.no_grad():
        logits, _ = model(ref["input"])
    assert torch.equal(logits, ref["logits"])


def test_effective_depth_matches_plain_model_when_disabled():
    cfg = ModelConfig(n_layers=4, **TINY)
    assert cfg.effective_depth() == 4
    model = TransformerLM(cfg)
    assert model.resolve_loops() == 1
    assert model.describe()["recurrent"] is None


# ---------------- shapes and the loop dial ----------------


def test_recurrent_forward_shapes():
    model = recurrent_model()
    idx, targets = fixed_batch(TINY["vocab_size"])
    logits, loss = model(idx, targets)
    assert logits.shape == (2, 16, TINY["vocab_size"])
    assert torch.isfinite(loss)


@pytest.mark.parametrize("loops", [1, 2, 3, 8, 11])
def test_shapes_are_loop_count_invariant(loops):
    """Loop counts past loop_slots reuse the last embedding row rather than
    indexing out of bounds, so the dial has no hard ceiling."""
    model = recurrent_model(loops=2, train_loop_sampling=[1, 4])
    assert model.cfg.recurrent.loop_slots == 4
    idx, _ = fixed_batch(TINY["vocab_size"])
    logits, _ = model(idx, loops=loops)
    assert logits.shape == (2, 16, TINY["vocab_size"])
    assert model.cfg.effective_depth(loops) == 1 + 2 * loops + 1


def test_effective_depth_and_describe():
    model = recurrent_model(prelude=1, core=3, coda=2, loops=4)
    assert model.cfg.n_layers == 6
    assert model.cfg.effective_depth() == 1 + 3 * 4 + 2
    info = model.describe()
    assert info["unique_layers"] == 6
    assert info["loops"] == 4
    assert info["effective_depth"] == 15
    assert info["recurrent"]["core_layers"] == 3


def test_more_loops_change_the_output():
    model = recurrent_model(loops=1)
    model.eval()
    idx, _ = fixed_batch(TINY["vocab_size"])
    with torch.no_grad():
        one, _ = model(idx, loops=1)
        four, _ = model(idx, loops=4)
    assert not torch.allclose(one, four)


def test_loops_override_context_manager_restores():
    model = recurrent_model(loops=2)
    assert model.resolve_loops() == 2
    with model.loops_override(7):
        assert model.resolve_loops() == 7
    assert model.resolve_loops() == 2
    model.set_loops(5)
    with model.loops_override(1):
        assert model.resolve_loops() == 1
    assert model.resolve_loops() == 5
    model.set_loops(None)
    assert model.resolve_loops() == 2


def test_explicit_argument_beats_standing_override():
    model = recurrent_model(loops=2)
    model.set_loops(6)
    assert model.resolve_loops(3) == 3


def test_sample_loops_stays_in_range_and_is_seeded():
    model = recurrent_model(loops=2, train_loop_sampling=[2, 5])
    gen = torch.Generator().manual_seed(11)
    first = [model.sample_loops(gen) for _ in range(40)]
    assert all(2 <= v <= 5 for v in first)
    assert len(set(first)) > 1
    gen2 = torch.Generator().manual_seed(11)
    second = [model.sample_loops(gen2) for _ in range(40)]
    assert first == second


def test_sample_loops_is_a_no_op_without_sampling():
    model = recurrent_model(loops=3)
    assert model.sample_loops(torch.Generator().manual_seed(1)) == 3
    assert model.resolve_loops() == 3


# ---------------- the per loop embedding ----------------


def test_loop_embedding_changes_activations_across_iterations():
    """With distinct FiLM rows the core sees a different input at each
    iteration; with the rows tied it degenerates to a fixed point map."""
    model = recurrent_model(loops=3, loop_embedding=True)
    model.eval()
    with torch.no_grad():
        model.loop_film.normal_(mean=0.0, std=0.1, generator=torch.Generator().manual_seed(4))
    idx, _ = fixed_batch(TINY["vocab_size"])
    with torch.no_grad():
        distinct, _ = model(idx)
        first_row = model.loop_film[0].clone()
        model.loop_film.copy_(first_row.expand_as(model.loop_film))
        tied, _ = model(idx)
    assert not torch.allclose(distinct, tied, atol=1e-5)


def test_loop_embedding_is_identity_at_init():
    """loop_film starts at zero, so an untrained recurrent model is exactly a
    weight tied stack and the FiLM adds no init time perturbation."""
    model = recurrent_model(loops=3, loop_embedding=True)
    assert torch.equal(model.loop_film, torch.zeros_like(model.loop_film))
    model.eval()
    idx, _ = fixed_batch(TINY["vocab_size"])
    with torch.no_grad():
        with_film, _ = model(idx)
    plain = recurrent_model(loops=3, loop_embedding=False)
    plain.load_state_dict(
        {k: v for k, v in model.state_dict().items() if k != "loop_film"}, strict=True
    )
    plain.eval()
    with torch.no_grad():
        without_film, _ = plain(idx)
    assert torch.equal(with_film, without_film)


def test_loop_embedding_absent_when_disabled():
    model = recurrent_model(loop_embedding=False)
    assert not hasattr(model, "loop_film")
    assert "loop_film" not in model.state_dict()


# ---------------- gradient flow at each backprop setting ----------------


def _grads_are_finite_everywhere(model, loops=None):
    idx, targets = fixed_batch(TINY["vocab_size"])
    model.train()
    _, loss = model(idx, targets, loops=loops)
    loss.backward()
    for name, param in model.named_parameters():
        assert param.grad is not None, name
        assert torch.isfinite(param.grad).all(), name
    return {name: p.grad.clone() for name, p in model.named_parameters()}


def test_gradient_flow_full_backprop():
    model = recurrent_model(loops=4)
    grads = _grads_are_finite_everywhere(model)
    assert grads["tok_emb.weight"].abs().sum() > 0
    assert grads["loop_adapter.weight"].abs().sum() > 0


def test_gradient_flow_with_truncated_backprop():
    model = recurrent_model(loops=4, backprop_last_k=1)
    grads = _grads_are_finite_everywhere(model)
    # The prelude injection keeps the embedding on the gradient path even when
    # the first three iterations are detached.
    assert grads["tok_emb.weight"].abs().sum() > 0
    assert grads["blocks.0.attn.wq.weight"].abs().sum() > 0


def test_adapter_injection_half_is_live_at_init():
    """A zero init on the prelude half of the adapter would make the embedding
    gradient exactly zero on the first truncated step, so it starts small but
    nonzero while the loop state half stays the identity."""
    d = TINY["d_model"]
    model = recurrent_model(loops=4)
    state_half = model.loop_adapter.weight[:, :d]
    inject_half = model.loop_adapter.weight[:, d:]
    assert torch.equal(state_half, torch.eye(d))
    assert inject_half.abs().sum() > 0
    assert inject_half.std().item() < 0.02


def test_truncation_without_prelude_injection_starves_the_prelude():
    """The documented tradeoff: with inject_prelude off, truncated backprop
    cuts the embedding and prelude off the gradient path entirely."""
    model = recurrent_model(loops=4, backprop_last_k=1, inject_prelude=False)
    idx, targets = fixed_batch(TINY["vocab_size"])
    model.train()
    _, loss = model(idx, targets)
    loss.backward()
    assert model.tok_emb.weight.grad is None
    assert model.blocks[0].attn.wq.weight.grad is None
    assert model.blocks[1].attn.wq.weight.grad is not None


def test_truncation_is_inactive_when_k_covers_every_loop():
    """k >= loops must give exactly the untruncated gradients."""
    full = recurrent_model(loops=3, seed=1)
    trunc = recurrent_model(loops=3, seed=1, backprop_last_k=3)
    a = _grads_are_finite_everywhere(full)
    b = _grads_are_finite_everywhere(trunc)
    for name in a:
        assert torch.allclose(a[name], b[name], atol=0, rtol=0), name


def test_truncation_changes_gradients_but_not_the_forward():
    full = recurrent_model(loops=4, seed=2)
    trunc = recurrent_model(loops=4, seed=2, backprop_last_k=2)
    idx, targets = fixed_batch(TINY["vocab_size"])
    full.train()
    trunc.train()
    _, loss_full = full(idx, targets)
    _, loss_trunc = trunc(idx, targets)
    assert torch.equal(loss_full, loss_trunc)
    loss_full.backward()
    loss_trunc.backward()
    g_full = full.blocks[1].mlp.w_down.weight.grad
    g_trunc = trunc.blocks[1].mlp.w_down.weight.grad
    assert not torch.allclose(g_full, g_trunc)


def test_truncation_is_off_under_no_grad_and_eval():
    """Detaching only matters in the backward pass, so an eval forward at any
    setting must match the untruncated eval forward exactly."""
    full = recurrent_model(loops=4, seed=3)
    trunc = recurrent_model(loops=4, seed=3, backprop_last_k=1)
    full.eval()
    trunc.eval()
    idx, _ = fixed_batch(TINY["vocab_size"])
    with torch.no_grad():
        a, _ = full(idx)
        b, _ = trunc(idx)
    assert torch.equal(a, b)


def test_grad_checkpointing_matches_plain_gradients():
    plain = recurrent_model(loops=4, seed=6)
    ckpt = recurrent_model(loops=4, seed=6, grad_checkpoint=True)
    a = _grads_are_finite_everywhere(plain)
    b = _grads_are_finite_everywhere(ckpt)
    for name in a:
        assert torch.allclose(a[name], b[name], atol=1e-6), name


def test_grad_checkpointing_with_truncation_together():
    model = recurrent_model(loops=4, grad_checkpoint=True, backprop_last_k=2)
    grads = _grads_are_finite_everywhere(model)
    assert grads["tok_emb.weight"].abs().sum() > 0


# ---------------- config validation ----------------


def test_layer_split_must_sum_to_n_layers():
    with pytest.raises(ValueError, match="must equal n_layers"):
        ModelConfig(n_layers=5, recurrent={"prelude_layers": 1, "core_layers": 2, "coda_layers": 1}, **TINY)


@pytest.mark.parametrize(
    "rec",
    [
        {"core_layers": 0},
        {"core_layers": 2, "loops": 0},
        {"core_layers": 2, "backprop_last_k": 0},
        {"core_layers": 2, "train_loop_sampling": [0, 3]},
        {"core_layers": 2, "train_loop_sampling": [4, 2]},
    ],
)
def test_rejects_bad_recurrent_settings(rec):
    with pytest.raises(ValueError):
        RecurrentConfig(**rec)


def test_loop_slots_defaults_to_the_largest_reachable_loop_count():
    assert RecurrentConfig(core_layers=2, loops=3).loop_slots == 3
    assert RecurrentConfig(core_layers=2, loops=3, train_loop_sampling=[1, 9]).loop_slots == 9


# ---------------- training, checkpointing, overfit ----------------


def trainer_cfg(**train_overrides):
    train = {
        "batch_size": 2,
        "grad_accum_steps": 1,
        "grad_clip": 1.0,
        "seed": 7,
        "log_interval": 50,
        "ckpt_interval": 0,
    }
    train.update(train_overrides)
    return {
        "optimizer": {"lr": 1.0e-2, "weight_decay": 0.0, "beta1": 0.9, "beta2": 0.95},
        "schedule": {"warmup_steps": 10, "max_steps": 250, "min_lr_ratio": 0.1},
        "train": train,
    }


def test_tiny_model_overfits_a_fixed_batch_at_two_loops(tmp_path):
    model = recurrent_model(prelude=1, core=1, coda=1, loops=2, seed=7)
    trainer = Trainer(model, trainer_cfg(), tmp_path, device="cpu")
    idx, targets = fixed_batch(TINY["vocab_size"], batch=4, seq_len=24, seed=8)
    losses = trainer.train(itertools.cycle([(idx, targets)]))
    assert len(losses) == 250
    assert all(math.isfinite(v) for v in losses)
    assert losses[-1] < 0.1, f"final loss {losses[-1]}"


def test_checkpoint_save_and_resume_with_recurrence(tmp_path):
    cfg = trainer_cfg(ckpt_interval=0)
    cfg["schedule"]["max_steps"] = 6
    model = recurrent_model(loops=2, seed=9, train_loop_sampling=[1, 4])
    trainer = Trainer(model, cfg, tmp_path, device="cpu")
    batch = fixed_batch(TINY["vocab_size"])
    trainer.train(itertools.cycle([batch]), until_step=3)
    trainer.save_checkpoint("mid.pt")
    tail = trainer.train(itertools.cycle([batch]), until_step=6)

    resumed_model = recurrent_model(loops=2, seed=99, train_loop_sampling=[1, 4])
    resumed = Trainer(resumed_model, cfg, tmp_path / "resume", device="cpu")
    resumed.load_checkpoint(tmp_path / "mid.pt")
    assert resumed.step == 3
    resumed_tail = resumed.train(itertools.cycle([batch]), until_step=6)
    # Same loss trajectory means the weights, the optimizer state, and the loop
    # count stream all came back.
    assert [round(v, 6) for v in resumed_tail] == [round(v, 6) for v in tail]
    for (name, a), b in zip(trainer.model.named_parameters(), resumed.model.parameters()):
        assert torch.allclose(a, b, atol=0, rtol=0), name


def test_trainer_logs_the_sampled_loop_count(tmp_path):
    import json

    cfg = trainer_cfg(log_interval=1, ckpt_interval=0)
    cfg["schedule"]["max_steps"] = 4
    model = recurrent_model(loops=2, train_loop_sampling=[1, 3])
    trainer = Trainer(model, cfg, tmp_path, device="cpu")
    trainer.train(itertools.cycle([fixed_batch(TINY["vocab_size"])]))
    records = [json.loads(line) for line in (tmp_path / "loss.jsonl").read_text().splitlines()]
    assert len(records) == 4
    assert all(1 <= r["loops"] <= 3 for r in records)


def test_trainer_logs_no_loop_count_without_recurrence(tmp_path):
    import json

    cfg = trainer_cfg(log_interval=1, ckpt_interval=0)
    cfg["schedule"]["max_steps"] = 2
    torch.manual_seed(0)
    model = TransformerLM(ModelConfig(n_layers=2, **TINY))
    trainer = Trainer(model, cfg, tmp_path, device="cpu")
    trainer.train(itertools.cycle([fixed_batch(TINY["vocab_size"])]))
    records = [json.loads(line) for line in (tmp_path / "loss.jsonl").read_text().splitlines()]
    assert all("loops" not in r for r in records)


# ---------------- the shipped config ----------------


def test_350m_loop_config_is_parameter_matched():
    with open(REPO_ROOT / "configs" / "350m-loop.yaml") as fh:
        loop_cfg = yaml.safe_load(fh)
    with open(REPO_ROOT / "configs" / "350m.yaml") as fh:
        base_cfg = yaml.safe_load(fh)
    loop_model = TransformerLM(ModelConfig(**loop_cfg["model"]))
    base_model = TransformerLM(ModelConfig(**base_cfg["model"]))
    loop_params = loop_model.num_params(non_embedding=False)
    base_params = base_model.num_params(non_embedding=False)
    assert abs(loop_params - base_params) / base_params < 0.01
    # Fewer unique layers, more layer applications: that is the whole point.
    assert loop_model.cfg.n_layers < base_model.cfg.n_layers
    assert loop_model.cfg.effective_depth() > base_model.cfg.effective_depth()


@pytest.mark.skipif(not torch.cuda.is_available(), reason="cuda is not available")
def test_350m_loop_trains_20_steps_on_cuda(tmp_path):
    with open(REPO_ROOT / "configs" / "350m-loop.yaml") as fh:
        cfg = yaml.safe_load(fh)
    cfg["model"]["max_seq_len"] = 1024
    cfg["schedule"]["max_steps"] = 20
    cfg["schedule"]["warmup_steps"] = 4
    cfg["train"]["batch_size"] = 1
    cfg["train"]["grad_accum_steps"] = 1
    cfg["train"]["ckpt_interval"] = 0
    cfg["train"]["log_interval"] = 1

    model_cfg = ModelConfig(**cfg["model"])
    model = TransformerLM(model_cfg)
    trainer = Trainer(model, cfg, tmp_path, device="cuda")
    # Trainer always writes a checkpoint on reaching its target step. At this
    # scale that is about 4.5 GiB of weights plus AdamW state, written twice,
    # into a tmpfs. The trajectory is what this test is about, so saving is off.
    trainer.save_checkpoint = lambda name=None: None
    gen = torch.Generator().manual_seed(2)
    tokens = torch.randint(
        0, model_cfg.vocab_size, (1, model_cfg.max_seq_len + 1), generator=gen
    )
    batch = (tokens[:, :-1].contiguous(), tokens[:, 1:].contiguous())
    losses = trainer.train(itertools.cycle([batch]), until_step=20)

    assert len(losses) == 20
    assert all(math.isfinite(v) for v in losses)
    assert losses[-1] < losses[0], f"loss did not decrease: {losses}"
