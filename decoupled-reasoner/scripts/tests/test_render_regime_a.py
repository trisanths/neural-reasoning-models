import json
import random
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from scripts import render_regime_a
from src.train.tokenizer import load_tokenizer, train_tokenizer

SHARD_SIZE = 2048

WORDS = [
    "orbit", "canal", "mercury", "quill", "harbor", "granite", "the",
    "of", "carried", "signal", "ledger", "vane", "sworn", "kestrel",
    "mill", "brine", "report", "filed", "under", "route",
]


@pytest.fixture(scope="module")
def tok_path(tmp_path_factory):
    base = tmp_path_factory.mktemp("regimeacorpus")
    rng = random.Random(7)
    corpus = base / "corpus.txt"
    with open(corpus, "w") as fh:
        for _ in range(1500):
            fh.write(" ".join(rng.choices(WORDS, k=10)) + "\n")
    path = base / "tokenizer.json"
    train_tokenizer([str(corpus)], out_path=str(path), vocab_size=512)
    return str(path)


@pytest.fixture(scope="module")
def parquet_dir(tmp_path_factory):
    base = tmp_path_factory.mktemp("regimeaparquet")
    rng = random.Random(13)
    for i, rows in enumerate([37, 53, 41]):
        texts = [
            " ".join(rng.choices(WORDS, k=rng.randint(4, 30)))
            for _ in range(rows)
        ]
        pq.write_table(pa.table({"text": texts}),
                       str(base / f"{i:03d}_00000.parquet"))
    return base


def render(out, tok_path, parquet_dir, procs, max_tokens=None, keep=True):
    argv = [
        "--parquet-dir", str(parquet_dir),
        "--tokenizer", tok_path,
        "--out", str(out),
        "--procs", str(procs),
        "--shard-size", str(SHARD_SIZE),
    ]
    if max_tokens is not None:
        argv += ["--max-tokens", str(max_tokens)]
    if keep:
        argv += ["--keep-chunks"]
    assert render_regime_a.main(argv) == 0


def read_index(out):
    with open(Path(out) / "index.json") as fh:
        return json.load(fh)


def stream_bytes(out):
    index = read_index(out)
    return b"".join((Path(out) / s["file"]).read_bytes()
                    for s in index["shards"])


@pytest.fixture(scope="module")
def single_out(tok_path, parquet_dir, tmp_path_factory):
    out = tmp_path_factory.mktemp("regimea_single")
    render(out, tok_path, parquet_dir, procs=1)
    return out


def test_multi_matches_single(single_out, tok_path, parquet_dir,
                              tmp_path_factory):
    out = tmp_path_factory.mktemp("regimea_multi")
    render(out, tok_path, parquet_dir, procs=2)
    assert read_index(out) == read_index(single_out)
    for entry in read_index(single_out)["shards"]:
        a = (Path(single_out) / entry["file"]).read_bytes()
        b = (Path(out) / entry["file"]).read_bytes()
        assert a == b, f"shard {entry['file']} differs between modes"


def test_max_tokens_cut_matches_single(single_out, tok_path, parquet_dir,
                                       tmp_path_factory):
    cap = read_index(single_out)["total_tokens"] // 2
    out_s = tmp_path_factory.mktemp("regimea_cap_single")
    out_m = tmp_path_factory.mktemp("regimea_cap_multi")
    render(out_s, tok_path, parquet_dir, procs=1, max_tokens=cap)
    render(out_m, tok_path, parquet_dir, procs=2, max_tokens=cap)
    assert read_index(out_m) == read_index(out_s)
    assert stream_bytes(out_m) == stream_bytes(out_s)
    total = read_index(out_m)["total_tokens"]
    assert total >= cap
    eot = load_tokenizer(tok_path).special_ids["<|eot|>"]
    stream = np.frombuffer(stream_bytes(out_m), dtype=np.uint16)
    # The cap cuts on a document boundary, so the stream ends with <|eot|>
    # and no earlier document end reaches the cap.
    assert stream[-1] == eot
    ends = np.flatnonzero(stream == eot) + 1
    assert ends[-1] == total
    assert all(e < cap for e in ends[:-1])


def test_restart_skips_done_and_rerenders_missing(single_out, tok_path,
                                                  parquet_dir,
                                                  tmp_path_factory):
    out = tmp_path_factory.mktemp("regimea_restart")
    render(out, tok_path, parquet_dir, procs=2)
    baseline = stream_bytes(out)
    chunks = Path(out) / "chunks"
    marker0 = chunks / "chunk-00000.done"
    mtime0 = marker0.stat().st_mtime_ns
    # Simulate a kill that lost chunk 1 entirely.
    (chunks / "chunk-00001.done").unlink()
    for p in sorted((chunks / "chunk-00001").iterdir()):
        p.unlink()
    render(out, tok_path, parquet_dir, procs=2)
    assert stream_bytes(out) == baseline
    assert marker0.stat().st_mtime_ns == mtime0, "done chunk was re-rendered"
    assert (chunks / "chunk-00001.done").exists()


def test_default_removes_chunks(single_out, tok_path, parquet_dir,
                                tmp_path_factory):
    out = tmp_path_factory.mktemp("regimea_clean")
    render(out, tok_path, parquet_dir, procs=2, keep=False)
    assert not (Path(out) / "chunks").exists()
    assert stream_bytes(out) == stream_bytes(single_out)
