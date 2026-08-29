"""The latent reasoning channel: hidden state straight back to input embedding.

Every condition in this project that dies near depth four passes its reasoning
state through the vocabulary between steps. A hidden state is projected to
logits, one symbol is selected, and that symbol is embedded again. The two
conditions built on this module do not. A step's output hidden state becomes
the next step's input embedding directly, so nothing is projected, nothing is
selected, and nothing is re-embedded.

No loss ever asks the continuous state to reproduce a written step. The labels
at every latent position are IGNORE, so the state is free to carry whatever
supports the reasoning that follows, including several live alternatives at
once, which is the whole reason for removing the symbol.

Three pieces live here.

trunk_from_embeds runs the model's own trunk starting at the embeddings rather
than at token ids. Under a recurrent config it calls the model's weight tied
core, so the per iteration FiLM conditioning and the loop count override are
src/train/model.py's and not a copy of them.

LatentHead turns a hidden state into the next input embedding: a fixed scale
measured once from the checkpoint, an optional linear map, and a per latent
step FiLM in the same zero initialised scale and shift form the looped core
uses per iteration.

with_depth_recurrence reinterprets a plain checkpoint's layers as a prelude, a
weight tied core and a coda. It is off by default because it changes what the
base network computes, which would break the match against the token channel
arms.
"""

from __future__ import annotations

import torch
import torch.nn as nn

from src.train.model import ModelConfig, TransformerLM


def trunk_from_embeds(model, x: torch.Tensor, loops: int | None = None
                      ) -> torch.Tensor:
    """The model's trunk, entered at the embeddings instead of at token ids.

    model.trunk looks up token embeddings and then runs the blocks. A latent
    step has to push a vector in at exactly that point, so this is everything
    after the lookup and nothing else. Passing model.tok_emb(ids) here returns
    the same tensor model.trunk(ids) returns, which the tests pin.
    """
    if x.shape[1] > model.cfg.max_seq_len:
        raise ValueError(f"sequence length {x.shape[1]} exceeds max_seq_len "
                         f"{model.cfg.max_seq_len}")
    if model.cfg.recurrent is None:
        for block in model.blocks:
            x = block(x, model.rope_cos, model.rope_sin)
    else:
        x = model._run_recurrent(x, model.rope_cos, model.rope_sin,
                                 model.resolve_loops(loops))
    return model.final_norm(x)


class LatentHead(nn.Module):
    """Hidden state to the next latent step's input embedding.

    scale is measured once from the checkpoint, as the ratio between the
    embedding table's RMS and the trunk output's RMS. A trunk output injected
    at its own magnitude sits nowhere near any embedding the backbone has ever
    read, and the first steps of training are then spent undoing that rather
    than learning anything.

    film holds one zero initialised scale and shift per latent step, the same
    conditioning the looped core applies per iteration. Zero means an untrained
    head is the identity, so step one is exactly the state the trunk produced
    and the condition starts from the plainest possible version of itself.
    Steps past the last slot reuse the last row, as loop_slots does.

    proj="none" adds two vectors per step and nothing else. proj="linear" adds
    a d by d map initialised to the identity, which is 1.05M parameters on the
    350M backbone. The parameter delta is reported with every run because it is
    the one axis on which these conditions cannot be matched to the arms.
    """

    def __init__(self, d_model: int, slots: int, proj: str = "none",
                 scale: float = 1.0):
        super().__init__()
        if proj not in ("none", "linear"):
            raise ValueError(f"proj must be none or linear, got {proj!r}")
        if slots < 1:
            raise ValueError("slots must be at least 1")
        self.d_model = int(d_model)
        self.slots = int(slots)
        self.proj_kind = proj
        self.register_buffer("scale", torch.tensor(float(scale)))
        self.film = nn.Parameter(torch.zeros(self.slots, 2 * d_model))
        self.proj = None
        if proj == "linear":
            self.proj = nn.Linear(d_model, d_model, bias=False)
            with torch.no_grad():
                self.proj.weight.copy_(torch.eye(d_model))

    def forward(self, h: torch.Tensor, step: int) -> torch.Tensor:
        z = h if self.proj is None else self.proj(h)
        z = z * self.scale.to(z.dtype)
        row = self.film[min(int(step), self.slots - 1)].to(z.dtype)
        s, b = row.chunk(2, dim=-1)
        return z * (1.0 + s) + b

    def num_params(self) -> int:
        return sum(p.numel() for p in self.parameters())

    def config(self) -> dict:
        return {"d_model": self.d_model, "slots": self.slots,
                "proj": self.proj_kind, "scale": float(self.scale.item()),
                "params": self.num_params()}


