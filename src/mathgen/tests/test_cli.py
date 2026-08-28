import json
import os

import pytest

from src.mathgen import cli


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def test_parse_seeds_accepts_the_three_forms():
    assert cli.parse_seeds("7") == [7]
    assert cli.parse_seeds("0-4") == [0, 1, 2, 3, 4]
    assert cli.parse_seeds("1,4,9") == [1, 4, 9]
    assert cli.parse_seeds("1,3-5") == [1, 3, 4, 5]
    with pytest.raises(ValueError):
        cli.parse_seeds("5-2")
    with pytest.raises(ValueError):
        cli.parse_seeds("")


def test_single_universe_writes_every_artifact(tmp_path):
    out = str(tmp_path / "u")
    assert cli.main(["--seed", "11", "--out", out, "--strict"]) == 0
    for name in ("textbook.md", "chunks.jsonl", "theory_graph.json",
                 "answer_key.json", "verification.json", "manifest.json"):
        assert os.path.exists(os.path.join(out, name)), name
    chapters = sorted(os.listdir(os.path.join(out, "chapters")))
    assert len(chapters) >= 5
    assert all(c.endswith(".md") for c in chapters)


def test_manifest_reports_per_level_and_per_chapter_and_no_pooled_score(tmp_path):
    out = str(tmp_path / "u")
    cli.main(["--seed", "12", "--out", out])
    man = _read(os.path.join(out, "manifest.json"))
    assert man["seed"] == 12
    assert 20 <= man["pages"] <= 60
    assert man["dependency_depth"] >= 4
    assert man["node_counts"]["theorem"] >= 4
    assert man["exercise_breakdown"]["by_level"]
    assert man["exercise_breakdown"]["by_chapter"]
    assert "pooled" in man["exercise_breakdown"]["note"]
    assert man["verification"]["all_passed"] is True
    assert man["verification"]["pass_rate"] == 1.0
    assert man["candidates_rejected"]["copyable"] >= 0
    assert sum(man["exercise_breakdown"]["by_level"].values()) == \
        man["exercise_breakdown"]["total"]


def test_theory_graph_is_machine_readable_and_complete(tmp_path):
    out = str(tmp_path / "u")
    cli.main(["--seed", "13", "--out", out])
    graph = _read(os.path.join(out, "theory_graph.json"))
    ids = {n["node_id"] for n in graph["nodes"]}
    assert graph["depth"] >= 4
    for edge in graph["edges"]:
        assert edge["from"] in ids and edge["to"] in ids
    for node in graph["nodes"]:
        assert set(node["depends_on"]) <= ids
        assert node["kind"] in ("signature", "axiom", "definition", "theorem",
                                "refutation")


def test_answer_key_carries_recipes_and_necessity_witnesses(tmp_path):
    out = str(tmp_path / "u")
    cli.main(["--seed", "14", "--out", out])
    key = _read(os.path.join(out, "answer_key.json"))
    assert key["exercises"]
    assert "pooled" in key["reporting_rule"]
    for ex in key["exercises"]:
        assert ex["answer"]
        assert ex["recipe"]["kind"]
        assert ex["necessity"]["answer_absent_from_prompt"] is True
        assert ex["necessity"]["sibling_divergence"] >= 0.5
        assert ex["required_chapters"]


def test_answer_key_answers_are_absent_from_the_chapters(tmp_path):
    """A reader with the book must still have to do the work."""
    out = str(tmp_path / "u")
    cli.main(["--seed", "15", "--out", out])
    key = _read(os.path.join(out, "answer_key.json"))
    with open(os.path.join(out, "textbook.md"), encoding="utf-8") as fh:
        book = fh.read()
    for ex in key["exercises"]:
        assert f"{ex['exercise_id']}. {ex['answer']}" not in book


def test_chunks_are_one_json_object_per_line(tmp_path):
    out = str(tmp_path / "u")
    cli.main(["--seed", "16", "--out", out])
    with open(os.path.join(out, "chunks.jsonl"), encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh if line.strip()]
    assert len(rows) >= 60
    assert {"chunk_id", "chapter", "section_kind", "node_ids", "text"} <= set(rows[0])


def test_multi_seed_run_writes_a_summary(tmp_path):
    out = str(tmp_path / "set")
    assert cli.main(["--seeds", "20-23", "--out", out, "--strict"]) == 0
    summary = _read(os.path.join(out, "summary.json"))
    assert summary["universes"] == 4
    assert summary["universes_fully_verified"] == 4
    assert summary["dependency_depth"]["min"] >= 4
    assert summary["pages"]["min"] >= 20
    assert summary["verification_pass_rate"]["min"] == 1.0
    for seed in (20, 21, 22, 23):
        assert os.path.exists(os.path.join(out, f"u{seed:04d}", "manifest.json"))


def test_novelty_flag_adds_the_audit(tmp_path):
    out = str(tmp_path / "set")
    cli.main(["--seeds", "30-32", "--out", out, "--novelty"])
    summary = _read(os.path.join(out, "summary.json"))
    assert summary["novelty"]["pairs"] == 3
    assert summary["novelty"]["symbol_overlap"]["max"] <= 0.15
    assert summary["novelty"]["answers_overlap"]["max"] <= 0.15


def test_a_rerun_reproduces_the_same_bytes(tmp_path):
    first, second = str(tmp_path / "a"), str(tmp_path / "b")
    cli.main(["--seed", "17", "--out", first])
    cli.main(["--seed", "17", "--out", second])
    for name in ("textbook.md", "chunks.jsonl", "theory_graph.json",
                 "answer_key.json"):
        with open(os.path.join(first, name), encoding="utf-8") as fh:
            a = fh.read()
        with open(os.path.join(second, name), encoding="utf-8") as fh:
            b = fh.read()
        assert a == b, name
