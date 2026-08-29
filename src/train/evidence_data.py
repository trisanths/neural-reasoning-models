"""Evidence bank construction and the (question, bank, answer) collator.

A training example for the cross-attention model is a question, an evidence
bank of N chunks, and an answer. The bank is built from an episode's own
document set, chunked, distractors and contradiction documents included, and
topped up from a pool of chunks drawn from other episodes. The model must
select; nothing hands it the supporting document.

Three bank modes:

  oracle       every gold chunk is placed in the bank, the rest is filled
               with distractors. This is the upper bound on retrieval and
               the regime the gate and selection behaviour are learned in.
  retrieval    the bank is the BM25 top N over the candidate pool for the
               question text, gold or no gold. gold_present records what
               actually happened, so a run can report its own hit rate
               rather than assuming one.
  distractors  gold chunks are removed and the bank is filled with the
               rest. Used as the control: an answer that survives this
               regime was not read out of the evidence.

BM25 is the same scorer the oracle query planner uses, src/train/retrieval's
BM25Index over normalized terms with reliability weighting, wrapped in an
inverted index so scoring a query against a few thousand chunks is a merge
over postings instead of a full scan.

The objective is answer tokens only. The working sequence is

    <|q|> question <|a|> answer <|eot|>

and the target vector is IGNORE_INDEX everywhere except the positions that
predict the answer tokens and the closing <|eot|>. Evidence never appears in
the working sequence at all, so evidence tokens are not merely masked out of
the loss, they are not in the prediction stream to begin with.

Everything is deterministic in (episodes, seed, knobs).
"""

from collections import defaultdict
from dataclasses import dataclass, field

import numpy as np
import torch

from src.train.retrieval import BM25Index, norm_terms

IGNORE_INDEX = -100


@dataclass
class Chunk:
    """One retrievable unit: a token window of a document plus its provenance."""

    token_ids: list
    text: str
    reliability: float = 1.0
    source: str = ""
    doc_index: int = -1
    chunk_index: int = 0
    supports: tuple = ()


@dataclass
class EvidenceExample:
    """A question, its bank, its answer, and what the bank turned out to hold."""

    question_ids: list
    answer_ids: list
    chunks: list
    gold_positions: tuple = ()
    mode: str = "oracle"
    question_text: str = ""
    answer_text: str = ""

    @property
    def gold_present(self) -> bool:
        return len(self.gold_positions) > 0


def chunk_document(text: str, tokenizer, chunk_len: int, reliability: float = 1.0,
                   source: str = "", doc_index: int = -1,
                   supports=()) -> list:
    """Split one document into chunk_len token windows.

    Windows do not overlap. A document shorter than chunk_len yields one
    short chunk, which the collator pads and masks; nothing is dropped and
    nothing is merged across documents, so a chunk always has one source.
    Each chunk carries the text of its own window, decoded back from the
    window's tokens, so BM25 scores the unit that actually enters the bank
    rather than the whole document it came from.
    """
    ids = tokenizer.encode(text)
    if not ids:
        return []
    out = []
    for k in range(0, len(ids), chunk_len):
        window = ids[k:k + chunk_len]
        out.append(Chunk(
            token_ids=list(window),
            text=text if len(ids) <= chunk_len else tokenizer.decode(list(window)),
            reliability=float(reliability),
            source=source,
            doc_index=doc_index,
            chunk_index=len(out),
            supports=tuple(supports),
        ))
    return out


def episode_chunks(episode: dict, tokenizer, chunk_len: int,
                   source: str = "") -> list:
    """Chunk every document of an episode, distractors and contradictions kept.

    The full document set is the point: an episode's bank contains the
    supporting documents, the unrelated ones, and the low reliability
    documents that contradict the facts. Selecting among them is the task.
    """
    chunks = []
    src = source or episode.get("episode_id", "")
    for i, doc in enumerate(episode.get("documents", [])):
        chunks.extend(chunk_document(
            doc["text"], tokenizer, chunk_len,
            reliability=float(doc.get("reliability", 1.0)),
            source=src, doc_index=i,
            supports=tuple(doc.get("supports", []) or ()),
        ))
    return chunks


