"""Optimization for the evidence model.

Two entry points, for two purposes.

train_evidence_steps is the short loop the unit tests and the bench use: a
fixed list of batches, a fixed number of steps, no checkpoints, no logging.

EvidenceTrainer is the real one. It subclasses src/train/trainer.py's Trainer
so a lane inherits the whole run-directory contract the block-4 tooling
depends on: the same cosine schedule, the same AdamW parameter grouping, the
same atomic checkpoint write, the same latest.pt, the same loss.jsonl. Only
the micro-batch body differs, because a batch here carries an evidence bank
and not a (inputs, targets) pair. That is what lets sync_loop.sh prune its
checkpoints, select_ckpt.py plan a resume from them, and status.sh read its
progress, with no special case for this lane.
"""

import time

import torch

from src.train.trainer import Trainer, cosine_lr, seed_everything


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


class EvidenceTrainer(Trainer):
    """Trainer over EvidenceBatch objects.

    Everything except the micro-batch body is inherited. torch.compile is
    left off by default for this lane: the working sequence is padded to the
    longest row of each batch, so its shape changes from step to step and
    dynamo would recompile against it. Setting train.compile true still
    works, it is simply not the default.
    """

    def __init__(self, model, cfg: dict, out_dir: str, device: str | None = None,
                 evidence_mode: str | None = None):
        super().__init__(model, cfg, out_dir, device=device)
        self.evidence_mode = evidence_mode
        self.tokens_seen = 0
        self.evidence_tokens_seen = 0

    def save_checkpoint(self, name: str | None = None):
        """Same checkpoint as the base trainer plus the token counters.

        Written in one pass rather than by reopening what the base class
        wrote: these are 4.5 GB files and a read-modify-rewrite would treble
        the I/O of every checkpoint interval. Without the counters a resumed
        lane would report answer_tokens_total from zero, and that is the
        first number anyone comparing this lane to the control reads.
        """
        state = {
            "model": self.model.state_dict(),
            "optimizer": self.optimizer.state_dict(),
            "step": self.step,
            "config": self.cfg,
            "torch_rng": torch.get_rng_state(),
            "loop_rng": self.loop_generator.get_state(),
            "tokens_seen": self.tokens_seen,
            "evidence_tokens_seen": self.evidence_tokens_seen,
        }
        if self.device == "cuda":
            state["cuda_rng"] = torch.cuda.get_rng_state_all()
        path = self.out_dir / (name or f"ckpt-{self.step:07d}.pt")
        self._atomic_save(state, path)
        self._atomic_save(state, self.out_dir / "latest.pt")
        return path

    def load_checkpoint(self, path) -> None:
        state = torch.load(path, map_location=self.device, weights_only=False)
        self.model.load_state_dict(state["model"])
        self.optimizer.load_state_dict(state["optimizer"])
        self.step = int(state["step"])
        torch.set_rng_state(state["torch_rng"].cpu())
        if "loop_rng" in state:
            self.loop_generator.set_state(state["loop_rng"].cpu())
        if self.device == "cuda" and "cuda_rng" in state:
            torch.cuda.set_rng_state_all([r.cpu() for r in state["cuda_rng"]])
        self.tokens_seen = int(state.get("tokens_seen", 0))
        self.evidence_tokens_seen = int(state.get("evidence_tokens_seen", 0))

    def train(self, batches, until_step: int | None = None) -> list:
        """Advance to until_step, defaulting to schedule.max_steps.

        Returns the mean micro-batch loss of every optimizer step taken. The
        logged record carries the supervised answer tokens and the evidence
        tokens read, because for this lane the answer tokens are the budget
        that matters and the evidence tokens are the thing being claimed.
        """
        target = self.max_steps if until_step is None else min(until_step, self.max_steps)
        losses: list = []
        batch_iter = iter(batches)
        self.model.train()
        start_time = time.time()
        while self.step < target:
            lr = self.lr_at(self.step)
            for group in self.optimizer.param_groups:
                group["lr"] = lr
            self.optimizer.zero_grad(set_to_none=True)
            step_loss = 0.0
            step_answer_tokens = 0
            step_evidence_tokens = 0
            step_gold = 0
            step_rows = 0
            for _ in range(self.grad_accum_steps):
                batch = next(batch_iter).to(self.device)
                step_answer_tokens += batch.n_answer_tokens
                step_evidence_tokens += batch.n_evidence_tokens
                step_gold += int(batch.gold_present.sum())
                step_rows += int(batch.gold_present.numel())
                if self.use_autocast:
                    with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                        _, loss = forward_batch(self.run_model, batch, self.evidence_mode)
                else:
                    _, loss = forward_batch(self.run_model, batch, self.evidence_mode)
                (loss / self.grad_accum_steps).backward()
                step_loss += loss.item() / self.grad_accum_steps
            if self.grad_clip > 0:
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.grad_clip)
            self.optimizer.step()
            self.step += 1
            self.tokens_seen += step_answer_tokens
            self.evidence_tokens_seen += step_evidence_tokens
            losses.append(step_loss)
            if self.step % self.log_interval == 0 or self.step == target:
                self._log({
                    "step": self.step,
                    "loss": step_loss,
                    "lr": lr,
                    "elapsed_s": round(time.time() - start_time, 3),
                    "answer_tokens": step_answer_tokens,
                    "evidence_tokens": step_evidence_tokens,
                    "answer_tokens_total": self.tokens_seen,
                    "evidence_tokens_total": self.evidence_tokens_seen,
                    "gold_rate": round(step_gold / max(1, step_rows), 4),
                })
            if self.ckpt_interval > 0 and self.step % self.ckpt_interval == 0:
                self.save_checkpoint()
        if self.step == target:
            self.save_checkpoint()
        return losses
