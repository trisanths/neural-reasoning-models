"""Correctness tests for the Coconut latent-reasoning loop."""

import sys

import torch

sys.path.insert(0, ".")
from src.coconut import Coconut  # noqa: E402
from src.data import Example, Tokenizer  # noqa: E402
from src.dataset import CurriculumConfig, build_batch  # noqa: E402
from src.model import ModelConfig, TinyLM  # noqa: E402


def _setup(n_latent_stage=3):
    torch.manual_seed(0)
    tok = Tokenizer()
    model = TinyLM(
        ModelConfig(vocab_size=len(tok), d_model=64, n_layers=3, n_heads=4, max_len=128)
    )
    model.eval()
    exs = [
        Example(
            question="every wumpus is a yumpus . alice is a wumpus . is alice a yumpus or kerpus ?",
            steps=["alice is a wumpus .", "every wumpus is a yumpus ."],
            answer="alice is a yumpus .",
            n_hops=1,
        ),
        Example(
            question="every bompus is a felpus . bob is a bompus . is bob a felpus or jompus ?",
            steps=["bob is a bompus .", "every bompus is a felpus ."],
            answer="bob is a felpus .",
            n_hops=1,
        ),
    ]
    cfg = CurriculumConfig(max_latent_stage=n_latent_stage, c_thought=1)
    return tok, model, exs, cfg


def test_multipass_matches_single_forward():
    """The incremental KV-cached passes must equal one forward over the
    assembled embedding sequence with thoughts spliced in."""
    tok, model, exs, cfg = _setup()
    batch = build_batch(exs, tok, stage=2, cfg=cfg)
    coco = Coconut(model)
    with torch.no_grad():
        _, logits, thoughts = coco(batch)

        # Rebuild the full input embeddings using the recorded thoughts.
        emb = model.wte(batch.input_ids)
        ls = batch.latent_start
        for j, th in enumerate(thoughts):
            emb[:, ls + j] = th
        ref = model(
            inputs_embeds=emb,
            attention_mask=batch.attention_mask,
            position_ids=batch.position_ids,
        ).logits
    assert logits.shape == ref.shape
    assert torch.allclose(logits, ref, atol=1e-4), (logits - ref).abs().max()


def test_stage_zero_is_plain_cot():
    """Stage 0 uses no latents and must contain the full textual chain."""
    tok, model, exs, cfg = _setup()
    batch = build_batch(exs, tok, stage=0, cfg=cfg)
    assert batch.n_latent == 0
    text = tok.decode(batch.input_ids[0].tolist())
    assert "alice is a wumpus" in text and "every wumpus is a yumpus" in text


def test_final_stage_has_no_textual_steps():
    """Past max_latent_stage the chain is gone and only latents remain."""
    tok, model, exs, cfg = _setup(n_latent_stage=2)
    batch = build_batch(exs, tok, stage=99, cfg=cfg)
    assert batch.n_latent == 2
    supervised = batch.labels[0][batch.labels[0] != -100]
    assert tok.decode(supervised.tolist()).strip().startswith("alice is a yumpus")


def test_thoughts_actually_feed_back():
    """Latent output must differ from feeding the raw <latent> embedding,
    otherwise the feedback loop is a no-op."""
    tok, model, exs, cfg = _setup()
    batch = build_batch(exs, tok, stage=2, cfg=cfg)
    coco = Coconut(model)
    with torch.no_grad():
        _, logits, _ = coco(batch)
        naive = model(
            input_ids=batch.input_ids,
            attention_mask=batch.attention_mask,
            position_ids=batch.position_ids,
        ).logits
    assert not torch.allclose(logits, naive, atol=1e-3)


def test_labels_mask_question_and_latents():
    tok, model, exs, cfg = _setup()
    batch = build_batch(exs, tok, stage=2, cfg=cfg)
    assert (batch.labels[:, : batch.answer_start] == -100).all()
    assert (batch.labels[:, batch.answer_start :] != -100).any()


def test_generation_shape_and_eos():
    tok, model, exs, cfg = _setup()
    batch = build_batch(exs, tok, stage=99, cfg=cfg, for_generation=True)
    coco = Coconut(model)
    out = coco.generate(batch, max_new_tokens=6, eos_id=tok.eos_id)
    assert out.shape == (2, 6)


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"PASS {name}")
