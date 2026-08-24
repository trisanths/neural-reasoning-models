"""Print details for questions the trace planner drops. Diagnostic only."""

import argparse
from collections import Counter

from src.train.retrieval import (
    BM25Index, build_hop_query, terms,
)
from src.worldgen.engine import generate_episodes


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=40)
    parser.add_argument("--seed", type=int, default=20260824)
    parser.add_argument("--show", type=int, default=12)
    args = parser.parse_args(argv)

    shown = 0
    fail_kinds = Counter()
    for episode in generate_episodes(args.seed, args.episodes):
        documents = episode["documents"]
        index = BM25Index.for_documents(documents)
        for question in episode["questions"]:
            derivation = question.get("derivation") or []
            if not derivation:
                continue
            available = set(terms(question["text"]))
            exclude = set()
            failed = None
            for hop, fid in enumerate(derivation):
                supports = [i for i, d in enumerate(documents)
                            if fid in d.get("supports", [])
                            and i not in exclude]
                q = None
                for cand in supports:
                    q = build_hop_query(index, documents, cand,
                                        available, exclude)
                    if q is not None:
                        target = cand
                        break
                if q is None:
                    failed = (hop, fid, supports)
                    break
                exclude.add(target)
                available |= set(terms(documents[target]["text"]))
            if failed is None:
                continue
            hop, fid, supports = failed
            kind = (episode["world"]["domain"], question["type"],
                    f"hop{hop + 1}of{len(derivation)}")
            fail_kinds[kind] += 1
            if shown < args.show:
                shown += 1
                tgt = supports[0] if supports else None
                print(f"--- {episode['episode_id']} {question['qid']} "
                      f"{kind}")
                print(f"Q: {question['text']}")
                if tgt is not None:
                    tdoc = documents[tgt]
                    cands = [t for t in dict.fromkeys(terms(tdoc['text']))
                             if t in available]
                    print(f"target[{tgt}]: {tdoc['text']}")
                    print(f"candidates: {cands}")
                    if cands:
                        query = " ".join(cands)
                        top = index.top(query, exclude)
                        print(f"full-cand query top[{top}]: "
                              f"{documents[top]['text']} "
                              f"supports={documents[top]['supports']} "
                              f"contradicts={documents[top]['contradicts']}")
                else:
                    print("no supporting document outside exclude")
    print("\nfailure kinds:")
    for kind, n in fail_kinds.most_common():
        print(f"  {kind}: {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
