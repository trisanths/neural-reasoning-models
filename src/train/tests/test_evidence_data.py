"""Bank construction, the answer-only objective, and determinism."""

import numpy as np
import pytest
import torch

from src.train.evidence_data import (IGNORE_INDEX, ChunkRetriever,
                                     EvidenceCollator, bank_stats,
                                     chunk_document, episode_chunks,
                                     examples_from_episode,
                                     examples_from_web_episode, hash_str)
from src.train.tests.evidence_fixtures import (StubTokenizer, pool_chunks,
                                               synthetic_episode)

CHUNK_LEN = 16
BANK = 24


def build(mode="oracle", bank=BANK, seed=5, n_pool=60):
    tok = StubTokenizer()
    ep = synthetic_episode(n_docs=12, n_questions=3, seed=1)
    pool = pool_chunks(n_pool, CHUNK_LEN, seed=seed)
    return tok, ep, examples_from_episode(ep, tok, CHUNK_LEN, bank, mode, seed,
                                          pool_chunks=pool)


def test_chunking_splits_long_documents_and_keeps_provenance():
    tok = StubTokenizer()
    text = " ".join(f"w{i}" for i in range(37))
    chunks = chunk_document(text, tok, 16, reliability=0.3, source="src", doc_index=4,
                            supports=("f1",))
    assert [len(c.token_ids) for c in chunks] == [16, 16, 5]
    assert all(c.doc_index == 4 and c.source == "src" for c in chunks)
    assert [c.chunk_index for c in chunks] == [0, 1, 2]
    assert all(c.reliability == 0.3 and c.supports == ("f1",) for c in chunks)
    assert chunk_document("", tok, 16) == []


def test_episode_chunks_keep_distractors_and_contradictions():
    tok = StubTokenizer()
    ep = synthetic_episode(n_docs=12, n_questions=3)
    chunks = episode_chunks(ep, tok, CHUNK_LEN)
    # Every document is represented, supporting or not.
    assert len({c.doc_index for c in chunks}) == 12
    assert sum(1 for c in chunks if c.supports) >= 3
    assert sum(1 for c in chunks if not c.supports) >= 9


def test_oracle_mode_always_places_gold():
    _, _, examples = build("oracle")
    assert len(examples) == 3
    for ex in examples:
        assert ex.gold_present
        assert len(ex.chunks) == BANK
        for pos in ex.gold_positions:
            assert ex.chunks[pos].supports


def test_oracle_bank_is_mostly_distractors():
    """The gold chunk is one of many; the model has to select."""
    _, _, examples = build("oracle")
    for ex in examples:
        assert len(ex.gold_positions) <= 2
        assert len(ex.chunks) - len(ex.gold_positions) >= BANK - 2


def test_distractor_mode_removes_gold():
    """Only this question's supporting chunks are removed; the rest stay,
    including documents that support some other question's derivation."""
    _, _, examples = build("distractors")
    for qi, ex in enumerate(examples):
        assert not ex.gold_present
        assert all(f"f{qi}" not in c.supports for c in ex.chunks)
    assert any(c.supports for ex in examples for c in ex.chunks)


def test_retrieval_mode_reports_its_own_hit_rate():
    _, _, examples = build("retrieval", bank=8)
    stats = bank_stats(examples)
    assert stats["examples"] == 3
    assert 0.0 <= stats["gold_rate"] <= 1.0
    # BM25 over an episode whose gold document repeats the question's terms
    # should reach it inside a bank of eight.
    assert stats["gold_rate"] > 0.5
    for ex in examples:
        assert len(ex.chunks) == 8


def test_retrieval_ranking_is_deterministic_and_ordered():
    tok = StubTokenizer()
    ep = synthetic_episode(n_docs=12, n_questions=3)
    chunks = episode_chunks(ep, tok, CHUNK_LEN) + pool_chunks(30, CHUNK_LEN)
    retriever = ChunkRetriever(chunks)
    a = retriever.top_n("what does subject1 map to", 5)
    b = retriever.top_n("what does subject1 map to", 5)
    assert a == b
    assert len(set(a)) == 5
    scored = [retriever.index.score("what does subject1 map to", i) for i in a]
    assert scored == sorted(scored, reverse=True)


def test_retriever_pads_when_the_query_matches_too_few_chunks():
    tok = StubTokenizer()
    chunks = episode_chunks(synthetic_episode(n_docs=4, n_questions=1), tok, CHUNK_LEN)
    retriever = ChunkRetriever(chunks)
    got = retriever.top_n("zzzz nothing matches this", 4)
    assert sorted(got) == [0, 1, 2, 3]


def test_bank_pool_lets_a_small_episode_fill_a_large_bank():
    _, _, examples = build("oracle", bank=200, n_pool=400)
    for ex in examples:
        assert len(ex.chunks) == 200
        assert sum(1 for c in ex.chunks if c.source == "pool") > 150


def test_collator_supervises_answer_tokens_only():
    tok, _, examples = build("oracle", bank=8)
    collator = EvidenceCollator(tok, bank_size=8, chunk_len=CHUNK_LEN, max_seq_len=64)
    batch = collator(examples)
    bsz, width = batch.input_ids.shape
    assert batch.targets.shape == (bsz, width)
    for b, ex in enumerate(examples):
        supervised = (batch.targets[b] != IGNORE_INDEX).nonzero().flatten().tolist()
        expected_n = len(ex.answer_ids) + 1  # answer tokens plus the closing eot
        assert len(supervised) == expected_n
        got = batch.targets[b][supervised].tolist()
        assert got == list(ex.answer_ids) + [tok.special_ids["<|eot|>"]]
        # Nothing from the question is ever a target.
        assert all(t not in ex.question_ids for t in got) or not ex.question_ids
        # The input at each supervised position is the token before it.
        prev = batch.input_ids[b][supervised[0]]
        assert int(prev) == tok.special_ids["<|a|>"]


