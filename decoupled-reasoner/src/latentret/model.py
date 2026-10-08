"""The looped-depth model with a retrieval step inside the loop.

Subclasses TransformerLM so the prelude, the weight-tied core, the per-loop FiLM
conditioning, the coda and the initialisation are exactly the ones already in
src/train/model.py. The new heads are built after super().__init__ has drawn
every pre-existing parameter, following the convention the pointer head set, so
switching retrieval on does not shift the values of anything that was there
before it.

One iteration reads:

    h  = core(h, e, i)                  the existing weight-tied core
    s  = h[answer position]             the partial computation, as a vector
    halt, retrieve = gate(s)            two logits from the recurrent state
    q  = query(s)                       or from the decoded distribution, or
                                        from the question, depending on the mode
    p  = softmax(q . doc_vectors)       retrieval over the episode's documents
    h  = h + sigmoid(retrieve) * xattn(h, doc_tokens, bias=log p)
    y_i = lm_head(final_norm(coda(h)))[answer position]

so the retrieved material is a change to the recurrent state that the remaining
iterations run on top of, and the readout exists at every iteration because
PonderNet needs a loss per iteration to weight.
"""

from __future__ import annotations

from dataclasses import dataclass

import torch
import torch.nn as nn

from src.latentret.gate import RetrievalGate, halting_distribution
from src.latentret.retriever import CopyReadout, LatentRetriever, LoopInjector
from src.train.model import ModelConfig, TransformerLM

QUERY_MODES = ("latent", "decoded", "question", "none")


@dataclass
class LatentRetConfig:
    d_ret: int = 96
    decoded_topk: int = 8
    gate_hidden: int | None = None
    halt_bias: float = -2.0
    retrieve_bias: float = 0.0
    inject_init_std: float = 0.02
    readout: str = "both"
    """lm, copy, or both.

    lm is generation: the answer has to come out of the vocabulary head, which
    for an invented word the model has never emitted is the hard version. copy
    is selection: point at a token in the store, through the same retrieval
    distribution that biases the injection. both mixes them, log(p_lm + p_copy)
    up to a constant, and is the default because it can fall back to either.
    """
    gate_copy: bool = False
    """Whether the gate multiplies the copy path as well as the injection.

    It does not by default, and that is a hole rather than a preference. With it
    off the copy readout reaches the store through the retrieval distribution
    but around the gate, so a model whose gate is shut can still answer. The
    latent_notask arm does exactly that: gate shut, noisy-or at 13.8, and task
    accuracy above the supervised arm's. The gate is then load bearing for the
    injection alone, which is less than the claim this experiment wants to make.

    With it on, log g is added to the copy scores, so the copy path fades as the
    gate closes and no answer is reachable through a shut gate. That is the
    arrangement the charter describes. It is off by default only so the
    committed code still describes the conditions already in results/latentret,
    which were run before the hole was found; latent_gated turns it on.
    """


@dataclass
class LatentRetOutput:
    logits: torch.Tensor          # (B, L, V) answer position logits per iteration
    halt_probs: torch.Tensor      # (B, L)
    gate_probs: torch.Tensor      # (B, L)
    doc_log_probs: torch.Tensor   # (B, L, N)


