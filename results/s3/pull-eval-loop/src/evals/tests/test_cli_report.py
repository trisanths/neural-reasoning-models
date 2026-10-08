import json

from src.evals.cli import main
from src.evals.report import build_report, render_markdown


def test_cli_end_to_end(tmp_path, tiny_ckpt, tok):
    tok_path = tmp_path / "tokenizer.json"
    tok.save(str(tok_path))
    out_dir = tmp_path / "report"
    rc = main(["--ckpt", str(tiny_ckpt), "--tokenizer", str(tok_path),
               "--out", str(out_dir), "--heldout-episodes", "2",
               "--heldout-seed", "31337", "--device", "cpu"])
    assert rc == 0
    report = json.loads((out_dir / "eval_report.json").read_text())
    assert report["meta"]["step"] == 7
    assert report["heldout_worlds"]["n_episodes"] == 2
    assert report["knowledge_probes"]["n"] >= 30
    md = (out_dir / "eval_report.md").read_text()
    assert "Held out worlds" in md
    assert "Knowledge probes" in md


def test_render_markdown_sections():
    heldout = {
        "suite": "heldout_worlds", "n_episodes": 1, "n_questions": 2,
        "accuracy": 0.5, "chance": 0.3,
        "per_domain": {"corporate": {"n": 2, "correct": 1, "accuracy": 0.5}},
        "per_type": {"lookup": {"n": 2, "correct": 1, "accuracy": 0.5}},
    }
    probes = {
        "suite": "knowledge_probes", "n": 40, "accuracy": 0.25,
        "chance": 0.25, "leakage_threshold": 0.455, "leakage_flag": False,
        "results": [],
    }
    report = build_report(heldout, probes, {"checkpoint": "x.pt", "step": 1,
                                            "heldout_seed": 9})
    md = render_markdown(report)
    assert "corporate" in md
    assert "lookup" in md
    assert "clear" in md
