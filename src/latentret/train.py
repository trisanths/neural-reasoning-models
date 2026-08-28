"""Train one latent-retrieval condition and report the curve it traced.

One function, because the whole experiment is the same training run with one
thing changed at a time: which query mode forms the query, whether the retrieval
term is in the loss at all, whether the distractors share the gold system's
name. Everything else is held.

Train and eval draw from disjoint seed ranges, so the invented words at eval
time were never seen in training. The rule families are shared, which is the
point: the model is meant to learn to read a rule of a known shape off a page it
has never seen, not to memorize any particular rule.
"""

from __future__ import annotations

import math
import time
from dataclasses import asdict, dataclass, field

import torch

from src.latentret.data import EpisodeStream
from src.latentret.evals import measure, per_iteration
from src.latentret.loss import LossWeights, latentret_loss
from src.latentret.model import LatentRetConfig, LatentRetrievalLM
from src.latentret.vocab import get_vocab
from src.train.model import ModelConfig

TRAIN_SEEDS = (0, 400_000)
EVAL_SEEDS = (900_000, 1_000_000)


@dataclass
class RunConfig:
    name: str = "latent"
    query_mode: str = "latent"
    hard: bool = True
    steps: int = 3000
    batch_size: int = 48
    lr: float = 1.5e-3
    warmup: int = 150
    min_lr_ratio: float = 0.05
    weight_decay: float = 0.05
    grad_clip: float = 1.0
    seed: int = 1234
    loops: int = 6
    d_model: int = 128
    n_heads: int = 4
    d_ff: int = 352
    prelude: int = 1
    core: int = 2
    coda: int = 1
    d_ret: int = 64
    readout: str = "both"
    inject: bool = True
    eval_every: int = 250
    eval_batches: int = 8
    weights: LossWeights = field(default_factory=lambda: LossWeights(gamma=0.25))


def build_model(cfg: RunConfig) -> LatentRetrievalLM:
    vocab = get_vocab()
    mcfg = ModelConfig(
        vocab_size=len(vocab),
        d_model=cfg.d_model,
        n_layers=cfg.prelude + cfg.core + cfg.coda,
        n_heads=cfg.n_heads,
        d_ff=cfg.d_ff,
        max_seq_len=256,
        recurrent={
            "prelude_layers": cfg.prelude,
            "core_layers": cfg.core,
            "coda_layers": cfg.coda,
            "loops": cfg.loops,
            "loop_embedding": True,
            "train_loop_sampling": None,
            "backprop_last_k": None,
            "grad_checkpoint": False,
            "inject_prelude": True,
        },
    )
    return LatentRetrievalLM(
        mcfg, LatentRetConfig(d_ret=cfg.d_ret, readout=cfg.readout))


def _lr_at(step: int, cfg: RunConfig) -> float:
    if step < cfg.warmup:
        return cfg.lr * (step + 1) / cfg.warmup
    t = (step - cfg.warmup) / max(1, cfg.steps - cfg.warmup)
    cos = 0.5 * (1.0 + math.cos(math.pi * min(1.0, t)))
    return cfg.lr * (cfg.min_lr_ratio + (1.0 - cfg.min_lr_ratio) * cos)


def train_one(cfg: RunConfig, device: str = "cuda") -> dict:
    torch.manual_seed(cfg.seed)
    model = build_model(cfg).to(device)
    train_stream = EpisodeStream(*TRAIN_SEEDS, cfg.batch_size, seed=cfg.seed,
                                 hard=cfg.hard)
    eval_stream = EpisodeStream(*EVAL_SEEDS, cfg.batch_size, seed=cfg.seed + 1,
                                hard=cfg.hard)
    opt = torch.optim.AdamW(model.parameters(), lr=cfg.lr,
                            weight_decay=cfg.weight_decay, betas=(0.9, 0.95))

    curve, started = [], time.time()
    for step in range(cfg.steps):
        for group in opt.param_groups:
            group["lr"] = _lr_at(step, cfg)
        batch = train_stream.batch().to(device)
        out = model.episode_forward(
            batch.prompt, batch.ans_pos, batch.docs, batch.doc_mask,
            batch.question, batch.question_mask,
            query_mode=cfg.query_mode, inject=cfg.inject)
        loss, stats = latentret_loss(out, batch, cfg.weights)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.grad_clip)
        opt.step()

        if step % cfg.eval_every == 0 or step == cfg.steps - 1:
            m = measure(model, eval_stream, device, cfg.eval_batches,
                        query_mode=cfg.query_mode)
            curve.append({"step": step, **stats, **m})
            print(f"[{cfg.name}] step {step:5d} loss {stats['loss']:.3f} "
                  f"task {stats['task']:.3f} ret {stats['retrieval']:.3f} "
                  f"acc {m['acc_final']:.3f} foil {m['acc_vs_foil']:.3f} "
                  f"hit {m['hit_gate']:.3f} "
                  f"gate_auc {m['gate_auc']:.3f} gap {m['gate_gap']:+.3f}",
                  flush=True)

    final = measure(model, eval_stream, device, 4 * cfg.eval_batches,
                    query_mode=cfg.query_mode)
    iters = per_iteration(model, eval_stream, device, 8, query_mode=cfg.query_mode)
    return {
        "config": {**asdict(cfg), "weights": asdict(cfg.weights)},
        "params": model.describe_latentret(),
        "curve": curve,
        "final": final,
        "per_iteration": iters,
        "minutes": (time.time() - started) / 60.0,
    }
