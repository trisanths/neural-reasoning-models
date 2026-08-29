"""The evidence lane's data stream and its command line entry point.

The stream's whole contract is that an example is a pure function of (seed,
global index): that is what makes a resumed lane replay the examples it would
have reached, and it is the only reason the run directory needs no iterator
state. Most of what follows is that property, checked from several angles.
"""

import json

import pytest
import torch

from src.train import evidence_cli
from src.train.evidence_data import EvidenceCollator, IGNORE_INDEX
from src.train.evidence_stream import (POOL_OFFSET, EvidenceStream,
                                       StreamConfig, config_from_yaml,
                                       load_web_episodes)
from src.train.tests.evidence_fixtures import TINY, StubTokenizer

BANK = 16
CHUNK = 16


def small_cfg(**kw) -> StreamConfig:
    base = dict(bank_size=BANK, chunk_len=CHUNK, pool_chunks=64,
                pool_episodes=4, questions_per_episode=3, seed=99)
    base.update(kw)
    return StreamConfig(**base)


def make_stream(**kw) -> EvidenceStream:
    return EvidenceStream(StubTokenizer(), small_cfg(**kw))


def web_episode(index: int) -> dict:
    """A scrubbed-web shaped episode: documents, and questions with a plan.

    The answer is a verbatim span of the planned document, which is the
    contract examples_from_web_episode relies on to locate the gold chunk.
    """
    docs = [{"text": f"web{index} doc{j} carries payload{index}_{j} and filler"}
            for j in range(6)]
    return {
        "episode_id": f"web-{index:06d}",
        "world": {"domain": "scrubbed_web"},
        "documents": docs,
        "questions": [
            {"text": f"what does web{index} doc{t} carry",
             "answer": f"payload{index}_{t}",
             "span_kind": "noun",
             "plan": [[f"web{index} doc{t}", t]]}
            for t in (3, 4)
        ],
    }


# ---- determinism and addressing ----


def test_example_is_a_pure_function_of_index():
    a, b = make_stream(), make_stream()
    for i in (0, 1, 5, 17, 61):
        ex_a, ex_b = a.example(i), b.example(i)
        assert ex_a.question_ids == ex_b.question_ids
        assert ex_a.answer_ids == ex_b.answer_ids
        assert [c.token_ids for c in ex_a.chunks] == [c.token_ids for c in ex_b.chunks]
        assert ex_a.gold_positions == ex_b.gold_positions


def test_a_different_seed_gives_different_examples():
    a = make_stream(seed=99)
    b = make_stream(seed=100)
    assert a.example(0).answer_ids != b.example(0).answer_ids


def test_out_of_order_access_matches_sequential_access():
    """The one-entry episode cache must not make the stream order dependent."""
    sequential = [make_stream().example(i) for i in range(9)]
    jumper = make_stream()
    shuffled = {i: jumper.example(i) for i in (7, 0, 3, 8, 1, 5, 2, 6, 4)}
    for i, ex in enumerate(sequential):
        assert shuffled[i].answer_ids == ex.answer_ids
        assert shuffled[i].gold_positions == ex.gold_positions


def test_consecutive_examples_share_one_episode_generation():
    stream = make_stream(questions_per_episode=3)
    for i in range(3):
        stream.example(i)
    assert stream.counts["worldgen"] == 1
    stream.example(3)
    assert stream.counts["worldgen"] == 2


def test_batches_from_a_start_index_match_the_examples_there():
    """Resume alignment: this is the property the CLI relies on."""
    tok = StubTokenizer()
    cfg = small_cfg()
    collator = EvidenceCollator(tok, cfg.bank_size, cfg.chunk_len, TINY.max_seq_len)
    start = 4 * 2  # two optimizer steps of accum 2, micro 2
    direct = EvidenceStream(tok, cfg)
    expected = collator([direct.example(start + k) for k in range(2)])
    resumed = EvidenceStream(StubTokenizer(), cfg)
    got = next(resumed.batches(2, collator, start=start))
    assert torch.equal(got.input_ids, expected.input_ids)
    assert torch.equal(got.targets, expected.targets)
    assert torch.equal(got.evidence_ids, expected.evidence_ids)


def test_stream_is_infinite_over_fresh_worlds():
    stream = make_stream()
    it = stream.examples(0)
    seen = {tuple(next(it).answer_ids) for _ in range(40)}
    assert len(seen) > 5
    assert stream.counts["worldgen"] >= 13


