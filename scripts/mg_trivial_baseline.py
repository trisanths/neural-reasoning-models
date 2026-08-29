"""A hand written parser answering mathgen exercises off the same served pages.

If a fifty line program reading the identical chunks matches or beats the
policy, the number is about the task and not about the substrate. This project
has already seen that happen: three untrained relation types sat at or below
chance while a regex scored 0.98 to 1.00 on the same items.

The program reads the tables page out of the served documents, rebuilds the
algebra from the printed grid, and answers. Two tiers, reported apart:

    parser   the question is parsed too. The prompt is scanned for a single
             expression over the printed element names and glyphs, and nothing
             else in the answer key is read. Coverage is reported, and items
             the parser declines are scored wrong in the all-items column.
    recipe   the structured recipe is taken from the answer key, so this tier
             answers every kind. It is an upper bound on what a program that
             reads only the chunks can do, with the question pre-parsed.

Run against `ep_sibling.jsonl` the same parser reads the rival tables and
answers the rival's way; run against `ep_blank.jsonl` it finds no table and
declines. Those are the same two controls the policy gets.
"""

from __future__ import annotations

import argparse
import json
import os
import re

from src.evals.naturalized import contains_answer, exact_match, normalize
from src.mathgen.algebra import ParseError, Structure
from src.mathgen.exercises import Undefined, compute

def shipped_correct(prediction: str, gold: str, slack: int = 6) -> bool:
    """`EpisodeEnv.is_correct` from src/rl/env.py, copied so the grader matches."""
    if exact_match(prediction, gold):
        return True
    gold_tokens = normalize(gold).split()
    if len(gold_tokens) == 1 and gold_tokens[0] in ("yes", "no"):
        return False
    pred_tokens = normalize(prediction).split()
    if not pred_tokens:
        return False
    if len(pred_tokens) > len(gold_tokens) + slack:
        return False
    return contains_answer(prediction, gold)


TABLE_HEAD = re.compile(r"The table for (.+?)\. Read the left argument")
REL_HEAD = re.compile(r"Every pair standing in the (\S+) relation")


def parse_tables(text: str):
    """Rebuild elements, glyphs, operation tables and relation pairs from prose."""
    heads = list(TABLE_HEAD.finditer(text))
    if not heads:
        return None
    bounds = []
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        rel = REL_HEAD.search(text, m.end(), end)
        bounds.append((m.group(1).strip(), m.end(), rel.start() if rel else end))

    elements, tables = None, []
    for glyph, lo, hi in bounds:
        parts = text[lo:hi].split("|")
        if len(parts) < 2:
            return None
        split = re.split(r"-{3,}", parts[1])
        if len(split) < 2:
            return None
        names = split[0].split()
        size = len(names)
        if size < 2:
            return None
        if elements is None:
            elements = names
        elif names != elements:
            return None
        rows, labels = [], [split[1].strip()]
        for piece in parts[2:]:
            words = piece.split()
            rows.append(words[:size])
            if len(words) > size:
                labels.append(words[size])
        if len(rows) != size or labels[:size] != elements:
            return None
        index = {n: i for i, n in enumerate(elements)}
        try:
            tables.append([[index[v] for v in row] for row in rows])
        except KeyError:
            return None

    glyphs = [g for g, _, _ in bounds]
    rel_glyph, pairs = "", set()
    m = REL_HEAD.search(text)
    if m:
        rel_glyph = m.group(1)
        tail = text[m.end():]
        esc = re.escape(rel_glyph)
        for lm in re.finditer(rf"(\S+)\s+{esc}\s+(.*?)(?=\S+\s+{esc}\s+|$)", tail):
            left = lm.group(1)
            if left not in elements:
                continue
            rights = re.split(r",|\band\b", lm.group(2))
            for r in rights:
                r = r.strip().strip(".")
                if r in elements:
                    pairs.add((elements.index(left), elements.index(r)))
    return Structure(
        system_name="parsed", object_name="object", object_plural="objects",
        elements=elements, op_glyphs=glyphs,
        op_names=["first", "second"][:len(glyphs)], tables=tables,
        rel_glyph=rel_glyph, rel_name="relation", rel_kind="parsed",
        rel_pairs=pairs, tag="parsed", seed=0)


def structure_from_documents(docs: list[dict]):
    for d in docs:
        s = parse_tables(d["text"])
        if s is not None:
            return s
    return None


TOKENS = re.compile(r"\(|\)|[A-Za-z]+|\S")


