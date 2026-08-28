"""Write every condition the falsification needs, plus the metadata to grade it.

Conditions
  textbook         the published headline: the defining pages are retrievable
  wrong_textbook   the published control: a different family's pages
  no_documents     the published control: a blank page
  swapped          same family, same words, same sentences, permuted values
  inverse_table    an untrained relation: the routing table read backwards
  chain_rule       an untrained relation: two stated hops
  band_rule        an untrained relation: three bands rather than two

Every condition writes an episodes jsonl in the shape src.rl.env.load_tasks
reads, and a meta jsonl carrying the answer set, the permuted-page answer and
the family, keyed by line number and qid.
"""

from __future__ import annotations

import argparse
import json
import os

from src.falsify.probe import (NEW_FAMILIES, candidates, generate_new_episode,
                               rebuild_system, swap_pages, twin_episode)
from src.skillacq.episodes import to_rl_episode
from src.skillacq.simple import SIMPLE_FAMILIES
from src.skillacq.systems import generate_episode


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--start", type=int, default=2900000)
    ap.add_argument("--count", type=int, default=250)
    ap.add_argument("--n-problems", type=int, default=6)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    names = (["textbook", "wrong_textbook", "no_documents", "swapped", "twin", "twin_named"]
             + list(NEW_FAMILIES))
    fh = {n: open(f"{args.out}/ep_{n}.jsonl", "w") for n in names}
    mh = {n: open(f"{args.out}/meta_{n}.jsonl", "w") for n in names}
    fams = sorted(SIMPLE_FAMILIES)

    for s in range(args.start, args.start + args.count):
        fam = fams[s % len(fams)]
        ep = generate_episode(s, family=fam, n_problems=args.n_problems)
        rec = to_rl_episode(ep, n_context=0)
        sysobj = rebuild_system(s, fam)
        cands = candidates(sysobj)
        base_meta = {"family": fam, "seed": s, "candidates": cands,
                     "answers": {p["qid"]: p["answer"] for p in ep.problems}}

        fh["textbook"].write(json.dumps(rec) + "\n")
        mh["textbook"].write(json.dumps(base_meta) + "\n")

        other = generate_episode(s + 777000, family=fams[(s + 1) % len(fams)],
                                 n_problems=args.n_problems)
        wrong = dict(rec)
        wrong["documents"] = [{"text": p} for p in other.textbook]
        fh["wrong_textbook"].write(json.dumps(wrong) + "\n")
        mh["wrong_textbook"].write(json.dumps(base_meta) + "\n")

        empty = dict(rec)
        empty["documents"] = [{"text": "This page is intentionally blank."}]
        fh["no_documents"].write(json.dumps(empty) + "\n")
        mh["no_documents"].write(json.dumps(base_meta) + "\n")

        pages, alt, informative = swap_pages(s, fam, ep.textbook, ep.problems)
        sw = dict(rec)
        sw["documents"] = [{"text": p} for p in pages]
        fh["swapped"].write(json.dumps(sw) + "\n")
        meta = dict(base_meta)
        meta["alt_answers"] = {p["qid"]: a for p, a in zip(ep.problems, alt)}
        meta["informative"] = {p["qid"]: bool(b)
                               for p, b in zip(ep.problems, informative)}
        mh["swapped"].write(json.dumps(meta) + "\n")

        for cond, attrib in (("twin", False), ("twin_named", True)):
            docs, twin_cands = twin_episode(s, fam, attributable=attrib)
            tw = dict(rec)
            tw["documents"] = docs
            fh[cond].write(json.dumps(tw) + "\n")
            tmeta = dict(base_meta)
            tmeta["twin_candidates"] = twin_cands
            mh[cond].write(json.dumps(tmeta) + "\n")

    for i, fam in enumerate(NEW_FAMILIES):
        for s in range(args.start, args.start + args.count):
            ep = generate_new_episode(s + 3000 * (i + 1), fam, n_problems=args.n_problems)
            sysobj = ep.pop("_system")
            fh[fam].write(json.dumps(ep) + "\n")
            mh[fam].write(json.dumps({
                "family": fam, "seed": ep["seed"],
                "candidates": candidates(sysobj),
                "answers": {q["qid"]: q["answer"] for q in ep["questions"]},
            }) + "\n")

    for h in list(fh.values()) + list(mh.values()):
        h.close()
    for n in names:
        with open(f"{args.out}/ep_{n}.jsonl") as f:
            print(n, sum(1 for _ in f), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
