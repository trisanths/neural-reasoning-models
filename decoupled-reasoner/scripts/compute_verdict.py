"""Apply the pre-registered kill-test decision rule to battery results.

Reads the combined results.json written by scripts.eval_battery, computes
per-regime seed means and standard deviations on the naturalized reading
contains-answer score (the gate metric; EM is reported alongside), the
C-to-A ratio of means, and a bootstrap 95 percent interval for that
ratio resampling both items and seeds. The rule comes from SPEC.md
section 7: a ratio of at least 0.90 means the strict form survives,
0.60 to 0.90 means the weakened form, below 0.60 means the strict form
is dead. Writes verdict.json and VERDICT.md.
"""

import argparse
import json
import time
from pathlib import Path

import numpy as np

RULE_TEXT = (
    "Compare regime C against regime A at the 350M class on the "
    "naturalized reading suite. If C reaches at least 90 percent of A's "
    "score, the strict form survives and Phase 2 tests it. Between 60 "
    "and 90 percent, the strict form is weakened: Phase 2 uses a "
    "frequency-ordered resident knowledge diet plus teacher "
    "distillation. Below 60 percent, the strict form is dead; Phase 2 "
    "tests only the weakened form and the writeup says so plainly.")

STRICT_THRESHOLD = 0.90
WEAK_THRESHOLD = 0.60


def collect_regime(checkpoints, regime):
    """Return the checkpoints of one regime, sorted by training seed."""
    cps = [c for c in checkpoints if c["meta"]["regime"] == regime]
    cps.sort(key=lambda c: c["meta"]["train_seed"])
    if not cps:
        raise ValueError(f"no regime {regime} checkpoints in results")
    return cps


def item_matrix(cps, item_ids, key):
    """Per-item outcome matrix, shape (n_seeds, n_items), for one metric."""
    rows = []
    for cp in cps:
        by_id = {it["id"]: it[key]
                 for it in cp["naturalized"]["clean"]["per_item"]}
        rows.append([1.0 if by_id[i] else 0.0 for i in item_ids])
    return np.asarray(rows, dtype=np.float64)


def seed_stats(matrix, cps):
    per_seed = {str(cp["meta"]["train_seed"]): round(float(row.mean()), 6)
                for cp, row in zip(cps, matrix)}
    means = matrix.mean(axis=1)
    mean = float(means.mean())
    std = float(means.std(ddof=1)) if len(means) > 1 else 0.0
    return {"n_seeds": len(cps), "per_seed": per_seed,
            "mean": round(mean, 6), "std": round(std, 6)}


def bootstrap_ratio(mat_a, mat_c, n_reps, seed):
    """Percentile CI for mean_C / mean_A resampling items and seeds."""
    rng = np.random.default_rng(seed)
    na, ni = mat_a.shape
    nc = mat_c.shape[0]
    ratios = []
    degenerate = 0
    for _ in range(n_reps):
        items = rng.integers(0, ni, ni)
        rows_a = rng.integers(0, na, na)
        rows_c = rng.integers(0, nc, nc)
        mean_a = float(mat_a[rows_a][:, items].mean())
        mean_c = float(mat_c[rows_c][:, items].mean())
        if mean_a <= 0.0:
            degenerate += 1
            continue
        ratios.append(mean_c / mean_a)
    if not ratios:
        return None, degenerate
    lo, hi = np.percentile(ratios, [2.5, 97.5])
    return [round(float(lo), 4), round(float(hi), 4)], degenerate


