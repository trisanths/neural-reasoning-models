"""Evaluate one checkpoint on the skillacq gate families and on mathgen universes.

One code path scores everything. The suite only decides which episodes jsonl is
read; model loading, rollout, the retrieval service, the grader and the metric
aggregation are shared, which is what makes the gate a gate. Running

    --suite gate

reproduces the recorded control numbers for `substitution_rule` and
`threshold_rule`; if those do not come back, no other number from this file
means anything.

Decoding is reported twice, always. Greedy is one sample per question.
Sampled is temperature 1.0 with --samples rollouts per question, reported as
pass@1 (the mean over every rollout) and pass@k (the fraction of questions with
at least one correct rollout). Greedy-only evaluation has produced false zeros
on this project, because a policy can carry behaviour without it being the
argmax.

Every row is written to a per-rollout jsonl. Aggregation is a separate pass over
that file, and it never groups across `answer_source`.
"""

from __future__ import annotations

import argparse
import json
import os
import time

import torch
import yaml

from src.evals.mc import load_checkpoint_model
from src.evals.naturalized import exact_match, normalize
from src.rl.env import EnvConfig, EpisodeEnv, load_tasks
from src.rl.sampler import CachedPolicy
from src.train.tokenizer import load_tokenizer

GATE_FAMILIES = ("substitution_rule", "threshold_rule")
GATE_TARGETS = {
    ("substitution_rule", "greedy"): 0.969,
    ("substitution_rule", "t1"): 0.828,
    ("threshold_rule", "greedy"): 1.000,
    ("threshold_rule", "t1"): 0.922,
}


# ---------------------------------------------------------------- episodes

def build_gate_episodes(out_dir: str, start: int, count: int,
                        n_problems: int) -> dict:
    """Skillacq simple-rule episodes, one family per file, retrieval only."""
    from src.skillacq.episodes import to_rl_episode
    from src.skillacq.systems import generate_episode

    os.makedirs(out_dir, exist_ok=True)
    paths = {}
    for family in GATE_FAMILIES:
        path = os.path.join(out_dir, f"ep_{family}.jsonl")
        with open(path, "w", encoding="utf-8") as fh:
            for seed in range(start, start + count):
                ep = generate_episode(seed, family=family, n_problems=n_problems)
                fh.write(json.dumps(to_rl_episode(ep, n_context=0)) + "\n")
        paths[family] = path
    return paths


# ------------------------------------------------------------------ rollout

def run_cell(env: EpisodeEnv, model, device, tasks, temperature: float,
             samples: int, seed: int, batch: int, policy_max_len: int):
    """`samples` rollouts per task, batched, one policy for the whole cell."""
    replicated = []
    for t in tasks:
        for k in range(samples):
            replicated.append((t, k))
    # Similar prompt lengths in one batch keep the left padding small; the
    # sampler's cache position is shared across the batch either way.
    replicated.sort(key=lambda pair: len(pair[0].prompt))
    policy = CachedPolicy(model, device, max_len=policy_max_len,
                          temperature=temperature, top_k=0, seed=seed)
    out = []
    for i in range(0, len(replicated), batch):
        window = replicated[i:i + batch]
        rolls = env.rollout(policy, [t for t, _ in window])
        for (task, k), roll in zip(window, rolls):
            out.append((task, k, roll))
    return out


def record(env: EpisodeEnv, suite: str, condition: str, decode: str,
           task, sample_index: int, roll, meta: dict, doc_index: dict) -> dict:
    """One rollout, with every diagnostic this project asks to see beside it."""
    served = []
    for r in roll.rounds:
        info = doc_index.get((task.episode_index, int(r["doc_index"])), {})
        served.append({"chunk_id": info.get("chunk_id", ""),
                       "chapter": info.get("chapter"),
                       "section_kind": info.get("section_kind", ""),
                       "query": r["query"]})
    served_text = normalize(" ".join(r["chunk"] for r in roll.rounds))
    gold_norm = normalize(task.gold)
    required = set(meta.get("required_chapters") or [])
    got_chapters = {s["chapter"] for s in served if s["chapter"] is not None}
    queries = [normalize(r["query"]) for r in roll.rounds]
    return {
        "suite": suite,
        "condition": condition,
        "decode": decode,
        "sample_index": sample_index,
        "episode_index": task.episode_index,
        "qid": task.qid,
        "seed": meta.get("seed"),
        "level": meta.get("level"),
        "answer_source": meta.get("answer_source"),
        "recipe_kind": meta.get("recipe_kind"),
        "answer_kind": meta.get("answer_kind"),
        "carrier_size": meta.get("carrier_size"),
        "question": task.question,
        "gold": task.gold,
        "prediction": roll.answer_text,
        "correct": bool(roll.correct),
        "strict_em": bool(exact_match(roll.answer_text, task.gold)),
        "n_rounds": roll.n_rounds,
        "any_retrieval": roll.n_rounds >= 1,
        "well_formed": bool(roll.info.get("well_formed", False)),
        "degenerate_queries": int(roll.info.get("degenerate_queries", 0)),
        "mean_query_len": (sum(roll.info.get("query_lens", [])) /
                           max(1, len(roll.info.get("query_lens", [])))),
        "stop_reason": roll.stop_reason,
        "n_generated": roll.n_generated,
        "pred_tokens": len(normalize(roll.answer_text).split()),
        "gold_tokens": len(gold_norm.split()),
        "retrieved_required_chapter": bool(required and (got_chapters & required)),
        "answer_in_retrieved": bool(gold_norm) and gold_norm in served_text,
        "served": served,
        "queries": queries,
    }


