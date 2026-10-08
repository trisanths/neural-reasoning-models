"""Elementary cellular automaton rule 110 traces.

A trace is an initial random row followed by one or more successor rows,
each computed by rule 110 with a circular boundary. The stream reads:
ROW bits NEXT bits [NEXT bits ...] EOS.
"""

from src.procgen import vocab

RULE = 110

VOCAB_RANGES = [
    [vocab.EOS, vocab.EOS + 1],
    [vocab.ROW, vocab.NEXT + 1],
    list(vocab.BIT_RANGE),
]


def step_rule110(row):
    """Apply one rule 110 step with a circular boundary."""
    n = len(row)
    return [
        (RULE >> ((row[(i - 1) % n] << 2) | (row[i] << 1) | row[(i + 1) % n])) & 1
        for i in range(n)
    ]


def generate_ca_trace(rng, width=24, steps=2):
    """Return a trace of `steps` transitions from a random row of `width` cells."""
    if width < 3:
        raise ValueError(f"width must be at least 3, got {width}")
    if steps < 1:
        raise ValueError(f"steps must be positive, got {steps}")
    row = [int(b) for b in rng.integers(2, size=width)]
    out = [vocab.ROW] + [vocab.bit_token(b) for b in row]
    for _ in range(steps):
        row = step_rule110(row)
        out.append(vocab.NEXT)
        out.extend(vocab.bit_token(b) for b in row)
    return out


def sample_example(rng, min_width=16, max_width=32, min_steps=1, max_steps=4):
    """Return one EOS-terminated trace with sampled width and step count."""
    width = int(rng.integers(min_width, max_width + 1))
    steps = int(rng.integers(min_steps, max_steps + 1))
    return generate_ca_trace(rng, width=width, steps=steps) + [vocab.EOS]