class ChunkRetriever:
    """BM25 top-N over a chunk list, via an inverted index.

    Scores come from BM25Index.term_score, so ranking matches the oracle
    retriever's definition exactly, reliability weighting included. Ties
    break toward the lower chunk index, so the ranking is deterministic.
    """

    def __init__(self, chunks: list):
        if not chunks:
            raise ValueError("ChunkRetriever needs at least one chunk")
        self.chunks = chunks
        self.index = BM25Index(
            [c.text for c in chunks],
            reliabilities=[c.reliability for c in chunks],
        )
        self.postings = defaultdict(list)
        for i, counts in enumerate(self.index.doc_terms):
            for term in counts:
                self.postings[term].append(i)

    def top_n(self, query: str, n: int, exclude=()) -> list:
        excluded = set(exclude)
        scores = defaultdict(float)
        for term in norm_terms(query):
            for i in self.postings.get(term, ()):
                if i not in excluded:
                    scores[i] += self.index.term_score(term, i)
        ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
        out = [i for i, _ in ranked[:n]]
        if len(out) < n:
            taken = set(out) | excluded
            for i in range(len(self.chunks)):
                if i not in taken:
                    out.append(i)
                    if len(out) == n:
                        break
        return out


def _gold_positions(chunks: list, gold_keys: set) -> list:
    """Indices of chunks whose document supports one of the derivation facts."""
    return [i for i, c in enumerate(chunks) if set(c.supports) & gold_keys]


def build_bank(candidate_chunks: list, gold_idx: list, bank_size: int,
               mode: str, question_text: str, rng,
               retriever: ChunkRetriever | None = None) -> tuple:
    """Choose bank_size chunks out of the candidates and shuffle them.

    Returns (chunks, gold_positions). Gold positions are the ranks the gold
    chunks landed at after the shuffle, which is what makes the chunk
    position embedding a real signal rather than a giveaway: gold sits at a
    random rank in oracle mode and at its retrieved rank in retrieval mode.
    """
    n_total = len(candidate_chunks)
    bank_size = min(bank_size, n_total)
    gold_set = set(gold_idx)

    if mode == "oracle":
        picked = list(gold_idx[:bank_size])
        rest = [i for i in range(n_total) if i not in set(picked)]
        need = min(bank_size - len(picked), len(rest))
        if need > 0:
            picked.extend(rest[i] for i in rng.choice(len(rest), size=need, replace=False))
        order = rng.permutation(len(picked))
        picked = [picked[i] for i in order]
    elif mode == "distractors":
        rest = [i for i in range(n_total) if i not in gold_set]
        take = min(bank_size, len(rest))
        picked = [rest[i] for i in rng.choice(len(rest), size=take, replace=False)] if take else []
    elif mode == "retrieval":
        if retriever is None:
            raise ValueError("retrieval mode needs a retriever")
        picked = retriever.top_n(question_text, bank_size)
    else:
        raise ValueError(f"unknown bank mode {mode!r}")

    chunks = [candidate_chunks[i] for i in picked]
    gold_positions = tuple(pos for pos, i in enumerate(picked) if i in gold_set)
    return chunks, gold_positions


