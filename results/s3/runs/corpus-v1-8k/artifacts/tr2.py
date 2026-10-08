"""The two shipped opgraph conditions on the transposed pages.

`src/audit/VERDICT.md` check 8 was measured on an opgraph arm in the opgraph
prompt shapes, not in the retrieval shape. Both are built here so the rebuilt
instrument can be run on the arms the number was recorded on, which is what
turns it from an untested rebuild into one that reproduces a known value.

  direct   `src/opgraph/data.py:direct_prompt`, the transposed pages in
           context, answer the question
  induce   `src/opgraph/data.py:induce_prompt`, one transposed page, write the
           operator. The induced operator is compared with the page's and with
           the training identity on eight probe pairs, which is the
           operator-level number VERDICT.md reports as 0 toward the page and
           290 toward training.
"""
from __future__ import annotations

import argparse, json, random, sys
sys.path.insert(0, "/home/ec2-user/decoupled-reasoner")

from src.corpus.transposed import transpose_page, N_CANDIDATES, _distractors, _MOD
from src.opgraph.data import direct_prompt, induce_prompt
from src.opgraph.invent import make_world, seq_flat
from src.opgraph.plan import run_plan

PROBES = [(7, 4), (12, 5), (5, 9), (8, 3), (2, 11), (11, 2), (6, 6), (9, 1)]


class FakeWorld:
    """A world whose context() serves the transposed pages."""
    def __init__(self, texts):
        self.texts = texts

    def context(self, keys=None):
        return "".join(" <|doc|> " + t for t in self.texts)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", required=True)
    ap.add_argument("--out-direct", required=True)
    ap.add_argument("--out-induce", required=True)
    args = ap.parse_args()

    n_d = n_i = 0
    seen_pages = set()
    with open(args.out_direct, "w") as fd, open(args.out_induce, "w") as fi:
        for line in open(args.episodes):
            ep = json.loads(line)
            q = ep["questions"][0]
            texts = [d["text"] for d in ep["documents"]]
            fd.write(json.dumps({
                "prompt": direct_prompt(FakeWorld(texts), q["text"]),
                "qid": q["qid"], "depth": ep["depth"], "seed": ep["seed"],
                "candidates": q["candidates"],
                "page_answer": q["page_answer"],
                "train_answer": q["train_answer"],
                "n_steps": ep["depth"], "n_symbols": 1,
            }) + "\n")
            n_d += 1
            for j, t in enumerate(texts):
                key = (ep["seed"], j)
                if key in seen_pages:
                    continue
                seen_pages.add(key)
                fi.write(json.dumps({
                    "prompt": induce_prompt(t), "seed": ep["seed"], "page": j,
                    "qid": f"w{ep['seed']}p{j}", "n_steps": 1, "n_symbols": 1,
                }) + "\n")
                n_i += 1
    print(json.dumps({"direct": n_d, "induce": n_i}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
