"""Command line over the experiment registry.

    uv run python -m scripts.exp backfill --mirror ~/registry-mirror --repo .
    uv run python -m scripts.exp list --lane falsify
    uv run python -m scripts.exp show rule-test-rlsimple-503-921
    uv run python -m scripts.exp pareto retrieval_dependency inference_flops
    uv run python -m scripts.exp add --run-id my-run --lane explore \
        --belief-changed "none" --metric reasoning=0.42
    uv run python -m scripts.exp objectives
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from src.registry import RunRecord, Store
from src.registry import backfill as backfill_mod
from src.registry import ingest, pareto, theory
from src.registry.schema import Arch, Compute, Metrics, get_path

DEFAULT_ROOT = "registry"


# ---------------------------------------------------------------------------
# formatting
# ---------------------------------------------------------------------------

def _fmt(value: Any, width: int = 9) -> str:
    if value is None:
        return "-".rjust(width)
    if isinstance(value, float):
        if value == 0:
            return "0".rjust(width)
        if abs(value) >= 1e5 or abs(value) < 1e-3:
            return f"{value:.3g}".rjust(width)
        return f"{value:.4f}".rjust(width)
    return str(value).rjust(width)


def _table(rows: list[dict[str, Any]], columns: list[tuple[str, str, int]]) -> str:
    header = " ".join(name.rjust(width) if i else name.ljust(width)
                      for i, (name, _, width) in enumerate(columns))
    lines = [header, "-" * len(header)]
    for row in rows:
        cells = []
        for i, (_, path, width) in enumerate(columns):
            value = get_path(row, path)
            if i == 0:
                cells.append(str(value if value is not None else "-").ljust(width))
            else:
                cells.append(_fmt(value, width))
        lines.append(" ".join(cells))
    return "\n".join(lines)


LIST_COLUMNS = [
    ("run_id", "run_id", 30),
    ("lane", "lane", 8),
    ("br", "branch", 4),
    ("params", "arch.params_total", 11),
    ("trainFLOP", "compute.train_flops", 10),
    ("read", "metrics.reading", 7),
    ("reason", "metrics.reasoning", 7),
    ("retdep", "metrics.retrieval_dependency", 7),
    ("probe", "metrics.closed_book_probe", 7),
    ("novel", "metrics.novel_system_acquisition", 7),
    ("ood", "metrics.ood_generalization", 7),
]


# ---------------------------------------------------------------------------
# commands
# ---------------------------------------------------------------------------

def cmd_backfill(args: argparse.Namespace) -> int:
    store = Store(args.root)
    records = backfill_mod.build_all(args.mirror, args.repo)
    if args.dry_run:
        for record in records:
            record.validate()
        print(f"{len(records)} rows validated, nothing written")
        return 0
    written = store.extend(records)
    print(f"wrote {len(written)} rows to {store.runs_path}")
    print(f"index has {store.rebuild_index()} runs")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    store = Store(args.root)
    metrics = Metrics(**_pairs(args.metric, float))
    compute = Compute(**_pairs(args.compute, float))
    arch = Arch(description=args.arch or "", **_pairs(args.arch_field, float))
    record = RunRecord(
        run_id=args.run_id,
        lane=args.lane,
        belief_changed=args.belief_changed,
        branch=args.branch,
        family=args.family,
        reasoning_suite=args.reasoning_suite,
        objective=args.objective or "",
        git_commit=args.git_commit or _head_commit(),
        data_mixture=json.loads(args.data_mixture) if args.data_mixture else {},
        arch=arch,
        compute=compute,
        metrics=metrics,
        sources=args.source or [],
        notes=args.notes or "",
    )
    blob = store.append(record)
    print(f"appended {blob['run_id']} revision {blob['revision']}")
    return 0


INGEST_READERS = {
    "rl": lambda p: ingest.rl_run_facts(p),
    "battery": ingest.read_eval_battery,
    "ablation": ingest.read_ablation,
    "dependency": ingest.read_dependency_sweep,
    "nrm": ingest.read_nrm_bench,
    "webdemo": ingest.read_web_demo,
    "config": ingest.read_train_config,
}


def cmd_ingest(args: argparse.Namespace) -> int:
    """Print what an ingester reads, so a row can be checked before it lands."""
    print(json.dumps(INGEST_READERS[args.kind](args.path), indent=2, default=str))
    return 0


def _deep_merge(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    """Patch wins leaf by leaf; a None in the patch leaves the base alone."""
    out = dict(base)
    for key, value in patch.items():
        if value is None:
            continue
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def cmd_merge(args: argparse.Namespace) -> int:
    """Fold an artefact's facts into an existing row as a new revision.

    ``add`` replaces a row wholesale, which means correcting one metric on a
    row that took a backfill and three hand edits to assemble either repeats
    every field or silently nulls the ones left out. This reads the highest
    revision of the row, overlays only the fields the artefact actually
    measured, and appends the result. A run_id with no row yet is created,
    which is why lane and belief-changed are accepted here too.
    """
    store = Store(args.root)
    facts = INGEST_READERS[args.kind](args.path)
    if isinstance(facts, list):
        raise SystemExit(f"{args.kind} reads many rows; merge takes one")

    run_id = args.run_id or facts.get("run_id")
    if not run_id:
        raise SystemExit("no --run-id and the artefact names none")

    existing = store.get(run_id)
    if existing is None:
        if not args.lane or not args.belief_changed:
            raise SystemExit(
                f"{run_id} is a new row; --lane and --belief-changed are required")
        base = RunRecord(run_id=run_id, lane=args.lane,
                         belief_changed=args.belief_changed).to_dict()
    else:
        base = {k: v for k, v in existing.items()
                if k not in ("_line", "revision", "recorded_at")}

    patch: dict[str, Any] = {
        "arch": facts.get("arch") or {},
        "compute": facts.get("compute") or {},
        "metrics": facts.get("metrics") or {},
        "detail": facts.get("detail") or {},
    }
    for field_name in ("family", "branch", "reasoning_suite", "objective"):
        value = getattr(args, field_name.replace("-", "_"), None) or facts.get(field_name)
        if value:
            patch[field_name] = value
    if args.lane:
        patch["lane"] = args.lane
    if args.belief_changed:
        patch["belief_changed"] = args.belief_changed
    if args.notes:
        patch["notes"] = args.notes

    merged = _deep_merge(base, patch)
    merged["sources"] = sorted(set(base.get("sources") or [])
                               | set(facts.get("sources") or [])
                               | set(args.source or []))
    merged["git_commit"] = args.git_commit or _head_commit() or base.get("git_commit")
    # The three evidence accuracies and the two differences derived from them
    # move together or not at all; a half-updated row would fail validation
    # against a stale derived value.
    new_metrics = facts.get("metrics") or {}
    if "acc_correct_evidence" in new_metrics:
        for name in ("retrieval_dependency", "evidence_lift"):
            merged["metrics"][name] = new_metrics.get(name)

    blob = store.append(merged)
    print(f"merged {blob['run_id']} revision {blob['revision']} "
          f"retdep {merged['metrics'].get('retrieval_dependency')}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    store = Store(args.root)
    rows = store.latest()
    if args.lane:
        rows = [r for r in rows if r.get("lane") == args.lane]
    if args.family:
        rows = [r for r in rows if r.get("family") == args.family]
    if args.branch:
        rows = [r for r in rows if (r.get("branch") or "") == args.branch]
    if args.suite:
        rows = [r for r in rows
                if args.suite in (r.get("reasoning_suite") or "")]
    if args.json:
        print(json.dumps(rows, indent=2))
        return 0
    print(_table(rows, LIST_COLUMNS))
    print(f"\n{len(rows)} rows")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    store = Store(args.root)
    row = store.get(args.run_id)
    if row is None:
        print(f"no run {args.run_id!r} in {store.runs_path}", file=sys.stderr)
        return 1
    print(json.dumps(row, indent=2, sort_keys=True))
    print("\ntheory:")
    for verdict in theory.evaluate(row):
        print(f"  {verdict['verdict']:<12} {verdict['key']}: {verdict['reason']}")
    return 0


def cmd_objectives(_: argparse.Namespace) -> int:
    for name, obj in sorted(pareto.OBJECTIVES.items()):
        print(f"{name:<22} {obj.direction:<4} {obj.label}")
    return 0


def cmd_pareto(args: argparse.Namespace) -> int:
    store = Store(args.root)
    rows = store.latest()
    if args.lane:
        rows = [r for r in rows if r.get("lane") == args.lane]
    if args.suite:
        rows = [r for r in rows
                if args.suite in (r.get("reasoning_suite") or "")]
    objectives = [pareto.resolve(name) for name in args.objectives]
    result = pareto.frontier_with_flags(rows, objectives)

    names = " vs ".join(o.name for o in objectives)
    print(f"Pareto frontier: {names}")
    for obj in objectives:
        print(f"  {obj.name}: {obj.direction}imise {obj.label}")
    print(f"  {result['n_scored']} of {len(rows)} rows have all objectives; "
          f"{len(result['skipped'])} skipped for missing values")
    print()

    width = max([len(f['row']['run_id']) for f in result["frontier_flagged"]]
                + [12])
    header = ("  " + "run_id".ljust(width) + " " + " ".join(
        o.name.rjust(14) for o in objectives) + "   lane")
    print(header)
    print("  " + "-" * (len(header) - 2))
    for flagged in result["frontier_flagged"]:
        row = flagged["row"]
        cells = " ".join(_fmt(flagged["values"][o.name], 14) for o in objectives)
        mark = " *" if flagged["promote"] else "  "
        print(f"{mark}{row['run_id'].ljust(width)} {cells}   {row.get('lane')}")

    if result["suites_mixed"]:
        print("\n  warning: this frontier puts several evaluation suites on "
              "one axis, so\n  the rows are not measuring the same task. "
              "Re-run with --suite to compare\n  like with like. Suites "
              "present:")
        for suite in result["frontier_suites"]:
            print(f"    {suite}")

    if result["n_promote"]:
        print(f"\n* {result['n_promote']} frontier rows contradict the current "
              "favoured theory. These are the rows to promote:")
        for flagged in result["frontier_flagged"]:
            if not flagged["promote"]:
                continue
            print(f"\n  {flagged['row']['run_id']}")
            for against in flagged["contradicts"]:
                print(f"    {against['key']}")
                print(f"      claim:  {against['statement']}")
                print(f"      but:    {against['reason']}")
    else:
        print("\nno frontier row contradicts the current favoured theory")

    if args.verbose and result["skipped"]:
        print("\nskipped for missing values:")
        for entry in result["skipped"]:
            print(f"  {entry['run_id']}: missing {', '.join(entry['missing'])}")
    return 0


def cmd_reindex(args: argparse.Namespace) -> int:
    store = Store(args.root)
    print(f"indexed {store.rebuild_index()} runs into {store.index_path}")
    return 0


def cmd_theory(_: argparse.Namespace) -> int:
    for claim in theory.CLAIMS:
        print(f"{claim.key}\n  {claim.statement}\n  falsified by: "
              f"{claim.falsified_by}\n")
    return 0


# ---------------------------------------------------------------------------

def _pairs(raw: list[str] | None, cast) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for item in raw or []:
        if "=" not in item:
            raise SystemExit(f"expected name=value, got {item!r}")
        name, _, value = item.partition("=")
        out[name.strip()] = None if value.strip() in ("", "null") else cast(value)
    return out


def _head_commit() -> str | None:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True,
            check=True).stdout.strip()
    except Exception:
        return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="exp", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=DEFAULT_ROOT,
                        help="registry directory (default: %(default)s)")
    subs = parser.add_subparsers(dest="command", required=True)

    p = subs.add_parser("backfill", help="rebuild rows from run artefacts")
    p.add_argument("--mirror", required=True,
                   help="local mirror of s3://.../runs/")
    p.add_argument("--repo", default=None, help="repository root, for results/")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_backfill)

    p = subs.add_parser("add", help="append one row by hand")
    p.add_argument("--run-id", required=True)
    p.add_argument("--lane", required=True, choices=["exploit", "explore", "falsify"])
    p.add_argument("--belief-changed", required=True,
                   help="what this run changed; 'none' is a valid answer")
    p.add_argument("--branch", default=None)
    p.add_argument("--family", default=None)
    p.add_argument("--reasoning-suite", default=None,
                   help="which evaluation produced --metric reasoning")
    p.add_argument("--objective", default=None)
    p.add_argument("--git-commit", default=None)
    p.add_argument("--data-mixture", default=None, help="JSON object")
    p.add_argument("--arch", default=None, help="one-line description")
    p.add_argument("--arch-field", action="append", metavar="NAME=VALUE")
    p.add_argument("--metric", action="append", metavar="NAME=VALUE")
    p.add_argument("--compute", action="append", metavar="NAME=VALUE")
    p.add_argument("--source", action="append")
    p.add_argument("--notes", default=None)
    p.set_defaults(func=cmd_add)

    p = subs.add_parser("merge", help="fold an artefact into a row, keeping the rest")
    p.add_argument("kind", choices=sorted(INGEST_READERS))
    p.add_argument("path")
    p.add_argument("--run-id", default=None,
                   help="defaults to the run_id the artefact names")
    p.add_argument("--lane", default=None,
                   choices=["exploit", "explore", "falsify"])
    p.add_argument("--belief-changed", default=None)
    p.add_argument("--branch", default=None)
    p.add_argument("--family", default=None)
    p.add_argument("--reasoning-suite", default=None)
    p.add_argument("--objective", default=None)
    p.add_argument("--git-commit", default=None)
    p.add_argument("--source", action="append")
    p.add_argument("--notes", default=None)
    p.set_defaults(func=cmd_merge)

    p = subs.add_parser("ingest", help="print what an ingester reads")
    p.add_argument("kind", choices=["rl", "battery", "ablation", "dependency", "nrm",
                                    "webdemo", "config"])
    p.add_argument("path")
    p.set_defaults(func=cmd_ingest)

    p = subs.add_parser("list", help="the table")
    p.add_argument("--lane")
    p.add_argument("--family")
    p.add_argument("--branch")
    p.add_argument("--suite", help="substring of reasoning_suite")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_list)

    p = subs.add_parser("show", help="one row in full, with theory verdicts")
    p.add_argument("run_id")
    p.set_defaults(func=cmd_show)

    p = subs.add_parser("pareto", help="the non-dominated set over objectives")
    p.add_argument("objectives", nargs="+")
    p.add_argument("--lane")
    p.add_argument("--suite",
                   help="restrict to rows whose reasoning_suite contains this, "
                        "so the reasoning axis compares like with like")
    p.add_argument("--verbose", action="store_true")
    p.set_defaults(func=cmd_pareto)

    p = subs.add_parser("objectives", help="what can be put on an axis")
    p.set_defaults(func=cmd_objectives)

    p = subs.add_parser("theory", help="the claims a frontier row is checked against")
    p.set_defaults(func=cmd_theory)

    p = subs.add_parser("reindex", help="rebuild the sqlite index from the jsonl")
    p.set_defaults(func=cmd_reindex)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    raise SystemExit(main())
