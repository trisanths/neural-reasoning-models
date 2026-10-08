import json
import random

import pytest

from src.train.data import ShardReader
from src.train.retrieval import (
    BM25Index,
    build_query,
    render_episode_retrieval,
    render_jsonl_to_shards_retrieval,
    terms,
)
from src.train.tokenizer import load_tokenizer, train_tokenizer


@pytest.fixture(scope="module")
def tok(tmp_path_factory):
    base = tmp_path_factory.mktemp("retrievalcorpus")
    rng = random.Random(7)
    words = [
        "lomera", "vantrix", "korath", "acquired", "shipped", "company",
        "officer", "route", "the", "of", "reports", "that", "cargo", "who",
    ]
    corpus = base / "corpus.txt"
    with open(corpus, "w") as fh:
        for _ in range(1500):
            fh.write(" ".join(rng.choices(words, k=10)) + "\n")
    path = base / "tokenizer.json"
    train_tokenizer([str(corpus)], out_path=str(path), vocab_size=1024)
    return load_tokenizer(str(path))


def make_episode():
    docs = [
        "the officer reports that cargo shipped on the route",
        "lomera acquired vantrix in the third quarter",
        "korath holds the northern route contract",
    ]
    return {
        "episode_id": "ep-000000",
        "seed": 1,
        "world": {
            "domain": "corporate",
            "entities": [
                {"id": "e1", "type": "company", "name": "Lomera"},
                {"id": "e2", "type": "company", "name": "Vantrix"},
            ],
            "rules": ["acquisition transfers subsidiaries"],
            "facts": [{"id": "f1", "s": "e1", "p": "acquired", "o": "e2", "t": 3}],
        },
        "documents": [
            {
                "doc_id": f"d{i + 1}",
                "text": text,
                "reliability": 0.9,
                "style": "filing",
                "supports": ["f1"] if i == 1 else [],
                "contradicts": [],
            }
            for i, text in enumerate(docs)
        ],
        "questions": [
            {
                "qid": "q1",
                "text": "who acquired vantrix",
                "answer": "lomera",
                "type": "multi_hop",
                "derivation": ["f1"],
                "hops": 1,
            }
        ],
    }


def test_terms_and_query_are_deterministic():
    assert terms("Who Acquired Vantrix?") == ["who", "acquired", "vantrix"]
    assert build_query("Who Acquired Vantrix?") == "who acquired vantrix"


def test_bm25_ranks_matching_document_first():
    docs = [d["text"] for d in make_episode()["documents"]]
    index = BM25Index(docs)
    assert index.top("who acquired vantrix") == 1
    assert index.top("northern route contract") == 2


def test_bm25_tie_breaks_toward_earliest():
    index = BM25Index(["alpha beta", "alpha beta"])
    assert index.top("alpha") == 0


def test_retrieval_trace_structure(tok):
    episode = make_episode()
    ids = render_episode_retrieval(episode, tok)
    sid = tok.special_ids
    for name in ("<|q|>", "<|retrieve|>", "<|result|>", "<|a|>", "<|eot|>"):
        assert ids.count(sid[name]) == 1
    order = [
        ids.index(sid["<|q|>"]),
        ids.index(sid["<|retrieve|>"]),
        ids.index(sid["<|result|>"]),
        ids.index(sid["<|a|>"]),
        ids.index(sid["<|eot|>"]),
    ]
    assert order == sorted(order)
    assert ids[-1] == sid["<|eot|>"]

    # The result span holds exactly the top BM25 document for the query.
    start = ids.index(sid["<|result|>"]) + 1
    end = ids.index(sid["<|a|>"])
    assert ids[start:end] == tok.encode(episode["documents"][1]["text"])
    # The query span reproduces build_query of the question.
    qstart = ids.index(sid["<|retrieve|>"]) + 1
    assert ids[qstart:start - 1] == tok.encode(build_query("who acquired vantrix"))


def test_retrieval_reaches_past_doc_budget(tok):
    episode = make_episode()
    # A budget of zero keeps every document out of the context.
    ids = render_episode_retrieval(episode, tok, max_doc_tokens=0)
    sid = tok.special_ids
    assert ids.count(sid["<|doc|>"]) == 0
    start = ids.index(sid["<|result|>"]) + 1
    end = ids.index(sid["<|a|>"])
    assert ids[start:end] == tok.encode(episode["documents"][1]["text"])


def test_render_jsonl_to_shards_retrieval(tok, tmp_path):
    jsonl = tmp_path / "episodes.jsonl"
    with open(jsonl, "w") as fh:
        for _ in range(3):
            fh.write(json.dumps(make_episode()) + "\n")
    out = tmp_path / "shards"
    total = render_jsonl_to_shards_retrieval(str(jsonl), tok, out, shard_size=256)
    reader = ShardReader(out)
    assert reader.total_tokens == total
    assert total == 3 * len(render_episode_retrieval(make_episode(), tok))
