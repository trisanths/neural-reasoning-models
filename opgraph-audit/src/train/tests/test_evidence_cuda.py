"""CUDA smoke: bf16 forward and backward, a real bank, loss goes down."""

import math
from pathlib import Path

import pytest
import torch
import yaml

from src.train.evidence_data import EvidenceCollator
from src.train.evidence_model import (EvidenceModelConfig,
                                      EvidenceTransformerLM, config_from_yaml)
from src.train.evidence_trainer import forward_batch, train_evidence_steps
from src.train.tests.evidence_fixtures import (StubTokenizer, marker_examples,
                                               pool_chunks, synthetic_episode)
from src.train.evidence_data import examples_from_episode

REPO_ROOT = Path(__file__).resolve().parents[3]

SMOKE_CFG = EvidenceModelConfig(
    vocab_size=512, d_model=256, n_layers=6, n_heads=8, d_ff=704,
    max_seq_len=128, d_enc=128, enc_layers=2, enc_heads=4, enc_d_ff=352,
    chunk_len=64, xattn_every=2, xattn_n_kv_heads=2, max_chunks=512,
)


@pytest.mark.skipif(not torch.cuda.is_available(), reason="cuda is not available")
def test_cuda_train_steps_reduce_loss():
    tok = StubTokenizer(vocab_size=512)
    examples = marker_examples(16, 64, 64, 512, seed=0)
    collator = EvidenceCollator(tok, bank_size=64, chunk_len=64, max_seq_len=128)
    batch = collator(examples)
    torch.manual_seed(0)
    model = EvidenceTransformerLM(SMOKE_CFG)
    losses = train_evidence_steps(model, [batch], steps=30, lr=2e-3,
                                  device="cuda", seed=0, warmup_steps=5)
    assert len(losses) == 30
    assert all(math.isfinite(v) for v in losses)
    assert losses[-1] < losses[0], losses


@pytest.mark.skipif(not torch.cuda.is_available(), reason="cuda is not available")
@pytest.mark.parametrize("mode", ["pooled", "tokens"])
def test_cuda_bf16_forward_backward_on_a_large_bank(mode):
    tok = StubTokenizer(vocab_size=512)
    ep = synthetic_episode(n_docs=12, n_questions=2)
    pool = pool_chunks(600, 64, seed=1, vocab_size=512)
    examples = examples_from_episode(ep, tok, 64, 256, "oracle", 4, pool_chunks=pool)
    collator = EvidenceCollator(tok, bank_size=256, chunk_len=64, max_seq_len=128)
    batch = collator(examples).to("cuda")
    torch.manual_seed(0)
    model = EvidenceTransformerLM(SMOKE_CFG).to("cuda")
    with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
        _, loss = forward_batch(model, batch, mode)
    assert torch.isfinite(loss)
    loss.backward()
    grads = [p.grad for n, p in model.named_parameters() if ".xattn." in n]
    assert grads and all(torch.isfinite(g).all() for g in grads)
    assert batch.n_evidence_tokens > 10_000


@pytest.mark.skipif(not torch.cuda.is_available(), reason="cuda is not available")
def test_350m_xattn_config_runs_on_one_gpu():
    """The shipped config, a 256 chunk bank, one forward and backward."""
    with open(REPO_ROOT / "configs" / "350m-xattn.yaml") as fh:
        cfg = yaml.safe_load(fh)
    model = EvidenceTransformerLM(config_from_yaml(cfg["model"])).to("cuda")
    total = model.param_breakdown()["total"]
    assert 3.6e8 < total < 3.9e8

    gen = torch.Generator(device="cuda").manual_seed(0)
    ids = torch.randint(0, 32768, (1, 64), device="cuda", generator=gen)
    ev = torch.randint(0, 32768, (1, 256, 128), device="cuda", generator=gen)
    mask = torch.ones_like(ev, dtype=torch.bool)
    targets = ids.clone()
    targets[:, :32] = -100
    with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
        _, loss = model(ids, ev, mask, targets=targets, mode="pooled")
    loss.backward()
    assert torch.isfinite(loss)
    torch.cuda.empty_cache()
