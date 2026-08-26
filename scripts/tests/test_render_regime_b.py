import json
import random
import shutil
from pathlib import Path

import numpy as np
import pytest

from scripts import render_regime_b
from src.train.data import ShardReader, ShardWriter
from src.train.tokenizer import (PROCGEN_OFFSET, PROCGEN_SYMBOLS,
                                 load_tokenizer, train_tokenizer)

BASE_SEED = 913
# One rendered worldgen episode is a few thousand tokens, so the chunk has
# to be large enough for the 15 percent share to hold several episodes.
CHUNK_TOKENS = 40000
NUM_CHUNKS = 3
NATURAL_WINDOW = 256


@pytest.fixture(scope="module")
def tok_path(tmp_path_factory):
    base = tmp_path_factory.mktemp("regimebcorpus")
    rng = random.Random(19)
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


@pytest.fixture(scope="module")
def natural_dir(tok_path, tmp_path_factory):
    """A small stand-in for rendered regime A shards: random BPE range ids."""
    out = tmp_path_factory.mktemp("regimeb_natural")
    tok = load_tokenizer(tok_path)
    rng = np.random.default_rng(5)
    writer = ShardWriter(str(out), shard_size=4096)
    bpe_base = PROCGEN_OFFSET + PROCGEN_SYMBOLS
    for _ in range(6):
        writer.write(rng.integers(bpe_base, tok.vocab_size,
                                  size=3000, dtype=np.uint16))
    writer.close()
    return str(out)


def run_render(out: Path, tok_path: str, natural_dir: str, procs: int = 2,
               extra: list | None = None) -> int:
    return render_regime_b.main([
        "--out", str(out),
        "--tokenizer", tok_path,
        "--natural-shards", natural_dir,
        "--seed", str(BASE_SEED),
        "--chunk-tokens", str(CHUNK_TOKENS),
        "--num-chunks", str(NUM_CHUNKS),
        "--natural-window", str(NATURAL_WINDOW),
        "--procs", str(procs),
    ] + (extra or []))


def chunk_bytes(chunk_dir: Path) -> bytes:
    return b"".join(p.read_bytes() for p in sorted(chunk_dir.glob("*.bin")))


@pytest.fixture(scope="module")
def rendered(tok_path, natural_dir, tmp_path_factory):
    out = tmp_path_factory.mktemp("regimeb_out")
    assert run_render(out, tok_path, natural_dir) == 0
    return out


def test_chunks_manifest_and_merged_index(rendered):
    with open(rendered / "manifest.json") as fh:
        manifest = json.load(fh)
    assert len(manifest["chunks"]) == NUM_CHUNKS
    for chunk in manifest["chunks"]:
        chunk_dir = rendered / f"chunk-{chunk['id']:05d}"
        assert (chunk_dir / "index.json").exists()
        assert Path(str(chunk_dir) + ".done").exists()
        assert chunk["tokens"] >= CHUNK_TOKENS
        reader = ShardReader(str(chunk_dir))
        assert reader.total_tokens == chunk["tokens"]
        assert chunk["tokens"] == sum(chunk["source_tokens"].values())
    assert manifest["total_tokens"] == sum(
        c["tokens"] for c in manifest["chunks"])
    merged = ShardReader(str(rendered))
    assert merged.total_tokens == manifest["total_tokens"]
    first = ShardReader(str(rendered / "chunk-00000"))
    n = first.total_tokens
    np.testing.assert_array_equal(
        merged.get_slice(n - 8, 16)[:8], first.get_slice(n - 8, 8))


def test_mix_tracks_targets(rendered):
    with open(rendered / "manifest.json") as fh:
        manifest = json.load(fh)
    total = manifest["total_tokens"]
    shares = {k: v / total
              for k, v in manifest["total_source_tokens"].items()}
    # Segments are coarse relative to these tiny chunks, so the tolerance
    # is loose; a full size chunk tracks far tighter.
    assert abs(shares["natural"] - 0.80) < 0.10
    assert abs(shares["worldgen"] - 0.15) < 0.10
    assert abs(shares["procgen"] - 0.05) < 0.04
    for chunk in manifest["chunks"]:
        assert chunk["worldgen_episodes"] > 0
        assert chunk["procgen_examples"] > 0
        assert chunk["natural_windows"] > 0


