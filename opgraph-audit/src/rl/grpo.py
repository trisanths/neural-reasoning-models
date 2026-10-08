"""Group-relative policy optimization over the retrieval environment.

For each question the policy writes G independent trajectories. Their
rewards are verifier scores, and the advantage of a trajectory is how far
its reward sits from its own group's mean, in units of the group's spread.
That is the whole critic: no value network, no learned reward model, and no
bootstrapping. A group whose rewards are all equal carries no signal and is
dropped from the batch.

Three things keep the update honest.

Token masking. Only tokens the policy actually emitted contribute to the
loss. Prompt tokens, the served chunk tokens spliced in by the environment,
and the <|result|> markers the environment inserted are all masked out. The
mask is recorded during the rollout, one flag per token, and carried through
padding and target shifting unchanged. Training on retrieved text would
teach the policy to predict documents rather than to ask for them.

A trust region. The surrogate is the clipped ratio of the current policy to
the policy that produced the rollouts, so several inner epochs over one
batch of rollouts stay bounded. With the default single inner epoch the
ratio starts at one and clipping is inert, which is the intended on-policy
case.

A leash to the starting policy. A k3 estimator of the KL to the frozen
reference (exp(d) - d - 1 for d = ref logp minus current logp) is added per
token. It is nonnegative, low variance, and it is what stops the policy from
drifting into a degenerate dialect that happens to score.
"""

import copy
import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

from src.train.trainer import cosine_lr


@dataclass
class GRPOConfig:
    group_size: int = 8
    prompts_per_step: int = 4
    inner_epochs: int = 1
    micro_batch_size: int = 4
    clip_eps: float = 0.2
    kl_coef: float = 0.02
    ent_coef: float = 0.0
    adv_eps: float = 1e-4
    normalize_advantage: bool = True
    drop_zero_variance_groups: bool = True
    lr: float = 1.0e-6
    weight_decay: float = 0.0
    beta1: float = 0.9
    beta2: float = 0.95
    eps: float = 1.0e-8
    grad_clip: float = 1.0
    warmup_steps: int = 10
    max_steps: int = 200
    min_lr_ratio: float = 1.0
    seed: int = 0

    def to_dict(self) -> dict:
        return dict(self.__dict__)


def group_advantages(rewards, group_size: int, eps: float = 1e-4,
                     normalize: bool = True) -> np.ndarray:
    """Group-relative advantages for rewards laid out group by group.

    rewards[i * group_size + j] is the reward of rollout j of group i. The
    advantage is the reward minus the group mean, divided by the group's
    standard deviation plus eps when normalize is set. A group with no
    spread yields exactly zero for every member.
    """
    arr = np.asarray(rewards, dtype=np.float64).reshape(-1)
    if group_size <= 0:
        raise ValueError("group_size must be positive")
    if arr.size % group_size != 0:
        raise ValueError("rewards length is not a multiple of group_size")
    grouped = arr.reshape(-1, group_size)
    centered = grouped - grouped.mean(axis=1, keepdims=True)
    if normalize:
        std = grouped.std(axis=1, keepdims=True)
        centered = np.where(std > 0.0, centered / (std + eps), 0.0)
    return centered.reshape(-1)


def pad_batch(rollouts, device, pad_token: int = 0):
    """Stack rollouts into inputs, targets, and a target-aligned loss mask.

    Position t of the logits predicts token t + 1, so targets drop the first
    token and the mask travels with them. Right padding never reaches the
    loss because its mask entries are zero.
    """
    lengths = [len(r.tokens) for r in rollouts]
    width = max(lengths)
    if width < 2:
        raise ValueError("a rollout needs at least two tokens")
    n = len(rollouts)
    ids = np.full((n, width), pad_token, dtype=np.int64)
    mask = np.zeros((n, width), dtype=np.float32)
    for i, r in enumerate(rollouts):
        ids[i, :len(r.tokens)] = r.tokens
        mask[i, :len(r.mask)] = r.mask
    ids_t = torch.from_numpy(ids).to(device)
    mask_t = torch.from_numpy(mask).to(device)
    return ids_t[:, :-1].contiguous(), ids_t[:, 1:].contiguous(), mask_t[:, 1:].contiguous()


