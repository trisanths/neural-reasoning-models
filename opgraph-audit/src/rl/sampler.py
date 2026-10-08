"""Batched samplers behind the rollout loop.

Two implementations of the same tiny interface. begin(prompts) conditions on
a batch of prompts and returns one proposed next token per sequence;
advance(tokens) appends one token to every sequence and returns the next
proposals. src/rl/env.py drives either one.

ScriptedPolicy recomputes from the full history through a caller supplied
step function. It is slow and exact, and it is what the tests use to pin the
rollout loop against src/evals/interactive.py.

CachedPolicy is the GPU path. It re-runs the TransformerLM's own modules with
a key/value cache, so decoding one token costs one token of compute instead
of re-reading the whole trace. The rollout loop keeps every sequence at the
same length (a sequence reading a served chunk consumes it one token per
iteration, exactly like a sequence that is speaking), so the cache position
is a single scalar for the whole batch and no per-sequence offset bookkeeping
is needed. Prompts do differ in length, so they are padded on the left and a
key mask hides the padding; RoPE encodes relative position, so the uniform
shift left padding introduces changes nothing.

CachedPolicy is verified against the plain model forward in the tests: same
logits, to bf16 tolerance, for the same tokens.
"""

import numpy as np
import torch
import torch.nn.functional as F

from src.train.model import apply_rope

PAD_TOKEN = 0


def sample_from_logits(logits: torch.Tensor, temperature: float, top_k: int,
                       generator: torch.Generator | None) -> torch.Tensor:
    """One token per row. temperature 0 means greedy, ties to the lowest id."""
    if temperature <= 0.0:
        return torch.argmax(logits.float(), dim=-1)
    scaled = logits.float() / float(temperature)
    if top_k and top_k > 0 and top_k < scaled.shape[-1]:
        kth = torch.topk(scaled, top_k, dim=-1).values[:, -1:]
        scaled = scaled.masked_fill(scaled < kth, float("-inf"))
    probs = torch.softmax(scaled, dim=-1)
    return torch.multinomial(probs, num_samples=1, generator=generator).squeeze(-1)


class ScriptedPolicy:
    """Full recompute policy over a step function, for tests and reference.

    step_fn(token_ids) returns next token scores for one sequence. Sampling
    is greedy by default, which makes a rollout reproduce the greedy decode
    of src/evals/interactive.py token for token.
    """

    def __init__(self, step_fn, temperature: float = 0.0, top_k: int = 0,
                 seed: int = 0):
        self.step_fn = step_fn
        self.temperature = float(temperature)
        self.top_k = int(top_k)
        self.rng = np.random.default_rng(seed)
        self.histories: list[list[int]] = []

    def _propose(self) -> list[int]:
        out = []
        for hist in self.histories:
            scores = np.asarray(self.step_fn(hist), dtype=np.float64).reshape(-1)
            if self.temperature <= 0.0:
                out.append(int(np.argmax(scores)))
                continue
            scaled = scores / self.temperature
            if self.top_k > 0 and self.top_k < scaled.size:
                cut = np.partition(scaled, -self.top_k)[-self.top_k]
                scaled = np.where(scaled < cut, -np.inf, scaled)
            scaled = scaled - scaled.max()
            probs = np.exp(scaled)
            probs /= probs.sum()
            out.append(int(self.rng.choice(probs.size, p=probs)))
        return out

    def begin(self, prompts) -> list[int]:
        self.histories = [list(p) for p in prompts]
        return self._propose()

    def advance(self, tokens) -> list[int]:
        for hist, tok in zip(self.histories, tokens):
            hist.append(int(tok))
        return self._propose()