def test_worldgen_index_ranges_disjoint(rendered):
    with open(rendered / "manifest.json") as fh:
        manifest = json.load(fh)
    stride = manifest["episode_stride"]
    for chunk in manifest["chunks"]:
        assert chunk["worldgen_index_base"] == chunk["id"] * stride
        assert chunk["worldgen_episodes"] < stride
    bases = [c["worldgen_index_base"] for c in manifest["chunks"]]
    assert len(set(bases)) == len(bases)
    top = max(bases) + stride
    assert top <= render_regime_b.HELDOUT_INDEX_BASE


def test_stream_contents(rendered, tok_path):
    tok = load_tokenizer(tok_path)
    sid = tok.special_ids
    reader = ShardReader(str(rendered))
    tokens = reader.get_slice(0, reader.total_tokens)
    counts = np.bincount(tokens, minlength=tok.vocab_size)
    # Worldgen QA structure is present.
    assert counts[sid["<|world|>"]] > 0
    assert counts[sid["<|q|>"]] > 0
    assert counts[sid["<|a|>"]] > 0
    # No retrieval traces anywhere in regime B.
    assert counts[sid["<|retrieve|>"]] == 0
    assert counts[sid["<|result|>"]] == 0
    # Procgen ids stay inside the reserved range and appear.
    reserved = counts[PROCGEN_OFFSET:PROCGEN_OFFSET + PROCGEN_SYMBOLS]
    assert reserved.sum() > 0
    assert int(tokens.max()) < tok.vocab_size


def test_deterministic_across_runs(rendered, tok_path, natural_dir,
                                   tmp_path_factory):
    out2 = tmp_path_factory.mktemp("regimeb_out2")
    assert run_render(out2, tok_path, natural_dir, procs=1) == 0
    for k in range(NUM_CHUNKS):
        a = chunk_bytes(rendered / f"chunk-{k:05d}")
        b = chunk_bytes(out2 / f"chunk-{k:05d}")
        assert a == b


def test_restart_skips_done_and_rerenders_partial(rendered, tok_path,
                                                  natural_dir):
    target = rendered / "chunk-00001"
    before = chunk_bytes(target)
    with open(rendered / "chunk-00000.done") as fh:
        untouched_before = json.load(fh)
    # Simulate a kill part way through chunk 1: marker gone, files partial.
    Path(str(target) + ".done").unlink()
    shutil.rmtree(target)
    target.mkdir()
    (target / "shard-00000.bin").write_bytes(b"\x00\x01garbage")
    assert run_render(rendered, tok_path, natural_dir) == 0
    assert chunk_bytes(target) == before
    with open(rendered / "chunk-00000.done") as fh:
        assert json.load(fh) == untouched_before
    merged = ShardReader(str(rendered))
    with open(rendered / "manifest.json") as fh:
        assert merged.total_tokens == json.load(fh)["total_tokens"]


def test_target_tokens_stops_early(tok_path, natural_dir, tmp_path_factory):
    out = tmp_path_factory.mktemp("regimeb_early")
    rc = render_regime_b.main([
        "--out", str(out),
        "--tokenizer", tok_path,
        "--natural-shards", natural_dir,
        "--seed", str(BASE_SEED),
        "--chunk-tokens", str(CHUNK_TOKENS),
        "--target-tokens", str(CHUNK_TOKENS),
        "--natural-window", str(NATURAL_WINDOW),
        "--procs", "1",
    ])
    assert rc == 0
    with open(out / "manifest.json") as fh:
        manifest = json.load(fh)
    assert 1 <= len(manifest["chunks"]) <= 2
    assert manifest["total_tokens"] >= CHUNK_TOKENS


