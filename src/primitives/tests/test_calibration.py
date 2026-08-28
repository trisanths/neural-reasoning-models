"""The instrument's own calibration, as executable claims.

A metric that has never been shown to move for its own faculty and to
stay still for the other six is not a measurement. These tests build
scripted stand-ins with exactly one faculty each and check the square
matrix that results: high on the diagonal, at chance off it.

They also check the two behavioural claims that no gold-reading stand-in
can establish on its own. The depth curve must track a stand-in whose
composition ability is genuinely capped at a chosen depth, and the
abstraction transfer margin must vanish for a stand-in that answers by
copying the nearest lesson case.
"""

from __future__ import annotations

import pytest

from src.primitives import PRIMITIVES, fakes, runner

N = 60
KS = (1, 2, 3)
SEED = 0


@pytest.fixture(scope="module")
def key():
    return fakes.build_answer_key(n=N, seed=SEED, mode="isolated", ks=KS,
                                 rescue_n=6)


def _profile(model):
    bundle = runner.run_suite(model, n=N, seed=SEED, mode="isolated", ks=KS,
                              keep_records=False)
    assert model.misses == 0, "the answer key missed a prompt the runner asked"
    return bundle["report"]


@pytest.fixture(scope="module")
def profiles(key):
    out = {"blind": _profile(fakes.blind_model(key, seed=7))}
    for name in PRIMITIVES:
        out[name] = _profile(fakes.faculty_model(key, name, seed=7))
    return out


SCALAR = ("intent", "gap", "acquisition", "abstraction", "memory",
          "verification")


@pytest.mark.parametrize("name", SCALAR)
def test_each_scalar_metric_responds_to_its_own_faculty(profiles, name):
    """Sensitivity: the stand-in with this faculty scores far above blind."""
    own = profiles[name][name]["headline"]
    blind = profiles["blind"][name]["headline"]
    assert own - blind > 0.30, (name, own, blind)


@pytest.mark.parametrize("name", SCALAR)
def test_each_scalar_metric_is_flat_for_the_other_faculties(profiles, name):
    """Specificity: no other faculty's stand-in moves this metric."""
    blind = profiles["blind"][name]["headline"]
    for other in PRIMITIVES:
        if other == name:
            continue
        got = profiles[other][name]["headline"]
        assert abs(got - blind) < 0.25, (name, other, got, blind)


def test_the_composition_curve_responds_to_composition_only(profiles):
    for kind in ("sequential", "relational", "novel"):
        assert profiles["composition"]["composition"][kind]["k_star"] == max(KS)
        assert profiles["blind"]["composition"][kind]["k_star"] == 0
        for other in PRIMITIVES:
            if other == "composition":
                continue
            assert profiles[other]["composition"][kind]["k_star"] == 0, \
                (kind, other)


@pytest.mark.parametrize("depth", [1, 2, 3])
def test_reported_depth_tracks_a_capped_stand_in(key, depth):
    """A stand-in that can compose to depth d and no further reports k*=d.

    This is the behavioural check the gold-reading stand-ins cannot give:
    the curve has to bend where the ability stops, not merely rise when a
    faculty is switched on.
    """
    model = fakes.depth_model(key, depth, seed=11)
    rep, _ = runner.run_composition(model, n=N, seed=SEED, mode="isolated",
                                    ks=KS)
    for kind in ("sequential", "relational", "novel"):
        assert rep[kind]["k_star"] == depth, (kind, depth, rep[kind]["curve"])


def test_capped_stand_in_keeps_its_step_probes(key):
    """The step-conditioned curve is not just the raw curve renamed.

    A depth-capped stand-in answers every single step correctly, so its
    step probe accuracy is one and its conditional curve is measured on
    the whole sample, while its raw curve still falls at the cap.
    """
    model = fakes.depth_model(key, 2, seed=11)
    rep, _ = runner.run_composition(model, n=N, seed=SEED, mode="isolated",
                                    ks=KS)
    seq = rep["sequential"]
    assert seq["step_probe_accuracy"]["acc"] == 1.0
    assert seq["items_with_all_steps_correct"]["acc"] == 1.0
    assert seq["k_star_step_clean"] == 2


