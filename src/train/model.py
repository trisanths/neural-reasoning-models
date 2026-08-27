"""Llama style decoder only transformer, with optional looped depth.

Rotary position embeddings, RMSNorm, SwiGLU feed forward, and untied input
and output embeddings. Sizes come from configs/*.yaml, which mirror the table
in SPEC.md section 5.

The model also supports depth recurrence: a prelude of P unique layers, a
recurrent core of R unique layers applied L times with tied weights, and a
coda of C unique layers. Effective computational depth is then P + R*L + C
while the parameter count stays P + R + C layers, so test time compute
decouples from parameter count. Recurrence is off unless model.recurrent is
set in the config, and with it off this file builds exactly the same modules
in exactly the same order as before, so old checkpoints load and produce
bit identical logits.
"""

from contextlib import contextmanager
from dataclasses import asdict, dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.utils.checkpoint


@dataclass
class RecurrentConfig:
    """Depth recurrence settings, the model.recurrent block of a config.

    core_layers      unique layers inside the looped core
    loops            default loop count at train and eval time
    prelude_layers   unique layers run once before the core
    coda_layers      unique layers run once after the core
    loop_embedding   per iteration FiLM scale and shift on the core input
    train_loop_sampling  [min, max] inclusive, sample the loop count per
                     optimizer step so the model is trained to be correct at
                     any depth, or null to always use loops
    backprop_last_k  backprop through only the last K iterations, running the
                     earlier ones under no_grad, or null for all iterations
    grad_checkpoint  recompute each loop iteration in the backward pass
    inject_prelude   feed the prelude output into every iteration through a
                     concat adapter, which is what keeps the prelude and the
                     embeddings on the gradient path when backprop_last_k is
                     set
    loop_slots       rows in the loop embedding table, defaults to the largest
                     loop count the config can ask for; larger loop counts at
                     generate time reuse the last row
    """

    core_layers: int = 0
    loops: int = 1
    prelude_layers: int = 0
    coda_layers: int = 0
    loop_embedding: bool = True
    train_loop_sampling: list | None = None
    backprop_last_k: int | None = None
    grad_checkpoint: bool = False
    inject_prelude: bool = True
    loop_slots: int | None = None

    def __post_init__(self):
        if self.core_layers < 1:
            raise ValueError("recurrent.core_layers must be at least 1")
        if self.loops < 1:
            raise ValueError("recurrent.loops must be at least 1")
        if self.prelude_layers < 0 or self.coda_layers < 0:
            raise ValueError("prelude_layers and coda_layers must be non negative")
        if self.backprop_last_k is not None and self.backprop_last_k < 1:
            raise ValueError("recurrent.backprop_last_k must be at least 1 or null")
        if self.train_loop_sampling is not None:
            lo, hi = self.train_loop_sampling
            if lo < 1 or hi < lo:
                raise ValueError("recurrent.train_loop_sampling must be [min, max] with 1 <= min <= max")
        if self.loop_slots is None:
            self.loop_slots = self.max_loops
        elif self.loop_slots < 1:
            raise ValueError("recurrent.loop_slots must be at least 1")

    @property
    def max_loops(self) -> int:
        if self.train_loop_sampling is None:
            return self.loops
        return max(self.loops, int(self.train_loop_sampling[1]))

    @property
    def unique_layers(self) -> int:
        return self.prelude_layers + self.core_layers + self.coda_layers


@dataclass
class ModelConfig:
    vocab_size: int = 32768
    d_model: int = 256
    n_layers: int = 8
    n_heads: int = 8
    d_ff: int = 704
    max_seq_len: int = 1024
    rope_theta: float = 10000.0
    norm_eps: float = 1e-5
    recurrent: RecurrentConfig | dict | None = None

    def __post_init__(self):
        if self.d_model % self.n_heads != 0:
            raise ValueError("d_model must be divisible by n_heads")
        if isinstance(self.recurrent, dict):
            self.recurrent = RecurrentConfig(**self.recurrent)
        if self.recurrent is not None and self.recurrent.unique_layers != self.n_layers:
            raise ValueError(
                "prelude_layers + core_layers + coda_layers must equal n_layers, got "
                f"{self.recurrent.unique_layers} against n_layers {self.n_layers}"
            )

    @property
    def head_dim(self) -> int:
        return self.d_model // self.n_heads

    def effective_depth(self, loops: int | None = None) -> int:
        """Layer applications per forward pass."""
        if self.recurrent is None:
            return self.n_layers
        rec = self.recurrent
        n = rec.loops if loops is None else loops
        return rec.prelude_layers + rec.core_layers * n + rec.coda_layers


