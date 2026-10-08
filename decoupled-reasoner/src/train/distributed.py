"""Process group setup and batch arithmetic for data parallel training.

torchrun exports RANK, LOCAL_RANK, WORLD_SIZE, MASTER_ADDR and MASTER_PORT.
init_distributed joins the group when those variables are present and returns
without creating one when they are not, so a plain `python -m src.train.cli`
run follows the same code path it followed before this module existed. Under
torchrun the group is created even at world size one, which is what makes the
world size one equivalence test meaningful: the same script goes through
DistributedDataParallel, no_sync and the logging all reduce, and still has to
produce the same losses.

Batch convention. A config states the global batch in sequences per optimizer
step. That number is divided across ranks, never multiplied by them:

    global_batch_size == batch_size * grad_accum_steps * world_size

batch_size is the per rank micro batch and grad_accum_steps is derived from
the world size at startup. The identity is asserted before the first step, so
a world size that does not divide the global batch fails immediately instead
of quietly training on a different token budget.
"""

import os
from dataclasses import dataclass

import torch
import torch.distributed as dist

# The state dict of a DistributedDataParallel wrapper carries this prefix on
# every key. Checkpoints written here never carry it, because the trainer
# always takes the state dict of the unwrapped module, but checkpoints written
# by other tools may.
DDP_PREFIX = "module."


# ---------------- environment ----------------


def env_world_size() -> int:
    return int(os.environ.get("WORLD_SIZE", "1"))


def env_rank() -> int:
    return int(os.environ.get("RANK", "0"))


def env_local_rank() -> int:
    return int(os.environ.get("LOCAL_RANK", "0"))


def launched_by_torchrun() -> bool:
    """True when the rendezvous variables torchrun sets are all present."""
    return all(k in os.environ for k in ("RANK", "WORLD_SIZE", "MASTER_ADDR"))


# ---------------- group state ----------------


def is_distributed() -> bool:
    return dist.is_available() and dist.is_initialized()


def get_world_size() -> int:
    return dist.get_world_size() if is_distributed() else 1


def get_rank() -> int:
    return dist.get_rank() if is_distributed() else 0


def is_main_process() -> bool:
    return get_rank() == 0


def default_device() -> str:
    if torch.cuda.is_available():
        return f"cuda:{env_local_rank()}" if launched_by_torchrun() else "cuda"
    return "cpu"


def init_distributed(backend: str | None = None, device: str | None = None) -> dict:
    """Join the torchrun process group when one is configured.

    Returns the rank, local rank, world size and device this process should
    use. Safe to call more than once and safe to call when there is no group,
    in which case it reports a world of one and initializes nothing. Pass
    device="cpu" to keep a group off the GPUs, which is how the tests run a
    real gloo group on a box whose GPUs belong to somebody else.
    """
    if is_distributed():
        return _info(device)
    if not launched_by_torchrun():
        return {
            "distributed": False,
            "rank": 0,
            "local_rank": 0,
            "world_size": 1,
            "device": device or default_device(),
            "backend": None,
        }
    local_rank = env_local_rank()
    use_cuda = torch.cuda.is_available() if device is None else str(device).startswith("cuda")
    if use_cuda:
        torch.cuda.set_device(local_rank)
        backend = backend or "nccl"
    else:
        backend = backend or "gloo"
    dist.init_process_group(backend=backend, world_size=env_world_size(), rank=env_rank())
    return _info(device)


def _info(device: str | None = None) -> dict:
    if device is None:
        device = f"cuda:{torch.cuda.current_device()}" if torch.cuda.is_available() else "cpu"
    return {
        "distributed": True,
        "rank": dist.get_rank(),
        "local_rank": env_local_rank(),
        "world_size": dist.get_world_size(),
        "device": device,
        "backend": dist.get_backend(),
    }


def destroy_distributed() -> None:
    """Tear the group down. A no op when there is no group."""
    if is_distributed():
        barrier()
        dist.destroy_process_group()


def barrier() -> None:
    if not is_distributed():
        return
    if dist.get_backend() == "nccl":
        dist.barrier(device_ids=[torch.cuda.current_device()])
    else:
        dist.barrier()


def all_reduce_mean(value: float, device: str | torch.device) -> float:
    """Average a python scalar across ranks. Returns it unchanged when there
    is no group. float64 keeps the round trip exact at world size one, where
    the reduction is a division by 1.0."""
    if not is_distributed():
        return value
    tensor = torch.tensor([value], dtype=torch.float64, device=device)
    dist.all_reduce(tensor, op=dist.ReduceOp.SUM)
    return float(tensor.item()) / dist.get_world_size()


# ---------------- checkpoint keys ----------------