class CachedPolicy:
    """Key/value cached batched decoding over a TransformerLM."""

    def __init__(self, model, device, max_len: int, temperature: float = 1.0,
                 top_k: int = 0, seed: int = 0, dtype=None):
        self.model = model
        self.device = torch.device(device)
        self.max_len = int(max_len)
        if self.max_len > model.cfg.max_seq_len:
            raise ValueError(
                f"max_len {self.max_len} exceeds model max_seq_len "
                f"{model.cfg.max_seq_len}")
        self.temperature = float(temperature)
        self.top_k = int(top_k)
        self.use_autocast = self.device.type == "cuda"
        # The cache holds whatever dtype the attention runs in, so reading it
        # back is a view rather than a per layer copy.
        if dtype is None:
            dtype = torch.bfloat16 if self.use_autocast else torch.float32
        self.dtype = dtype
        self.generator = torch.Generator(device=self.device)
        self.generator.manual_seed(int(seed))
        self.k_cache: list[torch.Tensor] = []
        self.v_cache: list[torch.Tensor] = []
        self.key_ok: torch.Tensor | None = None
        self.last_logits: torch.Tensor | None = None
        self.pos = 0

    def _alloc(self, batch: int) -> None:
        cfg = self.model.cfg
        shape = (batch, cfg.n_heads, self.max_len, cfg.head_dim)
        need = (not self.k_cache or self.k_cache[0].shape[0] != batch
                or self.k_cache[0].shape[2] != self.max_len)
        if need:
            self.k_cache = [torch.zeros(shape, dtype=self.dtype,
                                        device=self.device)
                            for _ in range(cfg.n_layers)]
            self.v_cache = [torch.zeros(shape, dtype=self.dtype,
                                        device=self.device)
                            for _ in range(cfg.n_layers)]

    def _forward(self, ids: torch.Tensor, start_pos: int) -> torch.Tensor:
        """Run the model over ids at positions start_pos.., write the cache,
        and return the logits of the final position only."""
        model = self.model
        cfg = model.cfg
        bsz, seq = ids.shape
        end = start_pos + seq
        cos = model.rope_cos[start_pos:end]
        sin = model.rope_sin[start_pos:end]

        key_ok = self.key_ok[:, :end]
        if seq == 1:
            mask = key_ok.view(bsz, 1, 1, end)
        else:
            rows = torch.arange(start_pos, end, device=self.device).view(-1, 1)
            cols = torch.arange(end, device=self.device).view(1, -1)
            causal = (cols <= rows).view(1, 1, seq, end)
            mask = key_ok.view(bsz, 1, 1, end) & causal

        x = model.tok_emb(ids)
        for li, block in enumerate(model.blocks):
            attn = block.attn
            h = block.attn_norm(x)
            q = attn.wq(h).view(bsz, seq, cfg.n_heads, cfg.head_dim).transpose(1, 2)
            k = attn.wk(h).view(bsz, seq, cfg.n_heads, cfg.head_dim).transpose(1, 2)
            v = attn.wv(h).view(bsz, seq, cfg.n_heads, cfg.head_dim).transpose(1, 2)
            q = apply_rope(q, cos, sin)
            k = apply_rope(k, cos, sin)
            self.k_cache[li][:, :, start_pos:end] = k.to(self.dtype)
            self.v_cache[li][:, :, start_pos:end] = v.to(self.dtype)
            keys = self.k_cache[li][:, :, :end].to(q.dtype)
            values = self.v_cache[li][:, :, :end].to(q.dtype)
            out = F.scaled_dot_product_attention(q, keys, values, attn_mask=mask)
            out = out.transpose(1, 2).reshape(bsz, seq, cfg.d_model)
            x = x + attn.wo(out)
            x = x + block.mlp(block.mlp_norm(x))
        x = model.final_norm(x[:, -1:])
        return model.lm_head(x)[:, -1]

    def _run(self, ids: torch.Tensor, start_pos: int) -> torch.Tensor:
        if self.use_autocast:
            with torch.autocast(device_type="cuda", dtype=self.dtype):
                with torch.no_grad():
                    return self._forward(ids, start_pos)
        with torch.no_grad():
            return self._forward(ids, start_pos)

    def begin(self, prompts) -> list[int]:
        prompts = [list(p) for p in prompts]
        batch = len(prompts)
        width = max(len(p) for p in prompts)
        if width > self.max_len:
            raise ValueError(f"prompt of {width} tokens exceeds max_len "
                             f"{self.max_len}")
        self._alloc(batch)
        padded = np.full((batch, width), PAD_TOKEN, dtype=np.int64)
        ok = np.zeros((batch, self.max_len), dtype=bool)
        for i, p in enumerate(prompts):
            padded[i, width - len(p):] = p
            ok[i, width - len(p):width] = True
        self.key_ok = torch.from_numpy(ok).to(self.device)
        ids = torch.from_numpy(padded).to(self.device)
        logits = self._run(ids, 0)
        self.pos = width
        return self._sample(logits)

    def advance(self, tokens) -> list[int]:
        if self.pos >= self.max_len:
            raise ValueError("cache is full; raise env max_len")
        ids = torch.tensor([[int(t)] for t in tokens], dtype=torch.long,
                           device=self.device)
        self.key_ok[:, self.pos] = True
        logits = self._run(ids, self.pos)
        self.pos += 1
        return self._sample(logits)

    def _sample(self, logits: torch.Tensor) -> list[int]:
        # Kept for the equivalence test against the plain model forward.
        self.last_logits = logits
        picked = sample_from_logits(logits, self.temperature, self.top_k,
                                    self.generator)
        return picked.tolist()
