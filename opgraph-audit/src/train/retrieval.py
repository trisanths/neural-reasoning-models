"""Oracle retrieval and retrieval-trace episode rendering, SPEC.md section 2.

Protocol v1: multi-hop traces guided by the question's derivation. Every
worldgen question carries an ordered chain of fact ids, and every fact has a
supporting document. The renderer emits one retrieve-result round per
derivation hop, so the trace walks the derivation through the retriever:

    <|q|> question
    <|retrieve|> query_1 <|result|> chunk_1
    ...
    <|retrieve|> query_H <|result|> chunk_H
    <|a|> answer <|eot|>

Questions with an empty derivation (the generator's negative yes/no items)
render with zero rounds.

No clairvoyance: the hop-k query is assembled only from terms that are
available at that point, meaning terms of the question plus terms of the
chunks returned by hops 1 through k-1. The builder intersects that set with
the target document's terms and grows the query greedily, keeping the term
that most improves the BM25 margin of the target over every other candidate
document. When the greedy query falls short, a bounded minimax pass picks
integer repeat counts for the candidate terms instead: BM25 scoring is
linear in a query's term counts, so choosing counts is a small game against
the strongest rival document, approximated with multiplicative weights and
always verified against the actual retriever before use.

The oracle retriever is within-episode Okapi BM25 with three contracts on top
of the plain formula. First, scoring runs over normalized terms: a small
synonym table folds the worldgen relation surface forms together (acquired,
takeover, purchased all score as one term) and a trailing-s stemmer handles
plurals, so a question can reach a document that phrases the relation
differently. Second, ranking weights each document's BM25 score by its stated
reliability, so low-reliability contradiction documents do not outrank the
sources they corrupt. Third, inside a single question's trace retrieval is
without replacement: a hop never returns a chunk an earlier hop of the same
question already returned.

Every planned query is verified against this retriever; the hop's supporting
document must rank top-1. A question is dropped from rendering, and counted,
when any of its hops cannot be made to verify. Everything is deterministic.
"""

import json
import math
import re
from collections import Counter

from src.train.data import ShardWriter, render_world_preamble
from src.train.tokenizer import TrainTokenizer

_TERM_RE = re.compile(r"[a-z0-9]+")

# Bounded attempts for the query builder: at most this many distinct terms
# per query, at most this many terms total after minimax reweighting, and
# this many multiplicative-weights refinement steps. The emitted query stays
# well under the eval loop's query token cap.
MAX_QUERY_TERMS = 12
MAX_QUERY_LEN = 24
MINIMAX_ITERS = 160


def terms(text: str) -> list[str]:
    """Lowercased alphanumeric terms, the surface unit queries are written in."""
    return _TERM_RE.findall(text.lower())


# The synonym table folds each relation's surface forms, across document
# templates and question phrasings, into one scoring term. This is part of
# the oracle retriever's definition, not a heuristic: the worldgen vocabulary
# is closed, so the folding is exact.
_SYNONYM_GROUPS = [
    ("acquire", ["acquired", "acquisition", "acquisitions", "takeover",
                 "purchased", "purchase"]),
    ("restrict", ["restricts", "restricted", "restriction", "prohibits",
                  "bans", "banned"]),
    ("adopt", ["adopts", "adoption", "incorporated", "enacted"]),
    ("hq", ["headquartered", "headquarters", "office", "located", "base"]),
    ("born", ["born", "birth"]),
    ("parent", ["parent", "grandparent", "child", "raised"]),
    ("route", ["route", "corridor", "shipping", "ships"]),
    ("capacity", ["capacity", "carries", "containers"]),
]
_SYNONYMS = {w: c for c, ws in _SYNONYM_GROUPS for w in ws}


def norm_term(term: str) -> str:
    """Normalize one surface term for scoring: synonym fold, then a
    trailing-s stemmer for plurals."""
    if term in _SYNONYMS:
        return _SYNONYMS[term]
    if len(term) > 3 and term.endswith("s") and not term.endswith("ss"):
        return term[:-1]
    return term


