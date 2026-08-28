import json

import pytest

from src.registry.schema import Metrics, RunRecord, ValidationError
from src.registry.store import Store


def rec(run_id="r1", **kwargs) -> RunRecord:
    base = dict(run_id=run_id, lane="explore", belief_changed="none")
    base.update(kwargs)
    return RunRecord(**base)


def test_append_writes_one_line_per_record(tmp_path):
    store = Store(tmp_path)
    store.append(rec("a"))
    store.append(rec("b"))
    lines = store.runs_path.read_text().strip().split("\n")
    assert len(lines) == 2
    assert {json.loads(line)["run_id"] for line in lines} == {"a", "b"}


def test_append_stamps_revision_and_time(tmp_path):
    store = Store(tmp_path)
    blob = store.append(rec("a"))
    assert blob["revision"] == 0
    assert blob["recorded_at"].endswith("Z")


def test_re_appending_a_run_id_creates_a_revision_and_keeps_the_old_line(tmp_path):
    store = Store(tmp_path)
    store.append(rec("a", metrics=Metrics(reasoning=0.1)))
    store.append(rec("a", metrics=Metrics(reasoning=0.9)))
    assert len(store.runs_path.read_text().strip().split("\n")) == 2
    latest = store.latest()
    assert len(latest) == 1
    assert latest[0]["revision"] == 1
    assert latest[0]["metrics"]["reasoning"] == 0.9
    # the original is still on disk
    first = list(store.read_all())[0]
    assert first["metrics"]["reasoning"] == 0.1


def test_the_store_never_rewrites_earlier_lines(tmp_path):
    store = Store(tmp_path)
    store.append(rec("a"))
    before = store.runs_path.read_text()
    store.append(rec("b"))
    assert store.runs_path.read_text().startswith(before)


def test_invalid_records_are_refused_before_they_touch_the_file(tmp_path):
    store = Store(tmp_path)
    with pytest.raises(ValidationError):
        store.append(rec("a", lane="nonsense"))
    assert not store.runs_path.exists()


def test_index_is_rebuildable_and_derived(tmp_path):
    store = Store(tmp_path)
    store.extend([rec("a", family="curve", metrics=Metrics(reading=0.2)),
                  rec("b", family="rlvr", metrics=Metrics(reading=0.9))])
    store.index_path.unlink()
    assert store.rebuild_index() == 2
    rows = store.query("SELECT run_id, reading FROM runs ORDER BY reading DESC")
    assert [(r["run_id"], r["reading"]) for r in rows] == [("b", 0.9), ("a", 0.2)]


def test_index_holds_only_the_latest_revision(tmp_path):
    store = Store(tmp_path)
    store.append(rec("a", metrics=Metrics(reasoning=0.1)))
    store.append(rec("a", metrics=Metrics(reasoning=0.9)))
    rows = store.query("SELECT run_id, reasoning FROM runs")
    assert len(rows) == 1
    assert rows[0]["reasoning"] == 0.9


def test_get_returns_none_for_an_unknown_run(tmp_path):
    store = Store(tmp_path)
    store.append(rec("a"))
    assert store.get("a")["run_id"] == "a"
    assert store.get("zzz") is None


def test_a_corrupt_line_is_reported_with_its_number(tmp_path):
    store = Store(tmp_path)
    store.append(rec("a"))
    with open(store.runs_path, "a") as handle:
        handle.write("not json\n")
    with pytest.raises(ValidationError, match=":2"):
        store.latest()


def test_blank_lines_are_ignored(tmp_path):
    store = Store(tmp_path)
    store.append(rec("a"))
    with open(store.runs_path, "a") as handle:
        handle.write("\n\n")
    assert len(store.latest()) == 1


def test_a_revision_replaces_the_whole_row_rather_than_patching_it(tmp_path):
    store = Store(tmp_path)
    store.append(rec("a", family="curve", metrics=Metrics(reading=0.2,
                                                          reasoning=0.8)))
    store.append(rec("a", metrics=Metrics(reasoning=0.9)))
    latest = store.get("a")
    assert latest["metrics"]["reasoning"] == 0.9
    # fields not passed again are gone, not carried forward
    assert latest["metrics"]["reading"] is None
    assert latest["family"] is None
