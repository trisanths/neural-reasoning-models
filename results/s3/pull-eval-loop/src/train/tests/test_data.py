import json
import random

import numpy as np
import pytest

from src.train.data import (
    ArraySource,
    BatchLoader,
    ShardReader,
    ShardWriter,
    load_procgen_bin,
    render_episode,
    render_jsonl_to_shards,
)
from src.train.tokenizer import PROCGEN_OFFSET, load_tokenizer, train_tokenizer


@pytest.fixture(scope="module")
def tok(tmp_path_factory):
    base = tmp_path_factory.mktemp("datacorpus")
    rng = random.Random(5)
    words = ["lomera", "vantrix", "acquired", "company", "officer", "the", "of", "reports"]
    corpus = base / "corpus.txt"
    with open(corpus, "w") as fh:
        for _ in range(1500):
            fh.write(" ".join(rng.choices(words, k=10)) + "\n")
    path = base / "tokenizer.json"
    train_tokenizer([str(corpus)], out_path=str(path), vocab_size=1024)
    return load_tokenizer(str(path))


def make_episode(n_docs=3, n_questions=2):
    return {
        "episode_id": "ep-000000",
        "seed": 12345,
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
                "doc_id": f"d{i}",
                "text": f"the officer reports that lomera acquired vantrix in filing {i}",
                "reliability": 0.9,
                "style": "filing",
                "supports": ["f1"],
                "contradicts": [],
            }
            for i in range(n_docs)
        ],
        "questions": [
            {
                "qid": f"q{i}",
                "text": "who acquired vantrix",
                "answer": "lomera",
                "type": "multi_hop",
                "derivation": ["f1"],
                "hops": 1,
            }
            for i in range(n_questions)
        ],
    }


def test_shard_write_read_round_trip(tmp_path):
    rng = np.random.default_rng(0)
    tokens = rng.integers(0, 1 << 16, size=10007, dtype=np.uint16)
    writer = ShardWriter(tmp_path, shard_size=1000)
    for start in range(0, tokens.size, 333):
        writer.write(tokens[start : start + 333])
    writer.close()

    with open(tmp_path / "index.json") as fh:
        index = json.load(fh)
    assert index["total_tokens"] == tokens.size
    assert len(index["shards"]) == 11

    reader = ShardReader(tmp_path)
    assert reader.total_tokens == tokens.size
    assert np.array_equal(reader.get_slice(0, tokens.size), tokens)
    # Slices that span shard boundaries must come back intact.
    assert np.array_equal(reader.get_slice(995, 2010), tokens[995:3005])
    assert np.array_equal(reader.get_slice(9990, 17), tokens[9990:])


def test_shard_writer_rejects_oversized_ids(tmp_path):
    writer = ShardWriter(tmp_path)
    with pytest.raises(ValueError):
        writer.write(np.array([70000]))


def test_render_episode_structure(tok):
    episode = make_episode(n_docs=3, n_questions=2)
    ids = render_episode(episode, tok)
    sid = tok.special_ids
    assert ids[0] == sid["<|world|>"]
    assert ids.count(sid["<|doc|>"]) == 3
    assert ids.count(sid["<|q|>"]) == 2
    assert ids.count(sid["<|a|>"]) == 2
    assert ids.count(sid["<|eot|>"]) == 2
    assert ids[-1] == sid["<|eot|>"]
    text = tok.decode(ids)
    assert "domain: corporate" in text
    assert "who acquired vantrix" in text


def test_render_episode_doc_budget(tok):
    episode = make_episode(n_docs=5)
    one_doc = len(tok.encode(episode["documents"][0]["text"])) + 1
    ids = render_episode(episode, tok, max_doc_tokens=2 * one_doc)
    assert ids.count(tok.special_ids["<|doc|>"]) == 2


def test_render_jsonl_to_shards(tok, tmp_path):
    jsonl = tmp_path / "episodes.jsonl"
    with open(jsonl, "w") as fh:
        for _ in range(4):
            fh.write(json.dumps(make_episode()) + "\n")
    out = tmp_path / "shards"
    total = render_jsonl_to_shards(str(jsonl), tok, out, shard_size=256)
    reader = ShardReader(out)
    assert reader.total_tokens == total
    assert total == 4 * len(render_episode(make_episode(), tok))


def test_procgen_offset(tmp_path):
    raw = np.array([0, 1, 5, 255, 17], dtype=np.uint16)
    path = tmp_path / "warmup.bin"
    raw.tofile(path)
    mapped = load_procgen_bin(str(path))
    assert np.array_equal(mapped, raw + PROCGEN_OFFSET)

    bad = np.array([0, 256], dtype=np.uint16)
    bad_path = tmp_path / "bad.bin"
    bad.tofile(bad_path)
    with pytest.raises(ValueError):
        load_procgen_bin(str(bad_path))


def test_batch_loader_shapes_and_determinism():
    tokens = np.random.default_rng(1).integers(0, 500, size=5000, dtype=np.uint16)
    source = ArraySource(tokens)
    a = BatchLoader(source, batch_size=4, seq_len=64, seed=9)
    b = BatchLoader(source, batch_size=4, seq_len=64, seed=9)
    c = BatchLoader(source, batch_size=4, seq_len=64, seed=10)
    xa, ya = a.next_batch()
    xb, yb = b.next_batch()
    xc, _ = c.next_batch()
    assert xa.shape == (4, 64) and ya.shape == (4, 64)
    assert xa.dtype.is_floating_point is False
    # The target is the input shifted by one position.
    assert (xa[:, 1:] == ya[:, :-1]).all()
    assert (xa == xb).all() and (ya == yb).all()
    assert not (xa == xc).all()
