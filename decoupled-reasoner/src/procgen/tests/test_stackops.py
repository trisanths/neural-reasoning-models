import numpy as np

from src.procgen import stackops, vocab


def replay(trace):
    """Simulate the trace and check every observation against the stack."""
    stack = []
    i = 0
    ops = 0
    while i < len(trace):
        tok = trace[i]
        if tok == vocab.PUSH:
            val = trace[i + 1]
            assert vocab.VALUE_RANGE[0] <= val < vocab.VALUE_RANGE[1]
            stack.append(val)
            i += 2
        elif tok == vocab.POP:
            assert stack, "pop on empty stack"
            stack.pop()
            i += 1
        else:
            raise AssertionError(f"expected an op token, got {tok}")
        assert trace[i] == vocab.OBS
        expected = stack[-1] if stack else vocab.EMPTY
        assert trace[i + 1] == expected
        i += 2
        ops += 1
    return ops


def test_determinism():
    for seed in range(5):
        a = stackops.generate_stack_trace(np.random.default_rng(seed), num_ops=30)
        b = stackops.generate_stack_trace(np.random.default_rng(seed), num_ops=30)
        assert a == b
        a = stackops.sample_example(np.random.default_rng(seed))
        b = stackops.sample_example(np.random.default_rng(seed))
        assert a == b


def test_observations_match_simulation():
    rng = np.random.default_rng(7)
    for _ in range(50):
        num_ops = int(rng.integers(1, 60))
        trace = stackops.generate_stack_trace(rng, num_ops=num_ops)
        assert replay(trace) == num_ops


def test_example_ends_with_eos_and_stays_in_range():
    rng = np.random.default_rng(8)
    ex = stackops.sample_example(rng)
    assert ex[-1] == vocab.EOS
    allowed = set()
    for lo, hi in stackops.VOCAB_RANGES:
        allowed.update(range(lo, hi))
    assert set(ex) <= allowed
    replay(ex[:-1])
