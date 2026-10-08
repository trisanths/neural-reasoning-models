"""The pilot runner: models x thinking x conditions over the item set, plus PopQA.

One records file per (model, thinking) for the generation items and one per
model for PopQA, all under --out:

    gen__<model>__think<0|1>.jsonl    one line per (item, condition)
    popqa__<model>.jsonl              one line per PopQA item
    throughput.jsonl                  wall time and token counts per batch
    run_log.jsonl                     one line per model: exit code, seconds,
                                      mirror failures
    RUNNING.lock                      present while the parent loop runs
    RUNNING.<model>.lock              present while one model's child runs

Resume. A record is keyed by (item_id, condition, prompt_hash); a rerun
skips every key already on disk, so a crash costs at most one batch. A torn
last line from a crash mid-write is cut off before appending. Records carry
the sha256 of the items file they were made from, the git commit and the
sha256 of the grader they were written under, and the report refuses any
record whose sha or prompt hash no longer matches and any configuration
whose records span more than one commit.

Mirror. After every batch the file just written is copied to the --s3
prefix, so the box can disappear without losing more than a batch. After
each model the parent copies every records file and run_log.jsonl once
more; a failed copy is counted, written to run_log.jsonl, and makes the
parent exit non-zero with a summary line.

Each model runs in its own subprocess, so the GPU is handed back in full
between models.

  python scripts/pilot_run.py --items /mnt/nvme/pilot/items/items.jsonl \\
      --popqa /mnt/nvme/pilot/items/popqa_fc.jsonl \\
      --out /mnt/nvme/pilot/records --s3 s3://.../runs/pilot-acq/records
"""

from __future__ import annotations

import argparse
import json
import os
import random
import subprocess
import sys
import time

from src.pilot.grade import grade
from src.pilot.items import CONDITIONS, file_sha, load_items, prompt_hash

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GEN_BATCH = 768
THINK_BATCH = 384
POPQA_BATCH = 1000


def gen_path(out_dir: str, model: str, thinking: bool) -> str:
    return os.path.join(out_dir, f"gen__{model}__think{int(thinking)}.jsonl")


def popqa_path(out_dir: str, model: str) -> str:
    return os.path.join(out_dir, f"popqa__{model}.jsonl")


def _utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def repair_tail(path: str) -> int:
    """Cut a torn last line left by a crash. Returns bytes removed."""
    if not os.path.exists(path):
        return 0
    with open(path, "rb+") as fh:
        data = fh.read()
        if not data or data.endswith(b"\n"):
            return 0
        keep = data.rfind(b"\n") + 1
        fh.truncate(keep)
        return len(data) - keep


