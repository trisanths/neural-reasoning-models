"""Command line entry point for RL against the verifiers.

Example:

    uv run python -m src.rl.cli \
        --init-checkpoint runs/curve-350me-503/latest.pt \
        --config configs/rl-350m.yaml \
        --episodes-jsonl data/regime_c/heldout.jsonl \
        --tokenizer data/tokenizer_v2.json \
        --out runs/rl-350m-001

The initial policy is a pretrained checkpoint; a frozen copy of it is the
KL reference. Each optimization step samples prompts_per_step questions,
writes group_size trajectories for each, scores them with the environment's
verifier, and takes one GRPO step on the policy-emitted tokens.

The run directory collects rl.jsonl (one record per step: reward mean,
accuracy, mean rounds, query length, KL, entropy, clip fraction, throughput),
samples-STEP.jsonl (full rollout transcripts for reading), eval.jsonl (greedy
held-out passes, including one before the first update), and checkpoints.
Resuming reads latest.pt from the run directory and continues the step count.
"""

import argparse
import json
import random
import time
from pathlib import Path

import numpy as np
import torch
import yaml

from src.evals.mc import load_checkpoint_model
from src.rl.env import EnvConfig, EpisodeEnv, load_tasks, make_service, rollout_stats
from src.rl.grpo import GRPOConfig, GRPOTrainer, group_advantages
from src.rl.sampler import CachedPolicy
from src.train.model import ModelConfig, TransformerLM
from src.train.tokenizer import load_tokenizer


def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m src.rl.cli")
    p.add_argument("--init-checkpoint", required=True,
                   help="pretrained checkpoint that seeds policy and reference")
    p.add_argument("--config", required=True, help="rl yaml config")
    p.add_argument("--episodes-jsonl", required=True,
                   help="worldgen or scrubbed-web episodes")
    p.add_argument("--out", required=True, help="run directory")
    p.add_argument("--tokenizer", required=True, help="tokenizer.json")
    p.add_argument("--eval-episodes-jsonl", default=None,
                   help="episodes for the greedy eval passes, default the "
                        "training file's held-out tail")
    p.add_argument("--steps", type=int, default=None,
                   help="override grpo.max_steps")
    p.add_argument("--resume", action="store_true",
                   help="continue from OUT/latest.pt")
    p.add_argument("--device", default=None)
    p.add_argument("--seed", type=int, default=None)
    return p


def _split_tasks(tasks, n_eval: int, seed: int):
    """Hold out the last n_eval tasks by episode, never by question, so an
    episode never straddles the split."""
    if n_eval <= 0:
        return tasks, []
    episodes = sorted({t.episode_index for t in tasks})
    rng = random.Random(seed)
    rng.shuffle(episodes)
    eval_eps: set[int] = set()
    count = 0
    for ep in episodes:
        if count >= n_eval:
            break
        eval_eps.add(ep)
        count += sum(1 for t in tasks if t.episode_index == ep)
    train = [t for t in tasks if t.episode_index not in eval_eps]
    held = [t for t in tasks if t.episode_index in eval_eps]
    return train, held


def run_eval(env, model, device, tasks, max_len, batch_size: int) -> dict:
    """Greedy pass over held-out tasks: what the policy does with no noise."""
    rolls = []
    model.eval()
    policy = CachedPolicy(model, device, max_len=max_len, temperature=0.0)
    for start in range(0, len(tasks), batch_size):
        chunk = tasks[start:start + batch_size]
        rolls.extend(env.rollout(policy, chunk))
    return rollout_stats(rolls), rolls


