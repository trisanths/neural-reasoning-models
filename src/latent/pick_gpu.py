"""Pick GPUs that are actually free, and refuse rather than crowd a card.

Several experiments share this box and an out of memory kill takes someone
else's multi hour run with it, so a lane waits for a card instead of squeezing
onto a busy one. Selection is on free memory first and utilisation second, and
a card is only offered if it has at least --need GiB free right now.

Prints one comma separated list of indices, or exits non zero having printed
nothing when the box has no room.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time


def snapshot():
    out = subprocess.run(
        ["nvidia-smi",
         "--query-gpu=index,utilization.gpu,memory.used,memory.total",
         "--format=csv,noheader,nounits"],
        capture_output=True, text=True, check=True).stdout
    rows = []
    for line in out.strip().splitlines():
        i, util, used, total = (x.strip() for x in line.split(","))
        rows.append({"index": int(i), "util": float(util),
                     "free_gib": (float(total) - float(used)) / 1024.0,
                     "used_gib": float(used) / 1024.0})
    return rows


def choose(rows, need, count, max_util):
    ok = [r for r in rows if r["free_gib"] >= need and r["util"] <= max_util]
    ok.sort(key=lambda r: (-r["free_gib"], r["util"]))
    return ok[:count]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--need", type=float, default=30.0, help="free GiB")
    ap.add_argument("--count", type=int, default=1)
    ap.add_argument("--max-util", type=float, default=101.0)
    ap.add_argument("--wait", type=int, default=0, help="seconds to keep trying")
    ap.add_argument("--poll", type=int, default=60)
    args = ap.parse_args(argv)

    deadline = time.time() + args.wait
    while True:
        rows = snapshot()
        picked = choose(rows, args.need, args.count, args.max_util)
        if len(picked) == args.count:
            print(",".join(str(r["index"]) for r in picked))
            return 0
        if time.time() >= deadline:
            print(f"[pick_gpu] no {args.count} card(s) with {args.need} GiB "
                  f"free: " + "; ".join(
                      f"{r['index']}:{r['free_gib']:.0f}GiB/{r['util']:.0f}%"
                      for r in rows), file=sys.stderr)
            return 1
        time.sleep(args.poll)


if __name__ == "__main__":
    raise SystemExit(main())
