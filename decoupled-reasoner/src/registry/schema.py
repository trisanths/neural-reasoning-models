"""One row per experiment run.

The schema is deliberately flat in its leaves: every metric is a float in
[0, 1] (or None), every cost is a positive number (or None), and every label
is a short string from a closed set. A number that was never measured is
None. There is no sentinel value that means "roughly" or "about" -- if a
number is in the store, an artefact on disk produced it or a documented
formula in flops.py derived it from one.
"""

from __future__ import annotations

import dataclasses
import math
import re
from dataclasses import dataclass, field
from typing import Any

SCHEMA_VERSION = 1

# How a run relates to the current favoured theory. Exploit pushes on a lever
# already known to work, explore opens a direction with no prior, falsify
# tries to kill a claim the project is currently leaning on.
LANES = ("exploit", "explore", "falsify")

RUN_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

# Metric names whose natural range is [0, 1].
_UNIT_METRICS = (
    "reading",
    "reasoning",
    "acc_correct_evidence",
    "acc_wrong_evidence",
    "acc_no_evidence",
    "closed_book_probe",
    "novel_system_acquisition",
    "ood_generalization",
)


class ValidationError(ValueError):
    """A record cannot be stored as written."""


def _num(value: Any, path: str, *, minimum: float | None = None,
         maximum: float | None = None) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"{path} must be a number or null, got {value!r}")
    value = float(value)
    if math.isnan(value) or math.isinf(value):
        raise ValidationError(f"{path} must be finite, got {value!r}")
    if minimum is not None and value < minimum:
        raise ValidationError(f"{path} must be >= {minimum}, got {value}")
    if maximum is not None and value > maximum:
        raise ValidationError(f"{path} must be <= {maximum}, got {value}")
    return value


@dataclass
class Arch:
    """What was trained, and how big it is.

    ``params_total`` counts every trainable weight including both embedding
    matrices; ``params_non_embedding`` drops them, and is the count that
    enters the FLOPs formulas.
    """

    description: str = ""
    variant: str | None = None  # dense | looped | xattn | none (no model)
    params_total: int | None = None
    params_non_embedding: int | None = None
    d_model: int | None = None
    n_layers: int | None = None
    n_heads: int | None = None
    d_ff: int | None = None
    vocab_size: int | None = None
    max_seq_len: int | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        for name in ("params_total", "params_non_embedding", "d_model",
                     "n_layers", "n_heads", "d_ff", "vocab_size",
                     "max_seq_len"):
            _num(getattr(self, name), f"arch.{name}", minimum=0)
        if (self.params_total is not None
                and self.params_non_embedding is not None
                and self.params_non_embedding > self.params_total):
            raise ValidationError(
                "arch.params_non_embedding exceeds arch.params_total")


@dataclass
class Compute:
    """What the run cost, in the units the frontier is drawn on.

    ``train_flops`` and the two inference numbers are derived, not metered;
    flops.py holds the formulas and names its assumptions. ``latency`` and
    ``gpu_utilization`` are only ever measured -- there is no formula for
    them, so they stay None unless an artefact recorded them.
    """

    train_tokens: float | None = None
    train_flops: float | None = None
    # Full forward cost of one answer: context tokens plus generated tokens.
    # Requires a measured context length, so it is often None.
    inference_flops_per_answer: float | None = None
    # Decode-only cost of one answer. Needs just the generated-token count,
    # so it is available for every run that logged an eval, and is a strict
    # lower bound on inference_flops_per_answer.
    decode_flops_per_answer: float | None = None
    latency_s_per_answer: float | None = None
    gpu_utilization: float | None = None  # fraction in [0, 1]
    gpu_type: str | None = None
    gpu_count: int | None = None
    wall_clock_s: float | None = None

    def validate(self) -> None:
        for name in ("train_tokens", "train_flops",
                     "inference_flops_per_answer", "decode_flops_per_answer",
                     "latency_s_per_answer", "wall_clock_s"):
            _num(getattr(self, name), f"compute.{name}", minimum=0)
        _num(self.gpu_utilization, "compute.gpu_utilization",
             minimum=0.0, maximum=1.0)
        _num(self.gpu_count, "compute.gpu_count", minimum=0)
        lower = self.decode_flops_per_answer
        upper = self.inference_flops_per_answer
        if lower is not None and upper is not None and lower > upper:
            raise ValidationError(
                "compute.decode_flops_per_answer exceeds "
                "compute.inference_flops_per_answer")


