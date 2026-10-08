"""Linear adapters for translating between small and large model latent spaces.

Each adapter is a bias-free linear projection.  Initialization uses Procrustes
alignment on paired activations from both models on the same inputs, falling
back to Kaiming uniform if Procrustes fails.
"""

import torch
import torch.nn as nn
from typing import Optional, Tuple


class LatentAdapter(nn.Module):
    """A single linear projection between two latent spaces."""

    def __init__(self, in_dim: int, out_dim: int):
        super().__init__()
        self.linear = nn.Linear(in_dim, out_dim, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.linear(x.to(self.linear.weight.dtype))


class AdapterPair(nn.Module):
    """Holds both S->L and L->S adapters as a single nn.Module.

    This makes it easy to pass ``adapter_pair.parameters()`` to the optimizer.
    """

    def __init__(self, small_dim: int, large_dim: int):
        super().__init__()
        self.small_to_large = LatentAdapter(small_dim, large_dim)
        self.large_to_small = LatentAdapter(large_dim, small_dim)
        self.small_dim = small_dim
        self.large_dim = large_dim

    def forward_s2l(self, h_small: torch.Tensor) -> torch.Tensor:
        return self.small_to_large(h_small)

    def forward_l2s(self, h_large: torch.Tensor) -> torch.Tensor:
        return self.large_to_small(h_large)


def procrustes_init(
    h_source: torch.Tensor,
    h_target: torch.Tensor,
) -> torch.Tensor:
    """Compute the Procrustes-optimal linear map from source to target space.

    Given paired activation matrices X (n, d_src) and Y (n, d_tgt), finds
    W = argmin ||XW - Y||_F  via the closed-form solution W = X^+ Y
    where X^+ is the Moore-Penrose pseudoinverse.

    For the orthogonal Procrustes special case (d_src == d_tgt), we additionally
    project through SVD to get the nearest orthogonal matrix.  When dimensions
    differ, we use the least-squares solution directly.

    Args:
        h_source: (n_samples, d_source) float32 activation matrix
        h_target: (n_samples, d_target) float32 activation matrix

    Returns:
        W: (d_source, d_target) weight matrix
    """
    X = h_source.float()
    Y = h_target.float()

    # Center both
    X = X - X.mean(dim=0, keepdim=True)
    Y = Y - Y.mean(dim=0, keepdim=True)

    if X.shape[1] == Y.shape[1]:
        # Square case: orthogonal Procrustes via SVD
        M = X.T @ Y  # (d, d)
        U, _, Vt = torch.linalg.svd(M)
        W = U @ Vt  # nearest orthogonal matrix
    else:
        # Rectangular case: least-squares solution
        # W = (X^T X)^{-1} X^T Y = X^+ Y
        W = torch.linalg.lstsq(X, Y).solution

    return W


def initialize_adapters_procrustes(
    adapter_pair: AdapterPair,
    h_small: torch.Tensor,
    h_large: torch.Tensor,
) -> bool:
    """Initialize both adapters using Procrustes alignment.

    Args:
        adapter_pair: The adapter pair to initialize
        h_small: (n_samples, small_dim) activations from the small model
        h_large: (n_samples, large_dim) activations from the large model

    Returns:
        True if Procrustes succeeded, False if we fell back to random init.
    """
    try:
        # S -> L
        W_sl = procrustes_init(h_small, h_large)
        adapter_pair.small_to_large.linear.weight.data.copy_(W_sl.T)

        # L -> S
        W_ls = procrustes_init(h_large, h_small)
        adapter_pair.large_to_small.linear.weight.data.copy_(W_ls.T)

        # DESIGN DECISION: nn.Linear stores weights as (out_features, in_features)
        # and computes output = input @ weight.T.  So if our Procrustes solution
        # W is (in_dim, out_dim), we store W.T as the weight.

        print("[adapters] Procrustes initialization succeeded")
        return True

    except Exception as e:
        print(f"[adapters] Procrustes initialization failed ({e}), "
              f"using default Kaiming init")
        # nn.Linear already uses Kaiming uniform by default
        return False


def collect_activations(
    model,
    tokenizer,
    texts: list[str],
    layer_module: nn.Module,
) -> torch.Tensor:
    """Run the model on a list of texts and collect mean-pooled hidden states
    at a specific layer via a forward hook.

    Returns: (n_texts, hidden_dim) tensor in float32.
    """
    from models.hooks import HiddenStateCapture

    capture = HiddenStateCapture().register(layer_module)
    all_states = []

    model.eval()
    with torch.no_grad():
        for text in texts:
            messages = [{"role": "user", "content": text}]
            inputs = tokenizer.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=True,
                return_dict=True,
                return_tensors="pt",
            ).to(model.device)

            model(**inputs)
            # Mean-pool over sequence length
            h = capture.get(clone=True).float().mean(dim=1)  # (1, hidden_dim)
            all_states.append(h.squeeze(0))

    capture.remove()
    return torch.stack(all_states)  # (n_texts, hidden_dim)
