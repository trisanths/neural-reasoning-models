"""A compact decoder-only transformer.

Deliberately minimal, but exposes the three things the latent pipeline needs and
that HuggingFace models also provide, so the pipeline code is backbone-agnostic:

  * ``inputs_embeds`` -- feed continuous vectors instead of token ids,
  * ``past_key_values`` -- reuse KV cache across the sequential latent passes,
  * ``output_hidden_states`` -- read the final-layer state that becomes the
    next continuous thought.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F


@dataclass
class ModelConfig:
    vocab_size: int
    d_model: int = 256
    n_layers: int = 6
    n_heads: int = 4
    d_ff: int | None = None
    max_len: int = 512
    dropout: float = 0.0
    tie_embeddings: bool = True

    def __post_init__(self) -> None:
        if self.d_ff is None:
            self.d_ff = 4 * self.d_model
        if self.d_model % self.n_heads != 0:
            raise ValueError("d_model must be divisible by n_heads")


class Block(nn.Module):
    def __init__(self, cfg: ModelConfig) -> None:
        super().__init__()
        self.n_heads = cfg.n_heads
        self.d_head = cfg.d_model // cfg.n_heads
        self.ln1 = nn.LayerNorm(cfg.d_model)
        self.qkv = nn.Linear(cfg.d_model, 3 * cfg.d_model)
        self.proj = nn.Linear(cfg.d_model, cfg.d_model)
        self.ln2 = nn.LayerNorm(cfg.d_model)
        self.mlp = nn.Sequential(
            nn.Linear(cfg.d_model, cfg.d_ff),
            nn.GELU(),
            nn.Linear(cfg.d_ff, cfg.d_model),
        )
        self.drop = nn.Dropout(cfg.dropout)

    def forward(
        self,
        x: torch.Tensor,
        past_kv: tuple[torch.Tensor, torch.Tensor] | None = None,
        attn_mask: torch.Tensor | None = None,
    ):
        B, T, C = x.shape
        h = self.ln1(x)
        q, k, v = self.qkv(h).split(C, dim=2)
        q = q.view(B, T, self.n_heads, self.d_head).transpose(1, 2)
        k = k.view(B, T, self.n_heads, self.d_head).transpose(1, 2)
        v = v.view(B, T, self.n_heads, self.d_head).transpose(1, 2)

        if past_kv is not None:
            k = torch.cat([past_kv[0], k], dim=2)
            v = torch.cat([past_kv[1], v], dim=2)
        present = (k, v)

        # Query position t (absolute index T_past + t) may attend to keys 0..T_past+t.
        T_full = k.shape[2]
        T_past = T_full - T
        causal = torch.ones(T, T_full, dtype=torch.bool, device=x.device).tril(
            diagonal=T_past
        )
        if attn_mask is not None:
            # attn_mask: (B, T_full), 1 = attend, 0 = padding.
            causal = causal.unsqueeze(0) & attn_mask[:, None, :].bool()
            # A query sitting on a left-pad position has every key masked, and a
            # fully-masked softmax row is NaN on some backends -- which would
            # then propagate through zero-weighted values into real positions.
            # Letting every query attend to itself keeps each row non-empty.
            # Real positions already permit self-attention, so this changes
            # nothing for them.
            self_idx = torch.arange(T, device=x.device) + T_past
            causal[:, torch.arange(T, device=x.device), self_idx] = True
            causal = causal.unsqueeze(1)  # (B, 1, T, T_full)
        else:
            causal = causal.view(1, 1, T, T_full)

        y = F.scaled_dot_product_attention(q, k, v, attn_mask=causal)
        y = y.transpose(1, 2).contiguous().view(B, T, C)
        x = x + self.drop(self.proj(y))
        x = x + self.drop(self.mlp(self.ln2(x)))
        return x, present


@dataclass
class CausalLMOutput:
    logits: torch.Tensor
    hidden_states: torch.Tensor  # final-layer states, (B, T, d_model)
    past_key_values: list[tuple[torch.Tensor, torch.Tensor]]
    loss: torch.Tensor | None = None
    all_hidden: list[torch.Tensor] | None = None  # per-layer, when requested


class TinyLM(nn.Module):
    def __init__(self, cfg: ModelConfig) -> None:
        super().__init__()
        self.cfg = cfg
        self.wte = nn.Embedding(cfg.vocab_size, cfg.d_model)
        self.wpe = nn.Embedding(cfg.max_len, cfg.d_model)
        self.drop = nn.Dropout(cfg.dropout)
        self.blocks = nn.ModuleList([Block(cfg) for _ in range(cfg.n_layers)])
        self.ln_f = nn.LayerNorm(cfg.d_model)
        self.lm_head = nn.Linear(cfg.d_model, cfg.vocab_size, bias=False)
        if cfg.tie_embeddings:
            self.lm_head.weight = self.wte.weight
        self.apply(self._init)

    def _init(self, module: nn.Module) -> None:
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, std=0.02)

    def get_input_embeddings(self) -> nn.Embedding:
        return self.wte

    def n_params(self, trainable_only: bool = False) -> int:
        ps = self.parameters()
        if trainable_only:
            ps = (p for p in ps if p.requires_grad)
        return sum(p.numel() for p in ps)

    def forward(
        self,
        input_ids: torch.Tensor | None = None,
        inputs_embeds: torch.Tensor | None = None,
        attention_mask: torch.Tensor | None = None,
        position_ids: torch.Tensor | None = None,
        past_key_values: list[tuple[torch.Tensor, torch.Tensor]] | None = None,
        labels: torch.Tensor | None = None,
        add_positional: bool = True,
        output_all_hidden: bool = False,
        logits_to_keep: int = 0,
    ) -> CausalLMOutput:
        # logits_to_keep is a memory optimisation that only matters for large
        # vocabularies, so it is accepted and ignored here to keep the backbone
        # interface uniform.
        del logits_to_keep
        if (input_ids is None) == (inputs_embeds is None):
            raise ValueError("pass exactly one of input_ids / inputs_embeds")
        if inputs_embeds is None:
            inputs_embeds = self.wte(input_ids)
        B, T, _ = inputs_embeds.shape

        past_len = 0 if past_key_values is None else past_key_values[0][0].shape[2]
        if position_ids is None:
            position_ids = torch.arange(
                past_len, past_len + T, device=inputs_embeds.device
            ).unsqueeze(0)

        x = inputs_embeds
        if add_positional:
            x = x + self.wpe(position_ids)
        x = self.drop(x)

        presents = []
        all_hidden = [x] if output_all_hidden else None
        for i, block in enumerate(self.blocks):
            past = None if past_key_values is None else past_key_values[i]
            x, present = block(x, past_kv=past, attn_mask=attention_mask)
            presents.append(present)
            if output_all_hidden:
                all_hidden.append(x)

        h = self.ln_f(x)
        logits = self.lm_head(h)

        loss = None
        if labels is not None:
            loss = F.cross_entropy(
                logits[:, :-1].reshape(-1, logits.size(-1)),
                labels[:, 1:].reshape(-1),
                ignore_index=-100,
            )
        return CausalLMOutput(
            logits=logits,
            hidden_states=h,
            past_key_values=presents,
            loss=loss,
            all_hidden=all_hidden,
        )
