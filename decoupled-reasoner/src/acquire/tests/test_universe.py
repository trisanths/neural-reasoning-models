"""The universe has to be trustworthy before anything measured on it counts."""

import re

import pytest

from src.acquire.universe import build_chapter, build_universe, prove


@pytest.fixture(scope="module")
def uni():
    return build_universe(seed=11, n_chapters=3, n_per_level=4)


def test_every_problem_carries_a_passing_proof(uni):
    problems = uni.problems()
    assert problems
    for p in problems:
        assert p.proof["ok"], (p.qid, p.proof["checks"])
        assert p.proof["checks"]["ablation"]
        assert p.proof["checks"]["isolation"]
        assert p.proof["checks"]["not_copyable"]
        assert p.proof["checks"]["choices"]


def test_all_three_levels_are_present(uni):
    levels = {p.level for p in uni.problems()}
    assert levels == {0, 1, 2}


def test_answer_never_appears_in_its_own_question(uni):
    for p in uni.problems():
        assert not re.search(rf"(?<![\w.]){re.escape(p.answer)}(?![\w.])", p.text)


def test_withholding_any_required_definition_undetermines_the_answer(uni):
    for ch in uni.chapters:
        for p in ch.problems:
            everything = set(ch.notions)
            value, _ = ch.evaluate(p.notion, p.case, known=everything)
            assert value == p.answer
            for withheld in p.required_notions:
                out, _ = ch.evaluate(p.notion, p.case,
                                     known=everything - {withheld})
                assert out is None, (p.qid, withheld)


def test_required_notions_grow_with_level(uni):
    by_level = {}
    for p in uni.problems():
        by_level.setdefault(p.level, []).append(len(p.required_notions))
    assert min(by_level[0]) == 1
    assert min(by_level[1]) >= 2
    assert min(by_level[2]) >= 3


def test_level_two_reaches_the_full_chain(uni):
    depths = [len(p.required_notions) for p in uni.problems() if p.level == 2]
    assert max(depths) >= 4


def test_theory_graph_matches_the_notions(uni):
    for ch in uni.chapters:
        g = ch.theory_graph()
        names = {n["notion"] for n in g["nodes"]}
        assert len(names) == 6
        for e in g["edges"]:
            assert e["prerequisite"] in names
            assert e["notion"] in names
        assert g["top"] in names
        assert ch.notions[g["top"]].level == 2


def test_invented_words_are_unique_across_the_universe(uni):
    words = []
    for ch in uni.chapters:
        words.extend(ch.attr_words.values())
        words.extend(ch.type_words)
        for n in ch.notions.values():
            words.append(n.name)
            words.extend(n.outputs)
    assert len(words) == len(set(words))


def test_pages_carry_the_kinds_lesson_ranking_needs(uni):
    kinds = {p.kind for p in uni.pages}
    assert {"preamble", "definition", "worked_example", "statement"} <= kinds
    for ch in uni.chapters:
        for name in ch.notions:
            assert ch.definition_page(name).kind == "definition"


def test_regenerating_from_the_seed_reproduces_the_chapter():
    a = build_chapter(4242, set())
    b = build_chapter(4242, set())
    assert [p.text for p in a.pages] == [p.text for p in b.pages]


def test_a_deliberately_leaky_problem_is_rejected(uni):
    """The proof is a real check, not a rubber stamp: hand prove() a page that
    states the answer outright and isolation must fail."""
    ch = uni.chapters[0]
    p = [q for q in ch.problems if q.level == 0][0]
    from src.acquire.universe import Page
    leaky = Page(page_id="leak/1", chapter="other", notion=None, level=0,
                 kind="statement", title="A leak.",
                 body=f"The answer to everything is {p.answer}.")
    out = prove(ch, p, list(uni.pages) + [leaky])
    assert not out["ok"]
    assert out["leaks"] == ["leak/1"]
