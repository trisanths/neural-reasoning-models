"""Stack operation traces.

A trace is a sequence of push and pop operations on one stack. Every
operation is followed by an observation of the resulting stack top, so the
stream reads: PUSH v OBS top, or POP OBS top, where top is EMPTY when the
stack has no elements. Pops never occur on an empty stack.
"""

from src.procgen import vocab

VOCAB_RANGES = [
    [vocab.EOS, vocab.EOS + 1],
    [vocab.PUSH, vocab.EMPTY + 1],
    list(vocab.VALUE_RANGE),
]


def generate_stack_trace(rng, num_ops=16, num_values=vocab.NUM_VALUES, pop_prob=0.5):
    """Return a trace of `num_ops` operations with observations after each."""
    if num_ops < 1:
        raise ValueError(f"num_ops must be positive, got {num_ops}")
    if not 1 <= num_values <= vocab.NUM_VALUES:
        raise ValueError(f"num_values must be in 1..{vocab.NUM_VALUES}, got {num_values}")
    stack = []
    out = []
    for _ in range(num_ops):
        if stack and rng.random() < pop_prob:
            stack.pop()
            out.append(vocab.POP)
        else:
            v = int(rng.integers(num_values))
            stack.append(v)
            out.append(vocab.PUSH)
            out.append(vocab.value_token(v))
        out.append(vocab.OBS)
        out.append(vocab.value_token(stack[-1]) if stack else vocab.EMPTY)
    return out


def sample_example(rng, min_ops=8, max_ops=40):
    """Return one EOS-terminated stack trace with a sampled operation count."""
    num_ops = int(rng.integers(min_ops, max_ops + 1))
    return generate_stack_trace(rng, num_ops=num_ops) + [vocab.EOS]
