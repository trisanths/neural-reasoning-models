import json
import random
import shutil
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from scripts import render_regime_e
from src.train.data import ShardReader
from src.train.tokenizer import (PROCGEN_OFFSET, PROCGEN_SYMBOLS,
                                 load_tokenizer, train_tokenizer)

BASE_SEED = 917
# One rendered worldgen retrieval episode is a few thousand tokens, so the
# chunk has to be large enough for the 10 percent share to hold at least one.
CHUNK_TOKENS = 40000
NUM_CHUNKS = 3
NATURAL_WINDOW = 256

# Real-world anchors planted in every raw document. The scrubber must keep
# all of them out of the rendered stream.
REAL_ENTITIES = ["Einstein", "Paris", "NASA", "Curie", "Lisbon"]


@pytest.fixture(scope="module")
def tok_path(tmp_path_factory):
    base = tmp_path_factory.mktemp("regimeecorpus")
    rng = random.Random(23)
    words = [
        "lomera", "vantrix", "korath", "acquired", "shipped", "company",
        "officer", "route", "the", "of", "reports", "that", "cargo", "who",
        "held", "contract", "quarter", "filing", "memo", "note", "sentence",
        "mentions", "passage", "does", "what", "when", "where", "many",
    ]
    corpus = base / "corpus.txt"
    with open(corpus, "w") as fh:
        for _ in range(1500):
            fh.write(" ".join(rng.choices(words, k=10)) + "\n")
    path = base / "tokenizer.json"
    train_tokenizer([str(corpus)], out_path=str(path), vocab_size=1024)
    return str(path)


@pytest.fixture(scope="module")
def parquet_dir(tmp_path_factory):
    out = tmp_path_factory.mktemp("regimee_parquet")
    rng = random.Random(31)
    subjects = ["Einstein", "Marie Curie", "NASA", "the harbor office",
                "the northern depot"]
    places = ["Paris", "Lisbon"]
    verbs = ["reported", "shipped", "audited", "approved", "recorded"]
    objects = ["a quarterly filing", "the cargo manifest", "an old ledger",
               "the survey results", "a repair contract"]
    # Every document opens with a sentence that mentions each planted
    # entity mid-sentence, so the scrubber's sentence-start heuristic has
    # the evidence it needs to treat later sentence-initial mentions as
    # entities.
    preamble = ("The council heard from Einstein, Marie Curie, NASA, "
                "Paris, and Lisbon before the review.")
    for fi in range(2):
        texts = []
        for _ in range(120):
            sents = [preamble]
            for _ in range(rng.randint(6, 10)):
                sents.append(
                    f"{rng.choice(subjects)} {rng.choice(verbs)} "
                    f"{rng.choice(objects)} in {rng.choice(places)} "
                    f"in {rng.randint(1900, 2020)} with "
                    f"{rng.randint(4, 900)} staff.")
            texts.append(" ".join(sents))
        table = pa.table({"text": texts})
        pq.write_table(table, out / f"{fi:03d}.parquet", row_group_size=40)
    return str(out)


def run_render(out: Path, tok_path: str, parquet_dir: str, procs: int = 2,
               extra: list | None = None) -> int:
    return render_regime_e.main([
        "--out", str(out),
        "--tokenizer", tok_path,
        "--parquet-dir", parquet_dir,
        "--seed", str(BASE_SEED),
        "--chunk-tokens", str(CHUNK_TOKENS),
        "--num-chunks", str(NUM_CHUNKS),
        "--natural-window", str(NATURAL_WINDOW),
        "--qa-per-passage", "4",
        "--qa-passage-chars", "600",
        "--procs", str(procs),
    ] + (extra or []))


def chunk_bytes(chunk_dir: Path) -> bytes:
    return b"".join(p.read_bytes() for p in sorted(chunk_dir.glob("*.bin")))


@pytest.fixture(scope="module")
def rendered(tok_path, parquet_dir, tmp_path_factory):
    out = tmp_path_factory.mktemp("regimee_out")
    assert run_render(out, tok_path, parquet_dir) == 0
    return out


def test_chunks_manifest_and_merged_index(rendered):
    with open(rendered / "manifest.json") as fh:
        manifest = json.load(fh)
    assert manifest["regime"] == "e"
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
    assert abs(shares["natural"] - 0.70) < 0.10
    assert abs(shares["qa"] - 0.15) < 0.10
    assert abs(shares["worldgen"] - 0.10) < 0.10
    assert abs(shares["procgen"] - 0.05) < 0.04
    for chunk in manifest["chunks"]:
        assert chunk["natural_docs"] > 0
        assert chunk["qa_traces"] > 0
        assert chunk["qa_pairs"] >= chunk["qa_traces"]
        assert chunk["worldgen_episodes"] > 0
        assert chunk["procgen_examples"] > 0


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
    assert top <= render_regime_e.HELDOUT_INDEX_BASE


