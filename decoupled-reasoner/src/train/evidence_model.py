"""Evidence cross-attention decoder: a large retrieved set read in parallel.

The standard model in src/train/model.py reads evidence by serializing a few
chunks into its context window, so evidence competes with the working
sequence for a quadratic-cost resource. This model separates the two. The
working sequence (question plus answer plus any scratchpad tokens) stays
short and is handled by causal self-attention exactly as before. Evidence
lives in a separate bank of N chunks of chunk_len tokens each, encoded once
by a small shared bidirectional encoder and then read by cross-attention
layers interleaved through the decoder.

Evidence tokens are keys and values only, never queries. That is the RETRO
and Perceiver arrangement, and it is what makes the cost linear: a decoder
of T tokens reading M evidence positions costs O(T * M) in the cross layers
instead of the O((T + M) ** 2) a concatenated context would cost. The
encoder itself is O(N * chunk_len ** 2), quadratic inside a chunk but linear
in the number of chunks, and every chunk is encoded independently so the
result is cacheable across questions that share a bank.

Three pieces beyond plain cross-attention:

  Selectable granularity. evidence_mode "pooled" gives the decoder one
  key-value position per chunk, a masked mean over the chunk's encoder
  states, so M = N. evidence_mode "tokens" exposes every evidence token, so
  M = N * chunk_len. Pooled is cheap enough to carry thousands of chunks;
  tokens keeps the span-level detail an extractive answer needs. Both use
  the same weights, so a model can be trained one way and run the other.

  Chunk provenance. Each chunk's encoder states get a learned chunk-position
  embedding, indexed by the chunk's rank in the bank, and a learned
  reliability embedding bucketed from the chunk's stated reliability. Rank
  carries what the retriever thought; reliability carries what the corpus
  says about the source. Neither is a hard filter, both are just signal the
  cross-attention can use to discount a chunk.

  A gate. Every cross-attention layer multiplies its output by a per-token
  sigmoid gate computed from the decoder state. A pure-reasoning step can
  drive the gate to zero and the layer becomes an exact no-op, which the
  tests check by construction. The bank also carries a learned null slot
  that is always unmasked, so attention has somewhere to go when every
  chunk in a row is padding, and no row can produce a NaN.

Grouped-query cross-attention keeps the evidence key-value tensors small:
xattn_n_kv_heads key-value heads serve n_heads query heads. At N = 256 and
chunk_len = 128 that is the difference between one and eight gigabytes of
key-value activation for a batch of four.

RMSNorm, SwiGLU, the rotary tables, and the decoder's self-attention are
imported from src/train/model.py so the two architectures stay the same
model family.
"""

from dataclasses import dataclass, field

import torch
import torch.nn as nn
import torch.nn.functional as F

from src.train.model import (Attention, ModelConfig, RMSNorm, SwiGLU,
                             apply_rope, precompute_rope)


