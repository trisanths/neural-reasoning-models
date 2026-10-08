"""ExaClient request shape, retry behavior, key hygiene, and MockExa.

Real network is never touched: transport tests use httpx.MockTransport
and everything else runs against MockExa. No test needs a real key.
"""

import json

import httpx
import pytest

from src.retrieval_web.exa import (
    API_KEY_ENV,
    MOCK_FIXTURES,
    ExaClient,
    ExaError,
    MockExa,
)

KEY = "test-key-abc123"


def make_client(handler, **kwargs):
    kwargs.setdefault("sleep", lambda s: None)
    return ExaClient(api_key=KEY, transport=httpx.MockTransport(handler),
                     **kwargs)


def ok_response(payload):
    return httpx.Response(200, json=payload)


def test_missing_key_raises(monkeypatch):
    monkeypatch.delenv(API_KEY_ENV, raising=False)
    with pytest.raises(ExaError) as excinfo:
        ExaClient()
    assert API_KEY_ENV in str(excinfo.value)


def test_key_from_env(monkeypatch):
    monkeypatch.setenv(API_KEY_ENV, KEY)
    seen = {}

    def handler(request):
        seen["key"] = request.headers.get("x-api-key")
        return ok_response({"results": []})

    client = ExaClient(transport=httpx.MockTransport(handler))
    client.search("anything")
    assert seen["key"] == KEY


def test_search_request_shape():
    seen = {}

    def handler(request):
        seen["url"] = str(request.url)
        seen["key"] = request.headers.get("x-api-key")
        seen["body"] = json.loads(request.content)
        return ok_response({"results": MOCK_FIXTURES[
            "okapi bm25 ranking function"]})

    client = make_client(handler)
    results = client.search("okapi bm25 ranking function", num_results=3)
    assert seen["url"] == "https://api.exa.ai/search"
    assert seen["key"] == KEY
    assert seen["body"]["query"] == "okapi bm25 ranking function"
    assert seen["body"]["type"] == "neural"
    assert seen["body"]["numResults"] == 3
    assert seen["body"]["contents"] == {"text": True}
    assert len(results) == 3
    assert results[0]["url"] == "https://example.org/ir/bm25"


def test_search_without_text_omits_contents():
    seen = {}

    def handler(request):
        seen["body"] = json.loads(request.content)
        return ok_response({"results": []})

    client = make_client(handler)
    client.search("q", text=False)
    assert "contents" not in seen["body"]


def test_contents_request_shape():
    seen = {}

    def handler(request):
        seen["url"] = str(request.url)
        seen["body"] = json.loads(request.content)
        return ok_response({"results": [{"url": "https://example.org/a",
                                         "text": "body"}]})

    client = make_client(handler)
    results = client.contents(["https://example.org/a"])
    assert seen["url"] == "https://api.exa.ai/contents"
    assert seen["body"] == {"urls": ["https://example.org/a"], "text": True}
    assert results[0]["text"] == "body"


def test_retry_then_success():
    attempts = []
    sleeps = []

    def handler(request):
        attempts.append(1)
        if len(attempts) < 3:
            return httpx.Response(503, text="unavailable")
        return ok_response({"results": [{"url": "u"}]})

    client = ExaClient(api_key=KEY, transport=httpx.MockTransport(handler),
                       max_retries=3, backoff_base=0.5,
                       sleep=sleeps.append)
    results = client.search("q")
    assert len(attempts) == 3
    assert sleeps == [0.5, 1.0]
    assert results == [{"url": "u"}]


def test_retry_gives_up_after_max_retries():
    attempts = []

    def handler(request):
        attempts.append(1)
        return httpx.Response(503, text="unavailable")

    client = make_client(handler, max_retries=2)
    with pytest.raises(ExaError) as excinfo:
        client.search("q")
    assert len(attempts) == 3
    assert excinfo.value.status == 503
    assert "503" in str(excinfo.value)


def test_timeout_retries_then_succeeds():
    attempts = []

    def handler(request):
        attempts.append(1)
        if len(attempts) == 1:
            raise httpx.ConnectTimeout("boom", request=request)
        return ok_response({"results": []})

    client = make_client(handler, max_retries=1)
    assert client.search("q") == []
    assert len(attempts) == 2


def test_timeout_exhaustion_raises_sanitized_error():
    def handler(request):
        raise httpx.ReadTimeout("boom", request=request)

    client = make_client(handler, max_retries=1)
    with pytest.raises(ExaError) as excinfo:
        client.search("q")
    assert "ReadTimeout" in str(excinfo.value)
    assert KEY not in str(excinfo.value)


def test_non_retryable_status_fails_fast():
    attempts = []

    def handler(request):
        attempts.append(1)
        return httpx.Response(400, text="bad request body")

    client = make_client(handler, max_retries=3)
    with pytest.raises(ExaError) as excinfo:
        client.search("q")
    assert len(attempts) == 1
    assert excinfo.value.status == 400
    assert "400" in str(excinfo.value)


def test_key_never_in_repr_or_errors():
    def handler(request):
        return httpx.Response(503, text="unavailable")

    client = make_client(handler, max_retries=1)
    assert KEY not in repr(client)
    with pytest.raises(ExaError) as excinfo:
        client.search("q")
    assert KEY not in str(excinfo.value)
    assert KEY not in repr(excinfo.value)


def test_non_json_body_raises():
    client = make_client(lambda request: httpx.Response(200, text="<html>"))
    with pytest.raises(ExaError) as excinfo:
        client.search("q")
    assert "non-json" in str(excinfo.value)


def test_mock_exa_serves_fixtures():
    mock = MockExa()
    results = mock.search("okapi bm25 ranking function", num_results=2)
    assert len(results) == 2
    assert results[0]["url"] == "https://example.org/ir/bm25"
    assert results[0]["text"]
    assert [r["score"] for r in results] == sorted(
        (r["score"] for r in results), reverse=True)
    assert mock.calls[0]["endpoint"] == "search"
    assert mock.calls[0]["num_results"] == 2


def test_mock_exa_unknown_query_is_empty():
    assert MockExa().search("no such canned query") == []


def test_mock_exa_returns_copies():
    mock = MockExa()
    first = mock.search("byte level bpe tokenizer")
    first[0]["text"] = "mutated"
    second = mock.search("byte level bpe tokenizer")
    assert second[0]["text"] != "mutated"


def test_mock_exa_text_flag():
    results = MockExa().search("byte level bpe tokenizer", text=False)
    assert results and all("text" not in r for r in results)


def test_mock_exa_contents():
    mock = MockExa()
    results = mock.contents(["https://example.org/nlp/rag",
                             "https://example.org/absent"])
    assert len(results) == 1
    assert results[0]["url"] == "https://example.org/nlp/rag"
    assert results[0]["text"]


def test_mock_exa_matches_client_surface():
    """MockExa accepts the same calls the tier makes on ExaClient."""
    mock = MockExa()
    results = mock.search("retrieval augmented generation",
                          num_results=5, text=True)
    assert isinstance(results, list)
    assert all(isinstance(r, dict) for r in results)
    assert all({"url", "title", "score", "text"} <= r.keys()
               for r in results)
