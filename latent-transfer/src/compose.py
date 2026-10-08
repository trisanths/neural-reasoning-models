"""Sequential composition task: depth-limited reasoning.

    start 3 add 4 mul 2 add 1 ?   ->   16 mod 10 = 6

A chain of `k` arithmetic updates over a single hidden value in Z_10. Each step
depends on the previous result, so answering requires `k` *sequential*
computations that cannot be parallelised away.

This is deliberately a different primitive from the ProsQA-style graph task.
That task's bottleneck is long-range content lookup (induction heads), which
from-scratch models take a very long time to form -- empirically they converge
to guessing instead. Here every operand sits next to its operator, so there is
nothing to retrieve: the only thing that makes the task hard is *depth*. That
isolates the capacity gap the cross-model pipeline is meant to close, which is
what the experiment actually needs to measure.

Reasoning steps are the running intermediate values, giving the Coconut
curriculum something concrete to compress into each continuous thought.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .data import Example

MOD = 10
DIGITS = [str(i) for i in range(MOD)]
OPS = ["add", "mul"]
# Units of Z_10: multiplying by these is invertible, so no information is lost.
COPRIME = [1, 3, 7, 9]
SYNTAX_C = ["start", "then", "?", "=", "."]

PAD, BOS, EOS = "<pad>", "<bos>", "<eos>"
BOT, EOT, LATENT = "<bot>", "<eot>", "<latent>"
SPECIALS_C = [PAD, BOS, EOS, BOT, EOT, LATENT]


class ComposeTokenizer:
    def __init__(self) -> None:
        self.itos = SPECIALS_C + SYNTAX_C + OPS + DIGITS
        self.stoi = {t: i for i, t in enumerate(self.itos)}
        self.pad_id = self.stoi[PAD]
        self.bos_id = self.stoi[BOS]
        self.eos_id = self.stoi[EOS]
        self.bot_id = self.stoi[BOT]
        self.eot_id = self.stoi[EOT]
        self.latent_id = self.stoi[LATENT]

    def __len__(self) -> int:
        return len(self.itos)

    def encode(self, text: str) -> list[int]:
        return [self.stoi[w] for w in text.split()]

    def decode(self, ids: list[int]) -> str:
        return " ".join(self.itos[i] for i in ids)


@dataclass
class ComposeConfig:
    n_steps: int = 6
    seed: int = 0


class ComposeGenerator:
    """Samples `n_steps` chained updates over a value in Z_10."""

    def __init__(self, n_steps: int = 6, seed: int = 0) -> None:
        if n_steps < 2:
            raise ValueError("n_steps must be >= 2")
        self.n_steps = n_steps
        self.rng = random.Random(seed)

    def sample(self) -> Example:
        val = self.rng.randrange(MOD)
        parts = [f"start {val}"]
        steps = [f"= {val} ."]
        for _ in range(self.n_steps):
            op = self.rng.choice(OPS)
            # Every operation must be a bijection on Z_10, otherwise the answer
            # distribution collapses (multiplying by 0 or 2 destroys
            # information) and a constant predictor scores well above chance.
            operand = (
                self.rng.randrange(MOD) if op == "add" else self.rng.choice(COPRIME)
            )
            val = (val + operand) % MOD if op == "add" else (val * operand) % MOD
            parts.append(f"then {op} {operand}")
            steps.append(f"= {val} .")
        question = " ".join(parts) + " ?"
        return Example(
            question=question,
            steps=steps,
            answer=f"= {val} .",
            n_hops=self.n_steps,
            meta={"final": val},
        )

    def generate(self, n: int) -> list[Example]:
        return [self.sample() for _ in range(n)]


def chance_level() -> float:
    """Uniform guess over the answer alphabet."""
    return 1.0 / MOD
