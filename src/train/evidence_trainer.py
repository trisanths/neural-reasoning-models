"""Minimal optimization loop for the evidence model.

src/train/trainer.py's Trainer takes (inputs, targets) pairs and moves both
to the device itself, which does not fit a batch that also carries an
evidence bank. Rather than change the shared trainer, this module runs the
same recipe (AdamW, the cosine schedule from trainer.py, gradient clipping,
bf16 autocast on cuda) over EvidenceBatch objects. It exists for the tests
and the bench; a full run would extend the shared trainer instead.
"""

import time

import torch

from src.train.trainer import cosine_lr, seed_everything


def build_optimizer(model, lr: float, weight_decay: float = 0.1,
                    betas=(0.9, 0.95), eps: float = 1e-8):
    decay, no_decay = [], []
    for param in model.parameters():
        if not param.requires_grad:
            continue
        (decay if param.dim() >= 2 else no_decay).append(param)
    return torch.optim.AdamW(
        [
            {"params": decay, "weight_decay": weight_decay},
            {"params": no_decay, "weight_decay": 0.0},
        ],
        lr=lr, betas=betas, eps=eps,
    )


def train_evidence_steps(model, batches, steps: int, lr: float = 1e-3,
                         device: str = "cpu", seed: int = 0,
                         warmup_steps: int = 10, min_lr_ratio: float = 0.1,
                         grad_clip: float = 1.0, weight_decay: float = 0.0,
                         mode: str | None = None) -> list:
    """Run `steps` optimizer steps over a cycling list of batches.

    Returns the loss of every step. Batches are EvidenceBatch objects; they
    are moved to the device once per step so a fixed list can be reused.
    """
    seed_everything(seed)
    model = model.to(device)
    model.train()
    opt = build_optimizer(model, lr, weight_decay=weight_decay)
    use_autocast = device == "cuda"
    losses = []
    for step in range(steps):
        batch = batches[step % len(batches)].to(device)
        cur_lr = cosine_lr(step, lr, warmup_steps, steps, min_lr_ratio)
        for group in opt.param_groups:
            group["lr"] = cur_lr
        opt.zero_grad(set_to_none=True)
        if use_autocast:
            with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                _, loss = forward_batch(model, batch, mode)
        else:
            _, loss = forward_batch(model, batch, mode)
        loss.backward()
        if grad_clip > 0:
            torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
        opt.step()
        losses.append(float(loss.detach()))
    return losses


def forward_batch(model, batch, mode: str | None = None, gate_override=None):
    return model(
        batch.input_ids,
        evidence_ids=batch.evidence_ids,
        evidence_mask=batch.evidence_mask,
        reliability=batch.reliability,
        chunk_mask=batch.chunk_mask,
        targets=batch.targets,
        gate_override=gate_override,
        mode=mode,
    )


def timed_forward(model, batch, mode: str | None = None, backward: bool = False,
                  device: str = "cuda") -> float:
    """Wall clock seconds for one forward, or one forward plus backward."""
    if device == "cuda":
        torch.cuda.synchronize()
    start = time.perf_counter()
    if backward:
        _, loss = forward_batch(model, batch, mode)
        loss.backward()
    else:
        with torch.no_grad():
            forward_batch(model, batch, mode)
    if device == "cuda":
        torch.cuda.synchronize()
    return time.perf_counter() - start
