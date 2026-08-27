"""Scrubbed-web retrieval episodes, the regime E3 trace source.

An episode bundles a dozen to thirty scrubbed real documents, builds an
on-the-fly BM25 index over the bundle, and renders extractive questions
whose answers are verbatim spans of specific documents, using the full
retrieval trace format of src/train/retrieval.py:

    <|world|> domain: scrubbed_web
    <|doc|> context documents (none in the query-first variant)
    <|q|> question
    <|retrieve|> query <|result|> supporting document
    <|a|> answer <|eot|>

Questions are span cloze items from src/scrub/extractive_qa, one target
document each, targets distinct within the episode. Non-query-first
episodes hold the first n_context documents in context and target only
documents outside that prefix, so the supporting evidence always arrives
through retrieval. The query-first variant holds no documents in context
at all: the question comes first and the first evidence a reader sees is
a retrieval result.

Hops are planned with build_hop_query, the greedy-then-minimax planner
behind the worldgen retrieval traces, under the same no-clairvoyance
contract: hop one draws its query terms from the question alone, and a
two-hop item first retrieves a bridge document whose terms then become
available to the second hop's query. The bridge is the document sharing
the most informative normalized terms with the question, where
informative means present in at most half the bundle, so ubiquitous
words never nominate a bridge. Every hop is verified against the actual
BM25 index (the target must rank top-1 with earlier hops excluded) and
every answer is checked to be a verbatim substring of the served
supporting document. A question whose plan cannot be verified is dropped
and counted.

Everything is deterministic in (documents, seed, knobs, state).
"""

import numpy as np

from src.scrub.extractive_qa import generate_qa
from src.train.data import render_world_preamble
from src.train.retrieval import (BM25Index, build_hop_query, norm_term,
                                 norm_terms, terms)

DOMAIN = "scrubbed_web"
BUNDLE_MIN = 12
BUNDLE_MAX = 30

# A bridge document must share at least this many informative normalized
# terms with the question before a two-hop plan is attempted, and at most
# this many bridge candidates are tried in descending overlap order.
MIN_BRIDGE_OVERLAP = 2
MAX_BRIDGE_TRIES = 4


def _seed_material(seed) -> tuple:
    if isinstance(seed, (tuple, list)):
        return tuple(int(s) for s in seed)
    return (int(seed),)


def _informative(index: BM25Index, norms: set) -> set:
    half = index.n_docs / 2
    return {t for t in norms if 0 < index.df.get(t, 0) <= half}


def _plan_two_hop(index: BM25Index, documents: list, target: int,
                  available: set):
    """Bridge-then-target plan: hop one retrieves a document sharing
    informative normalized terms with the question, hop two builds the
    target query with the bridge's terms available. Bridge candidates
    are tried in descending overlap order, index-ascending on ties, and
    the first candidate whose both hops verify wins. Returns the two
    verified rounds or None."""
    q_norms = _informative(index, {norm_term(t) for t in available})
    scored = []
    for j in range(len(documents)):
        if j == target:
            continue
        overlap = len(q_norms & set(norm_terms(documents[j]["text"])))
        if overlap >= MIN_BRIDGE_OVERLAP:
            scored.append((-overlap, j))
    for _, bridge in sorted(scored)[:MAX_BRIDGE_TRIES]:
        first = build_hop_query(index, documents, bridge, available, set())
        if first is None:
            continue
        hop2_available = available | set(terms(documents[bridge]["text"]))
        second = build_hop_query(index, documents, target, hop2_available,
                                 {bridge})
        if second is None:
            continue
        return [(first, bridge), (second, target)]
    return None


