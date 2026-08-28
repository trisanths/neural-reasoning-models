"""Append the four loss masking arms to the experiment registry.

One row per arm, so the frontier can argue with them the way it argues with
regime E. reading is the naturalized contains rate and closed_book_probe is
the probe accuracy, which the frontier minimizes. Everything the two columns
cannot hold, and it is most of what makes these rows worth reading, goes in
detail: the weight table the arm trained under, held out loss split by tag,
and probe accuracy split by whether the answer was a span the tagger could
reach at all.

Usage:

    uv run python -m scripts.lossmask_register \
        --results ~/results/lossmask/results.json --repo . [--dry-run]
"""

import argparse
import json
from pathlib import Path

ARMS = {
    "lm-a": ("lossmask-150m-a",
             "every factual span at weight 0.0: entities, numbers, dates and "
             "web anchors carry no gradient, natural text otherwise intact"),
    "lm-b": ("lossmask-150m-b",
             "numbers and dates at weight 0.0, names left alone"),
    "lm-c": ("lossmask-150m-c",
             "every factual span at weight 0.1: discounted, not removed"),
    "lm-d": ("lossmask-150m-d",
             "the control: every token at weight 1.0, plain cross entropy"),
}


def head_commit(repo: str):
    """The commit the code was at, or None when the tree is not a checkout.
    The arms train on a box holding an unpacked archive rather than a clone,
    so the caller usually passes --git-commit instead."""
    import subprocess

    try:
        out = subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"],
                             capture_output=True, text=True, check=True)
        return out.stdout.strip()
    except Exception:
        return None


def build_rows(results: list, tag_histogram: dict | None, belief: dict,
               git_commit=None) -> list:
    from scripts.lossmask_table import factual_loss, probe_split

    rows = []
    for row in results:
        name = Path(row["run"]).name
        run_id, objective = ARMS.get(name, (name, ""))
        weights = (row.get("lossmask") or {}).get("weights") or {}
        per_tag = row["heldout"].get("per_tag", {})
        rows.append({
            "run_id": run_id,
            "lane": "explore",
            "git_commit": git_commit,
            "branch": "C",
            "family": "lossmask",
            "objective": f"next token prediction on natural text, {objective}",
            "reasoning_suite": None,
            "belief_changed": belief.get(name, "none"),
            "data_mixture": {
                "regime": "lossmask",
                "natural": 1.0,
                "source": "regime A parquet, tagged by src/lossmask, tokens "
                          "byte identical to a plain regime A render",
                "loss_weights": weights or {"all": 1.0},
                "tag_histogram": tag_histogram or {},
            },
            "arch": {
                "description": "12L x 768d dense decoder, 2048 context",
                "variant": "dense",
                "d_model": 768, "n_layers": 12, "n_heads": 12, "d_ff": 2048,
                "max_seq_len": 2048, "vocab_size": 32768,
                "params_total": 135285504,
                "params_non_embedding": 84953856,
            },
            "compute": {
                "gpu_count": 1,
                "gpu_type": "NVIDIA H100 80GB SXM",
                "train_tokens": row["train_tokens"],
                "train_flops": 6 * 84953856 * row["train_tokens"],
            },
            "metrics": {
                "reading": row["naturalized_contains"],
                "closed_book_probe": row["probe_accuracy"],
            },
            "sources": [row["checkpoint"], row["run"]],
            "detail": {
                "loss_weights": weights,
                "step": row["step"],
                "naturalized_em": row["naturalized_em"],
                "naturalized_n": row["naturalized_n"],
                "probe_n": row["probe_n"],
                "probe_chance": row["probe_chance"],
                "probe_split": probe_split(row),
                "heldout_loss": row["heldout"]["loss"],
                "heldout_loss_per_tag": {k: v["loss"]
                                         for k, v in per_tag.items()},
                "heldout_loss_factual": (round(factual_loss(per_tag), 5)
                                         if per_tag else None),
                "heldout_tokens": row["heldout"]["tokens"],
            },
            "notes": "src/lossmask arm; every arm read the same shards under "
                     "the same seed and differed only in lossmask.weights",
        })
    return rows


def default_beliefs(results: list) -> dict:
    """One sentence per arm, written from the numbers actually measured.

    The registry refuses a blank here on purpose, and a canned sentence would
    be worse than none, so the text is assembled from the arm's own result
    against the control's.
    """
    by_name = {Path(r["run"]).name: r for r in results}
    control = by_name.get("lm-d")
    out = {}
    if control is None:
        return out
    out["lm-d"] = (
        f"none; the control arm, and the reference the other three are read "
        f"against: probe {control['probe_accuracy']:.3f} against chance "
        f"{control['probe_chance']:.2f}, naturalized contains "
        f"{control['naturalized_contains']:.3f}")
    for name in ("lm-a", "lm-b", "lm-c"):
        row = by_name.get(name)
        if row is None:
            continue
        base = control["naturalized_contains"]
        retained = row["naturalized_contains"] / base if base else float("nan")
        out[name] = (
            f"probe {row['probe_accuracy']:.3f} against the control's "
            f"{control['probe_accuracy']:.3f}, reading retained "
            f"{retained:.2f} of the control against regime E's 0.83, held out "
            f"loss {row['heldout']['loss']:.4f} against "
            f"{control['heldout']['loss']:.4f}")
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m scripts.lossmask_register")
    parser.add_argument("--results", required=True)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--corpus-index", default=None,
                        help="index.json of the tagged corpus, for the tag "
                             "histogram in data_mixture")
    parser.add_argument("--belief", action="append", default=[],
                        metavar="ARM=TEXT",
                        help="override the derived belief_changed for one arm")
    parser.add_argument("--git-commit", default=None,
                        help="the commit the arms were trained at; read from "
                             "--repo when it is a checkout")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    from src.registry.store import Store

    results = json.loads(Path(args.results).read_text())["results"]
    histogram = None
    if args.corpus_index:
        index = json.loads(Path(args.corpus_index).read_text())
        names = index.get("tag_names", {})
        histogram = {names.get(k, k): v
                     for k, v in (index.get("tag_histogram") or {}).items()}
    belief = default_beliefs(results)
    for override in args.belief:
        arm, _, text = override.partition("=")
        belief[arm] = text

    rows = build_rows(results, histogram, belief,
                      git_commit=args.git_commit or head_commit(args.repo))
    if args.dry_run:
        print(json.dumps(rows, indent=2))
        return 0
    store = Store(args.repo)
    for row in rows:
        blob = store.append(row)
        print(f"appended {blob['run_id']} revision {blob['revision']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
