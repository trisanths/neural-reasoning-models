"""Readers for the artefacts this project already writes.

Nothing here invents a number. Each function opens files that some earlier
run produced, pulls out the fields the registry cares about, and returns a
plain dict of facts with None wherever the artefact is silent. Turning those
facts into a RunRecord (which needs a lane, an objective and a sentence about
what changed) is the caller's job, because those are editorial and no file
on disk knows them.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from . import flops


def _read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _read_yaml(path: str | Path) -> dict[str, Any]:
    import yaml  # deferred: the store itself has no yaml dependency

    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


# ---------------------------------------------------------------------------
# RL run directories: rl.jsonl (per optimizer step) and eval.jsonl (per eval)
# ---------------------------------------------------------------------------

def read_rl_run(run_dir: str | Path) -> dict[str, Any]:
    """Summarise one RL run directory.

    Reads ``rl.jsonl`` for cost and ``eval.jsonl`` for scores. The final eval
    is the line tagged ``after`` if the run reached it, else the highest-step
    line -- runs that were stopped early still get scored at where they got
    to, which matters because most of the falsified levers were stopped early.
    """
    run_dir = Path(run_dir)
    out: dict[str, Any] = {
        "run_dir": str(run_dir),
        "sources": [],
        "steps": None,
        "wall_clock_s": None,
        "train_tokens": None,
        "rollouts": None,
        "eval_before": None,
        "eval_final": None,
        "eval_best": None,
        "final_tag": None,
        "reward_std_final": None,
        "generated_tokens": None,
    }

    rl_path = run_dir / "rl.jsonl"
    if rl_path.exists():
        steps = _read_jsonl(rl_path)
        out["sources"].append(str(rl_path))
        if steps:
            last = steps[-1]
            out["steps"] = last.get("step")
            out["wall_clock_s"] = last.get("elapsed_s")
            tokens = [s.get("train_tokens") for s in steps
                      if isinstance(s.get("train_tokens"), (int, float))]
            out["train_tokens"] = float(sum(tokens)) if tokens else None
            rollouts = [s.get("n_rollouts") for s in steps
                        if isinstance(s.get("n_rollouts"), (int, float))]
            out["rollouts"] = float(sum(rollouts)) if rollouts else None
            out["reward_std_final"] = last.get("reward_std")
            # Tokens the policy actually generated across every rollout. Used
            # for the decode half of the RL training cost; the prompt prefill
            # is not logged, so anything built on this is a lower bound.
            generated = [float(s["n_rollouts"]) * float(s["mean_generated"])
                         for s in steps
                         if isinstance(s.get("n_rollouts"), (int, float))
                         and isinstance(s.get("mean_generated"), (int, float))]
            out["generated_tokens"] = sum(generated) if generated else None

    eval_path = run_dir / "eval.jsonl"
    if eval_path.exists():
        evals = _read_jsonl(eval_path)
        out["sources"].append(str(eval_path))
        if evals:
            before = next((e for e in evals if e.get("tag") == "before"), None)
            after = next((e for e in reversed(evals)
                          if e.get("tag") == "after"), None)
            # A run whose only eval is the "before" line has no result: it was
            # stopped before its first scheduled eval. Scoring it at its
            # starting accuracy would read as a finding.
            trained = [e for e in evals if e.get("tag") != "before"]
            final = after or (max(trained, key=lambda e: (e.get("step") or 0))
                              if trained else None)
            best = max(evals, key=lambda e: (e.get("accuracy") or -1.0))
            out["eval_before"] = before
            out["eval_final"] = final
            out["eval_best"] = best if trained else None
            out["final_tag"] = final.get("tag") if final else None
    return out


def read_rl_eval_samples(run_dir: str | Path) -> dict[str, Any]:
    """Per-task-family accuracy from an RL run's sampled eval episodes.

    ``eval.jsonl`` records one pooled accuracy per eval, which hides the case
    where a run scores on one easy family and zero on the families the
    experiment was actually about. The sampled episodes carry a ``domain``
    per item, so this recovers the split. It covers only the sampled
    episodes, not the whole eval pool, and reports its own n so the reader
    can see how thin it is.
    """
    run_dir = Path(run_dir)
    counts: dict[str, list[int]] = {}
    files = sorted(p for p in run_dir.glob("eval-samples-*.jsonl")
                   if "before" not in p.name)
    for path in files:
        for row in _read_jsonl(path):
            domain = row.get("domain")
            if domain is None:
                continue
            slot = counts.setdefault(domain, [0, 0])
            slot[0] += 1
            slot[1] += 1 if row.get("correct") else 0
    return {
        "n_files": len(files),
        "per_domain": {
            domain: {"n": n, "correct": correct,
                     "accuracy": round(correct / n, 4) if n else None}
            for domain, (n, correct) in sorted(counts.items())
        },
    }


def rl_run_facts(run_dir: str | Path, *,
                 params_non_embedding: int | None = None) -> dict[str, Any]:
    """The registry-shaped view of an RL run: metrics and compute.

    ``latency_s_per_answer`` is the measured eval wall clock divided by the
    number of rollouts in that eval, so it is a batched per-answer latency at
    that eval's batch size, not a single-stream latency.
    """
    raw = read_rl_run(run_dir)
    final = raw["eval_final"] or {}
    before = raw["eval_before"] or {}

    latency = None
    if final.get("elapsed_s") and final.get("n_rollouts"):
        latency = float(final["elapsed_s"]) / float(final["n_rollouts"])

    decode = None
    if params_non_embedding and final.get("mean_generated") is not None:
        decode = flops.decode_flops_per_answer(
            params_non_embedding, final["mean_generated"])

    samples = read_rl_eval_samples(run_dir)
    return {
        "raw": raw,
        "sources": raw["sources"],
        "per_domain": samples["per_domain"],
        "metrics": {
            "reasoning": final.get("accuracy"),
        },
        "compute": {
            "wall_clock_s": raw["wall_clock_s"],
            "latency_s_per_answer": latency,
            "decode_flops_per_answer": decode,
        },
        "detail": {
            "steps": raw["steps"],
            "final_tag": raw["final_tag"],
            "accuracy_before": before.get("accuracy"),
            "accuracy_after": final.get("accuracy"),
            "accuracy_best": (raw["eval_best"] or {}).get("accuracy"),
            "reward_mean_after": final.get("reward_mean"),
            "any_retrieval_after": final.get("any_retrieval"),
            "well_formed_after": final.get("well_formed"),
            "mean_generated_after": final.get("mean_generated"),
            "eval_rollouts": final.get("n_rollouts"),
            "per_domain": samples["per_domain"],
            "per_domain_files": samples["n_files"],
        },
    }


# ---------------------------------------------------------------------------
# Eval battery: results.json from scripts/eval_battery.py
# ---------------------------------------------------------------------------

def read_eval_battery(results_path: str | Path) -> list[dict[str, Any]]:
    """One dict per checkpoint in an eval-battery ``results.json``.

    The battery's ``summary`` list carries the headline scores and its
    ``checkpoints`` list carries the model config and timings; they are
    matched by position, which is how the battery writes them.
    """
    results_path = Path(results_path)
    with open(results_path, "r", encoding="utf-8") as handle:
        blob = json.load(handle)

    summary = blob.get("summary") or []
    checkpoints = blob.get("checkpoints") or []
    out = []
    for index, row in enumerate(summary):
        detail = checkpoints[index] if index < len(checkpoints) else {}
        meta = detail.get("meta") or {}
        heldout = detail.get("heldout") or {}
        timings = detail.get("timings") or {}
        per_type = heldout.get("per_type") or {}
        out.append({
            "name": row.get("name"),
            "regime": row.get("regime"),
            "train_seed": row.get("train_seed"),
            "step": row.get("step"),
            "model_config": meta.get("model_config"),
            "checkpoint": meta.get("checkpoint"),
            "sources": [str(results_path)],
            "metrics": {
                # Naturalized reading, clean variant, contains-answer. This is
                # the pre-registered gate in SPEC.md section 7.
                "reading": row.get("naturalized_contains"),
                "reasoning": row.get("heldout_accuracy"),
                "closed_book_probe": row.get("probes_accuracy"),
            },
            "detail": {
                "naturalized_em": row.get("naturalized_em"),
                "naturalized_elicitation": row.get("naturalized_elicitation"),
                "naturalized_contains_contradiction":
                    row.get("naturalized_contains_contradiction"),
                "naturalized_contains_ocr": row.get("naturalized_contains_ocr"),
                "probes_leakage_flag": row.get("probes_leakage_flag"),
                "heldout_mean_rounds": row.get("heldout_mean_rounds"),
                "heldout_n_questions": heldout.get("n_questions"),
                "heldout_chance": heldout.get("chance"),
                "heldout_multi_hop": (per_type.get("multi_hop") or {}).get("accuracy"),
                "heldout_lookup": (per_type.get("lookup") or {}).get("accuracy"),
                "noise_slope": row.get("noise_slope"),
                "noise_clean_accuracy": row.get("noise_clean_accuracy"),
                "eval_seconds_total": timings.get("total_s"),
                "eval_heldout_s": timings.get("heldout_s"),
            },
        })
    return out


# ---------------------------------------------------------------------------
# Ablations: rule_test.json and ablation.json
# ---------------------------------------------------------------------------

# scripts/skill_rule_test.py writes no_documents, scripts/skill_ablation.py
# writes no_textbook. Same experiment, two spellings of the empty condition.
_CORRECT_KEYS = ("textbook", "correct", "correct_textbook", "rule_card")
_WRONG_KEYS = ("wrong_textbook", "wrong", "wrong_documents")
_NONE_KEYS = ("no_documents", "no_textbook", "none", "blank")


def _first(conditions: dict[str, Any], names: Iterable[str]) -> dict[str, Any] | None:
    for name in names:
        if name in conditions:
            return conditions[name]
    return None


def read_ablation(path: str | Path) -> dict[str, Any]:
    """Read a three-condition evidence ablation.

    Handles both ``rule_test.json`` and ``ablation.json``. Retrieval
    dependency is the point of the file: accuracy with the correct page minus
    accuracy with a different system's page. The blank-page condition is
    reported separately because it measures something else -- whether the
    model can answer with no evidence at all.
    """
    path = Path(path)
    with open(path, "r", encoding="utf-8") as handle:
        blob = json.load(handle)

    conditions = blob.get("conditions") or {}
    correct = _first(conditions, _CORRECT_KEYS)
    wrong = _first(conditions, _WRONG_KEYS)
    empty = _first(conditions, _NONE_KEYS)
    if correct is None:
        raise ValueError(
            f"{path} has no correct-evidence condition; saw {sorted(conditions)}")

    acc_correct = correct.get("accuracy")
    acc_wrong = wrong.get("accuracy") if wrong else None
    acc_none = empty.get("accuracy") if empty else None
    dependency = None
    if acc_correct is not None and acc_wrong is not None:
        dependency = acc_correct - acc_wrong

    return {
        "checkpoint": blob.get("checkpoint"),
        "temperature": blob.get("temperature"),
        "sources": [str(path)],
        "condition_names": sorted(conditions),
        "metrics": {
            "acc_correct_evidence": acc_correct,
            "acc_wrong_evidence": acc_wrong,
            "acc_no_evidence": acc_none,
            "retrieval_dependency": dependency,
            "novel_system_acquisition": acc_correct,
        },
        "detail": {
            "n_rollouts": correct.get("n_rollouts"),
            "well_formed_correct": correct.get("well_formed"),
            "well_formed_wrong": wrong.get("well_formed") if wrong else None,
            "any_retrieval_correct": correct.get("any_retrieval"),
            "mean_generated_correct": correct.get("mean_generated"),
        },
    }


# ---------------------------------------------------------------------------
# Two more artefacts the backfill needs
# ---------------------------------------------------------------------------

def read_nrm_bench(results_path: str | Path) -> dict[str, Any]:
    """Read run_nrm_bench.py output: retrieval vs no_retrieval vs oracle.

    This bench is the only artefact that records a measured total token count
    per answer, so it is the only source that can fill
    ``inference_flops_per_answer`` rather than the decode-only figure.
    """
    results_path = Path(results_path)
    with open(results_path, "r", encoding="utf-8") as handle:
        blob = json.load(handle)

    by_condition = blob.get("by_condition") or {}

    def pooled(name: str) -> dict[str, Any]:
        return ((by_condition.get(name) or {}).get("pooled") or {})

    retrieval = pooled("retrieval")
    no_retrieval = pooled("no_retrieval")
    oracle = pooled("oracle_context")

    real_web = (((by_condition.get("retrieval") or {}).get("by_suite") or {})
                .get("real_web") or {})

    return {
        "model": blob.get("model"),
        "checkpoint": blob.get("checkpoint"),
        "sources": [str(results_path)],
        "metrics": {
            "reasoning": retrieval.get("accuracy"),
            "acc_correct_evidence": oracle.get("accuracy"),
            "acc_no_evidence": no_retrieval.get("accuracy"),
            "ood_generalization": real_web.get("accuracy"),
        },
        "detail": {
            "n_items": blob.get("n_items"),
            "grounded_accuracy": retrieval.get("grounded_accuracy"),
            "gold_in_evidence": retrieval.get("gold_in_evidence"),
            "confabulation_rate": retrieval.get("confabulation_rate"),
            "mean_total_tokens": retrieval.get("mean_total_tokens"),
            "mean_generated_tokens": retrieval.get("mean_generated_tokens"),
            "mean_seconds": retrieval.get("mean_seconds"),
        },
    }


def read_web_demo(results_path: str | Path) -> list[dict[str, Any]]:
    """Read the real-web demo: accuracy with and without a live search tier."""
    results_path = Path(results_path)
    with open(results_path, "r", encoding="utf-8") as handle:
        blob = json.load(handle)

    out = []
    for name, model in (blob.get("models") or {}).items():
        accuracy = model.get("accuracy") or {}
        seconds = model.get("mean_seconds") or {}
        out.append({
            "model": name,
            "sources": [str(results_path)],
            "metrics": {
                "ood_generalization": accuracy.get("with_search"),
                "acc_no_evidence": accuracy.get("without_search"),
            },
            "detail": {
                "checkpoint_step": model.get("checkpoint_step"),
                "n_questions_web": (model.get("n_questions") or {}).get("web"),
                "mean_seconds_web": seconds.get("web"),
                "mean_query_tokens": model.get("mean_query_tokens"),
                "share_web_with_any_round": model.get("share_web_with_any_round"),
            },
        })
    return out


def read_train_config(config_path: str | Path) -> dict[str, Any]:
    """Parameter counts and training FLOPs from a pretraining ``config.yaml``."""
    config_path = Path(config_path)
    cfg = _read_yaml(config_path)
    model_cfg = cfg.get("model") or {}
    tokens = training_tokens_or_none(cfg, model_cfg)
    multiplier = flops.effective_layer_passes(model_cfg)
    # The cross-attention architecture carries an evidence encoder and gated
    # cross-attention blocks that the decoder formula knows nothing about, so
    # counting it here would produce a confident undercount. The measured
    # count for that shape lives in the evidence bench artefact instead.
    countable = not (model_cfg.get("evidence_mode") or model_cfg.get("d_enc"))
    counts = (flops.param_counts_from_config(model_cfg) if countable
              else {"params_total": None, "params_non_embedding": None})
    compute_p = (counts["params_non_embedding"] * multiplier
                 if countable else None)
    return {
        "config": cfg,
        "model_config": model_cfg,
        "sources": [str(config_path)],
        "arch": {
            "params_total": counts["params_total"],
            "params_non_embedding": counts["params_non_embedding"],
            "d_model": model_cfg.get("d_model"),
            "n_layers": model_cfg.get("n_layers"),
            "n_heads": model_cfg.get("n_heads"),
            "d_ff": model_cfg.get("d_ff"),
            "vocab_size": model_cfg.get("vocab_size"),
            "max_seq_len": model_cfg.get("max_seq_len"),
            "variant": "looped" if model_cfg.get("recurrent") else "dense",
        },
        "compute": {
            "train_tokens": tokens,
            "train_flops": (flops.training_flops(compute_p, tokens)
                            if tokens and compute_p else None),
        },
        "params_countable": countable,
        "layer_pass_multiplier": multiplier,
        "seed": (cfg.get("train") or {}).get("seed"),
    }


def training_tokens_or_none(cfg: dict[str, Any],
                            model_cfg: dict[str, Any]) -> int | None:
    schedule = cfg.get("schedule") or {}
    train = cfg.get("train") or {}
    if not schedule.get("max_steps") or not train.get("batch_size"):
        return None
    if not model_cfg.get("max_seq_len"):
        return None
    return flops.training_tokens(schedule, train, model_cfg)