def examples_from_episode(episode: dict, tokenizer, chunk_len: int,
                          bank_size: int, mode: str, seed: int,
                          pool_chunks: list | None = None,
                          retriever: ChunkRetriever | None = None) -> list:
    """One example per question of a worldgen episode.

    The candidate set is the episode's own chunks first, then the pool of
    chunks harvested from other episodes, so an episode with 23 short
    documents can still fill a bank of 256. Gold chunks are the ones whose
    document supports a fact in the question's derivation.
    """
    own = episode_chunks(episode, tokenizer, chunk_len)
    pool = list(pool_chunks or [])
    candidates = own + pool
    if retriever is None and mode == "retrieval":
        retriever = ChunkRetriever(candidates)
    out = []
    for qi, question in enumerate(episode.get("questions", [])):
        derivation = set(question.get("derivation") or [])
        gold_idx = _gold_positions(own, derivation) if derivation else []
        rng = np.random.default_rng((seed, hash_str(episode.get("episode_id", "")), qi))
        chunks, gold_positions = build_bank(
            candidates, gold_idx, bank_size, mode, question["text"], rng, retriever
        )
        out.append(EvidenceExample(
            question_ids=tokenizer.encode(question["text"]),
            answer_ids=tokenizer.encode(question["answer"]),
            chunks=chunks,
            gold_positions=gold_positions,
            mode=mode,
            question_text=question["text"],
            answer_text=question["answer"],
        ))
    return out


def examples_from_web_episode(episode: dict, tokenizer, chunk_len: int,
                              bank_size: int, mode: str, seed: int,
                              pool_chunks: list | None = None,
                              retriever: ChunkRetriever | None = None) -> list:
    """One example per question of a scrubbed-web bundle from src/scrub.

    A web episode has no derivation ids; the gold document is the last hop
    of the verified plan, and the gold chunks are the windows of that
    document that actually contain the answer span.
    """
    doc_texts = [d["text"] for d in episode["documents"]]
    own = []
    for i, text in enumerate(doc_texts):
        own.extend(chunk_document(text, tokenizer, chunk_len, reliability=1.0,
                                  source=episode.get("world", {}).get("domain", "web"),
                                  doc_index=i))
    pool = list(pool_chunks or [])
    candidates = own + pool
    if retriever is None and mode == "retrieval":
        retriever = ChunkRetriever(candidates)

    out = []
    for qi, question in enumerate(episode.get("questions", [])):
        plan = question.get("plan") or []
        target = plan[-1][1] if plan else -1
        answer = question["answer"]
        gold_idx = [i for i, c in enumerate(own)
                    if c.doc_index == target and answer in c.text]
        if not gold_idx:
            gold_idx = [i for i, c in enumerate(own) if c.doc_index == target]
        rng = np.random.default_rng((seed, hash_str(str(target)), qi))
        chunks, gold_positions = build_bank(
            candidates, gold_idx, bank_size, mode, question["text"], rng, retriever
        )
        out.append(EvidenceExample(
            question_ids=tokenizer.encode(question["text"]),
            answer_ids=tokenizer.encode(answer),
            chunks=chunks,
            gold_positions=gold_positions,
            mode=mode,
            question_text=question["text"],
            answer_text=answer,
        ))
    return out


def decode_chunk(chunk: Chunk, tokenizer) -> str:
    return tokenizer.decode(chunk.token_ids)


def hash_str(s: str) -> int:
    """Stable small integer from a string, for seeding. Python's hash is
    salted per process, so it cannot be used for anything reproducible."""
    h = 2166136261
    for byte in s.encode("utf-8"):
        h = ((h ^ byte) * 16777619) & 0xFFFFFFFF
    return h


@dataclass
class EvidenceBatch:
    """Tensors for one training step, all on the same device."""

    input_ids: torch.Tensor
    targets: torch.Tensor
    evidence_ids: torch.Tensor
    evidence_mask: torch.Tensor
    chunk_mask: torch.Tensor
    reliability: torch.Tensor
    gold_present: torch.Tensor

    def to(self, device):
        return EvidenceBatch(**{k: v.to(device) for k, v in self.__dict__.items()})

    @property
    def n_answer_tokens(self) -> int:
        return int((self.targets != IGNORE_INDEX).sum())

    @property
    def n_evidence_tokens(self) -> int:
        return int(self.evidence_mask.sum())


