"""Training loop: AdamW, cosine schedule with warmup, gradient accumulation,
bf16 autocast on cuda, gradient clipping, periodic checkpoints, jsonl loss
logging, deterministic seeding, and resume from checkpoint.

When the model config sets model.recurrent.train_loop_sampling, the loop count
is drawn once per optimizer step from its own generator and held across every
micro batch of that step, so the sampled depth is reproducible from the train
seed and independent of the data order.

Data parallel. When src.train.distributed has joined a torchrun process group
the model is wrapped in DistributedDataParallel and every micro batch except
the last of an optimizer step runs under no_sync, so gradients are all reduced
once per optimizer step rather than once per micro batch. The logged loss is
the mean over ranks, and only rank zero writes checkpoints and loss.jsonl. The
loop count generator is seeded from the train seed alone, never from the rank,
so every rank runs the same depth on the same step. Checkpoints hold the state
dict of the unwrapped module, so a distributed run and a single GPU run write
and read the same file."""

import inspect
import json
import math
import os
import time
from contextlib import nullcontext
from pathlib import Path

import numpy as np
import torch
from torch.nn.parallel import DistributedDataParallel

from src.train.distributed import (
    all_reduce_mean,
    barrier,
    get_rank,
    get_world_size,
    is_distributed,
    resolve_batch_plan,
    strip_ddp_prefix,
)
from src.train.model import TransformerLM

