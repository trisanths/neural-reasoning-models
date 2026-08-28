"""The non-dominated set over any pair (or tuple) of objectives.

A row dominates another when it is at least as good on every objective and
strictly better on one. The frontier is the set of rows nothing dominates.
Rows missing a value for any chosen objective are set aside rather than
treated as zero, and the caller is told how many were set aside, because
"this row has no measured inference cost" and "this row is free" are very
different claims.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Sequence

from . import theory
from .schema import get_path

MAX = "max"
MIN = "min"


@dataclass(frozen=True)
class Objective:
    name: str
    path: str
    direction: str
    label: str

    def value(self, row: dict[str, Any]) -> float | None:
        raw = get_path(row, self.path)
        if raw is None or isinstance(raw, bool) or not isinstance(raw, (int, float)):
            return None
        return float(raw)

    def score(self, row: dict[str, Any]) -> float | None:
        """Value rewritten so that higher is always better."""
        raw = self.value(row)
        if raw is None:
            return None
        return raw if self.direction == MAX else -raw


OBJECTIVES: dict[str, Objective] = {
    obj.name: obj
    for obj in (
        Objective("retrieval_dependency", "metrics.retrieval_dependency", MAX,
                  "retrieval dependency (correct minus wrong evidence)"),
        Objective("evidence_lift", "metrics.evidence_lift", MAX,
                  "evidence lift (correct minus no evidence)"),
        Objective("reasoning", "metrics.reasoning", MAX,
                  "task accuracy with evidence"),
        Objective("reading", "metrics.reading", MAX,
                  "naturalized reading, contains-answer"),
        Objective("novel_system", "metrics.novel_system_acquisition", MAX,
                  "accuracy on a system invented after training"),
        Objective("ood", "metrics.ood_generalization", MAX,
                  "out-of-distribution accuracy"),
        Objective("closed_book_probe", "metrics.closed_book_probe", MIN,
                  "closed-book knowledge probe (lower is the goal)"),
        Objective("params", "arch.params_total", MIN, "parameters"),
        Objective("inference_flops", "compute.inference_flops_per_answer", MIN,
                  "inference FLOPs per answer"),
        Objective("decode_flops", "compute.decode_flops_per_answer", MIN,
                  "decode FLOPs per answer"),
        Objective("train_flops", "compute.train_flops", MIN, "training FLOPs"),
        Objective("latency", "compute.latency_s_per_answer", MIN,
                  "measured seconds per answer"),
    )
}


def resolve(name: str) -> Objective:
    if name not in OBJECTIVES:
        raise KeyError(
            f"unknown objective {name!r}; known: {', '.join(sorted(OBJECTIVES))}")
    return OBJECTIVES[name]


def dominates(a: Sequence[float], b: Sequence[float]) -> bool:
    """True when a is at least as good everywhere and better somewhere."""
    return all(x >= y for x, y in zip(a, b)) and any(x > y for x, y in zip(a, b))


def frontier(rows: Iterable[dict[str, Any]],
             objectives: Sequence[Objective]) -> dict[str, Any]:
    """Split rows into the frontier, the dominated, and the unscorable."""
    scored: list[tuple[dict[str, Any], tuple[float, ...]]] = []
    skipped: list[dict[str, Any]] = []
    for row in rows:
        scores = [obj.score(row) for obj in objectives]
        if any(s is None for s in scores):
            missing = [obj.name for obj, s in zip(objectives, scores) if s is None]
            skipped.append({"run_id": row.get("run_id"), "missing": missing})
            continue
        scored.append((row, tuple(scores)))  # type: ignore[arg-type]

    front, dominated = [], []
    for row, scores in scored:
        beaten_by = next(
            (other["run_id"] for other, other_scores in scored
             if other is not row and dominates(other_scores, scores)),
            None,
        )
        if beaten_by is None:
            front.append(row)
        else:
            dominated.append({"run_id": row.get("run_id"),
                              "dominated_by": beaten_by})

    # Sort the frontier along the first objective so it reads as a curve.
    front.sort(key=lambda r: objectives[0].value(r) or 0.0,
               reverse=objectives[0].direction == MAX)
    return {
        "objectives": [obj.name for obj in objectives],
        "frontier": front,
        "dominated": dominated,
        "skipped": skipped,
        "n_scored": len(scored),
    }


def frontier_with_flags(rows: Iterable[dict[str, Any]],
                        objectives: Sequence[Objective]) -> dict[str, Any]:
    """The frontier, with each row's argument against the favoured theory.

    A frontier row carrying contradictions is the one to promote: it is both
    undominated on the axes we care about and evidence against something the
    programme currently believes.
    """
    result = frontier(rows, objectives)
    flagged = []
    for row in result["frontier"]:
        against = theory.contradictions(row)
        flagged.append({
            "row": row,
            "values": {obj.name: obj.value(row) for obj in objectives},
            "contradicts": against,
            "promote": bool(against),
        })
    result["frontier_flagged"] = flagged
    result["n_promote"] = sum(1 for f in flagged if f["promote"])
    # If `reasoning` is on an axis, the frontier is only a real comparison
    # when every row was graded on the same suite. Say which ones are mixed
    # rather than letting the picture imply they are commensurable.
    if any(obj.name == "reasoning" for obj in objectives):
        suites = sorted({row.get("reasoning_suite") or "unrecorded"
                         for row in result["frontier"]})
        result["frontier_suites"] = suites
        result["suites_mixed"] = len(suites) > 1
    else:
        result["frontier_suites"] = []
        result["suites_mixed"] = False
    return result
