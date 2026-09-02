"""Audit the Exa page caches before anything is scored against them.

A mock run once wrote empty result lists into the live cache under real query
keys, which silently weakened a falsifying control. Every cache entry is
therefore checked for shape and for non-empty page text, and the counts are
printed so a later run can be compared against them.
"""
import json
import os
import sys

def audit(d):
    tot = empty = broken = 0
    pages = 0
    chars = 0
    zero_text = 0
    bad = []
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".json"):
            continue
        tot += 1
        p = os.path.join(d, fn)
        try:
            v = json.load(open(p))
        except Exception as e:
            broken += 1
            bad.append((fn, f"unreadable {type(e).__name__}"))
            continue
        if isinstance(v, dict) and "results" in v:
            v = v["results"]
        if not isinstance(v, list):
            broken += 1
            bad.append((fn, "not a list"))
            continue
        if len(v) == 0:
            empty += 1
            bad.append((fn, "empty result list"))
            continue
        pages += len(v)
        n_text = 0
        for r in v:
            t = (r.get("text") or "") if isinstance(r, dict) else ""
            chars += len(t)
            if t.strip():
                n_text += 1
        if n_text == 0:
            zero_text += 1
            bad.append((fn, f"{len(v)} pages, none with text"))
    return {"dir": d, "entries": tot, "empty_lists": empty,
            "broken": broken, "entries_with_no_page_text": zero_text,
            "total_pages": pages,
            "mean_pages_per_entry": round(pages / tot, 2) if tot else 0,
            "total_text_chars": chars,
            "mean_text_chars_per_entry": round(chars / tot, 1) if tot else 0,
            "suspect": bad[:20], "n_suspect": len(bad)}

out = [audit(d) for d in sys.argv[1:] if os.path.isdir(d)]
print(json.dumps(out, indent=1))
