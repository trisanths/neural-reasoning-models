from src.evals.probes import PROBES, leakage_threshold, run_probes


def test_probes_well_formed():
    assert len(PROBES) >= 30
    for probe in PROBES:
        assert len(probe["options"]) == 4
        assert len(set(probe["options"])) == 4
        assert 0 <= probe["answer_idx"] < 4
        assert probe["text"].strip()


def test_leakage_threshold_reasonable():
    thr = leakage_threshold(40)
    assert 0.25 < thr < 0.5
    assert leakage_threshold(1000) < thr


def test_run_probes_structure(tok, tiny_model):
    out = run_probes(tiny_model, tok, "cpu")
    assert out["n"] == len(PROBES)
    assert 0.0 <= out["accuracy"] <= 1.0
    assert out["chance"] == 0.25
    assert isinstance(out["leakage_flag"], bool)
    assert len(out["results"]) == out["n"]


def test_run_probes_deterministic(tok, tiny_model):
    a = run_probes(tiny_model, tok, "cpu")
    b = run_probes(tiny_model, tok, "cpu")
    assert a["accuracy"] == b["accuracy"]
    assert [r["picked"] for r in a["results"]] == [r["picked"] for r in b["results"]]
