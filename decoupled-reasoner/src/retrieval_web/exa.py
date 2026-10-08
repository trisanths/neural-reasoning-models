"""Exa web search client for the retrieval fabric's web tier.

ExaClient talks to https://api.exa.ai over httpx. POST /search runs a
neural search and returns ranked results, optionally with page text
attached. POST /contents fetches page text for known urls. The api key
comes from the EXA_API_KEY environment variable or the api_key argument
and travels only in the x-api-key request header. No code path logs,
prints, or embeds the key: repr is sanitized and error messages carry the
endpoint, the status code, and a response snippet, never request headers.

Every request has a timeout. Timeouts, transport errors, and retryable
statuses (429 and the 5xx family) retry with exponential backoff. The
backoff schedule is deterministic and the sleep function is injectable,
so tests exercise the retry loop without waiting.

MockExa is an offline stand-in with the same duck-typed surface and
canned fixtures, so every consumer and every test runs without a key.
Tests that need to exercise the transport itself can pass an
httpx.MockTransport to ExaClient instead.
"""

import copy
import os
import time

import httpx

EXA_BASE_URL = "https://api.exa.ai"
API_KEY_ENV = "EXA_API_KEY"

DEFAULT_TIMEOUT = 15.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_BASE = 0.5
RETRY_STATUSES = frozenset({429, 500, 502, 503, 504})


class ExaError(RuntimeError):
    """Request failure with a sanitized message. status is the last HTTP
    status seen, or None when the failure never produced a response."""

    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