def apply_rule(ratio):
    if ratio is None:
        return ("not_computable",
                "The regime A mean is zero, so the ratio is undefined and "
                "the rule cannot be applied.")
    if ratio >= STRICT_THRESHOLD:
        return ("strict_survives",
                f"The ratio {ratio:.4f} is at or above {STRICT_THRESHOLD}. "
                "The strict form survives and Phase 2 tests it.")
    if ratio >= WEAK_THRESHOLD:
        return ("weakened",
                f"The ratio {ratio:.4f} falls between {WEAK_THRESHOLD} and "
                f"{STRICT_THRESHOLD}. The strict form is weakened: Phase 2 "
                "uses a frequency-ordered resident knowledge diet plus "
                "teacher distillation.")
    return ("strict_dead",
            f"The ratio {ratio:.4f} is below {WEAK_THRESHOLD}. The strict "
            "form is dead; Phase 2 tests only the weakened form.")


def render_markdown(verdict: dict) -> str:
    a = verdict["regimes"]["a"]
    c = verdict["regimes"]["c"]
    em = verdict["em"]
    lines = [
        "# Kill-test verdict",
        "",
        f"Generated {verdict['generated_at']} from "
        f"{verdict['n_items']} naturalized items and "
        f"{a['n_seeds']} A seeds, {c['n_seeds']} C seeds.",
        "",
        "## Gate metric: naturalized reading, contains-answer, clean variant",
        "",
        f"Regime A per seed: " + ", ".join(
            f"{k}: {v:.4f}" for k, v in a["per_seed"].items()),
        f"Regime A mean {a['mean']:.4f}, std {a['std']:.4f}.",
        "",
        f"Regime C per seed: " + ", ".join(
            f"{k}: {v:.4f}" for k, v in c["per_seed"].items()),
        f"Regime C mean {c['mean']:.4f}, std {c['std']:.4f}.",
        "",
    ]
    ratio = verdict["ratio"]
    if ratio is None:
        lines.append("C to A ratio of means: undefined, regime A mean is zero.")
    else:
        lines.append(f"C to A ratio of means: {ratio:.4f}.")
    ci = verdict["bootstrap"]["ci95"]
    if ci is None:
        lines.append("Bootstrap interval: not available, every replicate had "
                     "a zero regime A mean.")
    else:
        lines.append(
            f"Bootstrap 95 percent interval over items and seeds: "
            f"[{ci[0]:.4f}, {ci[1]:.4f}] "
            f"({verdict['bootstrap']['n_reps']} replicates, "
            f"{verdict['bootstrap']['n_degenerate']} dropped for a zero "
            f"regime A mean).")
    lines += [
        "",
        "For reference, exact match on the same variant: "
        f"A mean {em['a_mean']:.4f}, C mean {em['c_mean']:.4f}"
        + (f", ratio {em['ratio']:.4f}." if em["ratio"] is not None
           else ", ratio undefined."),
        "",
        "## Pre-registered rule (SPEC.md section 7)",
        "",
        RULE_TEXT,
        "",
        "## Outcome",
        "",
        verdict["outcome_text"],
        "",
    ]
    raised_c = verdict["leakage_flags_c_raised"]
    lines.append("## Knowledge probe leakage flags")
    lines.append("")
    lines.append(
        "The leakage rule applies to regime C only; regime A trained on "
        "real text and is expected to score above chance.")
    if raised_c:
        lines.append(
            "RAISED for: " + ", ".join(raised_c) + ". Those runs must be "
            "investigated before this verdict counts.")
    else:
        lines.append("Clear on every regime C checkpoint; their probe "
                     "scores are consistent with chance.")
    rounds = verdict["heldout_mean_rounds"]
    if rounds:
        lines.append("")
        lines.append("## Retrieval loop usage on held-out worlds")
        lines.append("")
        lines.append(
            "Mean served rounds per question in the interactive loop: "
            + ", ".join(f"{k}: {v:.2f}" for k, v in sorted(rounds.items()))
            + ". Values near zero mean the model answered mostly without "
            "retrieving, so heldout and noise numbers reflect closed-book "
            "behavior.")
    lines.append("")
    lines.append("## Provenance")
    lines.append("")
    for cp in verdict["checkpoints"]:
        lines.append(f"- {cp['name']}: step {cp['step']}, {cp['checkpoint']}")
    lines.append("")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m scripts.compute_verdict")
    parser.add_argument("--results", required=True,
                        help="combined results.json from scripts.eval_battery")
    parser.add_argument("--out", required=True,
                        help="directory for verdict.json and VERDICT.md")
    parser.add_argument("--bootstrap", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args(argv)

    with open(args.results) as fh:
        results = json.load(fh)
    checkpoints = results["checkpoints"]

    cps_a = collect_regime(checkpoints, "a")
    cps_c = collect_regime(checkpoints, "c")

    ids_sets = [set(it["id"] for it in cp["naturalized"]["clean"]["per_item"])
                for cp in cps_a + cps_c]
    item_ids = sorted(set.intersection(*ids_sets))
    if not item_ids:
        raise ValueError("no naturalized item ids shared by all checkpoints")

    mat_a = item_matrix(cps_a, item_ids, "contains")
    mat_c = item_matrix(cps_c, item_ids, "contains")
    stats_a = seed_stats(mat_a, cps_a)
    stats_c = seed_stats(mat_c, cps_c)

    ratio = (round(stats_c["mean"] / stats_a["mean"], 6)
             if stats_a["mean"] > 0 else None)
    ci95, degenerate = bootstrap_ratio(mat_a, mat_c, args.bootstrap, args.seed)
    outcome, outcome_text = apply_rule(ratio)

    em_a = item_matrix(cps_a, item_ids, "em").mean(axis=1)
    em_c = item_matrix(cps_c, item_ids, "em").mean(axis=1)
    em_a_mean = float(em_a.mean())
    em_c_mean = float(em_c.mean())
    em = {
        "a_mean": round(em_a_mean, 6),
        "a_std": round(float(em_a.std(ddof=1)) if len(em_a) > 1 else 0.0, 6),
        "c_mean": round(em_c_mean, 6),
        "c_std": round(float(em_c.std(ddof=1)) if len(em_c) > 1 else 0.0, 6),
        "ratio": round(em_c_mean / em_a_mean, 6) if em_a_mean > 0 else None,
    }

    leakage_flags = {}
    heldout_mean_rounds = {}
    cp_meta = []
    for cp in cps_a + cps_c:
        name = (f"killtest-{cp['meta']['regime']}-"
                f"{cp['meta']['train_seed']}")
        leakage_flags[name] = bool(
            cp.get("probes", {}).get("leakage_flag", False))
        rounds = cp.get("heldout", {}).get("mean_rounds")
        if rounds is not None:
            heldout_mean_rounds[name] = rounds
        cp_meta.append({"name": name, "step": cp["meta"]["step"],
                        "checkpoint": cp["meta"]["checkpoint"]})

    verdict = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "results_file": str(args.results),
        "gate_metric": "naturalized_reading.contains_answer.clean",
        "n_items": len(item_ids),
        "regimes": {"a": stats_a, "c": stats_c},
        "em": em,
        "ratio": ratio,
        "bootstrap": {"n_reps": args.bootstrap, "seed": args.seed,
                      "ci95": ci95, "n_degenerate": degenerate},
        "rule": {"source": "SPEC.md section 7", "text": RULE_TEXT,
                 "strict_threshold": STRICT_THRESHOLD,
                 "weak_threshold": WEAK_THRESHOLD},
        "outcome": outcome,
        "outcome_text": outcome_text,
        "leakage_flags": leakage_flags,
        "leakage_flags_c_raised": sorted(
            k for k, v in leakage_flags.items() if v and "-c-" in k),
        "heldout_mean_rounds": heldout_mean_rounds,
        "checkpoints": cp_meta,
    }

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "verdict.json"
    with open(json_path, "w") as fh:
        json.dump(verdict, fh, indent=1)
        fh.write("\n")
    md_path = out_dir / "VERDICT.md"
    md_path.write_text(render_markdown(verdict))

    print(f"ratio {ratio} ci95 {ci95} outcome {outcome}")
    print(f"wrote {json_path} and {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
