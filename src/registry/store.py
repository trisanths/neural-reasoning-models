"""Append-only JSONL of runs, with a sqlite index in front of it.

The JSONL file is the record of truth and is never rewritten. Correcting a
row means appending a new revision of it; the old line stays where it is, so
a frontier printed last week can still be reproduced from the file. The
sqlite database is a derived read cache with one row per run_id holding its
highest revision, and can be deleted and rebuilt at any time.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Iterator

from .schema import SCHEMA_VERSION, RunRecord, ValidationError

RUNS_FILE = "runs.jsonl"
INDEX_FILE = "index.db"

# Columns lifted out of the JSON blob so the CLI can filter and sort in SQL.
_INDEX_COLUMNS: list[tuple[str, str, str]] = [
    # (column, sql type, dotted path in the record)
    ("created", "TEXT", "created"),
    ("git_commit", "TEXT", "git_commit"),
    ("lane", "TEXT", "lane"),
    ("branch", "TEXT", "branch"),
    ("family", "TEXT", "family"),
    ("reasoning_suite", "TEXT", "reasoning_suite"),
    ("objective", "TEXT", "objective"),
    ("variant", "TEXT", "arch.variant"),
    ("params_total", "INTEGER", "arch.params_total"),
    ("params_non_embedding", "INTEGER", "arch.params_non_embedding"),
    ("train_tokens", "REAL", "compute.train_tokens"),
    ("train_flops", "REAL", "compute.train_flops"),
    ("inference_flops_per_answer", "REAL", "compute.inference_flops_per_answer"),
    ("decode_flops_per_answer", "REAL", "compute.decode_flops_per_answer"),
    ("latency_s_per_answer", "REAL", "compute.latency_s_per_answer"),
    ("gpu_utilization", "REAL", "compute.gpu_utilization"),
    ("reading", "REAL", "metrics.reading"),
    ("reasoning", "REAL", "metrics.reasoning"),
    ("retrieval_dependency", "REAL", "metrics.retrieval_dependency"),
    ("closed_book_probe", "REAL", "metrics.closed_book_probe"),
    ("novel_system_acquisition", "REAL", "metrics.novel_system_acquisition"),
    ("ood_generalization", "REAL", "metrics.ood_generalization"),
    ("belief_changed", "TEXT", "belief_changed"),
]


def _dig(blob: dict[str, Any], dotted: str) -> Any:
    node: Any = blob
    for part in dotted.split("."):
        if not isinstance(node, dict):
            return None
        node = node.get(part)
    return node


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Store:
    """The experiment database.

    >>> store = Store("registry")
    >>> store.append(record)          # writes a line, updates the index
    >>> rows = store.latest()         # one dict per run_id, newest revision
    """

    def __init__(self, root: str | os.PathLike[str]):
        self.root = Path(root)
        self.runs_path = self.root / RUNS_FILE
        self.index_path = self.root / INDEX_FILE

    # -- writing ---------------------------------------------------------

    def append(self, record: RunRecord | dict[str, Any],
               *, reindex: bool = True) -> dict[str, Any]:
        """Validate a record and append it as one JSONL line.

        Appending a run_id that already exists is not an error: it stores a
        new revision. The index then reports the new one and the file keeps
        both.
        """
        if isinstance(record, dict):
            record = RunRecord.from_dict(record)
        record.validate()
        blob = record.to_dict()
        blob["schema_version"] = blob.get("schema_version") or SCHEMA_VERSION
        blob["recorded_at"] = blob.get("recorded_at") or _now()
        blob["revision"] = self._next_revision(blob["run_id"])

        self.root.mkdir(parents=True, exist_ok=True)
        line = json.dumps(blob, sort_keys=True, ensure_ascii=False)
        if "\n" in line:
            raise ValidationError("record serialised to more than one line")
        # O_APPEND makes a single short write atomic against other appenders.
        fd = os.open(self.runs_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
        try:
            os.write(fd, (line + "\n").encode("utf-8"))
        finally:
            os.close(fd)
        if reindex:
            self.rebuild_index()
        return blob

    def extend(self, records) -> list[dict[str, Any]]:
        """Append many records, indexing once at the end."""
        written = [self.append(r, reindex=False) for r in records]
        self.rebuild_index()
        return written

    def _next_revision(self, run_id: str) -> int:
        highest = -1
        for blob in self.read_all():
            if blob.get("run_id") == run_id:
                highest = max(highest, int(blob.get("revision", 0)))
        return highest + 1

    # -- reading ---------------------------------------------------------

    def read_all(self) -> Iterator[dict[str, Any]]:
        """Every line ever appended, in file order."""
        if not self.runs_path.exists():
            return iter(())
        return self._iter_lines()

    def _iter_lines(self) -> Iterator[dict[str, Any]]:
        with open(self.runs_path, "r", encoding="utf-8") as handle:
            for number, line in enumerate(handle, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    blob = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValidationError(
                        f"{self.runs_path}:{number} is not valid JSON: {exc}"
                    ) from exc
                blob["_line"] = number
                yield blob

    def latest(self) -> list[dict[str, Any]]:
        """One record per run_id: the highest revision, then the last line."""
        best: dict[str, dict[str, Any]] = {}
        for blob in self.read_all():
            run_id = blob.get("run_id")
            current = best.get(run_id)
            if current is None:
                best[run_id] = blob
                continue
            if (int(blob.get("revision", 0)), blob["_line"]) >= (
                    int(current.get("revision", 0)), current["_line"]):
                best[run_id] = blob
        return sorted(best.values(), key=lambda b: b["_line"])

    def get(self, run_id: str) -> dict[str, Any] | None:
        for blob in self.latest():
            if blob["run_id"] == run_id:
                return blob
        return None

    # -- index -----------------------------------------------------------

    def rebuild_index(self) -> int:
        """Drop and rebuild the sqlite index from the JSONL. Returns row count."""
        self.root.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.index_path)
        try:
            cols = ", ".join(f"{name} {sqltype}" for name, sqltype, _ in _INDEX_COLUMNS)
            conn.execute("DROP TABLE IF EXISTS runs")
            conn.execute(
                "CREATE TABLE runs ("
                "run_id TEXT PRIMARY KEY, revision INTEGER, line INTEGER, "
                f"{cols}, json TEXT)"
            )
            rows = self.latest()
            conn.executemany(
                "INSERT INTO runs VALUES (%s)" % ",".join(
                    ["?"] * (4 + len(_INDEX_COLUMNS))),
                [
                    (
                        blob["run_id"],
                        int(blob.get("revision", 0)),
                        blob["_line"],
                        *[_dig(blob, path) for _, _, path in _INDEX_COLUMNS],
                        json.dumps(
                            {k: v for k, v in blob.items() if k != "_line"},
                            sort_keys=True),
                    )
                    for blob in rows
                ],
            )
            conn.execute("CREATE INDEX idx_runs_lane ON runs(lane)")
            conn.execute("CREATE INDEX idx_runs_family ON runs(family)")
            conn.commit()
            return len(rows)
        finally:
            conn.close()

    def query(self, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
        """Run read-only SQL against the index."""
        if not self.index_path.exists():
            self.rebuild_index()
        conn = sqlite3.connect(self.index_path)
        conn.row_factory = sqlite3.Row
        try:
            return list(conn.execute(sql, params))
        finally:
            conn.close()
