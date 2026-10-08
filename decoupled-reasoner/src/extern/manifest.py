"""A replayable record of what live search returned.

The pages themselves stay on disk under results/extern/exa_cache, keyed by a
hash of the query, because committing the page text would put megabytes of
third party prose in the repository. What is committed is this manifest: for
every query, its hash, the urls that came back in rank order and how much text
each carried. That is enough to say what a run saw, to detect that a cache
entry has changed, and to re-fetch the same urls if the cache is lost.
"""
from __future__ import annotations

import glob
import hashlib
import json
import os

CACHE = "results/extern/exa_cache"
OUT = "results/extern/exa_manifest.json"

rows = []
for p in sorted(glob.glob(f"{CACHE}/*.json")):
    try:
        pages = json.load(open(p))
    except Exception:
        continue
    body = open(p, "rb").read()
    rows.append({
        "cache_file": os.path.basename(p),
        "sha256": hashlib.sha256(body).hexdigest(),
        "n_pages": len(pages),
        "urls": [x.get("url", "") for x in pages],
        "titles": [(x.get("title") or "")[:80] for x in pages],
        "text_chars": [len(x.get("text") or "") for x in pages],
    })

man = {"cache_dir": CACHE, "n_queries": len(rows),
       "n_pages_total": sum(r["n_pages"] for r in rows),
       "chars_total": sum(sum(r["text_chars"]) for r in rows),
       "empty_queries": sum(1 for r in rows if r["n_pages"] == 0),
       "entries": rows}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(man, open(OUT, "w"), indent=1)
print(json.dumps({k: v for k, v in man.items() if k != "entries"}, indent=1))
