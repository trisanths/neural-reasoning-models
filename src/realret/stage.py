"""Put the datasets this lane needs on a worker, and prove they arrived.

A worker is bootstrapped with code and a checkpoint and not with data. A run
that discovers this only when a table comes out empty has wasted a card, and
one that never discovers it reports numbers computed over nothing. So every
file is recorded with its size and MD5 in a manifest written before it is
used, the manifest is re-verified against the bytes on disk afterwards, and
the counts are reported rather than an assurance that it went fine.

Two sources.

  s3     the diversity corpus components, which are the synthetic half of
         the training mixture. There is no way to regenerate these on a
         worker, so they move.
  hub    the four public benchmark test sets, laid out where
         `src/extern/bench.py` reads them. These are small and pulling them
         from their origin is one less copy to trust.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import time

BUCKET = "s3://decoupled-reasoner-009398924577"

CORPUS_FILES = [
    "relation_train.jsonl", "plan_train_step.jsonl", "plan_train_whole.jsonl",
    "external_train.jsonl", "mathgen_train.jsonl",
]

HUB_FILES = [
    ("cais/mmlu", "all/test-00000-of-00001.parquet",
     "extern/mmlu/all/test-00000-of-00001.parquet"),
    ("cais/mmlu", "all/dev-00000-of-00001.parquet",
     "extern/mmlu/all/dev-00000-of-00001.parquet"),
    ("allenai/ai2_arc", "ARC-Challenge/test-00000-of-00001.parquet",
     "extern/ai2_arc/ARC-Challenge/test-00000-of-00001.parquet"),
    ("allenai/winogrande", "winogrande_xl/validation-00000-of-00001.parquet",
     "extern/winogrande/winogrande_xl/validation-00000-of-00001.parquet"),
    ("openai/gsm8k", "main/test-00000-of-00001.parquet",
     "extern/gsm8k/main/test-00000-of-00001.parquet"),
]


def md5(path: str, chunk: int = 1 << 22) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def record(path: str) -> dict:
    st = os.stat(path)
    return {"path": path, "bytes": st.st_size, "md5": md5(path)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus-dir", required=True)
    ap.add_argument("--data-dir", required=True, help="repo data/ directory")
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--skip-corpus", action="store_true")
    a = ap.parse_args()

    os.makedirs(a.corpus_dir, exist_ok=True)
    os.makedirs(a.data_dir, exist_ok=True)
    entries: list[dict] = []
    t0 = time.time()

    if not a.skip_corpus:
        for name in CORPUS_FILES:
            dst = os.path.join(a.corpus_dir, name)
            if not os.path.exists(dst):
                subprocess.run(
                    ["aws", "s3", "cp", f"{BUCKET}/data/corpus/v1/{name}", dst,
                     "--only-show-errors"], check=True)
            entries.append({"source": "s3", **record(dst)})
            print(f"staged {name} {entries[-1]['bytes']} {entries[-1]['md5']}",
                  flush=True)

    from huggingface_hub import hf_hub_download
    for repo, remote, rel in HUB_FILES:
        dst = os.path.join(a.data_dir, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if not os.path.exists(dst):
            got = hf_hub_download(repo, remote, repo_type="dataset")
            subprocess.run(["cp", got, dst], check=True)
        entries.append({"source": f"hub:{repo}", **record(dst)})
        print(f"staged {rel} {entries[-1]['bytes']} {entries[-1]['md5']}",
              flush=True)

    manifest = {"written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "entries": entries, "n": len(entries),
                "seconds": round(time.time() - t0, 1)}
    os.makedirs(os.path.dirname(a.manifest) or ".", exist_ok=True)
    with open(a.manifest, "w") as fh:
        json.dump(manifest, fh, indent=1)

    # Re-read every byte and compare against the manifest just written.
    ok = bad = 0
    for e in entries:
        if os.path.exists(e["path"]) and md5(e["path"]) == e["md5"] \
                and os.stat(e["path"]).st_size == e["bytes"]:
            ok += 1
        else:
            bad += 1
            print(f"MISMATCH {e['path']}", flush=True)
    manifest["verified_ok"] = ok
    manifest["verified_bad"] = bad
    with open(a.manifest, "w") as fh:
        json.dump(manifest, fh, indent=1)
    print(json.dumps({"files": len(entries), "verified_ok": ok,
                      "verified_bad": bad, "manifest": a.manifest}), flush=True)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
