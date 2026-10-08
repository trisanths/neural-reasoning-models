"""Sequence and set operation tasks.

Each example renders as input values, an operator token, and the output
values. Two-operand tasks separate the operands with SEP. The tasks:

  sort:    a OP_SORT sorted(a)
  reverse: a OP_REVERSE reversed(a)
  union:   a SEP b OP_UNION sorted unique union of a and b
  diff:    a SEP b OP_DIFF sorted unique elements of a not in b
  delete:  a SEP v OP_DELETE a with every occurrence of v removed
"""

from src.procgen import vocab

TASKS = ("sort", "reverse", "union", "diff", "delete")

VOCAB_RANGES = [
    [vocab.EOS, vocab.SEP + 1],
    [vocab.OP_SORT, vocab.OP_DELETE + 1],
    list(vocab.VALUE_RANGE),
]


def _vals(values):
    return [vocab.value_token(v) for v in values]


def _sample_values(rng, length, num_values):
    return [int(x) for x in rng.integers(num_values, size=length)]


def generate_seqop(rng, task, length=8, num_values=vocab.NUM_VALUES):
    """Return one task example of `length` input values, without EOS."""
    if task not in TASKS:
        raise ValueError(f"unknown task {task!r}")
    if length < 1:
        raise ValueError(f"length must be positive, got {length}")
    if not 1 <= num_values <= vocab.NUM_VALUES:
        raise ValueError(f"num_values must be in 1..{vocab.NUM_VALUES}, got {num_values}")
    a = _sample_values(rng, length, num_values)
    if task == "sort":
        return _vals(a) + [vocab.OP_SORT] + _vals(sorted(a))
    if task == "reverse":
        return _vals(a) + [vocab.OP_REVERSE] + _vals(a[::-1])
    if task == "union":
        b = _sample_values(rng, length, num_values)
        out = sorted(set(a) | set(b))
        return _vals(a) + [vocab.SEP] + _vals(b) + [vocab.OP_UNION] + _vals(out)
    if task == "diff":
        b = _sample_values(rng, length, num_values)
        out = sorted(set(a) - set(b))
        return _vals(a) + [vocab.SEP] + _vals(b) + [vocab.OP_DIFF] + _vals(out)
    v = a[int(rng.integers(len(a)))]
    out = [x for x in a if x != v]
    return _vals(a) + [vocab.SEP, vocab.value_token(v)] + [vocab.OP_DELETE] + _vals(out)


def sample_example(rng, min_len=4, max_len=16):
    """Return one EOS-terminated example with a sampled task and length."""
    task = TASKS[int(rng.integers(len(TASKS)))]
    length = int(rng.integers(min_len, max_len + 1))
    return generate_seqop(rng, task, length=length) + [vocab.EOS]
