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
    args = ap.parse_args()
    levels = (tuple(int(x) for x in args.levels.split(","))
              if args.levels else None)
    stats = write_jsonl(args.out, range(args.start, args.start + args.count),
                        n_per_level=args.per_level, n_context=args.n_context,
                        chapters_per_universe=args.chapters_per_universe,
                        levels=levels)
    print(json.dumps(stats))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
