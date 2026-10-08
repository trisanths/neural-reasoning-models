"""Collect the per-checkpoint sweep artefacts into one table and one frontier.

Reads every dependency.json under a directory (the local mirror of
runs/dependency-sweep/), writes combined.json and table.md next to them, and
prints the non-dominated set on retrieval dependency against decode FLOPs per
answer.

The frontier here is deliberately narrow: it only compares checkpoints whose
rows quote the same protocol, because a generation dependency and a multiple
choice dependency are not the same quantity and putting them on one axis
invites the wrong conclusion. src/registry/pareto.py draws the same frontier
off the registry once the rows are merged; this one exists so the sweep can
be read without a registry.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(root: Path) -> list[dict]:
    rows = []
    for path in sorted(root.rglob("dependency.json")):
        with open(path) as fh:
            rows.append(json.load(fh))
    return rows


def _fam_spread(blob: dict) -> str:
    """The widest and narrowest family, so a pooled number cannot hide one."""
    fams = (blob.get("per_family") or {}).get("correct") or {}
    accs = {k: v.get("accuracy") for k, v in fams.items()
            if isinstance(v, dict) and v.get("accuracy") is not None}
    if not accs:
        return ""
    lo = min(accs, key=lambda k: accs[k])
    hi = max(accs, key=lambda k: accs[k])
    if lo == hi:
        return f"{lo} {accs[lo]:.2f}"
    return f"{lo} {accs[lo]:.2f} .. {hi} {accs[hi]:.2f}"


def frontier(rows: list[dict]) -> list[dict]:
    """Non-dominated on (dependency high, decode FLOPs low), within a protocol."""
    out = []
    for protocol in sorted({r.get("primary_protocol") for r in rows}):
        group = [r for r in rows if r.get("primary_protocol") == protocol]
        for a in group:
            da = a["metrics"]["retrieval_dependency"]
            fa = (a.get("compute") or {}).get("decode_flops_per_answer")
            if da is None or fa is None:
                continue
            dominated = False
            for b in group:
                if b is a:
                    continue
                db = b["metrics"]["retrieval_dependency"]
                fb = (b.get("compute") or {}).get("decode_flops_per_answer")
                if db is None or fb is None:
                    continue
                if db >= da and fb <= fa and (db > da or fb < fa):
                    dominated = True
                    break
            if not dominated:
                out.append(a)
    return sorted(out, key=lambda r: -r["metrics"]["retrieval_dependency"])


HEADER = ("run_id", "suite", "via", "n", "correct", "wrong", "blank",
          "dep", "lift", "retr", "params", "decodeFLOP")


def rowcells(blob: dict) -> list[str]:
    m = blob["metrics"]
    cond = blob.get("conditions") or {}
    corr = cond.get("correct") or {}
    return [
        blob["run_id"],
        blob.get("suite", ""),
        blob.get("primary_protocol", ""),
        str(blob.get("n_tasks") or ""),
        f"{m['acc_correct_evidence']:.4f}",
        f"{m['acc_wrong_evidence']:.4f}",
        f"{m['acc_no_evidence']:.4f}",
        f"{m['retrieval_dependency']:+.4f}",
        f"{m['evidence_lift']:+.4f}",
        (f"{corr['any_retrieval']:.2f}" if corr.get("any_retrieval") is not None
         else "-"),
        f"{(blob.get('arch') or {}).get('params_total') or 0:,}",
        f"{(blob.get('compute') or {}).get('decode_flops_per_answer') or 0:.3g}",
    ]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    root = Path(args.root)
    out = Path(args.out or root)
    out.mkdir(parents=True, exist_ok=True)
    rows = load(root)
    if not rows:
        raise SystemExit(f"no dependency.json under {root}")
    rows.sort(key=lambda r: -r["metrics"]["retrieval_dependency"])

    front = frontier(rows)
    front_ids = {r["run_id"] for r in front}

    widths = [max(len(HEADER[i]), max(len(rowcells(r)[i]) for r in rows))
              for i in range(len(HEADER))]
    lines = [" ".join(h.ljust(w) for h, w in zip(HEADER, widths))]
    lines.append("-" * len(lines[0]))
    for r in rows:
        cells = rowcells(r)
        mark = " *" if r["run_id"] in front_ids else ""
        lines.append(" ".join(c.ljust(w) for c, w in zip(cells, widths)) + mark)
    table = "\n".join(lines)

    md = ["# Retrieval dependency over every checkpoint",
          "",
          "acc(correct evidence) minus acc(wrong evidence), on the evaluation",
          "family each checkpoint was trained for. A star marks a row on the",
          "non-dominated set of dependency against decode FLOPs per answer,",
          "within its own protocol.",
          "", "```", table, "```", "",
          "## Per-family spread, correct-evidence condition", ""]
    for r in rows:
        spread = _fam_spread(r)
        if spread:
            md.append(f"- `{r['run_id']}` {spread}")
    (out / "table.md").write_text("\n".join(md) + "\n")

    combined = {
        "n_checkpoints": len(rows),
        "frontier": [r["run_id"] for r in front],
        "rows": [
            {
                "run_id": r["run_id"],
                "suite": r.get("suite"),
                "primary_protocol": r.get("primary_protocol"),
                "n_tasks": r.get("n_tasks"),
                "metrics": r["metrics"],
                "protocol_metrics": r.get("protocol_metrics"),
                "arch": r.get("arch"),
                "compute": r.get("compute"),
                "per_family": r.get("per_family"),
                "checkpoint": r.get("checkpoint"),
                "step": r.get("step"),
            }
            for r in rows
        ],
    }
    (out / "combined.json").write_text(json.dumps(combined, indent=2) + "\n")
    print(table)
    print(f"\nfrontier: {', '.join(r['run_id'] for r in front)}")
    print(f"\nwrote {out / 'combined.json'} and {out / 'table.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