def test_copying_the_nearest_lesson_case_earns_no_transfer_margin(key):
    """The abstraction contrast is against text matching, and it holds."""
    model = fakes.copy_model(key, seed=13)
    rep, _ = runner.run_abstraction(model, n=N, seed=SEED, mode="isolated")
    assert abs(rep["transfer"]["headline"]) < 1e-9
    assert not rep["transfer"]["beats_copy"]


@pytest.mark.parametrize("level", [0.0, 0.5, 1.0])
def test_a_metric_moves_monotonically_with_partial_ability(key, level):
    model = fakes.partial_model(key, "verification", level, seed=17)
    rep, _ = runner.run_verification(model, n=N, seed=SEED, mode="isolated")
    acc = rep["detection"]["acc"]
    lo, hi = {0.0: (0.30, 0.70), 0.5: (0.60, 0.90), 1.0: (0.99, 1.0)}[level]
    assert lo <= acc <= hi, (level, acc)


def test_the_rescue_matrix_locates_a_single_missing_faculty(key):
    """A stand-in missing one faculty is rescued by that faculty's oracle.

    The stand-in below has every faculty except composition. Under no
    intervention it fails the integrated episode, and the composition
    oracle is the one that brings it back, which is exactly the reading the
    matrix is built to support.
    """
    from src.primitives import episode as ep

    have = [f for f in ep.FACULTIES if f != "composition"]
    model = fakes.ScriptedModel(key, competent=have, seed=19)
    rep, _ = runner.run_rescue_matrix(model, n=6, seed=SEED)
    assert rep["baseline"]["acc"] < 0.4
    assert rep["rows"]["oracle_composition"]["accuracy"]["acc"] == 1.0
    assert rep["largest_rescue"] == "oracle_composition"
    for cond in ("oracle_intent", "oracle_gap", "oracle_memory"):
        assert rep["rows"][cond]["accuracy"]["acc"] < 0.4, cond


def test_the_forced_choice_rescue_matrix_locates_the_same_faculty(key):
    """The rescue reading survives the move to the forced-choice channel.

    The generation rescue matrix is useless for a model that writes
    nothing, which is exactly the model the channel exists for, so the
    matrix has to work there too.
    """
    from src.primitives import episode as ep

    pairs = runner.collect_choices(primitives=["memory"], n=2, seed=SEED,
                                   ks=(1,), rescue_n=6)
    have = [f for f in ep.FACULTIES if f != "composition"]
    model = fakes.ChoosingModel(key, competent=have, seed=23)
    model.learn_choices(pairs)
    rep = runner.run_forced_choice(model, primitives=["memory"], n=2,
                                   seed=SEED, ks=(1,), rescue_n=6)
    m = rep["rescue_matrix"]
    assert m["baseline"]["acc"] < 0.4
    assert m["rows"]["oracle_composition"]["accuracy"]["acc"] == 1.0
    assert m["largest_rescue"] == "oracle_composition"


def test_a_silent_model_scores_zero_and_not_chance(key):
    """Saying nothing is not the same as guessing, and must not look like it.

    A model that emits nothing expresses no verdict, so it is scored as
    wrong everywhere rather than credited with the chance rate. The parse
    rate goes to zero at the same time, which is what the report's format
    warning keys off.
    """
    silent = lambda q, c=None: ""
    rep, _ = runner.run_verification(silent, n=20, seed=SEED)
    assert rep["detection"]["acc"] == 0.0
    assert rep["parse_rate"]["acc"] == 0.0
    g, _ = runner.run_gap(silent, n=20, seed=SEED)
    assert g["detection"]["acc"] == 0.0