def norm_terms(text: str) -> list[str]:
    """Normalized terms of a text, the unit BM25 scores over and the unit the
    no-clairvoyance containment is defined under."""
    return [norm_term(t) for t in terms(text)]


class BM25Index:
    """Okapi BM25 over normalized terms of a fixed document list, with each
    document's score weighted by its reliability for ranking."""

    def __init__(self, doc_texts: list[str], k1: float = 1.5, b: float = 0.75,
                 reliabilities: list[float] | None = None):
        if not doc_texts:
            raise ValueError("BM25Index needs at least one document")
        self.k1 = k1
        self.b = b
        self.doc_terms = [Counter(norm_terms(t)) for t in doc_texts]
        self.doc_lens = [sum(c.values()) for c in self.doc_terms]
        self.avg_len = max(1e-9, sum(self.doc_lens) / len(self.doc_lens))
        self.df: Counter = Counter()
        for counts in self.doc_terms:
            self.df.update(counts.keys())
        self.n_docs = len(doc_texts)
        if reliabilities is None:
            reliabilities = [1.0] * self.n_docs
        if len(reliabilities) != self.n_docs:
            raise ValueError("one reliability per document required")
        self.reliability = [float(r) for r in reliabilities]

    @classmethod
    def for_documents(cls, documents: list[dict]) -> "BM25Index":
        """Index episode documents with their stated reliabilities."""
        return cls([d["text"] for d in documents],
                   reliabilities=[float(d.get("reliability", 1.0))
                                  for d in documents])

    def _idf(self, term: str) -> float:
        df = self.df.get(term, 0)
        return math.log(1.0 + (self.n_docs - df + 0.5) / (df + 0.5))

    def term_score(self, term: str, doc_index: int) -> float:
        """Reliability-weighted contribution of one normalized query term
        occurrence to one document's ranking score."""
        counts = self.doc_terms[doc_index]
        tf = counts.get(term, 0)
        if tf == 0:
            return 0.0
        length = self.doc_lens[doc_index]
        denom = tf + self.k1 * (1.0 - self.b + self.b * length / self.avg_len)
        raw = self._idf(term) * tf * (self.k1 + 1.0) / denom
        return raw * self.reliability[doc_index]

    def score(self, query: str, doc_index: int) -> float:
        return sum(self.term_score(t, doc_index) for t in norm_terms(query))

    def top(self, query: str, exclude=()) -> int:
        """Index of the best scoring document outside exclude. Ties break
        toward the earliest document, so retrieval is deterministic."""
        excluded = set(exclude)
        best_idx = -1
        best_score = float("-inf")
        for i in range(self.n_docs):
            if i in excluded:
                continue
            s = self.score(query, i)
            if s > best_score:
                best_score = s
                best_idx = i
        if best_idx < 0:
            raise ValueError("every document is excluded")
        return best_idx


def _margin(index: BM25Index, query_terms: list[str], target: int,
            exclude: set) -> float:
    """Target score minus the best other candidate's score. query_terms are
    surface terms; scoring normalizes them."""
    t_score = 0.0
    others = [0.0] * index.n_docs
    for term in query_terms:
        nt = norm_term(term)
        t_score += index.term_score(nt, target)
        for i in range(index.n_docs):
            if i != target and i not in exclude:
                others[i] += index.term_score(nt, i)
    rival = max((others[i] for i in range(index.n_docs)
                 if i != target and i not in exclude), default=float("-inf"))
    return t_score - rival


