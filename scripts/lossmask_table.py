"""Turn the four arm results into the table and the verdict.

Two derived numbers carry the argument.

  probe suppression   how far the arm moved from the control toward chance,
                      as a fraction of the distance the control had to fall.
                      1.0 is chance, 0.0 is the control.
  reading retained    the arm's naturalized contains rate over the control's.
                      Regime E, which destroyed the corpus, never got past
                      0.83 here. That is the number to beat.

Both rates carry Wilson intervals, because the naturalized suite is a few
hundred items and the probe suite is barely more than a hundred, and a table
of bare point estimates from samples that small invites reading noise as
result.
"""

import argparse
import json
import math
from pathlib import Path

ARM_LABELS = {
    "lm-a": "a  factual spans 0.0",
    "lm-b": "b  numbers and dates 0.0",
    "lm-c": "c  factual spans 0.1",
    "lm-d": "d  control, all 1.0",
}


def wilson(successes: int, n: int, z: float = 1.96) -> tuple:
    """Wilson score interval for a binomial rate."""
    if n == 0:
        return (0.0, 1.0)
    p = successes / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def fmt_ci(rate: float, n: int) -> str:
    lo, hi = wilson(round(rate * n), n)
    return f"{rate:.3f} [{lo:.3f}, {hi:.3f}]"


def factual_loss(per_tag: dict):
    """Token weighted mean loss over the entity, number, date and web tags:
    the half of the stream the masked arms were never paid to predict."""
    total = count = 0.0
    for name in ("entity", "number", "date", "web"):
        cell = per_tag.get(name)
        if cell:
            total += cell["loss"] * cell["tokens"]
            count += cell["tokens"]
    return total / count if count else None


def build_table(results: list) -> str:
    by_run = {Path(r["run"]).name: r for r in results}
    control = by_run.get("lm-d")
    lines = [
        "| arm | weights | probe (chance 0.25) | probe suppression | "
        "naturalized contains | reading retained | held out loss | "
        "loss on plain | loss on factual |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for name in ("lm-a", "lm-b", "lm-c", "lm-d"):
        row = by_run.get(name)
        if row is None:
            continue
        weights = (row.get("lossmask") or {}).get("weights") or {}
        weight_text = (", ".join(f"{k} {v}" for k, v in sorted(weights.items()))
                       or "none")
        probe = fmt_ci(row["probe_accuracy"], row["probe_n"])
        nat = fmt_ci(row["naturalized_contains"], row["naturalized_n"])
        suppression = retained = "reference"
        if control is not None and name != "lm-d":
            span = control["probe_accuracy"] - row["probe_chance"]
            suppression = (
                f"{(control['probe_accuracy'] - row['probe_accuracy']) / span:.2f}"
                if abs(span) > 1e-9 else "undefined")
            base = control["naturalized_contains"]
            retained = (f"{row['naturalized_contains'] / base:.3f}"
                        if base > 0 else "undefined")
        per_tag = row["heldout"].get("per_tag", {})
        plain = per_tag.get("plain", {}).get("loss")
        factual = factual_loss(per_tag)
        lines.append(
            f"| {ARM_LABELS.get(name, name)} | {weight_text} | {probe} | "
            f"{suppression} | {nat} | {retained} | "
            f"{row['heldout']['loss']:.4f} | "
            f"{'-' if plain is None else f'{plain:.4f}'} | "
            f"{'-' if factual is None else f'{factual:.4f}'} |")
    return "\n".join(lines)


def verdict(results: list) -> dict:
    by_run = {Path(r["run"]).name: r for r in results}
    control, masked = by_run.get("lm-d"), by_run.get("lm-a")
    if control is None or masked is None:
        return {"verdict": "incomplete", "reason": "need arms a and d"}
    chance = masked["probe_chance"]
    span = control["probe_accuracy"] - chance
    suppression = ((control["probe_accuracy"] - masked["probe_accuracy"]) / span
                   if abs(span) > 1e-9 else float("nan"))
    retained = (masked["naturalized_contains"] / control["naturalized_contains"]
                if control["naturalized_contains"] > 0 else float("nan"))
    n = control["probe_n"]
    control_lo, _ = wilson(round(control["probe_accuracy"] * n), n)
    return {
        "control_probe": control["probe_accuracy"],
        "control_probe_above_chance": control_lo > chance,
        "masked_probe": masked["probe_accuracy"],
        "probe_suppression": round(suppression, 3),
        "reading_retained": round(retained, 3),
        "heldout_loss_gap": round(
            masked["heldout"]["loss"] - control["heldout"]["loss"], 4),
        "heldout_plain_loss_gap": round(
            masked["heldout"]["per_tag"]["plain"]["loss"]
            - control["heldout"]["per_tag"]["plain"]["loss"], 4),
        "heldout_factual_loss_gap": round(
            factual_loss(masked["heldout"]["per_tag"])
            - factual_loss(control["heldout"]["per_tag"]), 4),
        "regime_e_reading_bar": 0.83,
        "beats_regime_e_reading": retained > 0.83,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m scripts.lossmask_table")
    parser.add_argument("--results", required=True, help="results.json")
    parser.add_argument("--out", default=None, help="markdown output path")
    args = parser.parse_args(argv)

    results = json.loads(Path(args.results).read_text())["results"]
    table = build_table(results)
    summary = verdict(results)
    text = (table + "\n\n```json\n" + json.dumps(summary, indent=2) + "\n```\n")
    print(text)
    if args.out:
        Path(args.out).write_text(text)
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
