"""Exa search with the request options the sweep needs.

`src/retrieval_web/exa.py` sends a fixed neural search with plain text
contents. This subclass reuses its key handling, timeout and retry and
adds the request fields the retrieval sweep varies: search type,
`includeDomains`, `category`, a character cap on returned text, and
`highlights`, which asks Exa for the sentences of each page that match a
query rather than the page from the top.

The extra fields are the only difference. Nothing here logs or returns
the api key.
"""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.getcwd())

from src.retrieval_web.exa import ExaClient


class ExaSearch(ExaClient):
    def search_ex(self, query: str, num_results: int = 10,
                  search_type: str = "neural", text: bool = True,
                  max_characters: int | None = None,
                  highlights: dict | None = None,
                  include_domains: list[str] | None = None,
                  exclude_domains: list[str] | None = None,
                  category: str | None = None) -> dict:
        payload: dict = {"query": str(query), "type": search_type,
                         "numResults": int(num_results)}
        contents: dict = {}
        if text:
            contents["text"] = ({"maxCharacters": int(max_characters)}
                                if max_characters else True)
        if highlights:
            contents["highlights"] = highlights
        if contents:
            payload["contents"] = contents
        if include_domains:
            payload["includeDomains"] = list(include_domains)
        if exclude_domains:
            payload["excludeDomains"] = list(exclude_domains)
        if category:
            payload["category"] = category
        return self._post("/search", payload)
