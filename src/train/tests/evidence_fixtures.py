"""Shared fixtures for the evidence cross-attention tests.

The stub tokenizer is a whitespace-and-hash scheme, not a real BPE. It gives
the collator and the bank builders the only two things they use, encode and
special_ids, without pulling a 32k tokenizer file into a unit test.
"""

import numpy as np

from src.train.evidence_data import Chunk, EvidenceExample
from src.train.evidence_model import EvidenceModelConfig

SPECIALS = ["<|doc|>", "<|q|>", "<|a|>", "<|retrieve|>", "<|result|>",
            "<|world|>", "<|eot|>"]


class StubTokenizer:
    """Deterministic word level tokenizer over a small vocabulary."""

    def __init__(self, vocab_size: int = 512):
        self.vocab_size = vocab_size
        self.special_ids = {name: i for i, name in enumerate(SPECIALS)}
        self._first_free = len(SPECIALS)
        self._words = {}

    def encode(self, text: str) -> list:
        out = []
        for word in text.split():
            h = 2166136261
            for byte in word.encode("utf-8"):
                h = ((h ^ byte) * 16777619) & 0xFFFFFFFF
            span = self.vocab_size - self._first_free
            tid = self._first_free + h % span
            self._words.setdefault(tid, word)
            out.append(tid)
        return out

    def decode(self, ids: list) -> str:
        return " ".join(self._words.get(i, f"tok{i}") for i in ids)


TINY = EvidenceModelConfig(
    vocab_size=512, d_model=64, n_layers=4, n_heads=4, d_ff=176,
    max_seq_len=64, d_enc=32, enc_layers=2, enc_heads=4, enc_d_ff=96,
    chunk_len=16, xattn_every=2, xattn_n_kv_heads=2, max_chunks=64,
)


def synthetic_episode(episode_id: str = "ep-test", n_docs: int = 12,
                      n_questions: int = 3, seed: int = 0) -> dict:
    """A worldgen-shaped episode: facts, supporting documents, distractors.

    Documents d0..d(n_questions-1) support facts f0..; the rest support
    nothing and exist to be selected against. Reliabilities vary so the
    reliability embedding sees more than one bucket.
    """
    rng = np.random.default_rng(seed)
    documents = []
    questions = []
    for i in range(n_questions):
        documents.append({
            "text": f"fact{i} holds that subject{i} maps to value{i} in period {i}",
            "reliability": 0.9,
            "supports": [f"f{i}"],
            "contradicts": [],
            "doc_id": f"d{i}",
        })
        questions.append({
            "qid": f"q{i}",
            "text": f"what does subject{i} map to",
            "answer": f"value{i}",
            "type": "lookup",
            "derivation": [f"f{i}"],
            "hops": 1,
        })
    for j in range(n_questions, n_docs):
        documents.append({
            "text": f"filler{j} notes unrelated activity around token{int(rng.integers(0, 999))}",
            "reliability": float(rng.uniform(0.1, 1.0)),
            "supports": [],
            "contradicts": [],
            "doc_id": f"d{j}",
        })
    return {
        "episode_id": episode_id,
        "seed": seed,
        "world": {"domain": "corporate", "entities": [], "rules": [], "facts": []},
        "documents": documents,
        "questions": questions,
    }


def pool_chunks(n: int, chunk_len: int, seed: int = 7, vocab_size: int = 512,
                first_free: int = 7) -> list:
    """A pool of unrelated chunks, standing in for the rest of the corpus."""
    rng = np.random.default_rng(seed)
    out = []
    for i in range(n):
        ids = [int(v) for v in rng.integers(first_free, vocab_size, size=chunk_len)]
        out.append(Chunk(token_ids=ids, text=f"pool document {i} " +
                         " ".join(f"w{v}" for v in ids[:8]),
                         reliability=0.5, source="pool", doc_index=i))
    return out


def marker_examples(n_examples: int, bank_size: int, chunk_len: int,
                    vocab_size: int, seed: int = 0, distractors_only: bool = False):
    """Examples whose answer is recoverable only from the evidence bank.

    Every example carries the identical question, so nothing in the working
    sequence distinguishes them. The answer token appears exactly once, in
    one gold chunk, alongside a shared marker token. With the gold chunk in
    the bank the answer is a copy.

    Without it the examples must be indistinguishable, or the blind control
    is not blind: a per-example random distractor bank is itself a unique
    key, and a two layer model learns to read the answer off that key
    instead of off the evidence, driving the blind loss to zero and hiding
    the very failure the control exists to catch. So distractors_only draws
    one distractor bank, in one order, and gives every example that same
    bank. Then the input really is constant across examples and the best
    possible prediction is the uniform marginal over the answer set.
    """
    rng = np.random.default_rng(seed)
    marker = 8
    answer_ids = [20 + 3 * i for i in range(n_examples)]
    banned = set(answer_ids) | {marker}
    question_ids = [9, 10, 11]

    def draw_distractor(index: int) -> Chunk:
        ids = []
        while len(ids) < chunk_len:
            v = int(rng.integers(12, vocab_size))
            if v not in banned:
                ids.append(v)
        return Chunk(token_ids=ids, text=f"distractor {index}",
                     reliability=0.5, source="distractor", doc_index=index)

    shared_blind_bank = None
    if distractors_only:
        bank = [draw_distractor(j) for j in range(bank_size)]
        order = rng.permutation(len(bank))
        shared_blind_bank = [bank[k] for k in order]

    examples = []
    for i in range(n_examples):
        if shared_blind_bank is not None:
            chunks = list(shared_blind_bank)
        else:
            chunks = [Chunk(
                token_ids=[marker, answer_ids[i]], text=f"gold {i}",
                reliability=1.0, source="gold", doc_index=0, supports=("f0",),
            )]
            while len(chunks) < bank_size:
                chunks.append(draw_distractor(len(chunks)))
            order = rng.permutation(len(chunks))
            chunks = [chunks[k] for k in order]
        gold = tuple(p for p, c in enumerate(chunks) if c.source == "gold")
        examples.append(EvidenceExample(
            question_ids=question_ids,
            answer_ids=[answer_ids[i]],
            chunks=chunks,
            gold_positions=gold,
            mode="distractors" if distractors_only else "oracle",
            question_text="what is the code",
            answer_text=f"value{i}",
        ))
    return examples
