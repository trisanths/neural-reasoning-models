"""Coconut latent reasoning loop adapted for cross-model tail-layer iteration.

Two modes:
  - Tail loop (default): run one injected full pass, then iterate only the
    large model's tail layers for ``num_iters`` recurrent refinement steps.
  - Full loop (ablation): re-run the entire large model each iteration.
"""

import torch
import torch.nn as nn
from typing import Optional, List

from transformers.masking_utils import (
    create_causal_mask,
    create_sliding_window_causal_mask,
)

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

    def _prepare_attention_mask_mapping(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor],
        position_ids: torch.Tensor,
    ):
        """Match the mask preparation logic used by the HF Qwen2 model."""
        if isinstance(attention_mask, dict):
            return attention_mask

        seq_len = hidden_states.shape[1]
        cache_position = torch.arange(seq_len, device=hidden_states.device)
        mask_kwargs = {
            "config": self.large_model.config,
            "inputs_embeds": hidden_states,
            "attention_mask": attention_mask,
            "cache_position": cache_position,
            "past_key_values": None,
            "position_ids": position_ids,
        }
        mask_mapping = {
            "full_attention": create_causal_mask(**mask_kwargs),
        }
        if "sliding_attention" in self.large_model.config.layer_types:
            mask_mapping["sliding_attention"] = create_sliding_window_causal_mask(**mask_kwargs)
        return mask_mapping

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
        attention_mask: Optional[torch.Tensor],
        position_ids: torch.Tensor,
    ) -> torch.Tensor:
        """Run a subset of large-model decoder layers on the hidden state."""
        attention_mask_mapping = self._prepare_attention_mask_mapping(
            hidden_states, attention_mask, position_ids
        )
        position_embeddings = self._rotary_emb(hidden_states, position_ids)

        for layer_idx in layer_indices:
            layer = self._layers[layer_idx]
            layer_type = self.large_model.config.layer_types[layer_idx]
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
        attention_mask_mapping = self._prepare_attention_mask_mapping(
            hidden_states, attention_mask, position_ids
        )
        position_embeddings = self._rotary_emb(hidden_states, position_ids)

        for layer_idx in range(self.large_config.num_layers):
            if layer_idx == self._tail_start and injected_state is not None:
                hidden_states = self._apply_injection(
                    hidden_states, injected_state, injection_mode
                )

            layer = self._layers[layer_idx]
            layer_type = self.large_model.config.layer_types[layer_idx]
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
            current_state = hidden_states

            for _ in range(self.num_iters):
                if self.full_loop:
                    h = self._run_layers(
                        list(range(self.large_config.num_layers)),
                        current_state,
                        attention_mask,
                        position_ids,
                    )
                else:
                    # Reuse the original token positions because the loop feeds
                    # back a full-sequence latent state instead of appending a
                    # fresh token each iteration.
                    h = self._run_layers(
                        self._tail_layers,
                        current_state,
                        attention_mask,
                        position_ids,
                    )
                current_state = self._norm(h)

        return current_state
