"""The project's current favoured theory, written down so rows can argue with it.

A Pareto-optimal row that agrees with what we already believe is a nice
confirmation. A Pareto-optimal row that *disagrees* is the one worth
promoting, because it is cheap evidence against a claim the programme is
currently spending money on. That only works if the claims are explicit, so
they live here as predicates rather than in a paragraph somewhere.

Each claim answers one question about a record: does this row contradict me?
The three answers are "contradicts", "consistent", and "n/a" -- the last when
the row simply lacks the numbers to say. Thresholds are stated in the claim,
not hidden in the caller.

Editing this file is expected. When a claim is overturned, change it here and
say so in the run's ``belief_changed`` field.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .schema import get_path

CONTRADICTS = "contradicts"
CONSISTENT = "consistent"
NOT_APPLICABLE = "n/a"

# Families whose task is arithmetic or multi-step execution over a retrieved
# rule, as opposed to reading a stated rule off a page. The distinction is
# the whole content of claim T3.
EXECUTION_FAMILIES = frozenset({
    "rlarith", "rlexec", "rlexec2", "rlproc", "rlrevise", "rlprocrev",
})

# The task families inside those runs that genuinely require executing a
# retrieved rule. skill_procedure is deliberately absent: a share of its
# items are no-ops whose answer is a number copied out of the question, so a
# run can score on it without computing anything.
ARITHMETIC_DOMAINS = frozenset({"skill_binary_op", "skill_units"})

# The knowledge probes are four-way, so chance is 0.25; the battery flags
# leakage above 0.3332, which is the upper bound of the chance interval it
# computes.
PROBE_LEAKAGE_THRESHOLD = 0.3332


@dataclass(frozen=True)
class Claim:
    key: str
    statement: str
    falsified_by: str
    check: Callable[[dict[str, Any]], tuple[str, str]]

    def evaluate(self, row: dict[str, Any]) -> tuple[str, str]:
        return self.check(row)


def _m(row: dict[str, Any], name: str) -> Any:
    return get_path(row, f"metrics.{name}")


def _check_reading_needs_natural_text(row: dict[str, Any]) -> tuple[str, str]:
    natural = get_path(row, "data_mixture.natural")
    reading = _m(row, "reading")
    if natural is None or reading is None:
        return NOT_APPLICABLE, "no natural-text share or no reading score"
    if natural > 0.0:
        return NOT_APPLICABLE, "run had natural text in its mixture"
    if reading > 0.05:
        return CONTRADICTS, (
            f"trained on no natural text yet reads at {reading:.3f}")
    return CONSISTENT, f"no natural text, reading {reading:.3f}"


def _check_evidence_dependence(row: dict[str, Any]) -> tuple[str, str]:
    reasoning = _m(row, "reasoning")
    dependency = _m(row, "retrieval_dependency")
    if reasoning is None or dependency is None:
        return NOT_APPLICABLE, "needs both reasoning and retrieval dependency"
    if reasoning < 0.5:
        return NOT_APPLICABLE, "task accuracy too low to say where it came from"
    if dependency <= 0.05:
        return CONTRADICTS, (
            f"scores {reasoning:.3f} but only {dependency:+.3f} of it depends "
            "on the evidence, so it is answering from weights")
    return CONSISTENT, f"dependency {dependency:+.3f} at accuracy {reasoning:.3f}"


def _check_execution_is_unlearned(row: dict[str, Any]) -> tuple[str, str]:
    family = (row.get("family") or "").lower()
    if family not in EXECUTION_FAMILIES:
        return NOT_APPLICABLE, "not an arithmetic or execution family"
    reasoning = _m(row, "reasoning")
    if reasoning is None:
        return NOT_APPLICABLE, "no task accuracy recorded"
    if reasoning > 0.05:
        domains = (row.get("detail") or {}).get("per_domain") or {}
        arithmetic = {name: block["accuracy"] for name, block in domains.items()
                      if name in ARITHMETIC_DOMAINS
                      and block.get("accuracy") is not None}
        if arithmetic and max(arithmetic.values()) <= 0.05:
            return CONSISTENT, (
                f"{family} pools to {reasoning:.3f}, but every arithmetic "
                "family in it is at zero (" + ", ".join(
                    f"{k} {v:.3f}" for k, v in sorted(arithmetic.items()))
                + "); the pooled score comes from elsewhere")
        return CONTRADICTS, (
            f"{family} reached {reasoning:.3f}; every prior attempt at "
            "arithmetic over retrieved rules ended at 0.000")
    return CONSISTENT, f"{family} ended at {reasoning:.3f}"


def _check_rl_is_the_lever(row: dict[str, Any]) -> tuple[str, str]:
    reasoning = _m(row, "reasoning")
    objective = (row.get("objective") or "").lower()
    if reasoning is None:
        return NOT_APPLICABLE, "no task accuracy recorded"
    is_rl = "grpo" in objective or "verifier" in objective or "rl" == objective[:2]
    if reasoning >= 0.8 and not is_rl:
        return CONTRADICTS, (
            f"reached {reasoning:.3f} without RL against a verifier "
            f"(objective: {row.get('objective')!r})")
    return CONSISTENT, "high scores came from the RL lever, or scores are modest"


def _check_small_is_enough(row: dict[str, Any]) -> tuple[str, str]:
    params = get_path(row, "arch.params_total")
    if params is None:
        return NOT_APPLICABLE, "no parameter count"
    if params > 500e6:
        return CONTRADICTS, (
            f"{params/1e6:.0f}M parameters; the thesis is a small "
            "fact-starved reasoner, so a frontier that needs this size "
            "argues against it")
    return CONSISTENT, f"{params/1e6:.0f}M parameters"


def _check_knowledge_stays_outside(row: dict[str, Any]) -> tuple[str, str]:
    probe = _m(row, "closed_book_probe")
    if probe is None:
        return NOT_APPLICABLE, "no closed-book probe"
    if probe > PROBE_LEAKAGE_THRESHOLD:
        return CONTRADICTS, (
            f"closed-book probe {probe:.3f} is above the {PROBE_LEAKAGE_THRESHOLD} "
            "leakage threshold, so knowledge is sitting in the weights")
    return CONSISTENT, f"closed-book probe {probe:.3f} is at chance"


CLAIMS: tuple[Claim, ...] = (
    Claim(
        key="T1-reading-needs-natural-text",
        statement=(
            "Pretraining with no natural text produces a model that cannot "
            "read natural text, at this scale."),
        falsified_by=(
            "a run whose mixture has natural share 0 and whose naturalized "
            "reading exceeds 0.05"),
        check=_check_reading_needs_natural_text,
    ),
    Claim(
        key="T2-evidence-dependence-is-real",
        statement=(
            "When a fact-starved reader scores well on a task it was given "
            "evidence for, the score comes from the evidence."),
        falsified_by=(
            "a run at accuracy 0.5 or better whose retrieval dependency is "
            "0.05 or less"),
        check=_check_evidence_dependence,
    ),
    Claim(
        key="T3-execution-over-rules-is-unlearned",
        statement=(
            "Arithmetic and multi-step execution over a retrieved rule cannot "
            "be taught by the methods tried so far: calculators, executors, "
            "complete rule cards, revision loops and partial credit all ended "
            "at 0.000."),
        falsified_by=(
            "an arithmetic or execution family run scoring above 0.05 on "
            "skill_binary_op or skill_units. A pooled score above 0.05 is not "
            "enough on its own: skill_procedure contains no-op items whose "
            "answer is copied out of the question."),
        check=_check_execution_is_unlearned,
    ),
    Claim(
        key="T4-rl-against-verifiers-is-the-lever",
        statement=(
            "The large accuracy gains come from RL against programmatic "
            "verifiers with retrieval inside the rollout, not from pretraining "
            "changes."),
        falsified_by=(
            "a run reaching 0.8 or better without an RL-against-verifier "
            "objective"),
        check=_check_rl_is_the_lever,
    ),
    Claim(
        key="T5-small-is-enough",
        statement=(
            "The target is a small fact-starved reasoner; capability should "
            "not require scale."),
        falsified_by=(
            "a frontier row that only earns its place at over 500M parameters"),
        check=_check_small_is_enough,
    ),
    Claim(
        key="T6-knowledge-stays-outside-the-weights",
        statement=(
            "Knowledge belongs in the retrieval fabric; the closed-book probe "
            "should sit at chance."),
        falsified_by=(
            f"a closed-book probe above {PROBE_LEAKAGE_THRESHOLD}"),
        check=_check_knowledge_stays_outside,
    ),
)


def evaluate(row: dict[str, Any]) -> list[dict[str, str]]:
    """Every claim's verdict on one row."""
    out = []
    for claim in CLAIMS:
        verdict, reason = claim.evaluate(row)
        out.append({
            "key": claim.key,
            "verdict": verdict,
            "reason": reason,
            "statement": claim.statement,
        })
    return out


def contradictions(row: dict[str, Any]) -> list[dict[str, str]]:
    """Only the claims this row argues against."""
    return [v for v in evaluate(row) if v["verdict"] == CONTRADICTS]
