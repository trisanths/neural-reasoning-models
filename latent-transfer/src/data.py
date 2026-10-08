"""ProsQA-style multi-hop reasoning task.

Mirrors the structure of the ProsQA dataset used by Coconut (Hao et al., 2024):
a random DAG over fictional concept names, a person asserted to belong to one
concept, and a question asking which of two candidate concepts the person
belongs to. Exactly one candidate is reachable from the person's root concept;
the other is a plausible distractor drawn from an unreachable branch.

Unlike the original, hop depth and distractor count are tunable, which lets us
place the difficulty in the window where a small model fails and a larger one
succeeds -- the capacity gap the cross-model pipeline is meant to close.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from typing import Iterator

# Fictional concept stems in the style of ProntoQA/ProsQA ("wumpus", "yumpus").
_PREFIXES = [
    "wum", "yum", "ker", "bom", "vum", "fel", "jom", "yim", "jel", "yer",
    "rem", "ter", "imp", "tim", "zhor", "zum", "stor", "lem", "grim", "dor",
    "quor", "brim", "flum", "snor", "plim", "trom", "gled", "vorp", "murk", "thal",
]
_SUFFIXES = ["pus", "ple", "kin"]
CONCEPTS = [p + s for s in _SUFFIXES for p in _PREFIXES]

PEOPLE = ["alice", "bob", "carol", "dave", "erin", "frank", "grace", "henry"]

# Word-level vocabulary. Tiny by design: a small embedding matrix keeps both
# models cheap, so compute goes into depth rather than into a 50k softmax.
SYNTAX = ["every", "is", "a", "or", "?", ".", "not"]

PAD, BOS, EOS = "<pad>", "<bos>", "<eos>"
BOT, EOT, LATENT = "<bot>", "<eot>", "<latent>"
SPECIALS = [PAD, BOS, EOS, BOT, EOT, LATENT]


class Tokenizer:
    """Whitespace/word-level tokenizer over a closed vocabulary."""

    def __init__(self) -> None:
        self.itos = SPECIALS + SYNTAX + PEOPLE + CONCEPTS
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
class Example:
    question: str
    steps: list[str]
    answer: str
    n_hops: int
    meta: dict = field(default_factory=dict)


class ProsQAGenerator:
    """Samples multi-hop reachability problems over a random layered DAG.

    Args:
        n_layers: depth of the concept DAG.
        width: concepts per layer.
        n_hops: length of the gold reasoning chain (>= 2).
        extra_edges: distractor edges added beyond the backbone chains.
        seed: RNG seed.
    """

    def __init__(
        self,
        n_layers: int = 6,
        width: int = 4,
        n_hops: int = 4,
        extra_edges: int = 10,
        seed: int = 0,
    ) -> None:
        if n_hops < 2:
            raise ValueError("n_hops must be >= 2 to require multi-hop reasoning")
        if n_hops > n_layers - 1:
            raise ValueError(
                f"n_hops={n_hops} needs at least {n_hops + 1} layers, got {n_layers}"
            )
        if n_layers * width > len(CONCEPTS):
            raise ValueError(
                f"need {n_layers * width} concepts, vocabulary has {len(CONCEPTS)}"
            )
        self.n_layers = n_layers
        self.width = width
        self.n_hops = n_hops
        self.extra_edges = extra_edges
        self.rng = random.Random(seed)

    def _sample_graph(self) -> tuple[list[list[str]], list[tuple[str, str]]]:
        """Builds a layered DAG; edges only go from layer i to layer i+1."""
        pool = self.rng.sample(CONCEPTS, self.n_layers * self.width)
        layers = [
            pool[i * self.width : (i + 1) * self.width] for i in range(self.n_layers)
        ]
        edges: set[tuple[str, str]] = set()
        # Backbone: every node gets at least one child, so paths are long enough.
        for i in range(self.n_layers - 1):
            for node in layers[i]:
                child = self.rng.choice(layers[i + 1])
                edges.add((node, child))
        for _ in range(self.extra_edges):
            i = self.rng.randrange(self.n_layers - 1)
            edges.add((self.rng.choice(layers[i]), self.rng.choice(layers[i + 1])))
        return layers, sorted(edges)

    @staticmethod
    def _reachable(root: str, adj: dict[str, list[str]]) -> dict[str, list[str]]:
        """BFS from root; returns node -> shortest path (list of nodes)."""
        paths = {root: [root]}
        queue = [root]
        while queue:
            node = queue.pop(0)
            for child in adj.get(node, []):
                if child not in paths:
                    paths[child] = paths[node] + [child]
                    queue.append(child)
        return paths

    def sample(self) -> Example | None:
        layers, edges = self._sample_graph()
        adj: dict[str, list[str]] = {}
        for src, dst in edges:
            adj.setdefault(src, []).append(dst)

        person = self.rng.choice(PEOPLE)
        root = self.rng.choice(layers[0])
        paths = self._reachable(root, adj)

        # Gold target: a concept at exactly n_hops edges from the root.
        targets = [n for n, p in paths.items() if len(p) - 1 == self.n_hops]
        if not targets:
            return None
        target = self.rng.choice(targets)

        # Distractor: unreachable from root, on the same layer as the target, and
        # degree-matched to it. Without the degree match the reachable target
        # simply appears in more statements than the distractor, and a model can
        # score ~69% by counting mentions instead of reasoning.
        target_layer = next(i for i, l in enumerate(layers) if target in l)
        degree: dict[str, int] = {}
        for src, dst in edges:
            degree[src] = degree.get(src, 0) + 1
            degree[dst] = degree.get(dst, 0) + 1
        candidates = [
            c
            for c in layers[target_layer]
            if c not in paths and degree.get(c, 0) == degree.get(target, 0)
        ]
        if not candidates:
            return None
        distractor = self.rng.choice(candidates)

        statements = [f"every {s} is a {d} ." for s, d in edges]
        self.rng.shuffle(statements)
        statements.append(f"{person} is a {root} .")
        # Randomize which side the correct answer appears on.
        cand = [target, distractor]
        self.rng.shuffle(cand)
        question = (
            " ".join(statements) + f" is {person} a {cand[0]} or {cand[1]} ?"
        )

        path = paths[target]
        steps = [f"{person} is a {root} ."] + [
            f"every {path[i]} is a {path[i + 1]} ." for i in range(len(path) - 1)
        ]
        return Example(
            question=question,
            steps=steps,
            answer=f"{person} is a {target} .",
            n_hops=self.n_hops,
            meta={"target": target, "distractor": distractor, "n_edges": len(edges)},
        )

    def generate(self, n: int) -> list[Example]:
        out: list[Example] = []
        attempts = 0
        while len(out) < n and attempts < n * 100:
            attempts += 1
            ex = self.sample()
            if ex is not None:
                out.append(ex)
        if len(out) < n:
            raise RuntimeError(f"only generated {len(out)}/{n} examples; loosen config")
        return out


def dedup_split(
    examples: list[Example], n_val: int, n_test: int
) -> tuple[list[Example], list[Example], list[Example]]:
    """Splits examples, guaranteeing no question string appears in two splits."""
    seen: set[str] = set()
    unique: list[Example] = []
    for ex in examples:
        if ex.question not in seen:
            seen.add(ex.question)
            unique.append(ex)
    test = unique[:n_test]
    val = unique[n_test : n_test + n_val]
    train = unique[n_test + n_val :]
    return train, val, test


def to_json(examples: list[Example]) -> list[dict]:
    return [
        {
            "question": e.question,
            "steps": e.steps,
            "answer": e.answer,
            "n_hops": e.n_hops,
            "meta": e.meta,
        }
        for e in examples
    ]


def save(examples: list[Example], path: str) -> None:
    with open(path, "w") as f:
        json.dump(to_json(examples), f)


def load(path: str) -> list[Example]:
    with open(path) as f:
        raw = json.load(f)
    return [
        Example(e["question"], e["steps"], e["answer"], e["n_hops"], e.get("meta", {}))
        for e in raw
    ]
