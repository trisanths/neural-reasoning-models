"""Wiring the pointer head into the plain decoder, and proving it costs nothing.

The first section is the whole reason model.pointer defaults to absent. The
references under data/ were produced by scripts/make_pointer_reference.py
running the pre pointer model.py out of git, so they are an old code artifact.
With the flag off the new model.py has to reproduce them exactly: the same
state dict keys, the same values out of the same seed, the same logits, the
same loss. Not close, equal.
"""

import os
from pathlib import Path

import pytest
import torch

from src.train.model import ModelConfig, TransformerLM
from src.train.pointer import PointerConfig
from src.train.tests.pointer_fixtures import copy_task_batch, probe_config

DATA = Path(__file__).resolve().parent / "data"
REF_TINY = DATA / "ref_no_pointer_tiny.pt"
REF_RECURRENT = DATA / "ref_no_pointer_recurrent.pt"
REF_350M = Path(os.environ.get("REF_350M_POINTER",
                               Path.home() / "runs" / "refptr" / "ref_350m_pointer.pt"))

TINY = {
    "vocab_size": 128, "d_model": 64, "n_heads": 4, "d_ff": 176, "max_seq_len": 64,
}


def load(path: Path) -> dict:
    # Deliberately not skipped when missing. A bit identity proof that quietly
    # does not run is worse than one that fails loudly, and the reference is one
    # command away. The references are generated rather than committed, which is
    # the same arrangement test_recurrent.py uses for its own.
    if not path.exists():
        raise FileNotFoundError(
            f"no pointer reference at {path}. Build it with\n"
            f"  uv run python scripts/make_pointer_reference.py --ref-rev c46c8a3"
        )
    return torch.load(path, map_location="cpu", weights_only=False)


# ---------------- flag off: bit identity ----------------


@pytest.mark.parametrize("ref_path", [REF_TINY, REF_RECURRENT])
def test_flag_off_reproduces_saved_logits(ref_path):
    ref = load(ref_path)
    model = TransformerLM(ModelConfig(**ref["model_config"]))
    assert model.cfg.pointer is None
    assert model.pointer is None
    loaded = model.load_state_dict(ref["state_dict"], strict=True)
    assert not loaded.missing_keys and not loaded.unexpected_keys
    model.eval()
    with torch.no_grad():
        logits, loss = model(ref["input"], ref["targets"])
    assert torch.equal(logits, ref["logits"]), (
        f"max abs diff {(logits - ref['logits']).abs().max().item()}"
    )
    assert torch.equal(loss, ref["loss"])


@pytest.mark.parametrize("ref_path", [REF_TINY, REF_RECURRENT])
def test_flag_off_reproduces_saved_init_stream(ref_path):
    """A new dataclass field must not perturb the init RNG stream, or every
    seeded run in the project would drift without the feature being used."""
    ref = load(ref_path)
    torch.manual_seed(ref["seed"])
    model = TransformerLM(ModelConfig(**ref["model_config"]))
    fresh = model.state_dict()
    assert set(fresh) == set(ref["state_dict"])
    for name, tensor in ref["state_dict"].items():
        assert torch.equal(fresh[name], tensor), name


@pytest.mark.skipif(not REF_350M.exists(), reason=f"no 350m reference at {REF_350M}")
def test_flag_off_bit_identical_at_350m():
    ref = load(REF_350M)
    model = TransformerLM(ModelConfig(**ref["model_config"]))
    model.load_state_dict(ref["state_dict"], strict=True)
    model.eval()
    with torch.no_grad():
        logits, _ = model(ref["input"], ref["targets"])
    assert torch.equal(logits, ref["logits"])


def test_flag_on_leaves_every_pre_existing_parameter_alone():
    """The head is built after everything else, so the shared parameters are
    identical value for value at the same seed. Only the new keys are new."""
    ref = load(REF_TINY)
    torch.manual_seed(ref["seed"])
    plain = TransformerLM(ModelConfig(**ref["model_config"])).state_dict()
    torch.manual_seed(ref["seed"])
    with_head = TransformerLM(ModelConfig(**{**ref["model_config"], "pointer": {}})).state_dict()
    added = set(with_head) - set(plain)
    assert not set(plain) - set(with_head)
    assert added == {"pointer.wq.weight", "pointer.wk.weight", "pointer.wv.weight",
                     "pointer.gate_proj.weight", "pointer.gate_proj.bias"}
    for name in plain:
        assert torch.equal(plain[name], with_head[name]), name


def test_flag_on_without_evidence_is_the_plain_forward():
    ref = load(REF_TINY)
    model = TransformerLM(ModelConfig(**{**ref["model_config"], "pointer": {}}))
    model.load_state_dict(ref["state_dict"], strict=False)
    model.eval()
    with torch.no_grad():
        logits, loss = model(ref["input"], ref["targets"])
    assert torch.equal(logits, ref["logits"])
    assert torch.equal(loss, ref["loss"])


# ---------------- flag on: the pointer path ----------------


def test_config_accepts_the_pointer_block_as_a_dict():
    cfg = ModelConfig(n_layers=2, pointer={"d_attn": 16, "gate_bias_init": -1.0}, **TINY)
    assert isinstance(cfg.pointer, PointerConfig)
    model = TransformerLM(cfg)
    assert model.pointer.d_attn == 16
    assert float(model.pointer.gate_proj.bias.detach()) == -1.0
    assert model.describe()["pointer"]["params"] == model.pointer.num_params()
    assert TransformerLM(ModelConfig(n_layers=2, **TINY)).describe()["pointer"] is None


