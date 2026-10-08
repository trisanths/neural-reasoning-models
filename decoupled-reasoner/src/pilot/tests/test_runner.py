"""The runner and the report, end to end, with a scripted backend in place of vLLM."""

import json
import os
import random
import time

import pytest

from src.pilot import report as rp
from src.pilot.items import file_sha, load_items
from src.pilot.runner import (gen_path, popqa_path, read_jsonl, repair_tail,
                              run_generation, run_popqa, select_items)
from src.pilot.vllm_model import MODELS, Generation, ModelSpec

REAL_ITEMS = os.environ.get("PILOT_ITEMS", "/mnt/nvme/pilot/items/items_v2.jsonl")


class ScriptedBackend:
    """Answers correctly on the oracle pages and with a fixed wrong number
    elsewhere; with leak, also correctly closed book."""

    def __init__(self, name, kind, items, oracle_right=True, leak=False,
                 thinking_modes=None):
        self.spec = ModelSpec(name, f"fake/{name}", kind, thinking_modes or (
            (False, True) if kind == "instruct" else (False,)))
        self.thinking = False
        self.calls = 0
        self.by_prompt = {}
        for it in items:
            for c, p in it["prompts"].items():
                self.by_prompt[p] = (it, c)
        self.oracle_right = oracle_right
        self.leak = leak

    def set_thinking(self, on):
        self.thinking = on

    def decode_params(self):
        return {"mode": "fake"}

    def generate(self, prompts):
        self.calls += 1
        out = []
        for p in prompts:
            it, c = self.by_prompt[p]
            if (c == "oracle" and self.oracle_right) or (
                    c == "closed_book" and self.leak):
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
    by_id = {it["item_id"]: it for it in items}
    for r in recs:
        assert r["correct"] == (r["condition"] == "oracle")
        assert r["items_sha"] == sha
        assert r["floor"] == by_id[r["item_id"]]["floors"][r["condition"]]
        for field in ("model", "thinking", "condition", "item_id", "family",
                      "level", "floor", "prompt_hash", "raw", "parsed",
                      "correct", "hedge", "answered", "n_prompt_tokens",
                      "n_answer_tokens", "git_head", "git_dirty", "grade_sha"):
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
                      "masked_question": "q X?",
                      "options": opts, "gold_index": 1, "gold": "GOLD",
                      "prop": "p", "s_pop": i, "quartile": 1 + i % 4,
                      "floor": 0.25})
    path = tmp_path / "popqa.jsonl"
    path.write_text("".join(json.dumps(it) + "\n" for it in items))
    return str(path), items


def _full_run(items_path, popqa_file, popqa_items, records_dir,
              oracle_right=True, leak=False, skip=()):
    """Every configuration of the plan, through the real runner functions."""
    os.makedirs(records_dir, exist_ok=True)
    items = load_items(items_path)
    sha = file_sha(items_path)
    for spec in MODELS.values():
        be = ScriptedBackend(spec.name, spec.kind, items,
                             oracle_right=oracle_right, leak=leak,
                             thinking_modes=spec.thinking_modes)
        for thinking in spec.thinking_modes:
            if (spec.name, thinking) in skip:
                continue
            run_generation(be, thinking, items, rp_conditions(), records_dir,
                           sha, None)
        if (spec.name, "popqa") not in skip:
            run_popqa(be, popqa_items, records_dir, file_sha(popqa_file), None)


def rp_conditions():
    from src.pilot.items import CONDITIONS
    return CONDITIONS


def test_report_reaches_go_on_a_reader_that_uses_the_pages(
        smoke_items_path, tmp_path, records_dir):
    pfile, pitems = _popqa_file(tmp_path)
    _full_run(smoke_items_path, pfile, pitems, records_dir)
    time.sleep(0.01)
    rep = rp.build(smoke_items_path, pfile, records_dir)
    assert rep["canary"]["strict_correct"] == 0
    assert rep["decision"]["validity"]["passed"]
    assert rep["decision"]["validity"]["cells_checked"] == 12 * 16 * 2
    go = rep["decision"]["go"]["lfm2.5-350m-base"]
    assert go["passes"] and go["popqa_acc"] == 1.0
    assert go["popqa_acc_masked"] == 1.0
    assert not go["qualifying_cells_all_lookup"]
    assert rep["decision"]["verdict"].startswith("GO: both")
    assert "qualifies on" in rep["decision"]["verdict"]
    md = rp.render_md(rep)
    assert "Rule 1, validity" in md and "As first registered" in md


def test_report_falls_back_when_no_reader_uses_the_pages(
        smoke_items_path, tmp_path, records_dir):
    pfile, pitems = _popqa_file(tmp_path)
    _full_run(smoke_items_path, pfile, pitems, records_dir, oracle_right=False)
    rep = rp.build(smoke_items_path, pfile, records_dir)
    assert rep["decision"]["verdict"].startswith("FAIL")


