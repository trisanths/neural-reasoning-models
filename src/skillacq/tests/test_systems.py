import json
import random
import tempfile

from src.skillacq.systems import (FAMILIES, _answer_is_copyable, generate_episode,
                                  system_overlap, verify_episode)
from src.skillacq.episodes import to_rl_episode, write_jsonl


def test_every_family_generates_and_verifies():
    for i, fam in enumerate(sorted(FAMILIES)):
        ep = generate_episode(1000 + i, family=fam)
        assert ep.family == fam
        assert ep.textbook and ep.problems
        assert verify_episode(ep)


def test_determinism_by_seed():
    a = generate_episode(7)
    b = generate_episode(7)
    assert a.textbook == b.textbook
    assert [p["answer"] for p in a.problems] == [p["answer"] for p in b.problems]


def test_systems_are_novel_across_seeds():
    overlaps = [system_overlap(s, s + 1) for s in range(50, 70)]
    assert max(overlaps) < 0.34


def test_answers_are_never_copyable_from_the_question():
    for s in range(200, 260):
        for p in generate_episode(s).problems:
            assert not _answer_is_copyable(p["answer"], p["text"])


def test_answers_require_the_textbook():
    """A generic reader without the rules cannot guess the numeric answers."""
    rng = random.Random(0)
    correct = 0
    total = 0
    for s in range(300, 340):
        ep = generate_episode(s)
        for p in ep.problems:
            if p["kind"] in {"decide"}:
                continue
            total += 1
            guess = str(rng.randint(0, 200))
            if guess == p["answer"]:
                correct += 1
    assert total > 0
    assert correct / total < 0.1


def test_rl_episode_shape_matches_env_expectations():
    ep = generate_episode(11)
    rec = to_rl_episode(ep)
    assert set(rec) >= {"documents", "questions", "world", "n_context"}
    assert all("text" in d for d in rec["documents"])
    q = rec["questions"][0]
    assert set(q) >= {"qid", "text", "answer", "plan"}
    assert rec["world"]["domain"].startswith("skill_")


def test_write_jsonl_roundtrip():
    with tempfile.NamedTemporaryFile("w+", suffix=".jsonl", delete=False) as fh:
        path = fh.name
    stats = write_jsonl(path, range(400, 410), n_problems=4)
    assert stats["episodes"] == 10
    assert stats["questions"] == 40
    with open(path) as fh:
        rows = [json.loads(line) for line in fh]
    assert len(rows) == 10
    assert all(r["questions"] for r in rows)


def test_retrieval_presentation_hides_pages_from_context():
    rec = to_rl_episode(generate_episode(12), n_context=0)
    assert rec["n_context"] == 0
    assert len(rec["documents"]) >= 3