# Offset so the loop count stream never coincides with the global torch stream
# seeded from the same number.
LOOP_SEED_OFFSET = 9973


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

    def __init__(
        self,
        model: TransformerLM,
        cfg: dict,
        out_dir: str,
        device: str | None = None,
        micro_batch_size: int | None = None,
        grad_accum_steps: int | None = None,
    ):
        self.cfg = cfg
        self.out_dir = Path(out_dir)
        self.rank = get_rank()
        self.world_size = get_world_size()
        self.is_main = self.rank == 0
        self.out_dir.mkdir(parents=True, exist_ok=True)
        # Remove temp files left behind by an interrupted checkpoint write.
        if self.is_main:
            for stale in self.out_dir.glob("*.pt.tmp"):
                stale.unlink(missing_ok=True)
        if device is None:
            if is_distributed() and torch.cuda.is_available():
                device = f"cuda:{torch.cuda.current_device()}"
            else:
                device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = device
        self.on_cuda = str(device).startswith("cuda")
        self.use_autocast = self.on_cuda

        train_cfg = cfg["train"]
        # The config states a global batch in sequences per optimizer step and
        # that number is divided across ranks. resolve_batch_plan asserts
        # global == micro * accum * world and raises on anything else.
        self.plan = resolve_batch_plan(
            train_cfg,
            self.world_size,
            micro_batch_size=micro_batch_size,
            grad_accum_steps=grad_accum_steps,
        )
        self.grad_accum_steps = self.plan.grad_accum_steps
        self.micro_batch_size = self.plan.micro_batch_size
        self.grad_clip = float(train_cfg.get("grad_clip", 1.0))
        self.log_interval = int(train_cfg.get("log_interval", 10))
        self.ckpt_interval = int(train_cfg.get("ckpt_interval", 500))
        self.seed = int(train_cfg.get("seed", 0))
        seed_everything(self.seed)

        self.model = model.to(device)

        # DistributedDataParallel wraps the module for gradient reduction only.
        # self.model stays the eager module, so parameters, optimizer state and
        # checkpoint keys are the same objects and the same names they are on
        # one GPU. Buffer broadcast is off because the only buffers are the
        # rope tables, which every rank computes identically at construction.
        self.ddp: DistributedDataParallel | None = None
        if is_distributed():
            ddp_kwargs = {}
            if self.on_cuda:
                ddp_kwargs["device_ids"] = [torch.cuda.current_device()]
                ddp_kwargs["output_device"] = torch.cuda.current_device()
            # torch 2.13 renamed broadcast_buffers to forward_sync_buffers and
            # deprecated the old spelling. Either way the answer is no: the
            # only buffers are the rope tables, which every rank computes from
            # the same config.
            if "forward_sync_buffers" in inspect.signature(DistributedDataParallel).parameters:
                ddp_kwargs["forward_sync_buffers"] = False
            else:
                ddp_kwargs["broadcast_buffers"] = False
            self.ddp = DistributedDataParallel(
                self.model,
                find_unused_parameters=bool(train_cfg.get("ddp_find_unused_parameters", False)),
                gradient_as_bucket_view=bool(train_cfg.get("ddp_gradient_as_bucket_view", False)),
                **ddp_kwargs,
            )

        # torch.compile wraps the forward pass only; parameters, optimizer
        # state, and checkpoints stay on the eager module, so state_dict
        # keys are unchanged and checkpoints resume with or without compile.
        self.compile = bool(train_cfg.get("compile", False))
        target = self.ddp if self.ddp is not None else self.model
        self.run_model = torch.compile(target) if self.compile else target

        # Depth recurrence. Sampling the loop count changes the traced graph,
        # so with compile on dynamo keeps one compiled variant per distinct
        # loop count; the cache limit is raised to cover the sampling range.
        recurrent = getattr(self.model.cfg, "recurrent", None)
        self.loop_sampling = recurrent is not None and recurrent.train_loop_sampling is not None
        self.loop_generator = torch.Generator()
        self.loop_generator.manual_seed(self.seed + LOOP_SEED_OFFSET)
        if self.compile and self.loop_sampling:
            # Imported as _dynamo rather than torch._dynamo: the latter would
            # make torch a local name for the whole of __init__.
            from torch import _dynamo

            span = int(recurrent.train_loop_sampling[1]) - int(recurrent.train_loop_sampling[0]) + 1
            _dynamo.config.cache_size_limit = max(_dynamo.config.cache_size_limit, 4 * span + 8)

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
        self._pending_loader_state: dict | None = None
        # Set by train() to whatever it is iterating, so save_checkpoint can
        # record the data position without the two having to agree on a
        # signature. A caller that stubs out save_checkpoint stays working.
        self._loader = None

    def lr_at(self, step: int) -> float:
        return cosine_lr(step, self.base_lr, self.warmup_steps, self.max_steps, self.min_lr_ratio)

    def _log(self, record: dict) -> None:
        if not self.is_main:
            return
        with open(self.log_path, "a") as fh:
            fh.write(json.dumps(record) + "\n")

    def save_checkpoint(self, name: str | None = None, loader=None) -> Path | None:
        """Write the checkpoint from rank zero and hold every rank at a barrier
        until it lands, so no rank races ahead of a half written file. Returns
        the path on rank zero and None elsewhere. The loader position comes
        from whatever train() is iterating unless one is passed here."""
        path = self.out_dir / (name or f"ckpt-{self.step:07d}.pt")
        if loader is None:
            loader = self._loader
        if self.is_main:
            state = {
                # The unwrapped module, so the keys carry no DDP prefix and the
                # file loads into a single GPU run unchanged.
                "model": self.model.state_dict(),
                "optimizer": self.optimizer.state_dict(),
                "step": self.step,
                "config": self.cfg,
                "torch_rng": torch.get_rng_state(),
                "loop_rng": self.loop_generator.get_state(),
                "world_size": self.world_size,
                "batch_plan": {
                    "global_batch_size": self.plan.global_batch_size,
                    "micro_batch_size": self.plan.micro_batch_size,
                    "grad_accum_steps": self.plan.grad_accum_steps,
                    "world_size": self.plan.world_size,
                },
            }
            if loader is not None and hasattr(loader, "state_dict"):
                state["loader"] = loader.state_dict()
            if self.on_cuda:
                state["cuda_rng"] = torch.cuda.get_rng_state_all()
            self._atomic_save(state, path)
            self._atomic_save(state, self.out_dir / "latest.pt")
        barrier()
        return path if self.is_main else None

    def _atomic_save(self, state: dict, path: Path) -> None:
        """Write to a temp file in the same directory, then rename over path,
        so a crash mid-write never leaves a truncated checkpoint behind."""
        tmp = path.with_name(path.name + ".tmp")
        torch.save(state, tmp)
        os.replace(tmp, path)

    def load_checkpoint(self, path: str) -> None:
        state = torch.load(path, map_location=self.device, weights_only=False)
        # Accept a checkpoint written from a wrapped model by any other tool.
        self.model.load_state_dict(strip_ddp_prefix(state["model"]))
        self.optimizer.load_state_dict(state["optimizer"])
        self.step = int(state["step"])
        torch.set_rng_state(state["torch_rng"].cpu())
        # Checkpoints written before depth recurrence have no loop stream.
        if "loop_rng" in state:
            self.loop_generator.set_state(state["loop_rng"].cpu())
        if self.on_cuda and "cuda_rng" in state:
            saved = [r.cpu() for r in state["cuda_rng"]]
            current = torch.cuda.get_rng_state_all()
            # A run that resumes on a different number of visible devices gets
            # its own device count back, filled from what was saved.
            if len(saved) == len(current):
                torch.cuda.set_rng_state_all(saved)
            else:
                torch.cuda.set_rng_state_all([saved[0].clone() for _ in current])
        loader_state = state.get("loader")
        if loader_state is not None:
            if int(loader_state.get("world_size", 1)) == self.world_size:
                self._pending_loader_state = loader_state
            elif self.is_main:
                print(
                    f"checkpoint loader position was recorded at world size "
                    f"{loader_state.get('world_size')} and this run is world size "
                    f"{self.world_size}; the rank regions differ, so data sampling "
                    "restarts from the top of each region"
                )

    def train(self, batches, until_step: int | None = None, save_at_end: bool = True) -> list[float]:
        """Advance to until_step, which defaults to schedule.max_steps.
        Returns the mean micro batch loss of every optimizer step taken,
        averaged over ranks. save_at_end=False skips the closing checkpoint,
        which is what throughput benchmarks want."""
        target = self.max_steps if until_step is None else min(until_step, self.max_steps)
        if self._pending_loader_state is not None and hasattr(batches, "load_state_dict"):
            batches.load_state_dict(self._pending_loader_state)
            self._pending_loader_state = None
        self._loader = batches if hasattr(batches, "state_dict") else None
        losses: list[float] = []
        batch_iter = iter(batches)
        self.model.train()
        last_micro = self.grad_accum_steps - 1
        start_time = time.time()
        while self.step < target:
            lr = self.lr_at(self.step)
            for group in self.optimizer.param_groups:
                group["lr"] = lr
            loops = self.model.sample_loops(self.loop_generator) if self.loop_sampling else None
            self.optimizer.zero_grad(set_to_none=True)
            step_loss = 0.0
            for micro in range(self.grad_accum_steps):
                inputs, targets = next(batch_iter)
                inputs = inputs.to(self.device, non_blocking=True)
                targets = targets.to(self.device, non_blocking=True)
                # Hold the all reduce back until the last micro batch, so the
                # gradients of one optimizer step cross the wire once instead
                # of once per accumulation step.
                sync = self.ddp is None or micro == last_micro
                with nullcontext() if sync else self.ddp.no_sync():
                    if self.use_autocast:
                        with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                            _, loss = self.run_model(inputs, targets)
                    else:
                        _, loss = self.run_model(inputs, targets)
                    (loss / self.grad_accum_steps).backward()
                step_loss += loss.item() / self.grad_accum_steps
            if self.grad_clip > 0:
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.grad_clip)
            self.optimizer.step()
            self.step += 1
            # Every rank saw a different slice of the global batch, so the
            # logged number is the mean over ranks of the mean micro loss.
            step_loss = all_reduce_mean(step_loss, self.device)
            losses.append(step_loss)
            if self.step % self.log_interval == 0 or self.step == target:
                record = {
                    "step": self.step,
                    "loss": step_loss,
                    "lr": lr,
                    "elapsed_s": round(time.time() - start_time, 3),
                }
                if self.world_size > 1:
                    record["world_size"] = self.world_size
                if self.on_cuda:
                    record["peak_mem_gb"] = round(
                        torch.cuda.max_memory_allocated(self.device) / 1024**3, 3
                    )
                if loops is not None:
                    record["loops"] = loops
                self._log(record)
            if self.ckpt_interval > 0 and self.step % self.ckpt_interval == 0:
                self.save_checkpoint()
        if save_at_end and self.step == target:
            self.save_checkpoint()
        return losses