def read_expression(prompt: str, s: Structure) -> str | None:
    """The one expression the prompt writes, or None.

    Declines whenever the prompt binds a variable (`Let z be ...`), because
    then the expression is an argument to something else, and whenever the
    prompt writes zero or more than one expression.
    """
    if re.search(r"\blet\b", prompt, re.I):
        return None
    toks = TOKENS.findall(prompt)
    allowed = set(s.elements) | set(s.op_glyphs) | {"(", ")"}
    runs, cur = [], []
    for t in toks:
        if t in allowed:
            cur.append(t)
        else:
            if cur:
                runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    good = []
    for run in runs:
        if len(run) < 3 or not any(t in s.op_glyphs for t in run):
            continue
        text = " ".join(run)
        try:
            s.parse(text)
        except (ParseError, KeyError):
            continue
        good.append(text)
    return good[0] if len(good) == 1 else None


def row(condition: str, tier: str, seed, ex_meta: dict, question: str,
        gold: str, prediction: str, n_docs: int) -> dict:
    pred = prediction or ""
    return {
        "suite": "mathgen", "condition": condition, "decode": tier,
        "sample_index": 0, "seed": seed,
        "episode_index": ex_meta["episode_index"], "qid": ex_meta["qid"],
        "level": ex_meta["level"], "answer_source": ex_meta["answer_source"],
        "answer_kind": ex_meta["answer_kind"],
        "recipe_kind": ex_meta["recipe_kind"],
        "carrier_size": ex_meta["carrier_size"],
        "question": question, "gold": gold, "prediction": pred,
        "correct": bool(shipped_correct(pred, gold)),
        "strict_em": bool(exact_match(pred, gold)),
        "attempted": bool(pred.strip()),
        "n_rounds": 1 if n_docs else 0, "any_retrieval": bool(n_docs),
        "well_formed": True, "degenerate_queries": 0, "mean_query_len": 0.0,
        "stop_reason": "program", "n_generated": len(pred.split()),
        "pred_tokens": len(normalize(pred).split()),
        "gold_tokens": len(normalize(gold).split()),
        "retrieved_required_chapter": True,
        "answer_in_retrieved": False, "answer_in_library": False,
        "served": [], "queries": [],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes-dir", required=True)
    ap.add_argument("--universes", required=True)
    ap.add_argument("--conditions", default="own,sibling,blank")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    n_written = 0
    stats = {}
    with open(args.out, "w", encoding="utf-8") as sink:
        for condition in args.conditions.split(","):
            path = os.path.join(args.episodes_dir, f"ep_{condition}.jsonl")
            meta = json.load(open(os.path.join(
                args.episodes_dir, f"meta_{condition}.json"), encoding="utf-8"))
            parsed_ok = 0
            n_eps = 0
            with open(path, encoding="utf-8") as fh:
                for line_no, line in enumerate(fh):
                    if not line.strip():
                        continue
                    ep = json.loads(line)
                    n_eps += 1
                    docs = ep["documents"]
                    s = structure_from_documents(docs)
                    parsed_ok += int(s is not None)
                    seed = ep.get("seed")
                    key = json.load(open(os.path.join(
                        args.universes, f"u{int(seed):04d}",
                        "answer_key.json"), encoding="utf-8"))
                    recipes = {e["exercise_id"]: e["recipe"]
                               for e in key["exercises"]}
                    for q in ep["questions"]:
                        m = dict(meta[f"{line_no}:{q['qid']}"])
                        m["episode_index"] = line_no
                        m["qid"] = q["qid"]
                        for tier in ("parser", "recipe"):
                            pred = ""
                            if s is not None:
                                try:
                                    if tier == "parser":
                                        expr = read_expression(q["text"], s)
                                        pred = s.evaluate(expr) if expr else ""
                                    else:
                                        pred = compute(s, recipes[q["qid"]])
                                except (Undefined, ParseError, KeyError,
                                        ValueError, IndexError):
                                    pred = ""
                            sink.write(json.dumps(row(
                                condition, tier, seed, m, q["text"],
                                q["answer"], pred, len(docs))) + "\n")
                            n_written += 1
            stats[condition] = {"episodes": n_eps, "tables_parsed": parsed_ok}
    for c, v in stats.items():
        print(f"{c:<8} episodes {v['episodes']:>4} "
              f"tables parsed {v['tables_parsed']:>4}")
    print(f"wrote {n_written} rows to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
