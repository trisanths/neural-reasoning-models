"""One-command activation test for the web retrieval tier.

With EXA_API_KEY set, runs three real queries end to end: Exa neural
search, page text chunked to the token budget with the project tokenizer,
BM25-ranked chunks printed as previews. Without the key it explains
itself and exits 0, so the script is safe to run before the key exists.

    uv run python -m scripts.web_smoke
    uv run python -m scripts.web_smoke --tokenizer runs/smoke-001/tokenizer.json

The tokenizer defaults to the newest tokenizer json found under the
usual run directories; pass --tokenizer to pin one.
"""

import argparse
import glob
import os
import sys

from src.retrieval_web.exa import API_KEY_ENV, ExaClient
from src.retrieval_web.tier import DEFAULT_CHUNK_TOKENS, WebRetrievalTier
from src.train.tokenizer import load_tokenizer

QUERIES = [
    "okapi bm25 ranking function original paper",
    "byte pair encoding tokenizer for language models",
    "retrieval augmented generation evaluation",
]

TOKENIZER_GLOBS = [
    os.path.expanduser("~/runs/tokenizer_v2/tokenizer_v2.json"),
    os.path.expanduser("~/runs/*/tokenizer.json"),
    "runs/*/tokenizer.json",
]


def find_tokenizer(explicit: str | None) -> str | None:
    if explicit:
        return explicit if os.path.exists(explicit) else None
    for pattern in TOKENIZER_GLOBS:
        matches = sorted(glob.glob(pattern))
        if matches:
            return matches[0]
    return None


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m scripts.web_smoke")
    parser.add_argument("--tokenizer", default=None,
                        help="tokenizer json path (default: search run dirs)")
    parser.add_argument("--chunk-tokens", type=int,
                        default=DEFAULT_CHUNK_TOKENS,
                        help="chunk token budget")
    parser.add_argument("--num-results", type=int, default=3,
                        help="pages to fetch per query")
    parser.add_argument("--top", type=int, default=5,
                        help="ranked chunks to preview per query")
    args = parser.parse_args()

    if not os.environ.get(API_KEY_ENV):
        print(f"{API_KEY_ENV} is not set, so the real web smoke is skipped.")
        print("Export the key and rerun; no other setup is needed.")
        return 0

    tokenizer_path = find_tokenizer(args.tokenizer)
    if tokenizer_path is None:
        print("no tokenizer json found; pass --tokenizer PATH")
        return 2
    tokenizer = load_tokenizer(tokenizer_path)
    print(f"tokenizer: {tokenizer_path}")

    client = ExaClient()
    tier = WebRetrievalTier(
        client, tokenizer,
        max_chunk_tokens=args.chunk_tokens,
        num_results=args.num_results,
    )

    total_chunks = 0
    failures = 0
    for query in QUERIES:
        print(f"\nquery: {query}")
        try:
            ranked = tier(query)
        except Exception as err:
            # Error text from the client is already sanitized.
            print(f"  failed: {err}")
            failures += 1
            continue
        if not ranked:
            print("  no chunks returned")
            failures += 1
            continue
        total_chunks += len(ranked)
        for chunk in ranked[:args.top]:
            preview = " ".join(chunk["text"].split())[:140]
            print(f"  [{chunk['rank']}] score={chunk['score']:.3f} "
                  f"{chunk['url']}")
            print(f"      {preview}")

    print()
    if failures:
        print(f"web smoke failed: {failures} of {len(QUERIES)} queries "
              "returned nothing")
        return 1
    print(f"web smoke passed: {len(QUERIES)} queries, "
          f"{total_chunks} ranked chunks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
