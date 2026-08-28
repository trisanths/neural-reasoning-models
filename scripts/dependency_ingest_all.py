"""Fold every sweep artefact into the registry, one revision per row.

Each row keeps its lane, its objective and the sentence about what the run
itself changed. What lands is the three accuracies, the two differences
derived from them, the decode cost of the answers the sweep generated, the
per-family splits, and one line of notes saying what the controls did.

That note is generated from the numbers, not written about them. A row whose
accuracy barely moves when the evidence is swapped says so in its own
figures, and a sentence that says anything the figures do not is a sentence
nobody can check.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def verdict(blob: dict) -> str:
    """One line, entirely derived from the row's own numbers."""
    m = blob["metrics"]
    c = m["acc_correct_evidence"]
    w = m["acc_wrong_evidence"]
    b = m["acc_no_evidence"]
    dep = m["retrieval_dependency"]
    proto = blob.get("primary_protocol")
    n = blob.get("n_tasks")
    head = (f"dependency-sweep ({proto}, n={n}): "
            f"correct {c:.3f}, wrong evidence {w:.3f}, blank page {b:.3f}, "
            f"dependency {dep:+.3f}")
    if c <= 0.02:
        return head + "; the checkpoint answers nothing under this protocol, so the controls say nothing either"
    share = w / c if c else 0.0
    if share >= 0.75:
        return head + f"; {share:.0%} of the accuracy survives a different episode's evidence"
    if share >= 0.35:
        return head + f"; {share:.0%} of the accuracy survives a different episode's evidence, so the number is part evidence and part prior"
    return head + f"; only {share:.0%} of the accuracy survives a different episode's evidence"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True,
                    help="local mirror of runs/dependency-sweep")
    ap.add_argument("--registry", default="registry")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    paths = sorted(Path(args.root).rglob("dependency.json"))
    if not paths:
        raise SystemExit(f"no dependency.json under {args.root}")

    failed = []
    for path in paths:
        with open(path) as fh:
            blob = json.load(fh)
        cmd = [sys.executable, "-m", "scripts.exp", "--root", args.registry,
               "merge", "dependency", str(path),
               "--run-id", blob["run_id"],
               "--append-notes", verdict(blob),
               "--source", f"s3://decoupled-reasoner-009398924577/runs/"
                           f"dependency-sweep/{blob['run_id']}/dependency.json"]
        if args.dry_run:
            print(" ".join(cmd))
            continue
        r = subprocess.run(cmd, text=True)
        if r.returncode != 0:
            failed.append(blob["run_id"])
    print(f"INGEST COMPLETE rows={len(paths)} failed={failed}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
