"""Web retrieval tier: pages from Exa, served as ranked token-budget chunks.

WebRetrievalTier is duck-typed like the BM25 oracle in
src/train/retrieval.py: a query-to-ranked-chunks callable. Calling it with
a query string returns ranked chunk dicts. Pages arrive from the Exa
client in relevance order, their text is chunked to a token budget with
the project tokenizer, and the pooled chunks are then ranked with the
same Okapi BM25 the training oracle scores with (uniform reliability,
ties toward the earliest chunk). One scoring rule therefore governs both
the episode oracle and the web tier.

WebTierIndex is the thin adapter for src/evals/interactive.py. It
presents the serving surface the decode loop uses on BM25Index, top(query,
exclude) plus a doc_texts list, while the documents underneath come from
the web, so a generate_with_retrieval style loop can serve web results in
place of episode documents. doc_texts grows as queries arrive; indices
are stable across calls, so the loop's without-replacement exclude set
works unchanged.

Chunking is deterministic. Sentences are packed greedily up to the token
budget; a single unit longer than the budget is hard-split on token
windows, which is safe because the project tokenizer is byte level and
round trips exactly.
"""

import re

from src.train.retrieval import BM25Index

DEFAULT_CHUNK_TOKENS = 128
DEFAULT_NUM_RESULTS = 5
DEFAULT_MAX_CHUNKS_PER_PAGE = 8

_PARAGRAPH_RE = re.compile(r"\n\s*\n")
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


def _split_units(text: str) -> list[str]:
    """Whitespace-normalized sentences, in document order."""
    units: list[str] = []
    for paragraph in _PARAGRAPH_RE.split(text):
        paragraph = " ".join(paragraph.split())
        if not paragraph:
            continue
        units.extend(s for s in _SENTENCE_RE.split(paragraph) if s)
    return units


def _hard_split(unit: str, tokenizer, max_tokens: int) -> list[str]:
    """Split one over-budget unit on token windows.

    Each window is decoded and re-encoded to verify it fits the budget,
    shrinking when a cut lands where re-encoding merges differently. The
    concatenation of the pieces reproduces the unit exactly because the
    byte level tokenizer round trips.
    """
    ids = tokenizer.encode(unit)
    pieces: list[str] = []
    start = 0
    while start < len(ids):
        width = min(max_tokens, len(ids) - start)
        piece = tokenizer.decode(ids[start:start + width])
        while width > 1 and len(tokenizer.encode(piece)) > max_tokens:
            width -= 1
            piece = tokenizer.decode(ids[start:start + width])
        pieces.append(piece)
        start += width
    return pieces


def chunk_text(text: str, tokenizer, max_tokens: int) -> list[str]:
    """Chunk text so every chunk encodes to at most max_tokens tokens.

    Greedy sentence packing preserves the word sequence; only a single
    sentence longer than the whole budget is cut mid-word by the token
    window fallback. Deterministic for fixed inputs.
    """
    if max_tokens < 1:
        raise ValueError("max_tokens must be at least 1")
    chunks: list[str] = []
    current = ""
    for unit in _split_units(str(text or "")):
        if len(tokenizer.encode(unit)) > max_tokens:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(_hard_split(unit, tokenizer, max_tokens))
            continue
        candidate = f"{current} {unit}" if current else unit
        if len(tokenizer.encode(candidate)) <= max_tokens:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = unit
    if current:
        chunks.append(current)
    return chunks


class WebRetrievalTier:
    """Query-to-ranked-chunks callable over an Exa-shaped client.

    client is anything with the ExaClient search surface, MockExa
    included. tokenizer is the project TrainTokenizer used to enforce the
    chunk token budget.
    """

    def __init__(
        self,
        client,
        tokenizer,
        max_chunk_tokens: int = DEFAULT_CHUNK_TOKENS,
        num_results: int = DEFAULT_NUM_RESULTS,
        max_chunks_per_page: int = DEFAULT_MAX_CHUNKS_PER_PAGE,
    ):
        if max_chunk_tokens < 1:
            raise ValueError("max_chunk_tokens must be at least 1")
        self.client = client
        self.tokenizer = tokenizer
        self.max_chunk_tokens = int(max_chunk_tokens)
        self.num_results = int(num_results)
        self.max_chunks_per_page = int(max_chunks_per_page)

    def __call__(self, query: str) -> list[dict]:
        """Ranked chunks for a query.

        Returns dicts with text, url, title, page_rank, chunk_index,
        score, and rank, ordered best first. Score is the oracle BM25 of
        the query against the pooled chunks; ties keep page order then
        chunk order, so the ranking is deterministic.
        """
        results = self.client.search(
            query, num_results=self.num_results, text=True)
        pool: list[dict] = []
        for page_rank, result in enumerate(results):
            page_text = result.get("text") or ""
            if not page_text.strip():
                continue
            page_chunks = chunk_text(
                page_text, self.tokenizer, self.max_chunk_tokens)
            for chunk_index, chunk in enumerate(
                    page_chunks[:self.max_chunks_per_page]):
                pool.append({
                    "text": chunk,
                    "url": result.get("url", ""),
                    "title": result.get("title", ""),
                    "page_rank": page_rank,
                    "chunk_index": chunk_index,
                })
        if not pool:
            return []
        index = BM25Index([c["text"] for c in pool])
        scores = [index.score(query, i) for i in range(len(pool))]
        order = sorted(range(len(pool)), key=lambda i: (-scores[i], i))
        ranked = []
        for rank, i in enumerate(order):
            chunk = dict(pool[i])
            chunk["score"] = scores[i]
            chunk["rank"] = rank
            ranked.append(chunk)
        return ranked


class WebTierIndex:
    """BM25Index-shaped serving adapter over a WebRetrievalTier.

    Mirrors the two things src/evals/interactive.py touches on the oracle
    index: top(query, exclude) returning a document index, and a
    doc_texts list the returned index points into. Chunks register in
    doc_texts the first time they are seen, deduplicated by text, so an
    index handed out once stays valid and the caller's exclude set gives
    without-replacement serving across rounds.
    """

    def __init__(self, tier: WebRetrievalTier):
        self.tier = tier
        self.doc_texts: list[str] = []
        self.doc_meta: list[dict] = []
        self._index_of: dict[str, int] = {}

    def _register(self, chunk: dict) -> int:
        text = chunk["text"]
        existing = self._index_of.get(text)
        if existing is not None:
            return existing
        index = len(self.doc_texts)
        self._index_of[text] = index
        self.doc_texts.append(text)
        self.doc_meta.append(
            {k: chunk.get(k, "") for k in ("url", "title")})
        return index

    def top(self, query: str, exclude=()) -> int:
        """Index of the best ranked chunk outside exclude.

        Matches BM25Index.top semantics: deterministic for a fixed
        client, and raises ValueError when nothing can be served, which
        is also what an empty result set maps to.
        """
        ranked = self.tier(query)
        for chunk in ranked:
            self._register(chunk)
        if not ranked:
            raise ValueError("every document is excluded")
        excluded = set(exclude)
        for chunk in ranked:
            index = self._index_of[chunk["text"]]
            if index not in excluded:
                return index
        raise ValueError("every document is excluded")
