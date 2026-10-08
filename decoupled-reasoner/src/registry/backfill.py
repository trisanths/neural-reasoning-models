"""Rebuild the registry from everything this project has already run.

Two kinds of information meet here. Numbers come out of artefacts through
ingest.py and are never typed by hand. Labels -- which lane a run belonged
to, what its objective was, what belief it moved -- are editorial and live in
the tables below, each traceable to a line in PLAN.md, CURVE.md, ARCH.md or
the run's own command.

The backfill is idempotent in the sense that re-running it produces the same
rows; because the store is append-only, running it twice writes a second
revision of each row rather than corrupting the first.
"""

from __future__ import annotations

import datetime as _dt
import json
import re
from pathlib import Path
from typing import Any, Iterable

from . import flops, ingest
from .schema import Arch, Compute, Metrics, RunRecord

# --------------------------------------------------------------------------
# Data mixtures, from the manifests the renderers wrote and from CURVE.md
# --------------------------------------------------------------------------

# Regimes A, B, C and D predate the manifest.json the regime E renderer
# writes, so their shares come from the documents that specify them:
# CURVE.md ("mix natural 0.80 / worldgen 0.15 / procgen 0.05 ... measured
# shares exactly 0.8000/0.1500/0.0500") and PLAN.md (regime D).
STATIC_MIXTURES: dict[str, dict[str, Any]] = {
    "a": {"regime": "A", "natural": 1.0,
          "source": "CURVE.md run matrix, ~/data/regime_a/shards"},
    "b": {"regime": "B", "natural": 0.80, "worldgen": 0.15, "procgen": 0.05,
          "source": "CURVE.md, measured shares 0.8000/0.1500/0.0500"},
    "c": {"regime": "C", "natural": 0.0, "worldgen": 1.0,
          "procgen_warmup_stream": True,
          "source": "CURVE.md run matrix, ~/data/regime_c/flat plus "
                    "proc_warmup_15m.bin"},
    "d": {"regime": "D", "natural": 0.80, "worldgen_retrieval_traces": 0.15,
          "procgen": 0.05, "source": "PLAN.md phase 2, weakened form"},
}


def mixture_for(regime: str, mirror: Path) -> dict[str, Any]:
    """The data mixture for a regime letter, preferring a rendered manifest."""
    regime = regime.lower()
    manifest = mirror / "runs" / "data-manifests" / f"regime_{regime}.json"
    if manifest.exists():
        blob = json.loads(manifest.read_text())
        mix = dict(blob.get("mix") or {})
        mix["regime"] = regime.upper()
        mix["total_tokens_rendered"] = blob.get("total_tokens")
        mix["source"] = str(manifest)
        return mix
    if regime in STATIC_MIXTURES:
        return dict(STATIC_MIXTURES[regime])
    return {"regime": regime.upper(), "source": None}


# --------------------------------------------------------------------------
# Which battery graded which model
# --------------------------------------------------------------------------

# Batteries that carry a `models` or `rows` block name their own models. The
# rest are resolved here, from the checkpoint directory plus the seed
# convention in CURVE.md: 111 is every regime A run, 211 every C run, 311
# every B run, and later seeds are per-run.
BATTERY_ALIASES: dict[str, dict[str, str]] = {
    "runs/killtest/evals/results.json": {
        # run_dir is the model directory itself
        "killtest-a-101": "killtest-a-101", "killtest-a-102": "killtest-a-102",
        "killtest-a-103": "killtest-a-103", "killtest-c-201": "killtest-c-201",
        "killtest-c-202": "killtest-c-202", "killtest-c-203": "killtest-c-203",
    },
    "runs/curve/evals-150m/results150.json": {
        "killtest-a-111": "curve-150m-a", "killtest-c-211": "curve-150m-c",
        "killtest-a-311": "curve-150m-b", "killtest-c-311": "curve-150m-b",
    },
    "runs/curve/evals-350me2/results.json": {
        # d_model 2048 in this battery is the 1300M pair; 1024 is the E line
        "killtest-a-111": "curve-1300m-a", "killtest-c-211": "curve-1300m-c",
        "killtest-a-502": "curve-350me-502", "killtest-c-502": "curve-350me-502",
        "killtest-a-503": "curve-350me-503", "killtest-c-503": "curve-350me-503",
        "killtest-a-601": "curve-350me2-601", "killtest-c-601": "curve-350me2-601",
        "killtest-a-602": "curve-350me2-602", "killtest-c-602": "curve-350me2-602",
        "killtest-a-603": "curve-350me2-603", "killtest-c-603": "curve-350me2-603",
    },
    "runs/curve/evals-350md/battery/results.json": {
        "killtest-a-401": "curve-350md-401", "killtest-c-401": "curve-350md-401",
        "killtest-a-402": "curve-350md-402", "killtest-c-402": "curve-350md-402",
        "killtest-a-403": "curve-350md-403", "killtest-c-403": "curve-350md-403",
    },
}

