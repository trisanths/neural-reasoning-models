import json
import random
from pathlib import Path

import pytest

from scripts import decode_trace, render_regime_c
from src.train.data import ShardReader
from src.train.tokenizer import load_tokenizer, train_tokenizer
from src.worldgen.engine import episode_seed

BASE_SEED = 77
EPS_PER_CHUNK = 4
NUM_CHUNKS = 3
HELDOUT = 5


@pytest.fixture(scope="module")
def tok_path(tmp_path_factory):
    base = tmp_path_factory.mktemp("regimeccorpus")
    rng = random.Random(11)
    words = [
        "lomera", "vantrix", "korath", "acquired", "shipped", "company",
        "officer", "route", "the", "of", "reports", "that", "cargo", "who",
        "held", "contract", "quarter", "filing", "memo", "note",
    ]
    corpus = base / "corpus.txt"
    with open(corpus, "w") as fh:
        for _ in range(1500):
            fh.write(" ".join(rng.choices(words, k=10)) + "\n")
    path = base / "tokenizer.json"
    train_tokenizer([str(corpus)], out_path=str(path), vocab_size=1024)
    return str(path)


def run_render(out: Path, tok_path: str, procs: int = 2) -> int:
    return render_regime_c.main([
        "--out", str(out),
        "--tokenizer", tok_path,
        "--seed", str(BASE_SEED),
        "--episodes-per-chunk", str(EPS_PER_CHUNK),
        "--num-chunks", str(NUM_CHUNKS),
        "--procs", str(procs),
        "--heldout", str(HELDOUT),
    ])


def chunk_bytes(chunk_dir: Path) -> bytes:
    return b"".join(p.read_bytes() for p in sorted(chunk_dir.glob("*.bin")))


@pytest.fixture(scope="module")
def rendered(tok_path, tmp_path_factory):
    out = tmp_path_factory.mktemp("regimec_out")
    assert run_render(out, tok_path) == 0
    return out


def test_chunks_and_manifest(rendered, tok_path):
    with open(rendered / "manifest.json") as fh:
        manifest = json.load(fh)
    assert len(manifest["chunks"]) == NUM_CHUNKS
    assert manifest["total_episodes"] == NUM_CHUNKS * EPS_PER_CHUNK
    for chunk in manifest["chunks"]:
        chunk_dir = rendered / f"chunk-{chunk['id']:05d}"
        assert (chunk_dir / "index.json").exists()
        assert Path(str(chunk_dir) + ".done").exists()
        reader = ShardReader(str(chunk_dir))
        assert reader.total_tokens == chunk["tokens"]
        assert chunk["start_index"] == chunk["id"] * EPS_PER_CHUNK
    assert manifest["total_tokens"] == sum(
        c["tokens"] for c in manifest["chunks"])


def test_heldout_disjoint_seed_range(rendered):
    lines = (rendered / "heldout.jsonl").read_text().strip().splitlines()
    assert len(lines) == HELDOUT
    heldout_seeds = []
    base = render_regime_c.HELDOUT_INDEX_BASE
    for j, line in enumerate(lines):
        episode = json.loads(line)
        assert episode["seed"] == episode_seed(BASE_SEED, base + j)
        assert episode["questions"]
        heldout_seeds.append(episode["seed"])
    train_seeds = {
        episode_seed(BASE_SEED, i)
        for i in range(NUM_CHUNKS * EPS_PER_CHUNK)
    }
    assert train_seeds.isdisjoint(heldout_seeds)
    assert (rendered / "heldout.jsonl.done").exists()


def test_trace_structure_in_rendered_chunk(rendered, tok_path):
    rc = decode_trace.main([
        "--shards", str(rendered / "chunk-00000"),
        "--tokenizer", tok_path,
    ])
    assert rc == 0


def test_oracle_round_trip_on_random_samples(rendered, tok_path):
    rc = decode_trace.main([
        "--manifest", str(rendered / "manifest.json"),
        "--tokenizer", tok_path,
        "--samples", "3",
        "--sample-seed", "5",
    ])
    assert rc == 0


def test_restart_skips_done_and_rerenders_partial(rendered, tok_path):
    target = rendered / "chunk-00001"
    before = chunk_bytes(target)
    marker = Path(str(target) + ".done")
    with open(marker) as fh:
        seconds_before = json.load(fh)["seconds"]
    other_marker = rendered / "chunk-00000.done"
    with open(other_marker) as fh:
        other_before = json.load(fh)

    for path in target.glob("*"):
        path.unlink()
    target.rmdir()
    marker.unlink()

    assert run_render(rendered, tok_path, procs=1) == 0
    assert chunk_bytes(target) == before
    with open(marker) as fh:
        stats = json.load(fh)
    assert stats["seconds"] != seconds_before or stats["tokens"] > 0
    with open(other_marker) as fh:
        assert json.load(fh) == other_before

    with open(rendered / "manifest.json") as fh:
        manifest = json.load(fh)
    assert len(manifest["chunks"]) == NUM_CHUNKS
    assert manifest["total_episodes"] == NUM_CHUNKS * EPS_PER_CHUNK