@dataclass
class EvidenceModelConfig:
    """Sizes for the decoder, the evidence encoder, and the cross-attention.

    The decoder fields mirror ModelConfig exactly, so a config can be read
    against configs/350m.yaml field by field. max_seq_len bounds the working
    sequence only; the evidence bank is bounded by max_chunks and chunk_len.
    """

    vocab_size: int = 32768
    d_model: int = 1024
    n_layers: int = 21
    n_heads: int = 16
    d_ff: int = 2944
    max_seq_len: int = 2048
    rope_theta: float = 10000.0
    norm_eps: float = 1e-5

    # Evidence encoder. It reads the decoder's token embedding through a
    # down projection rather than owning a second vocabulary sized table,
    # which saves d_enc * vocab_size parameters and keeps one token space.
    d_enc: int = 512
    enc_layers: int = 4
    enc_heads: int = 8
    enc_d_ff: int = 1408
    chunk_len: int = 128

    # Cross-attention. A cross layer is inserted after the self-attention of
    # every xattn_every-th block, counting from one, so xattn_every 3 in a
    # 21 layer decoder gives 7 cross layers at blocks 3, 6, ..., 21.
    xattn_every: int = 3
    xattn_n_kv_heads: int = 4
    evidence_mode: str = "pooled"
    max_chunks: int = 1024
    n_reliability_buckets: int = 16
    gate_bias_init: float = 0.0

    def __post_init__(self):
        if self.d_model % self.n_heads != 0:
            raise ValueError("d_model must be divisible by n_heads")
        if self.d_enc % self.enc_heads != 0:
            raise ValueError("d_enc must be divisible by enc_heads")
        if self.n_heads % self.xattn_n_kv_heads != 0:
            raise ValueError("n_heads must be divisible by xattn_n_kv_heads")
        if self.evidence_mode not in ("pooled", "tokens"):
            raise ValueError("evidence_mode must be 'pooled' or 'tokens'")
        if self.xattn_every < 1:
            raise ValueError("xattn_every must be at least 1")

    @property
    def head_dim(self) -> int:
        return self.d_model // self.n_heads

    @property
    def enc_head_dim(self) -> int:
        return self.d_enc // self.enc_heads

    @property
    def xattn_layers(self) -> list[int]:
        """Zero based indices of the decoder blocks that carry a cross layer."""
        return [i for i in range(self.n_layers) if (i + 1) % self.xattn_every == 0]

    def decoder_config(self) -> ModelConfig:
        """The plain ModelConfig the reused self-attention and SwiGLU expect."""
        return ModelConfig(
            vocab_size=self.vocab_size,
            d_model=self.d_model,
            n_layers=self.n_layers,
            n_heads=self.n_heads,
            d_ff=self.d_ff,
            max_seq_len=self.max_seq_len,
            rope_theta=self.rope_theta,
            norm_eps=self.norm_eps,
        )

    def encoder_config(self) -> ModelConfig:
        """A ModelConfig shaped for the encoder, used for its SwiGLU."""
        return ModelConfig(
            vocab_size=self.vocab_size,
            d_model=self.d_enc,
            n_layers=self.enc_layers,
            n_heads=self.enc_heads,
            d_ff=self.enc_d_ff,
            max_seq_len=self.chunk_len,
            rope_theta=self.rope_theta,
            norm_eps=self.norm_eps,
        )


@dataclass
class EvidenceMemory:
    """Encoded evidence ready for the cross layers.

    states has shape (B, 1 + M, d_enc); position zero is the learned null
    slot. mask has shape (B, 1 + M) and is True where a position may be
    attended. n_chunks and n_positions record what the bank held, for the
    throughput accounting in scripts/bench_evidence.py.
    """

    states: torch.Tensor
    mask: torch.Tensor
    mode: str
    n_chunks: int
    n_positions: int


class BiAttention(nn.Module):
    """Bidirectional self-attention inside one evidence chunk.

    Rotary positions run over the chunk, not the corpus, so a chunk encodes
    the same way wherever it lands in the bank. Every query is allowed to
    attend to its own position even when that position is padding, which
    keeps a fully padded chunk from producing NaN rows.
    """

    def __init__(self, cfg: EvidenceModelConfig):
        super().__init__()
        self.n_heads = cfg.enc_heads
        self.head_dim = cfg.enc_head_dim
        d = cfg.d_enc
        self.wq = nn.Linear(d, d, bias=False)
        self.wk = nn.Linear(d, d, bias=False)
        self.wv = nn.Linear(d, d, bias=False)
        self.wo = nn.Linear(d, d, bias=False)

    def forward(self, x, cos, sin, key_mask):
        bsz, seq_len, dim = x.shape
        q = self.wq(x).view(bsz, seq_len, self.n_heads, self.head_dim).transpose(1, 2)
        k = self.wk(x).view(bsz, seq_len, self.n_heads, self.head_dim).transpose(1, 2)
        v = self.wv(x).view(bsz, seq_len, self.n_heads, self.head_dim).transpose(1, 2)
        q = apply_rope(q, cos, sin)
        k = apply_rope(k, cos, sin)
        eye = torch.eye(seq_len, dtype=torch.bool, device=x.device)
        attn_mask = key_mask[:, None, None, :] | eye[None, None, :, :]
        out = F.scaled_dot_product_attention(q, k, v, attn_mask=attn_mask)
        out = out.transpose(1, 2).reshape(bsz, seq_len, dim)
        return self.wo(out)