def test_stream_contents(rendered, tok_path):
    tok = load_tokenizer(tok_path)
    sid = tok.special_ids
    reader = ShardReader(str(rendered))
    tokens = reader.get_slice(0, reader.total_tokens)
    counts = np.bincount(tokens, minlength=tok.vocab_size)
    # QA and worldgen structure is present.
    assert counts[sid["<|world|>"]] > 0
    assert counts[sid["<|doc|>"]] > 0
    assert counts[sid["<|q|>"]] > 0
    assert counts[sid["<|a|>"]] > 0
    # The worldgen share carries retrieval traces.
    assert counts[sid["<|retrieve|>"]] > 0
    assert counts[sid["<|result|>"]] > 0
    # Procgen ids stay inside the reserved range and appear.
    reserved = counts[PROCGEN_OFFSET:PROCGEN_OFFSET + PROCGEN_SYMBOLS]
    assert reserved.sum() > 0
    assert int(tokens.max()) < tok.vocab_size


def test_no_unscrubbed_entity_survives(rendered, tok_path):
    """Scrubber integration: the planted real-world entities from the raw
    parquet text never reach the rendered stream, in any source."""
    tok = load_tokenizer(tok_path)
    reader = ShardReader(str(rendered))
    text = tok.decode(list(reader.get_slice(0, reader.total_tokens)))
    for entity in REAL_ENTITIES:
        assert entity not in text
    # The QA traces are present with their domain marker.
    assert "domain: extractive_qa" in text


def test_qa_traces_round_trip_from_stream(rendered, tok_path):
    """Decode the stream, pull out every extractive QA trace, and verify
    each answer is derivable from its passage by string operations."""
    tok = load_tokenizer(tok_path)
    reader = ShardReader(str(rendered))
    text = tok.decode(list(reader.get_slice(0, reader.total_tokens)))
    traces = [seg for seg in text.split("<|world|>")
              if seg.startswith("domain: extractive_qa")]
    assert traces
    checked = 0
    for trace in traces:
        passage = trace.partition("<|doc|>")[2].partition("<|q|>")[0]
        assert passage.strip()
        body = trace.partition("<|q|>")[2]
        for block in body.split("<|q|>"):
            q_and_a, _, tail = block.partition("<|a|>")
            answer = tail.partition("<|eot|>")[0]
            assert q_and_a.endswith("?")
            if answer in ("yes", "no"):
                subject = q_and_a.partition('"')[2].rpartition('"')[0]
                assert subject
                assert (subject in passage) == (answer == "yes")
            else:
                assert answer in passage
            checked += 1
    assert checked > 0


def test_deterministic_across_runs(rendered, tok_path, parquet_dir,
                                   tmp_path_factory):
    out2 = tmp_path_factory.mktemp("regimee_out2")
    assert run_render(out2, tok_path, parquet_dir, procs=1) == 0
    for k in range(NUM_CHUNKS):
        a = chunk_bytes(rendered / f"chunk-{k:05d}")
        b = chunk_bytes(out2 / f"chunk-{k:05d}")
        assert a == b


def test_restart_skips_done_and_rerenders_partial(rendered, tok_path,
                                                  parquet_dir):
    target = rendered / "chunk-00001"
    before = chunk_bytes(target)
    with open(rendered / "chunk-00000.done") as fh:
        untouched_before = json.load(fh)
    # Simulate a kill part way through chunk 1: marker gone, files partial.
    Path(str(target) + ".done").unlink()
    shutil.rmtree(target)
    target.mkdir()
    (target / "shard-00000.bin").write_bytes(b"\x00\x01garbage")
    assert run_render(rendered, tok_path, parquet_dir) == 0
    assert chunk_bytes(target) == before
    with open(rendered / "chunk-00000.done") as fh:
        assert json.load(fh) == untouched_before
    merged = ShardReader(str(rendered))
    with open(rendered / "manifest.json") as fh:
        assert merged.total_tokens == json.load(fh)["total_tokens"]