def token_logprobs(model, inputs, targets, want_entropy: bool = False,
                   autocast: bool = True):
    """Log probability of each target token, and optionally the entropy."""
    device_type = inputs.device.type
    ctx = (torch.autocast(device_type=device_type, dtype=torch.bfloat16)
           if autocast and device_type == "cuda" else _NullCtx())
    with ctx:
        logits, _ = model(inputs)
    flat = logits.reshape(-1, logits.shape[-1]).float()
    logp = -F.cross_entropy(flat, targets.reshape(-1), reduction="none")
    logp = logp.view(targets.shape)
    entropy = None
    if want_entropy:
        logp_all = F.log_softmax(flat, dim=-1)
        entropy = -(logp_all.exp() * logp_all).sum(-1).view(targets.shape)
    return logp, entropy


class _NullCtx:
    def __enter__(self):
        return None

    def __exit__(self, *args):
        return False


def grpo_loss(logp, old_logp, ref_logp, advantages, mask, cfg: GRPOConfig,
              entropy=None, denom: float | None = None):
    """Masked GRPO surrogate plus the KL leash, summed over tokens.

    Returns (loss_sum, stats). The caller divides by the batch's total mask
    weight, which is what makes gradient accumulation over microbatches
    equivalent to one big batch.
    """
    adv = advantages.view(-1, 1)
    ratio = torch.exp(logp - old_logp)
    unclipped = ratio * adv
    clipped = torch.clamp(ratio, 1.0 - cfg.clip_eps, 1.0 + cfg.clip_eps) * adv
    pg = -torch.min(unclipped, clipped)
    diff = ref_logp - logp
    kl = torch.exp(diff) - diff - 1.0
    per_token = pg + cfg.kl_coef * kl
    if entropy is not None and cfg.ent_coef != 0.0:
        per_token = per_token - cfg.ent_coef * entropy
    loss_sum = (per_token * mask).sum()
    weight = mask.sum()
    with torch.no_grad():
        clip_frac = (((ratio > 1.0 + cfg.clip_eps) |
                      (ratio < 1.0 - cfg.clip_eps)).float() * mask).sum()
    stats = {
        "pg_sum": float((pg * mask).sum().item()),
        "kl_sum": float((kl * mask).sum().item()),
        "clip_sum": float(clip_frac.item()),
        "ent_sum": (float((entropy * mask).sum().item())
                    if entropy is not None else 0.0),
        "weight": float(weight.item()),
    }
    if denom is not None:
        loss_sum = loss_sum / denom
    return loss_sum, stats


