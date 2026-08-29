"""Generate the corpus, audit it, and write the manifest.

    python -m src.corpus.cli relation --out DIR --procs 64
    python -m src.corpus.cli plan     --out DIR --procs 64
    python -m src.corpus.cli mathgen  --out DIR --procs 64
    python -m src.corpus.cli external --out DIR --procs 64
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

from src.corpus import audit, build, external_frames, relations
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

# Seed allocation inside the two corpus bands. Each component gets its own
# sub range so a seed identifies its component as well as its item, and so a
# component can be regenerated without disturbing another. Every value below
# lies inside [CORPUS_TRAIN_SEED0, CORPUS_TRAIN_SEED1) or inside
# [CORPUS_HELDOUT_SEED0, CORPUS_HELDOUT_SEED1), which the manifest's seed check
# re-verifies over the seeds actually written.
TRAIN_BASE = {"relation": audit.CORPUS_TRAIN_SEED0,
              "plan": audit.CORPUS_TRAIN_SEED0 + 15_000_000,
              "mathgen": audit.CORPUS_TRAIN_SEED0 + 20_000_000,
              "external": audit.CORPUS_TRAIN_SEED0 + 30_000_000}
HELDOUT_BASE = {"relation": audit.CORPUS_HELDOUT_SEED0,
                "plan": audit.CORPUS_HELDOUT_SEED0 + 300_000,
                "mathgen": audit.CORPUS_HELDOUT_SEED0 + 400_000,
                "external": audit.CORPUS_HELDOUT_SEED0 + 500_000}

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
                                                rng, band=band)
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
    seed0, n_seeds, band, answer_source = job
    out, rejects = [], Counter()
    for r in range(n_seeds):
        try:
            ep = build.build_mathgen_episode(seed0 + r,
                                             answer_source=answer_source)
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
        ep["answer_source_filter"] = answer_source
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
    for band, (s0, n) in (("train", (TRAIN_BASE["relation"],
                                     args.seeds_per_cell)),
                          ("heldout", (HELDOUT_BASE["relation"],
                                       args.heldout_per_cell))):
        fams = TRAIN_FAMILIES if band == "train" else sorted(
            relations.STRUCTURES)
        # The held-out band spans the frame bank rather than filling it: it is
        # an evaluation set, and one that used every frame at every family
        # would be larger than it needs to be to measure a frame effect.
        idx = (range(len(frames)) if band == "train"
               else range(0, len(frames), args.heldout_frame_stride))
        for family in fams:
            # The two numeric structures are the only relation families whose
            # answer is not written on a page, so they are the only source of
            # derived items here. Left at one seed block each they would be a
            # sixth of the component and the corpus would be four fifths
            # stated, which is the pooling that hid a result before. The boost
            # is applied to the seed count, not to the frames, so every family
            # still spans the whole frame bank.
            mult = (args.derived_boost
                    if family in relations.NUMERIC_STRUCTURES else 1)
            for fi in idx:
                stride = 1000 if band == "train" else 100
                jobs.append((family, fi, s0 + cell * stride, n * mult, band))
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
    for band, (s0, n) in (("train", (TRAIN_BASE["plan"],
                                     args.seeds_per_cell)),
                          ("heldout", (HELDOUT_BASE["plan"],
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
                b = s["band"]
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
    for band, s0, total in (("train", TRAIN_BASE["mathgen"], args.universes),
                            ("heldout", HELDOUT_BASE["mathgen"],
                             args.heldout_universes)):
        # Half the universes keep every exercise and half keep only the ones
        # whose answer is not written on any page. mathgen's own mix is about
        # four fifths stated, and a corpus that inherited it would be reporting
        # a stated number with a derived tail rather than two families.
        per = 25
        half = total // 2
        for i in range(0, half, per):
            jobs.append((s0 + i, min(per, half - i), band, "all"))
        for i in range(half, total, per):
            jobs.append((s0 + i, min(per, total - i), band, "derived"))
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
                counts[f"{ep['band']}:filter:{ep['answer_source_filter']}"] += 1
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


def cmd_external(args) -> int:
    """The src/frames component: its train side frames only.

    Its own `split_frames` partition decides which frames may be trained on.
    Writing its test frames into the training band would destroy that split,
    so they go to the corpus held-out band and are named in the summary.
    """
    if not external_frames.available():
        print(json.dumps({"component": "external_frames",
                          "status": "src.frames not importable"}))
        return 0
    split = external_frames.frame_split("both")
    from src.frames.generate import FAMILIES
    jobs, cell = [], 0
    for band, names, n in (("train", split["train"], args.seeds_per_cell),
                           ("heldout", split["test"] + split["bridge"],
                            args.heldout_per_cell)):
        s0 = TRAIN_BASE["external"] if band == "train" \
            else HELDOUT_BASE["external"]
        for fname in names:
            for fam in FAMILIES:
                jobs.append((fname, fam, s0 + cell * 200, n, band))
                cell += 1
    os.makedirs(args.out, exist_ok=True)
    t0 = time.time()
    counts, rejects = Counter(), defaultdict(Counter)
    fh = {b: open(os.path.join(args.out, f"external_{b}.jsonl"), "w")
          for b in ("train", "heldout")}
    with _pool(args.procs, args.tokenizer) as pool:
        for fname, fam, kept, rej in pool.imap_unordered(external_frames.cell,
                                                         jobs, chunksize=1):
            for ep in kept:
                fh[ep["band"]].write(json.dumps(ep) + "\n")
                counts[f"{ep['band']}:episodes"] += 1
                counts[f"{ep['band']}:questions"] += len(ep["questions"])
                counts[f"{ep['band']}:fam:{fam}"] += len(ep["questions"])
            for k, v in rej.items():
                rejects[fam][k] += v
    for f in fh.values():
        f.close()
    summary = {"component": "external_frames", "source": "src.frames",
               "split_policy": split["policy"], "split_seed": split["seed"],
               "n_train_frames": len(split["train"]),
               "n_test_frames": len(split["test"]),
               "n_bridge_frames": len(split["bridge"]),
               "test_lexicons": split["test_lexicons"],
               "test_shapes": split["test_shapes"],
               "heldout_frame_names": sorted(split["test"]),
               "counts": dict(counts),
               "rejects_by_family": {k: dict(v) for k, v in rejects.items()},
               "elapsed_s": round(time.time() - t0, 1)}
    with open(os.path.join(args.out, "external_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps({k: summary[k] for k in
                      ("component", "n_train_frames", "n_test_frames",
                       "n_bridge_frames", "counts", "elapsed_s")}, indent=2))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("relation", "plan", "mathgen", "external"):
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
            p.add_argument("--heldout-frame-stride", type=int, default=8)
            p.add_argument("--derived-boost", type=int, default=4)
    args = ap.parse_args(argv)
    return {"relation": cmd_relation, "plan": cmd_plan,
            "mathgen": cmd_mathgen, "external": cmd_external}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
