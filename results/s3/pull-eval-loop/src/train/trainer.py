"""Training loop: AdamW, cosine schedule with warmup, gradient accumulation,
bf16 autocast on cuda, gradient clipping, periodic checkpoints, jsonl loss
logging, deterministic seeding, and resume from checkpoint."""

import json
import math
import time
from pathlib import Path

import numpy as np
import torch

from src.train.model import TransformerLM


def cosine_lr(step: int, base_lr: float, warmup_steps: int, max_steps: int, min_lr_ratio: float) -> float:
    """Linear warmup then cosine decay to base_lr * min_lr_ratio."""
    if warmup_steps > 0 and step < warmup_steps:
        return base_lr * (step + 1) / warmup_steps
    if step >= max_steps:
        return base_lr * min_lr_ratio
    span = max(1, max_steps - warmup_steps)
    progress = (step - warmup_steps) / span
    coeff = 0.5 * (1.0 + math.cos(math.pi * progress))
    return base_lr * (min_lr_ratio + (1.0 - min_lr_ratio) * coeff)


def seed_everything(seed: int) -> None:
    torch.manual_seed(seed)
    np.random.seed(seed % (1 << 32))
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


class Trainer:
    """Runs optimization steps over an iterator of (inputs, targets) batches.

    The config dict uses the same optimizer, schedule, and train sections as
    the yaml files under configs/.
    """

    def __init__(self, model: TransformerLM, cfg: dict, out_dir: str, device: str | None = None):
        self.cfg = cfg
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = device
        self.use_autocast = device == "cuda"

        train_cfg = cfg["train"]
        self.grad_accum_steps = int(train_cfg.get("grad_accum_steps", 1))
        self.grad_clip = float(train_cfg.get("grad_clip", 1.0))
        self.log_interval = int(train_cfg.get("log_interval", 10))
        self.ckpt_interval = int(train_cfg.get("ckpt_interval", 500))
        self.seed = int(train_cfg.get("seed", 0))
        seed_everything(self.seed)

        self.model = model.to(device)

        opt_cfg = cfg["optimizer"]
        decay, no_decay = [], []
        for param in self.model.parameters():
            if not param.requires_grad:
                continue
            (decay if param.dim() >= 2 else no_decay).append(param)
        self.optimizer = torch.optim.AdamW(
            [
                {"params": decay, "weight_decay": float(opt_cfg.get("weight_decay", 0.1))},
                {"params": no_decay, "weight_decay": 0.0},
            ],
            lr=float(opt_cfg["lr"]),
            betas=(float(opt_cfg.get("beta1", 0.9)), float(opt_cfg.get("beta2", 0.95))),
            eps=float(opt_cfg.get("eps", 1e-8)),
        )
        self.base_lr = float(opt_cfg["lr"])

        sched_cfg = cfg["schedule"]
        self.warmup_steps = int(sched_cfg.get("warmup_steps", 0))
        self.max_steps = int(sched_cfg["max_steps"])
        self.min_lr_ratio = float(sched_cfg.get("min_lr_ratio", 0.1))

        self.step = 0
        self.log_path = self.out_dir / "loss.jsonl"

    def lr_at(self, step: int) -> float:
        return cosine_lr(step, self.base_lr, self.warmup_steps, self.max_steps, self.min_lr_ratio)

    def _log(self, record: dict) -> None:
        with open(self.log_path, "a") as fh:
            fh.write(json.dumps(record) + "\n")

    def save_checkpoint(self, name: str | None = None) -> Path:
        state = {
            "model": self.model.state_dict(),
            "optimizer": self.optimizer.state_dict(),
            "step": self.step,
            "config": self.cfg,
            "torch_rng": torch.get_rng_state(),
        }
        if self.device == "cuda":
            state["cuda_rng"] = torch.cuda.get_rng_state_all()
        path = self.out_dir / (name or f"ckpt-{self.step:07d}.pt")
        torch.save(state, path)
        torch.save(state, self.out_dir / "latest.pt")
        return path

    def load_checkpoint(self, path: str) -> None:
        state = torch.load(path, map_location=self.device, weights_only=False)
        self.model.load_state_dict(state["model"])
        self.optimizer.load_state_dict(state["optimizer"])
        self.step = int(state["step"])
        torch.set_rng_state(state["torch_rng"].cpu())
        if self.device == "cuda" and "cuda_rng" in state:
            torch.cuda.set_rng_state_all([r.cpu() for r in state["cuda_rng"]])

    def train(self, batches, until_step: int | None = None) -> list[float]:
        """Advance to until_step, which defaults to schedule.max_steps.
        Returns the mean micro batch loss of every optimizer step taken."""
        target = self.max_steps if until_step is None else min(until_step, self.max_steps)
        losses: list[float] = []
        batch_iter = iter(batches)
        self.model.train()
        start_time = time.time()
        while self.step < target:
            lr = self.lr_at(self.step)
            for group in self.optimizer.param_groups:
                group["lr"] = lr
            self.optimizer.zero_grad(set_to_none=True)
            step_loss = 0.0
            for _ in range(self.grad_accum_steps):
                inputs, targets = next(batch_iter)
                inputs = inputs.to(self.device, non_blocking=True)
                targets = targets.to(self.device, non_blocking=True)
                if self.use_autocast:
                    with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                        _, loss = self.model(inputs, targets)
                else:
                    _, loss = self.model(inputs, targets)
                (loss / self.grad_accum_steps).backward()
                step_loss += loss.item() / self.grad_accum_steps
            if self.grad_clip > 0:
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.grad_clip)
            self.optimizer.step()
            self.step += 1
            losses.append(step_loss)
            if self.step % self.log_interval == 0 or self.step == target:
                self._log(
                    {
                        "step": self.step,
                        "loss": step_loss,
                        "lr": lr,
                        "elapsed_s": round(time.time() - start_time, 3),
                    }
                )
            if self.ckpt_interval > 0 and self.step % self.ckpt_interval == 0:
                self.save_checkpoint()
        if self.step == target:
            self.save_checkpoint()
        return losses