class RMSNorm(nn.Module):
    def __init__(self, dim: int, eps: float):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        normed = x.float() * torch.rsqrt(x.float().pow(2).mean(-1, keepdim=True) + self.eps)
        return normed.type_as(x) * self.weight


def precompute_rope(head_dim: int, max_seq_len: int, theta: float):
    inv_freq = 1.0 / (theta ** (torch.arange(0, head_dim, 2, dtype=torch.float32) / head_dim))
    positions = torch.arange(max_seq_len, dtype=torch.float32)
    freqs = torch.outer(positions, inv_freq)
    return torch.cos(freqs), torch.sin(freqs)


def apply_rope(x: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor) -> torch.Tensor:
    """Rotate the two halves of each head dimension. x has shape (B, H, T, hd)."""
    seq_len = x.shape[2]
    cos = cos[:seq_len].view(1, 1, seq_len, -1)
    sin = sin[:seq_len].view(1, 1, seq_len, -1)
    xf = x.float()
    half = xf.shape[-1] // 2
    x1, x2 = xf[..., :half], xf[..., half:]
    rotated = torch.cat([x1 * cos - x2 * sin, x2 * cos + x1 * sin], dim=-1)
    return rotated.type_as(x)


class Attention(nn.Module):
    def __init__(self, cfg: ModelConfig):
        super().__init__()
        self.n_heads = cfg.n_heads
        self.head_dim = cfg.head_dim
        self.wq = nn.Linear(cfg.d_model, cfg.d_model, bias=False)
        self.wk = nn.Linear(cfg.d_model, cfg.d_model, bias=False)
        self.wv = nn.Linear(cfg.d_model, cfg.d_model, bias=False)
        self.wo = nn.Linear(cfg.d_model, cfg.d_model, bias=False)

    def forward(self, x: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor) -> torch.Tensor:
        bsz, seq_len, dim = x.shape
        q = self.wq(x).view(bsz, seq_len, self.n_heads, self.head_dim).transpose(1, 2)
        k = self.wk(x).view(bsz, seq_len, self.n_heads, self.head_dim).transpose(1, 2)
        v = self.wv(x).view(bsz, seq_len, self.n_heads, self.head_dim).transpose(1, 2)
        q = apply_rope(q, cos, sin)
        k = apply_rope(k, cos, sin)
        out = F.scaled_dot_product_attention(q, k, v, is_causal=True)
        out = out.transpose(1, 2).reshape(bsz, seq_len, dim)
        return self.wo(out)