def test_report_says_invalid_when_a_reader_answers_closed_book(
        smoke_items_path, tmp_path, records_dir, monkeypatch):
    # At one or two items per smoke cell no count can be significant after
    # a 384-way Holm correction, so alpha is opened here to exercise the
    # path; the rule's power at full size is tested on its own below.
    monkeypatch.setattr(rp, "VALIDITY_ALPHA", 1.0)
    pfile, pitems = _popqa_file(tmp_path)
    _full_run(smoke_items_path, pfile, pitems, records_dir, leak=True)
    rep = rp.build(smoke_items_path, pfile, records_dir)
    assert rep["decision"]["verdict"].startswith("INVALID")
    assert all(f["condition"] == "closed_book"
               for f in rep["decision"]["validity"]["failures"])


def test_report_is_not_reached_while_any_configuration_is_missing(
        smoke_items_path, tmp_path, records_dir):
    pfile, pitems = _popqa_file(tmp_path)
    _full_run(smoke_items_path, pfile, pitems, records_dir,
              skip={("qwen3-8b", True)})
    rep = rp.build(smoke_items_path, pfile, records_dir)
    v = rep["decision"]["verdict"]
    assert v.startswith("not reached") and "qwen3-8b|think1" in v


def test_report_is_not_reached_without_every_popqa_record(
        smoke_items_path, tmp_path, records_dir):
    pfile, pitems = _popqa_file(tmp_path)
    _full_run(smoke_items_path, pfile, pitems, records_dir)
    p = popqa_path(records_dir, "lfm2.5-350m-base")
    rows = read_jsonl(p)[:3]
    with open(p, "w") as fh:
        fh.write("".join(json.dumps(r) + "\n" for r in rows))
    rep = rp.build(smoke_items_path, pfile, records_dir)
    assert rep["decision"]["verdict"].startswith("not reached")
    assert "lfm2.5-350m-base|popqa" in rep["decision"]["verdict"]
    assert not rep["decision"]["go"]["lfm2.5-350m-base"]["popqa_ok"]


def test_report_regrades_the_stored_text(smoke_items_path, tmp_path,
                                         records_dir):
    pfile, pitems = _popqa_file(tmp_path)
    _full_run(smoke_items_path, pfile, pitems, records_dir)
    p = gen_path(records_dir, "qwen3-0.6b-base", False)
    rows = read_jsonl(p)
    flipped = 0
    for r in rows:
        if r["condition"] == "oracle" and r["correct"]:
            r["correct"] = False
            flipped += 1
    with open(p, "w") as fh:
        fh.write("".join(json.dumps(r) + "\n" for r in rows))
    rep = rp.build(smoke_items_path, pfile, records_dir)
    assert rep["regrade"]["correct"] == flipped > 0
    assert rep["decision"]["go"]["qwen3-0.6b-base"]["cells_ok"]


def test_report_refuses_records_from_two_commits(smoke_items_path, tmp_path,
                                                 records_dir):
    pfile, pitems = _popqa_file(tmp_path)
    _full_run(smoke_items_path, pfile, pitems, records_dir)
    p = gen_path(records_dir, "qwen3-0.6b-base", False)
    rows = read_jsonl(p)
    rows[0]["git_head"] = "f" * 40
    with open(p, "w") as fh:
        fh.write("".join(json.dumps(r) + "\n" for r in rows))
    with pytest.raises(rp.Refusal, match="more than one commit"):
        rp.build(smoke_items_path, pfile, records_dir)
    rep = rp.build(smoke_items_path, pfile, records_dir,
                   allow_mixed_commits=True)
    assert len(rep["commits"]["qwen3-0.6b-base|think0"]) == 2


@pytest.mark.parametrize("lock", ["RUNNING.lock", "RUNNING.qwen3-8b.lock"])
def test_report_refuses_while_a_run_holds_a_lock(smoke_items_path, tmp_path,
                                                 records_dir, lock):
    pfile, pitems = _popqa_file(tmp_path)
    _full_run(smoke_items_path, pfile, pitems, records_dir)
    open(os.path.join(records_dir, lock), "w").write("{}")
    with pytest.raises(rp.Refusal, match="still writing"):
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


def test_records_older_than_an_identical_item_file_only_warn(
        smoke_items_path, tmp_path, records_dir):
    pfile, pitems = _popqa_file(tmp_path)
    _full_run(smoke_items_path, pfile, pitems, records_dir)
    p = gen_path(records_dir, "qwen3-0.6b-base", False)
    past = os.path.getmtime(smoke_items_path) - 3600
    os.utime(p, (past, past))
    rep = rp.build(smoke_items_path, pfile, records_dir)
    assert any("older" in w for w in rep["freshness"]["warnings"])


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


