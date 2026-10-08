"""Score one checkpoint on one episodes file, with the textbook either
retrievable or placed directly in context.

The in-context condition answers a different question from the retrieval one:
not can the model find the rules, but can it execute them at all once it has
them. Separating those two is what tells us where the failure lives.
"""

from __future__ import annotations

import argparse
import json

import torch
import yaml

from src.evals.mc import load_checkpoint_model
from src.rl.env import EnvConfig, EpisodeEnv, load_tasks, rollout_stats
from src.rl.sampler import CachedPolicy
from src.train.tokenizer import load_tokenizer


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--config", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--episodes", required=True)
    ap.add_argument("--in-context", action="store_true",
                    help="place every textbook page in the prompt instead of retrieving")
    ap.add_argument("--label", default="eval")
    ap.add_argument("--temperature", type=float, default=0.0)
    args = ap.parse_args()

    with open(args.config) as fh:
        cfg = yaml.safe_load(fh)
    env_cfg = EnvConfig(**cfg.get("env", {}))
    task_cfg = cfg.get("tasks", {})
    max_len = int(cfg.get("env", {}).get("max_len", 2048))

    path = args.episodes
    if args.in_context:
        path = args.episodes + ".incontext"
        with open(args.episodes) as src, open(path, "w") as dst:
            for line in src:
                d = json.loads(line)
                d["n_context"] = len(d.get("documents", []))
                dst.write(json.dumps(d) + "\n")

    tok = load_tokenizer(args.tokenizer)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, _ = load_checkpoint_model(args.checkpoint, device)
    env = EpisodeEnv(tok, env_cfg)
    tasks = load_tasks(path, tok,
                       questions_per_episode=int(task_cfg.get("questions_per_episode", 2)),
                       min_hops=int(task_cfg.get("min_hops", 1)),
                       max_prompt_tokens=int(task_cfg.get("max_prompt_tokens", 4096)),
                       limit_episodes=None,
                       seed=0)
    policy = CachedPolicy(model, device, max_len=max_len,
                          temperature=args.temperature, seed=99)
    rolls = []
    for i in range(0, len(tasks), 32):
        rolls.extend(env.rollout(policy, tasks[i:i + 32]))
    stats = rollout_stats(rolls)
    print(f"[{args.label}] n={len(tasks)} " +
          " ".join(f"{k} {v:.4f}" for k, v in stats.items() if isinstance(v, (int, float))),
          flush=True)
    for r in rolls[:4]:
        print("   gold:", str(r.task.gold)[:40], "| ans:", str(r.info.get("answer"))[:60], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
