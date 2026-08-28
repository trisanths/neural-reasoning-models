"""Recompute the non-neural answers in place, without touching the model run.

The model rollouts are expensive and the heuristics are not, so the two are
separable: this rewrites the baseline field of an existing prediction file
using the same load_tasks call that produced it.
"""

from __future__ import annotations

import argparse
import json
import random

import yaml

from src.falsify.probe import HEURISTICS, run_baseline, template_vocabulary
from src.rl.env import load_tasks
from src.train.tokenizer import load_tokenizer


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--pred", required=True)
    ap.add_argument("--conditions", default="textbook,wrong_textbook,no_documents,"
                                            "swapped,twin,twin_named,inverse_table,chain_rule,band_rule")
    args = ap.parse_args()

    with open(args.config) as fh:
        cfg = yaml.safe_load(fh)
    task_cfg = cfg.get("tasks", {})
    tok = load_tokenizer(args.tokenizer)
    vocab = template_vocabulary(200)
    print(f"template words {len(vocab)}", flush=True)

    for cond in args.conditions.split(","):
        path = f"{args.pred}/pred_{cond}.jsonl"
        try:
            records = [json.loads(l) for l in open(path)]
        except FileNotFoundError:
            continue
        tasks = load_tasks(f"{args.data}/ep_{cond}.jsonl", tok,
                           questions_per_episode=int(task_cfg.get("questions_per_episode", 2)),
                           min_hops=int(task_cfg.get("min_hops", 1)),
                           max_prompt_tokens=int(task_cfg.get("max_prompt_tokens", 1024)),
                           limit_episodes=None, seed=0)
        assert len(tasks) == len(records), (cond, len(tasks), len(records))
        rng = random.Random(7)
        for rec, t in zip(records, tasks):
            assert rec["qid"] == t.qid and rec["episode_index"] == t.episode_index
            rec["baseline"] = {}
            for name in HEURISTICS:
                for k in (1, 4, 6):
                    rec["baseline"][f"{name}@{k}"] = run_baseline(
                        name, t.question, t.documents, vocab, rng, topk=k)
        with open(path, "w") as fh:
            for rec in records:
                fh.write(json.dumps(rec) + "\n")
        print(f"[{cond}] {len(records)} rebaselined", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