def test_a_model_that_always_says_no_shows_a_false_alarm_rate_of_one(key):
    """The generous reading must not hand a degenerate reply a faculty.

    Answering "no" to everything is read as claiming a gap and as failing
    the candidate, which is exactly half right by construction, and the
    false-alarm rate is one. Both are visible; neither looks like skill.
    """
    always_no = lambda q, c=None: "no"
    g, _ = runner.run_gap(always_no, n=40, seed=SEED)
    assert abs(g["detection"]["acc"] - 0.5) < 1e-9
    assert g["false_alarm"]["acc"] == 1.0
    assert not g["detection"]["above_chance"]
    v, _ = runner.run_verification(always_no, n=40, seed=SEED)
    assert abs(v["detection"]["acc"] - 0.5) < 1e-9
    assert v["false_alarm"]["acc"] == 1.0


def test_naming_every_candidate_is_not_an_answer(key):
    """A reply that lists all the options counts as no choice at all."""
    from src.primitives import p5_composition as C

    items = C.generate_curve(10, "sequential", [2], seed=SEED)
    listy = [C.grade(i, ", ".join(i.gold["labels"])) for i in items]
    assert sum(g["correct"] for g in listy) == 0.0
    assert not any(g["parsed"] for g in listy)


def test_the_forced_choice_channel_tracks_the_same_faculties(key):
    """Preferring the right reading is measured, and stays specific.

    The channel exists so a checkpoint that cannot write a menu label is
    still asked which reading it prefers. It has to respond to the same
    faculty as the generation channel and to no other, or it is a second
    measurement of something else.
    """
    pairs = runner.collect_choices(n=12, seed=SEED, mode="isolated",
                                   ks=(1, 2), rescue_n=0)
    for target in ("gap", "memory", "verification"):
        model = fakes.ChoosingModel(key, competent=[target], seed=5)
        model.learn_choices(pairs)
        rep = runner.run_forced_choice(model, n=12, seed=SEED,
                                       mode="isolated", ks=(1, 2))
        assert model.misses == 0
        own = [s["acc"] for s in rep[target].values()]
        assert min(own) == 1.0, (target, rep[target])
        for other in ("gap", "memory", "verification"):
            if other == target:
                continue
            for stat in rep[other].values():
                # A margin rather than a bare interval test: at these sample
                # sizes a ninety-five percent interval clears chance on one
                # cell in forty by luck, and the claim being made is that the
                # metric does not move, not that it never wobbles.
                assert stat["adjusted_ci_lo"] <= 0.25, (target, other, stat)


def test_the_forced_choice_channel_has_a_working_depth_curve(key):
    pairs = runner.collect_choices(primitives=["composition"], n=12, seed=SEED,
                                   mode="isolated", ks=(1, 2, 3))
    model = fakes.ChoosingModel(key, competent=["composition"], seed=5,
                                max_depth=2)
    model.learn_choices(pairs)
    rep = runner.run_forced_choice(model, primitives=["composition"], n=12,
                                   seed=SEED, mode="isolated", ks=(1, 2, 3))
    comp = rep["composition"]
    assert comp["sequential/k1"]["acc"] == 1.0
    assert comp["sequential/k2"]["acc"] == 1.0
    assert not comp["sequential/k3"]["above_chance"]


def test_integrated_mode_runs_every_primitive(key):
    """Both modes have to work at every size for the substrate sweep."""
    k2 = fakes.build_answer_key(n=6, seed=1, mode="integrated", ks=(1, 2),
                                rescue_n=0)
    model = fakes.oracle_model(k2, seed=3)
    bundle = runner.run_suite(model, n=6, seed=1, mode="integrated", ks=(1, 2),
                              keep_records=False)
    assert model.misses == 0
    for name in PRIMITIVES:
        assert name in bundle["report"]
    assert bundle["report"]["meta"]["mode"] == "integrated"
