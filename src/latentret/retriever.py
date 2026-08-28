"""A retriever a latent query can address, and the path back into the loop.

The retriever is deliberately the simplest thing with a differentiable path
from a hidden state to a document choice: every document is embedded once with
the model's own token embedding table, mean pooled over its real tokens, and
projected into a small retrieval space; the score is a dot product. BM25 would
be a better retriever and admits no latent query at all, which is the point.

The injection is where this differs from every retrieval result in the project.
The scores become a distribution over documents, and log p(d) is added to the
attention logits of every token of document d in one cross-attention pass from
the working sequence into the concatenated document tokens. Retrieval and
attention are then the same softmax: an uncertain retriever mixes documents in
proportion to its belief, gradients reach the document choice through the
content that arrived, and the result is added to the residual stream rather than
appended to the token stream.
"""

from __future__ import annotations

import math

import torch
import torch.nn as nn
import torch.nn.functional as F

from src.train.model import RMSNorm


def masked_mean(x: torch.Tensor, mask: torch.Tensor, dim: int) -> torch.Tensor:
    """Mean of x over dim, counting only positions where mask is True."""
    m = mask.unsqueeze(-1).to(x.dtype)
    return (x * m).sum(dim) / m.sum(dim).clamp(min=1.0)


class LatentRetriever(nn.Module):
    """Dot product retrieval over mean pooled documents.

    Queries come from three places, and the projection they go through is the
    thing being compared: a latent query gets its own projection from the
    recurrent state, while a text query (the question, or the model's own
    decoded distribution) goes through the same encoder as the documents, which
    makes it an ordinary dense bi-encoder.
    """

    def __init__(self, d_model: int, d_ret: int, norm_eps: float = 1e-5,
                 decoded_topk: int = 8):
        super().__init__()
        self.doc_norm = RMSNorm(d_model, norm_eps)
        self.doc_proj = nn.Linear(d_model, d_ret, bias=False)
        self.state_norm = RMSNorm(d_model, norm_eps)
        self.query_proj = nn.Linear(d_model, d_ret, bias=False)
        self.scale = 1.0 / math.sqrt(d_ret)
        self.decoded_topk = decoded_topk

    def encode_docs(self, doc_emb: torch.Tensor, doc_mask: torch.Tensor) -> torch.Tensor:
        """(B, N, Ld, D) token embeddings to (B, N, d_ret) document vectors."""
        pooled = masked_mean(doc_emb, doc_mask, dim=2)
        return self.doc_proj(self.doc_norm(pooled))

    def latent_query(self, state: torch.Tensor) -> torch.Tensor:
        """(B, D) recurrent state to (B, d_ret)."""
        return self.query_proj(self.state_norm(state))

    def text_query(self, tok_emb: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        """(B, T, D) token embeddings of a text span to (B, d_ret)."""
        pooled = masked_mean(tok_emb, mask, dim=1)
        return self.doc_proj(self.doc_norm(pooled))

    def decoded_query(self, logits: torch.Tensor, embedding: nn.Embedding) -> torch.Tensor:
        """A query from what the model would say, not from what it is thinking.

        The top-k of the output distribution at the answer position, softmax
        renormalized, averaged over the token embedding table, then through the
        document encoder. This is the soft stand-in for decoding a text query:
        real decoding takes an argmax and passes no gradient, so this is the
        generous version of the comparison.
        """
        top_logits, top_ids = logits.topk(self.decoded_topk, dim=-1)
        weights = F.softmax(top_logits.float(), dim=-1).to(logits.dtype)
        vectors = embedding(top_ids)                       # (B, k, D)
        pooled = (vectors * weights.unsqueeze(-1)).sum(1)  # (B, D)
        return self.doc_proj(self.doc_norm(pooled))

    def log_probs(self, query: torch.Tensor, doc_vecs: torch.Tensor) -> torch.Tensor:
        """(B, d_ret) query against (B, N, d_ret) documents to (B, N) log probs."""
        scores = torch.einsum("bd,bnd->bn", query, doc_vecs) * self.scale
        return F.log_softmax(scores.float(), dim=-1).to(scores.dtype)


class LoopInjector(nn.Module):
    """Cross-attention from the recurrent state into the retrieved documents.

    The retrieval log probabilities enter as a per document additive bias on the
    attention logits, so document selection and token selection are decided by
    one softmax and the document choice stays differentiable.
    """

    def __init__(self, d_model: int, n_heads: int, norm_eps: float = 1e-5):
        super().__init__()
        self.n_heads = n_heads
        self.head_dim = d_model // n_heads
        self.norm = RMSNorm(d_model, norm_eps)
        self.wq = nn.Linear(d_model, d_model, bias=False)
        self.wk = nn.Linear(d_model, d_model, bias=False)
        self.wv = nn.Linear(d_model, d_model, bias=False)
        self.wo = nn.Linear(d_model, d_model, bias=False)

    def forward(self, h: torch.Tensor, doc_states: torch.Tensor,
                doc_mask: torch.Tensor, doc_log_probs: torch.Tensor) -> torch.Tensor:
        bsz, seq_len, dim = h.shape
        n_docs, doc_len = doc_states.shape[1], doc_states.shape[2]
        flat = doc_states.reshape(bsz, n_docs * doc_len, dim)
        q = self.wq(self.norm(h)).view(bsz, seq_len, self.n_heads, self.head_dim).transpose(1, 2)
        k = self.wk(flat).view(bsz, -1, self.n_heads, self.head_dim).transpose(1, 2)
        v = self.wv(flat).view(bsz, -1, self.n_heads, self.head_dim).transpose(1, 2)
        bias = doc_log_probs.unsqueeze(-1).expand(bsz, n_docs, doc_len)
        bias = bias.reshape(bsz, 1, 1, n_docs * doc_len)
        pad = ~doc_mask.reshape(bsz, 1, 1, n_docs * doc_len)
        bias = bias.masked_fill(pad, torch.finfo(bias.dtype).min).to(q.dtype)
        out = F.scaled_dot_product_attention(q, k, v, attn_mask=bias)
        out = out.transpose(1, 2).reshape(bsz, seq_len, dim)
        return self.wo(out)