def test_target_tokens_stops_early(tok_path, parquet_dir, tmp_path_factory):
    out = tmp_path_factory.mktemp("regimee_early")
    rc = render_regime_e.main([
        "--out", str(out),
        "--tokenizer", tok_path,
        "--parquet-dir", parquet_dir,
        "--seed", str(BASE_SEED),
        "--chunk-tokens", str(CHUNK_TOKENS),
        "--target-tokens", str(CHUNK_TOKENS),
        "--natural-window", str(NATURAL_WINDOW),
        "--qa-per-passage", "4",
        "--qa-passage-chars", "600",
        "--procs", "1",
    ])
    assert rc == 0
    with open(out / "manifest.json") as fh:
        manifest = json.load(fh)
    assert 1 <= len(manifest["chunks"]) <= 2
    assert manifest["total_tokens"] >= CHUNK_TOKENS


def test_mix_normalization_and_type_mix_parsing():
    with pytest.raises(ValueError):
        render_regime_e.normalize_mix({"natural": -1.0, "qa": 0.5})
    with pytest.raises(ValueError):
        render_regime_e.normalize_mix({"natural": 0.0, "qa": 0.0})
    mix = render_regime_e.normalize_mix({"natural": 1.0, "qa": 0.0,
                                         "worldgen": 1.0})
    assert set(mix) == {"natural", "worldgen"}
    assert abs(sum(mix.values()) - 1.0) < 1e-9
    parsed = render_regime_e.parse_type_mix("span_cloze=1,existence=1")
    assert parsed == {"span_cloze": 0.5, "existence": 0.5}
    with pytest.raises(ValueError):
        render_regime_e.parse_type_mix("bogus=1")
    parsed = render_regime_e.parse_type_mix("span_cloze=3,recap=1")
    assert parsed == {"span_cloze": 0.75, "recap": 0.25}


def test_webret_mix_validation():
    with pytest.raises(SystemExit):
        render_regime_e.main([
            "--out", "unused", "--tokenizer", "unused",
            "--parquet-dir", "unused", "--seed", "1", "--num-chunks", "1",
            "--webret-min-docs", "9", "--webret-max-docs", "4",
        ])


E2_ARGS = [
    "--mix-natural", "0.55", "--mix-qa", "0.30",
    "--mix-worldgen", "0.10", "--mix-procgen", "0.05",
    "--qa-type-mix",
    "span_cloze=0.60,sentence_select=0.15,existence=0.10,recap=0.15",
]

RECAP_LEAD = "The passage states that "


def test_e2_mix_renders_recap_traces(tok_path, parquet_dir,
                                     tmp_path_factory):
    """E2 configuration: rebalanced source mix plus the recap question
    type. Recap lines land between the document and the first question
    token, and every echoed span is a verbatim substring of its passage."""
    out = tmp_path_factory.mktemp("regimee2_out")
    rc = render_regime_e.main([
        "--out", str(out),
        "--tokenizer", tok_path,
        "--parquet-dir", parquet_dir,
        "--seed", str(BASE_SEED + 1),
        "--chunk-tokens", str(CHUNK_TOKENS),
        "--num-chunks", "2",
        "--natural-window", str(NATURAL_WINDOW),
        "--qa-per-passage", "4",
        "--qa-passage-chars", "600",
        "--procs", "2",
    ] + E2_ARGS)
    assert rc == 0
    with open(out / "manifest.json") as fh:
        manifest = json.load(fh)
    total = manifest["total_tokens"]
    shares = {k: v / total
              for k, v in manifest["total_source_tokens"].items()}
    assert abs(shares["natural"] - 0.55) < 0.10
    assert abs(shares["qa"] - 0.30) < 0.10
    assert manifest["total_qa_recaps"] > 0
    assert manifest["total_qa_pairs"] > 0

    tok = load_tokenizer(tok_path)
    reader = ShardReader(str(out))
    text = tok.decode(list(reader.get_slice(0, reader.total_tokens)))
    traces = [seg for seg in text.split("<|world|>")
              if seg.startswith("domain: extractive_qa")]
    assert traces
    checked = 0
    for trace in traces:
        head = trace.partition("<|doc|>")[2].partition("<|q|>")[0]
        head = head.partition("<|eot|>")[0]
        if RECAP_LEAD not in head:
            continue
        passage = head.split("\n" + RECAP_LEAD)[0]
        assert passage.strip()
        for line in head.split("\n"):
            if not line.startswith(RECAP_LEAD):
                continue
            span_txt = line.rpartition(" given is ")[2]
            if span_txt.endswith("."):
                span_txt = span_txt[:-1]
            assert span_txt
            assert span_txt in passage
            checked += 1
    assert checked >= 20


# Regime E3: shuffle entity policy plus scrubbed-web retrieval episodes.
# Bundle knobs are shrunk to the fixture corpus scale; the preset mix and
# policy stay as shipped.
E3_EXTRA = [
    "--webret-min-docs", "6", "--webret-max-docs", "10",
    "--webret-doc-chars", "500", "--webret-questions", "3",
    "--webret-context-docs", "2", "--pool-docs", "60",
]


