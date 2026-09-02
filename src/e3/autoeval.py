"""Evaluate every checkpoint the training run publishes, as it publishes it.

Polls the S3 weights prefix, and for each step not yet measured downloads the
slim checkpoint, runs the existing calibrated harnesses on it, appends one row
to curve.jsonl and pushes that back to S3. The loop owns no scoring of its
own: MMLU goes through src.extern.bench_ours and the retrieval policy through
src.extern.retrieval_ours, both unchanged, and only the interval and the floor
test are added here.

Running this beside the trainer costs the trainer about two minutes of
throughput per checkpoint, which at one checkpoint per 1000 steps is under
three percent.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

from src.e3.interval import summarise

TOKENS_PER_STEP = 262144
PREFIX = "s3://decoupled-reasoner-009398924577/runs/e3-350m"
WORK = Path("/mnt/nvme/e3eval")
CURVE = WORK / "curve.jsonl"
REPO = Path("/home/ec2-user/decoupled-reasoner")


def sh(cmd, **kw):
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, **kw)


def log(msg):
    print(time.strftime("%H:%M:%S "), msg, flush=True)


def done_steps():
    if not CURVE.exists():
        return set()
    out = set()
    for line in CURVE.read_text().splitlines():
        if line.strip():
            out.add(json.loads(line)["step"])
    return out


def list_remote():
    r = sh(["aws", "s3", "ls", PREFIX + "/weights/"])
    steps = {}
    for line in r.stdout.splitlines():
        parts = line.split()
        if parts and parts[-1].startswith("weights-"):
            name = parts[-1]
            steps[int(name[len("weights-"):-3])] = name
    return steps


def mmlu(ckpt, tag, n, seed=1234):
    out = WORK / f"mmlu_{tag}_n{n}_s{seed}.json"
    r = sh([sys.executable, "-m", "src.extern.bench_ours", "--ckpt", str(ckpt),
            "--tag", tag, "--task", "mmlu", "--n", str(n), "--seed", str(seed),
            "--out", str(out), "--device", "cuda"])
    if r.returncode != 0:
        log("mmlu failed " + r.stderr[-400:])
        return None
    res = json.load(open(out))
    recs = res["records"]
    k = sum(x["pred"] == x["gold"] for x in recs)
    row = summarise(k, len(recs), res["floor"])
    counts = [0, 0, 0, 0]
    for x in recs:
        if x["pred"] < 4:
            counts[x["pred"]] += 1
    row["pred_letter_counts"] = counts
    row["record_file"] = str(out)
    sh(["aws", "s3", "cp", str(out), f"{PREFIX}/eval/{out.name}",
        "--only-show-errors"])
    return row


def retrieval(ckpt, tag, n=200, seed=1234):
    out = WORK / f"ret_{tag}_n{n}.json"
    r = sh([sys.executable, "-m", "src.extern.retrieval_ours", "--ckpt",
            str(ckpt), "--tag", tag, "--n", str(n), "--seed", str(seed),
            "--passes", "none", "--max-new-tokens", "256", "--device", "cuda",
            "--cache", str(WORK / "exacache_e3_none"), "--out", str(out)])
    if r.returncode != 0:
        log("retrieval failed " + r.stderr[-400:])
        return None
    res = json.load(open(out))
    cell = res.get("none") or {}
    n_eff = cell.get("n", 0)
    issued = summarise(round(cell.get("issued_query", 0.0) * n_eff), n_eff, 0.0)
    sh(["aws", "s3", "cp", str(out), f"{PREFIX}/eval/{out.name}",
        "--only-show-errors"])
    return {"issued_query": cell.get("issued_query"),
            "issued_query_ci95": issued["ci95"],
            "named_none": cell.get("named_none"),
            "strict": cell.get("strict"), "n": n_eff,
            "record_file": str(out)}


def main() -> int:
    WORK.mkdir(parents=True, exist_ok=True)
    while True:
        try:
            have = done_steps()
            remote = list_remote()
            todo = sorted(s for s in remote if s not in have)
            for step in todo:
                name = remote[step]
                local = WORK / "cur.pt"
                log(f"fetching {name}")
                r = sh(["aws", "s3", "cp", f"{PREFIX}/weights/{name}",
                        str(local), "--only-show-errors"])
                if r.returncode != 0:
                    log("fetch failed " + r.stderr[-300:])
                    continue
                tag = f"e3step{step}"
                row = {"step": step,
                       "tokens_seen": step * TOKENS_PER_STEP,
                       "tokens_per_param": round(
                           step * TOKENS_PER_STEP / 375440384, 4),
                       "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                            time.gmtime()),
                       "mmlu_n500": mmlu(local, tag, 500),
                       "mmlu_n1000": mmlu(local, tag, 1000),
                       "retrieval_none_n200": retrieval(local, tag, 200)}
                with open(CURVE, "a") as fh:
                    fh.write(json.dumps(row) + "\n")
                sh(["aws", "s3", "cp", str(CURVE), f"{PREFIX}/eval/curve.jsonl",
                    "--only-show-errors"])
                local.unlink(missing_ok=True)
                m = row["mmlu_n1000"]
                log(f"step {step} tok/param {row['tokens_per_param']} "
                    f"mmlu_n1000 {m and m['acc']} ci {m and m['ci95']}")
        except Exception as exc:
            log("cycle error %r" % (exc,))
        time.sleep(300)


if __name__ == "__main__":
    raise SystemExit(main())
