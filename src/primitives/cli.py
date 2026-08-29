"""Command line entry point for the capability-primitive suite.

Against a checkpoint:

    uv run python -m src.primitives.cli --ckpt runs/x/latest.pt \
        --tokenizer runs/x/tokenizer.json --out results/x --n 40 \
        --mode isolated --rescue-n 20

Against a scripted stand-in, which needs no GPU and is what the
calibration evidence is produced from:

    uv run python -m src.primitives.cli --fake composition --out /tmp/fake
    uv run python -m src.primitives.cli --calibrate --out /tmp/cal

Sampled decoding is the default. Greedy decoding has produced false zeros
on this project, so --temperature 0 has to be asked for explicitly and is
recorded in the report when it is.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.primitives import PRIMITIVES
from src.primitives import report as rep
from src.primitives import runner


def _progress(msg: str) -> None:
    print(msg, flush=True)


def _build_fake(args):
    from src.primitives import fakes

    key = fakes.build_answer_key(n=args.n, seed=args.seed, mode=args.mode,
                                 ks=tuple(args.ks), rescue_n=args.rescue_n)
    if args.fake == "blind":
        return fakes.blind_model(key, seed=args.seed)
    if args.fake == "oracle":
        return fakes.oracle_model(key, seed=args.seed)
    if args.fake == "copy":
        return fakes.copy_model(key, seed=args.seed)
    if args.fake.startswith("depth"):
        return fakes.depth_model(key, int(args.fake[5:]), seed=args.seed)
    return fakes.faculty_model(key, args.fake, seed=args.seed)


def _build_checkpoint(args):
    from src.primitives.adapters import BatchedPredictor, CheckpointPredictor

    pred = CheckpointPredictor(
        args.ckpt, args.tokenizer, device=args.device,
        temperature=args.temperature, top_k=args.top_k,
        max_new_tokens=args.max_new_tokens, seed=args.decode_seed)
    batched = BatchedPredictor(pred, batch=args.batch,
                               char_budget=args.char_budget)
    pairs = runner.plan_pairs(primitives=args.primitives, n=args.n,
                              seed=args.seed, mode=args.mode,
                              ks=tuple(args.ks), rescue_n=args.rescue_n)
    _progress(f"decoding {len(pairs)} prompts in batches of {args.batch}")
    batched.warm(pairs, progress=_progress)
    return batched, pred


def calibrate(args) -> dict:
    """The stand-in matrix: does each metric respond to its own faculty.

    Every faculty stand-in is run against every primitive. The diagonal is
    the sensitivity claim and the off-diagonal is the specificity claim.
    """
    from src.primitives import fakes

    key = fakes.build_answer_key(n=args.n, seed=args.seed, mode=args.mode,
                                 ks=tuple(args.ks), rescue_n=0)
    rows = {}
    for name in ("blind",) + tuple(PRIMITIVES):
        model = (fakes.blind_model(key, seed=7) if name == "blind"
                 else fakes.faculty_model(key, name, seed=7))
        _progress(f"stand-in {name}")
        bundle = runner.run_suite(model, n=args.n, seed=args.seed,
                                  mode=args.mode, ks=tuple(args.ks),
                                  keep_records=False)
        r = bundle["report"]
        rows[name] = {p: r[p].get("headline") for p in PRIMITIVES if p in r}
        rows[name]["_misses"] = model.misses
    return rows


def render_calibration(rows: dict) -> str:
    cols = list(PRIMITIVES)
    out = ["# Metric calibration against scripted stand-ins", "",
           "Each row is a stand-in with exactly one faculty and chance",
           "behaviour in the other six, well formed throughout. A metric",
           "that works is high on its own diagonal cell and flat across the",
           "rest of its column.", "",
           "| stand-in | " + " | ".join(cols) + " |",
           "|" + "---|" * (len(cols) + 1)]
    for name, row in rows.items():
        cells = []
        for c in cols:
            v = row.get(c)
            if isinstance(v, dict):
                cells.append(",".join(str(x) for x in v.values()))
            elif v is None:
                cells.append("-")
            else:
                cells.append(f"{v:+.2f}")
        out.append(f"| {name} | " + " | ".join(cells) + " |")
    out.append("")
    out.append("Composition cells are the three depth thresholds in the order "
               "novel, relational, sequential as reported by the runner.")
    return "\n".join(out)


def rep_native(rep: dict) -> str:
    """The native-frame table. Deviations print beside the numbers."""
    out = ["# Native-frame profile", "",
           f"Mode: native. {rep['meta']['n_per_primitive']} items per "
           f"faculty, seed {rep['meta']['seed']}, "
           f"{rep['meta']['n_items']} model calls.", "",
           "The same seven faculties posed in the surface form the RL stage "
           "trained on. Read beside the suite-frame profile, never instead "
           "of it.", "",
           "| faculty | chance | strict | lenient | hedge | named nothing | "
           "parse rate | forced choice |",
           "|---|---|---|---|---|---|---|---|"]
    for fac in runner.NATIVE_FACULTIES:
        r = rep.get(fac)
        if not r:
            continue
        fc = r.get("forced_choice")
        out.append(
            f"| {fac} | {r['chance']:.3f} | "
            f"{r['strict']['acc']:.3f} [{r['strict']['ci_lo']:.3f}, "
            f"{r['strict']['ci_hi']:.3f}] n={r['n']} | "
            f"{r['lenient']['acc']:.3f} | {r['hedge_rate']['acc']:.3f} | "
            f"{r['no_candidate']['acc']:.3f} | {r['parse_rate']['acc']:.3f} | "
            + (f"{fc['acc']:.3f} [{fc['ci_lo']:.3f}, {fc['ci_hi']:.3f}]"
               + ("" if fc["above_chance"] else " (at chance)")
               if fc else "-") + " |")
    out += ["", "## What each faculty had to give up", ""]
    for fac in runner.NATIVE_FACULTIES:
        r = rep.get(fac)
        if r:
            out.append(f"- {fac}: {r['deviation']}.")
    out.append("")
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m src.primitives.cli")
    ap.add_argument("--ckpt")
    ap.add_argument("--tokenizer")
    ap.add_argument("--fake", help="blind, oracle, copy, depthN, or a "
                                   "faculty name")
    ap.add_argument("--native-frame", action="store_true",
                    help="re-render the seven faculties in the checkpoint's "
                         "trained surface form and measure both channels")
    ap.add_argument("--rescore", metavar="STEM",
                    help="recompute the grading blocks from a finished run's "
                         "records and re-render its report, no model needed")
    ap.add_argument("--calibrate", action="store_true",
                    help="run the stand-in matrix instead of a model")
    ap.add_argument("--out", required=True)
    ap.add_argument("--stem", default="primitives")
    ap.add_argument("--n", type=int, default=runner.DEFAULT_N)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--mode", default="isolated",
                    choices=("isolated", "integrated"))
    ap.add_argument("--primitives", default=None,
                    help="comma separated subset, default all seven")
    ap.add_argument("--ks", default="1,2,3,4,5")
    ap.add_argument("--rescue-n", type=int, default=0,
                    help="episodes in the causal rescue matrix, 0 to skip")
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--top-k", type=int, default=50)
    ap.add_argument("--max-new-tokens", type=int, default=48)
    ap.add_argument("--decode-seed", type=int, default=1234)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--char-budget", type=int, default=None,
                    help="prompt characters per decode batch; long prompts "
                         "therefore batch smaller. Default 1200 per slot.")
    ap.add_argument("--device", default=None)
    args = ap.parse_args(argv)
    args.ks = [int(x) for x in str(args.ks).split(",") if x.strip()]
    args.primitives = (args.primitives.split(",") if args.primitives else None)

    if args.rescore:
        # Grading rules change more often than model outputs do, and a
        # rerun costs a GPU hour to produce the same replies. The records
        # hold every reply, so a new rule is applied to a finished run
        # instead of re-earning it. This reaches only as far as the fields
        # the original grade emitted; a rule needing something the run
        # never recorded still costs a rerun.
        base = Path(args.out) / args.rescore
        report = json.loads((base.with_suffix(".json")).read_text())
        rec_path = Path(str(base) + "_records.jsonl")
        # Records older than the report they sit beside belong to an
        # earlier run. Grading those against this report silently mixes
        # two runs, and the result looks entirely normal, so refuse rather
        # than warn. This is not hypothetical: a crashed run left its
        # predecessor's records in place and a rescore picked them up.
        stale = (rec_path.exists()
                 and rec_path.stat().st_mtime
                 < (base.with_suffix(".json")).stat().st_mtime - 60)
        if stale:
            print(f"refusing: {rec_path.name} is older than the report it "
                  f"sits beside, so it belongs to an earlier run. Delete it "
                  f"and rerun, or pass a stem whose records match.",
                  file=sys.stderr)
            return 2
        records = ([json.loads(x) for x in open(rec_path) if x.strip()]
                   if rec_path.exists() else [])
        # With no records this is a re-render of the stored report, which
        # is the recovery path when a run finished its model work and then
        # died formatting the markdown.
        if records:
            report["hedging"] = runner.hedging_report(records)
        (base.with_suffix(".json")).write_text(
            json.dumps(report, indent=2, default=str))
        (base.with_suffix(".md")).write_text(rep.render_markdown(report))
        print(rep.render_markdown(report))
        print(f"\nrescored {base}.json and {base}.md from "
              f"{len(records)} records"
              if records else f"\nre-rendered {base}.md from the stored report")
        return 0

    if args.calibrate:
        rows = calibrate(args)

        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        (out / "calibration.json").write_text(json.dumps(rows, indent=2) + "\n")
        text = render_calibration(rows)
        (out / "calibration.md").write_text(text + "\n")
        print(text)
        return 0

    meta_extra = {}
    if args.fake:
        model = _build_fake(args)
    elif args.ckpt and args.tokenizer:
        model, pred = _build_checkpoint(args)
        meta_extra = {"checkpoint": args.ckpt, "decoding": pred.meta()}
    else:
        ap.error("give either --fake, or both --ckpt and --tokenizer")
        return 2

    if args.native_frame:
        rep = runner.run_native_frame(model, n=args.n, seed=args.seed,
                                      ks=tuple(args.ks), progress=_progress)
        recs = [r for f in rep.values() for r in f.pop("records", [])]
        rep["meta"] = {"mode": "native", "n_per_primitive": args.n,
                       "seed": args.seed, "n_items": len(recs),
                       "checkpoint": args.ckpt}
        out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
        (out / f"{args.stem}.json").write_text(
            json.dumps(rep, indent=2, default=str))
        with open(out / f"{args.stem}_records.jsonl", "w") as fh:
            for r in recs:
                fh.write(json.dumps(r, default=str) + "\n")
        text = rep_native(rep)
        (out / f"{args.stem}.md").write_text(text)
        print(text)
        print(f"\nwrote {out}/{args.stem}.json and .md")
        return 0

    bundle = runner.run_suite(model, primitives=args.primitives, n=args.n,
                              seed=args.seed, mode=args.mode,
                              ks=tuple(args.ks), rescue_n=args.rescue_n,
                              progress=_progress)
    bundle["report"]["meta"].update(meta_extra)
    if hasattr(model, "misses"):
        bundle["report"]["meta"]["stand_in_misses"] = model.misses
    if not args.fake and args.ckpt:
        bundle["report"]["meta"]["decoding"] = pred.meta()
        bundle["report"]["meta"]["oom_retries"] = model.retries
    jp, mp, rp = rep.write_report(bundle, args.out, stem=args.stem)
    print(rep.render_markdown(bundle["report"]))
    print(f"\nwrote {jp}\nwrote {mp}\nwrote {rp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