def test_failed_children_are_listed(smoke_items_path, tmp_path, records_dir):
    pfile, pitems = _popqa_file(tmp_path)
    _full_run(smoke_items_path, pfile, pitems, records_dir,
              skip={("qwen3-4b", False), ("qwen3-4b", True),
                    ("qwen3-4b", "popqa")})
    with open(os.path.join(records_dir, "run_log.jsonl"), "w") as fh:
        fh.write(json.dumps({"model": "qwen3-4b", "exit": 1}) + "\n")
    rep = rp.build(smoke_items_path, pfile, records_dir)
    assert "qwen3-4b" in rep["failed_models"]
    assert "exited non-zero" in rep["decision"]["verdict"]


# --------------------------------------------------------------------------
# rule 1 on its own, at the sizes of the real item set
# --------------------------------------------------------------------------
def _cells(spec, rng, rate_of):
    """Closed-book and blank cells for 12 configurations. spec maps a cell
    name to its per-item floors; rate_of(cell, floor) is the reader's
    per-item probability of a correct answer."""
    cells = {}
    for cfg in range(12):
        for name, floors in spec.items():
            for cond in ("closed_book", "blank"):
                k = sum(rng.random() < rate_of(name, f) for f in floors)
                n = len(floors)
                lo, hi = rp.wilson(k, n)
                cells[(f"m{cfg}", False, name, None, cond)] = {
                    "model": f"m{cfg}", "thinking": False, "cell": name,
                    "condition": cond, "n": n, "k": k, "acc": k / n,
                    "wilson_hi": hi, "floor": sum(floors) / n,
                    "item_floors": floors,
                    "p_at_or_above_floor": rp.poisson_binomial_upper(k, floors)}
    return cells


SIZES = {**{f"refuniverse/L{lv}": [0.0095] * 100 for lv in range(1, 9)},
         **{f"algebra/L{lv}": [0.0] * 100 + [0.3] * 10 for lv in (2, 3, 4, 5)},
         "binary_op": [0.021] * 50, "threshold_rule": [0.0] * 50,
         "substitution_rule": [0.0] * 50, "exception_rule": [0.0] * 50}


def test_rule_1_passes_a_reader_that_gets_everything_wrong():
    v = rp.rule_validity(_cells(SIZES, random.Random(0), lambda c, f: 0.0))
    assert v["passed"] and v["cells_checked"] == 384
    # The rule as first registered fails every 50-item cell at zero correct:
    # the Wilson upper bound of 0/50 is 0.071, above floor + 0.03 for floors
    # of 0.021 (binary_op) and 0 (labels a closed-book reader never sees).
    failing = {f["cell"] for f in v["as_registered"]["failures"]}
    assert failing == {"binary_op", "threshold_rule", "substitution_rule",
                       "exception_rule"}


def test_rule_1_passes_readers_at_their_floors():
    passes = sum(rp.rule_validity(_cells(SIZES, random.Random(s),
                                         lambda c, f: f))["passed"]
                 for s in range(20))
    assert passes >= 19


def test_rule_1_fails_a_leak_in_one_cell():
    def leak(cell, f):
        return 0.25 if cell == "refuniverse/L1" else f
    v = rp.rule_validity(_cells(SIZES, random.Random(1), leak))
    assert not v["passed"]
    assert {f["cell"] for f in v["failures"]} == {"refuniverse/L1"}


def test_holm_and_the_exact_tails():
    assert rp.holm({"a": 0.001, "b": 0.02, "c": 0.06}, 0.05) == {"a", "b"}
    assert rp.holm({"a": 0.001, "b": 0.03, "c": 0.04}, 0.05) == {"a"}
    assert rp.holm({"a": 0.03, "b": 0.04}, 0.05) == set()
    assert abs(rp.poisson_binomial_upper(3, [0.1] * 20)
               - rp.binom_upper_p(3, 20, 0.1)) < 1e-12
    assert rp.poisson_binomial_upper(0, [0.5]) == 1.0
    assert rp.poisson_binomial_upper(1, [0.0] * 5) == 0.0
    assert abs(rp.binom_upper_p(1, 100, 0.01) - (1 - 0.99 ** 100)) < 1e-12


@pytest.mark.skipif(not os.path.exists(REAL_ITEMS),
                    reason="the registered item file lives on the pilot box")
def test_rule_1_on_the_registered_item_file():
    items = load_items(REAL_ITEMS)
    spec: dict = {}
    for it in items:
        name = rp.cell_name(it["family"], it["level"])
        spec.setdefault(name, []).append(it["floors"]["closed_book"])
    assert len(spec) == 16
    assert rp.rule_validity(_cells(spec, random.Random(0),
                                   lambda c, f: 0.0))["passed"]
    passes = sum(rp.rule_validity(_cells(spec, random.Random(s),
                                         lambda c, f: f))["passed"]
                 for s in range(20))
    assert passes >= 19
    v = rp.rule_validity(_cells(spec, random.Random(2),
                                lambda c, f: 0.3 if c == "refuniverse/L5" else f))
    assert not v["passed"]