def run_render_e3(out: Path, tok_path: str, parquet_dir: str,
                  procs: int = 2) -> int:
    return render_regime_e.main([
        "--out", str(out),
        "--tokenizer", tok_path,
        "--parquet-dir", parquet_dir,
        "--seed", str(BASE_SEED + 2),
        "--chunk-tokens", str(CHUNK_TOKENS),
        "--num-chunks", "2",
        "--natural-window", str(NATURAL_WINDOW),
        "--qa-per-passage", "4",
        "--qa-passage-chars", "600",
        "--procs", str(procs),
        "--preset", "e3",
    ] + E3_EXTRA)


@pytest.fixture(scope="module")
def rendered_e3(tok_path, parquet_dir, tmp_path_factory):
    out = tmp_path_factory.mktemp("regimee3_out")
    assert run_render_e3(out, tok_path, parquet_dir) == 0
    return out


def test_e3_manifest_mix_and_policy(rendered_e3):
    with open(rendered_e3 / "manifest.json") as fh:
        manifest = json.load(fh)
    assert manifest["preset"] == "e3"
    assert manifest["entity_policy"] == "shuffle"
    assert manifest["mix"] == {"natural": 0.45, "qa": 0.25, "webret": 0.20,
                               "worldgen": 0.05, "procgen": 0.05}
    assert "recap" in manifest["qa_type_mix"]
    total = manifest["total_tokens"]
    shares = {k: v / total
              for k, v in manifest["total_source_tokens"].items()}
    # Whole episodes are coarse against these tiny chunks, so the bounds
    # are loose; a full size chunk tracks far tighter.
    assert 0.30 < shares["natural"] < 0.60
    assert 0.12 < shares["qa"] < 0.40
    assert 0.08 < shares["webret"] < 0.35
    assert shares["worldgen"] < 0.20
    assert shares["procgen"] < 0.10
    assert manifest["total_webret_episodes"] > 0
    assert manifest["total_webret_questions"] > 0
    assert manifest["total_qa_recaps"] > 0


def test_e3_query_first_fraction(rendered_e3):
    with open(rendered_e3 / "manifest.json") as fh:
        manifest = json.load(fh)
    episodes = manifest["total_webret_episodes"]
    query_first = manifest["total_webret_query_first"]
    assert episodes > 0
    assert query_first / episodes >= 0.40


def test_e3_webret_traces_supported_in_stream(rendered_e3, tok_path):
    """Stream-level support check: every scrubbed-web answer is a
    verbatim substring of the last served retrieval result, and the
    query-first share of traces carries no in-context documents."""
    tok = load_tokenizer(tok_path)
    reader = ShardReader(str(rendered_e3))
    text = tok.decode(list(reader.get_slice(0, reader.total_tokens)))
    traces = [seg for seg in text.split("<|world|>")
              if seg.startswith("domain: scrubbed_web")]
    assert traces
    checked = 0
    query_first = 0
    for trace in traces:
        head = trace.partition("<|q|>")[0]
        if "<|doc|>" not in head:
            query_first += 1
        for block in trace.split("<|q|>")[1:]:
            assert "<|retrieve|>" in block
            assert "<|result|>" in block
            answer = block.partition("<|a|>")[2].partition("<|eot|>")[0]
            last_result = block.partition("<|a|>")[0]
            last_result = last_result.rpartition("<|result|>")[2]
            assert answer
            assert answer in last_result
            checked += 1
    assert checked > 0
    assert query_first / len(traces) >= 0.40


def test_e3_pool_names_reach_the_stream(rendered_e3, tok_path):
    """Shuffle policy integration: the planted real entities are pool
    members, so they keep appearing in the rendered stream as
    reassigned names instead of vanishing."""
    tok = load_tokenizer(tok_path)
    reader = ShardReader(str(rendered_e3))
    text = tok.decode(list(reader.get_slice(0, reader.total_tokens)))
    present = sum(1 for entity in REAL_ENTITIES if entity in text)
    assert present >= 3


def test_e3_deterministic_across_procs(rendered_e3, tok_path, parquet_dir,
                                       tmp_path_factory):
    out2 = tmp_path_factory.mktemp("regimee3_out2")
    assert run_render_e3(out2, tok_path, parquet_dir, procs=1) == 0
    for k in range(2):
        a = chunk_bytes(rendered_e3 / f"chunk-{k:05d}")
        b = chunk_bytes(out2 / f"chunk-{k:05d}")
        assert a == b