class GRPOTrainer:
    """Optimizer, frozen reference, and the update over a batch of rollouts."""

    def __init__(self, model, cfg: GRPOConfig, out_dir: str,
                 device: str | None = None, ref_model=None):
        self.cfg = cfg
        self.device = torch.device(
            device or ("cuda" if torch.cuda.is_available() else "cpu"))
        self.model = model.to(self.device)
        if ref_model is None:
            ref_model = copy.deepcopy(model)
        self.ref_model = ref_model.to(self.device).eval()
        for p in self.ref_model.parameters():
            p.requires_grad_(False)
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        for stale in self.out_dir.glob("*.pt.tmp"):
            stale.unlink(missing_ok=True)

        decay, no_decay = [], []
        for p in self.model.parameters():
            if p.requires_grad:
                (decay if p.dim() >= 2 else no_decay).append(p)
        self.optimizer = torch.optim.AdamW(
            [{"params": decay, "weight_decay": cfg.weight_decay},
             {"params": no_decay, "weight_decay": 0.0}],
            lr=cfg.lr, betas=(cfg.beta1, cfg.beta2), eps=cfg.eps)
        self.step = 0
        self.autocast = self.device.type == "cuda"

    def lr_at(self, step: int) -> float:
        return cosine_lr(step, self.cfg.lr, self.cfg.warmup_steps,
                         self.cfg.max_steps, self.cfg.min_lr_ratio)

    def select_groups(self, rollouts, advantages):
        """Drop groups whose rewards were all equal; they carry no gradient."""
        g = self.cfg.group_size
        keep_rolls, keep_adv = [], []
        n_groups = len(rollouts) // g
        dropped = 0
        for i in range(n_groups):
            sl = slice(i * g, (i + 1) * g)
            block = advantages[sl]
            if self.cfg.drop_zero_variance_groups and not np.any(block != 0.0):
                dropped += 1
                continue
            keep_rolls.extend(rollouts[sl])
            keep_adv.extend(block.tolist())
        return keep_rolls, np.asarray(keep_adv, dtype=np.float64), dropped

    def _microbatches(self, rollouts, advantages):
        size = max(1, self.cfg.micro_batch_size)
        for start in range(0, len(rollouts), size):
            yield (rollouts[start:start + size],
                   advantages[start:start + size])

    def update(self, rollouts, advantages) -> dict:
        """One optimizer step over a batch of scored rollouts."""
        cfg = self.cfg
        rolls, adv, dropped = self.select_groups(rollouts, advantages)
        if not rolls:
            return {"skipped": True, "dropped_groups": dropped,
                    "n_train_rollouts": 0}

        # Old and reference log probabilities, frozen for the whole update.
        cached = []
        total_weight = 0.0
        self.model.eval()
        with torch.no_grad():
            for chunk, chunk_adv in self._microbatches(rolls, adv):
                inputs, targets, mask = pad_batch(chunk, self.device)
                old_logp, _ = token_logprobs(self.model, inputs, targets,
                                             autocast=self.autocast)
                ref_logp, _ = token_logprobs(self.ref_model, inputs, targets,
                                             autocast=self.autocast)
                cached.append({
                    "inputs": inputs, "targets": targets, "mask": mask,
                    "old_logp": old_logp.detach(), "ref_logp": ref_logp.detach(),
                    "adv": torch.tensor(chunk_adv, dtype=torch.float32,
                                        device=self.device),
                })
                total_weight += float(mask.sum().item())
        if total_weight <= 0.0:
            return {"skipped": True, "dropped_groups": dropped,
                    "n_train_rollouts": len(rolls)}

        self.model.train()
        lr = self.lr_at(self.step)
        for group in self.optimizer.param_groups:
            group["lr"] = lr

        agg = {"pg_sum": 0.0, "kl_sum": 0.0, "clip_sum": 0.0, "ent_sum": 0.0}
        loss_total = 0.0
        for epoch in range(cfg.inner_epochs):
            self.optimizer.zero_grad(set_to_none=True)
            agg = {"pg_sum": 0.0, "kl_sum": 0.0, "clip_sum": 0.0, "ent_sum": 0.0}
            loss_total = 0.0
            for item in cached:
                logp, entropy = token_logprobs(
                    self.model, item["inputs"], item["targets"],
                    want_entropy=cfg.ent_coef != 0.0, autocast=self.autocast)
                loss, stats = grpo_loss(
                    logp, item["old_logp"], item["ref_logp"], item["adv"],
                    item["mask"], cfg, entropy=entropy, denom=total_weight)
                loss.backward()
                loss_total += float(loss.item())
                for k in agg:
                    agg[k] += stats[k]
            grad_norm = torch.nn.utils.clip_grad_norm_(
                self.model.parameters(), cfg.grad_clip)
            self.optimizer.step()
        self.step += 1

        return {
            "skipped": False,
            "loss": loss_total,
            "pg_loss": agg["pg_sum"] / total_weight,
            "kl": agg["kl_sum"] / total_weight,
            "entropy": agg["ent_sum"] / total_weight,
            "clip_frac": agg["clip_sum"] / total_weight,
            "grad_norm": float(grad_norm),
            "lr": lr,
            "n_train_rollouts": len(rolls),
            "dropped_groups": dropped,
            "train_tokens": total_weight,
        }

    # ------------------------------------------------------------ checkpoints

    def save_checkpoint(self, model_config: dict, name: str | None = None) -> Path:
        state = {
            "model": self.model.state_dict(),
            "optimizer": self.optimizer.state_dict(),
            "step": self.step,
            "config": model_config,
            "rl_config": self.cfg.to_dict(),
            "torch_rng": torch.get_rng_state(),
        }
        if self.device.type == "cuda":
            state["cuda_rng"] = torch.cuda.get_rng_state_all()
        path = self.out_dir / (name or f"rl-{self.step:06d}.pt")
        self._atomic_save(state, path)
        self._atomic_save(state, self.out_dir / "latest.pt")
        return path

    @staticmethod
    def _atomic_save(state: dict, path: Path) -> None:
        tmp = path.with_name(path.name + ".tmp")
        torch.save(state, tmp)
        os.replace(tmp, path)

    def load_checkpoint(self, path) -> None:
        state = torch.load(path, map_location=self.device, weights_only=False)
        self.model.load_state_dict(state["model"])
        if "optimizer" in state:
            self.optimizer.load_state_dict(state["optimizer"])
        self.step = int(state.get("step", 0))
        if "torch_rng" in state:
            torch.set_rng_state(state["torch_rng"].cpu())
        if self.device.type == "cuda" and "cuda_rng" in state:
            torch.cuda.set_rng_state_all([r.cpu() for r in state["cuda_rng"]])
