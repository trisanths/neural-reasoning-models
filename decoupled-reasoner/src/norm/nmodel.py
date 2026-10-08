"""The normalizer: an encoder-decoder transformer with no world knowledge.

The claim this file exists to test is that turning surface text into a typed
structure is perception and not reasoning, so the network that does it should
be far smaller than a language model. Nothing here is pretrained and nothing
here is told what a page means. It reads a token sequence and writes a token
sequence, and everything the structure will later be used for happens in
`src/norm/interp.py` instead.

Four sizes are defined so the accuracy against parameters curve is measured
rather than asserted. `SIZES` is the sweep; `count_params` reports the total
and the count without the embedding tables, because a vocabulary of two
thousand words is not the part of the model anyone is arguing about.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import torch
import torch.nn.functional as F
from torch import nn


@dataclass
class Config:
    d_model: int = 256
    n_head: int = 8
    n_enc: int = 4
    n_dec: int = 4
    d_ff: int = 1024
    max_src: int = 1288
    max_tgt: int = 328
    dropout: float = 0.0
    src_vocab: int = 0
    tgt_vocab: int = 0


SIZES = {
    "xs": dict(d_model=64, n_head=2, n_enc=2, n_dec=2, d_ff=256),
    "s": dict(d_model=128, n_head=4, n_enc=3, n_dec=3, d_ff=512),
    "m": dict(d_model=256, n_head=8, n_enc=4, n_dec=4, d_ff=1024),
    "l": dict(d_model=512, n_head=8, n_enc=6, n_dec=6, d_ff=2048),
}


class MultiHeadAttention(nn.Module):
    def __init__(self, d, h, dropout=0.0):
        super().__init__()
        assert d % h == 0
        self.h, self.dk = h, d // h
        self.q = nn.Linear(d, d, bias=False)
        self.k = nn.Linear(d, d, bias=False)
        self.v = nn.Linear(d, d, bias=False)
        self.o = nn.Linear(d, d, bias=False)
        self.p = dropout

    def _split(self, x):
        b, n, _ = x.shape
        return x.view(b, n, self.h, self.dk).transpose(1, 2)

    def forward(self, x, mem=None, mask=None, causal=False):
        src = x if mem is None else mem
        q = self._split(self.q(x))
        k = self._split(self.k(src))
        v = self._split(self.v(src))
        y = F.scaled_dot_product_attention(
            q, k, v, attn_mask=mask, is_causal=causal,
            dropout_p=self.p if self.training else 0.0)
        b, _, n, _ = y.shape
        return self.o(y.transpose(1, 2).reshape(b, n, self.h * self.dk))


class FeedForward(nn.Module):
    def __init__(self, d, dff, dropout=0.0):
        super().__init__()
        self.a = nn.Linear(d, dff)
        self.b = nn.Linear(dff, d)
        self.drop = nn.Dropout(dropout)

    def forward(self, x):
        return self.b(self.drop(F.gelu(self.a(x))))


class EncoderLayer(nn.Module):
    def __init__(self, c: Config):
        super().__init__()
        self.n1 = nn.LayerNorm(c.d_model)
        self.at = MultiHeadAttention(c.d_model, c.n_head, c.dropout)
        self.n2 = nn.LayerNorm(c.d_model)
        self.ff = FeedForward(c.d_model, c.d_ff, c.dropout)

    def forward(self, x, mask):
        x = x + self.at(self.n1(x), mask=mask)
        return x + self.ff(self.n2(x))


class DecoderLayer(nn.Module):
    def __init__(self, c: Config):
        super().__init__()
        self.n1 = nn.LayerNorm(c.d_model)
        self.sa = MultiHeadAttention(c.d_model, c.n_head, c.dropout)
        self.n2 = nn.LayerNorm(c.d_model)
        self.ca = MultiHeadAttention(c.d_model, c.n_head, c.dropout)
        self.n3 = nn.LayerNorm(c.d_model)
        self.ff = FeedForward(c.d_model, c.d_ff, c.dropout)

    def forward(self, x, mem, src_mask):
        x = x + self.sa(self.n1(x), causal=True)
        x = x + self.ca(self.n2(x), mem=mem, mask=src_mask)
        return x + self.ff(self.n3(x))


class Normalizer(nn.Module):
    def __init__(self, c: Config):
        super().__init__()
        self.c = c
        d = c.d_model
        self.src_emb = nn.Embedding(c.src_vocab, d)
        self.tgt_emb = nn.Embedding(c.tgt_vocab, d)
        self.src_pos = nn.Embedding(c.max_src, d)
        self.tgt_pos = nn.Embedding(c.max_tgt, d)
        self.enc = nn.ModuleList([EncoderLayer(c) for _ in range(c.n_enc)])
        self.dec = nn.ModuleList([DecoderLayer(c) for _ in range(c.n_dec)])
        self.enc_out = nn.LayerNorm(d)
        self.dec_out = nn.LayerNorm(d)
        self.head = nn.Linear(d, c.tgt_vocab, bias=False)
        self.head.weight = self.tgt_emb.weight
        self.apply(self._init)

    @staticmethod
    def _init(m):
        if isinstance(m, nn.Linear):
            nn.init.normal_(m.weight, std=0.02)
            if m.bias is not None:
                nn.init.zeros_(m.bias)
        elif isinstance(m, nn.Embedding):
            nn.init.normal_(m.weight, std=0.02)

    def encode(self, src, src_pad):
        b, n = src.shape
        pos = torch.arange(n, device=src.device)
        x = self.src_emb(src) + self.src_pos(pos)[None]
        mask = (~src_pad)[:, None, None, :]
        for layer in self.enc:
            x = layer(x, mask)
        return self.enc_out(x), mask

    def decode(self, tgt, mem, src_mask):
        b, n = tgt.shape
        pos = torch.arange(n, device=tgt.device)
        x = self.tgt_emb(tgt) + self.tgt_pos(pos)[None]
        for layer in self.dec:
            x = layer(x, mem, src_mask)
        return self.head(self.dec_out(x))

    def forward(self, src, src_pad, tgt_in):
        mem, mask = self.encode(src, src_pad)
        return self.decode(tgt_in, mem, mask)


def count_params(model: nn.Module) -> dict:
    total = sum(p.numel() for p in model.parameters())
    emb = 0
    for name, p in model.named_parameters():
        if name.startswith(("src_emb", "tgt_emb", "src_pos", "tgt_pos")):
            emb += p.numel()
    return {"total": total, "embeddings": emb, "non_embedding": total - emb}


def build(size: str, src_vocab: int, tgt_vocab: int, **kw) -> Normalizer:
    cfg = Config(src_vocab=src_vocab, tgt_vocab=tgt_vocab,
                 **{**SIZES[size], **kw})
    return Normalizer(cfg)
