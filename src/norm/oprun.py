"""The systems that answer the acquisition items, other than the network.

    L   read the page, put the operation in an episode scoped library, run the
        plan. No gradient step is taken anywhere in this path.
    P   `src/norm/parse.py`, the project's hand written parser for the fourteen
        corpus shapes. It is the trivial program baseline that already beats
        the network everywhere it can read, and it is run here to say exactly
        what it does with a page that defines an operation.
    S1  the shortcut reader: take the first line in the text that states the
        question's key and answer with the other word on it.
    S2  the same reader taking the last such line instead.

S1 and S2 are the baselines that matter for this family. Two directories that
state the same key are what an agreement page is, so a reader that grabs a
matching line is right whenever the directories agree and right by luck when
they do not. Their scores are the real floor for this item set, above the
option set floor, and both are reported.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import re
import time

from src.norm import opread, parse
from src.norm.render import frame_by_id


def shortcut(text: str, key: str, fid: str, which: str) -> str:
    """The word a keyword reader takes off a line that states the key."""
    fr = frame_by_id(fid)
    try:
        rx = re.compile(fr.lookup_regex(key))
    except re.error:
        return ""
    hits = [m.group(1) for line in text.split("\n") for m in [rx.search(line)]
            if m is not None]
    if not hits:
        return ""
    return hits[0] if which == "first" else hits[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", default="results/norm/oneshot/items.jsonl.gz")
    ap.add_argument("--out", default="results/norm/oneshot/sys.jsonl.gz")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    items = [json.loads(l) for l in gzip.open(a.items, "rt")]
    if a.limit:
        items = items[:a.limit]
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    t0 = time.time()
    counts = {"L": {}, "P": {}}
    with gzip.open(a.out, "wt") as fh:
        for it in items:
            key = it["prog"]["inputs"][0][1]
            rec = {"id": it["id"], "cond": it["cond"],
                   "family": it["family"], "split": it["split"],
                   "fid": it["fid"], "gold": it["gold"],
                   "options": it["options"], "n_pages": it["n_pages"],
                   "n": it["n"], "item_key": it["item_key"]}
            got = opread.answer(it["text"], it["fid"])
            rec["L"] = {"answer": got["answer"], "state": got["state"],
                        "stage": got.get("stage", ""),
                        "reason": got.get("reason", "")[:160]}
            counts["L"][got["state"]] = counts["L"].get(got["state"], 0) + 1
            p = parse.parse(it["text"], it["fid"])
            if p.ok:
                from src.norm.interp import run as irun
                r = irun(p.program)
                rec["P"] = {"answer": r.text if r.ok else "",
                            "state": "ran" if r.ok else "refused",
                            "reason": "" if r.ok else r.reason[:160]}
            else:
                rec["P"] = {"answer": "", "state": "misread",
                            "reason": p.reason[:160]}
            counts["P"][rec["P"]["state"]] = \
                counts["P"].get(rec["P"]["state"], 0) + 1
            rec["S1"] = {"answer": shortcut(it["text"], key, it["fid"],
                                            "first"), "state": "ran"}
            rec["S2"] = {"answer": shortcut(it["text"], key, it["fid"],
                                            "last"), "state": "ran"}
            fh.write(json.dumps(rec) + "\n")
    meta = {"items": os.path.abspath(a.items), "out": os.path.abspath(a.out),
            "n": len(items), "states": counts,
            "seconds": round(time.time() - t0, 1)}
    with open(a.out.replace(".jsonl.gz", ".meta.json"), "w") as fh:
        json.dump(meta, fh, indent=2)
    print(json.dumps(meta))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
