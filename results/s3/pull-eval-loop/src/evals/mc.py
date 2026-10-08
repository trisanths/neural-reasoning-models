"""Multiple choice scoring by language model likelihood.

Each option is appended to the shared context and scored by the summed
negative log likelihood of the option tokens alone. The option with the
lowest NLL wins. Ties break toward the lower index, so scoring is
deterministic for a fixed model and inputs.
"""

import torch
import torch.nn.functional as F


def option_nll(model, context_ids, option_ids, device) -> float:
    """Summed NLL of option_ids given context_ids under the model."""
    if not option_ids:
        raise ValueError("option has no tokens")
    max_len = model.cfg.max_seq_len
    ids = list(context_ids) + list(option_ids)
    if len(ids) > max_len:
        # Keep the tail: the question and options sit at the end.
        ids = ids[-max_len:]
    n_opt = min(len(option_ids), len(ids) - 1)
    x = torch.tensor([ids], dtype=torch.long, device=device)
    with torch.no_grad():
        logits, _ = model(x)
    logprobs = F.log_softmax(logits[0, :-1].float(), dim=-1)
    targets = x[0, 1:]
    tail = logprobs[-n_opt:].gather(1, targets[-n_opt:].unsqueeze(1))
    return float(-tail.sum().item())


def score_mc(model, tokenizer, context_ids, options, device):
    """Return (best_index, per option NLL list) for text options."""
    nlls = []
    for option in options:
        ids = tokenizer.encode(option)
        if not ids:
            ids = tokenizer.encode(" " + option)
        nlls.append(option_nll(model, context_ids, ids, device))
    best = min(range(len(nlls)), key=lambda i: (nlls[i], i))
    return best, nlls


def load_checkpoint_model(ckpt_path, device):
    """Rebuild the TransformerLM stored in a trainer checkpoint."""
    from src.train.model import ModelConfig, TransformerLM

    state = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    model = TransformerLM(ModelConfig(**state["config"]["model"]))
    model.load_state_dict(state["model"])
    model.to(device).eval()
    return model, state
