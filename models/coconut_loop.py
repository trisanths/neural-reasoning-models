"""Coconut latent reasoning loop adapted for cross-model tail-layer iteration.

Two modes:
  - Tail loop (default): run one injected full pass, then iterate only the
    large model's tail layers for ``num_iters`` recurrent refinement steps.
  - Full loop (ablation): re-run the entire large model each iteration.
"""

import torch
import torch.nn as nn
from typing import Optional, List

from config import ModelConfig, resolve_module


class CoconutTailLoop:
    """Runs the Coconut continuous-thought loop over the large model's tail layers.

    This is a plain class (not nn.Module) because it does NOT own the large
    model; it borrows references to specific layers and the final norm. The
    large model stays frozen and unmodified.
    """

    def __init__(
        self,
        large_model: nn.Module,
        large_config: ModelConfig,
        inject_layer: int,
        num_iters: int = 6,
        full_loop: bool = False,
    ):
        self.large_model = large_model
        self.large_config = large_config
        self.inject_layer = inject_layer
        self.num_iters = num_iters
        self.full_loop = full_loop

        # Resolve and cache references to the modules we need.
        self._layers: nn.ModuleList = resolve_module(large_model, large_config.layers_path)
        self._norm: nn.Module = resolve_module(large_model, large_config.norm_path)
        self._embed: nn.Module = resolve_module(large_model, large_config.embed_path)
        self._rotary_emb: nn.Module = resolve_module(large_model, large_config.rotary_path)

        # inject_layer uses the HF hidden-state convention, so subtract 1 to
        # convert to the actual block index where the translated state enters.
        self._tail_start = inject_layer - 1
        self._tail_layers = list(range(self._tail_start, large_config.num_layers))

        # Cache layer_types once; fall back to all-full-attention for models
        # that pre-date the mixed-attention Qwen2.5 config field.
        config = large_model.config
        if hasattr(config, "layer_types"):
            self._layer_types: List[str] = list(config.layer_types)
        else:
            self._layer_types = ["full_attention"] * large_config.num_layers

        self._sliding_window: Optional[int] = getattr(config, "sliding_window", None)

    # ------------------------------------------------------------------
    # Mask construction — pure PyTorch, no transformers internals
    # ------------------------------------------------------------------

    def _build_attention_mask_mapping(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor],
    ) -> dict:
        """Build a {layer_type -> 4-D float mask} dict for the large model layers.

        We construct the masks ourselves rather than calling transformers'
        internal masking utilities, whose signatures change across versions.

        Shape: (batch, 1, seq_len, seq_len), additive float mask convention
        (0.0 = attend, large negative = do not attend).
        """
        batch, seq_len, _ = hidden_states.shape
        device = hidden_states.device
        dtype = hidden_states.dtype
        neg_inf = torch.finfo(dtype).min / 2

        # --- causal (upper-triangle) mask ---
        # triu(diagonal=1) gives True for future positions → fill with neg_inf
        causal_2d = torch.triu(
            torch.ones(seq_len, seq_len, device=device, dtype=torch.bool), diagonal=1
        )
        full_mask = torch.zeros(batch, 1, seq_len, seq_len, device=device, dtype=dtype)
        full_mask.masked_fill_(causal_2d, neg_inf)

        # --- padding mask (if provided) ---
        if attention_mask is not None and attention_mask.ndim == 2:
            # (batch, seq_len) → (batch, 1, 1, seq_len): mask padding tokens as keys
            pad_mask = attention_mask[:, None, None, :].to(dtype=torch.bool)
            full_mask = full_mask.masked_fill(~pad_mask, neg_inf)

        mask_mapping = {"full_attention": full_mask}

        # --- sliding-window mask (Qwen2.5 layers that use it) ---
        if "sliding_attention" in self._layer_types and self._sliding_window is not None:
            window = self._sliding_window
            rows = torch.arange(seq_len, device=device)
            cols = torch.arange(seq_len, device=device)
            # Positions too far in the past: row - col >= window
            beyond_window = (rows[:, None] - cols[None, :]) >= window
            sliding_mask = full_mask.clone()
            sliding_mask.masked_fill_(beyond_window, neg_inf)
            mask_mapping["sliding_attention"] = sliding_mask

        return mask_mapping

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_position_ids(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """Build position ids compatible with right-padded causal inputs."""
        if attention_mask is not None and attention_mask.ndim == 2:
            position_ids = attention_mask.long().cumsum(dim=-1) - 1
            position_ids.masked_fill_(attention_mask == 0, 0)
            return position_ids

        batch_size, seq_len = input_ids.shape
        return torch.arange(seq_len, device=input_ids.device).unsqueeze(0).expand(batch_size, -1)

    def _apply_injection(
        self,
        hidden_states: torch.Tensor,
        injected_state: torch.Tensor,
        injection_mode: str,
    ) -> torch.Tensor:
        """Inject the translated state, aligning on the sequence tail if needed."""
        injected = injected_state.to(device=hidden_states.device, dtype=hidden_states.dtype)

        if injected.shape[1] == hidden_states.shape[1]:
            if injection_mode == "replace":
                return injected
            return hidden_states + injected

        overlap = min(hidden_states.shape[1], injected.shape[1])
        target = slice(hidden_states.shape[1] - overlap, hidden_states.shape[1])
        source = slice(injected.shape[1] - overlap, injected.shape[1])
        hidden_states = hidden_states.clone()

        if injection_mode == "replace":
            hidden_states[:, target, :] = injected[:, source, :]
        else:
            hidden_states[:, target, :] = hidden_states[:, target, :] + injected[:, source, :]

        return hidden_states

    def _run_layers(
        self,
        layer_indices: List[int],
        hidden_states: torch.Tensor,
        attention_mask_mapping: dict,
        position_ids: torch.Tensor,
        position_embeddings,
    ) -> torch.Tensor:
        """Run a subset of large-model decoder layers on the hidden state."""
        for layer_idx in layer_indices:
            layer = self._layers[layer_idx]
            layer_type = self._layer_types[layer_idx]
            layer_out = layer(
                hidden_states,
                attention_mask=attention_mask_mapping[layer_type],
                position_ids=position_ids,
                past_key_values=None,
                use_cache=False,
                position_embeddings=position_embeddings,
            )
            hidden_states = layer_out[0] if isinstance(layer_out, tuple) else layer_out

        return hidden_states

    # ------------------------------------------------------------------
    # Main entry points
    # ------------------------------------------------------------------

    def initial_pass(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        injected_state: Optional[torch.Tensor] = None,
        injection_mode: str = "add",
    ) -> torch.Tensor:
        """Run one injected full forward pass through the large model."""
        hidden_states = self._embed(input_ids)
        position_ids = self._build_position_ids(input_ids, attention_mask)
        attention_mask_mapping = self._build_attention_mask_mapping(hidden_states, attention_mask)
        position_embeddings = self._rotary_emb(hidden_states, position_ids)

        for layer_idx in range(self.large_config.num_layers):
            if layer_idx == self._tail_start and injected_state is not None:
                hidden_states = self._apply_injection(
                    hidden_states, injected_state, injection_mode
                )

            layer = self._layers[layer_idx]
            layer_type = self._layer_types[layer_idx]
            layer_out = layer(
                hidden_states,
                attention_mask=attention_mask_mapping[layer_type],
                position_ids=position_ids,
                past_key_values=None,
                use_cache=False,
                position_embeddings=position_embeddings,
            )
            hidden_states = layer_out[0] if isinstance(layer_out, tuple) else layer_out

        return self._norm(hidden_states)

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        injected_state: Optional[torch.Tensor] = None,
        injection_mode: str = "add",
    ) -> torch.Tensor:
        """Run the full Coconut loop: initial pass + recurrent refinement."""
        with torch.no_grad():
            hidden_states = self.initial_pass(
                input_ids, attention_mask, injected_state, injection_mode
            )
            position_ids = self._build_position_ids(input_ids, attention_mask)
            # Mask and position embeddings are the same for every loop iteration
            # (same sequence length, same positions).
            attention_mask_mapping = self._build_attention_mask_mapping(
                hidden_states, attention_mask
            )
            position_embeddings = self._rotary_emb(hidden_states, position_ids)
            current_state = hidden_states

            for _ in range(self.num_iters):
                layer_indices = (
                    list(range(self.large_config.num_layers))
                    if self.full_loop
                    else self._tail_layers
                )
                # Reuse the original token positions because the loop feeds back
                # a full-sequence latent state rather than appending a fresh token.
                h = self._run_layers(
                    layer_indices,
                    current_state,
                    attention_mask_mapping,
                    position_ids,
                    position_embeddings,
                )
                current_state = self._norm(h)

        return current_state
