"""Web tier of the retrieval fabric.

ExaClient talks to the Exa search API, MockExa is its offline stand-in,
and tier.py turns either of them into the query-to-ranked-chunks callable
the rest of the project retrieves through. See src/train/retrieval.py for
the episode-local oracle this tier mirrors.
"""

from src.retrieval_web.exa import (
    API_KEY_ENV,
    EXA_BASE_URL,
    ExaClient,
    ExaError,
    MockExa,
)
from src.retrieval_web.tier import (
    DEFAULT_CHUNK_TOKENS,
    WebRetrievalTier,
    WebTierIndex,
    chunk_text,
)

__all__ = [
    "API_KEY_ENV",
    "EXA_BASE_URL",
    "ExaClient",
    "ExaError",
    "MockExa",
    "DEFAULT_CHUNK_TOKENS",
    "WebRetrievalTier",
    "WebTierIndex",
    "chunk_text",
]