def read_jsonl(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def append_jsonl(path: str, recs: list[dict]) -> None:
    with open(path, "a", encoding="utf-8") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


MIRROR_FAILURES: list[str] = []
PILOT_CODE_PATHS = ("src/pilot", "src/mathgen", "src/skillacq", "src/evals",
                    "src/extern", "scripts/pilot_run.py",
                    "scripts/pilot_report.py", "scripts/pilot_items.py",
                    "scripts/pilot_popqa.py")


def mirror(path: str, s3_prefix: str | None) -> bool:
    if not s3_prefix:
        return True
    dest = s3_prefix.rstrip("/") + "/" + os.path.basename(path)
    r = subprocess.run(["aws", "s3", "cp", path, dest, "--only-show-errors"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        MIRROR_FAILURES.append(os.path.basename(path))
        print(f"MIRROR FAILED for {path}: {r.stderr.strip()[:300]}", flush=True)
    return r.returncode == 0


def mirror_all(out_dir: str, s3_prefix: str | None) -> list[str]:
    """Copy every records and log file once more; the names that failed."""
    failed = []
    if not s3_prefix or not os.path.isdir(out_dir):
        return failed
    for name in sorted(os.listdir(out_dir)):
        if name.endswith(".jsonl") and name.startswith(
                ("gen__", "popqa__", "throughput", "run_log")):
            if not mirror(os.path.join(out_dir, name), s3_prefix):
                failed.append(name)
    return failed


def provenance() -> dict:
    """The commit the code runs at, whether src/ differs from it, and the
    grader's own hash, written into every record."""
    def git(*a):
        r = subprocess.run(["git", *a], cwd=REPO_ROOT, capture_output=True,
                           text=True)
        return r.stdout.strip() if r.returncode == 0 else None
    import hashlib

    from src.pilot import grade as grade_mod
    with open(grade_mod.__file__, "rb") as fh:
        grade_sha = hashlib.sha256(fh.read()).hexdigest()[:16]
    # Only the code the pilot imports or runs; an unrelated local edit
    # elsewhere in src/ says nothing about these records.
    dirty = git("status", "--porcelain", "--untracked-files=no", "--",
                *PILOT_CODE_PATHS)
    return {"git_head": git("rev-parse", "HEAD"),
            "git_dirty": bool(dirty) if dirty is not None else None,
            "grade_sha": grade_sha}


def select_items(items: list[dict], limit_per_cell: int | None) -> list[dict]:
    """All items, or the first limit_per_cell of each family x level cell."""
    if not limit_per_cell:
        return items
    seen: dict = {}
    out = []
    for it in items:
        key = (it["family"], it["level"])
        if seen.get(key, 0) < limit_per_cell:
            out.append(it)
            seen[key] = seen.get(key, 0) + 1
    return out


_PROVENANCE: dict = {}


def make_record(spec, thinking: bool, item: dict, cond: str, gen,
                items_sha: str, decode: dict) -> dict:
    completion = spec.kind == "base"
    g = grade(gen.text, item, completion=completion)
    if not _PROVENANCE:
        _PROVENANCE.update(provenance())
    floors = item.get("floors") or {}
    return {
        "model": spec.name, "hf_id": spec.hf_id, "kind": spec.kind,
        "thinking": thinking, "condition": cond,
        "item_id": item["item_id"], "family": item["family"],
        "level": item["level"], "floor": floors.get(cond, item["floor"]),
        **_PROVENANCE,
        "answer": item["answer"], "answer_kind": item["answer_kind"],
        "prompt_hash": item["prompt_hashes"][cond], "items_sha": items_sha,
        "raw": gen.raw, "text": gen.text, **g,
        "n_prompt_tokens": gen.n_prompt_tokens,
        "n_think_tokens": gen.n_think_tokens,
        "n_answer_tokens": gen.n_answer_tokens,
        "think_truncated": gen.think_truncated,
        "finish_reason": gen.finish_reason, "decode": decode,
        "written_utc": _utc(),
    }


def run_generation(backend, thinking: bool, items: list[dict], conditions,
                   out_dir: str, items_sha: str, s3: str | None,
                   batch_size: int | None = None) -> dict:
    spec = backend.spec
    backend.set_thinking(thinking)
    path = gen_path(out_dir, spec.name, thinking)
    repair_tail(path)
    done = {(r["item_id"], r["condition"], r["prompt_hash"])
            for r in read_jsonl(path)}
    todo = [(it, c) for it in items for c in conditions
            if (it["item_id"], c, it["prompt_hashes"][c]) not in done]
    for it, c in todo:
        if prompt_hash(it["prompts"][c]) != it["prompt_hashes"][c]:
            raise SystemExit(f"{it['item_id']} {c}: prompt does not match its hash")
    bs = batch_size or (THINK_BATCH if thinking else GEN_BATCH)
    decode = backend.decode_params()
    stats = {"model": spec.name, "thinking": thinking, "skipped": len(done),
             "todo": len(todo), "seconds": 0.0, "prompt_tokens": 0,
             "generated_tokens": 0}
    for start in range(0, len(todo), bs):
        chunk = todo[start:start + bs]
        t0 = time.time()
        gens = backend.generate([it["prompts"][c] for it, c in chunk])
        dt = time.time() - t0
        recs = [make_record(spec, thinking, it, c, g, items_sha, decode)
                for (it, c), g in zip(chunk, gens)]
        append_jsonl(path, recs)
        mirror(path, s3)
        n_in = sum(r["n_prompt_tokens"] for r in recs)
        n_out = sum(r["n_think_tokens"] + r["n_answer_tokens"] for r in recs)
        stats["seconds"] += dt
        stats["prompt_tokens"] += n_in
        stats["generated_tokens"] += n_out
        append_jsonl(os.path.join(out_dir, "throughput.jsonl"), [{
            "model": spec.name, "thinking": thinking, "phase": "generate",
            "n_prompts": len(chunk), "seconds": round(dt, 2),
            "prompt_tokens": n_in, "generated_tokens": n_out,
            "think_truncated": sum(r["think_truncated"] for r in recs),
            "written_utc": _utc()}])
        print(f"{spec.name} think={int(thinking)} {start + len(chunk)}/"
              f"{len(todo)} {dt:.1f}s gen_tok={n_out}", flush=True)
    return stats


def run_popqa(backend, items: list[dict], out_dir: str, popqa_sha: str,
              s3: str | None, batch_size: int = POPQA_BATCH) -> dict:
    from src.pilot.popqa import context_of, pairs_of, score_item

    spec = backend.spec
    path = popqa_path(out_dir, spec.name)
    repair_tail(path)
    done = {r["item_id"] for r in read_jsonl(path)}
    todo = [it for it in items if it["item_id"] not in done]
    if not _PROVENANCE:
        _PROVENANCE.update(provenance())
    t_all = 0.0
    for start in range(0, len(todo), batch_size):
        chunk = todo[start:start + batch_size]
        pairs = []
        for it in chunk:
            pairs += pairs_of(it)
            if it.get("masked_question"):
                pairs += pairs_of(it, masked=True)
        t0 = time.time()
        stats = backend.loglik(pairs)
        dt = time.time() - t0
        t_all += dt
        recs = []
        pos = 0
        for it in chunk:
            k = len(it["options"])
            real = stats[pos:pos + k]
            pos += k
            masked = None
            if it.get("masked_question"):
                masked = stats[pos:pos + k]
                pos += k
            s = score_item(it, real, masked)
            recs.append({"model": spec.name, "hf_id": spec.hf_id,
                         "kind": spec.kind, "item_id": it["item_id"],
                         "quartile": it["quartile"], "prop": it["prop"],
                         "s_pop": it["s_pop"], "floor": it["floor"],
                         "gold_index": it["gold_index"], **s,
                         "context_hash": prompt_hash(context_of(it)),
                         "popqa_sha": popqa_sha, **_PROVENANCE,
                         "written_utc": _utc()})
        append_jsonl(path, recs)
        mirror(path, s3)
        append_jsonl(os.path.join(out_dir, "throughput.jsonl"), [{
            "model": spec.name, "phase": "popqa", "n_items": len(chunk),
            "n_pairs": len(pairs), "seconds": round(dt, 2),
            "written_utc": _utc()}])
    return {"model": spec.name, "popqa_todo": len(todo), "seconds": t_all}


def throughput_probe(backend, items: list[dict], n: int, out_dir: str,
                     thinking_modes) -> list[dict]:
    """Time generation on n prompts sampled across the item set. No grading."""
    rng = random.Random(0)
    pool = [(it, c) for it in items for c in CONDITIONS]
    sample = rng.sample(pool, min(n, len(pool)))
    rows = []
    for thinking in thinking_modes:
        backend.set_thinking(thinking)
        t0 = time.time()
        gens = backend.generate([it["prompts"][c] for it, c in sample])
        dt = time.time() - t0
        row = {"model": backend.spec.name, "thinking": thinking,
               "phase": "probe", "n_prompts": len(sample),
               "seconds": round(dt, 2),
               "prompt_tokens": sum(g.n_prompt_tokens for g in gens),
               "generated_tokens": sum(g.n_think_tokens + g.n_answer_tokens
                                       for g in gens),
               "think_truncated": sum(g.think_truncated for g in gens),
               "per_full_set_hours": round(dt / len(sample) * len(pool) / 3600, 3),
               "written_utc": _utc()}
        rows.append(row)
        print(json.dumps(row), flush=True)
    append_jsonl(os.path.join(out_dir, "throughput_probe.jsonl"), rows)
    return rows


# --------------------------------------------------------------------------
# entry points
# --------------------------------------------------------------------------
def reap_engines(wait: float = 60.0) -> list[str]:
    """Stop vLLM engine processes a finished child left behind.

    A vLLM engine core is a separate process and survives its parent when the
    parent is killed, holding the GPU memory the next model needs. Only this
    user's processes are touched. Returns the pids it signalled.
    """
    uid = str(os.getuid())
    r = subprocess.run(["pgrep", "-u", uid, "-f", "VLLM::EngineCore"],
                       capture_output=True, text=True)
    pids = [p for p in r.stdout.split() if p.strip()]
    for p in pids:
        subprocess.run(["kill", p], capture_output=True)
    deadline = time.time() + wait
    while pids and time.time() < deadline:
        r = subprocess.run(["pgrep", "-u", uid, "-f", "VLLM::EngineCore"],
                           capture_output=True, text=True)
        if not r.stdout.strip():
            break
        time.sleep(1)
    if pids:
        print(f"reaped leftover engine processes {pids}", flush=True)
    return pids


def _child(args) -> int:
    from src.pilot.vllm_model import MODELS, VLLMModel

    spec = MODELS[args.models]
    os.makedirs(args.out, exist_ok=True)
    lock = os.path.join(args.out, f"RUNNING.{spec.name}.lock")
    with open(lock, "w") as fh:
        json.dump({"pid": os.getpid(), "model": spec.name, "since": _utc()}, fh)
    backend = None
    try:
        backend = VLLMModel(spec, max_model_len=args.max_model_len,
                            gpu_memory_utilization=args.gpu_mem)
        modes = [m for m in spec.thinking_modes
                 if args.thinking == "both" or (args.thinking == "on") == m]
        if args.items:
            items = select_items(load_items(args.items), args.limit_per_cell)
            if args.probe:
                throughput_probe(backend, items, args.probe, args.out, modes)
                return 0
            sha = file_sha(args.items)
            for thinking in modes:
                st = run_generation(backend, thinking, items, args.conditions,
                                    args.out, sha, args.s3, args.batch_size)
                print(json.dumps(st), flush=True)
        if args.popqa and not args.skip_popqa:
            pitems = load_items(args.popqa)
            if args.popqa_limit:
                pitems = pitems[:args.popqa_limit]
            st = run_popqa(backend, pitems, args.out, file_sha(args.popqa), args.s3)
            print(json.dumps(st), flush=True)
    finally:
        if backend is not None:
            backend.close()
        if os.path.exists(lock):
            os.remove(lock)
        for name in ("throughput.jsonl", "throughput_probe.jsonl"):
            p = os.path.join(args.out, name)
            if os.path.exists(p):
                mirror(p, args.s3)
        if MIRROR_FAILURES:
            print(f"MIRROR FAILURES in this child: {len(MIRROR_FAILURES)} "
                  f"({sorted(set(MIRROR_FAILURES))})", flush=True)
    return 0


def main(argv=None) -> int:
    from src.pilot.vllm_model import MODELS

    ap = argparse.ArgumentParser(description="run the acquisition pilot")
    ap.add_argument("--items", default=None)
    ap.add_argument("--popqa", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--s3", default=None, help="s3 prefix to mirror records to")
    ap.add_argument("--models", default="all",
                    help="comma list of names from src/pilot/vllm_model.MODELS")
    ap.add_argument("--conditions", default=",".join(CONDITIONS))
    ap.add_argument("--thinking", choices=["both", "off", "on"], default="both")
    ap.add_argument("--limit-per-cell", type=int, default=None)
    ap.add_argument("--popqa-limit", type=int, default=None)
    ap.add_argument("--skip-popqa", action="store_true")
    ap.add_argument("--batch-size", type=int, default=None)
    ap.add_argument("--probe", type=int, default=0,
                    help="time generation on this many sampled prompts, no records")
    ap.add_argument("--max-model-len", type=int, default=24576)
    ap.add_argument("--gpu-mem", type=float, default=0.88)
    ap.add_argument("--child", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    args.conditions = tuple(c for c in args.conditions.split(",") if c)
    bad = [c for c in args.conditions if c not in CONDITIONS]
    if bad:
        raise SystemExit(f"unknown conditions {bad}")

    if args.child:
        rc = _child(args)
        # vLLM's engine teardown at interpreter exit can abort the process
        # ("terminate called without an active exception") after every record
        # is safely on disk; leave without running it so the exit code means
        # what happened to the run.
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(rc)

    names = list(MODELS) if args.models == "all" else args.models.split(",")
    unknown = [n for n in names if n not in MODELS]
    if unknown:
        raise SystemExit(f"unknown models {unknown}; known {list(MODELS)}")
    os.makedirs(args.out, exist_ok=True)
    # The run-level lock: held for the whole loop, so a report cannot be
    # built between two models. A parent killed outright leaves it behind;
    # remove it by hand after checking nothing is running.
    run_lock = os.path.join(args.out, "RUNNING.lock")
    with open(run_lock, "w") as fh:
        json.dump({"pid": os.getpid(), "models": names, "since": _utc()}, fh)
    failures, mirror_failed = [], []
    try:
        for name in names:
            cmd = [sys.executable, "-m", "src.pilot.runner", "--child",
                   "--models", name] + [a for a in _passthrough(argv)]
            t0 = time.time()
            print(f"== {name} start {_utc()}", flush=True)
            rc = subprocess.run(cmd, cwd=REPO_ROOT).returncode
            reap_engines()
            print(f"== {name} exit {rc} after {time.time() - t0:.0f}s", flush=True)
            failed = mirror_all(args.out, args.s3)
            append_jsonl(os.path.join(args.out, "run_log.jsonl"), [{
                "model": name, "exit": rc, "seconds": round(time.time() - t0, 1),
                "mirror_failed": failed, "written_utc": _utc()}])
            failed += mirror_all_log(args.out, args.s3)
            mirror_failed += failed
            if rc != 0:
                failures.append(name)
    finally:
        if os.path.exists(run_lock):
            os.remove(run_lock)
    rc = 0
    if failures:
        print(f"models that failed: {failures}", flush=True)
        rc = 1
    if mirror_failed:
        print(f"MIRROR FAILED for {sorted(set(mirror_failed))}: the records "
              f"are on this box only until they are copied by hand", flush=True)
        rc = rc or 4
    return rc


def mirror_all_log(out_dir: str, s3_prefix: str | None) -> list[str]:
    p = os.path.join(out_dir, "run_log.jsonl")
    if os.path.exists(p) and not mirror(p, s3_prefix):
        return ["run_log.jsonl"]
    return []


def _passthrough(argv) -> list[str]:
    """The parent's arguments minus --models and its value."""
    argv = list(sys.argv[1:] if argv is None else argv)
    out, skip = [], False
    for a in argv:
        if skip:
            skip = False
            continue
        if a == "--models":
            skip = True
            continue
        if a.startswith("--models="):
            continue
        out.append(a)
    return out


if __name__ == "__main__":
    raise SystemExit(main())
