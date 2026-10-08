"""Pick which files of one S3-mirrored run directory to download for resume.

Reads `aws s3 ls s3://.../runs/curve/<lane>/` lines on stdin and prints one
plan line per file to fetch:

  GET <name> <bytes>          fetch this object
  LATEST_FROM <name>          latest.pt is missing or bad; after download,
                              copy this numbered checkpoint over latest.pt
  FAIL <reason>               nothing safe to resume from

Selection rules, unchanged from the block-2 handoff except that the
known-bad list is empty: every block-2 and block-3 checkpoint was written
by the atomic-save trainer, so no object is known truncated going into
block 4.
The size-consistency guard stays, because a sync can still race a write:
  - Checkpoints of one lane are all the same model and optimizer, so their
    byte sizes agree to within a few KB. Any numbered checkpoint smaller
    than 99 percent of the largest sibling is treated as truncated and
    skipped. latest.pt gets the same test (stray latest.pt.tmp objects are
    ignored: they match neither the ckpt pattern nor the latest.pt name).
  - Of the surviving numbered checkpoints only the newest is fetched;
    latest.pt is what --resume actually loads, the numbered one is the
    fallback copied over it when latest.pt fails the size test.
  - config.yaml, cmd.txt, loss.jsonl always fetch.

Pure stdlib. Exercised against the real runs/curve/ prefix before the
block-3 and block-4 handoffs; exit code 0 only when a resumable plan
exists.

Usage: aws s3 ls <prefix>/<lane>/ | python3 select_ckpt.py <lane>
"""

from __future__ import annotations

import re
import sys

KNOWN_BAD: set[str] = set()
SIZE_TOLERANCE = 0.99
SMALL_FILES = ("config.yaml", "cmd.txt", "loss.jsonl")
CKPT_RE = re.compile(r"^ckpt-(\d+)\.pt$")


def main() -> int:
    lane = sys.argv[1]
    listing: dict[str, int] = {}
    for line in sys.stdin:
        parts = line.split()
        # date time size name; skip PRE lines and blanks
        if len(parts) != 4 or not parts[2].isdigit():
            continue
        listing[parts[3]] = int(parts[2])

    for name in SMALL_FILES:
        if name not in listing:
            print(f"FAIL {lane} missing {name}")
            return 1
        print(f"GET {name} {listing[name]}")

    numbered = {}
    for name, size in listing.items():
        match = CKPT_RE.match(name)
        if not match:
            continue
        if f"{lane}/{name}" in KNOWN_BAD:
            print(f"# skip {name}: known truncated object", file=sys.stderr)
            continue
        numbered[name] = (int(match.group(1)), size)
    if not numbered:
        print(f"FAIL {lane} has no numbered checkpoints outside the bad list")
        return 1

    reference = max(size for _, size in numbered.values())
    good = {}
    for name, (step, size) in numbered.items():
        if size < reference * SIZE_TOLERANCE:
            print(f"# skip {name}: {size} bytes, sibling pattern {reference}",
                  file=sys.stderr)
            continue
        good[name] = (step, size)
    if not good:
        print(f"FAIL {lane} has no size-consistent numbered checkpoint")
        return 1

    newest = max(good, key=lambda n: good[n][0])
    print(f"GET {newest} {good[newest][1]}")

    latest_size = listing.get("latest.pt")
    if latest_size is not None and latest_size >= reference * SIZE_TOLERANCE:
        print(f"GET latest.pt {latest_size}")
    else:
        why = "missing" if latest_size is None else f"{latest_size} bytes"
        print(f"# latest.pt {why}, will copy {newest} over it", file=sys.stderr)
        print(f"LATEST_FROM {newest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
