import copy

from src.mathgen import exercises, textbook, theory, verify

SEEDS = list(range(10))


def _universe(seed):
    th = theory.build(seed)
    exs = exercises.build_exercises(th)
    book = textbook.build_textbook(th, exs)
    return th, exs, book


def test_every_universe_verifies_clean():
    for seed in SEEDS:
        th, exs, book = _universe(seed)
        report = verify.verify_universe(th, exs, book)
        assert report["all_passed"], [c for c in report["checks"] if c["failed"]]
        assert report["pass_rate"] == 1.0


def test_verification_actually_checks_a_lot():
    th, exs, book = _universe(3)
    report = verify.verify_universe(th, exs, book)
    assert report["assertions_checked"] > 300
    names = {c["name"] for c in report["checks"]}
    assert names == {"axiom_consistency", "axioms", "definition_extensions",
                     "theorems_and_refutations", "dependency_graph",
                     "worked_examples", "exercise_answers", "exercise_necessity",
                     "answer_source_labels"}
    for check in report["checks"]:
        assert check["total"] > 0, f"{check['name']} checked nothing"


def test_a_corrupted_theorem_is_caught():
    th, _exs, _book = _universe(3)
    node = next(th.nodes[n] for n in th.order if th.nodes[n].kind == "theorem")
    node.kind = "refutation"
    check = verify.verify_theorems(th)
    assert check.failed > 0


def test_a_corrupted_definition_extension_is_caught():
    th, _exs, _book = _universe(4)
    node = next(th.nodes[n] for n in th.order
                if th.nodes[n].kind == "definition"
                and "extension" in th.nodes[n].payload)
    node.payload["extension"] = ["not-an-object"]
    assert verify.verify_definitions(th).failed > 0


def test_a_corrupted_worked_example_is_caught():
    th, exs, book = _universe(5)
    book.chapters[0].worked_examples[0]["value"] = "wrong"
    assert verify.verify_worked_examples(book).failed > 0


def test_a_corrupted_exercise_answer_is_caught():
    th, exs, _book = _universe(6)
    broken = copy.deepcopy(exs)
    broken[0].answer = "definitely-wrong"
    assert verify.verify_exercises(th, broken).failed > 0


def test_a_forward_citation_is_caught():
    th, _exs, _book = _universe(7)
    last = th.nodes[th.order[-1]]
    first = th.nodes[th.order[0]]
    first.depends_on = [last.node_id]
    assert verify.verify_graph(th).failed > 0


def test_an_inconsistent_axiom_declaration_is_caught():
    th, _exs, _book = _universe(8)
    name = next(iter(th.profile["fails"]))
    th.profile["holds"][name] = None
    assert verify.verify_consistency(th).failed > 0


def test_novelty_audit_reports_near_zero_symbol_overlap():
    for a, b in [(1, 2), (3, 4), (5, 6), (7, 8)]:
        audit = verify.novelty_audit(a, b)
        assert audit["symbol_overlap"] <= 0.10, audit["shared_symbols"]
        assert 0.0 <= audit["phrase_overlap"] <= 1.0
        assert audit["ngram_size"] == 5


def test_answers_do_not_transfer_between_universes():
    """The cross universe number that would let a model cheat stays near zero."""
    for a, b in [(1, 2), (3, 4), (5, 6)]:
        audit = verify.novelty_audit(a, b)
        assert audit["answers_overlap"] <= 0.10


def test_a_universe_has_no_symbol_overlap_with_itself_removed():
    audit = verify.novelty_audit(2, 2)
    assert audit["symbol_overlap"] == 1.0
    assert audit["answers_overlap"] == 1.0


def test_novelty_sweep_covers_every_pair():
    sweep = verify.novelty_sweep([1, 2, 3, 4])
    assert sweep["pairs"] == 6
    assert sweep["symbol_overlap"]["max"] <= 0.15
    assert sweep["answers_overlap"]["max"] <= 0.15
    for key in ("symbol_overlap", "phrase_overlap", "vocabulary_overlap"):
        assert sweep[key]["min"] <= sweep[key]["mean"] <= sweep[key]["max"]


def test_a_mislabelled_answer_source_is_caught():
    th, exs, book = _universe(9)
    derived = next(e for e in exs
                   if e.answer_source == "derived_by_computation")
    derived.answer_source = "stated_in_a_chapter"
    assert verify.verify_answer_sources(th, exs, book).failed > 0
