"""Task integrity tests.

A reasoning benchmark is only meaningful if it cannot be solved without
reasoning. During development a mention-frequency heuristic scored 69% on this
task because the reachable target appeared in more statements than the
unreachable distractor; these tests keep that class of shortcut closed.
"""

import sys
from collections import Counter

sys.path.insert(0, ".")
from src.data import ProsQAGenerator, Tokenizer, dedup_split  # noqa: E402

GEN = ProsQAGenerator(n_layers=6, width=4, n_hops=4, extra_edges=10, seed=123)
EXAMPLES = GEN.generate(800)


def test_answer_is_reachable_and_distractor_is_not():
    """The gold answer must follow from the stated edges; the distractor must not."""
    for ex in EXAMPLES[:200]:
        edges = set()
        root = None
        for stmt in ex.question.split(" . "):
            w = stmt.split()
            if len(w) >= 5 and w[0] == "every":
                edges.add((w[1], w[4]))
            elif len(w) >= 4 and w[1] == "is":
                root = w[3]
        assert root is not None
        seen, queue = {root}, [root]
        while queue:
            node = queue.pop()
            for s, d in edges:
                if s == node and d not in seen:
                    seen.add(d)
                    queue.append(d)
        assert ex.meta["target"] in seen, "gold answer is not reachable"
        assert ex.meta["distractor"] not in seen, "distractor is reachable"


def test_no_mention_frequency_shortcut():
    """Counting how often each candidate appears must carry no signal."""
    wins = 0
    for ex in EXAMPLES:
        c = Counter(ex.question.split())
        if c[ex.meta["target"]] > c[ex.meta["distractor"]]:
            wins += 1
    assert wins == 0, f"frequency heuristic wins on {wins}/{len(EXAMPLES)} examples"


def test_no_position_shortcut():
    """The correct answer must appear first about half the time."""
    first = sum(1 for ex in EXAMPLES if ex.question.split()[-4] == ex.meta["target"])
    rate = first / len(EXAMPLES)
    assert 0.42 < rate < 0.58, f"answer is first {rate:.3f} of the time"


def test_requires_multiple_hops():
    """No example may be answerable by a single edge from the root."""
    for ex in EXAMPLES[:200]:
        root = ex.steps[0].split()[-2]
        assert f"every {root} is a {ex.meta['target']} ." not in ex.question
        assert len(ex.steps) == ex.n_hops + 1


def test_splits_do_not_overlap():
    train, val, test = dedup_split(EXAMPLES, n_val=50, n_test=50)
    qs = [set(e.question for e in s) for s in (train, val, test)]
    assert not (qs[0] & qs[1]) and not (qs[0] & qs[2]) and not (qs[1] & qs[2])


def test_tokenizer_roundtrip():
    tok = Tokenizer()
    for ex in EXAMPLES[:50]:
        assert tok.decode(tok.encode(ex.question)) == ex.question
        assert tok.decode(tok.encode(ex.answer)) == ex.answer


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"PASS {name}")
