"""Tests for the sequential-composition task."""

import sys
from collections import Counter

sys.path.insert(0, ".")
from src.compose import MOD, ComposeGenerator, ComposeTokenizer  # noqa: E402
from src.dataset import CurriculumConfig, build_batch  # noqa: E402

GEN = ComposeGenerator(n_steps=6, seed=7)
EXAMPLES = GEN.generate(3000)


def _recompute(ex) -> int:
    """Independently re-evaluates the arithmetic chain from the question text."""
    w = ex.question.split()
    val = int(w[1])
    i = 2
    while i < len(w) and w[i] == "then":
        op, operand = w[i + 1], int(w[i + 2])
        val = (val + operand) % MOD if op == "add" else (val * operand) % MOD
        i += 3
    return val


def test_answers_are_arithmetically_correct():
    for ex in EXAMPLES[:500]:
        assert _recompute(ex) == ex.meta["final"]
        assert ex.answer == f"= {ex.meta['final']} ."


def test_steps_are_the_running_intermediate_values():
    """Each curriculum step must be the value after that many operations."""
    for ex in EXAMPLES[:200]:
        w = ex.question.split()
        val = int(w[1])
        assert ex.steps[0] == f"= {val} ."
        i, s = 2, 1
        while i < len(w) and w[i] == "then":
            op, operand = w[i + 1], int(w[i + 2])
            val = (val + operand) % MOD if op == "add" else (val * operand) % MOD
            assert ex.steps[s] == f"= {val} ."
            i += 3
            s += 1
        assert s == len(ex.steps)


def test_answer_distribution_is_near_uniform():
    """Every operation is a bijection on Z_10, so no constant predictor should
    do much better than chance."""
    c = Counter(ex.meta["final"] for ex in EXAMPLES)
    majority = max(c.values()) / len(EXAMPLES)
    assert majority < 0.15, f"majority-class baseline {majority:.3f} is too high"


def test_requires_all_steps():
    """Truncating the chain early must change the answer most of the time,
    so the task cannot be solved by reading only the tail."""
    changed = 0
    for ex in EXAMPLES[:500]:
        w = ex.question.split()
        # Drop the first operation and recompute.
        val = int(w[1])
        i = 5  # skip 'start d' and the first 'then op d'
        while i < len(w) and w[i] == "then":
            op, operand = w[i + 1], int(w[i + 2])
            val = (val + operand) % MOD if op == "add" else (val * operand) % MOD
            i += 3
        if val != ex.meta["final"]:
            changed += 1
    assert changed / 500 > 0.7, "early operations barely affect the answer"


def test_batch_builds_and_tokenizes():
    tok = ComposeTokenizer()
    cfg = CurriculumConfig(max_latent_stage=6, c_thought=1)
    b = build_batch(EXAMPLES[:4], tok, stage=99, cfg=cfg)
    assert b.n_latent == 6
    supervised = b.labels[0][b.labels[0] != -100]
    assert tok.decode(supervised.tolist()).startswith("=")
    for ex in EXAMPLES[:50]:
        assert tok.decode(tok.encode(ex.question)) == ex.question


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"PASS {name}")
