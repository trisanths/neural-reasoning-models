import torch

from src.train.model import ModelConfig, TransformerLM

TINY = ModelConfig(
    vocab_size=128, d_model=64, n_layers=2, n_heads=4, d_ff=176, max_seq_len=64
)


def test_forward_shapes():
    model = TransformerLM(TINY)
    idx = torch.randint(0, TINY.vocab_size, (3, 32))
    logits, loss = model(idx)
    assert logits.shape == (3, 32, TINY.vocab_size)
    assert loss is None


def test_forward_with_targets_and_backward():
    torch.manual_seed(0)
    model = TransformerLM(TINY)
    idx = torch.randint(0, TINY.vocab_size, (2, 16))
    targets = torch.randint(0, TINY.vocab_size, (2, 16))
    logits, loss = model(idx, targets)
    assert logits.shape == (2, 16, TINY.vocab_size)
    assert loss.dim() == 0
    assert torch.isfinite(loss)
    loss.backward()
    for name, param in model.named_parameters():
        assert param.grad is not None, name
        assert torch.isfinite(param.grad).all(), name


def test_untied_embeddings():
    model = TransformerLM(TINY)
    assert model.tok_emb.weight.data_ptr() != model.lm_head.weight.data_ptr()


def test_rejects_overlong_sequence():
    model = TransformerLM(TINY)
    idx = torch.randint(0, TINY.vocab_size, (1, TINY.max_seq_len + 1))
    try:
        model(idx)
        raised = False
    except ValueError:
        raised = True
    assert raised


def test_variable_lengths_consistent():
    torch.manual_seed(0)
    model = TransformerLM(TINY)
    model.eval()
    idx = torch.randint(0, TINY.vocab_size, (1, 24))
    with torch.no_grad():
        full, _ = model(idx)
        prefix, _ = model(idx[:, :10])
    # Causal masking means a prefix must produce the same logits as the same
    # positions inside a longer sequence.
    assert torch.allclose(full[:, :10], prefix, atol=1e-4)
