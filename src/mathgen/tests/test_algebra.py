import itertools

import pytest

from src.mathgen import algebra


SEEDS = list(range(24))


def test_determinism_by_seed():
    for seed in SEEDS[:8]:
        a = algebra.sample_structure(seed)
        b = algebra.sample_structure(seed)
        assert a.as_dict() == b.as_dict()


def test_signature_is_well_formed():
    for seed in SEEDS:
        s = algebra.sample_structure(seed)
        assert 3 <= s.size <= 8
        assert len(set(s.elements)) == s.size
        assert 1 <= len(s.op_glyphs) <= 2
        assert len(s.op_glyphs) == len(s.tables) == len(s.op_names)
        assert len(set(s.op_glyphs)) == len(s.op_glyphs)
        assert s.rel_glyph not in s.op_glyphs
        assert s.object_name and s.system_name


def test_tables_are_closed():
    for seed in SEEDS:
        s = algebra.sample_structure(seed)
        for k in range(len(s.tables)):
            assert len(s.tables[k]) == s.size
            for row in s.tables[k]:
                assert len(row) == s.size
                assert all(0 <= v < s.size for v in row)


def test_axiom_profile_matches_exhaustive_truth():
    """Every declared axiom really holds and every refuted one really fails."""
    lookup = dict(algebra.AXIOM_MENU)
    for seed in SEEDS:
        s = algebra.sample_structure(seed)
        profile = algebra.axiom_profile(s)
        assert profile["holds"], "a system with no axioms at all is a bug"
        for name in profile["holds"]:
            assert lookup[name](s)[0] is True
        for name in profile["fails"]:
            assert lookup[name](s)[0] is False


def test_consistency_report_passes_for_every_sampled_system():
    for seed in range(60):
        s = algebra.sample_structure(seed)
        report = algebra.consistency_report(s, algebra.axiom_profile(s))
        assert report["ok"], report["problems"]


def test_consistency_report_catches_a_planted_contradiction():
    s = algebra.sample_structure(1)
    profile = algebra.axiom_profile(s)
    broken = {"holds": dict(profile["holds"]), "fails": dict(profile["fails"])}
    # Claim an axiom holds that the model refutes, or one already refuted.
    name = next(iter(profile["fails"]))
    broken["holds"][name] = None
    report = algebra.consistency_report(s, broken)
    assert not report["ok"]
    assert any(name in p for p in report["problems"])


def test_associativity_witness_is_a_real_counterexample():
    for seed in SEEDS:
        s = algebra.sample_structure(seed)
        ok, witness = algebra.check_associative(s, 0)
        if ok:
            continue
        i = s.index[witness["x"]]
        j = s.index[witness["y"]]
        m = s.index[witness["z"]]
        assert s.op(0, s.op(0, i, j), m) != s.op(0, i, s.op(0, j, m))
        assert s.name(s.op(0, s.op(0, i, j), m)) == witness["left"]


def test_identity_and_inverses_agree_with_the_tables():
    for seed in SEEDS:
        s = algebra.sample_structure(seed)
        e = s.identity_of(0)
        if e is None:
            continue
        for x in range(s.size):
            assert s.op(0, e, x) == x and s.op(0, x, e) == x
            inv = s.inverse_of(x, 0)
            if inv is not None:
                assert s.op(0, x, inv) == e and s.op(0, inv, x) == e


def test_evaluation_respects_stated_precedence_and_association():
    for seed in SEEDS:
        s = algebra.sample_structure(seed)
        a, b, c = s.elements[0], s.elements[1], s.elements[2]
        g0 = s.op_glyphs[0]
        # The first operation associates to the left.
        flat = s.evaluate(f"{a} {g0} {b} {g0} {c}")
        left = s.evaluate(f"({a} {g0} {b}) {g0} {c}")
        assert flat == left
        if s.has_two_ops:
            g1 = s.op_glyphs[1]
            # The second operation binds tighter than the first.
            mixed = s.evaluate(f"{a} {g0} {b} {g1} {c}")
            explicit = s.evaluate(f"{a} {g0} ({b} {g1} {c})")
            assert mixed == explicit


def test_evaluation_agrees_with_the_raw_tables():
    for seed in SEEDS:
        s = algebra.sample_structure(seed)
        g0 = s.op_glyphs[0]
        for i, j in itertools.product(range(s.size), repeat=2):
            got = s.evaluate(f"{s.elements[i]} {g0} {s.elements[j]}")
            assert got == s.name(s.op(0, i, j))


def test_powers_and_inverse_notation():
    for seed in SEEDS:
        s = algebra.sample_structure(seed)
        x = s.elements[1]
        g0 = s.op_glyphs[0]
        assert s.evaluate(f"{x}^3") == s.evaluate(f"({x} {g0} {x}) {g0} {x}")
        if s.has_inverses:
            e = s.name(s.identity_of(0))
            assert s.evaluate(f"{x} {g0} {x}'") == e


def test_parse_errors_are_raised_not_silently_wrong():
    s = algebra.sample_structure(2)
    g0 = s.op_glyphs[0]
    with pytest.raises(algebra.ParseError):
        s.evaluate("notanelement " + g0 + " " + s.elements[0])
    with pytest.raises(algebra.ParseError):
        s.evaluate(f"{s.elements[0]} {g0}")
    with pytest.raises(algebra.ParseError):
        s.evaluate(f"({s.elements[0]} {g0} {s.elements[1]}")


def test_relation_is_decidable_on_every_pair():
    for seed in SEEDS:
        s = algebra.sample_structure(seed)
        for i, j in itertools.product(range(s.size), repeat=2):
            assert isinstance(s.decide(i, j), bool)
            written = f"{s.elements[i]} {s.rel_glyph} {s.elements[j]}"
            assert s.decide_written(written) == s.decide(i, j)


def test_sibling_keeps_the_surface_and_changes_the_content():
    for seed in SEEDS:
        s = algebra.sample_structure(seed)
        sib = s.sibling(1)
        assert sib.elements == s.elements
        assert sib.op_glyphs == s.op_glyphs
        assert sib.rel_glyph == s.rel_glyph
        assert sib.tables[0] != s.tables[0]
        assert sib.size == s.size


def test_siblings_are_themselves_consistent_systems():
    for seed in SEEDS[:12]:
        sib = algebra.sample_structure(seed).sibling(2)
        report = algebra.consistency_report(sib, algebra.axiom_profile(sib))
        assert report["ok"], report["problems"]


def test_the_menu_covers_both_operations_when_two_are_present():
    seen_two_ops = False
    for seed in range(40):
        s = algebra.sample_structure(seed)
        if not s.has_two_ops:
            continue
        seen_two_ops = True
        profile = algebra.axiom_profile(s)
        both = set(profile["holds"]) | set(profile["fails"])
        assert "associativity_second" in both
        assert "distributivity" in both
    assert seen_two_ops


def test_single_operation_systems_do_not_report_second_operation_axioms():
    for seed in range(40):
        s = algebra.sample_structure(seed)
        if s.has_two_ops:
            continue
        profile = algebra.axiom_profile(s)
        both = set(profile["holds"]) | set(profile["fails"])
        assert not (both & algebra._SECOND_OP_AXIOMS)
