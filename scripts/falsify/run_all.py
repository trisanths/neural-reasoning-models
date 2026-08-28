"""Run the checkpoint and the non-neural baselines over identical items.

For every condition the same load_tasks call builds the task list, so the
model and each heuristic answer exactly the same questions from exactly the
same document store. Predictions are dumped raw; all grading happens later in
analyze.py so a single run can be scored under several graders.
"""

from __future__ import annotations

import argparse
import json
import random
import time

import torch
import yaml

from src.evals.mc import load_checkpoint_model
from src.falsify.probe import HEURISTICS, run_baseline, template_vocabulary
from src.rl.env import EnvConfig, EpisodeEnv, load_tasks
from src.rl.sampler import CachedPolicy
from src.train.tokenizer import load_tokenizer


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--config", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--conditions", default="textbook,wrong_textbook,no_documents,"
                                            "swapped,twin,twin_named,inverse_table,chain_rule,band_rule")
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--seeds", type=int, default=1,
                    help="model sampling repeats, for a cleaner accuracy estimate")
    args = ap.parse_args()

    with open(args.config) as fh:
        cfg = yaml.safe_load(fh)
    env_cfg = EnvConfig(**cfg.get("env", {}))
    task_cfg = cfg.get("tasks", {})
    max_len = int(cfg.get("env", {}).get("max_len", 2048))

    tok = load_tokenizer(args.tokenizer)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, _ = load_checkpoint_model(args.checkpoint, device)
    model.eval()
    env = EpisodeEnv(tok, env_cfg)

    print("learning the template vocabulary from the corpus", flush=True)
    vocab = template_vocabulary(200)
    print(f"template words {len(vocab)}", flush=True)

    for cond in args.conditions.split(","):
        t0 = time.time()
        path = f"{args.data}/ep_{cond}.jsonl"
        tasks = load_tasks(path, tok,
                           questions_per_episode=int(task_cfg.get("questions_per_episode", 2)),
                           min_hops=int(task_cfg.get("min_hops", 1)),
                           max_prompt_tokens=int(task_cfg.get("max_prompt_tokens", 1024)),
                           limit_episodes=None, seed=0)
        records = [{"episode_index": t.episode_index, "qid": t.qid,
                    "question": t.question, "gold": t.gold, "domain": t.domain,
                    "model": [], "n_rounds": [], "stop": [], "baseline": {}}
                   for t in tasks]

        for rep in range(args.seeds):
            policy = CachedPolicy(model, device, max_len=max_len,
                                  temperature=args.temperature, seed=1234 + 1000 * rep)
            rolls = []
            for start in range(0, len(tasks), 32):
                rolls.extend(env.rollout(policy, tasks[start:start + 32]))
            for rec, roll in zip(records, rolls):
                rec["model"].append(roll.answer_text)
                rec["n_rounds"].append(roll.n_rounds)
                rec["stop"].append(roll.stop_reason)
                if rep == 0:
                    rec["retrieved"] = [r["chunk"] for r in roll.rounds]

        rng = random.Random(7)
        for rec, t in zip(records, tasks):
            for name in HEURISTICS:
                for k in (1, 4, 6):
                    rec["baseline"][f"{name}@{k}"] = run_baseline(
                        name, t.question, t.documents, vocab, rng, topk=k)
        with open(f"{args.out}/pred_{cond}.jsonl", "w") as fh:
            for rec in records:
                fh.write(json.dumps(rec) + "\n")
        print(f"[{cond}] n={len(tasks)} {time.time() - t0:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