class EncoderBlock(nn.Module):
    def __init__(self, cfg: EvidenceModelConfig):
        super().__init__()
        enc_cfg = cfg.encoder_config()
        self.attn_norm = RMSNorm(cfg.d_enc, cfg.norm_eps)
        self.attn = BiAttention(cfg)
        self.mlp_norm = RMSNorm(cfg.d_enc, cfg.norm_eps)
        self.mlp = SwiGLU(enc_cfg)

    def forward(self, x, cos, sin, key_mask):
        x = x + self.attn(self.attn_norm(x), cos, sin, key_mask)
        x = x + self.mlp(self.mlp_norm(x))
        return x


class EvidenceEncoder(nn.Module):
    """Encodes every chunk of the bank independently and identically.

    Input is token ids of shape (B, N, L) with a validity mask of the same
    shape. Chunks are folded into the batch dimension, so the cost is linear
    in N and the encoding of a chunk does not depend on the rest of the bank.
    Chunk rank and reliability embeddings are added after the stack, which is
    what lets a cached chunk encoding be reused at a different rank.
    """

    def __init__(self, cfg: EvidenceModelConfig, tok_emb: nn.Embedding):
        super().__init__()
        self.cfg = cfg
        self.tok_emb = tok_emb
        self.in_proj = nn.Linear(cfg.d_model, cfg.d_enc, bias=False)
        self.layers = nn.ModuleList(EncoderBlock(cfg) for _ in range(cfg.enc_layers))
        self.final_norm = RMSNorm(cfg.d_enc, cfg.norm_eps)
        self.chunk_pos = nn.Embedding(cfg.max_chunks, cfg.d_enc)
        self.reliability_emb = nn.Embedding(cfg.n_reliability_buckets, cfg.d_enc)
        cos, sin = precompute_rope(cfg.enc_head_dim, cfg.chunk_len, cfg.rope_theta)
        self.register_buffer("rope_cos", cos, persistent=False)
        self.register_buffer("rope_sin", sin, persistent=False)

    def reliability_bucket(self, reliability: torch.Tensor) -> torch.Tensor:
        n = self.cfg.n_reliability_buckets
        idx = (reliability.clamp(0.0, 1.0) * n).long()
        return idx.clamp(0, n - 1)

    def forward(self, evidence_ids, evidence_mask, reliability=None):
        cfg = self.cfg
        bsz, n_chunks, seq_len = evidence_ids.shape
        if seq_len > cfg.chunk_len:
            raise ValueError(f"chunk length {seq_len} exceeds chunk_len {cfg.chunk_len}")
        if n_chunks > cfg.max_chunks:
            raise ValueError(f"bank of {n_chunks} chunks exceeds max_chunks {cfg.max_chunks}")
        flat_ids = evidence_ids.reshape(bsz * n_chunks, seq_len)
        flat_mask = evidence_mask.reshape(bsz * n_chunks, seq_len)
        x = self.in_proj(self.tok_emb(flat_ids))
        for layer in self.layers:
            x = layer(x, self.rope_cos, self.rope_sin, flat_mask)
        x = self.final_norm(x)
        x = x.view(bsz, n_chunks, seq_len, cfg.d_enc)

        ranks = torch.arange(n_chunks, device=evidence_ids.device)
        x = x + self.chunk_pos(ranks)[None, :, None, :]
        if reliability is not None:
            buckets = self.reliability_bucket(reliability)
            x = x + self.reliability_emb(buckets)[:, :, None, :]
        return x