def test_forward_returns_a_normalized_distribution_with_evidence():
    batch = copy_task_batch(n_docs=4)
    torch.manual_seed(0)
    model = TransformerLM(probe_config(pointer={}))
    log_probs, loss = model(batch.input_ids, batch.authored_targets,
                            evidence_positions=batch.evidence_positions,
                            select=batch.authored_positions)
    total = log_probs.exp().sum(-1)
    assert torch.allclose(total, torch.ones_like(total), atol=1e-4)
    assert torch.isfinite(loss)


def test_evidence_positions_gather_the_right_tokens():
    batch = copy_task_batch(n_docs=4)
    torch.manual_seed(0)
    model = TransformerLM(probe_config(pointer={}))
    x = model.trunk(batch.input_ids)
    states, ids, mask = model._resolve_evidence(
        x, batch.input_ids, batch.evidence_positions, None, None, None
    )
    live = batch.evidence_positions >= 0
    assert torch.equal(mask, live)
    assert torch.equal(ids[live], batch.evidence_ids[live])
    for b in range(batch.input_ids.shape[0]):
        for m, pos in enumerate(batch.evidence_positions[b].tolist()):
            if pos >= 0:
                assert torch.equal(states[b, m], x[b, pos])


def test_explicit_evidence_states_may_come_from_elsewhere():
    """The head does not care where the states came from, which is what lets
    the cross-attention model reuse it against an encoded bank."""
    torch.manual_seed(0)
    model = TransformerLM(probe_config(pointer={}))
    idx = torch.randint(0, 256, (2, 12))
    states = torch.randn(2, 5, model.cfg.d_model)
    ids = torch.randint(0, 256, (2, 5))
    log_probs, _ = model(idx, evidence_states=states, evidence_ids=ids)
    total = log_probs.exp().sum(-1)
    assert torch.allclose(total, torch.ones_like(total), atol=1e-4)
    with pytest.raises(ValueError):
        model(idx, evidence_states=states)


def test_trunk_is_what_the_lm_head_reads():
    torch.manual_seed(0)
    model = TransformerLM(probe_config())
    model.eval()
    idx = torch.randint(0, 256, (2, 16))
    with torch.no_grad():
        logits, _ = model(idx)
        assert torch.equal(model.lm_head(model.trunk(idx)), logits)


def test_select_slices_the_plain_path_too():
    torch.manual_seed(0)
    model = TransformerLM(probe_config())
    model.eval()
    idx = torch.randint(0, 256, (2, 16))
    picked = torch.tensor([[3, 9], [1, 15]])
    with torch.no_grad():
        full, _ = model(idx)
        part, _ = model(idx, select=picked)
    for b in range(2):
        for k, t in enumerate(picked[b].tolist()):
            assert torch.equal(part[b, k], full[b, t])


def test_gradient_reaches_the_trunk_through_the_copy_path_alone():
    """With the gate pinned to zero the vocabulary head contributes nothing, so
    any gradient that arrives at the body came through the evidence.

    Only the answer token is supervised here. A gate of exactly zero gives the
    closing <|eot|> a probability of exactly zero, because <|eot|> is not in
    the evidence, and an infinite loss is not a thing to take a gradient of.
    That is a property of the pinned diagnostic gate, not of the learned one,
    which logsigmoid keeps finite at any logit.
    """
    batch = copy_task_batch(n_docs=4)
    targets = batch.authored_targets.clone()
    targets[:, 1:] = -100
    torch.manual_seed(0)
    model = TransformerLM(probe_config(pointer={}))
    _, loss = model(batch.input_ids, targets,
                    evidence_positions=batch.evidence_positions,
                    select=batch.authored_positions, gate_override=0.0)
    loss.backward()
    assert float(model.lm_head.weight.grad.abs().sum()) == 0.0
    assert float(model.pointer.wk.weight.grad.abs().sum()) > 0.0
    assert float(model.blocks[0].attn.wq.weight.grad.abs().sum()) > 0.0


def test_pointer_forward_exposes_the_gate_and_the_copy_distribution():
    batch = copy_task_batch(n_docs=4)
    torch.manual_seed(0)
    model = TransformerLM(probe_config(pointer={}))
    out, loss = model.pointer_forward(
        batch.input_ids, batch.authored_targets,
        evidence_positions=batch.evidence_positions,
        select=batch.authored_positions,
    )
    assert out.gate.shape == (*batch.authored_targets.shape, 1)
    assert out.log_p_copy.shape[-1] == batch.evidence_positions.shape[1]
    assert torch.isfinite(loss)
    with pytest.raises(ValueError):
        TransformerLM(probe_config()).pointer_forward(batch.input_ids)


def test_pointer_and_recurrence_compose():
    cfg = ModelConfig(
        n_layers=4, pointer={},
        recurrent={"prelude_layers": 1, "core_layers": 2, "coda_layers": 1, "loops": 2},
        **TINY,
    )
    torch.manual_seed(0)
    model = TransformerLM(cfg)
    idx = torch.randint(0, TINY["vocab_size"], (2, 16))
    positions = torch.tensor([[0, 1, 2, 3]] * 2)
    log_probs, _ = model(idx, evidence_positions=positions)
    total = log_probs.exp().sum(-1)
    assert torch.allclose(total, torch.ones_like(total), atol=1e-4)
    assert model.describe()["effective_depth"] == 1 + 2 * 2 + 1
