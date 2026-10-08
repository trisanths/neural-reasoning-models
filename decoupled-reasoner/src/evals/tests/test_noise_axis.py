import random

import pytest

from src.evals.noise_axis import (
    DEFAULT_RATES,
    build_examples,
    corrupt_examples,
    run_noise_axis,
)


def make_examples(n_episodes=4, per_episode=3, chunks_per=4):
    examples = []
    for eid in range(n_episodes):
        for j in range(per_episode):
            qid = f"q{eid}x{j}"
            answer = f"tok{eid}x{j}"
            chunks = [f"{qid} holds {answer}"]
            chunks += [f"filler ep{eid} c{k}" for k in range(chunks_per - 1)]
            examples.append({"question": qid, "answer": answer,
                             "chunks": chunks, "episode_id": eid})
    return examples


def scan_answer(question, chunks):
    for chunk in chunks:
        if chunk.startswith(question + " holds "):
            return chunk.split()[-1]
    return "unknown"


def test_corrupt_rate_zero_is_identity():
    examples = make_examples()
    out = corrupt_examples(examples, 0.0, random.Random(0))
    assert [e["chunks"] for e in out] == [e["chunks"] for e in examples]


def test_corrupt_swaps_exact_count_from_other_episodes():
    examples = make_examples()
    chunk_owner = {}
    for ex in examples:
        for c in ex["chunks"]:
            chunk_owner[c] = ex["episode_id"]
    out = corrupt_examples(examples, 0.5, random.Random(1))
    for orig, new in zip(examples, out):
        changed = [i for i in range(4) if new["chunks"][i] != orig["chunks"][i]]
        assert len(changed) == 2
        for i in changed:
            assert chunk_owner[new["chunks"][i]] != orig["episode_id"]
    assert examples[0]["chunks"][0].startswith("q0x0")


def test_corrupt_requires_other_episodes():
    solo = make_examples(n_episodes=1)
    with pytest.raises(ValueError):
        corrupt_examples(solo, 0.5, random.Random(0))
    out = corrupt_examples(solo, 0.0, random.Random(0))
    assert len(out) == len(solo)
    with pytest.raises(ValueError):
        corrupt_examples(solo, 1.5, random.Random(0))


def test_run_noise_axis_report_shape():
    examples = make_examples()
    report = run_noise_axis(scan_answer, examples, seed=11)
    assert report["suite"] == "noise_axis"
    assert report["n"] == len(examples)
    assert report["rates"] == list(DEFAULT_RATES)
    assert set(report["accuracy_per_rate"]) == {"0", "0.1", "0.25", "0.5"}
    assert report["accuracy_per_rate"]["0"] == 1.0
    assert report["clean_accuracy"] == 1.0
    for acc in report["accuracy_per_rate"].values():
        assert 0.0 <= acc <= 1.0
    assert report["degradation"] >= 0.0


def test_run_noise_axis_degrades_and_is_deterministic():
    examples = make_examples(n_episodes=6, per_episode=4)
    a = run_noise_axis(scan_answer, examples, seed=3)
    b = run_noise_axis(scan_answer, examples, seed=3)
    assert a == b
    assert a["accuracy_per_rate"]["0.5"] < 1.0
    assert a["slope"] < 0.0
    full = run_noise_axis(scan_answer, examples, rates=(0.0, 1.0), seed=3)
    assert full["accuracy_per_rate"]["1"] == 0.0
    assert full["degradation"] == 1.0
    assert full["slope"] == -1.0


def test_run_noise_axis_immune_reader_has_zero_slope():
    examples = make_examples()
    lookup = {ex["question"]: ex["answer"] for ex in examples}
    report = run_noise_axis(lambda q, c: lookup[q], examples, seed=0)
    assert all(acc == 1.0 for acc in report["accuracy_per_rate"].values())
    assert report["slope"] == 0.0
    assert report["degradation"] == 0.0


def test_run_noise_axis_input_validation():
    with pytest.raises(ValueError):
        run_noise_axis(scan_answer, [], seed=0)
    with pytest.raises(ValueError):
        run_noise_axis(scan_answer, make_examples(), rates=(), seed=0)


def test_build_examples_from_worldgen(episodes):
    examples = build_examples(episodes)
    assert examples
    n_questions = sum(len(ep["questions"]) for ep in episodes)
    assert len(examples) == n_questions
    for ex in examples:
        assert set(ex) == {"question", "answer", "chunks", "episode_id"}
        episode = episodes[ex["episode_id"]]
        assert len(ex["chunks"]) == len(episode["documents"])
    ids = {ex["episode_id"] for ex in examples}
    assert ids == set(range(len(episodes)))
