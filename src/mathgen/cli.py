"""Write a universe to disk: chapters, a theory graph, an answer key, a manifest.

    uv run python -m src.mathgen.cli --seed 7 --out data/mathgen/u7
    uv run python -m src.mathgen.cli --seeds 0-19 --out data/mathgen/set0 --novelty

Everything is a function of the seed, so a universe can be thrown away and
rebuilt rather than stored. What lands on disk:

    chapters/NN-slug.md      one file per chapter
    textbook.md              the whole book in reading order
    chunks.jsonl             retrieval units, each tagged with chapter,
                             section kind and the node ids it covers
    theory_graph.json        nodes and edges, the source of the prerequisite
                             levels the benchmark is built from
    answer_key.json          every exercise with its answer, its recipe, and
                             its necessity witness
    verification.json        the report from an independent recomputation
    manifest.json            counts, page total, per level and per chapter
                             breakdowns, and the verification summary

Scores against these exercises must be reported per level, per chapter and, above
all, per answer source. An exercise can be unanswerable without its chapter and
still be answerable by copying out of it, and those two families have differed
by half a point on this project before. The manifest gives all three breakdowns
and deliberately gives no pooled number. --answer-source derived keeps only the
exercises the chapters do not state the answer to.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time

from src.mathgen import exercises as ex_mod
from src.mathgen import textbook as tb_mod
from src.mathgen import theory as th_mod
from src.mathgen import verify as verify_mod


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:48]


def build_universe(seed: int, n_siblings: int = 4, variants: int = 3,
                   answer_source: str = "all") -> dict:
    """Theory, exercises and textbook for one seed, plus its verification."""
    theory = th_mod.build(seed)
    exercises = ex_mod.build_exercises(theory, n_siblings=n_siblings,
                                       variants=variants)
    if answer_source == "derived":
        exercises = [e for e in exercises
                     if e.answer_source == "derived_by_computation"]
    elif answer_source == "stated":
        exercises = [e for e in exercises
                     if e.answer_source == "stated_in_a_chapter"]
    book = tb_mod.build_textbook(theory, exercises)
    report = verify_mod.verify_universe(theory, exercises, book)
    return {"theory": theory, "exercises": exercises, "book": book,
            "verification": report}


def manifest(universe: dict, elapsed: float) -> dict:
    theory = universe["theory"]
    book = universe["book"]
    exercises = universe["exercises"]
    graph = theory.to_graph()
    s = theory.structure
    chapters = [
        {"number": c.number, "title": c.title, "register": c.register,
         "words": c.word_count(), "sections": len(c.sections),
         "node_ids": c.node_ids,
         "exercises": sum(1 for e in exercises if e.chapter == c.number)}
        for c in book.chapters
    ]
    covered = {e.chapter for e in exercises}
    return {
        "seed": s.seed,
        "system": s.system_name,
        "objects": s.object_plural,
        "carrier_size": s.size,
        "operations": s.op_glyphs,
        "relation": s.rel_glyph,
        "model_tag": s.tag,
        "pages": book.pages(),
        "words": book.word_count(),
        "words_per_page": tb_mod.WORDS_PER_PAGE,
        "chapters": len(book.chapters),
        "sections": sum(len(c.sections) for c in book.chapters),
        "dependency_depth": graph["depth"],
        "node_counts": graph["counts"],
        "chapter_detail": chapters,
        "chapters_without_exercises": sorted(
            c.number for c in book.chapters if c.number not in covered),
        "exercise_breakdown": ex_mod.breakdown(exercises),
        "candidates_rejected": ex_mod.rejected_report(theory),
        "verification": {
            "all_passed": universe["verification"]["all_passed"],
            "assertions_checked": universe["verification"]["assertions_checked"],
            "pass_rate": universe["verification"]["pass_rate"],
            "per_check": {c["name"]: c["pass_rate"]
                          for c in universe["verification"]["checks"]},
        },
        "generation_seconds": round(elapsed, 3),
    }


def write_universe(universe: dict, out_dir: str, elapsed: float) -> dict:
    theory = universe["theory"]
    book = universe["book"]
    exercises = universe["exercises"]
    os.makedirs(os.path.join(out_dir, "chapters"), exist_ok=True)

    for chapter in book.chapters:
        path = os.path.join(out_dir, "chapters",
                            f"{chapter.number:02d}-{_slug(chapter.title)}.md")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(chapter.to_markdown())

    with open(os.path.join(out_dir, "textbook.md"), "w", encoding="utf-8") as fh:
        fh.write(tb_mod.to_markdown(book))

    with open(os.path.join(out_dir, "chunks.jsonl"), "w", encoding="utf-8") as fh:
        for chunk in tb_mod.chunks(book):
            fh.write(json.dumps(chunk) + "\n")

    with open(os.path.join(out_dir, "theory_graph.json"), "w", encoding="utf-8") as fh:
        json.dump(theory.to_graph(), fh, indent=2)
        fh.write("\n")

    key = {
        "seed": theory.structure.seed,
        "system": theory.structure.system_name,
        "reporting_rule": (
            "Report accuracy per level, per chapter and per answer_source. A "
            "pooled number over these exercises can hide a whole family sitting "
            "at zero, which is the failure this generator exists to prevent. "
            "The answer_source split is the sharpest of the three: a "
            "stated_in_a_chapter exercise is answerable by copying from a "
            "retrieved page and a derived_by_computation one is not."),
        "exercises": [e.to_dict() for e in exercises],
    }
    with open(os.path.join(out_dir, "answer_key.json"), "w", encoding="utf-8") as fh:
        json.dump(key, fh, indent=2)
        fh.write("\n")

    with open(os.path.join(out_dir, "verification.json"), "w", encoding="utf-8") as fh:
        json.dump(universe["verification"], fh, indent=2)
        fh.write("\n")

    man = manifest(universe, elapsed)
    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(man, fh, indent=2)
        fh.write("\n")
    return man


def parse_seeds(spec: str) -> list:
    """Accept '7', '0-19', or '1,4,9'."""
    out: list = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part.lstrip("-"):
            lo, _, hi = part.partition("-")
            lo_i, hi_i = int(lo), int(hi)
            if hi_i < lo_i:
                raise ValueError(f"empty seed range {part!r}")
            out.extend(range(lo_i, hi_i + 1))
        else:
            out.append(int(part))
    if not out:
        raise ValueError("no seeds given")
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m src.mathgen.cli",
        description="Generate procedural mathematical universes.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--seed", type=int, help="a single seed")
    group.add_argument("--seeds", type=str,
                       help="several seeds: '0-19' or '1,4,9'")
    parser.add_argument("--out", type=str, required=True, help="output directory")
    parser.add_argument("--siblings", type=int, default=4,
                        help="rival systems each exercise is tested against")
    parser.add_argument("--variants", type=int, default=3,
                        help="how many candidate exercises each node proposes")
    parser.add_argument("--answer-source", choices=["all", "derived", "stated"],
                        default="all",
                        help="keep only exercises whose answer must be computed, "
                             "or only those the chapters state outright")
    parser.add_argument("--novelty", action="store_true",
                        help="run the novelty audit over every pair of seeds")
    parser.add_argument("--strict", action="store_true",
                        help="exit non zero if any verification check fails")
    args = parser.parse_args(argv)

    seeds = [args.seed] if args.seed is not None else parse_seeds(args.seeds)
    os.makedirs(args.out, exist_ok=True)

    manifests = []
    failed = 0
    for seed in seeds:
        started = time.time()
        universe = build_universe(seed, n_siblings=args.siblings,
                                  variants=args.variants,
                                  answer_source=args.answer_source)
        elapsed = time.time() - started
        target = args.out if len(seeds) == 1 else os.path.join(args.out, f"u{seed:04d}")
        os.makedirs(target, exist_ok=True)
        man = write_universe(universe, target, elapsed)
        manifests.append(man)
        if not man["verification"]["all_passed"]:
            failed += 1
        print(f"seed {seed:>5}  {man['system']:<12} "
              f"{man['pages']:>5} pages  {man['chapters']:>3} chapters  "
              f"depth {man['dependency_depth']}  "
              f"{man['node_counts']['theorem']:>3} theorems  "
              f"{man['exercise_breakdown']['total']:>3} exercises "
              f"({man['exercise_breakdown']['by_answer_source'].get('derived_by_computation', 0):>3} derived)  "
              f"verified {man['verification']['pass_rate']:.4f}  "
              f"{elapsed:.2f}s")

    if len(seeds) > 1:
        summary = {
            "seeds": seeds,
            "universes": len(manifests),
            "pages": _stat([m["pages"] for m in manifests]),
            "chapters": _stat([m["chapters"] for m in manifests]),
            "dependency_depth": _stat([m["dependency_depth"] for m in manifests]),
            "theorems": _stat([m["node_counts"]["theorem"] for m in manifests]),
            "refutations": _stat([m["node_counts"]["refutation"] for m in manifests]),
            "definitions": _stat([m["node_counts"]["definition"] for m in manifests]),
            "exercises": _stat([m["exercise_breakdown"]["total"] for m in manifests]),
            "verification_pass_rate": _stat(
                [m["verification"]["pass_rate"] for m in manifests]),
            "universes_fully_verified": sum(
                1 for m in manifests if m["verification"]["all_passed"]),
            "seconds_per_universe": _stat(
                [m["generation_seconds"] for m in manifests]),
            "exercises_by_level": _merge(
                [m["exercise_breakdown"]["by_level"] for m in manifests]),
            "exercises_by_answer_source": _merge(
                [m["exercise_breakdown"]["by_answer_source"] for m in manifests]),
        }
        if args.novelty:
            summary["novelty"] = verify_mod.novelty_sweep(seeds[:8])
        path = os.path.join(args.out, "summary.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(summary, fh, indent=2)
            fh.write("\n")
        print(f"wrote {path}")
        print(f"fully verified: {summary['universes_fully_verified']}"
              f"/{len(manifests)}")

    if args.strict and failed:
        print(f"{failed} universes failed verification")
        return 1
    return 0


def _stat(values: list) -> dict:
    return {"min": min(values), "mean": round(sum(values) / len(values), 4),
            "max": max(values)}


def _merge(dicts: list) -> dict:
    out: dict = {}
    for d in dicts:
        for k, v in d.items():
            out[k] = out.get(k, 0) + v
    return {k: out[k] for k in sorted(out)}


if __name__ == "__main__":
    raise SystemExit(main())
