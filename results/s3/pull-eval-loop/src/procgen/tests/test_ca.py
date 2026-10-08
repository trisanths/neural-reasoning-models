import numpy as np

from src.procgen import ca, vocab

RULE110 = {
    (1, 1, 1): 0,
    (1, 1, 0): 1,
    (1, 0, 1): 1,
    (1, 0, 0): 0,
    (0, 1, 1): 1,
    (0, 1, 0): 1,
    (0, 0, 1): 1,
    (0, 0, 0): 0,
}


def reference_step(row):
    n = len(row)
    return [RULE110[(row[(i - 1) % n], row[i], row[(i + 1) % n])] for i in range(n)]


def parse_rows(trace):
    assert trace[0] == vocab.ROW
    rows = [[]]
    for tok in trace[1:]:
        if tok == vocab.NEXT:
            rows.append([])
        else:
            assert vocab.BIT_RANGE[0] <= tok < vocab.BIT_RANGE[1]
            rows[-1].append(tok - vocab.BIT_BASE)
    return rows


def test_determinism():
    for seed in range(5):
        a = ca.generate_ca_trace(np.random.default_rng(seed), width=20, steps=3)
        b = ca.generate_ca_trace(np.random.default_rng(seed), width=20, steps=3)
        assert a == b
        a = ca.sample_example(np.random.default_rng(seed))
        b = ca.sample_example(np.random.default_rng(seed))
        assert a == b


def test_rows_follow_rule_110():
    rng = np.random.default_rng(21)
    for _ in range(40):
        width = int(rng.integers(3, 40))
        steps = int(rng.integers(1, 6))
        trace = ca.generate_ca_trace(rng, width=width, steps=steps)
        rows = parse_rows(trace)
        assert len(rows) == steps + 1
        for row in rows:
            assert len(row) == width
        for prev, nxt in zip(rows, rows[1:]):
            assert nxt == reference_step(prev)


def test_example_ends_with_eos_and_stays_in_range():
    rng = np.random.default_rng(22)
    ex = ca.sample_example(rng)
    assert ex[-1] == vocab.EOS
    allowed = set()
    for lo, hi in ca.VOCAB_RANGES:
        allowed.update(range(lo, hi))
    assert set(ex) <= allowed
    rows = parse_rows(ex[:-1])
    for prev, nxt in zip(rows, rows[1:]):
        assert nxt == reference_step(prev)