class LatentRetrievalLM(TransformerLM):
    def __init__(self, cfg: ModelConfig, ret: LatentRetConfig | dict | None = None):
        super().__init__(cfg)
        if cfg.recurrent is None:
            raise ValueError("latent retrieval needs a recurrent core")
        if isinstance(ret, dict):
            ret = LatentRetConfig(**ret)
        self.ret_cfg = ret or LatentRetConfig()
        self.retriever = LatentRetriever(
            cfg.d_model, self.ret_cfg.d_ret, cfg.norm_eps, self.ret_cfg.decoded_topk
        )
        self.gate = RetrievalGate(
            cfg.d_model, self.ret_cfg.gate_hidden, cfg.norm_eps,
            self.ret_cfg.halt_bias, self.ret_cfg.retrieve_bias,
        )
        self.injector = LoopInjector(cfg.d_model, cfg.n_heads, cfg.norm_eps)
        self.copy_head = (CopyReadout(cfg.d_model, cfg.norm_eps)
                          if self.ret_cfg.readout in ("copy", "both") else None)
        # The injection starts near zero, so iteration one runs as it would
        # without retrieval and the loop does not begin from a shove.
        with torch.no_grad():
            self.injector.wo.weight.normal_(0.0, self.ret_cfg.inject_init_std)

    # ---------------- helpers ----------------

    @staticmethod
    def _at(x: torch.Tensor, pos: torch.Tensor) -> torch.Tensor:
        """(B, T, D) gathered at one position per row to (B, D)."""
        idx = pos.view(-1, 1, 1).expand(-1, 1, x.shape[-1])
        return x.gather(1, idx).squeeze(1)

    def _readout(self, h: torch.Tensor, pos: torch.Tensor) -> torch.Tensor:
        y = h
        for block in self.coda_blocks:
            y = block(y, self.rope_cos, self.rope_sin)
        return self.lm_head(self._at(self.final_norm(y), pos))

    # ---------------- forward ----------------

    def episode_forward(self, prompt, ans_pos, docs, doc_mask, question=None,
                        question_mask=None, *, query_mode: str = "latent",
                        inject: bool = True, loops: int | None = None,
                        gate_override: float | None = None) -> LatentRetOutput:
        if query_mode not in QUERY_MODES:
            raise ValueError(f"query_mode must be one of {QUERY_MODES}")
        n_loops = self.resolve_loops(loops)
        cos, sin = self.rope_cos, self.rope_sin

        doc_emb = self.tok_emb(docs)                              # (B, N, Ld, D)
        doc_vecs = self.retriever.encode_docs(doc_emb, doc_mask)  # (B, N, d_ret)
        static_query = None
        if query_mode == "question":
            static_query = self.retriever.text_query(self.tok_emb(question), question_mask)

        x = self.tok_emb(prompt)
        for block in self.prelude_blocks:
            x = block(x, cos, sin)
        e = x
        h = x

        logits, halt_logits, gates, doc_logps = [], [], [], []
        for i in range(n_loops):
            h = self._core_once(h, e, cos, sin, i)
            state = self._at(h, ans_pos)
            halt_logit, retrieve_logit = self.gate(state)
            g = torch.sigmoid(retrieve_logit)
            if gate_override is not None:
                g = torch.full_like(g, float(gate_override))

            if query_mode == "latent":
                query = self.retriever.latent_query(state)
            elif query_mode == "question":
                query = static_query
            elif query_mode == "decoded":
                query = self.retriever.decoded_query(
                    self._readout(h, ans_pos), self.tok_emb
                )
            else:
                query = torch.zeros_like(doc_vecs[:, 0])
            log_p = self.retriever.log_probs(query, doc_vecs)

            if inject:
                delta = self.injector(h, doc_emb, doc_mask, log_p)
                h = h + g.view(-1, 1, 1) * delta

            step_logits = self._readout(h, ans_pos)
            if self.copy_head is not None:
                copy_logits = self.copy_head(
                    self._at(h, ans_pos), doc_emb, docs, doc_mask, log_p,
                    self.cfg.vocab_size)
                if self.ret_cfg.gate_copy:
                    copy_logits = copy_logits + g.clamp_min(1e-6).log().unsqueeze(-1)
                if self.ret_cfg.readout == "copy":
                    step_logits = copy_logits
                else:
                    step_logits = torch.logaddexp(step_logits.float(), copy_logits)
            logits.append(step_logits)
            halt_logits.append(halt_logit)
            gates.append(g)
            doc_logps.append(log_p)

        halt = torch.stack(halt_logits, dim=1)
        return LatentRetOutput(
            logits=torch.stack(logits, dim=1),
            halt_probs=halting_distribution(halt),
            gate_probs=torch.stack(gates, dim=1),
            doc_log_probs=torch.stack(doc_logps, dim=1),
        )

    def describe_latentret(self) -> dict:
        base = self.describe()
        heads = [self.retriever, self.gate, self.injector]
        if self.copy_head is not None:
            heads.append(self.copy_head)
        extra = sum(p.numel() for m in heads for p in m.parameters())
        base["latentret_params"] = extra
        base["d_ret"] = self.ret_cfg.d_ret
        base["readout"] = self.ret_cfg.readout
        base["gate_copy"] = self.ret_cfg.gate_copy
        return base