def _minimax_query(index: BM25Index, target: int, candidates: list[str],
                   exclude: set) -> str | None:
    """Minimax reweighting fallback for build_hop_query.

    A query's score against any document is linear in the query's term
    counts, so choosing counts is a two-player game: pick nonnegative
    weights over the candidate norms so the target's weighted score beats
    every rival's. Multiplicative weights against the currently strongest
    rival approximates the minimax weighting; the weights are then rounded
    to small integer repeat counts at a few query lengths and each rounding
    is verified against the actual retriever. Returns the first verified
    query, or None.
    """
    norms: list[str] = []
    surface_of: dict[str, str] = {}
    for term in candidates:
        nt = norm_term(term)
        if nt not in surface_of:
            surface_of[nt] = term
            norms.append(nt)
    rivals = [d for d in range(index.n_docs)
              if d != target and d not in exclude]
    if not norms or not rivals:
        return None
    t_score = {nt: index.term_score(nt, target) for nt in norms}
    scale = max(t_score.values())
    if scale <= 0.0:
        return None
    r_score = [{nt: index.term_score(nt, d) for nt in norms} for d in rivals]

    weights = {nt: 1.0 for nt in norms}
    best_x = None
    best_gap = float("inf")
    for _ in range(MINIMAX_ITERS):
        total = sum(weights.values())
        x = {nt: w / total for nt, w in weights.items()}
        worst = None
        worst_gap = float("-inf")
        for rs in r_score:
            gap = sum(x[nt] * (rs[nt] - t_score[nt]) for nt in norms)
            if gap > worst_gap:
                worst_gap, worst = gap, rs
        if worst_gap < best_gap:
            best_gap, best_x = worst_gap, x
        for nt in norms:
            weights[nt] *= math.exp(-0.5 * (worst[nt] - t_score[nt]) / scale)
        peak = max(weights.values())
        if peak < 1e-12 or peak > 1e12:
            weights = {nt: w / peak for nt, w in weights.items()}

    for length in (6, 10, 16, MAX_QUERY_LEN):
        parts: list[str] = []
        for nt in norms:
            parts.extend([surface_of[nt]] * int(round(best_x[nt] * length)))
        if not parts or len(parts) > MAX_QUERY_LEN:
            continue
        query = " ".join(parts)
        if index.top(query, exclude) == target:
            return query
    return None


def build_hop_query(index: BM25Index, documents: list[dict], target: int,
                    available: set, exclude: set) -> str | None:
    """Build a query that ranks documents[target] top-1 under the oracle.

    Candidate terms are the available surface terms whose normalized form
    occurs in the target document, ordered by that form's first appearance in
    the document. The query grows greedily by BM25 margin; after each addition
    the actual retriever is consulted, and the first query that verifies is
    returned. If the plain greedy query never verifies, the minimax
    reweighting pass picks integer repeat counts for the candidate terms
    instead. Returns None when no verifying query exists within the bounds.
    """
    doc_norm = norm_terms(documents[target]["text"])
    first_pos = {}
    for pos, nt in enumerate(doc_norm):
        first_pos.setdefault(nt, pos)
    candidates = sorted(
        (t for t in available if norm_term(t) in first_pos),
        key=lambda t: (first_pos[norm_term(t)], t),
    )
    if not candidates:
        return None

    chosen: list[str] = []
    remaining = list(candidates)
    for _ in range(min(len(candidates), MAX_QUERY_TERMS)):
        best_term = None
        best_margin = float("-inf")
        for term in remaining:
            m = _margin(index, chosen + [term], target, exclude)
            if m > best_margin:
                best_margin = m
                best_term = term
        chosen.append(best_term)
        remaining.remove(best_term)
        query = " ".join(chosen)
        if index.top(query, exclude) == target:
            return query

    return _minimax_query(index, target, candidates, exclude)


