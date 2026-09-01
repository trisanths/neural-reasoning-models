"""Compare sweep conditions on the same items, paired.

Prints for each condition and a chosen context: the answer present rate,
the share of those that are pages carrying the exam item itself, and the
share that carry every distractor as well. A configuration that lifts the
answer present rate by finding the quiz page the question came from has
not improved retrieval, it has found the test set, so `clean` is the rate
that excludes both.

With --paired it also prints the discordant pairs against a baseline
condition, which is what a difference on the same 50 items rests on.
"""
from __future__ import annotations

import argparse
import glob
import json
import os


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return [round((c - h) / d, 3), round((c + h) / d, 3)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="results/extern/retsweep")
    ap.add_argument("--ctx", default="passages@20")
    ap.add_argument("--baseline", default="")
    ap.add_argument("--names", default="")
    a = ap.parse_args()
    want = [x for x in a.names.split(",") if x]
    rows = {}
    for f in sorted(glob.glob(os.path.join(a.dir, "*.json"))):
        d = json.load(open(f))
        name = d["summary"]["name"]
        if want and name not in want:
            continue
        rows[name] = d
    print(f"context = {a.ctx}")
    print(f"{'condition':22} {'n':>3} {'searches':>8} {'hit':>6} {'ci':>14} "
          f"{'stem':>5} {'answr':>6} {'clean':>6} {'soft':>6} {'r@1':>5} "
          f"{'r@20':>5}")
    for name, d in rows.items():
        recs = d["records"]
        n = len(recs)
        if not recs or a.ctx not in recs[0]["ctx"]:
            continue
        hit = sum(1 for r in recs if r["ctx"][a.ctx]["token"])
        stem = sum(1 for r in recs if r["ctx"][a.ctx]["stem"])
        alld = sum(1 for r in recs if r["ctx"][a.ctx]["token"]
                   and r["ctx"][a.ctx]["n_distractors"] >= 3)
        answr = sum(1 for r in recs if r["ctx"][a.ctx]["token"]
                    and not r["ctx"][a.ctx]["stem"])
        clean = sum(1 for r in recs if r["ctx"][a.ctx]["token"]
                    and not r["ctx"][a.ctx]["stem"]
                    and r["ctx"][a.ctx]["n_distractors"] < 3)
        soft = sum(1 for r in recs if r["ctx"][a.ctx]["soft"])
        rec = d["summary"]["recall_full_text"]
        r1 = rec.get("token@1", {}).get("rate")
        r20 = rec.get("token@20", rec.get("token@10", {})).get("rate")
        ci = wilson(hit, n)
        print(f"{name:22} {n:3d} {d['summary']['live_searches']:8d} "
              f"{hit/n:6.3f} [{ci[0]:.3f},{ci[1]:.3f}] {stem/n:5.2f} "
              f"{answr/n:6.3f} {clean/n:6.3f} {soft/n:6.3f} "
              f"{str(r1):>5} {str(r20):>5}")
    if a.baseline and a.baseline in rows:
        base = {r["id"]: r for r in rows[a.baseline]["records"]}
        print(f"\npaired against {a.baseline} on {a.ctx}: "
              f"b=only baseline hits, c=only condition hits")
        for name, d in rows.items():
            if name == a.baseline:
                continue
            b = c = 0
            for r in d["records"]:
                o = base.get(r["id"])
                if o is None or a.ctx not in o["ctx"]:
                    continue
                x, y = o["ctx"][a.ctx]["token"], r["ctx"][a.ctx]["token"]
                b += x and not y
                c += y and not x
            print(f"  {name:22} b={b:3d} c={c:3d}  net={c-b:+d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
