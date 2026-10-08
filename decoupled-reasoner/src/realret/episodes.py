"""Real questions turned into episodes the retrieval loop can walk.

An episode is the shape `src/rl/env.py` and `src/evals/interactive.py`
already read: a world header, a document bundle, and a question with a
planned sequence of retrieval rounds. Nothing about the format is new here.
What is new is that the documents are real text and the questions are ones
people wrote.

The bundle. HotpotQA ships its own retrieval corpus, ten titled paragraphs
of which two support the answer, so that bundle is used exactly as the
dataset supplies it. The two MRQA sources ship one passage document per
question, so the bundle is that document's own passages plus mined
negatives: passages belonging to other questions that share an uncommon
term with this one. A negative about the same entity is the only kind worth
having, because a bundle of unrelated pages makes any query look good.

The rounds. Round one always writes the question itself as the query,
tail-trimmed to the environment's twenty-four token cap. That is the policy
that has to transfer, because a live web search takes the question and not a
term vector, and a model trained to open with keyword soup would carry the
soup to the search box. Later rounds refine, and a refinement is built by
`src/train/retrieval.py:build_hop_query` out of the terms available at that
point, which is the question plus every page already served and nothing
else. That no-clairvoyance rule is the one `src/scrub/web_retrieval.py`
enforces, and `verify.py` re-checks it from the written episode alone.

So a one-hop item whose question already surfaces its passage is one round.
A one-hop item whose question misses is a miss and then a refinement, which
is a trace worth training on. A HotpotQA item is the question, the page it
reaches, and then a query naming the bridge that page introduced.

Every plan is verified against the same BM25 gate that serves at evaluation
time, including its tie-break policy, so a planned round is a round the
environment reproduces.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import time

from src.realret.sources import answer_in, clean, norm
from src.train import retrieval as _retrieval
from src.train.retrieval import BM25Index, norm_term, norm_terms, terms

DOMAIN = "web"
QUERY_MAX_TOKENS = 24
MAX_ROUNDS = 4
BUNDLE = 12

# A term shared by more than this many questions nominates nothing useful.
MINE_DF_MAX = 3000
MINE_DF_MIN = 2
MINE_CANDIDATES = 60
# Bridge terms a refinement may add on top of the question words.
MAX_BRIDGE_TERMS = 4

_WORD = re.compile(r"[a-z0-9]+")
_STOP = set("""a an and are as at be been but by for from had has have he her his
how i if in into is it its of on or that the their there these they this to was
were what when where which who whom why will with you your do does did not no
""".split())


def content_terms(text: str) -> set[str]:
    return {t for t in _WORD.findall(text.lower())
            if t not in _STOP and len(t) > 1}


def natural_query(question: str, tok) -> tuple[str, bool]:
    """The question as the query, compressed to the environment's token cap.

    A question that fits is written out whole, which is the case that has to
    transfer to a search box. One that does not first loses its stopwords and
    then its leading words, always on a word boundary: cutting on the raw
    token tail turns "Allie Goertz" into "z", and a query built out of word
    fragments is a query no search engine and no BM25 gate can use.

    Returns the query and whether any compression happened.
    """
    def fits(text: str) -> bool:
        return len(tok.encode(text)) <= QUERY_MAX_TOKENS

    if fits(question):
        return question, False
    words = [w for w in question.split()
             if w.lower().strip("?.,;:!\"'()") not in _STOP]
    if words and fits(" ".join(words)):
        return " ".join(words), True
    while len(words) > 1 and not fits(" ".join(words)):
        words.pop(0)
    return " ".join(words), True


# ------------------------------------------------------------------- mining

def mine_index(items: list[dict]) -> dict:
    """term -> item positions, over uncommon question terms only."""
    post: dict = {}
    for i, it in enumerate(items):
        for t in content_terms(it["question"]):
            post.setdefault(t, []).append(i)
    return {t: v for t, v in post.items()
            if MINE_DF_MIN <= len(v) <= MINE_DF_MAX}


def mine_distractors(items: list[dict], post: dict, i: int, want: int,
                     rng: random.Random) -> list[dict]:
    """Passages of other questions that share uncommon terms with this one."""
    it = items[i]
    hits: dict = {}
    for t in content_terms(it["question"]):
        for j in post.get(t, ()):  # noqa: PERF
            if j != i:
                hits[j] = hits.get(j, 0) + 1
    order = sorted(hits.items(), key=lambda kv: (-kv[1], kv[0]))[:MINE_CANDIDATES]
    answers = [a for a in it["answers"]] + [it["answer"]]
    out: list[dict] = []
    seen = {norm(d["text"]) for d in it["docs"]}
    for j, _ in order:
        for d in items[j]["docs"]:
            key = norm(d["text"])
            if key in seen or len(key) < 80:
                continue
            if any(answer_in(d["text"], a) for a in answers):
                continue
            seen.add(key)
            out.append({"title": d.get("title", ""), "text": d["text"]})
            if len(out) >= want:
                return out
    # Not enough topical negatives: fill from anywhere, which is honest
    # padding rather than a pretend hard negative.
    guard = 0
    while len(out) < want and guard < 200:
        guard += 1
        j = rng.randrange(len(items))
        if j == i:
            continue
        for d in items[j]["docs"][:1]:
            key = norm(d["text"])
            if key in seen or len(key) < 80:
                continue
            if any(answer_in(d["text"], a) for a in answers):
                continue
            seen.add(key)
            out.append({"title": d.get("title", ""), "text": d["text"]})
            break
    return out


# ------------------------------------------------------------------ planning

def _serve(index: BM25Index, texts: list[str], query: str, served: set) -> int:
    tied, _ = index.top_group(query, exclude=served)
    return _retrieval.break_tie(query, texts, tied,
                                _retrieval.RETRIEVAL_TIE_BREAK)


def _margin(index: BM25Index, query: str, target: int, exclude: set) -> float:
    """Target's BM25 score less the best other live document's."""
    best_other = float("-inf")
    for i in range(index.n_docs):
        if i == target or i in exclude:
            continue
        best_other = max(best_other, index.score(query, i))
    if best_other == float("-inf"):
        best_other = 0.0
    return index.score(query, target) - best_other


def _fit(parts: list[str], keep_tail: list[str], tok) -> str | None:
    """Join to a query inside the token cap, dropping the earliest question
    words first so the bridge terms a later hop depends on always survive."""
    head = list(parts)
    while head or keep_tail:
        q = " ".join(head + keep_tail)
        if len(tok.encode(q)) <= QUERY_MAX_TOKENS:
            return q
        if head:
            head.pop(0)
        else:
            keep_tail.pop(0)
    return None


def refine_query(question: str, index: BM25Index, texts: list[str],
                 target: int, served: set, available: set, tok) -> str | None:
    """A second query: what the question asked, plus what the pages read so
    far say about the page still wanted.

    Terms come only from the question and from documents already served, so
    the no-clairvoyance rule holds. Bridge terms are added greedily by BM25
    margin and the query is accepted the moment the gate actually serves the
    target with the earlier rounds excluded. Starting from the question's own
    words rather than from nothing is deliberate: a query builder free to
    write one rare token produces things like "her" and "to", and a policy
    trained on those carries them to a live search box.
    """
    base = [t for t in terms(question) if t not in _STOP]
    if not base:
        base = list(terms(question))
    q = _fit(base, [], tok)
    if q and _serve(index, texts, q, served) == target:
        return q

    half = max(1.0, index.n_docs / 2)
    tgt_first: dict = {}
    for pos, nt in enumerate(norm_terms(texts[target])):
        tgt_first.setdefault(nt, pos)
    base_norm = {norm_term(t) for t in base}
    cand = []
    for t in sorted(available):
        nt = norm_term(t)
        if nt in base_norm or nt not in tgt_first:
            continue
        if index.df.get(nt, 0) > half or len(t) < 2:
            continue
        cand.append(t)
    cand.sort(key=lambda t: (tgt_first[norm_term(t)], t))
    cand = cand[:MINE_CANDIDATES]

    bridge: list[str] = []
    for _ in range(MAX_BRIDGE_TERMS):
        best, best_m = None, float("-inf")
        for t in cand:
            if t in bridge:
                continue
            m = _margin(index, " ".join(base + bridge + [t]), target, served)
            if m > best_m:
                best_m, best = m, t
        if best is None:
            break
        bridge.append(best)
        q = _fit(base, list(bridge), tok)
        if q and _serve(index, texts, q, served) == target:
            return q
    return None


def plan_rounds(question: str, docs: list[dict], gold: list[int], tok,
                max_rounds: int = MAX_ROUNDS):
    """Plan the retrieval rounds. Returns (plan, reason, info).

    plan is a list of [query, doc index]. reason is "ok" or why the item is
    dropped. Round one is always the question. Later rounds are refinements
    over the terms available at that point.
    """
    texts = [d["text"] for d in docs]
    index = BM25Index(texts)
    required = list(dict.fromkeys(gold))
    served: list[int] = []
    plan: list[list] = []
    available = set(terms(question))
    trimmed = False
    misses = 0

    for r in range(max_rounds):
        if not required:
            break
        if r == 0:
            query, trimmed = natural_query(question, tok)
        else:
            query = None
            avail_norm = {norm_term(t) for t in available}
            order = sorted(
                required,
                key=lambda d: (-len(avail_norm & set(norm_terms(texts[d]))), d))
            for cand in order:
                q = refine_query(question, index, texts, cand, set(served),
                                 available, tok)
                if q is not None:
                    query = q
                    break
            if query is None:
                return None, "unplannable", {"misses": misses}
        try:
            pick = _serve(index, texts, query, set(served))
        except ValueError:
            return None, "exhausted", {"misses": misses}
        plan.append([query, int(pick)])
        served.append(int(pick))
        available |= set(terms(texts[pick]))
        if pick in required:
            required.remove(pick)
        else:
            misses += 1

    if required:
        return None, "unserved", {"misses": misses}
    return plan, "ok", {"misses": misses, "trimmed": trimmed,
                        "rounds": len(plan)}


def build_episode(item: dict, docs: list[dict], gold: list[int], tok,
                  max_rounds: int = MAX_ROUNDS):
    plan, reason, info = plan_rounds(item["question"], docs, gold, tok,
                                     max_rounds)
    if plan is None:
        return None, reason
    answer = item["answer"]
    yesno = norm(answer) in ("yes", "no")
    on_page = any(answer_in(docs[d]["text"], answer) for _, d in plan)
    if not yesno and not on_page:
        # The answer has to be readable off a page the trace served, or the
        # example teaches recall from weights rather than reading. A yes/no
        # comparison answer stands on no page by construction and is kept.
        return None, "answer_off_page"
    return {
        "world": {"domain": DOMAIN},
        "documents": [{"text": d["text"]} for d in docs],
        "n_context": 0,
        "questions": [{
            "text": item["question"],
            "answer": answer,
            "plan": plan,
            "qid": item["qid"],
        }],
        "source": item["source"],
        "qid": item["qid"],
        "hash": item["hash"],
        "hops": item["hops"],
        "kind": item.get("kind", ""),
        "level": item.get("level", ""),
        "rounds": len(plan),
        "yesno": bool(yesno),
        "misses": info.get("misses", 0),
        "trimmed": bool(info.get("trimmed")),
    }, "ok"


# ----------------------------------------------------------------------- cli

def read_items(path: str, limit: int = 0, stride: int = 1) -> list[dict]:
    out = []
    with open(path) as fh:
        for n, line in enumerate(fh):
            if n % stride:
                continue
            out.append(json.loads(line))
            if limit and len(out) >= limit:
                break
    return out


def cmd_build(args) -> int:
    from src.train.tokenizer import load_tokenizer

    tok = load_tokenizer(args.tokenizer)
    rng = random.Random(args.seed)
    items = read_items(args.items, args.limit, args.stride)
    source = items[0]["source"] if items else "?"
    post = mine_index(items) if source != "hotpot_qa" else {}

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    fh = open(args.out, "w")
    drops: dict = {}
    kept = 0
    rounds_hist: dict = {}
    miss_hist: dict = {}
    trimmed = 0
    t0 = time.time()
    for i, it in enumerate(items):
        if source == "hotpot_qa":
            docs = list(it["docs"])
            gold = list(it["gold"])
        else:
            own = list(it["docs"])
            want = max(0, args.bundle - len(own))
            extra = mine_distractors(items, post, i, want, rng) if want else []
            docs = own + extra
            gold = list(it["gold"])
        order = list(range(len(docs)))
        random.Random(f"{args.seed}:{it['qid']}").shuffle(order)
        pos = {o: k for k, o in enumerate(order)}
        docs = [docs[o] for o in order]
        gold = [pos[g] for g in gold]
        ep, reason = build_episode(it, docs, gold, tok, args.max_rounds)
        if ep is None:
            drops[reason] = drops.get(reason, 0) + 1
            continue
        fh.write(json.dumps(ep) + "\n")
        kept += 1
        rounds_hist[ep["rounds"]] = rounds_hist.get(ep["rounds"], 0) + 1
        miss_hist[ep["misses"]] = miss_hist.get(ep["misses"], 0) + 1
        trimmed += int(ep["trimmed"])
        if kept and kept % 5000 == 0:
            print(f"{source}: {kept} kept of {i+1} seen, "
                  f"{time.time() - t0:.0f}s", flush=True)
        if args.take and kept >= args.take:
            break
    fh.close()
    summary = {"source": source, "items_path": args.items, "seen": i + 1,
               "kept": kept, "drops": drops, "bundle": args.bundle,
               "max_rounds": args.max_rounds, "seed": args.seed,
               "rounds_hist": {str(k): v for k, v in sorted(rounds_hist.items())},
               "miss_hist": {str(k): v for k, v in sorted(miss_hist.items())},
               "query_trimmed": trimmed,
               "out": os.path.abspath(args.out),
               "seconds": round(time.time() - t0, 1)}
    with open(args.out + ".summary.json", "w") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps(summary), flush=True)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--items", required=True)
    b.add_argument("--out", required=True)
    b.add_argument("--tokenizer", default="/home/ec2-user/data/tokenizer_v2.json")
    b.add_argument("--bundle", type=int, default=BUNDLE)
    b.add_argument("--max-rounds", type=int, default=MAX_ROUNDS)
    b.add_argument("--limit", type=int, default=0)
    b.add_argument("--stride", type=int, default=1)
    b.add_argument("--take", type=int, default=0)
    b.add_argument("--seed", type=int, default=5150)
    b.set_defaults(fn=cmd_build)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
