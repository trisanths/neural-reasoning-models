"""Drive scripts/dependency_sweep.py over every checkpoint the project owns.

The checkpoints live in S3 and total a couple of hundred gigabytes, so this
pulls one at a time, measures it, ships the artefacts back, and deletes the
weights before pulling the next. It is resumable: a run whose dependency.json
is already in the destination prefix is skipped unless --force.

The manifest says which evaluation suite each checkpoint is graded on. That
is not a detail. A policy trained by GRPO on invented arithmetic scored on
held-out worlds, or a pretraining checkpoint scored on rule cards it never
met, answers the transfer question rather than this one.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

BUCKET = "s3://decoupled-reasoner-009398924577"
DEST = f"{BUCKET}/runs/dependency-sweep"


def sh(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=False, text=True, **kw)


def s3_has(key_url: str) -> bool:
    r = sh(["aws", "s3", "ls", key_url], capture_output=True)
    return r.returncode == 0 and bool(r.stdout.strip())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--work", default=os.path.expanduser("~/depsweep"))
    ap.add_argument("--config", default="configs/dependency-sweep.yaml")
    ap.add_argument("--tokenizer", default=os.path.expanduser("~/data/tokenizer_v2.json"))
    ap.add_argument("--heldout",
                    default=os.path.expanduser("~/data/regime_c/heldout.jsonl"))
    ap.add_argument("--count", type=int, default=250)
    ap.add_argument("--mc-count", type=int, default=None)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--temperature", type=float, default=0.8)
    ap.add_argument("--dest", default=DEST)
    ap.add_argument("--only", default=None, help="comma separated run ids")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--keep-weights", action="store_true")
    args = ap.parse_args()

    with open(args.manifest) as fh:
        manifest = json.load(fh)
    if args.only:
        want = {s.strip() for s in args.only.split(",") if s.strip()}
        manifest = [m for m in manifest if m["run_id"] in want]

    work = Path(args.work)
    work.mkdir(parents=True, exist_ok=True)

    done, failed = [], []
    for i, entry in enumerate(manifest, start=1):
        run_id = entry["run_id"]
        out_dir = work / run_id
        marker = f"{args.dest}/{run_id}/dependency.json"
        if not args.force and s3_has(marker):
            print(f"[{i}/{len(manifest)}] {run_id}: already measured, skipping",
                  flush=True)
            done.append(run_id)
            continue

        src = f"{BUCKET}/{entry['key']}"
        local = work / f"{run_id}.pt"
        t0 = time.monotonic()
        print(f"[{i}/{len(manifest)}] {run_id}: pulling {src}", flush=True)
        r = sh(["aws", "s3", "cp", src, str(local), "--only-show-errors"])
        if r.returncode != 0 or not local.exists():
            print(f"[{i}] {run_id}: download failed", flush=True)
            failed.append((run_id, "download"))
            continue
        pull_s = round(time.monotonic() - t0, 1)

        out_dir.mkdir(parents=True, exist_ok=True)
        cmd = [
            sys.executable, "-m", "scripts.dependency_sweep",
            "--checkpoint", str(local),
            "--run-id", run_id,
            "--suite", entry["suite"],
            "--config", args.config,
            "--tokenizer", args.tokenizer,
            "--out", str(out_dir),
            "--count", str(args.count),
            "--batch", str(args.batch),
            "--temperature", str(args.temperature),
        ]
        if entry["suite"] == "worldgen":
            cmd += ["--heldout", args.heldout]
        cmd += ["--protocols", entry.get("protocols", "gen")]
        if entry.get("primary"):
            cmd += ["--primary", entry["primary"]]
        if entry.get("mc_count") or args.mc_count:
            cmd += ["--mc-count", str(entry.get("mc_count") or args.mc_count)]
        if entry.get("mc_retrieval"):
            cmd += ["--mc-retrieval"]
        r = sh(cmd)
        if not args.keep_weights:
            local.unlink(missing_ok=True)
        if r.returncode != 0:
            print(f"[{i}] {run_id}: sweep failed rc={r.returncode}", flush=True)
            failed.append((run_id, f"rc{r.returncode}"))
            continue

        sh(["aws", "s3", "sync", str(out_dir), f"{args.dest}/{run_id}",
            "--exclude", "cond_*.jsonl", "--only-show-errors"])
        print(f"[{i}/{len(manifest)}] {run_id}: done in "
              f"{round(time.monotonic() - t0, 1)}s (pull {pull_s}s)", flush=True)
        done.append(run_id)

    print(f"SWEEP COMPLETE done={len(done)} failed={len(failed)} {failed}",
          flush=True)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