# ---- banks ----


def test_bank_is_filled_from_the_pool_to_bank_size():
    stream = make_stream()
    ex = stream.example(0)
    assert len(ex.chunks) == BANK
    assert all(len(c.token_ids) <= CHUNK for c in ex.chunks)


def test_pool_is_drawn_from_its_own_seed_stream():
    """A pool chunk must not be the gold chunk of the example it pads."""
    stream = make_stream()
    pool_sources = {c.source for c in stream.pool}
    assert pool_sources
    assert all(s.startswith("pool-") for s in pool_sources)
    ex = stream.example(0)
    gold_sources = {ex.chunks[p].source for p in ex.gold_positions}
    assert not (gold_sources & pool_sources)


def test_oracle_mode_places_gold_whenever_the_episode_has_any():
    """Oracle mode is an upper bound on retrieval, not a guarantee of gold.

    A worldgen question whose derivation names a fact that no single document
    states has no gold chunk to place, and the bank is then all distractors.
    That is a property of the episode, not of the bank builder, so what the
    builder owes is this: gold goes in whenever gold exists. The synthetic
    fixture episode always has it, so the check can be exact there.
    """
    from src.train.evidence_data import examples_from_episode
    from src.train.tests.evidence_fixtures import synthetic_episode

    tok = StubTokenizer()
    examples = examples_from_episode(
        synthetic_episode(n_docs=12, n_questions=3), tok, CHUNK, BANK,
        "oracle", seed=3)
    assert examples
    assert all(ex.gold_present for ex in examples)


def test_most_real_worldgen_banks_carry_gold_under_oracle():
    stream = make_stream(bank_mode="oracle")
    rate = sum(stream.example(i).gold_present for i in range(48)) / 48
    assert rate > 0.8


def test_distractor_mode_removes_gold():
    stream = make_stream(bank_mode="distractors")
    assert not any(stream.example(i).gold_present for i in range(12))


def test_bank_report_counts_what_it_saw():
    stream = make_stream()
    report = stream.bank_report(n=12)
    assert report["examples"] == 12
    assert 0.0 < report["gold_rate"] <= 1.0
    assert report["mean_bank_chunks"] == BANK
    assert report["pool_chunks"] == len(stream.pool)


# ---- the web source ----


def test_web_share_of_one_takes_every_episode_from_the_file():
    stream = EvidenceStream(StubTokenizer(), small_cfg(web_share=1.0),
                            web_episodes=[web_episode(i) for i in range(4)])
    for i in range(9):
        stream.example(i)
    assert stream.counts["web"] > 0
    assert stream.counts["worldgen"] == 0


def test_web_share_of_zero_never_reads_the_file():
    stream = EvidenceStream(StubTokenizer(), small_cfg(web_share=0.0),
                            web_episodes=[web_episode(0)])
    for i in range(9):
        stream.example(i)
    assert stream.counts["web"] == 0


def test_mixed_share_lands_near_the_configured_rate():
    stream = EvidenceStream(StubTokenizer(), small_cfg(web_share=0.5),
                            web_episodes=[web_episode(i) for i in range(8)])
    for i in range(600):
        stream.is_web(i)
    web = sum(1 for i in range(600) if stream.is_web(i))
    assert 0.4 < web / 600 < 0.6


def test_the_source_coin_is_stable_across_instances():
    kw = dict(web_share=0.5)
    a = EvidenceStream(StubTokenizer(), small_cfg(**kw),
                       web_episodes=[web_episode(i) for i in range(8)])
    b = EvidenceStream(StubTokenizer(), small_cfg(**kw),
                       web_episodes=[web_episode(i) for i in range(8)])
    assert [a.is_web(i) for i in range(50)] == [b.is_web(i) for i in range(50)]


def test_web_share_without_episodes_is_rejected():
    with pytest.raises(ValueError, match="no web episodes"):
        EvidenceStream(StubTokenizer(), small_cfg(web_share=0.3))


def test_an_episode_with_no_questions_is_skipped_not_retried():
    empty = {"episode_id": "web-empty", "world": {"domain": "scrubbed_web"},
             "documents": [{"text": "a document with nothing asked of it"}],
             "questions": []}
    stream = EvidenceStream(StubTokenizer(), small_cfg(web_share=1.0),
                            web_episodes=[empty, web_episode(1)])
    # Index 0 lands on the empty episode and must resolve, not recurse away.
    ex = stream.example(0)
    assert ex.answer_ids