class SwiGLU(nn.Module):
    def __init__(self, cfg: ModelConfig):
        super().__init__()
        self.w_gate = nn.Linear(cfg.d_model, cfg.d_ff, bias=False)
        self.w_up = nn.Linear(cfg.d_model, cfg.d_ff, bias=False)
        self.w_down = nn.Linear(cfg.d_ff, cfg.d_model, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.w_down(F.silu(self.w_gate(x)) * self.w_up(x))


class Block(nn.Module):
    def __init__(self, cfg: ModelConfig):
        super().__init__()
        self.attn_norm = RMSNorm(cfg.d_model, cfg.norm_eps)
        self.attn = Attention(cfg)
        self.mlp_norm = RMSNorm(cfg.d_model, cfg.norm_eps)
        self.mlp = SwiGLU(cfg)

    def forward(self, x: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor) -> torch.Tensor:
        x = x + self.attn(self.attn_norm(x), cos, sin)
        x = x + self.mlp(self.mlp_norm(x))
        return x


class TransformerLM(nn.Module):
    def __init__(self, cfg: ModelConfig):
        super().__init__()
        self.cfg = cfg
        self.tok_emb = nn.Embedding(cfg.vocab_size, cfg.d_model)
        self.blocks = nn.ModuleList(Block(cfg) for _ in range(cfg.n_layers))
        self.final_norm = RMSNorm(cfg.d_model, cfg.norm_eps)
        self.lm_head = nn.Linear(cfg.d_model, cfg.vocab_size, bias=False)
        rec = cfg.recurrent
        # The loop adapter and the loop embedding table exist only under
        # recurrence. Building nothing here when recurrence is off keeps the
        # init RNG stream, the module order, and the state dict keys byte for
        # byte identical to the plain model.
        if rec is not None and rec.inject_prelude:
            self.loop_adapter = nn.Linear(2 * cfg.d_model, cfg.d_model, bias=False)
        if rec is not None and rec.loop_embedding:
            self.loop_film = nn.Parameter(torch.zeros(rec.loop_slots, 2 * cfg.d_model))
        cos, sin = precompute_rope(cfg.head_dim, cfg.max_seq_len, cfg.rope_theta)
        self.register_buffer("rope_cos", cos, persistent=False)
        self.register_buffer("rope_sin", sin, persistent=False)
        self.apply(self._init_weights)
        # Residual output projections get a smaller init so the residual stream
        # variance stays flat with depth. Under recurrence the core runs
        # rec.loops times, so scale by the effective depth rather than by the
        # unique layer count.
        depth = cfg.effective_depth()
        scale = 0.02 / (2 * depth) ** 0.5
        for block in self.blocks:
            nn.init.normal_(block.attn.wo.weight, mean=0.0, std=scale)
            nn.init.normal_(block.mlp.w_down.weight, mean=0.0, std=scale)
        if rec is not None and rec.inject_prelude:
            # The loop state half of the adapter starts as the identity, so the
            # residual stream passes through iteration one unchanged. The
            # prelude half starts small but nonzero, at the same scale as the
            # residual output projections. Zero there would be tidier, but it
            # makes d(loss)/d(prelude output) exactly zero, so under
            # backprop_last_k the embeddings and the prelude would get no
            # gradient at all on the first step and would only come alive once
            # the adapter itself had moved. A small nonzero init keeps them on
            # the gradient path from step one, which is the entire reason the
            # injection exists.
            with torch.no_grad():
                self.loop_adapter.weight.normal_(mean=0.0, std=scale)
                self.loop_adapter.weight[:, : cfg.d_model].copy_(torch.eye(cfg.d_model))
        # loop_film stays at zero, which is scale 1 and shift 0, so an
        # untrained loop embedding is the identity.
        self._loops_override: int | None = None
        # Plain lists of the same Block objects held by self.blocks, so the
        # forward pass never slices a ModuleList and the state dict keys stay
        # blocks.N.*. Assigning a list does not register the modules twice.
        if rec is None:
            self.prelude_blocks, self.core_blocks, self.coda_blocks = [], [], []
        else:
            start = rec.prelude_layers
            stop = start + rec.core_layers
            self.prelude_blocks = [self.blocks[i] for i in range(start)]
            self.core_blocks = [self.blocks[i] for i in range(start, stop)]
            self.coda_blocks = [self.blocks[i] for i in range(stop, cfg.n_layers)]

    @staticmethod
    def _init_weights(module: nn.Module):
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    # ---------------- loop count control ----------------

    @property
    def recurrent(self) -> RecurrentConfig | None:
        return self.cfg.recurrent

    def resolve_loops(self, loops: int | None = None) -> int:
        """The loop count a forward pass would use: explicit argument first,
        then any standing override, then the config default."""
        rec = self.cfg.recurrent
        if rec is None:
            return 1
        if loops is not None:
            return int(loops)
        if self._loops_override is not None:
            return int(self._loops_override)
        return rec.loops

    def set_loops(self, loops: int | None) -> None:
        """Set a standing loop count, or None to fall back to the config."""
        if loops is not None and int(loops) < 1:
            raise ValueError("loops must be at least 1")
        self._loops_override = None if loops is None else int(loops)

    @contextmanager
    def loops_override(self, loops: int | None):
        """Temporarily run at a different depth, for test time compute dials."""
        previous = self._loops_override
        try:
            self.set_loops(loops)
            yield self
        finally:
            self._loops_override = previous

    def sample_loops(self, generator: torch.Generator | None = None) -> int:
        """Draw a loop count for one optimizer step and make it the standing
        override. Uniform over recurrent.train_loop_sampling inclusive; a no op
        that returns the current count when sampling is off."""
        rec = self.cfg.recurrent
        if rec is None or rec.train_loop_sampling is None:
            return self.resolve_loops()
        lo, hi = int(rec.train_loop_sampling[0]), int(rec.train_loop_sampling[1])
        drawn = int(torch.randint(lo, hi + 1, (1,), generator=generator).item())
        self.set_loops(drawn)
        return drawn

    # ---------------- forward ----------------

    def _core_once(self, h, e, cos, sin, index: int):
        rec = self.cfg.recurrent
        if rec.inject_prelude:
            h = self.loop_adapter(torch.cat([h, e], dim=-1))
        if rec.loop_embedding:
            row = self.loop_film[min(index, rec.loop_slots - 1)]
            scale, shift = row.chunk(2, dim=-1)
            h = h * (1.0 + scale) + shift
        for block in self.core_blocks:
            h = block(h, cos, sin)
        return h

    def _run_recurrent(self, x, cos, sin, loops: int):
        rec = self.cfg.recurrent
        for block in self.prelude_blocks:
            x = block(x, cos, sin)
        e = x
        k = rec.backprop_last_k
        truncate = self.training and torch.is_grad_enabled() and k is not None and k < loops
        use_ckpt = (
            rec.grad_checkpoint
            and self.training
            and torch.is_grad_enabled()
        )
        for i in range(loops):
            detached = truncate and i < loops - k
            if detached:
                with torch.no_grad():
                    x = self._core_once(x, e, cos, sin, i)
                x = x.detach()
            elif use_ckpt:
                x = torch.utils.checkpoint.checkpoint(
                    self._core_once, x, e, cos, sin, i, use_reentrant=False
                )
            else:
                x = self._core_once(x, e, cos, sin, i)
        for block in self.coda_blocks:
            x = block(x, cos, sin)
        return x

    def forward(self, idx: torch.Tensor, targets: torch.Tensor | None = None, loops: int | None = None):
        seq_len = idx.shape[1]
        if seq_len > self.cfg.max_seq_len:
            raise ValueError(f"sequence length {seq_len} exceeds max_seq_len {self.cfg.max_seq_len}")
        x = self.tok_emb(idx)
        if self.cfg.recurrent is None:
            for block in self.blocks:
                x = block(x, self.rope_cos, self.rope_sin)
        else:
            x = self._run_recurrent(x, self.rope_cos, self.rope_sin, self.resolve_loops(loops))
        x = self.final_norm(x)
        logits = self.lm_head(x)
        loss = None
        if targets is not None:
            loss = F.cross_entropy(
                logits.float().view(-1, self.cfg.vocab_size), targets.reshape(-1)
            )
        return logits, loss

    # ---------------- bookkeeping ----------------

    def num_params(self, non_embedding: bool = True) -> int:
        total = sum(p.numel() for p in self.parameters())
        if non_embedding:
            total -= self.tok_emb.weight.numel()
            total -= self.lm_head.weight.numel()
        return total

    def describe(self, loops: int | None = None) -> dict:
        """Parameter counts and effective depth, for logs and bench reports."""
        rec = self.cfg.recurrent
        n = self.resolve_loops(loops) if rec is not None else None
        return {
            "params_total": self.num_params(non_embedding=False),
            "params_non_embedding": self.num_params(),
            "unique_layers": self.cfg.n_layers,
            "loops": n,
            "effective_depth": self.cfg.effective_depth(n),
            "recurrent": asdict(rec) if rec is not None else None,
        }
