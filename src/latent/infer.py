"""Decoding with a latent segment, and the counters that price it.

The generation loop is the same shape as src.opgraph.run.Generator: batched,
key value cached, one token per sequence per round. The difference is the R
rounds before the answer, where the sequence advances on a vector rather than
on a token id. Those rounds are the reasoning channel, and they are counted
separately from the rounds that write the answer, because a gain that turns out
to be R extra forward passes is test time compute and not the removal of the
vocabulary bottleneck.

Two decoders are here. LatentPolicy is the cached one, which is what every
reported number comes from. latent_generate_slow recomputes the whole prefix at
every step and is what the tests hold the cached one against, because a cache
bug in a decoder that injects its own embeddings would be invisible in the
accuracy and fatal to it.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import torch
import torch.nn.functional as F

from src.latent.core import trunk_from_embeds
from src.rl.sampler import CachedPolicy
from src.train.model import apply_rope


@dataclass
class DecodeCost:
    """Forward passes and wall clock, split by what they were spent on."""

    examples: int = 0
    prompt_passes: int = 0
    prompt_positions: int = 0
    reason_passes: int = 0
    reason_positions: int = 0
    decode_passes: int = 0
    decode_positions: int = 0
    layers_per_pass: int = 0
    prompt_seconds: float = 0.0
    reason_seconds: float = 0.0
    decode_seconds: float = 0.0
    total_seconds: float = 0.0

    def add(self, other: "DecodeCost") -> None:
        for name in self.__dataclass_fields__:
            if name == "layers_per_pass":
                self.layers_per_pass = max(self.layers_per_pass,
                                           other.layers_per_pass)
                continue
            setattr(self, name, getattr(self, name) + getattr(other, name))

    def per_example(self) -> dict:
        n = max(1, self.examples)
        out = {"examples": self.examples, "layers_per_pass": self.layers_per_pass}
        for name in self.__dataclass_fields__:
            if name in ("examples", "layers_per_pass"):
                continue
            out[name + "_per_example"] = getattr(self, name) / n
        out["reason_layer_apps_per_example"] = (
            self.reason_positions * self.layers_per_pass / n)
        out["total_layer_apps_per_example"] = (
            (self.prompt_positions + self.reason_positions
             + self.decode_positions) * self.layers_per_pass / n)
        return out


class LatentPolicy(CachedPolicy):
    """CachedPolicy that can also advance on a vector, and hands back states.

    Two changes to the parent's forward: the input can be an embedding instead
    of a token id lookup, and the final normed state of the last position is
    kept, since that state is the whole payload of a latent step. The tests pin
    this against the parent with embeds left off: same logits, same tokens.
    """

    def __init__(self, model, device, max_len: int, temperature: float = 1.0,
                 top_k: int = 0, seed: int = 0, dtype=None):
        if model.cfg.recurrent is not None:
            raise NotImplementedError(
                "the cached decoder runs model.blocks directly and does not "
                "implement the looped core; run depth recurrence through the "
                "uncached path instead of getting a quietly wrong number")
        super().__init__(model, device, max_len, temperature=temperature,
                         top_k=top_k, seed=seed, dtype=dtype)
        self.last_hidden: torch.Tensor | None = None
        self.passes = 0
        self.positions = 0

    def _forward(self, ids: torch.Tensor, start_pos: int,
                 embeds: torch.Tensor | None = None) -> torch.Tensor:
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

        x = model.tok_emb(ids) if embeds is None else embeds.to(model.tok_emb.weight.dtype)
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
        self.last_hidden = x[:, -1]
        return model.lm_head(x)[:, -1]

    def _run(self, ids: torch.Tensor, start_pos: int,
             embeds: torch.Tensor | None = None) -> torch.Tensor:
        self.passes += 1
        self.positions += int(ids.shape[1])
        if self.use_autocast:
            with torch.autocast(device_type="cuda", dtype=self.dtype):
                with torch.no_grad():
                    return self._forward(ids, start_pos, embeds)
        with torch.no_grad():
            return self._forward(ids, start_pos, embeds)

    def advance_embed(self, vec: torch.Tensor) -> list[int]:
        """Append one position whose input embedding is the given vector."""
        if self.pos >= self.max_len:
            raise ValueError("cache is full; raise max_len")
        bsz = vec.shape[0]
        ids = torch.zeros((bsz, 1), dtype=torch.long, device=self.device)
        self.key_ok[:, self.pos] = True
        logits = self._run(ids, self.pos, vec.unsqueeze(1))
        self.pos += 1
        return self._sample(logits)


def _sync(device) -> None:
    if torch.device(device).type == "cuda":
        torch.cuda.synchronize()


def latent_generate(model, head, tok, prompts: list[str], r_steps: int,
                    max_new: int = 96, temperature: float = 0.0,
                    top_k: int = 0, seed: int = 0, device: str = "cuda",
                    batch_size: int = 16, force_answer: bool = True
                    ) -> tuple[list[str], DecodeCost]:
    """Prompt, then r_steps latent rounds, then decode until <|eot|>.

    The <|a|> that closes the latent segment is written by the scaffold rather
    than predicted, which is why nothing was ever trained to predict it. A
    prompt that already ends in <|a|>, which is every prompt in the token
    channel arms, passes force_answer=False.
    """
    if r_steps and head is None:
        raise ValueError("latent steps need a head")
    texts: list[str] = []
    total = DecodeCost(layers_per_pass=model.cfg.effective_depth())
    for i in range(0, len(prompts), batch_size):
        chunk = prompts[i:i + batch_size]
        out, cost = _latent_batch(model, head, tok, chunk, r_steps, max_new,
                                  temperature, top_k, seed, device,
                                  force_answer)
        texts.extend(out)
        total.add(cost)
    return texts, total


def _latent_batch(model, head, tok, prompts, r_steps, max_new, temperature,
                  top_k, seed, device, force_answer=True):
    eot = tok.token_id("<|eot|>")
    a_id = tok.token_id("<|a|>")
    ids = [tok.encode(p) for p in prompts]
    width = max(len(x) for x in ids)
    cap = min(width + r_steps + 2 + max_new, model.cfg.max_seq_len)
    if width + r_steps + 2 >= cap:
        raise ValueError(f"prompt {width} plus {r_steps} latent steps leaves no "
                         f"room inside max_seq_len {model.cfg.max_seq_len}")
    pol = LatentPolicy(model, device, max_len=cap, temperature=temperature,
                       top_k=top_k, seed=seed)
    cost = DecodeCost(examples=len(prompts),
                      layers_per_pass=model.cfg.effective_depth())

    _sync(device)
    t0 = time.perf_counter()
    nxt = pol.begin(ids)
    _sync(device)
    t1 = time.perf_counter()
    cost.prompt_passes = len(prompts)
    cost.prompt_positions = width * len(prompts)
    cost.prompt_seconds = t1 - t0

    for r in range(r_steps):
        h = pol.last_hidden
        with torch.no_grad():
            z = head(h.float(), r)
        nxt = pol.advance_embed(z)
    _sync(device)
    t2 = time.perf_counter()
    cost.reason_passes = r_steps * len(prompts)
    cost.reason_positions = r_steps * len(prompts)
    cost.reason_seconds = t2 - t1

    rounds = 0
    if force_answer:
        nxt = pol.advance([a_id] * len(prompts))
        rounds = 1
    done = [False] * len(prompts)
    gen: list[list[int]] = [[] for _ in prompts]
    for _ in range(max_new):
        step = []
        for i, t in enumerate(nxt):
            if done[i]:
                step.append(0)
                continue
            if t == eot:
                done[i] = True
                step.append(0)
                continue
            gen[i].append(int(t))
            step.append(int(t))
        if all(done):
            break
        nxt = pol.advance(step)
        rounds += 1
    _sync(device)
    t3 = time.perf_counter()
    cost.decode_passes = rounds * len(prompts)
    cost.decode_positions = rounds * len(prompts)
    cost.decode_seconds = t3 - t2
    cost.total_seconds = t3 - t0
    return [tok.decode(g).strip() for g in gen], cost


def latent_generate_slow(model, head, tok, prompts: list[str], r_steps: int,
                         max_new: int = 32, device: str = "cuda"
                         ) -> list[str]:
    """Reference decoder: no cache, whole prefix recomputed at every step.

    Greedy only, one sequence at a time, and far too slow for a sweep. It is
    here so the cached decoder has something exact to be checked against.
    """
    eot = tok.token_id("<|eot|>")
    a_id = tok.token_id("<|a|>")
    out = []
    for p in prompts:
        ids = tok.encode(p)
        emb = model.tok_emb(torch.tensor([ids], device=device))
        for r in range(r_steps):
            with torch.no_grad():
                h = trunk_from_embeds(model, emb)
                z = head(h[:, -1].float(), r)
            emb = torch.cat([emb, z.unsqueeze(1).to(emb.dtype)], dim=1)
        a_emb = model.tok_emb(torch.tensor([[a_id]], device=device))
        emb = torch.cat([emb, a_emb], dim=1)
        gen: list[int] = []
        for _ in range(max_new):
            with torch.no_grad():
                h = trunk_from_embeds(model, emb)
                logits = model.lm_head(h[:, -1])
            nxt = int(torch.argmax(logits.float(), dim=-1).item())
            if nxt == eot:
                break
            gen.append(nxt)
            emb = torch.cat(
                [emb, model.tok_emb(torch.tensor([[nxt]], device=device))],
                dim=1)
        out.append(tok.decode(gen).strip())
    return out


def token_generate(model, tok, prompts: list[str], max_new: int = 96,
                   temperature: float = 0.0, top_k: int = 0, seed: int = 0,
                   device: str = "cuda", batch_size: int = 16
                   ) -> tuple[list[str], DecodeCost]:
    """The plain token channel, counted the same way, for matched compute.

    A written trace spends one forward pass per token it writes. That number
    has to sit beside the latent conditions' R, or the comparison is between a
    condition that was allowed extra passes and one that was not.
    """
    return latent_generate(model, None, tok, prompts, 0, max_new, temperature,
                           top_k, seed, device, batch_size, force_answer=False)