def doc_index_for(path: str) -> dict:
    """(episode line, document position) -> chunk metadata, for the trace."""
    index = {}
    with open(path, encoding="utf-8") as fh:
        for line_no, line in enumerate(fh):
            if not line.strip():
                continue
            for j, doc in enumerate(json.loads(line).get("documents", [])):
                if isinstance(doc, dict):
                    index[(line_no, j)] = doc
    return index


def library_answer_availability(path: str, meta: dict) -> dict:
    """Per question, whether its gold answer appears anywhere in served pages.

    This is the copy-availability audit. A `stated_in_a_chapter` exercise is
    answerable by copying out of some page; a `derived_by_computation` one is
    not, and if that separation does not show up here the label is not doing
    what it claims.
    """
    out = {}
    with open(path, encoding="utf-8") as fh:
        for line_no, line in enumerate(fh):
            if not line.strip():
                continue
            ep = json.loads(line)
            blob = normalize(" ".join(d["text"] for d in ep.get("documents", [])))
            for q in ep.get("questions", []):
                gold = normalize(q["answer"])
                out[f"{line_no}:{q['qid']}"] = bool(gold) and gold in blob
    return out


# ---------------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--config", required=True, help="yaml holding env: and tasks:")
    ap.add_argument("--suite", choices=["gate", "mathgen"], required=True)
    ap.add_argument("--episodes-dir", required=True)
    ap.add_argument("--out", required=True, help="per-rollout jsonl")
    ap.add_argument("--samples", type=int, default=4)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--limit-questions", type=int, default=0,
                    help="0 keeps every question")
    ap.add_argument("--conditions", default="", help="comma list; default all")
    ap.add_argument("--skip-greedy", action="store_true")
    ap.add_argument("--skip-sampled", action="store_true")
    args = ap.parse_args()

    with open(args.config, encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    env_cfg = EnvConfig(**cfg.get("env", {}))
    task_cfg = cfg.get("tasks", {})
    policy_max_len = min(4096, int(env_cfg.max_len) + 512)

    tok = load_tokenizer(args.tokenizer)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, _ = load_checkpoint_model(args.checkpoint, device)
    model.eval()
    env = EpisodeEnv(tok, env_cfg)

    if args.suite == "gate":
        names = list(GATE_FAMILIES)
    else:
        names = [c for c in ("own", "sibling", "blank")]
    if args.conditions:
        names = [c.strip() for c in args.conditions.split(",") if c.strip()]

    started = time.time()
    n_written = 0
    with open(args.out, "w", encoding="utf-8") as sink:
        for name in names:
            path = os.path.join(args.episodes_dir, f"ep_{name}.jsonl")
            meta_path = os.path.join(args.episodes_dir, f"meta_{name}.json")
            meta_all = {}
            if os.path.exists(meta_path):
                with open(meta_path, encoding="utf-8") as fh:
                    meta_all = json.load(fh)
            tasks = load_tasks(
                path, tok,
                questions_per_episode=int(task_cfg.get("questions_per_episode", 2)),
                min_hops=int(task_cfg.get("min_hops", 1)),
                max_prompt_tokens=int(task_cfg.get("max_prompt_tokens", 384)),
                limit_episodes=None, seed=0)
            if args.limit_questions:
                tasks = tasks[:args.limit_questions]
            docs = doc_index_for(path)
            avail = library_answer_availability(path, meta_all)
            print(f"[{args.suite}/{name}] {len(tasks)} questions", flush=True)

            plan = []
            if not args.skip_greedy:
                plan.append(("greedy", 0.0, 1, args.seed))
            if not args.skip_sampled:
                plan.append(("t1", args.temperature, args.samples, args.seed + 1))
            for decode, temperature, samples, seed in plan:
                rolls = run_cell(env, model, device, tasks, temperature,
                                 samples, seed, args.batch, policy_max_len)
                n_correct = 0
                for task, k, roll in rolls:
                    key = f"{task.episode_index}:{task.qid}"
                    row = record(env, args.suite, name, decode, task, k, roll,
                                 meta_all.get(key, {}), docs)
                    row["answer_in_library"] = bool(avail.get(key, False))
                    sink.write(json.dumps(row) + "\n")
                    n_written += 1
                    n_correct += int(row["correct"])
                print(f"  {decode:<7} rollouts {len(rolls):>6} "
                      f"raw_mean_correct {n_correct / max(1, len(rolls)):.4f} "
                      f"({time.time() - started:.0f}s)", flush=True)
    print(f"wrote {n_written} rollouts to {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
