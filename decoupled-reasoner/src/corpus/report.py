"""Read the generated corpus and write the manifest.

    python -m src.corpus.report --dir DIR --tokenizer PATH --out DIR/manifest.json

Every count carries its denominator and nothing is pooled across components or
across families. The leakage section names the two checks it runs: a reserved
seed range interval test, and a sha256 intersection over question and answer
content hashes against the evaluation sets regenerated from their own seeds.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from collections import Counter, defaultdict

from src.corpus import audit


def _read(path):
    if not os.path.exists(path):
        return
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def relation_stats(path, encode) -> dict:
    fams = defaultdict(Counter)
    frames = Counter()
    axes = defaultdict(Counter)
    plan_len = defaultdict(Counter)
    n_ops = defaultdict(Counter)
    src = defaultdict(Counter)
    qtype = defaultdict(Counter)
    seeds = set()
    hashes = set()
    lens = defaultdict(lambda: defaultdict(list))
    n_ep = 0
    proposed = Counter()
    structural = Counter()
    for ep in _read(path):
        n_ep += 1
        fam = ep["family"]
        proposed[fam] += ep.get("n_proposed_questions", 0)
        structural[fam] += ep.get("n_structural_rejects", 0)
        fams[fam]["episodes"] += 1
        fams[fam]["questions"] += len(ep["questions"])
        fams[fam]["pages"] += len(ep["documents"])
        frames[ep["frame"]] += 1
        for k, v in ep.get("frame_axes", {}).items():
            axes[k][v] += 1
        seeds.add(ep["seed"])
        if encode is not None:
            pg = sum(len(encode(d["text"])) for d in ep["documents"])
            lens[fam][ep["frame"]].append(pg)
        for q in ep["questions"]:
            plan_len[fam][q.get("plan_len", 1)] += 1
            n_ops[fam][q.get("n_distinct_ops", 1)] += 1
            src[fam][q.get("answer_source", "unlabelled")] += 1
            qtype[fam][q.get("type", "unknown")] += 1
            hashes.add(q["hash"])
    parity = {}
    for fam, per in lens.items():
        view = {k: {"n": len(v), "median": sorted(v)[len(v) // 2]}
                for k, v in per.items() if v}
        r = audit.parity_report(view, tolerance=0.15)
        r.pop("per_frame_median", None)
        parity[fam] = r
    rej = {}
    for fam in proposed:
        tot = proposed[fam]
        rej[fam] = {"questions_proposed": tot,
                    "questions_structurally_rejected": structural[fam],
                    "rejection_rate": round(structural[fam] / tot, 4)
                    if tot else 0.0}
    return {
        "n_episodes": n_ep,
        "by_family": {k: dict(v) for k, v in fams.items()},
        "structural_question_rejection_by_family": rej,
        "n_distinct_frames": len(frames),
        "frame_use_min": min(frames.values()) if frames else 0,
        "frame_use_max": max(frames.values()) if frames else 0,
        "frame_axes": {k: dict(v) for k, v in axes.items()},
        "plan_length_by_family": {k: dict(sorted(v.items()))
                                  for k, v in plan_len.items()},
        "distinct_ops_by_family": {k: dict(sorted(v.items()))
                                   for k, v in n_ops.items()},
        "answer_source_by_family": {k: dict(v) for k, v in src.items()},
        "question_type_by_family": {k: dict(v) for k, v in qtype.items()},
        "page_token_parity_by_family": parity,
        "seeds": {"n": len(seeds), "min": min(seeds, default=None),
                  "max": max(seeds, default=None)},
        "_seeds": seeds,
        "_hashes": hashes,
    }


def plan_stats(whole_path, step_path) -> dict:
    steps = Counter()
    syms = Counter()
    qframes = Counter()
    symbol_names = Counter()
    seeds = set()
    hashes = set()
    n = 0
    for r in _read(whole_path):
        n += 1
        steps[r["n_steps"]] += 1
        syms[r["n_symbols"]] += 1
        qframes[r["qframe"]] += 1
        for s in r.get("symbols", []):
            symbol_names[s] += 1
        seeds.add(r["seed"])
        hashes.add(r["hash"])
    n_steps_examples = sum(1 for _ in _read(step_path))
    return {
        "n_whole_plans": n,
        "n_step_examples": n_steps_examples,
        "plan_length": dict(sorted(steps.items())),
        "distinct_symbols": dict(sorted(syms.items())),
        "question_frames": dict(qframes),
        "n_distinct_operator_symbols_used": len(symbol_names),
        "plans_longer_than_32": sum(v for k, v in steps.items() if k > 32),
        "plans_longer_than_3": sum(v for k, v in steps.items() if k > 3),
        "plans_with_more_than_2_symbols": sum(v for k, v in syms.items()
                                              if k > 2),
        "seeds": {"n": len(seeds), "min": min(seeds, default=None),
                  "max": max(seeds, default=None)},
        "_seeds": seeds,
        "_hashes": hashes,
    }


def mathgen_stats(path) -> dict:
    src = Counter()
    gen_src = Counter()
    levels = Counter()
    kinds = Counter()
    rel = Counter()
    seeds = set()
    hashes = set()
    n = 0
    nq = 0
    for ep in _read(path):
        n += 1
        seeds.add(ep["seed"])
        rel[ep.get("relation_kind", "unknown")] += 1
        for q in ep["questions"]:
            nq += 1
            src[q["answer_source"]] += 1
            gen_src[q.get("generator_answer_source", "unlabelled")] += 1
            levels[q.get("level")] += 1
            kinds[q.get("type")] += 1
            hashes.add(q["hash"])
    return {
        "n_universes": n, "n_questions": nq,
        "answer_source_independent_label": dict(src),
        "answer_source_generator_label": dict(gen_src),
        "levels": dict(sorted(levels.items(), key=lambda kv: str(kv[0]))),
        "recipe_kinds": dict(kinds),
        "structure_relation_kinds": dict(rel),
        "seeds": {"n": len(seeds), "min": min(seeds, default=None),
                  "max": max(seeds, default=None)},
        "_seeds": seeds,
        "_hashes": hashes,
    }


def external_stats(path) -> dict:
    fams = defaultdict(Counter)
    frames = Counter()
    lexicons = Counter()
    shapes = Counter()
    src = defaultdict(Counter)
    seeds = set()
    hashes = set()
    n = 0
    for ep in _read(path):
        n += 1
        fam = ep["family"]
        fams[fam]["episodes"] += 1
        fams[fam]["questions"] += len(ep["questions"])
        frames[ep["frame"]] += 1
        ax = ep.get("frame_axes", {})
        lexicons[ax.get("lexicon")] += 1
        shapes[ax.get("shape")] += 1
        seeds.add(ep["seed"])
        for q in ep["questions"]:
            src[fam][q.get("answer_source", "unlabelled")] += 1
            hashes.add(q["hash"])
    return {
        "n_episodes": n,
        "by_family": {k: dict(v) for k, v in fams.items()},
        "n_distinct_frames": len(frames),
        "lexicons": dict(lexicons), "shapes": dict(shapes),
        "answer_source_by_family": {k: dict(v) for k, v in src.items()},
        "seeds": {"n": len(seeds), "min": min(seeds, default=None),
                  "max": max(seeds, default=None)},
        "_seeds": seeds,
        "_hashes": hashes,
    }


# ------------------------------------------------------------- eval sets

def evaluation_set_hashes(limit_falsify: int = 250) -> dict:
    """Regenerate the evaluation sets from their own seeds and hash them.

    A seed range test alone would miss an item that two different seeds happen
    to draw identically, and it says nothing about an evaluation set built by a
    different generator. Hashing the question text with its gold answer catches
    both.
    """
    out = {}
    try:
        from src.falsify.probe import NEW_FAMILIES, generate_new_episode
        from src.skillacq.simple import SIMPLE_FAMILIES
        from src.skillacq.systems import generate_episode
        fams = sorted(SIMPLE_FAMILIES)
        hs, seeds = set(), set()
        for s in range(2_900_000, 2_900_000 + limit_falsify):
            seeds.add(s)
            ep = generate_episode(s, family=fams[s % len(fams)], n_problems=6)
            for p in ep.problems:
                hs.add(audit.question_hash(p["text"], p["answer"]))
        out["falsify_textbook"] = {"n": len(hs), "hashes": hs, "seeds": seeds}
        hs2, seeds2 = set(), set()
        newf = sorted(NEW_FAMILIES)
        for i, s in enumerate(range(2_900_000, 2_900_000 + limit_falsify)):
            seeds2.add(s)
            for fam in newf:
                ep = generate_new_episode(s, fam, n_problems=6)
                for q in ep["questions"]:
                    hs2.add(audit.question_hash(q["text"], q["answer"]))
        out["falsify_new_relations"] = {"n": len(hs2), "hashes": hs2,
                                        "seeds": seeds2}
    except Exception as exc:  # noqa: BLE001
        out["falsify_error"] = str(exc)
    try:
        from src.opgraph.data import eval_items
        grid = {"sequential": [1, 2, 3, 4, 5, 6, 7, 8],
                "sequential_paren": [2, 3, 4, 5, 6],
                "breadth": [1, 2, 3, 4, 5, 6],
                "novel": [2, 3, 4, 5, 6],
                "same_page_pair": [2], "units": [1]}
        hs, seeds = set(), set()
        for kind, depths in grid.items():
            for d in depths:
                for it in eval_items(kind, d, 40):
                    hs.add(audit.question_hash(it.text, it.gold))
                    seeds.add(it.world.seed)
        out["opgraph_eval"] = {"n": len(hs), "hashes": hs, "seeds": seeds}
    except Exception as exc:  # noqa: BLE001
        out["opgraph_error"] = str(exc)
    try:
        from src.disc.renderers import CHAIN_RENDERERS, chain_episode
        hs, seeds = set(), set()
        for name, r in CHAIN_RENDERERS.items():
            for d in (1, 2):
                for s in range(0, 250):
                    seeds.add(s)
                    ep = chain_episode(s, d, r)
                    for q in ep["questions"]:
                        hs.add(audit.question_hash(q["text"], q["answer"]))
        out["disc_template_chain"] = {"n": len(hs), "hashes": hs,
                                      "seeds": seeds}
    except Exception as exc:  # noqa: BLE001
        out["disc_error"] = str(exc)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--tokenizer", default="")
    ap.add_argument("--out", default="")
    ap.add_argument("--skip-evalsets", action="store_true")
    args = ap.parse_args(argv)
    from src.corpus.cli import (HELDOUT_FAMILIES, PLAN_STEPS, PLAN_SYMBOLS,
                                TRAIN_FAMILIES, _make_encode)
    encode, enc_kind = _make_encode(args.tokenizer)
    d = args.dir
    t0 = time.time()

    man = {
        "corpus": "decoupled-reasoner diversity corpus",
        "built_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "tokenizer": enc_kind,
        "train_families": list(TRAIN_FAMILIES),
        "heldout_families": list(HELDOUT_FAMILIES),
        "plan_step_grid": list(PLAN_STEPS),
        "plan_symbol_grid": list(PLAN_SYMBOLS),
        "components": {},
    }
    train_hashes, held_hashes = set(), set()
    train_seeds, held_seeds = set(), set()

    for name, band, fn, paths in (
            ("relation", "train", relation_stats,
             (os.path.join(d, "relation_train.jsonl"),)),
            ("relation", "heldout", relation_stats,
             (os.path.join(d, "relation_heldout.jsonl"),)),
            ("external_frames", "train", external_stats,
             (os.path.join(d, "external_train.jsonl"),)),
            ("external_frames", "heldout", external_stats,
             (os.path.join(d, "external_heldout.jsonl"),)),
            ("mathgen", "train", mathgen_stats,
             (os.path.join(d, "mathgen_train.jsonl"),)),
            ("mathgen", "heldout", mathgen_stats,
             (os.path.join(d, "mathgen_heldout.jsonl"),)),
            ("plan", "train", plan_stats,
             (os.path.join(d, "plan_train_whole.jsonl"),
              os.path.join(d, "plan_train_step.jsonl"))),
            ("plan", "heldout", plan_stats,
             (os.path.join(d, "plan_heldout_whole.jsonl"),
              os.path.join(d, "plan_heldout_step.jsonl")))):
        if fn is relation_stats:
            st = fn(paths[0], encode)
        else:
            st = fn(*paths)
        hs = st.pop("_hashes", set())
        sd = st.pop("_seeds", set())
        if band == "train":
            train_hashes |= hs
            train_seeds |= sd
        else:
            held_hashes |= hs
            held_seeds |= sd
        man["components"].setdefault(name, {})[band] = st

    for fname in ("relation_summary.json", "plan_summary.json",
                  "mathgen_summary.json", "external_summary.json"):
        p = os.path.join(d, fname)
        if os.path.exists(p):
            with open(p) as fh:
                man.setdefault("generation_summaries", {})[fname] = json.load(fh)

    ext = {} if args.skip_evalsets else evaluation_set_hashes()
    ext_hashes = {k: v["hashes"] for k, v in ext.items()
                  if isinstance(v, dict) and "hashes" in v}
    man["leakage"] = {
        "seed_check": audit.seed_disjointness(train_seeds | held_seeds),
        "hash_check": audit.hash_disjointness(train_hashes, held_hashes,
                                              ext_hashes),
        "evaluation_sets_regenerated": {
            k: v["n"] for k, v in ext.items()
            if isinstance(v, dict) and "n" in v},
        "evaluation_set_errors": {k: v for k, v in ext.items()
                                  if isinstance(v, str)},
        "corpus_bands": {
            "train": [audit.CORPUS_TRAIN_SEED0, audit.CORPUS_TRAIN_SEED1],
            "heldout": [audit.CORPUS_HELDOUT_SEED0, audit.CORPUS_HELDOUT_SEED1],
        },
        "reserved_ranges": {k: list(v) for k, v in
                            audit.RESERVED_SEED_RANGES.items()},
    }
    man["elapsed_s"] = round(time.time() - t0, 1)
    text = json.dumps(man, indent=1, default=str)
    out = args.out or os.path.join(d, "manifest.json")
    with open(out, "w") as fh:
        fh.write(text)
    print(f"wrote {out} ({len(text)} bytes)")
    print(json.dumps(man["leakage"]["seed_check"], indent=1))
    print(json.dumps({k: v for k, v in man["leakage"]["hash_check"].items()
                      if k != "external"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
