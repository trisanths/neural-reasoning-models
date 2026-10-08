import difflib

import pytest

from src.evals.naturalized import (
    REGISTERS,
    SUITE_VERSION,
    WRAP_STYLES,
    contains_answer,
    evaluate,
    exact_match,
    inject_contradiction,
    load_suite,
    normalize,
    ocr_noise,
    rhetorical_wrap,
)


@pytest.fixture(scope="module")
def suite():
    return load_suite()


def test_suite_metadata(suite):
    meta = suite["metadata"]
    assert meta["version"] == SUITE_VERSION == "DRAFT-1"
    assert meta["n_items"] == len(suite["items"]) >= 250
    assert set(meta["per_register"]) == set(REGISTERS)
    assert sum(meta["per_register"].values()) == meta["n_items"]
    for register in REGISTERS:
        assert meta["per_register"][register] >= 40


def test_items_well_formed(suite):
    seen = set()
    for item in suite["items"]:
        assert item["id"] not in seen
        seen.add(item["id"])
        assert item["register"] in REGISTERS
        words = len(item["passage"].split())
        assert 150 <= words <= 400, item["id"]
        assert item["question"].strip()
        assert item["answer"].strip()
        assert len(normalize(item["answer"]).split()) <= 6, item["id"]


def test_answers_and_distractors_in_passage(suite):
    for item in suite["items"]:
        assert contains_answer(item["passage"], item["answer"]), item["id"]
        assert item["distractors"], item["id"]
        for d in item["distractors"]:
            assert contains_answer(item["passage"], d), item["id"]
            assert normalize(d) != normalize(item["answer"]), item["id"]


def test_normalize_and_scoring():
    assert normalize("The  Blue-Door!") == "blue door"
    assert exact_match("The Annex.", "annex")
    assert not exact_match("annexes", "annex")
    assert contains_answer("we chose the blue door today", "Blue Door")
    assert not contains_answer("the bluesy doors", "blue door")
    assert not contains_answer("anything", "")


def test_ocr_noise_deterministic():
    text = "The quick brown fox jumps over 12 lazy dogs." * 20
    a = ocr_noise(text, 0.2, seed=7)
    b = ocr_noise(text, 0.2, seed=7)
    c = ocr_noise(text, 0.2, seed=8)
    assert a == b
    assert a != c
    assert ocr_noise(text, 0.0, seed=7) == text
    with pytest.raises(ValueError):
        ocr_noise(text, 1.5, seed=0)


def test_ocr_noise_scales_with_rate():
    text = "Reading comprehension survives light noise better than heavy." * 30
    light = ocr_noise(text, 0.05, seed=3)
    heavy = ocr_noise(text, 0.4, seed=3)
    sim_light = difflib.SequenceMatcher(None, text, light, autojunk=False).ratio()
    sim_heavy = difflib.SequenceMatcher(None, text, heavy, autojunk=False).ratio()
    assert sim_light > sim_heavy


def test_inject_contradiction(suite):
    items = suite["items"][:20]
    untouched = inject_contradiction(items, 0.0, seed=1)
    assert all(not it["contradicted"] for it in untouched)
    assert [it["passage"] for it in untouched] == [it["passage"] for it in items]

    hit = inject_contradiction(items, 1.0, seed=1)
    again = inject_contradiction(items, 1.0, seed=1)
    assert [it["passage"] for it in hit] == [it["passage"] for it in again]
    for orig, new in zip(items, hit):
        assert new["contradicted"]
        assert new["passage"].startswith(orig["passage"])
        assert len(new["passage"]) > len(orig["passage"])
        assert new["answer"] == orig["answer"]
        assert "contradicted" not in orig
    with pytest.raises(ValueError):
        inject_contradiction(items, -0.1, seed=1)


def test_rhetorical_wrap():
    text = "The committee approved the budget on Tuesday."
    for style in WRAP_STYLES:
        wrapped = rhetorical_wrap(text, style, seed=5)
        assert text in wrapped
        assert len(wrapped) > len(text)
        assert wrapped == rhetorical_wrap(text, style, seed=5)
    a = rhetorical_wrap(text, "persuasive", seed=5)
    b = rhetorical_wrap(text, "dismissive", seed=5)
    assert a != b
    with pytest.raises(ValueError):
        rhetorical_wrap(text, "sarcastic", seed=5)


def test_evaluate_oracle_and_junk(suite):
    items = suite["items"][:30]
    answers = {(it["passage"], it["question"]): it["answer"] for it in items}

    def oracle(passage, question):
        return answers[(passage, question)]

    report = evaluate(items, oracle)
    assert report["suite"] == "naturalized_reading"
    assert report["version"] == SUITE_VERSION
    assert report["n"] == 30
    assert report["em"] == 1.0
    assert report["contains"] == 1.0
    for stats in report["per_register"].values():
        assert stats["em"] == 1.0

    junk = evaluate(items, lambda p, q: "xyzzy plugh")
    assert junk["em"] == 0.0
    assert junk["contains"] == 0.0
    with pytest.raises(ValueError):
        evaluate([], oracle)


def test_wrapped_and_noised_items_still_scoreable(suite):
    item = suite["items"][0]
    wrapped = rhetorical_wrap(item["passage"], "academic", seed=2)
    assert contains_answer(wrapped, item["answer"])
    noised = ocr_noise(item["passage"], 0.02, seed=2)
    assert len(noised) > 0
