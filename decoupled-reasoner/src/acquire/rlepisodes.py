"""The layered universe as RL episodes, shaped for src/rl/env.py.

The checkpoint we have retrieves on worldgen questions and falls silent on
these, which is not a fact about the loop but about what that policy was
trained on. So the universe exports itself in the shape src/rl/cli.py reads
and a short RL run teaches the policy to drive the retrieve-result loop on
these questions.

The training and evaluation seeds never overlap, and because every chapter
regenerates its glyphs, its notion names and its output words from its own
seed, nothing learned on a training chapter can be memorised into an answer
on an evaluation chapter. What can transfer is the behaviour: read the pages,
apply what they say. That is the same argument src/skillacq rests on, and the
same reason a seed split is enough here.

Two presentations, matching src/skillacq/episodes.py. With n_context zero the
pages arrive only through retrieval, which is the acquisition condition. With
n_context set, a prefix of the pages sits in the prompt.
"""

from __future__ import annotations

import json

from src.acquire.universe import Universe, build_universe


def to_rl_episode(universe: Universe, chapter, n_context: int = 0,
                  own_chapter_only: bool = True,
                  levels: tuple[int, ...] | None = None) -> dict:
    """One chapter as an episode. Documents are pages; questions are problems.

    own_chapter_only keeps the retrievable store to this chapter, which is
    what a training episode wants: the policy should learn to find the right
    page, not to discriminate between chapters, and the distractor chapters
    are held back for evaluation where discrimination is the point.
    """
    pages = [p for p in universe.pages
             if not own_chapter_only or p.chapter == chapter.chapter_id]
    problems = [p for p in chapter.problems
                if levels is None or p.level in levels]
    return {
        "episode_id": chapter.chapter_id,
        "seed": chapter.seed,
        "world": {"domain": "acquire_chapter"},
        "n_context": n_context,
        "documents": [{"text": p.text, "reliability": 1.0} for p in pages],
        "questions": [
            {
                "qid": prob.qid,
                "text": prob.text,
                "answer": prob.answer,
                "plan": list(prob.required_notions),
                "type": f"level{prob.level}_{prob.phrasing}",
            }
            for prob in problems
        ],
    }


def write_jsonl(path: str, seeds, n_per_level: int = 6, n_context: int = 0,
                chapters_per_universe: int = 2,
                own_chapter_only: bool = True,
                levels: tuple[int, ...] | None = None) -> dict:
    """Write episodes for a seed range. One line per chapter with problems."""
    n_eps = 0
    n_q = 0
    counts: dict = {}
    with open(path, "w") as fh:
        for seed in seeds:
            uni = build_universe(seed, n_chapters=chapters_per_universe,
                                 n_per_level=n_per_level)
            for ch in uni.chapters:
                if not ch.problems:
                    continue
                rec = to_rl_episode(uni, ch, n_context=n_context,
                                    own_chapter_only=own_chapter_only,
                                    levels=levels)
                if not rec["questions"]:
                    continue
                fh.write(json.dumps(rec) + "\n")
                n_eps += 1
                n_q += len(rec["questions"])
                for q in rec["questions"]:
                    lv = q["type"].split("_")[0]
                    counts[lv] = counts.get(lv, 0) + 1
    return {"episodes": n_eps, "questions": n_q, "path": path,
            "by_level": counts}


def write_incontext_jsonl(path: str, seeds, n_per_level: int = 8,
                          levels: tuple[int, ...] = (0,),
                          n_distractors: int = 2, seed: int = 0) -> dict:
    """One episode per problem, with its pages in the prompt and nothing to
    retrieve.

    Two attempts at teaching the retrieve-then-answer loop from cold stalled,
    each on a different saturated shaping term, and neither produced a single
    correct answer to learn from. This export removes the exploration problem
    instead of tuning around it: the pages the problem needs are already in
    context, alongside distractor pages from another notion, so the only thing
    left to learn is to read the right rule and say the word it gives.

    That is also exactly how src/acquire/loop.py calls the policy. The loop's
    searching is done in Python, and what it asks the model for is an answer
    given a card and a question. Training the ability the loop actually uses
    is the point; teaching the policy to drive its own search is a different
    experiment.
    """
    import random as _random

    rng = _random.Random(seed)
    n_eps = 0
    counts: dict = {}
    with open(path, "w") as fh:
        for s in seeds:
            uni = build_universe(s, n_chapters=2, n_per_level=n_per_level)
            pages = {p.page_id: p for p in uni.pages}
            for ch in uni.chapters:
                for prob in ch.problems:
                    if prob.level not in levels:
                        continue
                    needed = [pages[pid] for pid in prob.required_pages
                              if pid in pages]
                    pool = [p for p in uni.pages
                            if p.page_id not in prob.required_pages
                            and p.kind == "definition"]
                    extra = rng.sample(pool, min(n_distractors, len(pool)))
                    docs = needed + extra
                    rng.shuffle(docs)
                    fh.write(json.dumps({
                        "episode_id": f"{prob.qid}",
                        "seed": ch.seed,
                        "world": {"domain": "acquire_incontext"},
                        "n_context": len(docs),
                        "documents": [{"text": p.text, "reliability": 1.0}
                                      for p in docs],
                        "questions": [{
                            "qid": prob.qid, "text": prob.text,
                            "answer": prob.answer,
                            "plan": list(prob.required_notions),
                            "type": f"level{prob.level}_{prob.phrasing}",
                        }],
                    }) + "\n")
                    n_eps += 1
                    counts[prob.level] = counts.get(prob.level, 0) + 1
    return {"episodes": n_eps, "path": path, "by_level": counts}


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--start", type=int, required=True)
    ap.add_argument("--count", type=int, required=True)
    ap.add_argument("--per-level", type=int, default=6)
    ap.add_argument("--n-context", type=int, default=0)
    ap.add_argument("--chapters-per-universe", type=int, default=2)
    ap.add_argument("--levels", default="",
                    help="comma separated levels to keep, e.g. 0,1")
    ap.add_argument("--incontext", action="store_true",
                    help="one episode per problem with its pages in the prompt")
    args = ap.parse_args()
    levels = (tuple(int(x) for x in args.levels.split(","))
              if args.levels else None)
    if args.incontext:
        stats = write_incontext_jsonl(
            args.out, range(args.start, args.start + args.count),
            n_per_level=args.per_level, levels=levels or (0,))
        print(json.dumps(stats))
        return 0
    stats = write_jsonl(args.out, range(args.start, args.start + args.count),
                        n_per_level=args.per_level, n_context=args.n_context,
                        chapters_per_universe=args.chapters_per_universe,
                        levels=levels)
    print(json.dumps(stats))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
