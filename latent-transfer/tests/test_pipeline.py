"""Correctness tests for the cross-model handoff."""

import sys

import torch

sys.path.insert(0, ".")
from src.data import Example, Tokenizer  # noqa: E402
from src.dataset import CurriculumConfig, build_batch  # noqa: E402
from src.model import ModelConfig, TinyLM  # noqa: E402
from src.pipeline import CrossModelPipeline  # noqa: E402
from src.projectors import Projector, apply_lora  # noqa: E402

D_S, D_B = 32, 48


def _setup(k=3):
    torch.manual_seed(0)
    tok = Tokenizer()
    small = TinyLM(ModelConfig(vocab_size=len(tok), d_model=D_S, n_layers=2, n_heads=4, max_len=128))
    big = TinyLM(ModelConfig(vocab_size=len(tok), d_model=D_B, n_layers=3, n_heads=4, max_len=128))
    pipe = CrossModelPipeline(small, big, Projector(D_S, D_B), Projector(D_B, D_S))
    exs = [
        Example(
            question="every wumpus is a yumpus . alice is a wumpus . is alice a yumpus or kerpus ?",
            steps=["alice is a wumpus .", "every wumpus is a yumpus ."],
            answer="alice is a yumpus .",
            n_hops=1,
        )
    ] * 2
    cfg = CurriculumConfig(max_latent_stage=k, c_thought=1)
    batch = build_batch(exs, tok, stage=99, cfg=cfg)
    return tok, pipe, batch, cfg


def test_forward_shapes_and_loss():
    tok, pipe, batch, _ = _setup()
    loss, logits, thoughts = pipe(batch, return_thoughts=True)
    assert logits.shape[:2] == batch.input_ids.shape
    assert len(thoughts) == batch.n_latent
    assert thoughts[0].shape == (2, D_B)
    assert torch.isfinite(loss)


def test_gradients_reach_both_projectors():
    """Both directions of the handoff must be trainable from the answer loss."""
    _, pipe, batch, _ = _setup()
    loss, _, _ = pipe(batch)
    loss.backward()
    up = pipe.proj_up.net.weight.grad
    down = pipe.proj_down.net.weight.grad
    assert up is not None and up.abs().sum() > 0, "no gradient to up-projector"
    assert down is not None and down.abs().sum() > 0, "no gradient to down-projector"


def test_big_model_is_load_bearing():
    """Perturbing the big model must change the pipeline output.

    If it does not, the big model contributes nothing and any accuracy gain
    would be coming from the small model plus projectors alone.
    """
    _, pipe, batch, _ = _setup()
    with torch.no_grad():
        before = pipe(batch)[1].clone()
        for p in pipe.big.parameters():
            p.add_(torch.randn_like(p) * 0.5)
        after = pipe(batch)[1]
    assert not torch.allclose(before, after, atol=1e-4), "big model has no effect"


def test_thoughts_differ_across_latent_steps():
    """A degenerate pipeline emits the same vector at every step."""
    _, pipe, batch, _ = _setup()
    with torch.no_grad():
        _, _, thoughts = pipe(batch, return_thoughts=True)
    for j in range(1, len(thoughts)):
        assert not torch.allclose(thoughts[0], thoughts[j], atol=1e-6)


def test_generation_runs():
    tok, pipe, _, cfg = _setup()
    exs = [
        Example(
            question="every wumpus is a yumpus . alice is a wumpus . is alice a yumpus or kerpus ?",
            steps=["alice is a wumpus .", "every wumpus is a yumpus ."],
            answer="alice is a yumpus .",
            n_hops=1,
        )
    ] * 2
    gbatch = build_batch(exs, tok, stage=99, cfg=cfg, for_generation=True)
    out = pipe.generate(gbatch, max_new_tokens=6, eos_id=tok.eos_id)
    assert out.shape == (2, 6)


def test_compressed_handoff_limits_big_model_context():
    """With n_message set, the big model must only ever see m + k positions.

    This is what makes the pipeline cheaper than running the big model
    directly, so it is checked structurally rather than trusted.
    """
    tok, pipe, batch, _ = _setup()
    m = 4
    pipe.n_message = m
    seen = {}
    orig = pipe.big.forward

    def spy(*args, **kwargs):
        out = orig(*args, **kwargs)
        kv = out.past_key_values
        seen["max_ctx"] = max(seen.get("max_ctx", 0), kv[0][0].shape[2])
        return out

    pipe.big.forward = spy
    loss, _, thoughts = pipe(batch, return_thoughts=True)
    pipe.big.forward = orig

    assert seen["max_ctx"] == m + batch.n_latent, seen
    assert seen["max_ctx"] < batch.latent_start, "compression did not shrink context"
    assert torch.isfinite(loss)
    assert len(thoughts) == batch.n_latent


def test_compressed_handoff_trains():
    _, pipe, batch, _ = _setup()
    pipe.n_message = 4
    loss, _, _ = pipe(batch)
    loss.backward()
    assert pipe.proj_up.net.weight.grad.abs().sum() > 0
    assert pipe.proj_down.net.weight.grad.abs().sum() > 0


def test_lora_freezes_backbone():
    torch.manual_seed(0)
    tok = Tokenizer()
    m = TinyLM(ModelConfig(vocab_size=len(tok), d_model=D_S, n_layers=2, n_heads=4, max_len=128))
    params = apply_lora(m, rank=4)
    assert len(params) > 0
    trainable = [p for p in m.parameters() if p.requires_grad]
    # Only LoRA a/b matrices should be trainable.
    assert sum(p.numel() for p in trainable) == sum(p.numel() for p in params)


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"PASS {name}")
