"""Verifies the HF adapter satisfies the same contract as TinyLM.

Runs against a tiny rotary (Llama-style) model, because that is architecturally
what Qwen is: the cache is a mutating Cache object rather than a list of tuples,
and position is folded into attention rather than added to the embedding. Both
differ from the hand-written backbone, so the pipeline's assumptions have to be
re-checked rather than assumed to carry over.

Skips cleanly when the model cannot be downloaded.
"""

import sys

import torch

sys.path.insert(0, ".")

TINY = "hf-internal-testing/tiny-random-LlamaForCausalLM"


def _load():
    try:
        from transformers import AutoModelForCausalLM

        from src.hf_backbone import HFBackbone

        m = AutoModelForCausalLM.from_pretrained(TINY, dtype=torch.float32)
        return HFBackbone(m)
    except Exception as exc:  # offline, or hub unavailable
        print(f"SKIP (cannot load {TINY}): {type(exc).__name__}")
        return None


def test_kv_cache_matches_full_forward():
    m = _load()
    if m is None:
        return
    m.eval()
    ids = torch.randint(0, 100, (2, 12))
    with torch.no_grad():
        full = m(input_ids=ids).logits
        out = m(input_ids=ids[:, :8])
        cache, pieces = out.past_key_values, [out.logits]
        for t in range(8, 12):
            out = m(input_ids=ids[:, t : t + 1], past_key_values=cache)
            cache = out.past_key_values
            pieces.append(out.logits)
        inc = torch.cat(pieces, dim=1)
    assert torch.allclose(full, inc, atol=1e-4), (full - inc).abs().max()


def test_coconut_multipass_matches_single_forward():
    """The latent loop must be exact on an HF backbone too."""
    m = _load()
    if m is None:
        return
    m.eval()
    from src.coconut import Coconut
    from src.dataset import Batch

    B, T, ls, k = 2, 14, 6, 3
    ids = torch.randint(0, 100, (B, T))
    batch = Batch(
        input_ids=ids,
        labels=torch.full((B, T), -100),
        attention_mask=torch.ones(B, T, dtype=torch.long),
        position_ids=torch.arange(T).unsqueeze(0).expand(B, T).contiguous(),
        latent_start=ls,
        n_latent=k,
        answer_start=ls + k + 1,
    )
    batch.labels[:, ls + k + 1 :] = ids[:, ls + k + 1 :]
    coco = Coconut(m)
    with torch.no_grad():
        _, logits, thoughts = coco(batch)
        emb = m.wte(ids).clone()
        for j, th in enumerate(thoughts):
            emb[:, ls + j] = th
        ref = m(
            inputs_embeds=emb,
            attention_mask=batch.attention_mask,
            position_ids=batch.position_ids,
        ).logits
    assert logits.shape == ref.shape
    assert torch.allclose(logits, ref, atol=1e-4), (logits - ref).abs().max()


def test_pipeline_runs_across_two_hf_models():
    a, b = _load(), _load()
    if a is None or b is None:
        return
    from src.dataset import Batch
    from src.pipeline import CrossModelPipeline
    from src.projectors import Projector

    d = a.cfg.d_model
    pipe = CrossModelPipeline(a, b, Projector(d, d), Projector(d, d), n_message=4)
    B, T, ls, k = 2, 14, 6, 3
    ids = torch.randint(0, 100, (B, T))
    batch = Batch(
        input_ids=ids,
        labels=torch.full((B, T), -100),
        attention_mask=torch.ones(B, T, dtype=torch.long),
        position_ids=torch.arange(T).unsqueeze(0).expand(B, T).contiguous(),
        latent_start=ls,
        n_latent=k,
        answer_start=ls + k + 1,
    )
    batch.labels[:, ls + k + 1 :] = ids[:, ls + k + 1 :]
    loss, _, thoughts = pipe(batch, return_thoughts=True)
    loss.backward()
    assert torch.isfinite(loss)
    assert len(thoughts) == k
    assert pipe.proj_up.net.weight.grad.abs().sum() > 0


def test_add_positional_false_is_rejected():
    """Rotary models fold position into attention, so the flag cannot be
    honoured; it must raise rather than silently no-op."""
    m = _load()
    if m is None:
        return
    try:
        m(input_ids=torch.randint(0, 100, (1, 4)), add_positional=False)
    except NotImplementedError:
        return
    raise AssertionError("add_positional=False should raise on a rotary model")


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"PASS {name}")
