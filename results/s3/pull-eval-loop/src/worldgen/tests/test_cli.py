import json

from src.worldgen.cli import main


def test_cli_writes_jsonl_and_meta(tmp_path):
    out = tmp_path / "worlds.jsonl"
    rc = main(["--episodes", "8", "--seed", "77", "--out", str(out),
               "--validate"])
    assert rc == 0
    lines = out.read_text().strip().split("\n")
    assert len(lines) == 8
    episodes = [json.loads(line) for line in lines]
    assert episodes[0]["episode_id"] == "ep-000000"
    assert episodes[-1]["episode_id"] == "ep-000007"
    meta = json.loads((tmp_path / "worlds.jsonl.meta.json").read_text())
    assert meta["episodes"] == 8
    assert meta["seed"] == 77
    assert meta["total_questions"] == sum(len(e["questions"]) for e in episodes)


def test_cli_reproducible(tmp_path):
    a = tmp_path / "a.jsonl"
    b = tmp_path / "b.jsonl"
    main(["--episodes", "4", "--seed", "5", "--out", str(a)])
    main(["--episodes", "4", "--seed", "5", "--out", str(b)])
    assert a.read_text() == b.read_text()


def test_cli_domain_filter(tmp_path):
    out = tmp_path / "c.jsonl"
    main(["--episodes", "3", "--seed", "5", "--out", str(out),
          "--domains", "logistics"])
    for line in out.read_text().strip().split("\n"):
        assert json.loads(line)["world"]["domain"] == "logistics"
