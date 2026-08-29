"""Decoding that reports its own truncation, at any temperature.

Two things the depth sweep needs that the plain generator does not give. A
temperature, because greedy decoding has produced false zeros on this project.
And whether a generation stopped because the model wrote its end token or
because it ran out of budget: a plan cut off by the token cap would look like
a short plan, which is exactly the measurement being made, so the cap has to
be visible in every record.
"""

from __future__ import annotations

from src.opgraph.run import EOT, Generator
from src.rl.sampler import CachedPolicy


class TGenerator(Generator):
    """Batched decoding with a temperature and a per-sequence cap flag."""

    def __init__(self, model, tok, device="cuda", batch_size: int = 16,
                 temperature: float = 0.0, seed: int = 0):
        super().__init__(model, tok, device, batch_size)
        self.temperature = float(temperature)
        self.seed = int(seed)

    def generate_full(self, prompts: list[str], max_new: int = 96) -> list[dict]:
        out: list[dict] = []
        for i in range(0, len(prompts), self.batch_size):
            out.extend(self._batch_full(prompts[i:i + self.batch_size], max_new))
        return out

    def generate(self, prompts: list[str], max_new: int = 96) -> list[str]:
        return [r["text"] for r in self.generate_full(prompts, max_new)]

    def _batch(self, prompts: list[str], max_new: int) -> list[str]:
        return [r["text"] for r in self._batch_full(prompts, max_new)]

    def _batch_full(self, prompts: list[str], max_new: int) -> list[dict]:
        ids = [self.tok.encode(p) for p in prompts]
        width = max(len(x) for x in ids)
        cap = min(width + max_new + 2, self.model.cfg.max_seq_len)
        budget = max(1, cap - width - 2)
        policy = CachedPolicy(self.model, self.device, max_len=cap,
                              temperature=self.temperature, seed=self.seed)
        nxt = policy.begin(ids)
        done = [False] * len(ids)
        gen: list[list[int]] = [[] for _ in ids]
        for _ in range(budget):
            step = []
            for i, t in enumerate(nxt):
                if done[i]:
                    step.append(0)
                    continue
                if t == self.eot_id:
                    done[i] = True
                    step.append(0)
                    continue
                gen[i].append(int(t))
                step.append(int(t))
            if all(done):
                break
            nxt = policy.advance(step)
        return [{"text": self.tok.decode(g).strip(), "ntok": len(g),
                 "hit_cap": (not d), "budget": budget}
                for g, d in zip(gen, done)]


def eot_id_of(tok):
    return tok.token_id(EOT)
