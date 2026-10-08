"""Write a fourth page condition: only the chapters an exercise actually needs.

The full library of a mathgen universe is 95 to 151 chunks, and picking the
right one out of that is a separate ability from applying what the page says.
This project has already measured how expensive that selection is elsewhere:
going from two gold pages to a six page set cost the minimal composition repro
0.5375 down to 0.125 without touching the computation.

So this condition serves, per exercise, only the chunks belonging to the
chapters in its `required_chapters`. If a family scores zero here as well, the
zero is not about finding the page. One episode per exercise, because the
document store differs per question.
"""

from __future__ import annotations

import argparse
import json
import os

from src.mathgen.cli import parse_seeds
from src.mathgen.rlbridge import library, read_universe


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--universes", required=True)
    ap.add_argument("--seeds", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    meta = {}
    line_no = 0
    n_pages = []
    with open(os.path.join(args.out, "ep_gold.jsonl"), "w",
              encoding="utf-8") as fh:
        for seed in parse_seeds(args.seeds):
            chunks, key, man = read_universe(
                os.path.join(args.universes, f"u{seed:04d}"))
            pages = library(chunks)
            for ex in key["exercises"]:
                wanted = set(ex["required_chapters"])
                docs = [{"text": c["text"], "chunk_id": c["chunk_id"],
                         "chapter": c["chapter"],
                         "section_kind": c["section_kind"],
                         "chapter_title": c.get("chapter_title", "")}
                        for c in pages if c["chapter"] in wanted]
                if not docs:
                    docs = [{"text": "This page is intentionally blank.",
                             "chunk_id": "blank", "chapter": -99,
                             "section_kind": "blank", "chapter_title": "blank"}]
                n_pages.append(len(docs))
                fh.write(json.dumps({
                    "episode_id": f"mathgen-{seed:04d}-gold-{ex['exercise_id']}",
                    "seed": seed,
                    "world": {"domain": "mathgen"},
                    "n_context": 0,
                    "documents": docs,
                    "questions": [{
                        "qid": ex["exercise_id"],
                        "text": ex["prompt"],
                        "answer": ex["answer"],
                        "plan": [ex["target_node"]],
                        "type": ex["recipe"]["kind"],
                    }],
                }) + "\n")
                meta[f"{line_no}:{ex['exercise_id']}"] = {
                    "seed": seed, "system": man["system"],
                    "carrier_size": man["carrier_size"], "level": ex["level"],
                    "answer_source": ex["answer_source"],
                    "answer_kind": ex["answer_kind"],
                    "recipe_kind": ex["recipe"]["kind"],
                    "required_chapters": ex["required_chapters"],
                    "chapter": ex["chapter"],
                }
                line_no += 1
    with open(os.path.join(args.out, "meta_gold.json"), "w",
              encoding="utf-8") as fh:
        json.dump(meta, fh)
    print(f"gold {line_no} episodes, pages per episode "
          f"min {min(n_pages)} mean {sum(n_pages)/len(n_pages):.1f} "
          f"max {max(n_pages)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
