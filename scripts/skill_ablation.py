"""Does the model actually use the textbook it is given?

Runs one checkpoint over the same held-out invented systems under three
conditions: the real textbook retrievable, a different system's textbook
retrievable, and nothing retrievable. A model that has genuinely learned
inference-time skill acquisition scores well only in the first condition.
A model that memorized or guesses scores the same everywhere.
"""

from __future__ import annotations

import argparse
import json
import random

import torch
import yaml

from src.evals.mc import load_checkpoint_model
from src.rl.cli import run_eval
from src.rl.env import EnvConfig, EpisodeEnv, load_tasks
from src.skillacq.episodes import to_rl_episode
from src.skillacq.systems import generate_episode
from src.train.tokenizer import load_tokenizer


def write_conditions(base_dir: str, seeds: range, n_problems: int) -> dict:
    """Three episode files that differ only in which documents are available."""
    paths = {
        "textbook": f"{base_dir}/eval_textbook.jsonl",
        "wrong_textbook": f"{base_dir}/eval_wrong.jsonl",
        "no_textbook": f"{base_dir}/eval_none.jsonl",
    }
    handles = {k: open(v, "w") for k, v in paths.items()}
    rng = random.Random(12345)
    for s in seeds:
        ep = generate_episode(s, n_problems=n_problems)
        rec = to_rl_episode(ep, n_context=0)
        handles["textbook"].write(json.dumps(rec) + "\n")

        other = generate_episode(s + 500000, n_problems=n_problems)
        wrong = dict(rec)
        wrong["documents"] = [{"text": p} for p in other.textbook]
        handles["wrong_textbook"].write(json.dumps(wrong) + "\n")

        none = dict(rec)
        none["documents"] = []
        handles["no_textbook"].write(json.dumps(none) + "\n")
    for h in handles.values():
        h.close()
    return paths


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--config", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--eval-start", type=int, default=900000)
    ap.add_argument("--eval-count", type=int, default=300)
    ap.add_argument("--n-problems", type=int, default=6)
    args = ap.parse_args()

    with open(args.config) as fh:
        cfg = yaml.safe_load(fh)
    env_cfg = EnvConfig(**cfg.get("env", {}))
    task_cfg = cfg.get("tasks", {})
    max_len = int(cfg.get("env", {}).get("max_len", 2048))

    tok = load_tokenizer(args.tokenizer)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, _ = load_checkpoint_model(args.checkpoint, device)

    paths = write_conditions(args.out, range(args.eval_start, args.eval_start + args.eval_count),
                             args.n_problems)
    env = EpisodeEnv(tok, env_cfg)
    results = {}
    for name, path in paths.items():
        tasks = load_tasks(path, tok,
                           questions_per_episode=int(task_cfg.get("questions_per_episode", 2)),
                           min_hops=int(task_cfg.get("min_hops", 1)),
                           max_prompt_tokens=int(task_cfg.get("max_prompt_tokens", 1024)),
                           limit_episodes=None,
                           seed=0)
        stats, _ = run_eval(env, model, device, tasks, max_len, batch_size=32)
        results[name] = {"n_tasks": len(tasks), **stats}
        print(f"[{name}] n={len(tasks)} " +
              " ".join(f"{k} {v:.4f}" for k, v in stats.items()
                       if isinstance(v, (int, float))), flush=True)

    with open(f"{args.out}/ablation.json", "w") as fh:
        json.dump({"checkpoint": args.checkpoint, "conditions": results}, fh, indent=2)
    t = results["textbook"].get("accuracy", 0.0)
    w = results["wrong_textbook"].get("accuracy", 0.0)
    n = results["no_textbook"].get("accuracy", 0.0)
    print(f"SKILL_ABLATION textbook {t:.4f} wrong {w:.4f} none {n:.4f} "
          f"lift_over_none {t - n:+.4f} lift_over_wrong {t - w:+.4f}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