class ExaClient:
    """Minimal Exa API client: search and contents, with timeout and retry.

    transport and sleep exist for tests: transport is handed to the
    underlying httpx.Client (pass httpx.MockTransport to script responses)
    and sleep replaces time.sleep in the backoff loop.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = EXA_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_base: float = DEFAULT_BACKOFF_BASE,
        transport=None,
        sleep=None,
    ):
        key = api_key if api_key is not None else os.environ.get(API_KEY_ENV, "")
        if not key:
            raise ExaError(
                f"no Exa api key: set {API_KEY_ENV} or pass api_key")
        self.base_url = base_url.rstrip("/")
        self.timeout = float(timeout)
        self.max_retries = int(max_retries)
        self.backoff_base = float(backoff_base)
        self._sleep = time.sleep if sleep is None else sleep
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            transport=transport,
            headers={"x-api-key": key, "accept": "application/json"},
        )

    def __repr__(self) -> str:
        # The key never appears in repr.
        return f"ExaClient(base_url={self.base_url!r}, key=<set>)"

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "ExaClient":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def search(self, query: str, num_results: int = 10,
               text: bool = True) -> list[dict]:
        """Neural search. Returns the ranked result dicts from the API,
        each with url, title, and score, plus text when requested."""
        payload: dict = {
            "query": str(query),
            "type": "neural",
            "numResults": int(num_results),
        }
        if text:
            payload["contents"] = {"text": True}
        data = self._post("/search", payload)
        return list(data.get("results") or [])

    def contents(self, urls: list[str], text: bool = True) -> list[dict]:
        """Fetch page contents for known urls."""
        payload: dict = {"urls": [str(u) for u in urls]}
        if text:
            payload["text"] = True
        data = self._post("/contents", payload)
        return list(data.get("results") or [])

    def _post(self, path: str, payload: dict) -> dict:
        """POST with retry. Raises ExaError after the attempts run out or
        on a non-retryable status. Messages never include headers."""
        last_error: ExaError | None = None
        for attempt in range(self.max_retries + 1):
            if attempt:
                self._sleep(self.backoff_base * (2 ** (attempt - 1)))
            try:
                response = self._client.post(path, json=payload)
            except httpx.TransportError as err:
                # Timeouts subclass TransportError in httpx. The exception
                # type name is safe to report; header contents are not.
                last_error = ExaError(
                    f"POST {path} failed: {type(err).__name__}")
                continue
            status = response.status_code
            if status in RETRY_STATUSES:
                last_error = ExaError(
                    f"POST {path} failed: HTTP {status}", status=status)
                continue
            if status != 200:
                raise ExaError(
                    f"POST {path} failed: HTTP {status}: "
                    f"{response.text[:200]}", status=status)
            try:
                return response.json()
            except ValueError:
                raise ExaError(f"POST {path} returned non-json body",
                               status=status)
        assert last_error is not None
        raise last_error


# Canned fixtures for MockExa. Urls are synthetic example.org addresses and
# the texts are generic technical prose, written so chunking and BM25
# ranking have something meaningful to bite on. Scores descend within each
# query, matching the ranked order a real search returns.
MOCK_FIXTURES: dict[str, list[dict]] = {
    "okapi bm25 ranking function": [
        {
            "id": "https://example.org/ir/bm25",
            "url": "https://example.org/ir/bm25",
            "title": "Okapi BM25 scoring in practice",
            "score": 0.91,
            "text": (
                "Okapi BM25 is a ranking function used by search engines to "
                "score documents against a query. The score combines term "
                "frequency, inverse document frequency, and a length "
                "normalization controlled by two parameters.\n\n"
                "The parameter k1 saturates term frequency so a word "
                "repeated many times stops adding score. The parameter b "
                "controls how strongly long documents are penalized. Typical "
                "values are k1 between 1.2 and 2.0 and b around 0.75.\n\n"
                "BM25 remains a strong baseline for ranking. Many retrieval "
                "systems layer a learned reranker on top of a BM25 candidate "
                "list rather than replacing it."
            ),
        },
        {
            "id": "https://example.org/ir/tfidf",
            "url": "https://example.org/ir/tfidf",
            "title": "From tf-idf to probabilistic ranking",
            "score": 0.78,
            "text": (
                "The tf-idf weighting scheme scores a term by its frequency "
                "in a document discounted by how many documents contain it. "
                "It predates BM25 and shares the same intuition.\n\n"
                "Probabilistic ranking models justify these weights from a "
                "relevance model. The Okapi experiments at TREC turned that "
                "theory into the BM25 formula used today."
            ),
        },
        {
            "id": "https://example.org/ir/eval",
            "url": "https://example.org/ir/eval",
            "title": "Evaluating ranked retrieval",
            "score": 0.55,
            "text": (
                "Ranked retrieval is evaluated with graded judgments over a "
                "fixed document collection. Mean average precision and nDCG "
                "summarize how high the relevant documents sit in the "
                "ranking. A ranking function is only as good as the "
                "collection it is tuned on."
            ),
        },
    ],
    "byte level bpe tokenizer": [
        {
            "id": "https://example.org/nlp/bpe",
            "url": "https://example.org/nlp/bpe",
            "title": "Byte level BPE explained",
            "score": 0.88,
            "text": (
                "Byte pair encoding builds a vocabulary by repeatedly "
                "merging the most frequent adjacent symbol pair. Starting "
                "from raw bytes instead of characters means any string "
                "tokenizes without unknown tokens.\n\n"
                "A byte level BPE tokenizer round trips exactly: decoding "
                "the token ids of a string reproduces the string byte for "
                "byte. That property makes token windows safe to cut and "
                "rejoin."
            ),
        },
        {
            "id": "https://example.org/nlp/vocab",
            "url": "https://example.org/nlp/vocab",
            "title": "Choosing a vocabulary size",
            "score": 0.63,
            "text": (
                "Vocabulary size trades sequence length against embedding "
                "table size. Small vocabularies produce long token "
                "sequences. Large ones spend parameters on rare merges that "
                "seldom fire."
            ),
        },
    ],
    "retrieval augmented generation": [
        {
            "id": "https://example.org/nlp/rag",
            "url": "https://example.org/nlp/rag",
            "title": "Retrieval augmented generation",
            "score": 0.9,
            "text": (
                "Retrieval augmented generation lets a language model "
                "consult an external corpus at inference time. The model "
                "writes a query, a retriever returns supporting text, and "
                "generation continues conditioned on what came back.\n\n"
                "Serving retrieval during decoding separates what the model "
                "must know from what it can look up. A small model with a "
                "good retriever can answer questions its weights never "
                "stored."
            ),
        },
        {
            "id": "https://example.org/nlp/hops",
            "url": "https://example.org/nlp/hops",
            "title": "Multi-hop question answering",
            "score": 0.71,
            "text": (
                "Multi-hop questions need evidence from several documents "
                "chained together. Each retrieval round should be phrased "
                "from what is already known, not from the answer. Training "
                "traces that respect that constraint teach a model to drive "
                "the loop itself."
            ),
        },
    ],
}


class MockExa:
    """Offline stand-in for ExaClient with the same duck-typed surface.

    Serves deep copies of canned fixtures keyed by exact query string and
    records every call in self.calls for test assertions. Unknown queries
    return no results. Needs no key and touches no network.
    """

    def __init__(self, fixtures: dict[str, list[dict]] | None = None):
        self.fixtures = MOCK_FIXTURES if fixtures is None else fixtures
        self.calls: list[dict] = []

    def search(self, query: str, num_results: int = 10,
               text: bool = True) -> list[dict]:
        self.calls.append({"endpoint": "search", "query": query,
                           "num_results": num_results, "text": text})
        results = copy.deepcopy(self.fixtures.get(query, []))[:num_results]
        if not text:
            for result in results:
                result.pop("text", None)
        return results

    def contents(self, urls: list[str], text: bool = True) -> list[dict]:
        self.calls.append({"endpoint": "contents", "urls": list(urls),
                           "text": text})
        by_url = {}
        for results in self.fixtures.values():
            for result in results:
                by_url.setdefault(result.get("url"), result)
        found = [copy.deepcopy(by_url[u]) for u in urls if u in by_url]
        if not text:
            for result in found:
                result.pop("text", None)
        return found
