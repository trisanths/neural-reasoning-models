"""k-Dyck and k-Shuffle-Dyck word generators.

A k-Dyck word is a well-nested bracket sequence over k bracket types, so a
close must match the most recent unmatched open. A k-Shuffle-Dyck word only
requires each bracket type to be balanced on its own, with every prefix
having at least as many opens as closes per type; nesting across types is
unconstrained.
"""

from src.procgen import vocab

DEFAULT_KS = (4, 8, 16)

VOCAB_RANGES = [list(vocab.BRACKET_RANGE), [vocab.EOS, vocab.EOS + 1]]


def _check_args(k, length):
    if not 1 <= k <= vocab.MAX_K:
        raise ValueError(f"k must be in 1..{vocab.MAX_K}, got {k}")
    if length < 2 or length % 2 != 0:
        raise ValueError(f"length must be even and at least 2, got {length}")


def generate_dyck(rng, k=8, length=64):
    """Return a k-Dyck word of exactly `length` bracket tokens."""
    _check_args(k, length)
    stack = []
    out = []
    for pos in range(length):
        remaining = length - pos
        can_open = remaining >= len(stack) + 2
        can_close = len(stack) > 0
        if can_open and (not can_close or rng.random() < 0.5):
            t = int(rng.integers(k))
            stack.append(t)
            out.append(vocab.open_token(t))
        else:
            out.append(vocab.close_token(stack.pop()))
    return out


def generate_shuffle_dyck(rng, k=8, length=64):
    """Return a k-Shuffle-Dyck word of exactly `length` bracket tokens."""
    _check_args(k, length)
    depths = [0] * k
    total = 0
    out = []
    for pos in range(length):
        remaining = length - pos
        can_open = remaining >= total + 2
        can_close = total > 0
        if can_open and (not can_close or rng.random() < 0.5):
            t = int(rng.integers(k))
            depths[t] += 1
            total += 1
            out.append(vocab.open_token(t))
        else:
            open_types = [i for i in range(k) if depths[i] > 0]
            t = open_types[int(rng.integers(len(open_types)))]
            depths[t] -= 1
            total -= 1
            out.append(vocab.close_token(t))
    return out


def _sample_params(rng, ks, min_pairs, max_pairs):
    k = int(ks[int(rng.integers(len(ks)))])
    length = 2 * int(rng.integers(min_pairs, max_pairs + 1))
    return k, length


def sample_dyck_example(rng, ks=DEFAULT_KS, min_pairs=8, max_pairs=64):
    """Return one EOS-terminated k-Dyck example with sampled k and length."""
    k, length = _sample_params(rng, ks, min_pairs, max_pairs)
    return generate_dyck(rng, k=k, length=length) + [vocab.EOS]


def sample_shuffle_dyck_example(rng, ks=DEFAULT_KS, min_pairs=8, max_pairs=64):
    """Return one EOS-terminated k-Shuffle-Dyck example with sampled k and length."""
    k, length = _sample_params(rng, ks, min_pairs, max_pairs)
    return generate_shuffle_dyck(rng, k=k, length=length) + [vocab.EOS]
