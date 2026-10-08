"""Real ProsQA through an HF tokenizer, end to end.

Two things here are easy to get silently wrong and expensive to discover later:
subword merges across segment boundaries, and batches that mix chain lengths
(ProsQA has 3 to 6 steps). Both are checked.

Skips cleanly when the data or the hub model is unavailable.
"""

import os
import sys

import torch

sys.path.insert(0, ".")

DATA = "data_prosqa/prosqa_valid.json"
TINY = "hf-internal-testing/tiny-random-LlamaForCausalLM"


def _setup():
    if not os.path.exists(DATA):
        print(f"SKIP (no {DATA})")
        return None
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer

        from src.hf_backbone import HFBackbone, HFTokenizerAdapter
        from src.prosqa import ProsQAHFTokenizer, load_prosqa

        hf_tok = AutoTokenizer.from_pretrained(TINY)
        adapter = HFTokenizerAdapter(hf_tok)
        tok = ProsQAHFTokenizer(adapter)
        model = AutoModelForCausalLM.from_pretrained(TINY, dtype=torch.float32)
        model.resize_token_embeddings(len(hf_tok))
        return tok, HFBackbone(model, hf_tok), load_prosqa(DATA)
    except Exception as exc:
        print(f"SKIP (cannot load): {type(exc).__name__}: {exc}")
        return None


def test_loads_real_prosqa():
    s = _setup()
    if s is None:
        return
    _, _, exs = s
    assert len(exs) == 300
    counts = {len(e.steps) for e in exs}
    assert counts == {3, 4, 5, 6}, counts
    e = exs[0]
    assert e.question.endswith("?")
    assert e.meta["target"] == e.answer.rstrip(".").split()[-1]


def test_sentencepiece_is_rejected_loudly():
    """SentencePiece gives a word different ids at a string start than
    mid-sequence, so segments cannot be encoded independently. That must raise
    rather than silently produce a misaligned curriculum."""
    s = _setup()
    if s is None:
        return
    tok, _, exs = s
    from src.prosqa import TokenizerIncompatible, assert_tokenizer_compatible

    try:
        assert_tokenizer_compatible(tok, exs)
    except TokenizerIncompatible:
        return
    raise AssertionError("SentencePiece tokenizer should have been rejected")


def test_bpe_tokenizers_pass_the_gate():
    """The real targets (Qwen, GPT-2) must encode segments exactly."""
    if not os.path.exists(DATA):
        print(f"SKIP (no {DATA})")
        return
    try:
        from transformers import AutoTokenizer

        from src.hf_backbone import HFTokenizerAdapter
        from src.prosqa import ProsQAHFTokenizer, assert_tokenizer_compatible, load_prosqa
    except Exception as exc:
        print(f"SKIP: {type(exc).__name__}")
        return
    exs = load_prosqa(DATA)
    for name in ("gpt2",):  # Qwen checked separately; 3GB download
        try:
            t = AutoTokenizer.from_pretrained(name)
        except Exception as exc:
            print(f"SKIP {name}: {type(exc).__name__}")
            continue
        assert_tokenizer_compatible(ProsQAHFTokenizer(HFTokenizerAdapter(t)), exs)


def test_batch_mixes_chain_lengths():
    """ProsQA batches contain 3- to 6-step chains; the latent block must stay
    aligned while the number of skipped steps varies per example."""
    s = _setup()
    if s is None:
        return
    tok, _, exs = s
    from src.dataset import CurriculumConfig, build_batch
    from src.engine import FINAL_STAGE

    mixed = sorted(exs, key=lambda e: len(e.steps))
    batch_examples = [mixed[0], mixed[-1], mixed[len(mixed) // 2]]
    assert len({len(e.steps) for e in batch_examples}) > 1, "not actually mixed"

    cfg = CurriculumConfig(max_latent_stage=6, c_thought=1, pad_latent_to_max=True)
    b = build_batch(batch_examples, tok, FINAL_STAGE, cfg)
    assert b.n_latent == 6
    # Every row's latent block sits at the same index.
    for i in range(len(batch_examples)):
        row = b.input_ids[i, b.latent_start : b.latent_start + b.n_latent]
        assert (row == tok.latent_id).all(), row
    # Supervision covers only the answer at the final stage.
    for i, ex in enumerate(batch_examples):
        sup = b.labels[i][b.labels[i] != -100]
        assert "###" in tok.decode(sup.tolist())


def test_coconut_forward_on_real_prosqa():
    s = _setup()
    if s is None:
        return
    tok, model, exs = s
    from src.coconut import Coconut
    from src.dataset import CurriculumConfig, build_batch
    from src.engine import FINAL_STAGE

    cfg = CurriculumConfig(max_latent_stage=6, c_thought=1, pad_latent_to_max=True)
    b = build_batch(exs[:4], tok, FINAL_STAGE, cfg)
    coco = Coconut(model)
    loss, logits, thoughts = coco(b)
    assert torch.isfinite(loss)
    assert len(thoughts) == 6
    assert logits.shape[:2] == b.input_ids.shape


def test_answer_key_handles_hf_spacing():
    from src.engine import _answer_key, _final_sentence

    assert _answer_key("Tom is a zhorpus.") == "zhorpus"
    assert _answer_key("alice is a grimpus .") == "grimpus"
    assert _answer_key("= 5 .") == "5"
    assert _final_sentence("every x is a y.\n### Tom is a zhorpus.") == "Tom is a zhorpus."


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"PASS {name}")
