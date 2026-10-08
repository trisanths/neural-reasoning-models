"""Coconut: chain of continuous thought (Hao et al., 2024).

The model's final-layer hidden state is fed back as the next input embedding
instead of being decoded to a token, so reasoning happens in the residual
stream. Each latent position costs one sequential forward pass; the KV cache is
carried across passes so earlier positions are computed exactly once.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

from .dataset import Batch
from .model import TinyLM


def masked_cross_entropy(logits: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
    """Cross-entropy over supervised positions only.

    Selecting before the loss rather than relying on ignore_index matters at
    scale: the flattened (B*T, V) tensor and its float32 upcast are the largest
    allocations in the step, and under the curriculum almost every position is
    masked. At the final stage only the answer is supervised, roughly ten
    positions out of four hundred, so this avoids materialising two orders of
    magnitude more logits than the loss actually reads.
    """
    shift_logits = logits[:, :-1]
    shift_labels = labels[:, 1:]
    sel = shift_labels != -100
    if not sel.any():
        return shift_logits.sum() * 0.0  # keeps the graph connected
    return F.cross_entropy(shift_logits[sel].float(), shift_labels[sel])


class Coconut(nn.Module):
    def __init__(self, base: TinyLM) -> None:
        super().__init__()
        self.base = base

    def _prefix(
        self,
        batch: Batch,
        thought_hook=None,
        prefix_embeds: torch.Tensor | None = None,
        need_logits: bool = True,
    ) -> tuple[list[torch.Tensor], list, torch.Tensor, list[torch.Tensor]]:
        """Runs question + latent block.

        Returns (logit_pieces, kv_cache, last_hidden, thoughts). ``thought_hook``
        may transform each thought before it is fed back, which is how the
        cross-model pipeline injects an externally-produced thought.
        ``prefix_embeds`` replaces the question's input embeddings, which is how
        the big model is driven from another model's projected states.
        """
        ls, k = batch.latent_start, batch.n_latent
        emb = self.base.wte(batch.input_ids) if prefix_embeds is None else None
        if prefix_embeds is not None:
            emb = torch.cat(
                [prefix_embeds, self.base.wte(batch.input_ids[:, ls:])], dim=1
            )

        out = self.base(
            inputs_embeds=emb[:, :ls],
            attention_mask=batch.attention_mask[:, :ls],
            position_ids=batch.position_ids[:, :ls],
            # Training reads these for the loss; generation discards them, and
            # over a ~400-token question at a 152k vocabulary that is 8 GB.
            logits_to_keep=0 if need_logits else 1,
        )
        pieces = [out.logits]
        kv = out.past_key_values
        last_h = out.hidden_states[:, -1]  # state at <bot>, seeds the first thought

        thoughts: list[torch.Tensor] = []
        for j in range(k):
            thought = last_h if thought_hook is None else thought_hook(last_h, j)
            thoughts.append(thought)
            pos = ls + j
            out = self.base(
                inputs_embeds=thought.unsqueeze(1),
                attention_mask=batch.attention_mask[:, : pos + 1],
                position_ids=batch.position_ids[:, pos : pos + 1],
                past_key_values=kv,
            )
            pieces.append(out.logits)
            kv = out.past_key_values
            last_h = out.hidden_states[:, -1]
        return pieces, kv, last_h, thoughts

    def forward(self, batch: Batch, thought_hook=None, prefix_embeds: torch.Tensor | None = None):
        ls, k = batch.latent_start, batch.n_latent
        if k == 0:
            out = self.base(
                input_ids=batch.input_ids,
                attention_mask=batch.attention_mask,
                position_ids=batch.position_ids,
            )
            logits, thoughts = out.logits, []
        else:
            pieces, kv, _, thoughts = self._prefix(batch, thought_hook, prefix_embeds)
            tail_start = ls + k
            if tail_start < batch.input_ids.shape[1]:
                emb = self.base.wte(batch.input_ids[:, tail_start:])
                out = self.base(
                    inputs_embeds=emb,
                    attention_mask=batch.attention_mask,
                    position_ids=batch.position_ids[:, tail_start:],
                    past_key_values=kv,
                )
                pieces.append(out.logits)
            logits = torch.cat(pieces, dim=1)

        loss = masked_cross_entropy(logits, batch.labels)
        return loss, logits, thoughts

    @torch.no_grad()
    def generate(self, batch: Batch, max_new_tokens: int, eos_id: int, thought_hook=None):
        """Greedy decoding after the latent block. Batch must be built with
        ``for_generation=True`` so the sequence ends at ``<eot>``."""
        ls, k = batch.latent_start, batch.n_latent
        B = batch.input_ids.shape[0]
        device = batch.input_ids.device

        if k == 0:
            out = self.base(
                input_ids=batch.input_ids,
                attention_mask=batch.attention_mask,
                position_ids=batch.position_ids,
                logits_to_keep=1,  # only the last position is read below
            )
            kv = out.past_key_values
            logits = out.logits[:, -1]
            cur_len = batch.input_ids.shape[1]
        else:
            pieces, kv, _, _ = self._prefix(batch, thought_hook, need_logits=False)
            # After the latent block comes <eot>, the final real token.
            eot_pos = ls + k
            emb = self.base.wte(batch.input_ids[:, eot_pos : eot_pos + 1])
            out = self.base(
                inputs_embeds=emb,
                attention_mask=batch.attention_mask[:, : eot_pos + 1],
                position_ids=batch.position_ids[:, eot_pos : eot_pos + 1],
                past_key_values=kv,
            )
            kv = out.past_key_values
            logits = out.logits[:, -1]
            cur_len = eot_pos + 1

        mask = batch.attention_mask[:, :cur_len]
        tokens = torch.zeros(B, max_new_tokens, dtype=torch.long, device=device)
        done = torch.zeros(B, dtype=torch.bool, device=device)
        pos = batch.position_ids[:, cur_len - 1] + 1

        for t in range(max_new_tokens):
            nxt = logits.argmax(-1)
            nxt = torch.where(done, torch.zeros_like(nxt), nxt)
            tokens[:, t] = nxt
            done = done | (nxt == eos_id)
            if bool(done.all()):
                break
            mask = torch.cat([mask, torch.ones(B, 1, dtype=mask.dtype, device=device)], 1)
            out = self.base(
                input_ids=nxt.unsqueeze(1),
                attention_mask=mask,
                position_ids=pos.unsqueeze(1),
                past_key_values=kv,
            )
            kv = out.past_key_values
            logits = out.logits[:, -1]
            pos = pos + 1
        return tokens
