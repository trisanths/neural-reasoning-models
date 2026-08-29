"""Shapes, gradients, the gate, determinism, and the parameter budget."""

from pathlib import Path

import pytest
import torch
import yaml

from src.train.evidence_model import (EvidenceModelConfig,
                                      EvidenceTransformerLM, config_from_yaml)
from src.train.model import ModelConfig, TransformerLM
from src.train.tests.evidence_fixtures import TINY

REPO_ROOT = Path(__file__).resolve().parents[3]


def make_batch(cfg: EvidenceModelConfig, bsz=2, seq=12, n_chunks=6, seed=0):
    gen = torch.Generator().manual_seed(seed)
    ids = torch.randint(0, cfg.vocab_size, (bsz, seq), generator=gen)
    ev = torch.randint(0, cfg.vocab_size, (bsz, n_chunks, cfg.chunk_len), generator=gen)
    mask = torch.ones_like(ev, dtype=torch.bool)
    mask[:, :, cfg.chunk_len // 2:] = False  # half of every chunk is padding
    chunk_mask = torch.ones((bsz, n_chunks), dtype=torch.bool)
    chunk_mask[0, -1] = False  # one short bank
    rel = torch.rand((bsz, n_chunks), generator=gen)
    return ids, ev, mask, chunk_mask, rel


@pytest.mark.parametrize("mode", ["pooled", "tokens"])
def test_forward_shapes(mode):
    cfg = EvidenceModelConfig(**{**TINY.__dict__, "evidence_mode": mode})
    model = EvidenceTransformerLM(cfg)
    ids, ev, mask, chunk_mask, rel = make_batch(cfg)
    logits, loss = model(ids, ev, mask, rel, chunk_mask)
    assert logits.shape == (2, 12, cfg.vocab_size)
    assert loss is None


@pytest.mark.parametrize("mode", ["pooled", "tokens"])
def test_memory_shapes(mode):
    model = EvidenceTransformerLM(TINY)
    ids, ev, mask, chunk_mask, rel = make_batch(TINY, n_chunks=5)
    mem = model.encode_evidence(ev, mask, rel, chunk_mask, mode=mode)
    expected = 5 if mode == "pooled" else 5 * TINY.chunk_len
    assert mem.n_positions == expected
    # One extra position for the always-available null slot.
    assert mem.states.shape == (2, expected + 1, TINY.d_enc)
    assert mem.mask.shape == (2, expected + 1)
    assert bool(mem.mask[:, 0].all())


@pytest.mark.parametrize("mode", ["pooled", "tokens"])
def test_gradients_flow_everywhere(mode):
    torch.manual_seed(0)
    cfg = EvidenceModelConfig(**{**TINY.__dict__, "evidence_mode": mode})
    model = EvidenceTransformerLM(cfg)
    ids, ev, mask, chunk_mask, rel = make_batch(cfg)
    targets = ids.clone()
    targets[:, :4] = -100
    _, loss = model(ids, ev, mask, rel, chunk_mask, targets=targets)
    assert torch.isfinite(loss)
    loss.backward()
    for name, param in model.named_parameters():
        assert param.grad is not None, name
        assert torch.isfinite(param.grad).all(), name
    # The evidence path in particular must carry gradient, not just exist.
    for name in ["encoder.in_proj.weight", "encoder.chunk_pos.weight",
                 "encoder.reliability_emb.weight", "null_evidence"]:
        grad = dict(model.named_parameters())[name].grad
        assert grad.abs().sum() > 0, name
    xattn_grads = [p.grad.abs().sum() for n, p in model.named_parameters()
                   if ".xattn." in n and "gate_proj" not in n]
    assert xattn_grads and all(g > 0 for g in xattn_grads)


def test_loss_covers_exactly_the_unmasked_positions():
    """The reported loss must be the mean over supervised positions only."""
    torch.manual_seed(0)
    model = EvidenceTransformerLM(TINY)
    model.eval()
    ids, ev, mask, chunk_mask, rel = make_batch(TINY)
    targets = ids.clone()
    targets[:, :6] = -100
    with torch.no_grad():
        logits, loss = model(ids, ev, mask, rel, chunk_mask, targets=targets)
        manual = torch.nn.functional.cross_entropy(
            logits[:, 6:].float().reshape(-1, TINY.vocab_size),
            targets[:, 6:].reshape(-1),
        )
    assert torch.allclose(loss, manual, atol=1e-6)


@pytest.mark.parametrize("mode", ["pooled", "tokens"])
def test_gate_zero_suppresses_evidence(mode):
    torch.manual_seed(0)
    cfg = EvidenceModelConfig(**{**TINY.__dict__, "evidence_mode": mode,
                                 "gate_bias_init": 2.0})
    model = EvidenceTransformerLM(cfg)
    model.eval()
    ids, ev_a, mask, chunk_mask, rel = make_batch(cfg, seed=1)
    _, ev_b, _, _, _ = make_batch(cfg, seed=99)
    with torch.no_grad():
        open_a, _ = model(ids, ev_a, mask, rel, chunk_mask)
        open_b, _ = model(ids, ev_b, mask, rel, chunk_mask)
        shut_a, _ = model(ids, ev_a, mask, rel, chunk_mask, gate_override=0.0)
        shut_b, _ = model(ids, ev_b, mask, rel, chunk_mask, gate_override=0.0)
        no_evidence, _ = model(ids)
    # With the gate open, the bank changes the answer.
    assert not torch.allclose(open_a, open_b, atol=1e-5)
    # With the gate shut, the bank is irrelevant and the model is the plain
    # decoder it would be with no evidence at all.
    assert torch.allclose(shut_a, shut_b, atol=1e-6)
    assert torch.allclose(shut_a, no_evidence, atol=1e-6)


def test_gate_is_learnable_and_bounded():
    cfg = EvidenceModelConfig(**{**TINY.__dict__, "gate_bias_init": 0.0})
    model = EvidenceTransformerLM(cfg)
    x = torch.randn(2, 5, cfg.d_model)
    block = next(b for b in model.blocks if b.xattn is not None)
    gate = block.xattn.gate(x, None)
    assert gate.shape == (2, 5, 1)
    assert torch.allclose(gate, torch.full_like(gate, 0.5))
    with torch.no_grad():
        block.xattn.gate_proj.bias.fill_(-8.0)
    assert float(block.xattn.gate(x, None).detach().max()) < 1e-3


def test_determinism_same_seed():
    def run(seed):
        torch.manual_seed(seed)
        model = EvidenceTransformerLM(TINY)
        model.eval()
        ids, ev, mask, chunk_mask, rel = make_batch(TINY, seed=3)
        with torch.no_grad():
            logits, _ = model(ids, ev, mask, rel, chunk_mask)
        return logits
    assert torch.equal(run(11), run(11))
    assert not torch.equal(run(11), run(12))


def test_chunk_encoding_is_independent_of_the_rest_of_the_bank():
    """A chunk's encoding may depend on its rank, never on its neighbours."""
    torch.manual_seed(0)
    model = EvidenceTransformerLM(TINY)
    model.eval()
    gen = torch.Generator().manual_seed(5)
    ev = torch.randint(0, TINY.vocab_size, (1, 4, TINY.chunk_len), generator=gen)
    mask = torch.ones_like(ev, dtype=torch.bool)
    rel = torch.ones((1, 4))
    with torch.no_grad():
        a = model.encoder(ev, mask, rel)
        swapped = ev.clone()
        swapped[:, 2:] = torch.randint(0, TINY.vocab_size, (1, 2, TINY.chunk_len),
                                       generator=gen)
        b = model.encoder(swapped, mask, rel)
    assert torch.allclose(a[:, :2], b[:, :2], atol=1e-6)


def test_padded_chunks_do_not_produce_nan():
    model = EvidenceTransformerLM(TINY)
    ids = torch.randint(0, TINY.vocab_size, (1, 8))
    ev = torch.zeros((1, 3, TINY.chunk_len), dtype=torch.long)
    mask = torch.zeros_like(ev, dtype=torch.bool)
    chunk_mask = torch.zeros((1, 3), dtype=torch.bool)
    rel = torch.ones((1, 3))
    logits, _ = model(ids, ev, mask, rel, chunk_mask)
    assert torch.isfinite(logits).all()


def test_rejects_oversized_inputs():
    model = EvidenceTransformerLM(TINY)
    ids = torch.zeros((1, TINY.max_seq_len + 1), dtype=torch.long)
    with pytest.raises(ValueError):
        model(ids)
    ids = torch.zeros((1, 4), dtype=torch.long)
    long_chunks = torch.zeros((1, 2, TINY.chunk_len + 1), dtype=torch.long)
    with pytest.raises(ValueError):
        model(ids, long_chunks)
    wide_bank = torch.zeros((1, TINY.max_chunks + 1, TINY.chunk_len), dtype=torch.long)
    with pytest.raises(ValueError):
        model(ids, wide_bank)


def test_config_validation():
    with pytest.raises(ValueError):
        EvidenceModelConfig(d_model=100, n_heads=16)
    with pytest.raises(ValueError):
        EvidenceModelConfig(evidence_mode="magic")
    with pytest.raises(ValueError):
        EvidenceModelConfig(n_heads=16, xattn_n_kv_heads=5)


def test_xattn_layer_placement():
    cfg = EvidenceModelConfig(n_layers=21, xattn_every=3)
    assert cfg.xattn_layers == [2, 5, 8, 11, 14, 17, 20]
    model = EvidenceTransformerLM(EvidenceModelConfig(
        **{**TINY.__dict__, "n_layers": 4, "xattn_every": 2}))
    with_x = [i for i, b in enumerate(model.blocks) if b.xattn is not None]
    assert with_x == [1, 3]


def test_350m_xattn_matches_the_standard_350m_budget():
    with open(REPO_ROOT / "configs" / "350m-xattn.yaml") as fh:
        xcfg = yaml.safe_load(fh)
    with open(REPO_ROOT / "configs" / "350m.yaml") as fh:
        scfg = yaml.safe_load(fh)

    model = EvidenceTransformerLM(config_from_yaml(xcfg["model"]))
    split = model.param_breakdown()
    standard = TransformerLM(ModelConfig(**scfg["model"]))
    std_total = sum(p.numel() for p in standard.parameters())

    ratio = split["total"] / std_total
    assert 0.98 <= ratio <= 1.02, (split["total"], std_total, ratio)
    # The parts are all present and none of them has collapsed to nothing.
    assert split["encoder"] > 10_000_000
    assert split["cross_attention"] > 10_000_000
    assert split["decoder"] > 200_000_000
    assert split["embedding"] == split["lm_head"] == 32768 * 1024
    assert split["total"] == sum(p.numel() for p in model.parameters())