# ---- clamping and the collator contract ----


def test_long_questions_are_clamped_to_the_configured_bound():
    stream = make_stream(max_question_tokens=3, max_answer_tokens=2)
    for i in range(6):
        ex = stream.example(i)
        assert len(ex.question_ids) <= 3
        assert len(ex.answer_ids) <= 2


def test_collated_batch_supervises_only_the_answer():
    tok = StubTokenizer()
    cfg = small_cfg()
    stream = EvidenceStream(tok, cfg)
    collator = EvidenceCollator(tok, cfg.bank_size, cfg.chunk_len, TINY.max_seq_len)
    batch = collator([stream.example(i) for i in range(4)])
    assert batch.input_ids.shape[0] == 4
    assert batch.evidence_ids.shape == (4, BANK, CHUNK)
    supervised = (batch.targets != IGNORE_INDEX).sum(dim=1)
    assert int(supervised.min()) >= 1
    # Nothing before the answer marker is supervised.
    for row in range(4):
        first = int((batch.targets[row] != IGNORE_INDEX).nonzero()[0])
        assert first >= len(stream.example(row).question_ids)


def test_batches_are_the_configured_width():
    tok = StubTokenizer()
    cfg = small_cfg()
    stream = EvidenceStream(tok, cfg)
    collator = EvidenceCollator(tok, cfg.bank_size, cfg.chunk_len, TINY.max_seq_len)
    it = stream.batches(3, collator, start=0)
    for _ in range(3):
        assert next(it).input_ids.shape[0] == 3


# ---- prefetch ----


def test_prefetch_yields_exactly_what_the_direct_iterator_yields():
    tok = StubTokenizer()
    cfg = small_cfg()
    collator = EvidenceCollator(tok, cfg.bank_size, cfg.chunk_len, TINY.max_seq_len)
    plain = EvidenceStream(StubTokenizer(), cfg).batches(2, collator, prefetch=0)
    threaded = EvidenceStream(StubTokenizer(), cfg).batches(2, collator, prefetch=4)
    for _ in range(6):
        a, b = next(plain), next(threaded)
        assert torch.equal(a.input_ids, b.input_ids)
        assert torch.equal(a.targets, b.targets)
        assert torch.equal(a.evidence_ids, b.evidence_ids)


def test_prefetch_depth_comes_from_the_config():
    tok = StubTokenizer()
    cfg = small_cfg(prefetch=0)
    collator = EvidenceCollator(tok, cfg.bank_size, cfg.chunk_len, TINY.max_seq_len)
    stream = EvidenceStream(tok, cfg)
    it = stream.batches(2, collator)
    assert next(it).input_ids.shape[0] == 2


def test_a_producer_error_reaches_the_consumer():
    from src.train.evidence_stream import _prefetched

    def blows_up():
        yield 1
        raise RuntimeError("bank build failed")

    it = _prefetched(blows_up(), 2)
    assert next(it) == 1
    with pytest.raises(RuntimeError, match="bank build failed"):
        next(it)


def test_prefetch_terminates_on_a_finite_source():
    from src.train.evidence_stream import _prefetched

    assert list(_prefetched(iter([1, 2, 3]), 2)) == [1, 2, 3]


def test_closing_the_consumer_stops_the_producer_thread():
    """A producer left running into interpreter shutdown aborts the process.

    That is not a tidiness point. The CLI's --dry-run takes a fixed number of
    batches and returns, and bootstrap4.sh reads its exit code to decide
    whether the evidence lane may run at all, so a producer still inside a
    torch op at teardown costs the lane.
    """
    import itertools
    import threading
    import time

    def endless():
        for i in itertools.count():
            yield i

    from src.train.evidence_stream import _prefetched

    before = {t.name for t in threading.enumerate()}
    it = _prefetched(endless(), 2)
    assert next(it) == 0
    assert any(t.name == "evidence-prefetch" for t in threading.enumerate())
    it.close()
    deadline = time.time() + 10
    while time.time() < deadline:
        if not any(t.name == "evidence-prefetch" for t in threading.enumerate()):
            break
        time.sleep(0.05)
    assert not any(t.name == "evidence-prefetch" for t in threading.enumerate())
    assert {t.name for t in threading.enumerate()} <= before | {"evidence-prefetch"}