def test_worldgen_retrieval_flag_renders_regime_d(tok_path, natural_dir,
                                                  tmp_path_factory):
    """--worldgen-retrieval puts multi-hop traces in the worldgen segments
    and nowhere else; natural and procgen segments match the plain samplers."""
    out = tmp_path_factory.mktemp("regimed_out")
    assert run_render(out, tok_path, natural_dir, procs=1,
                      extra=["--worldgen-retrieval"]) == 0
    tok = load_tokenizer(tok_path)
    sid = tok.special_ids
    with open(out / "manifest.json") as fh:
        manifest = json.load(fh)
    assert manifest["regime"] == "d"
    assert manifest["worldgen_retrieval"] is True

    chunk = manifest["chunks"][0]
    reader = ShardReader(str(out / "chunk-00000"))
    stream = reader.get_slice(0, reader.total_tokens)
    counts = np.bincount(stream, minlength=tok.vocab_size)
    assert counts[sid["<|retrieve|>"]] > 0
    assert counts[sid["<|result|>"]] > 0

    # Replay the chunk's worldgen stream with the retrieval sampler. Its
    # token total must match the manifest's worldgen share, and it must
    # account for every trace token in the chunk, which proves the traces
    # sit only in worldgen segments.
    sampler = render_regime_b.WorldgenSampler(
        tok, BASE_SEED, 0, manifest["episode_stride"], manifest["domains"],
        manifest["contradiction_rate"], manifest["filler_rate"],
        manifest["max_doc_tokens"], retrieval=True)
    wg_tokens: list = []
    for _ in range(chunk["worldgen_episodes"]):
        wg_tokens.extend(sampler.next_segment())
    assert len(wg_tokens) == chunk["source_tokens"]["worldgen"]
    wg_counts = np.bincount(np.asarray(wg_tokens), minlength=tok.vocab_size)
    assert wg_counts[sid["<|retrieve|>"]] == counts[sid["<|retrieve|>"]]
    assert wg_counts[sid["<|result|>"]] == counts[sid["<|result|>"]]

    # The natural share replays byte for byte from the plain natural
    # sampler, so the flag left it untouched, and it carries no trace ids.
    nat = render_regime_b.NaturalSampler(
        ShardReader(natural_dir), NATURAL_WINDOW,
        np.random.default_rng((BASE_SEED, 0, 1)))
    nat_tokens = np.concatenate(
        [nat.next_segment() for _ in range(chunk["natural_windows"])])
    assert nat_tokens.size == chunk["source_tokens"]["natural"]
    assert sid["<|retrieve|>"] not in nat_tokens
    assert sid["<|result|>"] not in nat_tokens

    # The procgen share replays from the plain procgen sampler and stays in
    # the reserved range, so it is untouched too. Reserved-range tokens in
    # the chunk come only from procgen, and their histograms match.
    proc = render_regime_b.ProcgenSampler(
        render_regime_b.parse_procgen_mix(manifest["procgen_mix"]),
        np.random.default_rng((BASE_SEED, 0, 2)))
    proc_tokens = np.concatenate(
        [proc.next_segment() for _ in range(chunk["procgen_examples"])])
    assert proc_tokens.size == chunk["source_tokens"]["procgen"]
    lo, hi = PROCGEN_OFFSET, PROCGEN_OFFSET + PROCGEN_SYMBOLS
    assert proc_tokens.min() >= lo and proc_tokens.max() < hi
    proc_counts = np.bincount(proc_tokens, minlength=tok.vocab_size)
    np.testing.assert_array_equal(counts[lo:hi], proc_counts[lo:hi])


def test_mix_normalization_rejects_bad_weights():
    with pytest.raises(ValueError):
        render_regime_b.normalize_mix(-1.0, 0.5, 0.5)
    with pytest.raises(ValueError):
        render_regime_b.normalize_mix(0.0, 0.0, 0.0)
    mix = render_regime_b.normalize_mix(1.0, 0.0, 1.0)
    assert set(mix) == {"natural", "procgen"}
    assert abs(sum(mix.values()) - 1.0) < 1e-9