def build_web_episode(doc_texts: list, seed, n_questions: int = 4,
                      two_hop_share: float = 0.25,
                      query_first: bool = False, n_context: int = 3,
                      state: dict | None = None) -> dict:
    """One scrubbed-web retrieval episode over a bundle of scrubbed
    documents.

    Question targets are distinct and, in non-query-first episodes, lie
    outside the in-context prefix. Each candidate is planned and
    verified as described in the module docstring; unverifiable
    candidates are dropped and counted in the returned stats. A
    caller-held state dict carries the cloze deficit counters across
    episodes, exactly as in generate_qa. Deterministic in every
    argument."""
    if len(doc_texts) < 2:
        raise ValueError("an episode bundle needs at least two documents")
    material = _seed_material(seed)
    rng = np.random.default_rng(material)
    index = BM25Index(doc_texts)
    documents = [{"text": t} for t in doc_texts]
    n_ctx = 0 if query_first else min(n_context, len(doc_texts) - 1)
    candidates = list(range(n_ctx, len(doc_texts)))
    order = [candidates[i] for i in rng.permutation(len(candidates))]
    if state is None:
        state = {}
    questions = []
    dropped = 0
    hops = 0
    for target in order:
        if len(questions) >= n_questions:
            break
        qas = generate_qa(doc_texts[target], material + (101, target), 1,
                          mix={"span_cloze": 1.0}, state=state)
        two_hop = bool(rng.random() < two_hop_share)
        if not qas:
            dropped += 1
            continue
        qa = qas[0]
        available = set(terms(qa["question"]))
        plan = None
        if two_hop:
            plan = _plan_two_hop(index, documents, target, available)
        if plan is None:
            query = build_hop_query(index, documents, target, available,
                                    set())
            if query is not None:
                plan = [(query, target)]
        if plan is None or qa["answer"] not in doc_texts[target]:
            dropped += 1
            continue
        hops += len(plan)
        questions.append({
            "text": qa["question"],
            "answer": qa["answer"],
            "span_kind": qa["span_kind"],
            "plan": [[q, d] for q, d in plan],
        })
    return {
        "world": {"domain": DOMAIN},
        "documents": documents,
        "questions": questions,
        "query_first": bool(query_first),
        "n_context": n_ctx,
        "stats": {"questions": len(questions), "dropped": dropped,
                  "hops": hops},
    }


def render_web_episode(episode: dict, tokenizer) -> list:
    """Token stream for one episode in the retrieval trace layout. The
    query-first variant emits no <|doc|> region, so the first evidence a
    reader sees arrives through <|result|>."""
    sid = tokenizer.special_ids
    documents = episode["documents"]
    tokens = [sid["<|world|>"]]
    tokens.extend(tokenizer.encode(render_world_preamble(episode["world"])))
    for doc in documents[:episode.get("n_context", 0)]:
        tokens.append(sid["<|doc|>"])
        tokens.extend(tokenizer.encode(doc["text"]))
    for question in episode["questions"]:
        tokens.append(sid["<|q|>"])
        tokens.extend(tokenizer.encode(question["text"]))
        for query, doc_idx in question["plan"]:
            tokens.append(sid["<|retrieve|>"])
            tokens.extend(tokenizer.encode(query))
            tokens.append(sid["<|result|>"])
            tokens.extend(tokenizer.encode(documents[doc_idx]["text"]))
        tokens.append(sid["<|a|>"])
        tokens.extend(tokenizer.encode(question["answer"]))
        tokens.append(sid["<|eot|>"])
    return tokens


def verify_web_episode(episode: dict) -> list:
    """Re-check every trace contract from the episode dict alone.

    Returns a list of failure strings, empty when the episode is clean.
    Per question: the answer is a verbatim span of the last served
    document, that document lies outside the in-context prefix, every
    hop's query ranks its document top-1 with earlier hops excluded, and
    no query uses a surface term that was unavailable at its hop
    (question terms plus previously served documents)."""
    failures = []
    doc_texts = [d["text"] for d in episode["documents"]]
    index = BM25Index(doc_texts)
    n_ctx = episode.get("n_context", 0)
    for qi, question in enumerate(episode["questions"]):
        plan = question["plan"]
        if not plan:
            failures.append(f"q{qi}: empty plan")
            continue
        final = plan[-1][1]
        if question["answer"] not in doc_texts[final]:
            failures.append(f"q{qi}: answer not in served document")
        if final < n_ctx:
            failures.append(f"q{qi}: answer document sits in context")
        available = set(terms(question["text"]))
        served: set = set()
        for hi, (query, doc_idx) in enumerate(plan):
            if not set(terms(query)) <= available:
                failures.append(f"q{qi} hop{hi}: clairvoyant query term")
            if index.top(query, exclude=served) != doc_idx:
                failures.append(f"q{qi} hop{hi}: query does not verify")
            served.add(doc_idx)
            available |= set(terms(doc_texts[doc_idx]))
    return failures