def main(argv=None) -> int:
    args = build_argparser().parse_args(argv)
    with open(args.config) as fh:
        cfg = yaml.safe_load(fh)
    env_cfg = EnvConfig(**cfg.get("env", {}))
    grpo_cfg = GRPOConfig(**cfg.get("grpo", {}))
    task_cfg = cfg.get("tasks", {})
    run_cfg = cfg.get("run", {})
    if args.steps is not None:
        grpo_cfg.max_steps = args.steps
    if args.seed is not None:
        grpo_cfg.seed = args.seed

    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    torch.manual_seed(grpo_cfg.seed)
    np.random.seed(grpo_cfg.seed % (1 << 32))

    tokenizer = load_tokenizer(args.tokenizer)
    model, state = load_checkpoint_model(args.init_checkpoint, device)
    model_config = state["config"]
    ref_model = TransformerLM(ModelConfig(**model_config["model"]))
    ref_model.load_state_dict(state["model"])
    print(f"policy from {args.init_checkpoint} at pretrain step "
          f"{state.get('step', -1)}, device {device}")

    env = EpisodeEnv(tokenizer, env_cfg)
    tasks = load_tasks(args.episodes_jsonl, tokenizer,
                       limit_episodes=task_cfg.get("limit_episodes"),
                       questions_per_episode=task_cfg.get("questions_per_episode", 2),
                       min_hops=task_cfg.get("min_hops", 1),
                       max_prompt_tokens=task_cfg.get("max_prompt_tokens", 384),
                       seed=grpo_cfg.seed)
    n_eval = int(run_cfg.get("eval_tasks", 96))
    if args.eval_episodes_jsonl:
        train_tasks = tasks
        eval_tasks = load_tasks(args.eval_episodes_jsonl, tokenizer,
                                limit_episodes=task_cfg.get("eval_limit_episodes"),
                                questions_per_episode=1,
                                min_hops=task_cfg.get("min_hops", 1),
                                max_prompt_tokens=task_cfg.get("max_prompt_tokens", 384),
                                seed=grpo_cfg.seed + 1)[:n_eval]
    else:
        train_tasks, eval_tasks = _split_tasks(tasks, n_eval, grpo_cfg.seed)
        eval_tasks = eval_tasks[:n_eval]
    if not train_tasks:
        raise SystemExit("no training tasks after filtering")
    print(f"{len(train_tasks)} train tasks, {len(eval_tasks)} eval tasks")

    trainer = GRPOTrainer(model, grpo_cfg, args.out, device=device,
                          ref_model=ref_model)
    if args.resume:
        latest = out_dir / "latest.pt"
        if latest.exists():
            trainer.load_checkpoint(latest)
            print(f"resumed at rl step {trainer.step}")

    log_path = out_dir / "rl.jsonl"
    eval_path = out_dir / "eval.jsonl"
    eval_every = int(run_cfg.get("eval_every", 100))
    sample_every = int(run_cfg.get("sample_every", 25))
    sample_n = int(run_cfg.get("sample_n", 4))
    ckpt_every = int(run_cfg.get("ckpt_every", 100))
    log_every = int(run_cfg.get("log_every", 1))
    eval_batch = int(run_cfg.get("eval_batch", 32))

    def log(path, record):
        with open(path, "a") as fh:
            fh.write(json.dumps(record) + "\n")

    def do_eval(tag: str):
        if not eval_tasks:
            return None
        t0 = time.time()
        stats, rolls = run_eval(env, trainer.model, device, eval_tasks,
                                env_cfg.max_len, eval_batch)
        stats.update({"step": trainer.step, "tag": tag,
                      "elapsed_s": round(time.time() - t0, 2)})
        log(eval_path, stats)
        with open(out_dir / f"eval-samples-{tag}.jsonl", "w") as fh:
            for r in rolls[:sample_n]:
                fh.write(json.dumps(env.transcript(r)) + "\n")
        print(f"[eval {tag}] accuracy {stats['accuracy']:.4f} "
              f"reward {stats['reward_mean']:.4f} "
              f"rounds {stats['mean_rounds']:.3f} "
              f"qlen {stats['mean_query_len']:.2f} "
              f"({stats['elapsed_s']}s)")
        return stats

    if eval_every > 0 and trainer.step == 0:
        do_eval("before")

    rng = random.Random(grpo_cfg.seed + 7)
    policy = CachedPolicy(model, device, max_len=env_cfg.max_len,
                          temperature=float(run_cfg.get("temperature", 1.0)),
                          top_k=int(run_cfg.get("top_k", 0)),
                          seed=grpo_cfg.seed)
    g = grpo_cfg.group_size
    started = time.time()
    rollouts_done = 0
    iterations = 0
    # A step that finds no reward spread anywhere takes no gradient, so the
    # step counter does not move. The iteration cap keeps such a run from
    # spinning forever on a policy that scores identically everywhere.
    max_iterations = int(run_cfg.get("max_iteration_factor", 6)) * grpo_cfg.max_steps
    while trainer.step < grpo_cfg.max_steps and iterations < max_iterations:
        iterations += 1
        step_t0 = time.time()
        picked = [train_tasks[rng.randrange(len(train_tasks))]
                  for _ in range(grpo_cfg.prompts_per_step)]
        batch_tasks = [t for t in picked for _ in range(g)]
        services = [make_service(t.documents) for t in batch_tasks]
        model.eval()
        rolls = env.rollout(policy, batch_tasks, services)
        gen_s = time.time() - step_t0
        rollouts_done += len(rolls)

        rewards = [r.reward for r in rolls]
        adv = group_advantages(rewards, g, eps=grpo_cfg.adv_eps,
                               normalize=grpo_cfg.normalize_advantage)
        upd_t0 = time.time()
        upd = trainer.update(rolls, adv)
        upd_s = time.time() - upd_t0

        record = {"step": trainer.step, "rollout_s": round(gen_s, 3),
                  "update_s": round(upd_s, 3),
                  "rollouts_per_s": round(len(rolls) / max(gen_s, 1e-9), 3),
                  "elapsed_s": round(time.time() - started, 1)}
        record.update(rollout_stats(rolls))
        record.update({k: v for k, v in upd.items() if k != "skipped"})
        if trainer.step % log_every == 0 or trainer.step == grpo_cfg.max_steps:
            log(log_path, record)
        if trainer.step % max(1, log_every) == 0:
            print(f"step {record['step']:5d} r {record['reward_mean']:.3f} "
                  f"acc {record['accuracy']:.3f} rounds {record['mean_rounds']:.2f} "
                  f"qlen {record['mean_query_len']:.1f} "
                  f"kl {record.get('kl', 0.0):.5f} "
                  f"gen {gen_s:.1f}s upd {upd_s:.1f}s")
        if sample_every > 0 and trainer.step % sample_every == 0:
            with open(out_dir / f"samples-{trainer.step:06d}.jsonl", "w") as fh:
                for r in rolls[:sample_n]:
                    fh.write(json.dumps(env.transcript(r)) + "\n")
        if ckpt_every > 0 and trainer.step % ckpt_every == 0:
            trainer.save_checkpoint(model_config)
        if eval_every > 0 and trainer.step % eval_every == 0:
            do_eval(f"step{trainer.step:06d}")

    trainer.save_checkpoint(model_config, name="final.pt")
    if eval_every > 0:
        do_eval("after")
    total = time.time() - started
    print(f"done: {trainer.step} steps, {rollouts_done} rollouts, "
          f"{total / 3600:.3f} h, "
          f"{trainer.step / max(total / 3600, 1e-9):.1f} steps per hour")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