class CrossAttention(nn.Module):
    """Decoder tokens query the evidence memory. Grouped key-value heads.

    The gate is a per-token sigmoid of a linear read of the decoder state.
    At gate zero the layer contributes exactly nothing, so a decoder step
    that needs no evidence pays only the compute, never the representation.
    """

    def __init__(self, cfg: EvidenceModelConfig):
        super().__init__()
        self.n_heads = cfg.n_heads
        self.n_kv_heads = cfg.xattn_n_kv_heads
        self.head_dim = cfg.head_dim
        kv_dim = self.n_kv_heads * self.head_dim
        self.wq = nn.Linear(cfg.d_model, cfg.d_model, bias=False)
        self.wk = nn.Linear(cfg.d_enc, kv_dim, bias=False)
        self.wv = nn.Linear(cfg.d_enc, kv_dim, bias=False)
        self.wo = nn.Linear(cfg.d_model, cfg.d_model, bias=False)
        self.gate_proj = nn.Linear(cfg.d_model, 1, bias=True)
        nn.init.zeros_(self.gate_proj.weight)
        nn.init.constant_(self.gate_proj.bias, cfg.gate_bias_init)

    def gate(self, x: torch.Tensor, override: float | None) -> torch.Tensor:
        if override is not None:
            return torch.full(
                (x.shape[0], x.shape[1], 1), float(override),
                dtype=x.dtype, device=x.device,
            )
        return torch.sigmoid(self.gate_proj(x))

    def forward(self, x, memory, memory_mask, gate_override=None):
        if gate_override is not None and float(gate_override) == 0.0:
            # Exact no-op, and it skips the evidence read entirely.
            return torch.zeros_like(x)
        bsz, seq_len, dim = x.shape
        gate = self.gate(x, gate_override)
        n_pos = memory.shape[1]
        q = self.wq(x).view(bsz, seq_len, self.n_heads, self.head_dim).transpose(1, 2)
        k = self.wk(memory).view(bsz, n_pos, self.n_kv_heads, self.head_dim).transpose(1, 2)
        v = self.wv(memory).view(bsz, n_pos, self.n_kv_heads, self.head_dim).transpose(1, 2)
        attn_mask = memory_mask[:, None, None, :]
        out = F.scaled_dot_product_attention(
            q, k, v, attn_mask=attn_mask, enable_gqa=self.n_kv_heads != self.n_heads
        )
        out = out.transpose(1, 2).reshape(bsz, seq_len, dim)
        return gate * self.wo(out)


class EvidenceBlock(nn.Module):
    """Self-attention, optional evidence cross-attention, then SwiGLU."""

    def __init__(self, cfg: EvidenceModelConfig, with_xattn: bool):
        super().__init__()
        dec_cfg = cfg.decoder_config()
        self.attn_norm = RMSNorm(cfg.d_model, cfg.norm_eps)
        self.attn = Attention(dec_cfg)
        self.xattn = None
        if with_xattn:
            self.xattn_norm = RMSNorm(cfg.d_model, cfg.norm_eps)
            self.xattn = CrossAttention(cfg)
        self.mlp_norm = RMSNorm(cfg.d_model, cfg.norm_eps)
        self.mlp = SwiGLU(dec_cfg)

    def forward(self, x, cos, sin, memory=None, memory_mask=None, gate_override=None):
        x = x + self.attn(self.attn_norm(x), cos, sin)
        if self.xattn is not None and memory is not None:
            x = x + self.xattn(self.xattn_norm(x), memory, memory_mask, gate_override)
        x = x + self.mlp(self.mlp_norm(x))
        return x