@torch.no_grad()
def measure_scale(model, ids: torch.Tensor) -> float:
    """Embedding RMS over trunk output RMS, from one calibration batch."""
    emb_rms = model.tok_emb.weight.float().pow(2).mean().sqrt()
    h = trunk_from_embeds(model, model.tok_emb(ids))
    hid_rms = h.float().pow(2).mean().sqrt().clamp_min(1e-6)
    return float(emb_rms / hid_rms)


def with_depth_recurrence(model, prelude: int, core: int, coda: int,
                          loops: int, train_loop_sampling=None,
                          loop_embedding: bool = True,
                          inject_prelude: bool = True):
    """A copy of the model whose middle layers run as a weight tied core.

    The base checkpoint here is a plain 24 layer stack, so switching this on
    changes what the network computes and the run is no longer matched against
    the token channel arms on anything but the checkpoint file. It exists so a
    latent step can be given extra depth through src/train/model.py's own
    looped core, its per iteration FiLM and its train_loop_sampling, rather
    than through a second recurrent core written here.

    Returns (model, report). report names the state dict keys that were added
    by recurrence and had no weights to load, which are the loop adapter and
    the loop FiLM table.
    """
    old = model.cfg
    rec = {"core_layers": core, "loops": loops, "prelude_layers": prelude,
           "coda_layers": coda, "loop_embedding": loop_embedding,
           "train_loop_sampling": train_loop_sampling,
           "inject_prelude": inject_prelude}
    cfg = ModelConfig(vocab_size=old.vocab_size, d_model=old.d_model,
                      n_layers=old.n_layers, n_heads=old.n_heads,
                      d_ff=old.d_ff, max_seq_len=old.max_seq_len,
                      rope_theta=old.rope_theta, norm_eps=old.norm_eps,
                      recurrent=rec, pointer=None)
    new = TransformerLM(cfg)
    missing, unexpected = new.load_state_dict(model.state_dict(), strict=False)
    return new, {"missing": list(missing), "unexpected": list(unexpected),
                 "effective_depth": cfg.effective_depth()}


# ------------------------------------------------------- tensor plumbing

def compress_index(first_latent: torch.Tensor, n_latent: int, r: int,
                   width: int) -> torch.Tensor:
    """Row indices that keep the first r latent slots and drop the rest.

    A training example is laid out prompt, n_latent slots, <|a|>, target. Pass
    r of the latent chain has only r of those slots filled, and the remaining
    slots must not be in the sequence at all: leaving a placeholder embedding
    where a latent will later go would let the answer positions attend to a
    token that carries no state, and the loss at pass r would then not be the
    loss of answering after r latent steps.

    Dropping the tail slots shifts everything after them down by n_latent - r.
    Rotary position embeddings are relative, so that shift is the right thing
    rather than a compromise: the answer sits r positions after the prompt,
    which is where it sits at inference when r steps were taken.

    Every row loses the same number of positions, so the compressed batch is
    still rectangular even though first_latent differs per row.
    """
    if not 0 <= r <= n_latent:
        raise ValueError(f"r must be in [0, {n_latent}], got {r}")
    length = width - n_latent + r
    ar = torch.arange(length, device=first_latent.device).view(1, length)
    fl = first_latent.view(-1, 1)
    return torch.where(ar < fl + r, ar, ar + (n_latent - r))


def scatter_at(emb: torch.Tensor, pos: torch.Tensor, vec: torch.Tensor
               ) -> torch.Tensor:
    """emb with row pos of each batch element replaced by vec, differentiably."""
    b, length, _ = emb.shape
    ar = torch.arange(length, device=emb.device).view(1, length, 1)
    mask = (ar == pos.view(b, 1, 1)).to(emb.dtype)
    return emb * (1.0 - mask) + vec.unsqueeze(1) * mask


def gather_at(h: torch.Tensor, pos: torch.Tensor) -> torch.Tensor:
    """The hidden state at one position per batch element."""
    b, _, d = h.shape
    return h.gather(1, pos.view(b, 1, 1).expand(b, 1, d)).squeeze(1)