# Later files win when the same model was graded twice, so put the curated
# reports last.
BATTERY_ORDER = [
    "runs/killtest/evals/results.json",
    "runs/curve/evals-150m/results150.json",
    "runs/curve/evals-350md/battery/results.json",
    "runs/curve/evals-350me2/results.json",
    "runs/curve/evals-350md/results-d.json",
    "runs/curve/evals-e501/results-e501-700m.json",
    "runs/curve/evals-e-repl/results-e-replication.json",
]


def _battery_model_map(path: Path, rel: str) -> dict[str, str]:
    blob = json.loads(path.read_text())
    if isinstance(blob.get("models"), dict):
        return dict(blob["models"])
    if isinstance(blob.get("rows"), list):
        out = {}
        for row in blob["rows"]:
            if row.get("graded_as") and row.get("model"):
                out[row["graded_as"]] = row["model"]
        if out:
            return out
    return dict(BATTERY_ALIASES.get(rel, {}))


def collect_battery_scores(mirror: Path) -> dict[str, dict[str, Any]]:
    """Fold every eval battery into one score per model.

    A checkpoint is graded twice, once with each elicitation, because the
    regime C models only answer in their own trace format. The gate takes the
    better of the two, which is what ``reading`` records here; both are kept
    in ``detail`` so the choice is auditable.
    """
    scores: dict[str, dict[str, Any]] = {}
    for rel in BATTERY_ORDER:
        path = mirror / rel
        if not path.exists():
            continue
        aliases = _battery_model_map(path, rel)
        for graded in ingest.read_eval_battery(path):
            model = aliases.get(graded["name"], graded["name"])
            slot = scores.setdefault(model, {
                "model": model, "gradings": [], "sources": []})
            slot["gradings"].append(graded)
            slot["sources"].append(str(path))

    for slot in scores.values():
        gradings = slot["gradings"]

        def best(metric: str) -> tuple[Any, dict[str, Any] | None]:
            scored = [g for g in gradings if g["metrics"].get(metric) is not None]
            if not scored:
                return None, None
            winner = max(scored, key=lambda g: g["metrics"][metric])
            return winner["metrics"][metric], winner

        reading, reading_from = best("reading")
        reasoning, reasoning_from = best("reasoning")
        probes = [g["metrics"]["closed_book_probe"] for g in gradings
                  if g["metrics"].get("closed_book_probe") is not None]
        last = gradings[-1]

        latency = None
        seconds = last["detail"].get("eval_heldout_s")
        questions = last["detail"].get("heldout_n_questions")
        if seconds and questions:
            # The heldout suite's own wall clock over its own question count,
            # not the whole battery's, which also covers three naturalized
            # passes and the probes.
            latency = float(seconds) / float(questions)

        slot["metrics"] = {
            "reading": reading,
            "reasoning": reasoning,
            "closed_book_probe": max(probes) if probes else None,
        }
        slot["model_config"] = last.get("model_config")
        slot["step"] = last.get("step")
        slot["latency_s_per_answer"] = latency
        slot["detail"] = {
            "elicitations": {g["name"]: g["detail"].get("naturalized_elicitation")
                             for g in gradings},
            "reading_from": reading_from["name"] if reading_from else None,
            "reasoning_from": reasoning_from["name"] if reasoning_from else None,
            "per_grading": {g["name"]: g["metrics"] | g["detail"] for g in gradings},
        }
    return scores


# --------------------------------------------------------------------------
# The charter: lane, objective and belief for each family
# --------------------------------------------------------------------------

_REGIME_FROM_NAME = re.compile(
    r"^(?:killtest|curve)-(?:(?P<size>\d+m)(?P<letter>[a-e]\d?)?)?[-]?(?P<tail>[abc])?")

# The evaluation behind metrics.reasoning, per run family. Rows are only
# comparable on that axis when these match.
SUITE_HELDOUT = "heldout_worlds (eval battery, docs in context or interactive)"
SUITE_RL_WORLDGEN = "rl_episodes:regime_c_heldout_worlds"
SUITE_RL_INVENTED = "rl_episodes:skillacq_invented_systems"
SUITE_RL_SIMPLE = "rl_episodes:skillacq_simple_rule_families"
SUITE_RL_ARITH = "rl_episodes:skillacq_arithmetic"
SUITE_RL_PROC = "rl_episodes:skillacq_procedural"
SUITE_RL_WEB = "rl_episodes:scrubbed_web"
SUITE_NRM = "nrm_bench (real and scrubbed web, three evidence conditions)"
SUITE_RULE_ABLATION = "skillacq_invented_systems, three evidence conditions"

PRETRAIN_OBJECTIVE = "next-token language modelling"
RL_OBJECTIVE = "GRPO against a programmatic verifier, retrieval inside the rollout"


