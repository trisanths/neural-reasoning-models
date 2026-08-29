"""Serve a mathgen universe through the RL retrieval channel as ordinary evidence.

A universe written by `python -m src.mathgen.cli` lands on disk as chapters,
a textbook, `chunks.jsonl`, an answer key and a manifest. This module turns
that directory into the episodes jsonl that `src.rl.env.load_tasks` reads, so
the retrieval service in `src/rl/env.py` indexes the chunks with the same BM25
oracle it uses for worldgen documents and skillacq textbook pages. Nothing
about the chunk text changes on the way in.

Three page conditions, matching the controls this project runs everywhere:

    own       the universe's own chunks
    sibling   `Structure.sibling()`, the same names and glyphs over different
              tables, rendered as a full textbook of its own
    blank     one blank page

The exercise sections of the textbook are dropped from the retrievable
library. They print exercise prompts and no answers, so keeping them would
hand a term-overlap retriever the target chapter for free on every question
without adding a single fact. The generator's own `answer_source` label is
measured against a textbook built with no exercise sections
(`label_answer_sources` calls `build_textbook(theory)` with no exercises), so
dropping them is what keeps the served pages and the label consistent.

Every question keeps its `answer_source`, `level`, `required_chapters` and
recipe in a side file keyed by episode line and qid, because `Task` carries
none of that and no figure here may be pooled across answer source.
"""

from __future__ import annotations

import json
import os

BLANK_PAGE = "This page is intentionally blank."
DROP_SECTION_KINDS = ("exercises",)
CONDITIONS = ("own", "sibling", "blank")


def read_universe(path: str) -> tuple[list[dict], dict, dict]:
    """chunks.jsonl, answer_key.json and manifest.json for one universe."""
    with open(os.path.join(path, "chunks.jsonl"), encoding="utf-8") as fh:
        chunks = [json.loads(line) for line in fh if line.strip()]
    with open(os.path.join(path, "answer_key.json"), encoding="utf-8") as fh:
        key = json.load(fh)
    with open(os.path.join(path, "manifest.json"), encoding="utf-8") as fh:
        man = json.load(fh)
    return chunks, key, man


def library(chunks: list[dict], drop=DROP_SECTION_KINDS) -> list[dict]:
    return [c for c in chunks if c.get("section_kind") not in drop]


def sibling_chunks(seed: int, offset: int = 1) -> list[dict]:
    """The sibling system's textbook, chunked the same way.

    Same system name, same object names, same glyphs, same element names,
    different tables. A page from here answers a question about this universe
    only by coincidence.
    """
    from src.mathgen import textbook as tb_mod
    from src.mathgen import theory as th_mod

    own = th_mod.build(seed)
    sib_structure = own.structure.sibling(offset)
    sib_theory = th_mod.build_theory(sib_structure)
    return tb_mod.chunks(tb_mod.build_textbook(sib_theory))


def _documents(condition: str, seed: int, own_chunks: list[dict]) -> list[dict]:
    if condition == "own":
        pages = library(own_chunks)
    elif condition == "sibling":
        pages = library(sibling_chunks(seed))
    elif condition == "blank":
        return [{"text": BLANK_PAGE, "chunk_id": "blank", "chapter": -99,
                 "section_kind": "blank", "chapter_title": "blank"}]
    else:
        raise ValueError(f"unknown condition {condition!r}")
    return [{"text": c["text"], "chunk_id": c["chunk_id"],
             "chapter": c["chapter"], "section_kind": c["section_kind"],
             "chapter_title": c.get("chapter_title", "")} for c in pages]


def write_condition(out_path: str, meta_path: str, universe_root: str,
                    seeds: list[int], condition: str) -> dict:
    """Write one episodes jsonl plus its side file. One episode per universe."""
    n_q = 0
    meta: dict = {}
    with open(out_path, "w", encoding="utf-8") as fh:
        for line_no, seed in enumerate(seeds):
            udir = os.path.join(universe_root, f"u{seed:04d}")
            own_chunks, key, man = read_universe(udir)
            documents = _documents(condition, seed, own_chunks)
            questions = []
            for ex in key["exercises"]:
                questions.append({
                    "qid": ex["exercise_id"],
                    "text": ex["prompt"],
                    "answer": ex["answer"],
                    "plan": [ex["target_node"]],
                    "type": ex["recipe"]["kind"],
                })
                meta[f"{line_no}:{ex['exercise_id']}"] = {
                    "seed": seed,
                    "system": man["system"],
                    "carrier_size": man["carrier_size"],
                    "level": ex["level"],
                    "answer_source": ex["answer_source"],
                    "answer_kind": ex["answer_kind"],
                    "recipe_kind": ex["recipe"]["kind"],
                    "required_chapters": ex["required_chapters"],
                    "chapter": ex["chapter"],
                }
                n_q += 1
            fh.write(json.dumps({
                "episode_id": f"mathgen-{seed:04d}-{condition}",
                "seed": seed,
                "world": {"domain": "mathgen"},
                "n_context": 0,
                "documents": documents,
                "questions": questions,
            }) + "\n")
    with open(meta_path, "w", encoding="utf-8") as fh:
        json.dump(meta, fh)
    return {"path": out_path, "episodes": len(seeds), "questions": n_q,
            "condition": condition}


def write_all(out_dir: str, universe_root: str, seeds: list[int]) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    report = {}
    for condition in CONDITIONS:
        report[condition] = write_condition(
            os.path.join(out_dir, f"ep_{condition}.jsonl"),
            os.path.join(out_dir, f"meta_{condition}.json"),
            universe_root, seeds, condition)
    return report


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="python -m src.mathgen.rlbridge")
    ap.add_argument("--universes", required=True, help="root holding uNNNN dirs")
    ap.add_argument("--seeds", required=True, help="'0-24' or '1,4,9'")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    from src.mathgen.cli import parse_seeds
    report = write_all(args.out, args.universes, parse_seeds(args.seeds))
    for condition, row in report.items():
        print(f"{condition:<8} {row['episodes']:>4} episodes "
              f"{row['questions']:>6} questions  {row['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