def strip_ddp_prefix(state_dict: dict) -> dict:
    """Drop the DistributedDataParallel key prefix so a checkpoint written by
    a wrapped model loads into a bare model."""
    if not any(k.startswith(DDP_PREFIX) for k in state_dict):
        return state_dict
    return {
        (k[len(DDP_PREFIX):] if k.startswith(DDP_PREFIX) else k): v
        for k, v in state_dict.items()
    }


def add_ddp_prefix(state_dict: dict) -> dict:
    """Add the wrapper prefix, for loading a bare checkpoint straight into a
    DistributedDataParallel object rather than into its inner module."""
    if all(k.startswith(DDP_PREFIX) for k in state_dict):
        return state_dict
    return {DDP_PREFIX + k: v for k, v in state_dict.items()}


# ---------------- batch arithmetic ----------------


@dataclass(frozen=True)
class BatchPlan:
    """How one optimizer step is split up.

    global_batch_size  sequences per optimizer step, summed over every rank
    micro_batch_size   sequences per forward pass on one rank
    grad_accum_steps   forward passes per rank per optimizer step
    world_size         ranks
    """

    global_batch_size: int
    micro_batch_size: int
    grad_accum_steps: int
    world_size: int

    def tokens_per_step(self, seq_len: int) -> int:
        return self.global_batch_size * seq_len

    def describe(self) -> str:
        return (
            f"global batch {self.global_batch_size} seq = micro {self.micro_batch_size}"
            f" x accum {self.grad_accum_steps} x world {self.world_size}"
        )


class BatchPlanError(ValueError):
    """Raised when a config and a world size cannot be reconciled."""


def resolve_batch_plan(
    train_cfg: dict,
    world_size: int,
    micro_batch_size: int | None = None,
    grad_accum_steps: int | None = None,
) -> BatchPlan:
    """Work out the per rank accumulation for this world size.

    train.global_batch_size is the source of truth when present. A config that
    predates the key states the same quantity as batch_size * grad_accum_steps
    at world size one, so that product is the fallback. Every failure here is
    loud: a world size that does not divide the global batch is a silently
    wrong token budget, which is the exact bug this function exists to stop.
    """
    if world_size < 1:
        raise BatchPlanError(f"world_size must be at least 1, got {world_size}")

    micro = int(micro_batch_size if micro_batch_size is not None else train_cfg["batch_size"])
    if micro < 1:
        raise BatchPlanError(f"train.batch_size must be at least 1, got {micro}")

    stated_accum = train_cfg.get("grad_accum_steps")
    stated_global = train_cfg.get("global_batch_size")
    if stated_global is not None and stated_accum is not None:
        # Both keys present, so they have to agree at world size one, where
        # the config was written. Disagreement means the config drifted.
        legacy = int(train_cfg["batch_size"]) * int(stated_accum)
        if legacy != int(stated_global):
            raise BatchPlanError(
                f"config train section is inconsistent: global_batch_size "
                f"{stated_global} but batch_size {train_cfg['batch_size']} x "
                f"grad_accum_steps {stated_accum} = {legacy}. global_batch_size is "
                "sequences per optimizer step summed over ranks, so at world size "
                "one it must equal batch_size x grad_accum_steps."
            )

    if grad_accum_steps is not None:
        # An explicit accumulation is the caller stating the shape they want,
        # so the global batch follows from it. src.train.cli reports the
        # difference when the config asked for something else.
        accum = int(grad_accum_steps)
        if accum < 1:
            raise BatchPlanError(f"grad_accum_steps override must be at least 1, got {accum}")
        global_batch = micro * accum * world_size
    else:
        if stated_global is not None:
            global_batch = int(stated_global)
        else:
            global_batch = micro * int(stated_accum if stated_accum is not None else 1)
        if global_batch < 1:
            raise BatchPlanError(f"global batch must be at least 1, got {global_batch}")
        per_step = micro * world_size
        if global_batch % per_step != 0:
            raise BatchPlanError(
                f"global_batch_size {global_batch} is not divisible by micro batch "
                f"{micro} x world size {world_size} = {per_step}. Pick a world size "
                "or a micro batch that divides the global batch; the global batch "
                "is split across ranks, it is not multiplied by them."
            )
        accum = global_batch // per_step
        if accum < 1:
            raise BatchPlanError(
                f"world size {world_size} with micro batch {micro} already exceeds "
                f"the global batch {global_batch}; there is nothing left to accumulate"
            )

    product = micro * accum * world_size
    if product != global_batch:
        raise BatchPlanError(
            f"batch plan does not close: micro {micro} x accum {accum} x world "
            f"{world_size} = {product}, expected global_batch_size {global_batch}"
        )
    return BatchPlan(
        global_batch_size=global_batch,
        micro_batch_size=micro,
        grad_accum_steps=accum,
        world_size=world_size,
    )