def _run_regime(run_id: str, cmd_text: str | None) -> str | None:
    """Regime letter, read off the run's --data flag where possible."""
    if cmd_text:
        match = re.search(r"--data \S*/regime_([a-z0-9]+)", cmd_text)
        if match:
            return match.group(1).upper()
    match = re.search(r"^killtest-([ac])-", run_id)
    if match:
        return match.group(1).upper()
    # curve-150m-a and curve-350m-b carry the letter after the size; the
    # later lines carry it attached to it, optionally with a variant word:
    # curve-350md-401, curve-350me2-601, curve-350me3loop-711.
    match = re.match(
        r"^curve-\d+m(?P<letter>[a-z])?(?P<digit>\d)?(?:loop)?-(?P<tail>.+)$",
        run_id)
    if match:
        letter = match.group("letter")
        if letter:
            return (letter + (match.group("digit") or "")).upper()
        tail = match.group("tail")
        if tail in ("a", "b", "c"):
            return tail.upper()
    return None


def _mtime_date(paths: Iterable[Path]) -> str | None:
    stamps = [p.stat().st_mtime for p in paths if p.exists()]
    if not stamps:
        return None
    return _dt.datetime.fromtimestamp(
        max(stamps), _dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_cmd(run_dir: Path) -> str | None:
    cmd = run_dir / "cmd.txt"
    return cmd.read_text() if cmd.exists() else None


def _gpu_count(cmd_text: str | None) -> int | None:
    if not cmd_text:
        return None
    match = re.search(r"CUDA_VISIBLE_DEVICES=([0-9,]+)", cmd_text)
    if not match:
        return None
    return len([x for x in match.group(1).split(",") if x])


# Belief statements are the project's own words, from the phase reports.
BELIEF = {
    "killtest-a": (
        "none; the regime A runs are the reference arm the kill test is "
        "measured against"),
    "killtest-c": (
        "killed the strict form. Pretraining purely on synthetic worlds scores "
        "0.000 on naturalized reading on every seed against 0.205 for regime A, "
        "below the 0.6 ratio gate in SPEC.md section 7, while still scoring "
        "0.66 to 0.72 on its own held-out worlds. The model learned the format "
        "and never learned to read."),
    "curve-a": "none; regime A is the reference arm at each size",
    "curve-c": (
        "none beyond the kill test; regime C reproduces its zero reading at "
        "every size, so the failure is not a small-model artefact"),
    "curve-b": (
        "mixing 80 percent natural text with worldgen keeps reading close to "
        "the pure-natural arm, so the trace conventions are not what destroyed "
        "reading in regime C"),
    "curve-d": (
        "the weakened form survives its gate: regime D reads at 0.93 of the "
        "regime A reference while carrying the retrieval trace convention"),
    "curve-e": (
        "adding a QA-trace share on top of natural text moves reading and "
        "held-out reasoning together; the E line is the working pretraining "
        "recipe"),
    "curve-e3": (
        "raising the web-retrieval share to 0.20 and shuffling entity names "
        "tests whether the reader can be pushed off resident knowledge during "
        "pretraining rather than after it"),
    "curve-loop": (
        "a weight-tied looped core buys depth without parameters; whether it "
        "buys reasoning at fixed parameter count is what this run measures"),
    "curve-xattn": (
        "cross-attention over an evidence encoder changes the cost curve of "
        "reading long evidence, so evidence length stops being paid for in "
        "decoder context"),
}


# --------------------------------------------------------------------------
# Builders
# --------------------------------------------------------------------------

def _pretraining_record(run_dir: Path, mirror: Path,
                        battery: dict[str, dict[str, Any]],
                        *, lane: str, family: str, belief: str,
                        gpu_type: str | None,
                        description: str, notes: str = "") -> RunRecord:
    run_id = run_dir.name
    cfg_path = run_dir / "config.yaml"
    cmd_text = _read_cmd(run_dir)
    regime = _run_regime(run_id, cmd_text)

    arch = Arch(description=description)
    compute = Compute(gpu_type=gpu_type, gpu_count=_gpu_count(cmd_text))
    sources = [str(p) for p in (cfg_path, run_dir / "cmd.txt",
                                run_dir / "loss.jsonl") if p.exists()]

    if cfg_path.exists():
        parsed = ingest.read_train_config(cfg_path)
        arch = Arch(description=description, **parsed["arch"])
        if (parsed["model_config"] or {}).get("evidence_mode"):
            arch.variant = "xattn"
        arch.extra = {
            "seed": parsed["seed"],
            "layer_pass_multiplier": parsed["layer_pass_multiplier"],
        }
        if (parsed["model_config"] or {}).get("recurrent"):
            arch.extra["recurrent"] = parsed["model_config"]["recurrent"]
        compute.train_tokens = parsed["compute"]["train_tokens"]
        compute.train_flops = parsed["compute"]["train_flops"]

    scored = battery.get(run_id)
    metrics = Metrics()
    detail: dict[str, Any] = {}
    suite = SUITE_HELDOUT if scored else None
    if scored:
        metrics = Metrics(**scored["metrics"])
        compute.latency_s_per_answer = scored["latency_s_per_answer"]
        sources.extend(scored["sources"])
        detail = scored["detail"]

    mixture = mixture_for(regime, mirror) if regime else {}
    return RunRecord(
        run_id=run_id,
        lane=lane,
        belief_changed=belief,
        created=_mtime_date([run_dir / "loss.jsonl", cfg_path]),
        git_commit=None,  # not recorded by the trainer at the time
        branch=regime,
        family=family,
        reasoning_suite=suite,
        objective=PRETRAIN_OBJECTIVE,
        data_mixture=mixture,
        arch=arch,
        compute=compute,
        metrics=metrics,
        sources=sorted(set(sources)),
        detail=detail,
        notes=notes,
    )


def _rl_record(run_dir: Path, *, lane: str, family: str, belief: str,
               description: str, params_non_embedding: int | None,
               params_total: int | None, base_regime: str | None,
               objective: str, gpu_type: str | None, suite: str | None,
               novel_system: bool, notes: str = "") -> RunRecord:
    run_id = run_dir.name
    facts = ingest.rl_run_facts(run_dir, params_non_embedding=params_non_embedding)
    detail = facts["detail"]
    metrics = Metrics(reasoning=facts["metrics"]["reasoning"])
    if novel_system:
        metrics.novel_system_acquisition = facts["metrics"]["reasoning"]

    compute = Compute(
        wall_clock_s=facts["compute"]["wall_clock_s"],
        latency_s_per_answer=facts["compute"]["latency_s_per_answer"],
        decode_flops_per_answer=facts["compute"]["decode_flops_per_answer"],
        train_tokens=facts["raw"]["train_tokens"],
        gpu_type=gpu_type,
        gpu_count=1,
    )
    # An RL step costs a backward pass over the tokens it trains on plus a
    # forward pass over every token the policy generated to get there. The
    # prompt prefill is not logged, so this is a lower bound and says so.
    update_tokens = facts["raw"]["train_tokens"]
    rollout_tokens = facts["raw"]["generated_tokens"]
    if params_non_embedding and (update_tokens or rollout_tokens):
        compute.train_flops = (
            flops.training_flops(params_non_embedding, update_tokens or 0.0)
            + flops.decode_flops_per_answer(params_non_embedding,
                                            rollout_tokens or 0.0))
        detail["train_flops_is_lower_bound"] = True
        detail["rollout_generated_tokens"] = rollout_tokens
        detail["update_tokens"] = update_tokens

    return RunRecord(
        run_id=run_id,
        lane=lane,
        belief_changed=belief,
        created=_mtime_date([run_dir / "rl.jsonl", run_dir / "eval.jsonl"]),
        branch=base_regime,
        family=family,
        reasoning_suite=suite,
        objective=objective,
        data_mixture={"episodes": "programmatically generated, verifier scored",
                      "base_checkpoint_regime": base_regime},
        arch=Arch(description=description, variant="dense",
                  params_total=params_total,
                  params_non_embedding=params_non_embedding),
        compute=compute,
        metrics=metrics,
        sources=facts["sources"],
        detail=detail,
        notes=notes,
    )


# --------------------------------------------------------------------------
# Run tables
# --------------------------------------------------------------------------

H100 = "NVIDIA H100 80GB SXM"
L40S = "NVIDIA L40S"

# (run directory under the mirror, lane, family, belief key)
PRETRAIN_RUNS: list[tuple[str, str, str, str]] = [
    ("runs/killtest/killtest-a-101", "falsify", "killtest", "killtest-a"),
    ("runs/killtest/killtest-a-102", "falsify", "killtest", "killtest-a"),
    ("runs/killtest/killtest-a-103", "falsify", "killtest", "killtest-a"),
    ("runs/killtest/killtest-c-201", "falsify", "killtest", "killtest-c"),
    ("runs/killtest/killtest-c-202", "falsify", "killtest", "killtest-c"),
    ("runs/killtest/killtest-c-203", "falsify", "killtest", "killtest-c"),
    ("runs/curve/curve-150m-a", "explore", "curve", "curve-a"),
    ("runs/curve/curve-700m-a", "explore", "curve", "curve-a"),
    ("runs/curve/curve-1300m-a", "explore", "curve", "curve-a"),
    ("runs/curve/curve-150m-c", "explore", "curve", "curve-c"),
    ("runs/curve/curve-700m-c", "explore", "curve", "curve-c"),
    ("runs/curve/curve-1300m-c", "explore", "curve", "curve-c"),
    ("runs/curve/curve-150m-b", "explore", "curve", "curve-b"),
    ("runs/curve/curve-350m-b", "explore", "curve", "curve-b"),
    ("runs/curve/curve-350md-401", "explore", "curve", "curve-d"),
    ("runs/curve/curve-350md-402", "explore", "curve", "curve-d"),
    ("runs/curve/curve-350md-403", "explore", "curve", "curve-d"),
    ("runs/curve/curve-350me-501", "explore", "curve", "curve-e"),
    ("runs/curve/curve-350me-502", "explore", "curve", "curve-e"),
    ("runs/curve/curve-350me-503", "explore", "curve", "curve-e"),
    ("runs/curve/curve-350me2-601", "explore", "curve", "curve-e"),
    ("runs/curve/curve-350me2-602", "explore", "curve", "curve-e"),
    ("runs/curve/curve-350me2-603", "explore", "curve", "curve-e"),
    ("runs/curve/curve-350me3-701", "explore", "curve", "curve-e3"),
    ("runs/curve/curve-350me3loop-711", "explore", "arch", "curve-loop"),
    ("runs/curve/curve-350me3loop-712", "explore", "arch", "curve-loop"),
    ("runs/curve/curve-350xattn-731", "explore", "arch", "curve-xattn"),
]

# Every rl-350m-* config trains the same dense 350M policy class: d_model
# 1024, 24 layers, d_ff 2816, vocab 32768. The looped and cross-attention
# variants exist only as curve-350me3loop-* and curve-350xattn-731, and no RL
# launch artefact references them, so the parameter count below is the same
# for every RL run whichever 350M checkpoint initialised it.
RL_POLICY_CONFIG = {"d_model": 1024, "n_layers": 24, "d_ff": 2816,
                    "n_heads": 16, "vocab_size": 32768, "max_seq_len": 4096}

# (run dir, lane, family, base checkpoint or None, belief, novel-system task)
RL_RUNS: list[tuple[str, str, str, str | None, str, bool]] = [
    ("runs/rlvr/rl-350m-a", "exploit", "rlvr", None,
     "RL against the programmatic verifier with retrieval inside the rollout "
     "took held-out accuracy from 0.448 to 0.854 on one L40S in under ten "
     "minutes. This is the cheapest strong lever the project has found.",
     False),
    ("runs/rlvr/rl-350m-b", "exploit", "rlvr", None,
     "The same lever run to 400 steps reaches 0.948, but 80 percent of groups "
     "produced no gradient because every rollout in them scored alike. Group "
     "size, not steps, is the binding constraint.",
     False),
    ("runs/curve/curve-rl-350md401-742", "exploit", "rlblock", "curve-350md-401",
     "The verifier lever transfers to a regime D checkpoint at block scale.",
     False),
    ("runs/curve/curve-rl-350me503-741", "exploit", "rlblock", "curve-350me-503",
     "The verifier lever transfers to a regime E checkpoint at block scale.",
     False),
    ("runs/final/rlskill-curve-350me-503-901", "explore", "rlskill",
     "curve-350me-503",
     "A model can be trained to read a textbook for a system invented after "
     "its training data and apply it, but only to 0.156 from 0.000 at this "
     "budget: the skill exists and is weak.",
     True),
    ("runs/final/rlskill-curve-350md-401-902", "explore", "rlskill",
     "curve-350md-401",
     "Regime D initialisation reaches the same place as regime E on invented "
     "systems, so the pretraining difference does not decide this task.",
     True),
    ("runs/final/rlskill2-e2base-911", "explore", "rlskill2", "curve-350me2-603",
     "A regime E2 base starts higher on invented systems and finishes at the "
     "same 0.11, so the ceiling is not set by the base model.",
     True),
    ("runs/final/rlskill2-fastlr-912", "explore", "rlskill2", "curve-350me-503",
     "Tripling the learning rate does not lift the invented-system ceiling.",
     True),
    ("runs/final/rlskill2-deep-913", "explore", "rlskill2", "curve-350me-503",
     "More retrieval rounds and a longer answer budget do not lift the "
     "invented-system ceiling either.",
     True),
    ("runs/final/rlsimple-503-921", "exploit", "rlsimple", "curve-350me-503",
     "Cut the invented systems down to simple stated-rule families and the "
     "same lever reaches 0.995 from 0.000. Reading a stated rule off a page "
     "is learnable; the failures elsewhere are about executing rules, not "
     "about retrieval.",
     True),
    ("runs/final/rlarith-calc-931", "falsify", "rlarith", None,
     "Handing the policy a calculator through the retrieval channel did not "
     "teach arithmetic over retrieved rules. The pooled 0.156 is entirely "
     "skill_procedure at 0.467; skill_binary_op and skill_units are both at "
     "0.000 over 45 sampled items each, and the skill_procedure items it gets "
     "right are the ones whose answer is a number copied out of the question. "
     "Stopped at 1500 steps.",
     True),
    ("runs/final/rlexec2-942", "falsify", "rlexec2", None,
     "An explicit executor channel did not teach rule execution either; the "
     "policy learned to fill the format and score the shaping terms while "
     "answer accuracy stayed at 0.000.",
     True),
    ("runs/final/rlproc-952", "falsify", "rlproc", "curve-350me-503",
     "Cold-start hyper-parameters on the procedural family left answer "
     "accuracy at 0.000 while reward climbed on the shaping terms alone.",
     True),
    ("runs/final/rlproc-953", "falsify", "rlproc", "curve-350me-503",
     "Adding partial credit to the procedural family did not change the "
     "outcome: reward rises, answers do not.",
     True),
    ("runs/final/rlrevise-961", "falsify", "rlrevise", "curve-350me-503",
     "Executor plus a trained revision loop, the combination Reflexion's "
     "ablation says is the only one that helps, still ended at 0.000 on "
     "arithmetic over retrieved rules.",
     True),
    ("runs/final/rlprocrev-971", "falsify", "rlprocrev", "curve-350me-503",
     "A revision loop on the procedural family with a shortened answer budget "
     "also ended at 0.000. Five distinct interventions have now failed on the "
     "same task shape.",
     True),
    ("runs/rlweb/rlweb-curve-350me-503-801", "explore", "rlweb",
     "curve-350me-503",
     "RL on scrubbed-web episodes barely moves: the policy retrieves and then "
     "does not extract, which is the failure the web demo measured.",
     False),
    ("runs/rlweb/rlweb-curve-350md-401-802", "explore", "rlweb",
     "curve-350md-401",
     "Same result from the regime D base: retrieval happens, extraction does not.",
     False),
    ("runs/rlweb/rlweb-curve-350me2-603-803", "explore", "rlweb",
     "curve-350me2-603",
     "Same result from the regime E2 base.",
     False),
]


RL_FAMILY_SUITE = {
    "rlvr": SUITE_RL_WORLDGEN,
    "rlblock": SUITE_RL_WORLDGEN,
    "rlskill": SUITE_RL_INVENTED,
    "rlskill2": SUITE_RL_INVENTED,
    "rlsimple": SUITE_RL_SIMPLE,
    "rlarith": SUITE_RL_ARITH,
    "rlexec2": SUITE_RL_ARITH,
    "rlproc": SUITE_RL_PROC,
    "rlrevise": SUITE_RL_ARITH,
    "rlprocrev": SUITE_RL_PROC,
    "rlweb": SUITE_RL_WEB,
}


def _describe(model_cfg: dict[str, Any] | None) -> str:
    if not model_cfg:
        return "unrecorded"
    bits = [f"{model_cfg.get('n_layers')}L x {model_cfg.get('d_model')}d"]
    if model_cfg.get("recurrent"):
        rec = model_cfg["recurrent"]
        bits.append(f"weight-tied core looped {rec.get('loops')}x")
    elif model_cfg.get("evidence_mode"):
        bits.append(f"cross-attention over an evidence encoder "
                    f"({model_cfg.get('evidence_mode')})")
    else:
        bits.append("dense decoder")
    return ", ".join(bits)


def build_pretraining_rows(mirror: Path,
                           battery: dict[str, dict[str, Any]]) -> list[RunRecord]:
    rows = []
    for rel, lane, family, belief_key in PRETRAIN_RUNS:
        run_dir = mirror / rel
        if not run_dir.exists():
            continue
        cfg = run_dir / "config.yaml"
        model_cfg = {}
        if cfg.exists():
            model_cfg = (ingest.read_train_config(cfg)["model_config"]) or {}
        gpu = L40S if family == "arch" and "xattn" in rel else H100
        rows.append(_pretraining_record(
            run_dir, mirror, battery,
            lane=lane, family=family, belief=BELIEF[belief_key],
            gpu_type=gpu, description=_describe(model_cfg)))
    return rows


def build_rl_rows(mirror: Path) -> list[RunRecord]:
    counts = flops.param_counts_from_config(RL_POLICY_CONFIG)
    rows = []
    for rel, lane, family, base, belief, novel in RL_RUNS:
        run_dir = mirror / rel
        if not (run_dir / "rl.jsonl").exists():
            continue
        gpu = L40S if family == "rlvr" else H100
        record = _rl_record(
            run_dir, lane=lane, family=family, belief=belief,
            suite=RL_FAMILY_SUITE[family],
            description="24L x 1024d dense decoder, RL policy",
            params_non_embedding=counts["params_non_embedding"],
            params_total=counts["params_total"],
            base_regime=None, objective=RL_OBJECTIVE, gpu_type=gpu,
            novel_system=novel,
            notes=("base checkpoint not recorded in the launch artefacts; "
                   "parameter count is the 350M policy class every rl-350m-* "
                   "config targets" if base is None else ""))
        record.detail["base_checkpoint"] = base
        record.data_mixture["base_checkpoint"] = base
        rows.append(record)
    return rows


def build_study_rows(mirror: Path, repo: Path | None) -> list[RunRecord]:
    """Rows for measurement studies: ablations, benches, demos, baselines."""
    rows: list[RunRecord] = []
    counts = flops.param_counts_from_config(RL_POLICY_CONFIG)
    p_non_emb = counts["params_non_embedding"]

    # -- the three-condition rule ablation -------------------------------
    rule_test = mirror / "runs/rule-test/rule_test.json"
    if rule_test.exists():
        facts = ingest.read_ablation(rule_test)
        detail = facts["detail"]
        decode = None
        if detail.get("mean_generated_correct") is not None:
            decode = flops.decode_flops_per_answer(
                p_non_emb, detail["mean_generated_correct"])
        rows.append(RunRecord(
            run_id="rule-test-rlsimple-503-921",
            lane="falsify",
            branch="E",
            family="rule-test",
            reasoning_suite=SUITE_RULE_ABLATION,
            objective="three-condition evidence ablation, greedy-free sampling "
                      "at temperature 0.7",
            created=_mtime_date([rule_test]),
            data_mixture={"eval_systems": "invented after training, held out "
                                          "from the RL pool"},
            arch=Arch(description="24L x 1024d dense decoder, RL policy",
                      variant="dense",
                      params_total=counts["params_total"],
                      params_non_embedding=p_non_emb),
            compute=Compute(decode_flops_per_answer=decode,
                            gpu_type=H100, gpu_count=1),
            metrics=Metrics(**facts["metrics"]),
            sources=facts["sources"],
            detail=detail | {"checkpoint": facts["checkpoint"],
                             "conditions": facts["condition_names"]},
            belief_changed=(
                "settled that the dependence on retrieved material is real. "
                "0.680 with the correct page, 0.002 with a different system's "
                "page, 0.000 with a blank page, retrieving and well formed in "
                "all three, so the score is not a prior over answers and not a "
                "format artefact."),
        ))

    # -- the skill ablation whose raw artefact never landed ---------------
    rows.append(RunRecord(
        run_id="skill-ablation-arithmetic",
        lane="falsify",
        branch="E",
        family="skill-ablation",
        reasoning_suite=SUITE_RL_ARITH,
        objective="three-condition evidence ablation on the arithmetic "
                  "invented-system families",
        created=None,
        arch=Arch(description="24L x 1024d dense decoder, RL policy",
                  variant="dense",
                  params_total=counts["params_total"],
                  params_non_embedding=p_non_emb),
        compute=Compute(gpu_type=H100, gpu_count=1),
        metrics=Metrics(acc_correct_evidence=0.104, acc_wrong_evidence=0.098,
                        novel_system_acquisition=0.104),
        sources=["ARCH.md section 1"],
        detail={"raw_artefact": None},
        notes=("the raw ablation.json is not in the bucket: "
               "ablate_when_done.sh writes to runs/skill-ablation/ and that "
               "prefix is empty, so these two numbers are transcribed from "
               "ARCH.md section 1, which the run produced. Re-run "
               "scripts/skill_ablation.py to replace this row with an "
               "artefact-sourced one."),
        belief_changed=(
            "on arithmetic families the model scores 0.104 with the correct "
            "page and 0.098 with the wrong one, a dependency of 0.006. It is "
            "not reading the rule at all, which is why every intervention "
            "aimed at teaching it to execute the rule failed."),
    ))

    # -- the retrieval-noise benchmark -----------------------------------
    nrm = mirror / "runs/nrm-bench/dry/results-curve-350md-401.json"
    if nrm.exists():
        facts = ingest.read_nrm_bench(nrm)
        detail = facts["detail"]
        inference = decode = None
        if detail.get("mean_total_tokens") is not None:
            inference = 2.0 * p_non_emb * float(detail["mean_total_tokens"])
        if detail.get("mean_generated_tokens") is not None:
            decode = flops.decode_flops_per_answer(
                p_non_emb, detail["mean_generated_tokens"])
        rows.append(RunRecord(
            run_id="nrm-bench-dry-350md401",
            lane="explore",
            branch="D",
            family="nrm-bench",
            reasoning_suite=SUITE_NRM,
            objective="benchmark only, no training: retrieval vs no retrieval "
                      "vs oracle context over real and scrubbed web suites",
            created=_mtime_date([nrm]),
            arch=Arch(description="24L x 1024d dense decoder", variant="dense",
                      params_total=counts["params_total"],
                      params_non_embedding=p_non_emb),
            compute=Compute(inference_flops_per_answer=inference,
                            decode_flops_per_answer=decode,
                            latency_s_per_answer=detail.get("mean_seconds"),
                            gpu_type=L40S, gpu_count=1),
            metrics=Metrics(**facts["metrics"]),
            sources=facts["sources"],
            detail=detail,
            belief_changed=(
                "the gold answer reaches the context far more often than it "
                "reaches the answer: 0.276 gold-in-evidence against 0.150 "
                "accuracy, and oracle context scores 0.059, below plain "
                "retrieval. The bottleneck is extraction, not retrieval."),
        ))

    # -- the real-web demo ------------------------------------------------
    demo = mirror / "runs/webdemo/results-webdemo.json"
    if demo.exists():
        for entry in ingest.read_web_demo(demo):
            detail = entry["detail"]
            rows.append(RunRecord(
                run_id=f"webdemo-{entry['model']}",
                lane="falsify",
                branch=_run_regime(entry["model"], None),
                family="webdemo",
                objective="demo only, no training: answer real factual "
                          "questions through a live search tier",
                created=_mtime_date([demo]),
                arch=Arch(description="24L x 1024d dense decoder",
                          variant="dense",
                          params_total=counts["params_total"],
                          params_non_embedding=p_non_emb),
                compute=Compute(latency_s_per_answer=detail.get("mean_seconds_web"),
                                gpu_type=L40S, gpu_count=1),
                metrics=Metrics(**entry["metrics"]),
                sources=entry["sources"],
                detail=detail,
                belief_changed=(
                    "the reader scores 0.000 on real web questions with search "
                    "and 0.000 without, while issuing a query on every single "
                    "item. Retrieval behaviour transferred to the open web and "
                    "answering did not."),
            ))

    # -- the evidence cross-attention cost bench --------------------------
    bench = mirror / "runs/evidence/evidence-bench-l40s.json"
    if bench.exists():
        blob = json.loads(bench.read_text())
        params = blob.get("params") or {}
        runs = blob.get("xattn") or []
        cheapest = min(runs, key=lambda r: r.get("seconds_per_step", 1e9)) if runs else {}
        rows.append(RunRecord(
            run_id="evidence-bench-l40s",
            lane="explore",
            family="evidence-bench",
            objective="cost measurement only, no training: forward throughput "
                      "of cross-attention over an evidence encoder",
            created=_mtime_date([bench]),
            arch=Arch(description="21L x 1024d decoder with a 4L x 512d "
                                  "evidence encoder",
                      variant="xattn",
                      params_total=params.get("total"),
                      params_non_embedding=params.get("non_embedding")),
            compute=Compute(
                gpu_type=blob.get("gpu"), gpu_count=1,
                inference_flops_per_answer=(
                    cheapest.get("fwd_tflops_per_seq", 0) * 1e12 or None),
                latency_s_per_answer=(
                    cheapest.get("seconds_per_step") /
                    blob.get("answer_tokens_per_seq", 1)
                    if cheapest.get("seconds_per_step") else None)),
            metrics=Metrics(),
            sources=[str(bench)],
            detail={"configs_measured": len(runs),
                    "best": cheapest,
                    "param_ratio_vs_standard": blob.get("param_ratio")},
            belief_changed=(
                "reading 8192 evidence tokens costs 0.243 TFLOPs and 82 ms per "
                "sequence on an L40S at a parameter count within 0.05 percent "
                "of the standard 350M, so evidence length can be paid for "
                "outside the decoder context."),
        ))

    # -- external baselines ------------------------------------------------
    if repo is not None:
        for path in sorted((repo / "runs/public_bench").glob(
                "*/public_bench_report.json")):
            blob = json.loads(path.read_text())
            meta = blob.get("meta") or {}
            nat = (blob.get("results") or {}).get("naturalized") or {}
            rows.append(RunRecord(
                run_id=f"public-bench-{path.parent.name}",
                lane="explore",
                family="public-bench",
                objective="external baseline, no training: an off-the-shelf "
                          "instruction model on our naturalized reading suite",
                created=_mtime_date([path]),
                arch=Arch(description=meta.get("model") or "external model",
                          variant="external"),
                compute=Compute(gpu_type=meta.get("device")),
                metrics=Metrics(reading=nat.get("contains")),
                sources=[str(path)],
                detail={"n": nat.get("n"), "em": nat.get("em"),
                        "model": meta.get("model"),
                        "prompt_style": meta.get("prompt_style"),
                        "per_group": nat.get("per_group")},
                belief_changed=(
                    "a knowledge-rich off-the-shelf model of similar size "
                    "reads our naturalized suite at %.3f contains-answer, "
                    "which is the number our knowledge-free arm has to reach."
                    % (nat.get("contains") or 0.0)),
            ))
    return rows


def build_all(mirror: str | Path, repo: str | Path | None = None) -> list[RunRecord]:
    """Every row the project's artefacts support, in a stable order."""
    mirror = Path(mirror)
    repo = Path(repo) if repo else None
    battery = collect_battery_scores(mirror)
    rows = build_pretraining_rows(mirror, battery)
    rows += build_rl_rows(mirror)
    rows += build_study_rows(mirror, repo)
    return rows
