"""Curriculum dataset construction, following Coconut's staging scheme.

Sequence layout at curriculum stage ``s``::

    [pad]* [question] <bot> [latent]*k <eot> [steps[s:]] [answer] <eos> [pad]*

Stage 0 is plain chain-of-thought. Each stage replaces one more leading
reasoning step with a continuous thought, and the final stage removes the
textual chain entirely -- that last configuration is what we evaluate.

Questions are *left*-padded so the ``<bot>`` marker lands on the same absolute
index for every row in a batch. Every example here has the same number of
reasoning steps, so the latent block is then batch-aligned, which turns
Coconut's sequential latent passes into simple slicing instead of the
per-example scatter the reference implementation needs.
"""

from __future__ import annotations

from dataclasses import dataclass

import torch

from .data import Example, Tokenizer


@dataclass
class CurriculumConfig:
    max_latent_stage: int = 5
    c_thought: int = 1
    pad_latent_to_max: bool = True
    no_cot: bool = False  # ablation: no steps, no latents
    cot_only: bool = False  # ablation: always stage 0 (explicit CoT)


def latents_and_skip(stage: int, n_steps: int, cfg: CurriculumConfig) -> tuple[int, int]:
    """Returns (n_latent_tokens, n_skip_steps) for a curriculum stage."""
    if cfg.no_cot:
        return 0, n_steps
    if cfg.cot_only:
        return 0, 0
    if stage > cfg.max_latent_stage:
        n_skip = n_steps
        n_latent = (
            cfg.max_latent_stage
            if cfg.pad_latent_to_max
            else min(n_steps, cfg.max_latent_stage)
        )
    else:
        n_skip, n_latent = stage, stage
    return n_latent * cfg.c_thought, n_skip


@dataclass
class Batch:
    input_ids: torch.Tensor
    labels: torch.Tensor
    attention_mask: torch.Tensor
    position_ids: torch.Tensor
    latent_start: int  # absolute index of the first latent position
    n_latent: int
    answer_start: int  # absolute index where the answer segment begins

    def to(self, device) -> "Batch":
        return Batch(
            self.input_ids.to(device),
            self.labels.to(device),
            self.attention_mask.to(device),
            self.position_ids.to(device),
            self.latent_start,
            self.n_latent,
            self.answer_start,
        )


def build_batch(
    examples: list[Example],
    tok: Tokenizer,
    stage: int,
    cfg: CurriculumConfig,
    for_generation: bool = False,
) -> Batch:
    """Tokenizes and collates one batch at a given curriculum stage.

    With ``for_generation`` the sequence stops after ``<eot>``: the answer is to
    be produced by the model rather than teacher-forced.
    """
    # Subword tokenizers need separators attached inside the encoded segment,
    # so a tokenizer may supply segment-specific encoders. Word-level ones fall
    # back to plain encode().
    enc_q = getattr(tok, "encode_question", tok.encode)
    enc_s = getattr(tok, "encode_step", tok.encode)
    enc_a = getattr(tok, "encode_answer", tok.encode)
    q_ids = [enc_q(e.question) for e in examples]
    steps_ids = [[enc_s(s) for s in e.steps] for e in examples]
    ans_ids = [enc_a(e.answer) + [tok.eos_id] for e in examples]

    # Real datasets mix chain lengths (ProsQA has 3 to 6 steps), so how many
    # steps get skipped is per-example. The *number of latents* must still be
    # uniform, otherwise the latent block would start at a different index in
    # each row and the sequential passes could not be sliced. pad_latent_to_max
    # is what guarantees that at the final stage.
    per_example = [latents_and_skip(stage, len(s), cfg) for s in steps_ids]
    n_latent = per_example[0][0]
    if any(p[0] != n_latent for p in per_example):
        raise ValueError(
            "latent counts differ within the batch; set pad_latent_to_max=True, "
            "or bucket examples by step count before batching"
        )
    skips = [p[1] for p in per_example]

    q_max = max(len(q) for q in q_ids)
    # <bot> at q_max, latents at q_max+1 .. q_max+n_latent, <eot> after.
    prefix_len = q_max + 1 + n_latent + 1
    latent_start = q_max + 1

    tails = []
    for i in range(len(examples)):
        tail: list[int] = []
        for st in steps_ids[i][skips[i] :]:
            tail += st
        tail += ans_ids[i]
        tails.append(tail)
    tail_max = 0 if for_generation else max(len(t) for t in tails)
    total = prefix_len + tail_max

    pad = tok.pad_id
    input_ids = torch.full((len(examples), total), pad, dtype=torch.long)
    labels = torch.full((len(examples), total), -100, dtype=torch.long)
    attention_mask = torch.zeros((len(examples), total), dtype=torch.long)
    position_ids = torch.zeros((len(examples), total), dtype=torch.long)

    for i in range(len(examples)):
        lp = q_max - len(q_ids[i])  # left pad
        seq = (
            q_ids[i]
            + [tok.bot_id]
            + [tok.latent_id] * n_latent
            + [tok.eot_id]
            + (tails[i] if not for_generation else [])
        )
        input_ids[i, lp : lp + len(seq)] = torch.tensor(seq)
        attention_mask[i, lp : lp + len(seq)] = 1
        position_ids[i, lp : lp + len(seq)] = torch.arange(len(seq))
        if not for_generation:
            # Supervise only the textual tail (remaining steps + answer).
            labels[i, prefix_len : prefix_len + len(tails[i])] = torch.tensor(tails[i])

    return Batch(
        input_ids=input_ids,
        labels=labels,
        attention_mask=attention_mask,
        position_ids=position_ids,
        latent_start=latent_start,
        n_latent=n_latent,
        answer_start=prefix_len,
    )


def iterate_batches(
    examples: list[Example],
    tok: Tokenizer,
    stage: int,
    cfg: CurriculumConfig,
    batch_size: int,
    shuffle: bool = True,
    seed: int = 0,
    for_generation: bool = False,
):
    idx = list(range(len(examples)))
    if shuffle:
        import random

        random.Random(seed).shuffle(idx)
    for i in range(0, len(idx), batch_size):
        chunk = [examples[j] for j in idx[i : i + batch_size]]
        if chunk:
            yield build_batch(chunk, tok, stage, cfg, for_generation=for_generation)
