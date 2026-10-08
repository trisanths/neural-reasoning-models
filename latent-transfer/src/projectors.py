"""Maps between the residual streams of two independently trained models.

The model-stitching literature (Bansal et al. 2021; Chen et al. 2025) finds that
a simple affine map suffices to move features between networks, so ``linear`` is
the default and the MLP variant exists to test whether extra capacity helps.

``rms_match`` optionally rescales the projected vector to the target model's
typical activation magnitude. Two models trained separately have no reason to
share a scale, and feeding a badly-scaled vector into a LayerNorm-based network
lands it far outside the distribution the network was trained on.
"""

from __future__ import annotations

import torch
import torch.nn as nn


class Projector(nn.Module):
    def __init__(
        self,
        d_in: int,
        d_out: int,
        kind: str = "linear",
        hidden_mult: int = 4,
        rms_match: bool = True,
        init_identity: bool = False,
        target_rms: float | None = None,
    ) -> None:
        super().__init__()
        self.kind = kind
        if kind == "linear":
            self.net: nn.Module = nn.Linear(d_in, d_out)
        elif kind == "mlp":
            self.net = nn.Sequential(
                nn.Linear(d_in, hidden_mult * d_in),
                nn.GELU(),
                nn.Linear(hidden_mult * d_in, d_out),
            )
        else:
            raise ValueError(f"unknown projector kind {kind!r}")

        self.rms_match = rms_match
        # Learned output scale. The initial value matters far more than it looks:
        # a 0.5B's final hidden states have RMS ~9.4 while a 7B's input
        # embeddings have RMS ~0.0156, a 300x gap. Starting at 1.0 therefore
        # feeds the receiver vectors ~64x larger than anything it saw in
        # training, which is the out-of-distribution regime where frozen
        # receivers collapse (cf. arXiv 2606.03280, reporting translated norms
        # of 0.85 against a native 68.70). Pass the receiver's measured
        # embedding RMS so the projector starts in the right neighbourhood.
        init = 1.0 if target_rms is None else float(target_rms)
        self.out_scale = nn.Parameter(torch.full((1,), init)) if rms_match else None

        if init_identity and kind == "linear" and d_in == d_out:
            nn.init.eye_(self.net.weight)
            nn.init.zeros_(self.net.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # The projector sits between two backbones that may run in bf16 while
        # its own parameters stay in fp32. Keeping the parameters in the higher
        # precision matters: this is the only module being trained from scratch
        # here, and the RMS normalisation below is numerically poor in bf16.
        # So cast around the computation rather than demoting the weights.
        param_dtype = next(self.parameters()).dtype
        in_dtype = x.dtype
        y = self.net(x.to(param_dtype))
        if self.rms_match:
            rms = y.pow(2).mean(-1, keepdim=True).clamp_min(1e-8).sqrt()
            y = y / rms * self.out_scale
        return y.to(in_dtype)


class LoRALinear(nn.Module):
    """Low-rank adapter wrapping a frozen linear layer."""

    def __init__(self, base: nn.Linear, rank: int = 8, alpha: float = 16.0) -> None:
        super().__init__()
        self.base = base
        for p in self.base.parameters():
            p.requires_grad = False
        self.a = nn.Parameter(torch.zeros(rank, base.in_features))
        self.b = nn.Parameter(torch.zeros(base.out_features, rank))
        nn.init.normal_(self.a, std=0.02)
        self.scale = alpha / rank

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.base(x) + (x @ self.a.T @ self.b.T) * self.scale


def apply_lora(model: nn.Module, rank: int = 8, alpha: float = 16.0) -> list[nn.Parameter]:
    """Wraps attention/MLP projections in LoRA adapters; returns trainable params.

    Freezes everything else, so the backbone keeps the behaviour it learned
    standalone while gaining just enough flexibility to consume foreign thoughts.
    """
    for p in model.parameters():
        p.requires_grad = False
    targets: list[tuple[nn.Module, str, nn.Linear]] = []
    for module in model.modules():
        for name, child in module.named_children():
            if isinstance(child, nn.Linear):
                targets.append((module, name, child))
    params: list[nn.Parameter] = []
    for parent, name, lin in targets:
        lora = LoRALinear(lin, rank=rank, alpha=alpha)
        # Match the layer being wrapped. Adapters are created fresh, so without
        # this they land on CPU whenever the model has already been moved to a
        # device, and the first matmul fails on mixed devices.
        lora = lora.to(device=lin.weight.device, dtype=lin.weight.dtype)
        setattr(parent, name, lora)
        params += [lora.a, lora.b]
    return params
