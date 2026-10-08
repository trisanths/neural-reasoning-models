"""Push training checkpoints to S3 so a wiped instance store costs nothing.

Every cycle: upload loss.jsonl, then for each new ckpt-*.pt write a weights
only copy (1.5 GB rather than 4.5 GB) and upload it under weights/, upload the
full optimizer carrying file under resume/ at a coarser stride, and prune old
local checkpoints so /mnt/nvme does not fill.
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import torch

RUN = Path(sys.argv[1])
PREFIX = sys.argv[2].rstrip("/")
WEIGHTS_EVERY = int(sys.argv[3]) if len(sys.argv) > 3 else 1000
RESUME_EVERY = int(sys.argv[4]) if len(sys.argv) > 4 else 4000
KEEP_LOCAL = 2

state_path = RUN / "s3_watch_state.json"
done = set()
if state_path.exists():
    done = set(json.load(open(state_path))["done"])


def s3cp(src, dst):
    r = subprocess.run(["aws", "s3", "cp", str(src), dst, "--only-show-errors"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("upload failed", dst, r.stderr[:300], flush=True)
        return False
    return True


def log(msg):
    print(time.strftime("%H:%M:%S "), msg, flush=True)


while True:
    try:
        loss = RUN / "loss.jsonl"
        if loss.exists():
            s3cp(loss, PREFIX + "/loss.jsonl")
        cks = sorted(RUN.glob("ckpt-*.pt"))
        for ck in cks:
            step = int(ck.stem.split("-")[1])
            if ck.name in done:
                continue
            # A checkpoint still being written has a sibling .tmp; skip it.
            if (RUN / (ck.name + ".tmp")).exists():
                continue
            size = ck.stat().st_size
            if size < 1_000_000_000:
                continue
            if step % WEIGHTS_EVERY == 0:
                sd = torch.load(ck, map_location="cpu", weights_only=False)
                slim = {"model": sd["model"], "step": sd["step"], "config": sd["config"]}
                out = RUN / ("weights-%07d.pt" % step)
                torch.save(slim, out)
                del sd, slim
                ok = s3cp(out, PREFIX + "/weights/" + out.name)
                out.unlink(missing_ok=True)
                log("weights %d uploaded %s" % (step, ok))
            if step % RESUME_EVERY == 0:
                ok = s3cp(ck, PREFIX + "/resume/" + ck.name)
                log("resume %d uploaded %s" % (step, ok))
            done.add(ck.name)
            json.dump({"done": sorted(done)}, open(state_path, "w"))
        # Prune: keep the newest KEEP_LOCAL ckpt files, latest.pt is separate.
        cks = sorted(RUN.glob("ckpt-*.pt"))
        for ck in cks[:-KEEP_LOCAL]:
            if ck.name in done:
                ck.unlink(missing_ok=True)
                log("pruned local %s" % ck.name)
    except Exception as exc:  # keep the watcher alive across transient faults
        log("cycle error %r" % (exc,))
    time.sleep(180)
