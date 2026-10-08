"""Oracle retrieval and retrieval-trace episode rendering, SPEC.md section 2.

The retriever is within-episode BM25 over the episode's documents. Documents
in this generation are single passages, so the retrieved chunk is the whole
document text. The renderer teaches the emit-query-read loop: after each
question it writes the query the model should emit, the chunk the oracle
returns for that query, and then the answer.

Trace layout per question:

    <|q|> question <|retrieve|> query <|result|> chunk <|a|> answer <|eot|>

Everything is deterministic: the query is a fixed function of the question
text and BM25 breaks score ties by document order.
"""

import json
import math
import re
from collections import Counter

from src.train.data import ShardWriter, render_world_preamble
from src.train.tokenizer import TrainTokenizer

_TERM_RE = re.compile(r"[a-z0-9]+")


def terms(text: str) -> list[str]:
    """Lowercased alphanumeric terms, the unit BM25 scores over."""
    return _TERM_RE.findall(text.lower())


def build_query(question_text: str) -> str:
    """The oracle query for a question: its terms, joined with spaces."""
    return " ".join(terms(question_text))


class BM25Index:
    """Okapi BM25 over a fixed list of document texts."""

    def __init__(self, doc_texts: list[str], k1: float = 1.5, b: float = 0.75):
        if not doc_texts:
            raise ValueError("BM25Index needs at least one document")
        self.k1 = k1
        self.b = b
        self.doc_terms = [Counter(terms(t)) for t in doc_texts]
        self.doc_lens = [sum(c.values()) for c in self.doc_terms]
        self.avg_len = max(1e-9, sum(self.doc_lens) / len(self.doc_lens))
        self.df: Counter = Counter()
        for counts in self.doc_terms:
            self.df.update(counts.keys())
        self.n_docs = len(doc_texts)

    def _idf(self, term: str) -> float:
        df = self.df.get(term, 0)
        return math.log(1.0 + (self.n_docs - df + 0.5) / (df + 0.5))

    def score(self, query: str, doc_index: int) -> float:
        counts = self.doc_terms[doc_index]
        length = self.doc_lens[doc_index]
        score = 0.0
        for term in terms(query):
            tf = counts.get(term, 0)
            if tf == 0:
                continue
            denom = tf + self.k1 * (1.0 - self.b + self.b * length / self.avg_len)
            score += self._idf(term) * tf * (self.k1 + 1.0) / denom
        return score

    def top(self, query: str) -> int:
        """Index of the best scoring document. Ties break toward the earliest
        document, so retrieval is deterministic."""
        best_idx = 0
        best_score = float("-inf")
        for i in range(self.n_docs):
            s = self.score(query, i)
            if s > best_score:
                best_score = s
                best_idx = i
        return best_idx


def render_episode_retrieval(
    episode: dict, tokenizer: TrainTokenizer, max_doc_tokens: int | None = None
) -> list[int]:
    """Render one episode with retrieval traces.

    The preamble and in-context documents follow render_episode exactly. The
    BM25 index covers every document in the episode, including those the
    max_doc_tokens budget excluded from the context, so the traces show
    retrieval reaching past the context window.
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

    index = BM25Index([d["text"] for d in documents]) if documents else None
    for question in episode.get("questions", []):
        tokens.append(sid["<|q|>"])
        tokens.extend(tokenizer.encode(question["text"]))
        if index is not None:
            query = build_query(question["text"])
            chunk = documents[index.top(query)]["text"]
            tokens.append(sid["<|retrieve|>"])
            tokens.extend(tokenizer.encode(query))
            tokens.append(sid["<|result|>"])
            tokens.extend(tokenizer.encode(chunk))
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
