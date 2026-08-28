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
