"""Remove the episodes a benchmark test item reaches, and the split duplicates.

Two removals, both by content rather than by a hand-written list of ids.

  benchmark   an episode goes if a benchmark test stem appears verbatim in
              its question or in any document of its bundle, or if a training
              question and a benchmark stem share more than the near
              threshold of their word 5-grams. Every document in the bundle
              is scanned and not only the ones the planned trace serves,
              because a bundle document the plan skips is still a document
              the serving gate can return at evaluation time.

  split       a training episode goes if its content hash appears in the
              evaluation file for its source. TriviaQA ships the same
              question in its train and validation files, and a question
              answered in training is not a held-out question.

Removal is from the training side in both cases, so the evaluation sets keep
their stated denominators.

The counts are the point. This writes how many episodes were removed, why,
and which benchmark stem reached each one, and the contamination scan is then
re-run over the cleaned files so the reported number is measured on what is
trained rather than promised about it.
"""

from __future__ import annotations

import argparse
import json
import os
import time

from src.realret.contam import bench_items, grams, norm


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", nargs="+", required=True)
    ap.add_argument("--eval", nargs="*", default=[],
                    help="source=path pairs whose hashes are removed from train")
    ap.add_argument("--root", default="data/extern")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--near-threshold", type=float, default=0.7)
    a = ap.parse_args()

    t0 = time.time()
    items = bench_items(a.root)
    post: dict = {}
    stems = []
    for i, it in enumerate(items):
        g = grams(it["stem"].split())
        stems.append((it, g))
        for x in g:
            post.setdefault(x, []).append(i)

    eval_hashes: dict = {}
    for spec in a.eval:
        src, path = spec.split("=", 1)
        hs = set()
        with open(path) as fh:
            for line in fh:
                hs.add(json.loads(line)["hash"])
        eval_hashes[src] = hs

    os.makedirs(a.out_dir, exist_ok=True)
    report: dict = {"near_threshold": a.near_threshold, "files": {},
                    "removed_examples": []}
    for path in a.episodes:
        out = os.path.join(a.out_dir, os.path.basename(path))
        kept = 0
        removed = {"benchmark_exact": 0, "benchmark_near": 0, "split_dup": 0}
        with open(path) as fh, open(out, "w") as sink:
            for line in fh:
                ep = json.loads(line)
                q = ep["questions"][0]
                src = ep.get("source", "")
                if ep.get("hash") in eval_hashes.get(src, ()):
                    removed["split_dup"] += 1
                    continue
                why = None
                hit = None
                fields = [q["text"]] + [d["text"] for d in ep["documents"]]
                for text in fields:
                    s = norm(text)
                    g = grams(s.split())
                    if not g:
                        continue
                    cand: dict = {}
                    for x in g:
                        for i in post.get(x, ()):  # noqa: PERF
                            cand[i] = cand.get(i, 0) + 1
                    for i, shared in cand.items():
                        it, bg = stems[i]
                        if it["stem"] and it["stem"] in s:
                            why, hit = "benchmark_exact", it
                            break
                        if shared / max(1, len(g | bg)) >= a.near_threshold:
                            why, hit = "benchmark_near", it
                            break
                    if why:
                        break
                if why:
                    removed[why] += 1
                    if len(report["removed_examples"]) < 60:
                        report["removed_examples"].append({
                            "file": os.path.basename(path), "why": why,
                            "qid": ep.get("qid"), "source": src,
                            "question": q["text"][:160],
                            "benchmark_task": hit["task"],
                            "benchmark_stem": hit["stem"][:160]})
                    continue
                sink.write(line)
                kept += 1
        total = kept + sum(removed.values())
        report["files"][path] = {"in": total, "kept": kept,
                                 "removed": removed, "out": os.path.abspath(out)}
        print(f"{os.path.basename(path)}: in {total} kept {kept} "
              f"removed {json.dumps(removed)}", flush=True)

    report["seconds"] = round(time.time() - t0, 1)
    report["totals"] = {
        k: sum(v["removed"][k] for v in report["files"].values())
        for k in ("benchmark_exact", "benchmark_near", "split_dup")}
    report["kept_total"] = sum(v["kept"] for v in report["files"].values())
    report["in_total"] = sum(v["in"] for v in report["files"].values())
    os.makedirs(os.path.dirname(a.report) or ".", exist_ok=True)
    with open(a.report, "w") as fh:
        json.dump(report, fh, indent=1)
    print(json.dumps({k: v for k, v in report.items()
                      if k != "removed_examples"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
