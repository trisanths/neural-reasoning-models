"""Chunking, tier ranking contract, and the BM25Index-shaped adapter.

Everything runs against MockExa; no network, no key.
"""

import pytest

from src.retrieval_web.exa import MOCK_FIXTURES, MockExa
from src.retrieval_web.tier import (
    WebRetrievalTier,
    WebTierIndex,
    chunk_text,
)
from src.train.retrieval import BM25Index

QUERY = "okapi bm25 ranking function"


def make_tier(tok, fixtures=None, **kwargs):
    kwargs.setdefault("max_chunk_tokens", 48)
    kwargs.setdefault("num_results", 3)
    return WebRetrievalTier(MockExa(fixtures), tok, **kwargs)


def all_fixture_texts():
    return [r["text"] for results in MOCK_FIXTURES.values() for r in results]


def test_chunk_text_respects_budget(tok):
    for budget in (24, 48, 96):
        for text in all_fixture_texts():
            chunks = chunk_text(text, tok, budget)
            assert chunks
            for chunk in chunks:
                assert len(tok.encode(chunk)) <= budget


def test_chunk_text_preserves_words(tok):
    # With a budget no sentence exceeds, packing never cuts inside a word,
    # so the concatenated chunks carry the original word sequence.
    for text in all_fixture_texts():
        chunks = chunk_text(text, tok, 96)
        assert " ".join(chunks).split() == text.split()


def test_chunk_text_hard_split_preserves_bytes(tok):
    # One giant sentence with no boundaries forces the token window path.
    text = "alpha bravo charlie delta echo foxtrot " * 60
    text = text.strip() + "."
    chunks = chunk_text(text, tok, 24)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(tok.encode(chunk)) <= 24
    assert "".join(chunks) == text


def test_chunk_text_deterministic(tok):
    text = all_fixture_texts()[0]
    assert chunk_text(text, tok, 32) == chunk_text(text, tok, 32)


def test_chunk_text_empty_and_invalid(tok):
    assert chunk_text("", tok, 32) == []
    assert chunk_text("   \n\n  ", tok, 32) == []
    with pytest.raises(ValueError):
        chunk_text("x", tok, 0)


def test_tier_returns_ranked_chunk_dicts(tok):
    tier = make_tier(tok)
    ranked = tier(QUERY)
    assert ranked
    for chunk in ranked:
        assert {"text", "url", "title", "page_rank", "chunk_index",
                "score", "rank"} <= chunk.keys()
        assert len(tok.encode(chunk["text"])) <= 48
    assert [c["rank"] for c in ranked] == list(range(len(ranked)))
    scores = [c["score"] for c in ranked]
    assert scores == sorted(scores, reverse=True)


def test_tier_is_a_callable_like_the_oracle(tok):
    # The duck-typed contract: call it with a query, get ranked chunks.
    tier = make_tier(tok)
    assert callable(tier)
    assert tier(QUERY) == tier(QUERY)


def test_tier_ranks_query_matching_chunk_first(tok):
    boring = ("Nothing relevant lives in this opening sentence about "
              "weather and gardens.")
    hit = ("The target phrase appears here with the target phrase "
           "repeated for weight.")
    # A budget that fits either sentence alone but not both, computed from
    # the actual token counts so the split is guaranteed.
    budget = max(len(tok.encode(boring)), len(tok.encode(hit)))
    fixtures = {
        "the target phrase": [{
            "id": "https://example.org/one",
            "url": "https://example.org/one",
            "title": "one",
            "score": 0.9,
            "text": boring + "\n\n" + hit,
        }],
    }
    tier = make_tier(tok, fixtures=fixtures, max_chunk_tokens=budget)
    ranked = tier("the target phrase")
    assert len(ranked) == 2
    assert "target phrase" in ranked[0]["text"]


def test_tier_empty_results_give_empty_ranking(tok):
    tier = make_tier(tok)
    assert tier("no such canned query") == []


def test_tier_skips_pages_without_text(tok):
    fixtures = {"q": [
        {"id": "a", "url": "a", "title": "a", "score": 0.9, "text": "   "},
        {"id": "b", "url": "b", "title": "b", "score": 0.8,
         "text": "A usable sentence about the topic."},
    ]}
    ranked = make_tier(tok, fixtures=fixtures)("q")
    assert ranked
    assert all(c["url"] == "b" for c in ranked)


def test_tier_caps_chunks_per_page(tok):
    tier = make_tier(tok, max_chunk_tokens=8, max_chunks_per_page=2)
    ranked = tier(QUERY)
    for page_rank in {c["page_rank"] for c in ranked}:
        page_chunks = [c for c in ranked if c["page_rank"] == page_rank]
        assert len(page_chunks) <= 2


def test_adapter_top_serves_and_registers(tok):
    adapter = WebTierIndex(make_tier(tok))
    index = adapter.top(QUERY)
    assert adapter.doc_texts[index]
    assert adapter.doc_meta[index]["url"].startswith("https://example.org/")
    # The same query with the same exclusions serves the same index.
    assert adapter.top(QUERY) == index


def test_adapter_top_without_replacement(tok):
    adapter = WebTierIndex(make_tier(tok))
    served = set()
    first = adapter.top(QUERY, exclude=served)
    served.add(first)
    second = adapter.top(QUERY, exclude=served)
    assert second != first
    served.add(second)
    third = adapter.top(QUERY, exclude=served)
    assert third not in (first, second)


def test_adapter_top_exhaustion_matches_oracle_error(tok):
    adapter = WebTierIndex(make_tier(tok))
    n_chunks = len(adapter.tier(QUERY))
    served = set()
    for _ in range(n_chunks):
        served.add(adapter.top(QUERY, exclude=served))
    with pytest.raises(ValueError, match="every document is excluded"):
        adapter.top(QUERY, exclude=served)


def test_adapter_empty_results_raise_like_exhaustion(tok):
    adapter = WebTierIndex(make_tier(tok))
    with pytest.raises(ValueError):
        adapter.top("no such canned query")


def test_adapter_serving_order_matches_oracle_bm25(tok):
    """Serving the web pool without replacement yields the same chunk texts,
    in the same order, as BM25Index.top over that pool. The adapter is a
    drop-in for the oracle index on a fixed document set."""
    tier = make_tier(tok)
    pool_texts = [c["text"] for c in sorted(
        tier(QUERY), key=lambda c: (c["page_rank"], c["chunk_index"]))]
    oracle = BM25Index(pool_texts)

    adapter = WebTierIndex(make_tier(tok))
    adapter_served, oracle_served = set(), set()
    for _ in range(len(pool_texts)):
        a = adapter.top(QUERY, exclude=adapter_served)
        o = oracle.top(QUERY, exclude=oracle_served)
        assert adapter.doc_texts[a] == pool_texts[o]
        adapter_served.add(a)
        oracle_served.add(o)


def test_adapter_indices_stable_across_queries(tok):
    adapter = WebTierIndex(make_tier(tok, num_results=3))
    first = adapter.top(QUERY)
    text = adapter.doc_texts[first]
    adapter.top("byte level bpe tokenizer")
    assert adapter.doc_texts[first] == text
