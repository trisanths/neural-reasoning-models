import json

import numpy as np
import pytest

from src.procgen import cli, vocab

MIX = "dyck=0.3,shuffle_dyck=0.2,stack=0.15,seqops=0.15,ca=0.1,graph=0.1"


def run(tmp_path, name, tokens=50000, seed=3, mix=MIX):
    out = tmp_path / name
    rc = cli.main([
        "--tokens", str(tokens),
        "--seed", str(seed),
        "--mix", mix,
        "--out", str(out),
    ])
    assert rc == 0
    arr = np.fromfile(out, dtype=np.uint16)
    with open(str(out) + ".meta.json", encoding="utf-8") as f:
        meta = json.load(f)
    return arr, meta


def test_parse_mix():
    mix = cli.parse_mix("dyck=1,ca=3")
    assert mix == {"dyck": 0.25, "ca": 0.75}
    with pytest.raises(ValueError):
        cli.parse_mix("nosuch=1")
    with pytest.raises(ValueError):
        cli.parse_mix("dyck=0")
    with pytest.raises(ValueError):
        cli.parse_mix("dyck=1,dyck=2")
    with pytest.raises(ValueError):
        cli.parse_mix("")


def test_same_seed_gives_identical_output(tmp_path):
    a, meta_a = run(tmp_path, "a.bin")
    b, meta_b = run(tmp_path, "b.bin")
    assert np.array_equal(a, b)
    assert meta_a == meta_b


def test_different_seed_gives_different_output(tmp_path):
    a, _ = run(tmp_path, "a.bin", seed=3)
    b, _ = run(tmp_path, "b.bin", seed=4)
    assert not np.array_equal(a, b)


def test_exact_token_count_and_dtype(tmp_path):
    tokens = 12345
    arr, meta = run(tmp_path, "c.bin", tokens=tokens)
    assert arr.size == tokens
    assert arr.dtype == np.uint16
    assert meta["tokens"] == tokens


def test_vocabulary_stays_within_declared_ranges(tmp_path):
    arr, meta = run(tmp_path, "d.bin")
    assert int(arr.max()) < meta["vocab"]["vocab_size"]
    present = set(np.unique(arr).tolist())
    reserved = set(meta["vocab"]["reserved_ids"])
    assert not (present & reserved), "reserved ids leaked into the stream"
    allowed = set()
    for ranges in meta["generator_ranges"].values():
        for lo, hi in ranges:
            allowed.update(range(lo, hi))
    assert present <= allowed


def test_mix_proportions_approximately_honored(tmp_path):
    arr, meta = run(tmp_path, "e.bin", tokens=200000)
    weights = meta["mix"]
    counts = meta["token_counts_before_truncation"]
    total = sum(counts.values())
    assert total >= 200000
    for name, weight in weights.items():
        share = counts[name] / total
        assert abs(share - weight) < 0.02, f"{name}: share {share} vs weight {weight}"
    assert all(meta["example_counts"][name] > 0 for name in weights)


def test_partial_mix(tmp_path):
    arr, meta = run(tmp_path, "f.bin", tokens=20000, mix="dyck=0.5,ca=0.5")
    assert set(meta["mix"]) == {"dyck", "ca"}
    present = set(np.unique(arr).tolist())
    for tok in (vocab.PUSH, vocab.POP, vocab.EDGE, vocab.QUERY):
        assert tok not in present


def test_every_generator_is_seed_deterministic():
    for name, fn in cli.GENERATORS.items():
        a = fn(np.random.default_rng(99))
        b = fn(np.random.default_rng(99))
        assert a == b, name