def test_closing_a_stream_batch_iterator_stops_its_thread():
    import threading
    import time

    tok = StubTokenizer()
    cfg = small_cfg(prefetch=2)
    collator = EvidenceCollator(tok, cfg.bank_size, cfg.chunk_len, TINY.max_seq_len)
    it = EvidenceStream(tok, cfg).batches(2, collator)
    next(it)
    it.close()
    deadline = time.time() + 10
    while time.time() < deadline:
        if not any(t.name == "evidence-prefetch" for t in threading.enumerate()):
            break
        time.sleep(0.05)
    assert not any(t.name == "evidence-prefetch" for t in threading.enumerate())


# ---- config plumbing ----


def test_config_from_yaml_rejects_unknown_keys():
    with pytest.raises(ValueError, match="unknown data config keys"):
        config_from_yaml({"bank_size": 8, "banck_mode": "oracle"})


def test_config_from_yaml_accepts_the_shipped_shape():
    cfg = config_from_yaml({"bank_size": 256, "chunk_len": 128,
                            "bank_mode": "oracle", "pool_chunks": 4096,
                            "web_share": 0.25, "seed": 1234})
    assert cfg.bank_size == 256
    assert cfg.web_share == 0.25


def test_web_share_out_of_range_is_rejected():
    with pytest.raises(ValueError, match="web_share"):
        StreamConfig(web_share=1.5)


def test_pool_offset_separates_the_two_streams():
    assert POOL_OFFSET != 0


def test_load_web_episodes_reads_jsonl(tmp_path):
    path = tmp_path / "episodes.jsonl"
    with open(path, "w") as fh:
        for i in range(3):
            fh.write(json.dumps(web_episode(i)) + "\n")
    got = load_web_episodes(str(path))
    assert len(got) == 3
    assert got[0]["world"]["domain"] == "scrubbed_web"


def test_load_web_episodes_rejects_a_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_web_episodes(str(tmp_path / "nope.jsonl"))


def test_load_web_episodes_rejects_an_empty_file(tmp_path):
    path = tmp_path / "empty.jsonl"
    path.write_text("\n")
    with pytest.raises(ValueError, match="is empty"):
        load_web_episodes(str(path))


def test_load_web_episodes_returns_nothing_for_no_path():
    assert load_web_episodes(None) == []


# ---- the command line ----


def tiny_config(tmp_path, **overrides) -> str:
    """A config that instantiates the real model at the fixture's tiny size."""
    cfg = {
        "model": {
            "vocab_size": TINY.vocab_size, "d_model": TINY.d_model,
            "n_layers": TINY.n_layers, "n_heads": TINY.n_heads,
            "d_ff": TINY.d_ff, "max_seq_len": TINY.max_seq_len,
            "d_enc": TINY.d_enc, "enc_layers": TINY.enc_layers,
            "enc_heads": TINY.enc_heads, "enc_d_ff": TINY.enc_d_ff,
            "chunk_len": CHUNK, "xattn_every": TINY.xattn_every,
            "xattn_n_kv_heads": TINY.xattn_n_kv_heads, "max_chunks": TINY.max_chunks,
        },
        "data": {"bank_size": BANK, "chunk_len": CHUNK, "pool_chunks": 64,
                 "pool_episodes": 2, "questions_per_episode": 3,
                 "max_question_tokens": 12, "max_answer_tokens": 4},
        "optimizer": {"lr": 1e-3, "weight_decay": 0.0},
        "schedule": {"warmup_steps": 1, "max_steps": 2, "min_lr_ratio": 0.1},
        "train": {"batch_size": 2, "grad_accum_steps": 1, "grad_clip": 1.0,
                  "seed": 5, "log_interval": 1, "ckpt_interval": 2},
    }
    for section, values in overrides.items():
        cfg[section].update(values)
    import yaml
    path = tmp_path / "cfg.yaml"
    with open(path, "w") as fh:
        yaml.safe_dump(cfg, fh)
    return str(path)


class _StubTok(StubTokenizer):
    """StubTokenizer with the vocab_size attribute the CLI checks."""


def _patch_tokenizer(monkeypatch):
    monkeypatch.setattr(evidence_cli, "load_tokenizer",
                        lambda path: _StubTok(TINY.vocab_size))


