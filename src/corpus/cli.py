"""Generate the corpus, audit it, and write the manifest.

    python -m src.corpus.cli relation --out DIR --procs 64
    python -m src.corpus.cli plan     --out DIR --procs 64
    python -m src.corpus.cli mathgen  --out DIR --procs 64
    python -m src.corpus.cli parity   --out DIR --tokenizer PATH
    python -m src.corpus.cli agree    --out DIR
    python -m src.corpus.cli manifest --out DIR

CPU only. Nothing here touches a GPU, imports torch, or trains anything.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import random
import time
from collections import Counter, defaultdict

from src.corpus import audit, build, relations
from src.corpus.frames import load_frames

# Structures held out of training so that a relation type generalisation test
# still exists after this corpus is trained on. The three families the falsify
# lane measured (`inverse_table`, `chain_rule`, `band_rule`) go into training
# because they are the named ceilings, which means `src/falsify/probe.py` stops
# being an untrained relation probe the moment this corpus is used. These four
# replace it.
HELDOUT_FAMILIES = ("two_key", "exclusion", "priority_list", "agreement")
TRAIN_FAMILIES = tuple(f for f in sorted(relations.STRUCTURES)
                       if f not in HELDOUT_FAMILIES)

# Long walks live on the two single page structures, whose question names one
# scope however long the walk is. The multi page chains stay short because
# their question has to name every stage, and a depth 48 chain question would
# be longer than every other item in the corpus.
DEPTH_SCHEDULE = {
    "chain_rule": (1, 2, 3, 4, 5, 6),
    "inverse_chain": (1, 2, 3, 4, 5, 6),
    "weighted_chain": (1, 2, 3, 4, 5, 6),
    "transitive": (1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 28, 32,
                   36, 40, 44, 48),
    "modular_apply": (1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 28, 32,
                      36, 40, 44, 48),
}

PLAN_STEPS = (1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48)
PLAN_SYMBOLS = (1, 2, 3, 4, 5)

_STATE: dict = {}


# --------------------------------------------------------------- tokenizer

def _make_encode(tokenizer_path):
    if tokenizer_path and os.path.exists(tokenizer_path):
        from src.train.tokenizer import load_tokenizer
        tok = load_tokenizer(tokenizer_path)
        return tok.encode, "tokenizer_v2"
    return (lambda s: s.split()), "whitespace_proxy"


# ----------------------------------------------------------------- workers

def _init(tokenizer_path):
    from src.corpus.frames import global_reserved
    frames, source = load_frames()
    encode, kind = _make_encode(tokenizer_path)
    _STATE["frames"] = frames
    _STATE["frame_source"] = source
    _STATE["encode"] = encode
    _STATE["encode_kind"] = kind
    _STATE["global_reserved"] = global_reserved(frames)


def _relation_cell(job):
    """One (family, frame) cell: its seed block, generated and audited."""
    family, frame_idx, seed0, n_seeds, band = job
    frames = _STATE["frames"]
    frame = frames[frame_idx]
    encode = _STATE["encode"]
    depths = DEPTH_SCHEDULE.get(family, (1,))
    rng = random.Random(seed0)
    kept, rejects = [], Counter()
    for r in range(n_seeds):
        seed = seed0 + r
        depth = depths[r % len(depths)]
        try:
            ep = build.build_relation_episode(
                seed, family, frame, encode, depth=depth,
                global_reserved=_STATE["global_reserved"])
        except Exception as exc:  # noqa: BLE001
            rejects["generator_error:" + type(exc).__name__] += 1
            continue
        rep = build.audit_relation_episode(ep, frame, rng)
        ok, why = build.keep_relation_episode(ep, rep)
        if not ok:
            rejects[why] += 1
            continue
        ep["band"] = band
        ep["audit"] = rep
        ep.pop("invented_words", None)
        kept.append(ep)
        rejects["kept"] += 1
    return family, frame.fid, kept, dict(rejects)


def _plan_cell(job):
    n_steps, n_symbols, seed0, n_seeds, band = job
    from src.corpus.frames_default import LEXICONS  # noqa: F401  (import cost check)
    from src.corpus.plans import PLAN_QUESTION_FRAMES
    qframes = sorted(PLAN_QUESTION_FRAMES)
    rng = random.Random(seed0)
    whole, steps, rejects = [], [], Counter()
    for r in range(n_seeds):
        seed = seed0 + r
        qf = qframes[r % len(qframes)]
        try:
            res, why = build.build_plan_records(seed, n_steps, n_symbols, qf,
                                                rng)
        except Exception as exc:  # noqa: BLE001
            rejects["generator_error:" + type(exc).__name__] += 1
            continue
        if res is None:
            if isinstance(why, dict):
                for k, v in why.items():
                    rejects[k] += v
            else:
                rejects[str(why)] += 1
            continue
        w, st = res
        w["band"] = band
        for k, v in w.pop("rejects", {}).items():
            rejects[k] += v
        whole.append(w)
        # The stepwise arm expands one plan into one example per step. At depth
        # 48 that is 48 examples from one world, which would let the plan arm
        # dominate the corpus by token count, so a bounded sample is taken.
        if len(st) > 8:
            st = [st[0]] + rng.sample(st[1:], 7)
        steps.extend(st)
        rejects["kept"] += 1
    return n_steps, n_symbols, whole, steps, dict(rejects)


def _mathgen_cell(job):
    seed0, n_seeds, band = job
    out, rejects = [], Counter()
    for r in range(n_seeds):
        try:
            ep = build.build_mathgen_episode(seed0 + r)
        except Exception as exc:  # noqa: BLE001
            rejects["generator_error:" + type(exc).__name__] += 1
            continue
        if not ep["questions"]:
            rejects["no_exercises"] += 1
            continue
        if not ep["verification"]["all_passed"]:
            rejects["verification_failed"] += 1
            continue
        ep["band"] = band
        out.append(ep)
        rejects["kept"] += 1
    return out, dict(rejects)


# ------------------------------------------------------------------ writers

def _write(path, records):
    with open(path, "w") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")
    return len(records)


def _pool(procs, tokenizer):
    ctx = mp.get_context("fork")
    return ctx.Pool(procs, initializer=_init, initargs=(tokenizer,))


# ------------------------------------------------------------- subcommands

def cmd_relation(args) -> int:
    frames, source = load_frames()
    os.makedirs(args.out, exist_ok=True)
    jobs = []
    cell = 0
    for band, (s0, n) in (("train", (audit.CORPUS_TRAIN_SEED0,
                                     args.seeds_per_cell)),
                          ("heldout", (audit.CORPUS_HELDOUT_SEED0,
                                       args.heldout_per_cell))):
        fams = TRAIN_FAMILIES if band == "train" else sorted(
            relations.STRUCTURES)
        for family in fams:
            for fi in range(len(frames)):
                jobs.append((family, fi, s0 + cell * 1000, n, band))
                cell += 1
    t0 = time.time()
    per_family_frame = defaultdict(Counter)
    rejects = defaultdict(Counter)
    counts = Counter()
    seeds_used = set()
    fh = {b: open(os.path.join(args.out, f"relation_{b}.jsonl"), "w")
          for b in ("train", "heldout")}
    with _pool(args.procs, args.tokenizer) as pool:
        for family, fid, kept, rej in pool.imap_unordered(_relation_cell, jobs,
                                                          chunksize=1):
            band = kept[0]["band"] if kept else None
            for ep in kept:
                fh[ep["band"]].write(json.dumps(ep) + "\n")
                seeds_used.add(ep["seed"])
                counts[f"{ep['band']}:episodes"] += 1
                counts[f"{ep['band']}:questions"] += len(ep["questions"])
                per_family_frame[(ep["band"], family)][fid] += 1
            for k, v in rej.items():
                rejects[family][k] += v
            if band is None:
                rejects[family]["empty_cell"] += 1
    for f in fh.values():
        f.close()
    summary = {
        "component": "relation",
        "frame_source": source,
        "n_frames": len(frames),
        "train_families": list(TRAIN_FAMILIES),
        "heldout_families": list(HELDOUT_FAMILIES),
        "counts": dict(counts),
        "rejects_by_family": {k: dict(v) for k, v in rejects.items()},
        "seeds": {"n": len(seeds_used), "min": min(seeds_used, default=None),
                  "max": max(seeds_used, default=None)},
        "elapsed_s": round(time.time() - t0, 1),
    }
    with open(os.path.join(args.out, "relation_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps({k: summary[k] for k in
                      ("component", "frame_source", "n_frames", "counts",
                       "elapsed_s")}, indent=2))
    return 0


def cmd_plan(args) -> int:
    os.makedirs(args.out, exist_ok=True)
    jobs = []
    cell = 0
    for band, (s0, n) in (("train", (audit.CORPUS_TRAIN_SEED0 + 50_000_000,
                                     args.seeds_per_cell)),
                          ("heldout", (audit.CORPUS_HELDOUT_SEED0 + 500_000,
                                       args.heldout_per_cell))):
        for ns in PLAN_STEPS:
            for k in PLAN_SYMBOLS:
                if k > ns:
                    continue
                jobs.append((ns, k, s0 + cell * 1000, n, band))
                cell += 1
    t0 = time.time()
    rejects = defaultdict(Counter)
    counts = Counter()
    fh = {}
    for b in ("train", "heldout"):
        fh[(b, "whole")] = open(os.path.join(args.out, f"plan_{b}_whole.jsonl"),
                                "w")
        fh[(b, "step")] = open(os.path.join(args.out, f"plan_{b}_step.jsonl"),
                               "w")
    with _pool(args.procs, args.tokenizer) as pool:
        for ns, k, whole, steps, rej in pool.imap_unordered(_plan_cell, jobs,
                                                            chunksize=1):
            for w in whole:
                fh[(w["band"], "whole")].write(json.dumps(w) + "\n")
                counts[f"{w['band']}:whole"] += 1
                counts[f"{w['band']}:steps_{ns}"] += 1
                counts[f"{w['band']}:symbols_{k}"] += 1
            for s in steps:
                b = "train" if s["seed"] < audit.CORPUS_HELDOUT_SEED0 else \
                    "heldout"
                fh[(b, "step")].write(json.dumps(s) + "\n")
                counts[f"{b}:step_examples"] += 1
            for kk, v in rej.items():
                rejects[f"steps_{ns}_symbols_{k}"][kk] += v
    for f in fh.values():
        f.close()
    summary = {"component": "plan", "counts": dict(counts),
               "rejects_by_cell": {k: dict(v) for k, v in rejects.items()},
               "plan_steps": list(PLAN_STEPS),
               "plan_symbols": list(PLAN_SYMBOLS),
               "elapsed_s": round(time.time() - t0, 1)}
    with open(os.path.join(args.out, "plan_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps({"component": "plan", "counts": dict(counts),
                      "elapsed_s": summary["elapsed_s"]}, indent=2))
    return 0


def cmd_mathgen(args) -> int:
    os.makedirs(args.out, exist_ok=True)
    jobs = []
    for band, s0, total in (("train", audit.CORPUS_TRAIN_SEED0 + 60_000_000,
                             args.universes),
                            ("heldout", audit.CORPUS_HELDOUT_SEED0 + 700_000,
                             args.heldout_universes)):
        per = 25
        for i in range(0, total, per):
            jobs.append((s0 + i, min(per, total - i), band))
    t0 = time.time()
    counts = Counter()
    rejects = Counter()
    assertions = Counter()
    fh = {b: open(os.path.join(args.out, f"mathgen_{b}.jsonl"), "w")
          for b in ("train", "heldout")}
    with _pool(args.procs, args.tokenizer) as pool:
        for eps, rej in pool.imap_unordered(_mathgen_cell, jobs, chunksize=1):
            for ep in eps:
                v = ep.pop("verification")
                assertions["checked"] += v["assertions_checked"]
                assertions["passed"] += v["assertions_passed"]
                assertions["universes"] += 1
                counts[f"{ep['band']}:universes"] += 1
                counts[f"{ep['band']}:questions"] += len(ep["questions"])
                for q in ep["questions"]:
                    counts[f"{ep['band']}:src:{q['answer_source']}"] += 1
                    counts[f"{ep['band']}:level:{q['level']}"] += 1
                fh[ep["band"]].write(json.dumps(ep) + "\n")
            for k, v in rej.items():
                rejects[k] += v
    for f in fh.values():
        f.close()
    summary = {"component": "mathgen", "counts": dict(counts),
               "rejects": dict(rejects), "verification": dict(assertions),
               "elapsed_s": round(time.time() - t0, 1)}
    with open(os.path.join(args.out, "mathgen_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2)[:3000])
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("relation", "plan", "mathgen"):
        p = sub.add_parser(name)
        p.add_argument("--out", required=True)
        p.add_argument("--procs", type=int, default=32)
        p.add_argument("--tokenizer", default="")
        if name == "mathgen":
            p.add_argument("--universes", type=int, default=8000)
            p.add_argument("--heldout-universes", type=int, default=400)
        else:
            p.add_argument("--seeds-per-cell", type=int, default=48)
            p.add_argument("--heldout-per-cell", type=int, default=2)
    args = ap.parse_args(argv)
    return {"relation": cmd_relation, "plan": cmd_plan,
            "mathgen": cmd_mathgen}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