class EvidenceTransformerLM(nn.Module):
    """Decoder over a working sequence with cross-attention over an evidence bank.

    forward takes the working token ids plus the bank and returns logits and,
    when targets are given, the mean cross entropy over target positions that
    are not IGNORE_INDEX. Evidence tokens never enter the working sequence, so
    they are structurally unpredictable rather than merely masked out.
    """

    IGNORE_INDEX = -100

    def __init__(self, cfg: EvidenceModelConfig):
        super().__init__()
        self.cfg = cfg
        self.tok_emb = nn.Embedding(cfg.vocab_size, cfg.d_model)
        self.encoder = EvidenceEncoder(cfg, self.tok_emb)
        self.null_evidence = nn.Parameter(torch.zeros(cfg.d_enc))
        xattn_at = set(cfg.xattn_layers)
        self.blocks = nn.ModuleList(
            EvidenceBlock(cfg, with_xattn=i in xattn_at) for i in range(cfg.n_layers)
        )
        self.final_norm = RMSNorm(cfg.d_model, cfg.norm_eps)
        self.lm_head = nn.Linear(cfg.d_model, cfg.vocab_size, bias=False)
        cos, sin = precompute_rope(cfg.head_dim, cfg.max_seq_len, cfg.rope_theta)
        self.register_buffer("rope_cos", cos, persistent=False)
        self.register_buffer("rope_sin", sin, persistent=False)
        self.apply(self._init_weights)
        scale = 0.02 / (2 * cfg.n_layers) ** 0.5
        for block in self.blocks:
            nn.init.normal_(block.attn.wo.weight, mean=0.0, std=scale)
            nn.init.normal_(block.mlp.w_down.weight, mean=0.0, std=scale)
            if block.xattn is not None:
                nn.init.normal_(block.xattn.wo.weight, mean=0.0, std=scale)
                nn.init.zeros_(block.xattn.gate_proj.weight)
                nn.init.constant_(block.xattn.gate_proj.bias, cfg.gate_bias_init)
        nn.init.normal_(self.null_evidence, mean=0.0, std=0.02)

    @staticmethod
    def _init_weights(module: nn.Module):
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def encode_evidence(self, evidence_ids, evidence_mask=None, reliability=None,
                        chunk_mask=None, mode: str | None = None) -> EvidenceMemory:
        """Encode a bank once so several decoder calls can share it.

        evidence_ids has shape (B, N, L). evidence_mask marks real tokens,
        chunk_mask marks banks shorter than N. mode overrides the config's
        pooled or tokens granularity for this call; the weights are the same
        either way.
        """
        cfg = self.cfg
        mode = mode or cfg.evidence_mode
        if mode not in ("pooled", "tokens"):
            raise ValueError("mode must be 'pooled' or 'tokens'")
        bsz, n_chunks, seq_len = evidence_ids.shape
        if evidence_mask is None:
            evidence_mask = torch.ones_like(evidence_ids, dtype=torch.bool)
        evidence_mask = evidence_mask.bool()
        if chunk_mask is not None:
            evidence_mask = evidence_mask & chunk_mask.bool()[:, :, None]

        states = self.encoder(evidence_ids, evidence_mask, reliability)
        if mode == "pooled":
            weights = evidence_mask.to(states.dtype)
            denom = weights.sum(-1, keepdim=True).clamp(min=1.0)
            pooled = (states * weights[..., None]).sum(2) / denom
            flat_states = pooled
            flat_mask = evidence_mask.any(-1)
            n_positions = n_chunks
        else:
            flat_states = states.reshape(bsz, n_chunks * seq_len, cfg.d_enc)
            flat_mask = evidence_mask.reshape(bsz, n_chunks * seq_len)
            n_positions = n_chunks * seq_len

        null = self.null_evidence.to(flat_states.dtype).expand(bsz, 1, cfg.d_enc)
        flat_states = torch.cat([null, flat_states], dim=1)
        ones = torch.ones(bsz, 1, dtype=torch.bool, device=flat_mask.device)
        flat_mask = torch.cat([ones, flat_mask], dim=1)
        return EvidenceMemory(flat_states, flat_mask, mode, n_chunks, n_positions)

    def forward(self, input_ids, evidence_ids=None, evidence_mask=None,
                reliability=None, chunk_mask=None, targets=None,
                gate_override=None, memory: EvidenceMemory | None = None,
                mode: str | None = None):
        seq_len = input_ids.shape[1]
        if seq_len > self.cfg.max_seq_len:
            raise ValueError(
                f"sequence length {seq_len} exceeds max_seq_len {self.cfg.max_seq_len}"
            )
        if memory is None and evidence_ids is not None:
            memory = self.encode_evidence(
                evidence_ids, evidence_mask, reliability, chunk_mask, mode
            )
        mem_states = memory.states if memory is not None else None
        mem_mask = memory.mask if memory is not None else None

        x = self.tok_emb(input_ids)
        for block in self.blocks:
            x = block(x, self.rope_cos, self.rope_sin, mem_states, mem_mask, gate_override)
        x = self.final_norm(x)
        logits = self.lm_head(x)
        loss = None
        if targets is not None:
            loss = F.cross_entropy(
                logits.float().view(-1, self.cfg.vocab_size),
                targets.reshape(-1),
                ignore_index=self.IGNORE_INDEX,
            )
        return logits, loss

    def param_breakdown(self) -> dict:
        """Parameter counts split by role, for the fair comparison table."""
        groups = {
            "embedding": 0,
            "lm_head": 0,
            "decoder": 0,
            "encoder": 0,
            "cross_attention": 0,
        }
        for name, param in self.named_parameters():
            n = param.numel()
            if name.startswith("tok_emb"):
                groups["embedding"] += n
            elif name.startswith("lm_head"):
                groups["lm_head"] += n
            elif name.startswith("encoder") or name == "null_evidence":
                groups["encoder"] += n
            elif ".xattn" in name:
                groups["cross_attention"] += n
            else:
                groups["decoder"] += n
        groups["total"] = sum(v for k, v in groups.items() if k != "total")
        groups["non_embedding"] = groups["total"] - groups["embedding"] - groups["lm_head"]
        return groups

    def num_params(self, non_embedding: bool = True) -> int:
        b = self.param_breakdown()
        return b["non_embedding"] if non_embedding else b["total"]