def test_evidence_tokens_are_never_prediction_targets():
    """Evidence lives outside the working sequence, so it cannot be predicted."""
    tok, _, examples = build("oracle", bank=8)
    collator = EvidenceCollator(tok, bank_size=8, chunk_len=CHUNK_LEN, max_seq_len=64)
    batch = collator(examples)
    working = set(batch.input_ids.flatten().tolist())
    for b, ex in enumerate(examples):
        chunk_positions = batch.evidence_mask[b].sum()
        assert chunk_positions > 0
    # The targets vector has exactly as many live entries as answer tokens,
    # no matter how many evidence tokens the bank carries.
    live = int((batch.targets != IGNORE_INDEX).sum())
    assert live == sum(len(e.answer_ids) + 1 for e in examples)
    assert batch.n_evidence_tokens > 10 * live


def test_collator_pads_short_banks_and_marks_them():
    tok = StubTokenizer()
    ep = synthetic_episode(n_docs=4, n_questions=2)
    examples = examples_from_episode(ep, tok, CHUNK_LEN, 32, "oracle", 3)
    collator = EvidenceCollator(tok, bank_size=32, chunk_len=CHUNK_LEN, max_seq_len=64)
    batch = collator(examples)
    assert batch.evidence_ids.shape == (2, 32, CHUNK_LEN)
    for b, ex in enumerate(examples):
        n = len(ex.chunks)
        assert bool(batch.chunk_mask[b, :n].all())
        assert not bool(batch.chunk_mask[b, n:].any())
        assert not bool(batch.evidence_mask[b, n:].any())


def test_collator_pads_the_working_sequence_without_supervising_the_pad():
    tok = StubTokenizer()
    ep = synthetic_episode(n_docs=6, n_questions=3)
    examples = examples_from_episode(ep, tok, CHUNK_LEN, 8, "oracle", 3)
    examples[0].answer_ids = examples[0].answer_ids + [42, 43, 44]
    collator = EvidenceCollator(tok, bank_size=8, chunk_len=CHUNK_LEN, max_seq_len=64)
    batch = collator(examples)
    lengths = [(batch.targets[b] != IGNORE_INDEX).sum().item() for b in range(3)]
    assert lengths[0] == len(examples[0].answer_ids) + 1
    assert batch.input_ids.shape[1] == max(
        1 + len(e.question_ids) + 1 + len(e.answer_ids) for e in examples
    )


def test_collator_rejects_an_overlong_working_sequence():
    tok = StubTokenizer()
    ep = synthetic_episode(n_docs=4, n_questions=1)
    examples = examples_from_episode(ep, tok, CHUNK_LEN, 8, "oracle", 3)
    examples[0].answer_ids = list(range(100))
    collator = EvidenceCollator(tok, bank_size=8, chunk_len=CHUNK_LEN, max_seq_len=16)
    with pytest.raises(ValueError):
        collator(examples)


def test_bank_construction_is_deterministic():
    a = build("oracle", seed=9)[2]
    b = build("oracle", seed=9)[2]
    c = build("oracle", seed=10)[2]
    key = lambda exs: [[ch.token_ids for ch in e.chunks] for e in exs]
    assert key(a) == key(b)
    assert key(a) != key(c)


def test_collation_is_deterministic():
    tok, _, examples = build("oracle", bank=8)
    collator = EvidenceCollator(tok, bank_size=8, chunk_len=CHUNK_LEN, max_seq_len=64)
    first = collator(examples)
    second = collator(examples)
    assert torch.equal(first.input_ids, second.input_ids)
    assert torch.equal(first.evidence_ids, second.evidence_ids)
    assert torch.equal(first.reliability, second.reliability)


def test_reliability_reaches_the_batch():
    tok, ep, examples = build("oracle", bank=BANK)
    collator = EvidenceCollator(tok, bank_size=BANK, chunk_len=CHUNK_LEN, max_seq_len=64)
    batch = collator(examples)
    live = batch.reliability[batch.chunk_mask]
    assert float(live.min()) < float(live.max())
    assert 0.0 <= float(live.min()) and float(live.max()) <= 1.0


def test_web_episode_examples():
    """Scrubbed-web bundles go through the same path as worldgen episodes."""
    tok = StubTokenizer()
    docs = [f"document {i} says the token value{i} appears in section {i}" for i in range(6)]
    episode = {
        "world": {"domain": "scrubbed_web"},
        "documents": [{"text": t} for t in docs],
        "questions": [
            {"text": "which token appears in section 3", "answer": "value3",
             "plan": [["section 3", 3]]},
            {"text": "which token appears in section 5", "answer": "value5",
             "plan": [["bridge", 1], ["section 5", 5]]},
        ],
    }
    examples = examples_from_web_episode(episode, tok, CHUNK_LEN, 6, "oracle", 2)
    assert len(examples) == 2
    for ex in examples:
        assert ex.gold_present
        assert len(ex.chunks) == 6
    assert examples[1].chunks[examples[1].gold_positions[0]].doc_index == 5


def test_hash_str_is_stable_across_processes():
    assert hash_str("ep-000000") == hash_str("ep-000000")
    assert hash_str("ep-000000") != hash_str("ep-000001")
    assert hash_str("") == 2166136261


def test_batch_device_move_keeps_shapes():
    tok, _, examples = build("oracle", bank=8)
    collator = EvidenceCollator(tok, bank_size=8, chunk_len=CHUNK_LEN, max_seq_len=64)
    batch = collator(examples).to("cpu")
    assert batch.input_ids.device.type == "cpu"
    assert batch.n_answer_tokens > 0