def plan_question_trace(question: dict, documents: list[dict],
                        index: BM25Index | None) -> list[tuple[str, int]] | None:
    """Plan the retrieve-result rounds for one question.

    Returns one (query, document index) pair per derivation hop, in order, or
    None when some hop cannot be made to verify and the question must be
    dropped. An empty derivation plans as an empty list of rounds.
    """
    derivation = question.get("derivation") or []
    if not derivation:
        return []
    if index is None:
        return None
    available = set(terms(question.get("text", "")))
    exclude: set = set()
    plan: list[tuple[str, int]] = []
    for fid in derivation:
        supports = [i for i, d in enumerate(documents)
                    if fid in d.get("supports", []) and i not in exclude]
        query = None
        target = None
        for cand in supports:
            q = build_hop_query(index, documents, cand, available, exclude)
            if q is not None:
                query, target = q, cand
                break
        if query is None:
            return None
        plan.append((query, target))
        exclude.add(target)
        available |= set(terms(documents[target]["text"]))
    return plan


def plan_episode_traces(episode: dict) -> tuple[list, dict]:
    """Plan every question in an episode.

    Returns (plans, stats). plans aligns with episode["questions"]; each entry
    is a list of (query, doc index) rounds or None for a dropped question.
    stats counts questions, rendered, dropped, no_derivation (rendered with
    zero rounds), and total planned hops.
    """
    documents = episode.get("documents", [])
    index = BM25Index.for_documents(documents) if documents else None
    plans = []
    stats = {"questions": 0, "rendered": 0, "dropped": 0,
             "no_derivation": 0, "hops": 0}
    for question in episode.get("questions", []):
        stats["questions"] += 1
        plan = plan_question_trace(question, documents, index)
        plans.append(plan)
        if plan is None:
            stats["dropped"] += 1
        else:
            stats["rendered"] += 1
            stats["hops"] += len(plan)
            if not plan:
                stats["no_derivation"] += 1
    return plans, stats


def render_episode_retrieval(
    episode: dict, tokenizer: TrainTokenizer, max_doc_tokens: int | None = None
) -> list[int]:
    """Render one episode with multi-hop retrieval traces.

    The preamble and in-context documents follow render_episode exactly. The
    BM25 index covers every document in the episode, including those the
    max_doc_tokens budget excluded from the context, so the traces show
    retrieval reaching past the context window. Questions whose plan fails
    verification are omitted from the stream.
    """
    sid = tokenizer.special_ids
    documents = episode.get("documents", [])
    tokens: list[int] = [sid["<|world|>"]]
    tokens.extend(tokenizer.encode(render_world_preamble(episode.get("world", {}))))
    doc_budget = max_doc_tokens
    for doc in documents:
        doc_tokens = tokenizer.encode(doc["text"])
        cost = len(doc_tokens) + 1
        if doc_budget is not None:
            if cost > doc_budget:
                break
            doc_budget -= cost
        tokens.append(sid["<|doc|>"])
        tokens.extend(doc_tokens)

    plans, _ = plan_episode_traces(episode)
    for question, plan in zip(episode.get("questions", []), plans):
        if plan is None:
            continue
        tokens.append(sid["<|q|>"])
        tokens.extend(tokenizer.encode(question["text"]))
        for query, doc_idx in plan:
            tokens.append(sid["<|retrieve|>"])
            tokens.extend(tokenizer.encode(query))
            tokens.append(sid["<|result|>"])
            tokens.extend(tokenizer.encode(documents[doc_idx]["text"]))
        tokens.append(sid["<|a|>"])
        tokens.extend(tokenizer.encode(question["answer"]))
        tokens.append(sid["<|eot|>"])
    return tokens


def render_jsonl_to_shards_retrieval(
    jsonl_path: str,
    tokenizer: TrainTokenizer,
    out_dir: str,
    max_doc_tokens: int | None = None,
    shard_size: int = 1 << 24,
) -> int:
    """Render every episode in a worldgen JSONL file into uint16 shards with
    retrieval traces. Returns the total token count."""
    writer = ShardWriter(out_dir, shard_size=shard_size)
    total = 0
    with open(jsonl_path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            episode = json.loads(line)
            tokens = render_episode_retrieval(
                episode, tokenizer, max_doc_tokens=max_doc_tokens
            )
            writer.write(tokens)
            total += len(tokens)
    writer.close()
    return total