def config_from_yaml(cfg: dict) -> EvidenceModelConfig:
    """Build a model config from the `model` section of a yaml config."""
    fields = {f for f in EvidenceModelConfig.__dataclass_fields__}
    unknown = set(cfg) - fields
    if unknown:
        raise ValueError(f"unknown model config keys: {sorted(unknown)}")
    return EvidenceModelConfig(**cfg)


def cross_attention_flops(cfg: EvidenceModelConfig, seq_len: int, n_chunks: int,
                          mode: str | None = None) -> dict:
    """Analytic forward FLOPs, split into the parts that scale with evidence.

    Reported per sequence, counting a multiply-accumulate as two FLOPs. This
    is the deterministic companion to the wall clock timing: the evidence
    terms here are exactly linear in n_chunks, so a timing curve that bends
    away from this shape is a bug in the implementation, not in the design.
    """
    mode = mode or cfg.evidence_mode
    d, d_enc, L = cfg.d_model, cfg.d_enc, cfg.chunk_len
    n_xattn = len(cfg.xattn_layers)
    evidence_tokens = n_chunks * L
    n_positions = n_chunks if mode == "pooled" else evidence_tokens

    # Encoder: projections and MLP are linear in evidence tokens, the
    # attention term is quadratic inside a chunk and linear across chunks.
    enc_proj = 2 * evidence_tokens * (4 * d_enc * d_enc + 3 * d_enc * cfg.enc_d_ff)
    enc_attn = 2 * n_chunks * cfg.enc_layers * 2 * L * L * d_enc
    enc_embed_proj = 2 * evidence_tokens * d * d_enc

    kv_dim = cfg.xattn_n_kv_heads * cfg.head_dim
    xattn_kv = 2 * n_xattn * n_positions * 2 * d_enc * kv_dim
    xattn_q = 2 * n_xattn * seq_len * 2 * d * d
    xattn_scores = 2 * n_xattn * 2 * seq_len * n_positions * d

    self_attn = 2 * cfg.n_layers * (seq_len * 4 * d * d + 2 * seq_len * seq_len * d)
    mlp = 2 * cfg.n_layers * seq_len * 3 * d * cfg.d_ff
    head = 2 * seq_len * d * cfg.vocab_size

    evidence_linear = enc_proj + enc_attn + enc_embed_proj + xattn_kv + xattn_scores
    return {
        "encoder": enc_proj + enc_attn + enc_embed_proj,
        "cross_attention": xattn_kv + xattn_q + xattn_scores,
        "decoder": self_attn + mlp + head,
        "evidence_scaling": evidence_linear,
        "total": evidence_linear + xattn_q + self_attn + mlp + head,
        "evidence_tokens": evidence_tokens,
        "n_positions": n_positions,
    }
