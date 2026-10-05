"""The runner and the report, end to end, with a scripted backend in place of vLLM."""

import json
import os
import time

import pytest

from src.pilot import report as rp
from src.pilot.items import file_sha, load_items
from src.pilot.runner import (gen_path, popqa_path, read_jsonl, repair_tail,
                              run_generation, run_popqa, select_items)
from src.pilot.vllm_model import Generation, ModelSpec


class ScriptedBackend:
    """Answers correctly on the oracle pages and with a fixed wrong number elsewhere."""

    def __init__(self, name, kind, items, oracle_right=True):
        self.spec = ModelSpec(name, f"fake/{name}", kind,
                              (False, True) if kind == "instruct" else (False,))
        self.thinking = False
        self.calls = 0
        self.by_prompt = {}
        for it in items:
            for c, p in it["prompts"].items():
                self.by_prompt[p] = (it, c)
        self.oracle_right = oracle_right

    def set_thinking(self, on):
        self.thinking = on

    def decode_params(self):
        return {"mode": "fake"}

    def generate(self, prompts):
        self.calls += 1
        out = []
        for p in prompts:
            it, c = self.by_prompt[p]
            if c == "oracle" and self.oracle_right:
                ans = it["answer"]
            elif it["answer_kind"] == "names":
                wrong = [x for x in it["candidates"]
                         if x.lower() not in it["answer"].lower()]
                ans = wrong[0] if wrong else "nothing"
            else:
                ans = str(int(it["answer"]) + 1)
            text = f" {ans}\n" if self.spec.kind == "base" else f"Answer: {ans}"
            out.append(Generation(text, text, len(p) // 4, n_answer_tokens=3))
        return out

    def loglik(self, pairs):
        # The gold option is cheap per token; everything else is dear.
        return [(1.0 * len(c.split()), len(c.split())) if c.strip() == "GOLD"
                else (3.0 * len(c.split()), len(c.split())) for _, c in pairs]


@pytest.fixture()
def records_dir(tmp_path):
    return str(tmp_path / "records")


def test_select_items_caps_each_cell(smoke_items_path):
    items = load_items(smoke_items_path)
    sel = select_items(items, 1)
    cells = [(it["family"], it["level"]) for it in sel]
    assert len(cells) == len(set(cells))


def test_generation_records_resume_and_grade(smoke_items_path, records_dir):
    os.makedirs(records_dir)
    items = load_items(smoke_items_path)
    sha = file_sha(smoke_items_path)
    be = ScriptedBackend("fake-base", "base", items)
    st = run_generation(be, False, items[:5], ("closed_book", "oracle"),
                        records_dir, sha, None, batch_size=4)
    assert st["todo"] == 10
    st = run_generation(be, False, items, ("closed_book", "oracle"),
                        records_dir, sha, None, batch_size=4)
    assert st["skipped"] == 10 and st["todo"] == 2 * len(items) - 10
    recs = read_jsonl(gen_path(records_dir, "fake-base", False))
    assert len(recs) == 2 * len(items)
    for r in recs:
        assert r["correct"] == (r["condition"] == "oracle")
        assert r["items_sha"] == sha
        for field in ("model", "thinking", "condition", "item_id", "family",
                      "level", "floor", "prompt_hash", "raw", "parsed",
                      "correct", "hedge", "n_prompt_tokens", "n_answer_tokens"):
            assert field in r


def test_a_torn_last_line_is_cut_before_appending(tmp_path):
    p = tmp_path / "x.jsonl"
    p.write_text('{"a": 1}\n{"a": 2')
    assert repair_tail(str(p)) == len('{"a": 2')
    assert read_jsonl(str(p)) == [{"a": 1}]


def _popqa_file(tmp_path):
    items = []
    for i in range(8):
        opts = ["x y z", "GOLD", "w", "v u"]
        items.append({"item_id": f"popqa-{i}", "question": f"q{i}?",
                      "options": opts, "gold_index": 1, "gold": "GOLD",
                      "prop": "p", "s_pop": i, "quartile": 1 + i % 4,
                      "floor": 0.25})
    path = tmp_path / "popqa.jsonl"
    path.write_text("".join(json.dumps(it) + "\n" for it in items))
    return str(path), items


def _full_run(items_path, popqa_file, popqa_items, records_dir, oracle_right=True):
    os.makedirs(records_dir, exist_ok=True)
    items = load_items(items_path)
    sha = file_sha(items_path)
    for name, kind in (("lfm2.5-350m-base", "base"), ("qwen3-0.6b-base", "base"),
                       ("qwen3-1.7b-base", "base")):
        be = ScriptedBackend(name, kind, items, oracle_right=oracle_right)
        run_generation(be, False, items, rp_conditions(), records_dir, sha, None)
        run_popqa(be, popqa_items, records_dir, file_sha(popqa_file), None)


def rp_conditions():
    from src.pilot.items import CONDITIONS
    return CONDITIONS


def test_report_reaches_go_on_a_reader_that_uses_the_pages(
        smoke_items_path, tmp_path, records_dir, monkeypatch):
    # The smoke set has one or two items per cell, where no Wilson upper
    # bound can sit within 0.03 of a floor, so the validity slack is opened
    # here to exercise the rest of the decision. The rule itself is tested
    # on its own below.
    monkeypatch.setattr(rp, "VALIDITY_SLACK", 1.0)
    pfile, pitems = _popqa_file(tmp_path)
    _full_run(smoke_items_path, pfile, pitems, records_dir)
    time.sleep(0.01)
    rep = rp.build(smoke_items_path, pfile, records_dir)
    assert rep["canary"]["strict_correct"] == 0
    assert rep["decision"]["validity"]["passed"]
    go = rep["decision"]["go"]["lfm2.5-350m-base"]
    assert go["passes"] and go["popqa_acc"] == 1.0
    assert rep["decision"]["verdict"].startswith("GO: both")
    md = rp.render_md(rep)
    assert "Rule 1, validity" in md


def test_report_falls_back_when_no_reader_uses_the_pages(
        smoke_items_path, tmp_path, records_dir, monkeypatch):
    monkeypatch.setattr(rp, "VALIDITY_SLACK", 1.0)
    pfile, pitems = _popqa_file(tmp_path)
    _full_run(smoke_items_path, pfile, pitems, records_dir, oracle_right=False)
    rep = rp.build(smoke_items_path, pfile, records_dir)
    assert rep["decision"]["verdict"].startswith("FAIL")


def test_report_says_invalid_when_validity_fails(smoke_items_path, tmp_path,
                                                 records_dir):
    pfile, pitems = _popqa_file(tmp_path)
    _full_run(smoke_items_path, pfile, pitems, records_dir)
    rep = rp.build(smoke_items_path, pfile, records_dir)
    assert rep["decision"]["verdict"].startswith("INVALID")


def test_report_refuses_while_a_run_holds_the_lock(smoke_items_path, tmp_path,
                                                   records_dir):
    pfile, pitems = _popqa_file(tmp_path)
    _full_run(smoke_items_path, pfile, pitems, records_dir)
    open(os.path.join(records_dir, "RUNNING.lock"), "w").write("{}")
    with pytest.raises(rp.Refusal):
        rp.build(smoke_items_path, pfile, records_dir)


def test_report_refuses_records_newer_than_itself(smoke_items_path, tmp_path,
                                                  records_dir):
    pfile, pitems = _popqa_file(tmp_path)
    _full_run(smoke_items_path, pfile, pitems, records_dir)
    p = gen_path(records_dir, "lfm2.5-350m-base", False)
    future = time.time() + 3600
    os.utime(p, (future, future))
    with pytest.raises(rp.Refusal, match="newer"):
        rp.build(smoke_items_path, pfile, records_dir)


def test_report_refuses_records_older_than_the_items(smoke_items_path, tmp_path,
                                                     records_dir):
    pfile, pitems = _popqa_file(tmp_path)
    _full_run(smoke_items_path, pfile, pitems, records_dir)
    p = gen_path(records_dir, "qwen3-0.6b-base", False)
    past = os.path.getmtime(smoke_items_path) - 3600
    os.utime(p, (past, past))
    with pytest.raises(rp.Refusal, match="older"):
        rp.build(smoke_items_path, pfile, records_dir)


def test_report_refuses_records_from_another_item_file(smoke_items_path, tmp_path,
                                                       records_dir):
    pfile, pitems = _popqa_file(tmp_path)
    _full_run(smoke_items_path, pfile, pitems, records_dir)
    p = gen_path(records_dir, "qwen3-0.6b-base", False)
    rows = read_jsonl(p)
    rows[0]["items_sha"] = "0" * 64
    with open(p, "w") as fh:
        fh.write("".join(json.dumps(r) + "\n" for r in rows))
    with pytest.raises(rp.Refusal, match="another item file"):
        rp.build(smoke_items_path, pfile, records_dir)


def test_validity_rule_fails_when_closed_book_beats_its_floor():
    cells = {("m", False, "refuniverse", 1, "closed_book"): {
        "model": "m", "thinking": False, "cell": "refuniverse/L1",
        "condition": "closed_book", "n": 100, "k": 1, "acc": 0.01,
        "wilson_hi": 0.0545, "floor": 0.0099, "p_at_or_above_floor": 0.63}}
    v = rp.rule_validity(cells)
    assert not v["passed"] and len(v["failures"]) == 1
    cells[("m", False, "refuniverse", 1, "closed_book")].update(k=0, acc=0.0,
                                                                 wilson_hi=0.037)
    assert rp.rule_validity(cells)["passed"]


def test_binomial_tail():
    assert abs(rp.binom_upper_p(1, 100, 0.01) - (1 - 0.99 ** 100)) < 1e-12
    assert rp.binom_upper_p(0, 10, 0.5) == 1.0
