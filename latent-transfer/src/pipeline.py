"""Cross-model latent reasoning handoff.

    user -> small model -> latent -> [projector] -> big model's latent space
         -> continuous-thought reasoning -> [projector] -> small model -> answer

The small model reads the question and keeps its KV cache. Its final-layer
states are projected into the big model's residual space, where the big model
runs Coconut-style continuous-thought steps. Those thoughts are projected back
down and consumed by the small model at its latent positions, which then decodes
the answer from its existing cache.

The big model never decodes a token and the small model never re-reads the
question, so the reasoning is carried entirely by vectors crossing between two
independently trained latent spaces.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

from .coconut import masked_cross_entropy
from .dataset import Batch
from .model import TinyLM
from .projectors import Projector


class CrossModelPipeline(nn.Module):
    def __init__(
        self,
        small: TinyLM,
        big: TinyLM,
        proj_up: Projector,
        proj_down: Projector,
        add_positional_big: bool = True,
        detach_handoff: bool = False,
        n_message: int | None = None,
        tap_layer: int | None = None,
    ) -> None:
        super().__init__()
        self.small = small
        self.big = big
        self.proj_up = proj_up
        self.proj_down = proj_down
        self.add_positional_big = add_positional_big
        # If set, only the final ``n_message`` small-model states cross to the
        # big model. Those positions are causally downstream of the whole
        # question, so they can carry it in compressed form. This is what makes
        # the pipeline cheaper than running the big model directly: big-model
        # cost becomes O(n_message + k) instead of O(question length).
        self.n_message = n_message
        # Index into all_hidden (0 = embeddings, L = final block). None = the
        # post-LayerNorm final state.
        self.tap_layer = tap_layer
        # Cuts gradient flow from the small model's decoder back through the big
        # model; used when training stages independently.
        self.detach_handoff = detach_handoff

    # -- small model: read the question -------------------------------------
    def _small_prefix(self, batch: Batch, need_logits: bool = True):
        ls = batch.latent_start
        out = self.small(
            input_ids=batch.input_ids[:, :ls],
            attention_mask=batch.attention_mask[:, :ls],
            position_ids=batch.position_ids[:, :ls],
            output_all_hidden=self.tap_layer is not None,
            # forward() reads these for the loss; generate() discards them.
            logits_to_keep=0 if need_logits else 1,
        )
        # Final-layer states are shaped by the small model's own output head;
        # intermediate features are often the better donor for stitching.
        donor = (
            out.hidden_states
            if self.tap_layer is None
            else out.all_hidden[self.tap_layer]
        )
        return out.logits, out.past_key_values, donor

    # -- big model: reason in continuous space -------------------------------
    def big_thoughts(self, hidden_small: torch.Tensor, batch: Batch) -> list[torch.Tensor]:
        """Projects the small model's states up and runs k latent steps."""
        ls, k = batch.latent_start, batch.n_latent
        B = hidden_small.shape[0]
        device = hidden_small.device

        if self.n_message is None:
            src = hidden_small
            mask = batch.attention_mask[:, :ls]
            pos_ids = batch.position_ids[:, :ls]
            base = ls
        else:
            m = min(self.n_message, hidden_small.shape[1])
            src = hidden_small[:, -m:]
            # These are all real (non-pad) states, and they are re-indexed from
            # 0 because the big model sees a short fresh sequence, not the
            # original question layout.
            mask = torch.ones(B, m, dtype=batch.attention_mask.dtype, device=device)
            pos_ids = torch.arange(m, device=device).unsqueeze(0).expand(B, m)
            base = m

        embeds = self.proj_up(src)
        out = self.big(
            inputs_embeds=embeds,
            attention_mask=mask,
            position_ids=pos_ids,
            add_positional=self.add_positional_big,
            # The big model never decodes here; only its hidden states and cache
            # are read, so its vocabulary projection is pure waste.
            logits_to_keep=1,
        )
        kv = out.past_key_values
        h = out.hidden_states[:, -1]

        thoughts = []
        for j in range(k):
            thoughts.append(h)
            step_mask = torch.cat(
                [mask, torch.ones(B, j + 1, dtype=mask.dtype, device=device)], dim=1
            )
            step_pos = torch.full((B, 1), base + j, dtype=torch.long, device=device)
            out = self.big(
                inputs_embeds=h.unsqueeze(1),
                attention_mask=step_mask,
                position_ids=step_pos,
                past_key_values=kv,
                add_positional=self.add_positional_big,
            )
            kv = out.past_key_values
            h = out.hidden_states[:, -1]
        return thoughts

    # -- small model: consume thoughts and answer ----------------------------
    def _small_consume(self, batch: Batch, kv, thoughts: list[torch.Tensor], tail: bool):
        ls, k = batch.latent_start, batch.n_latent
        pieces = []
        for j in range(k):
            t = self.proj_down(thoughts[j])
            if self.detach_handoff:
                t = t.detach()
            pos = ls + j
            out = self.small(
                inputs_embeds=t.unsqueeze(1),
                attention_mask=batch.attention_mask[:, : pos + 1],
                position_ids=batch.position_ids[:, pos : pos + 1],
                past_key_values=kv,
            )
            pieces.append(out.logits)
            kv = out.past_key_values
        if tail:
            start = ls + k
            if start < batch.input_ids.shape[1]:
                out = self.small(
                    input_ids=batch.input_ids[:, start:],
                    attention_mask=batch.attention_mask,
                    position_ids=batch.position_ids[:, start:],
                    past_key_values=kv,
                )
                pieces.append(out.logits)
                kv = out.past_key_values
        return pieces, kv

    def forward(self, batch: Batch, return_thoughts: bool = False):
        prefix_logits, kv, hidden_small = self._small_prefix(batch)
        thoughts = self.big_thoughts(hidden_small, batch)
        pieces, _ = self._small_consume(batch, kv, thoughts, tail=True)
        logits = torch.cat([prefix_logits] + pieces, dim=1)
        loss = masked_cross_entropy(logits, batch.labels)
        if return_thoughts:
            return loss, logits, thoughts
        return loss, logits, []

    @torch.no_grad()
    def generate(self, batch: Batch, max_new_tokens: int, eos_id: int, **_):
        ls, k = batch.latent_start, batch.n_latent
        B = batch.input_ids.shape[0]
        device = batch.input_ids.device

        _, kv, hidden_small = self._small_prefix(batch, need_logits=False)
        thoughts = self.big_thoughts(hidden_small, batch)
        _, kv = self._small_consume(batch, kv, thoughts, tail=False)

        # <eot> closes the latent block.
        eot_pos = ls + k
        out = self.small(
            input_ids=batch.input_ids[:, eot_pos : eot_pos + 1],
            attention_mask=batch.attention_mask[:, : eot_pos + 1],
            position_ids=batch.position_ids[:, eot_pos : eot_pos + 1],
            past_key_values=kv,
        )
        kv = out.past_key_values
        logits = out.logits[:, -1]

        mask = batch.attention_mask[:, : eot_pos + 1]
        tokens = torch.zeros(B, max_new_tokens, dtype=torch.long, device=device)
        done = torch.zeros(B, dtype=torch.bool, device=device)
        pos = batch.position_ids[:, eot_pos] + 1

        for t in range(max_new_tokens):
            nxt = logits.argmax(-1)
            nxt = torch.where(done, torch.zeros_like(nxt), nxt)
            tokens[:, t] = nxt
            done = done | (nxt == eos_id)
            if bool(done.all()):
                break
            mask = torch.cat([mask, torch.ones(B, 1, dtype=mask.dtype, device=device)], 1)
            out = self.small(
                input_ids=nxt.unsqueeze(1),
                attention_mask=mask,
                position_ids=pos.unsqueeze(1),
                past_key_values=kv,
            )
            kv = out.past_key_values
            logits = out.logits[:, -1]
            pos = pos + 1
        return tokens

    def train(self, mode: bool = True):
        return super().train(mode)