@dataclass
class Metrics:
    """The six axes the programme is actually steering on, plus their parts.

    reading                  natural-text comprehension, contains-answer
    reasoning                task accuracy with the evidence it is entitled to
    retrieval_dependency     acc(correct evidence) - acc(wrong evidence).
                             The strict test: wrong evidence is as long, as
                             well formed and as retrievable as right evidence,
                             so only reading tells them apart.
    evidence_lift            acc(correct evidence) - acc(no evidence).
                             The weak test: a model can score here by noticing
                             that it has documents at all.
    closed_book_probe        knowledge-probe accuracy with nothing retrieved;
                             LOW is the goal, this is a leakage measure
    novel_system_acquisition accuracy on a system invented after training,
                             given its page
    ood_generalization       accuracy on a distribution the run never trained on

    ``retrieval_dependency`` and ``evidence_lift`` are derived from the three
    accuracies below them when those are present, and cannot disagree with
    them.
    """

    reading: float | None = None
    reasoning: float | None = None
    retrieval_dependency: float | None = None
    evidence_lift: float | None = None
    acc_correct_evidence: float | None = None
    acc_wrong_evidence: float | None = None
    acc_no_evidence: float | None = None
    closed_book_probe: float | None = None
    novel_system_acquisition: float | None = None
    ood_generalization: float | None = None

    def validate(self) -> None:
        for name in _UNIT_METRICS:
            _num(getattr(self, name), f"metrics.{name}",
                 minimum=0.0, maximum=1.0)
        for name in ("retrieval_dependency", "evidence_lift"):
            _num(getattr(self, name), f"metrics.{name}",
                 minimum=-1.0, maximum=1.0)
        self._reconcile("retrieval_dependency", self.acc_wrong_evidence,
                        "acc_correct_evidence - acc_wrong_evidence")
        self._reconcile("evidence_lift", self.acc_no_evidence,
                        "acc_correct_evidence - acc_no_evidence")

    def _reconcile(self, field_name: str, subtrahend: float | None,
                   description: str) -> None:
        if self.acc_correct_evidence is None or subtrahend is None:
            return
        implied = self.acc_correct_evidence - subtrahend
        current = getattr(self, field_name)
        if current is None:
            setattr(self, field_name, implied)
        elif abs(current - implied) > 1e-6:
            raise ValidationError(
                "metrics.%s %.6f disagrees with %s = %.6f"
                % (field_name, current, description, implied))


@dataclass
class RunRecord:
    """A single experiment run.

    ``belief_changed`` is required and free text. "none" is a legitimate and
    common answer; an empty string is not, because a run whose effect on the
    project's beliefs was never written down is a run nobody can read later.
    """

    run_id: str
    lane: str
    belief_changed: str
    created: str | None = None       # ISO 8601, when the run was produced
    git_commit: str | None = None
    branch: str | None = None        # charter branch / data regime letter
    family: str | None = None        # killtest, curve, rlvr, rlskill, ...
    # Which evaluation produced metrics.reasoning. Two runs are only
    # comparable on that axis if this matches: a pretraining run graded on
    # held-out worlds and an RL run graded on its own episode pool are
    # answering different questions, and putting them on one frontier without
    # saying so invites exactly the wrong conclusion.
    reasoning_suite: str | None = None
    objective: str = ""              # what the loss actually optimised
    data_mixture: dict[str, Any] = field(default_factory=dict)
    arch: Arch = field(default_factory=Arch)
    compute: Compute = field(default_factory=Compute)
    metrics: Metrics = field(default_factory=Metrics)
    sources: list[str] = field(default_factory=list)
    # Everything the artefacts recorded that has no fixed column: per-grading
    # breakdowns, retrieval rates, stop reasons. Never read by the frontier,
    # always kept so a row can be argued with.
    detail: dict[str, Any] = field(default_factory=dict)
    notes: str = ""
    schema_version: int = SCHEMA_VERSION
    recorded_at: str | None = None   # set by the store on append

    def validate(self) -> "RunRecord":
        if not isinstance(self.run_id, str) or not RUN_ID_RE.match(self.run_id):
            raise ValidationError(f"run_id {self.run_id!r} is not a valid id")
        if self.lane not in LANES:
            raise ValidationError(
                f"lane {self.lane!r} must be one of {LANES}")
        if not isinstance(self.belief_changed, str) or not self.belief_changed.strip():
            raise ValidationError(
                "belief_changed is required; write 'none' if the run moved nothing")
        if not isinstance(self.data_mixture, dict):
            raise ValidationError("data_mixture must be a mapping")
        if not isinstance(self.sources, list):
            raise ValidationError("sources must be a list of paths or URIs")
        if not isinstance(self.detail, dict):
            raise ValidationError("detail must be a mapping")
        self.arch.validate()
        self.compute.validate()
        self.metrics.validate()
        return self

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "RunRecord":
        raw = dict(raw)
        arch = Arch(**raw.pop("arch", {}) or {})
        compute = Compute(**raw.pop("compute", {}) or {})
        metrics = Metrics(**raw.pop("metrics", {}) or {})
        known = {f.name for f in dataclasses.fields(cls)}
        unknown = set(raw) - known
        if unknown:
            raise ValidationError(f"unknown fields: {sorted(unknown)}")
        return cls(arch=arch, compute=compute, metrics=metrics, **raw)


def get_path(record: RunRecord | dict[str, Any], dotted: str) -> Any:
    """Read ``metrics.reasoning`` style paths off a record or its dict form."""
    node: Any = record if isinstance(record, dict) else record.to_dict()
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node
