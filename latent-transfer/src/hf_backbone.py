"""Adapts a HuggingFace causal LM to the interface the pipeline expects.

The pipeline only needs three things from a backbone, all of which HF models
already provide: feeding continuous vectors via ``inputs_embeds``, carrying a KV
cache across the sequential latent passes, and reading final-layer hidden
states. This wrapper normalises the return type and the cache handling so
``Coconut`` and ``CrossModelPipeline`` work unchanged on Qwen, Llama or GPT-2.

Cache note: transformers v4.36+ returns ``Cache`` objects that mutate in place
and grow. The pipeline never rewinds a cache, it only ever appends, so passing
the returned object straight back is correct. Each fresh forward with
``past_key_values=None`` allocates a new cache, which is what keeps the teacher
and student passes in stage 1 from contaminating each other.
"""

from __future__ import annotations

from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F

from .model import CausalLMOutput


@dataclass
class HFConfig:
    """Mirrors the fields of ModelConfig that the pipeline reads."""

    d_model: int
    n_layers: int
    vocab_size: int
    max_len: int


class HFBackbone(nn.Module):
    """Wraps ``AutoModelForCausalLM`` in the TinyLM interface."""

    def __init__(self, model, tokenizer=None) -> None:
        super().__init__()
        self.model = model
        self.tokenizer = tokenizer
        cfg = model.config
        self.cfg = HFConfig(
            d_model=cfg.hidden_size,
            n_layers=cfg.num_hidden_layers,
            vocab_size=cfg.vocab_size,
            max_len=getattr(cfg, "max_position_embeddings", 4096),
        )

    @classmethod
    def load(cls, name: str, dtype=torch.bfloat16, device="cuda", **kw):
        from transformers import AutoModelForCausalLM, AutoTokenizer

        tok = AutoTokenizer.from_pretrained(name)
        model = AutoModelForCausalLM.from_pretrained(name, dtype=dtype, **kw).to(device)
        return cls(model, tok)

    # -- TinyLM-compatible surface ------------------------------------------
    @property
    def wte(self) -> nn.Module:
        return self.model.get_input_embeddings()

    def get_input_embeddings(self) -> nn.Module:
        return self.model.get_input_embeddings()

    def n_params(self, trainable_only: bool = False) -> int:
        ps = self.parameters()
        if trainable_only:
            ps = (p for p in ps if p.requires_grad)
        return sum(p.numel() for p in ps)

    def resize_for_markers(self, n_new: int) -> None:
        """Grows the embedding table for the <bot>/<eot>/<latent> markers."""
        self.model.resize_token_embeddings(len(self.tokenizer) + n_new)
        self.cfg.vocab_size = self.model.config.vocab_size

    def forward(
        self,
        input_ids: torch.Tensor | None = None,
        inputs_embeds: torch.Tensor | None = None,
        attention_mask: torch.Tensor | None = None,
        position_ids: torch.Tensor | None = None,
        past_key_values=None,
        labels: torch.Tensor | None = None,
        add_positional: bool = True,
        output_all_hidden: bool = False,
        logits_to_keep: int = 0,
    ) -> CausalLMOutput:
        if (input_ids is None) == (inputs_embeds is None):
            raise ValueError("pass exactly one of input_ids / inputs_embeds")
        if not add_positional:
            # Rotary models fold position into attention rather than adding it to
            # the embedding, so there is nothing to switch off. Silently ignoring
            # the flag would let an ablation look like it ran when it did not.
            raise NotImplementedError(
                "add_positional=False is meaningless for rotary-embedding models; "
                "the ablation only applies to learned positional embeddings"
            )

        extra = {}
        if logits_to_keep:
            # During generation only the last position's logits are read, but HF
            # projects every position through the vocabulary by default. At a
            # 152k vocabulary that is 8 GB of tensors we immediately discard.
            extra["logits_to_keep"] = logits_to_keep
        out = self.model(
            input_ids=input_ids,
            inputs_embeds=inputs_embeds,
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=past_key_values,
            use_cache=True,
            output_hidden_states=True,
            return_dict=True,
            **extra,
        )

        loss = None
        if labels is not None:
            from .coconut import masked_cross_entropy

            loss = masked_cross_entropy(out.logits, labels)
        return CausalLMOutput(
            logits=out.logits,
            hidden_states=out.hidden_states[-1],
            past_key_values=out.past_key_values,
            loss=loss,
            all_hidden=list(out.hidden_states) if output_all_hidden else None,
        )


class HFTokenizerAdapter:
    """Gives an HF tokenizer the marker-id surface the curriculum builder uses."""

    MARKERS = ["<bot>", "<eot>", "<latent>"]

    def __init__(self, tokenizer) -> None:
        self.tok = tokenizer
        added = tokenizer.add_special_tokens(
            {"additional_special_tokens": self.MARKERS}
        )
        self.n_added = added
        if tokenizer.pad_token_id is None:
            tokenizer.pad_token = tokenizer.eos_token
        self.pad_id = tokenizer.pad_token_id
        self.eos_id = tokenizer.eos_token_id
        self.bos_id = tokenizer.bos_token_id or tokenizer.eos_token_id
        self.bot_id, self.eot_id, self.latent_id = tokenizer.convert_tokens_to_ids(
            self.MARKERS
        )

    def __len__(self) -> int:
        return len(self.tok)

    def encode(self, text: str) -> list[int]:
        return self.tok.encode(text, add_special_tokens=False)

    def decode(self, ids: list[int]) -> str:
        return self.tok.decode(ids, skip_special_tokens=True)
