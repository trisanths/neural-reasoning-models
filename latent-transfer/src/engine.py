"""Training and evaluation loops."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass

import torch

from .coconut import Coconut
from .data import Example, Tokenizer
from .dataset import CurriculumConfig, build_batch, iterate_batches, latents_and_skip

FINAL_STAGE = 99  # any stage > max_latent_stage: full latent, no textual chain


def _final_sentence(text: str) -> str:
    """Extracts the answer span.

    Datasets that mark the answer with '###' (the ProsQA/GSM8K convention) are
    split on that; otherwise the answer is the last complete sentence, since the
    model may emit remaining reasoning steps first.
    """
    if "###" in text:
        return text.split("###")[-1].strip()
    parts = [p.strip() for p in text.split(".") if p.strip()]
    return (parts[-1] + " .") if parts else text.strip()


def _answer_key(text: str) -> str:
    """The decision-carrying token of an answer.

    Works across tokenisations: the word-level tasks emit 'alice is a grimpus .'
    while an HF tokeniser emits 'Tom is a zhorpus.' with no space before the
    period, so trailing punctuation is stripped before taking the last word.
    """
    t = text.strip().rstrip(".").strip()
    parts = t.split()
    return parts[-1] if parts else ""


def get_device() -> torch.device:
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


@torch.no_grad()
def evaluate(
    model: Coconut,
    examples: list[Example],
    tok: Tokenizer,
    cfg: CurriculumConfig,
    device: torch.device,
    batch_size: int = 64,
    stage: int = FINAL_STAGE,
    max_new_tokens: int | None = None,
    thought_hook=None,
) -> dict:
    """Greedy-decodes answers and scores them.

    ``exact`` is full-string match. ``concept`` scores only the predicted
    target concept, which is the actual binary reasoning decision.

    At curriculum stages that retain textual reasoning the model emits the
    remaining chain before the answer, so we budget enough tokens for it and
    score the final sentence.
    """
    model.eval()
    if max_new_tokens is None:
        # Budget for the LONGEST chain present, not the first example. ProsQA
        # mixes 3- to 6-step problems, and a budget sized on a short one
        # truncates long ones before they emit the answer marker, scoring them
        # zero for a decoding reason rather than a reasoning one.
        n_steps = max(len(e.steps) for e in examples)
        _, n_skip = latents_and_skip(stage, n_steps, cfg)
        # Subword tokenizers need more room than the word-level ones this was
        # first tuned on: a ProsQA step is ~7 tokens and the answer ~9.
        max_new_tokens = 16 + 12 * max(n_steps - n_skip, 0)

    n = correct = concept_correct = 0
    for i in range(0, len(examples), batch_size):
        chunk = examples[i : i + batch_size]
        batch = build_batch(chunk, tok, stage, cfg, for_generation=True).to(device)
        out = model.generate(
            batch, max_new_tokens=max_new_tokens, eos_id=tok.eos_id, thought_hook=thought_hook
        )
        for j, ex in enumerate(chunk):
            ids = out[j].tolist()
            if tok.eos_id in ids:
                ids = ids[: ids.index(tok.eos_id)]
            pred = _final_sentence(tok.decode(ids))
            gold = ex.answer.strip()
            n += 1
            correct += int(pred == gold)
            if _answer_key(pred) and _answer_key(pred) == _answer_key(gold):
                concept_correct += 1
    return {
        "exact": correct / max(n, 1),
        "concept": concept_correct / max(n, 1),
        "n": n,
    }


@dataclass
class TrainConfig:
    epochs_per_stage: int = 3
    batch_size: int = 32
    lr: float = 3e-4
    weight_decay: float = 0.01
    grad_clip: float = 1.0
    warmup_frac: float = 0.03
    reset_optimizer: bool = True
    log_every: int = 50
    eval_every_stage: bool = True


def _make_optimizer(params, tc: TrainConfig):
    return torch.optim.AdamW(params, lr=tc.lr, weight_decay=tc.weight_decay, betas=(0.9, 0.95))


def train_curriculum(
    model: Coconut,
    train_ex: list[Example],
    val_ex: list[Example],
    tok: Tokenizer,
    cur: CurriculumConfig,
    tc: TrainConfig,
    device: torch.device,
    stages: list[int] | None = None,
    log=print,
    thought_hook=None,
    params=None,
    on_stage_end=None,
) -> dict:
    """Runs the Coconut curriculum: one block of epochs per stage.

    The optimizer is reset at each stage boundary (as in the reference
    implementation) because the objective changes discontinuously when a
    reasoning step is replaced by a latent.
    """
    if stages is None:
        stages = list(range(cur.max_latent_stage + 1)) + [FINAL_STAGE]
    params = list(model.parameters()) if params is None else list(params)
    opt = _make_optimizer(params, tc)
    history = []
    step = 0
    n_skipped = 0
    t0 = time.time()

    for stage in stages:
        if tc.reset_optimizer:
            opt = _make_optimizer(params, tc)
        n_batches = math.ceil(len(train_ex) / tc.batch_size) * tc.epochs_per_stage
        sched = torch.optim.lr_scheduler.OneCycleLR(
            opt,
            max_lr=tc.lr,
            total_steps=max(n_batches, 1),
            pct_start=tc.warmup_frac,
            anneal_strategy="cos",
        )
        model.train()
        for epoch in range(tc.epochs_per_stage):
            running, cnt = 0.0, 0
            for batch in iterate_batches(
                train_ex, tok, stage, cur, tc.batch_size, shuffle=True, seed=step
            ):
                batch = batch.to(device)
                loss, _, _ = model(batch, thought_hook=thought_hook)
                # A single non-finite batch would propagate into the weights and
                # every later loss reads nan, so the run looks alive while
                # learning nothing. Clipping does not help: clipping nan yields
                # nan. Skip the update instead and count it.
                if not torch.isfinite(loss):
                    n_skipped += 1
                    opt.zero_grad(set_to_none=True)
                    continue
                loss.backward()
                # A finite loss can still produce non-finite gradients: bf16
                # backward over long sequences overflows well before the forward
                # does. Stepping on those corrupts the weights, after which every
                # later loss reads nan and the run learns nothing while appearing
                # to train. clip_grad_norm_ returns the pre-clip norm, so it
                # doubles as the check.
                gnorm = torch.nn.utils.clip_grad_norm_(params, tc.grad_clip)
                if not torch.isfinite(gnorm):
                    n_skipped += 1
                    opt.zero_grad(set_to_none=True)
                    continue
                opt.step()
                sched.step()
                opt.zero_grad(set_to_none=True)
                running += loss.item()
                cnt += 1
                step += 1
                if tc.log_every and step % tc.log_every == 0:
                    log(
                        f"  stage {stage} ep {epoch} step {step} "
                        f"loss {running / max(cnt, 1):.4f} ({time.time() - t0:.0f}s)"
                    )
                    running, cnt = 0.0, 0
        if on_stage_end is not None:
            # Checkpoint per stage. A crash in a later stage otherwise discards
            # every earlier stage's training, which on a long curriculum is
            # hours of compute for no artefact.
            on_stage_end(stage)
        if tc.eval_every_stage:
            m = evaluate(model, val_ex, tok, cur, device, stage=stage, thought_hook=thought_hook)
            skip_note = f" skipped={n_skipped}" if n_skipped else ""
            log(f"[stage {stage}] val exact={m['exact']:.3f} concept={m['concept']:.3f}{skip_note}")
            history.append({"stage": stage, **m})
            model.train()
    return {"history": history, "steps": step, "skipped": n_skipped,
            "seconds": time.time() - t0}
