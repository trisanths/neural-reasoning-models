import numpy as np
import pytest

from src.procgen import dyck, vocab


def decode(tok):
    offset = tok - vocab.BRACKET_BASE
    return offset // 2, offset % 2 == 0


def test_dyck_determinism():
    for seed in range(5):
        a = dyck.generate_dyck(np.random.default_rng(seed), k=8, length=100)
        b = dyck.generate_dyck(np.random.default_rng(seed), k=8, length=100)
        assert a == b
        a = dyck.sample_dyck_example(np.random.default_rng(seed))
        b = dyck.sample_dyck_example(np.random.default_rng(seed))
        assert a == b


def test_shuffle_dyck_determinism():
    for seed in range(5):
        a = dyck.generate_shuffle_dyck(np.random.default_rng(seed), k=8, length=100)
        b = dyck.generate_shuffle_dyck(np.random.default_rng(seed), k=8, length=100)
        assert a == b
        a = dyck.sample_shuffle_dyck_example(np.random.default_rng(seed))
        b = dyck.sample_shuffle_dyck_example(np.random.default_rng(seed))
        assert a == b


def test_dyck_seeds_differ():
    a = dyck.generate_dyck(np.random.default_rng(0), k=8, length=200)
    b = dyck.generate_dyck(np.random.default_rng(1), k=8, length=200)
    assert a != b


def test_dyck_well_formed():
    rng = np.random.default_rng(42)
    for k in (1, 4, 8, 16):
        for length in (2, 20, 128):
            word = dyck.generate_dyck(rng, k=k, length=length)
            assert len(word) == length
            stack = []
            for tok in word:
                assert vocab.BRACKET_RANGE[0] <= tok < vocab.BRACKET_RANGE[1]
                t, is_open = decode(tok)
                assert t < k
                if is_open:
                    stack.append(t)
                else:
                    assert stack, "close with empty stack"
                    assert stack.pop() == t, "mismatched close"
            assert not stack, "unclosed brackets"


def test_shuffle_dyck_well_formed():
    rng = np.random.default_rng(43)
    for k in (1, 4, 8, 16):
        for length in (2, 20, 128):
            word = dyck.generate_shuffle_dyck(rng, k=k, length=length)
            assert len(word) == length
            depths = [0] * k
            for tok in word:
                assert vocab.BRACKET_RANGE[0] <= tok < vocab.BRACKET_RANGE[1]
                t, is_open = decode(tok)
                assert t < k
                depths[t] += 1 if is_open else -1
                assert depths[t] >= 0, "close before open for a type"
            assert all(d == 0 for d in depths), "unbalanced type"


def test_examples_end_with_eos_and_stay_in_range():
    rng = np.random.default_rng(44)
    for sampler in (dyck.sample_dyck_example, dyck.sample_shuffle_dyck_example):
        ex = sampler(rng)
        assert ex[-1] == vocab.EOS
        allowed = set()
        for lo, hi in dyck.VOCAB_RANGES:
            allowed.update(range(lo, hi))
        assert set(ex) <= allowed


def test_bad_args_raise():
    rng = np.random.default_rng(0)
    with pytest.raises(ValueError):
        dyck.generate_dyck(rng, k=8, length=7)
    with pytest.raises(ValueError):
        dyck.generate_dyck(rng, k=0, length=8)
    with pytest.raises(ValueError):
        dyck.generate_shuffle_dyck(rng, k=17, length=8)