class EvidenceCollator:
    """Turns EvidenceExamples into padded batches.

    The working sequence is right padded with the pad token and the padded
    positions are IGNORE_INDEX in the targets, so causal attention never
    lets a padded tail change a real position and the loss never sees one.
    Banks shorter than bank_size are padded with empty chunks and marked in
    chunk_mask.
    """

    def __init__(self, tokenizer, bank_size: int, chunk_len: int,
                 max_seq_len: int, pad_id: int | None = None):
        self.tokenizer = tokenizer
        self.bank_size = bank_size
        self.chunk_len = chunk_len
        self.max_seq_len = max_seq_len
        sid = tokenizer.special_ids
        self.q_id = sid["<|q|>"]
        self.a_id = sid["<|a|>"]
        self.eot_id = sid["<|eot|>"]
        self.pad_id = self.eot_id if pad_id is None else pad_id

    def encode_example(self, ex: EvidenceExample) -> tuple:
        """Working-sequence ids and targets for one example.

        Layout: <|q|> question <|a|> answer <|eot|>, next token prediction,
        supervised only on the answer tokens and the closing <|eot|>.
        """
        ids = [self.q_id] + list(ex.question_ids) + [self.a_id] + list(ex.answer_ids) + [self.eot_id]
        if len(ids) > self.max_seq_len + 1:
            raise ValueError(
                f"working sequence of {len(ids)} tokens exceeds max_seq_len {self.max_seq_len}"
            )
        inputs = ids[:-1]
        targets = ids[1:]
        answer_start = 1 + len(ex.question_ids)  # index of <|a|> in inputs
        masked = [IGNORE_INDEX] * len(targets)
        for t in range(answer_start, len(targets)):
            masked[t] = targets[t]
        return inputs, masked

    def __call__(self, examples: list) -> EvidenceBatch:
        rows = [self.encode_example(ex) for ex in examples]
        width = max(len(r[0]) for r in rows)
        bsz = len(examples)
        input_ids = torch.full((bsz, width), self.pad_id, dtype=torch.long)
        targets = torch.full((bsz, width), IGNORE_INDEX, dtype=torch.long)
        for b, (ids, tgt) in enumerate(rows):
            input_ids[b, :len(ids)] = torch.tensor(ids, dtype=torch.long)
            targets[b, :len(tgt)] = torch.tensor(tgt, dtype=torch.long)

        n, L = self.bank_size, self.chunk_len
        evidence_ids = torch.full((bsz, n, L), self.pad_id, dtype=torch.long)
        evidence_mask = torch.zeros((bsz, n, L), dtype=torch.bool)
        chunk_mask = torch.zeros((bsz, n), dtype=torch.bool)
        reliability = torch.ones((bsz, n), dtype=torch.float32)
        for b, ex in enumerate(examples):
            for c, chunk in enumerate(ex.chunks[:n]):
                ids = chunk.token_ids[:L]
                evidence_ids[b, c, :len(ids)] = torch.tensor(ids, dtype=torch.long)
                evidence_mask[b, c, :len(ids)] = True
                chunk_mask[b, c] = True
                reliability[b, c] = chunk.reliability
        gold_present = torch.tensor(
            [ex.gold_present for ex in examples], dtype=torch.bool
        )
        return EvidenceBatch(input_ids, targets, evidence_ids, evidence_mask,
                             chunk_mask, reliability, gold_present)


def bank_stats(examples: list) -> dict:
    """Diagnostics for a set of built examples: gold hit rate and bank fill."""
    if not examples:
        return {"examples": 0}
    n_gold = sum(1 for e in examples if e.gold_present)
    sizes = [len(e.chunks) for e in examples]
    tokens = [sum(len(c.token_ids) for c in e.chunks) for e in examples]
    return {
        "examples": len(examples),
        "gold_present": n_gold,
        "gold_rate": n_gold / len(examples),
        "mean_bank_chunks": sum(sizes) / len(sizes),
        "mean_bank_tokens": sum(tokens) / len(tokens),
        "mean_answer_tokens": sum(len(e.answer_ids) for e in examples) / len(examples),
    }