def test_cli_dry_run_builds_batches_and_exits(tmp_path, monkeypatch, capsys):
    _patch_tokenizer(monkeypatch)
    cfg = tiny_config(tmp_path)
    rc = evidence_cli.main(["--config", cfg, "--tokenizer", "unused",
                            "--out", str(tmp_path / "run"), "--dry-run", "2"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "DRY_RUN_OK" in out
    assert "bank report" in out
    assert not (tmp_path / "run" / "latest.pt").exists()


def test_cli_trains_and_writes_a_resumable_run_directory(tmp_path, monkeypatch):
    _patch_tokenizer(monkeypatch)
    cfg = tiny_config(tmp_path)
    out = tmp_path / "run"
    assert evidence_cli.main(["--config", cfg, "--tokenizer", "unused",
                              "--out", str(out)]) == 0
    assert (out / "latest.pt").exists()
    assert (out / "ckpt-0000002.pt").exists()
    records = [json.loads(line) for line in open(out / "loss.jsonl")]
    assert [r["step"] for r in records] == [1, 2]
    assert all(r["answer_tokens"] > 0 for r in records)
    assert all(r["evidence_tokens"] > 0 for r in records)
    assert all(0.0 <= r["gold_rate"] <= 1.0 for r in records)


def test_cli_resume_continues_the_step_count_and_the_token_totals(tmp_path, monkeypatch):
    _patch_tokenizer(monkeypatch)
    out = tmp_path / "run"
    first = tiny_config(tmp_path)
    evidence_cli.main(["--config", first, "--tokenizer", "unused", "--out", str(out)])
    before = [json.loads(line) for line in open(out / "loss.jsonl")][-1]

    second = tiny_config(tmp_path, schedule={"max_steps": 4})
    evidence_cli.main(["--config", second, "--tokenizer", "unused",
                       "--out", str(out), "--resume"])
    records = [json.loads(line) for line in open(out / "loss.jsonl")]
    assert [r["step"] for r in records] == [1, 2, 3, 4]
    assert records[-1]["answer_tokens_total"] > before["answer_tokens_total"]


def test_cli_rejects_a_bank_larger_than_max_chunks(tmp_path, monkeypatch):
    _patch_tokenizer(monkeypatch)
    cfg = tiny_config(tmp_path, data={"bank_size": TINY.max_chunks + 1})
    with pytest.raises(SystemExit, match="exceeds model.max_chunks"):
        evidence_cli.main(["--config", cfg, "--tokenizer", "unused",
                           "--out", str(tmp_path / "run"), "--dry-run", "1"])


def test_cli_rejects_a_chunk_len_mismatch(tmp_path, monkeypatch):
    _patch_tokenizer(monkeypatch)
    cfg = tiny_config(tmp_path, data={"chunk_len": CHUNK * 2})
    with pytest.raises(SystemExit, match="does not match"):
        evidence_cli.main(["--config", cfg, "--tokenizer", "unused",
                           "--out", str(tmp_path / "run"), "--dry-run", "1"])


def test_cli_rejects_a_vocab_mismatch(tmp_path, monkeypatch):
    monkeypatch.setattr(evidence_cli, "load_tokenizer", lambda path: _StubTok(64))
    cfg = tiny_config(tmp_path)
    with pytest.raises(SystemExit, match="does not match the tokenizer"):
        evidence_cli.main(["--config", cfg, "--tokenizer", "unused",
                           "--out", str(tmp_path / "run"), "--dry-run", "1"])


def test_cli_requires_web_episodes_when_the_share_is_positive(tmp_path, monkeypatch):
    _patch_tokenizer(monkeypatch)
    cfg = tiny_config(tmp_path, data={"web_share": 0.5})
    with pytest.raises(SystemExit, match="--web-episodes was not given"):
        evidence_cli.main(["--config", cfg, "--tokenizer", "unused",
                           "--out", str(tmp_path / "run"), "--dry-run", "1"])


def test_cli_reads_a_web_episode_file(tmp_path, monkeypatch, capsys):
    _patch_tokenizer(monkeypatch)
    path = tmp_path / "web.jsonl"
    with open(path, "w") as fh:
        for i in range(4):
            fh.write(json.dumps(web_episode(i)) + "\n")
    cfg = tiny_config(tmp_path, data={"web_share": 1.0})
    rc = evidence_cli.main(["--config", cfg, "--tokenizer", "unused",
                            "--out", str(tmp_path / "run"),
                            "--web-episodes", str(path), "--dry-run", "2"])
    assert rc == 0
    assert "DRY_RUN_OK" in capsys.readouterr().out
