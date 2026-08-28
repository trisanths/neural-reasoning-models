"""The decisive test: does the model apply a rule it has just read?

The simple families answer with invented words that occur nowhere except in
the textbook page that defines them, so a correct answer is only possible by
reading that page. Three conditions, sampled rather than greedy because a
policy can carry the behaviour without it being the argmax yet:

  textbook        the defining page is retrievable
  wrong_textbook  a different invented system's pages are retrievable
  no_documents    nothing is retrievable

Rule application is demonstrated when textbook clearly beats both controls.
"""

from __future__ import annotations

import argparse
import json

import torch
import yaml

from src.evals.mc import load_checkpoint_model
from src.rl.env import EnvConfig, EpisodeEnv, load_tasks, rollout_stats
from src.rl.sampler import CachedPolicy
from src.skillacq.episodes import to_rl_episode
from src.skillacq.simple import SIMPLE_FAMILIES
from src.skillacq.systems import generate_episode
from src.train.tokenizer import load_tokenizer


def build_conditions(out_dir: str, start: int, count: int, n_problems: int) -> dict:
    fams = sorted(SIMPLE_FAMILIES)
    paths = {c: f"{out_dir}/rule_{c}.jsonl"
             for c in ("textbook", "wrong_textbook", "no_documents")}
    fh = {k: open(v, "w") for k, v in paths.items()}
    for s in range(start, start + count):
        fam = fams[s % len(fams)]
        ep = generate_episode(s, family=fam, n_problems=n_problems)
        rec = to_rl_episode(ep, n_context=0)
        fh["textbook"].write(json.dumps(rec) + "\n")

        other = generate_episode(s + 777000, family=fams[(s + 1) % len(fams)],
                                 n_problems=n_problems)
        wrong = dict(rec)
        wrong["documents"] = [{"text": p} for p in other.textbook]
        fh["wrong_textbook"].write(json.dumps(wrong) + "\n")

        empty = dict(rec)
        empty["documents"] = [{"text": "This page is intentionally blank."}]
        fh["no_documents"].write(json.dumps(empty) + "\n")
    for h in fh.values():
        h.close()
    return paths


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--config", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--start", type=int, default=2900000)
    ap.add_argument("--count", type=int, default=250)
    ap.add_argument("--n-problems", type=int, default=6)
    ap.add_argument("--temperature", type=float, default=0.7)
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

    paths = build_conditions(args.out, args.start, args.count, args.n_problems)
    results = {}
    for name, path in paths.items():
        tasks = load_tasks(path, tok,
                           questions_per_episode=int(task_cfg.get("questions_per_episode", 2)),
                           min_hops=int(task_cfg.get("min_hops", 1)),
                           max_prompt_tokens=int(task_cfg.get("max_prompt_tokens", 1024)),
                           limit_episodes=None, seed=0)
        policy = CachedPolicy(model, device, max_len=max_len,
                              temperature=args.temperature, seed=1234)
        rolls = []
        for start in range(0, len(tasks), 32):
            rolls.extend(env.rollout(policy, tasks[start:start + 32]))
        stats = rollout_stats(rolls)
        results[name] = {"n_tasks": len(tasks), **stats}
        print(f"[{name}] n={len(tasks)} " +
              " ".join(f"{k} {v:.4f}" for k, v in stats.items()
                       if isinstance(v, (int, float))), flush=True)

    with open(f"{args.out}/rule_test.json", "w") as fh:
        json.dump({"checkpoint": args.checkpoint, "temperature": args.temperature,
                   "conditions": results}, fh, indent=2)
    t = results["textbook"].get("accuracy", 0.0)
    w = results["wrong_textbook"].get("accuracy", 0.0)
    n = results["no_documents"].get("accuracy", 0.0)
    print(f"RULE_TEST textbook {t:.4f} wrong {w:.4f} blank {n:.4f} "
          f"lift_over_wrong {t - w:+.4f} lift_over_blank {t - n:+.4f}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
