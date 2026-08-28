"""Three-condition evidence ablation for one checkpoint.

Fifty-three of this project's fifty-five recorded runs carry an accuracy
nobody has asked the only question that matters about it: did the evidence
the model retrieved produce the answer, or would any page have done? This
script answers that for one checkpoint, on the evaluation family the
checkpoint was trained for.

Three conditions over identical questions. Only the evidence changes.

    correct   the episode's own documents
    wrong     a different episode's (or a different invented system's)
              documents: as many pages, as long, as retrievable
    blank     pages that say they are blank

Four of the five suites keep n_context at zero, so every fact arrives through
the retriever and the prompt is byte-identical across the three conditions.
The web suite is the exception: scrubbed-web episodes carry a document prefix
in the prompt and were trained that way, so the prefix is swapped along with
the retrievable pages rather than removed.

The blank condition uses a real page rather than an empty document list on
purpose. An empty list makes make_service return None, the rollout never
gets a retriever, and the resulting zero says nothing about the model.
scripts/skill_ablation.py has that bug; scripts/skill_rule_test.py does not.

Decoding is sampled, not greedy, at one sample per item with a fixed seed
shared across the three conditions, so the comparison is paired. Greedy
decode has produced false zeros on this project before: a policy can carry a
behaviour without it being the argmax.

Two protocols, because the project's runs were never graded under one.

    gen   the RL environment's own rollout: the policy emits <|retrieve|>,
          writes a query, reads the served chunk and writes a free-form
          answer, graded by the naturalized normalizer. This is what every
          RL run's logged accuracy means.
    mc    the eval battery's held-out worlds: documents packed into the
          context, the true answer scored against distractors by likelihood.
          This is what every pretraining run's logged accuracy means, and a
          pretrained checkpoint that never learned the emit-query-read
          protocol scores a flat zero under gen whatever its documents say.

Running only gen would have written twenty-odd rows of 0.000/0.000/0.000 and
called them measurements. Both protocols run on every worldgen checkpoint;
mc needs a per-domain distractor pool and a world, so it is worldgen only.

Two numbers come out of each, both defined in src/registry/schema.py:

    retrieval_dependency = acc(correct) - acc(wrong)   the strict test
    evidence_lift        = acc(correct) - acc(blank)   the weak test

Everything is reported per family as well as pooled. Pooling once hid a
subtask whose answers were copyable straight out of the question, so every
item is also flagged for copyability and a copyable-excluded accuracy is
reported next to the raw one.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

import torch
import yaml

from src.evals.heldout import run_heldout
from src.evals.mc import load_checkpoint_model
from src.registry.flops import compute_params, param_counts_from_config
from src.rl.env import EnvConfig, EpisodeEnv, load_tasks, rollout_stats
from src.rl.sampler import CachedPolicy
from src.skillacq.episodes import to_rl_episode
from src.skillacq.procedures import PROCEDURE_FAMILIES, build_procedure_episode
from src.skillacq.simple import SIMPLE_FAMILIES
from src.skillacq.systems import FAMILIES as ARITH_FAMILIES
from src.skillacq.systems import generate_episode
from src.train.tokenizer import load_tokenizer

BLANK_PAGE = "This page is intentionally blank."

# The suite a checkpoint is graded on is the family it was trained for.
# Grading an arithmetic policy on rule application, or a pretrained model on
# invented systems it never met, measures the transfer question rather than
# this one.
SUITES = ("worldgen", "web", "simple", "arith", "procfmt")

# Suites whose episodes come from a file rather than a generator.
FILE_SUITES = ("worldgen", "web")


# ---------------------------------------------------------------------------
# building the three conditions
# ---------------------------------------------------------------------------

def _invented_episodes(suite: str, start: int, count: int,
                       n_problems: int) -> list[dict]:
    """Correct-condition episodes for one of the invented-system suites."""
    if suite == "simple":
        fams = sorted(SIMPLE_FAMILIES)
    elif suite == "arith":
        fams = sorted(ARITH_FAMILIES)
    elif suite == "procfmt":
        fams = sorted(PROCEDURE_FAMILIES)
    else:
        raise ValueError(suite)

    out = []
    for i in range(count):
        seed = start + i
        fam = fams[i % len(fams)]
        if suite == "procfmt":
            rec = build_procedure_episode(seed, family=fam,
                                          n_problems=n_problems)
        else:
            ep = generate_episode(seed, family=fam, n_problems=n_problems)
            rec = to_rl_episode(ep, n_context=0)
        rec["_family"] = fam
        rec["_seed"] = seed
        out.append(rec)
    return out


def _wrong_documents(suite: str, rec: dict, i: int, start: int,
                     n_problems: int, pool: list[dict]) -> list[dict]:
    """Documents for the wrong-evidence condition.

    For the invented suites this is a different system from a different
    family, freshly generated far away in seed space, so no page in it can
    bear on the question. For worldgen it is another held-out episode's
    document set, which is the same shape of evidence about a different
    world.
    """
    if suite in FILE_SUITES:
        other = pool[(i + len(pool) // 2 + 1) % len(pool)]
        if other is rec:
            other = pool[(i + 1) % len(pool)]
        return list(other.get("documents", []))

    if suite == "simple":
        fams = sorted(SIMPLE_FAMILIES)
    elif suite == "arith":
        fams = sorted(ARITH_FAMILIES)
    else:
        fams = sorted(PROCEDURE_FAMILIES)
    other_fam = fams[(i + 1) % len(fams)]
    other_seed = start + i + 777000
    if suite == "procfmt":
        other = build_procedure_episode(other_seed, family=other_fam,
                                        n_problems=n_problems)
        return list(other.get("documents", []))
    ep = generate_episode(other_seed, family=other_fam, n_problems=n_problems)
    return [{"text": page} for page in ep.textbook]


def build_conditions(out_dir: Path, suite: str, *, start: int, count: int,
                     n_problems: int, heldout: str | None,
                     skip: int = 0) -> dict[str, str]:
    """Write one jsonl per condition. The questions are identical in all three.

    ``skip`` drops the first N lines of a file-backed suite. regime_c's
    held-out worlds are already disjoint from training, but the scrubbed-web
    episodes file is the one the web RL lane trained from, and its first few
    thousand episodes are exactly what that lane saw.
    """
    if suite in FILE_SUITES:
        if not heldout:
            raise SystemExit(f"--heldout is required for the {suite} suite")
        base = []
        with open(heldout) as fh:
            for line_no, line in enumerate(fh):
                if line_no < skip:
                    continue
                if line_no >= skip + count:
                    break
                line = line.strip()
                if line:
                    rec = json.loads(line)
                    rec["_family"] = rec.get("world", {}).get("domain", "unknown")
                    rec["_seed"] = rec.get("seed")
                    base.append(rec)
    else:
        base = _invented_episodes(suite, start, count, n_problems)

    paths = {c: str(out_dir / f"cond_{c}.jsonl")
             for c in ("correct", "wrong", "blank")}
    handles = {k: open(v, "w") for k, v in paths.items()}
    try:
        for i, rec in enumerate(base):
            clean = {k: v for k, v in rec.items() if not k.startswith("_")}
            # Scrubbed-web episodes keep a document prefix in the prompt and
            # were trained that way, so the web suite keeps it and swaps that
            # prefix along with the retrievable pages. Everywhere else every
            # fact already arrives through the retriever.
            n_context = int(clean.get("n_context", 0)) if suite == "web" else 0
            clean["n_context"] = n_context
            handles["correct"].write(json.dumps(clean) + "\n")

            wrong = dict(clean)
            wrong["documents"] = _wrong_documents(suite, rec, i, start,
                                                  n_problems, base)
            handles["wrong"].write(json.dumps(wrong) + "\n")

            blank = dict(clean)
            # Enough blank pages that the in-context prefix keeps its shape
            # and one is still left for the retriever to serve.
            blank["documents"] = [{"text": BLANK_PAGE}] * max(1, n_context + 1)
            handles["blank"].write(json.dumps(blank) + "\n")
    finally:
        for h in handles.values():
            h.close()
    return paths


# ---------------------------------------------------------------------------
# splits
# ---------------------------------------------------------------------------

def _load_episodes(path: str, limit: int) -> list[dict]:
    """Read back a condition file as plain episode dicts, for the mc path."""
    out = []
    with open(path) as fh:
        for i, line in enumerate(fh):
            if i >= limit:
                break
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def _copyable(answer: str, question: str) -> bool:
    """True when the gold answer stands alone inside the question text.

    The arithmetic ablation's procedure family scored 0.467 on answers that
    were copied out of the question, and the pooled number hid it. Any item
    that can be answered by echoing is reported separately here.
    """
    if not answer:
        return False
    return re.search(rf"(?<![\w.]){re.escape(str(answer))}(?![\w.])",
                     str(question)) is not None


def _split_stats(rolls) -> dict:
    """Accuracy and its parts for one group of rollouts."""
    if not rolls:
        return {}
    stats = rollout_stats(rolls)
    hard = [r for r in rolls if not _copyable(r.task.gold, r.task.question)]
    stats["n_copyable"] = len(rolls) - len(hard)
    stats["accuracy_noncopyable"] = (
        float(sum(r.correct for r in hard)) / len(hard) if hard else None)
    return stats


def _by_family(rolls) -> dict:
    groups: dict[str, list] = {}
    for r in rolls:
        groups.setdefault(r.task.domain, []).append(r)
    return {k: _split_stats(v) for k, v in sorted(groups.items())}


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--suite", required=True, choices=SUITES)
    ap.add_argument("--config", required=True,
                    help="config supplying the env and tasks blocks")
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--heldout", default=None,
                    help="episodes jsonl for the file-backed suites: held-out "
                         "worlds for worldgen, scrubbed web for web")
    ap.add_argument("--skip", type=int, default=0,
                    help="drop the first N episodes of a file-backed suite, "
                         "to stay clear of what the run trained on")
    ap.add_argument("--max-prompt-tokens", type=int, default=None,
                    help="override the config; web prompts carry a document "
                         "prefix and do not fit the default")
    ap.add_argument("--start", type=int, default=4100000)
    ap.add_argument("--count", type=int, default=250,
                    help="episodes per condition")
    ap.add_argument("--n-problems", type=int, default=6)
    ap.add_argument("--temperature", type=float, default=0.8)
    ap.add_argument("--top-k", type=int, default=0)
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--protocols", default="gen",
                    help="comma separated: gen, mc (mc is worldgen only)")
    ap.add_argument("--mc-count", type=int, default=None,
                    help="episodes for the mc protocol, defaults to --count")
    ap.add_argument("--mc-retrieval", action="store_true",
                    help="mc reaches the documents through the interactive "
                         "loop instead of packing them into the context")
    ap.add_argument("--primary", default=None, choices=["gen", "mc"],
                    help="which protocol the registry row quotes; defaults to "
                         "gen when it was run")
    args = ap.parse_args()
    protocols = [p.strip() for p in args.protocols.split(",") if p.strip()]
    for p in protocols:
        if p not in ("gen", "mc"):
            raise SystemExit(f"unknown protocol {p!r}")
    if "mc" in protocols and args.suite != "worldgen":
        raise SystemExit("the mc protocol needs a world and a distractor pool; "
                         "it is worldgen only")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(args.config) as fh:
        cfg = yaml.safe_load(fh)
    env_cfg = EnvConfig(**cfg.get("env", {}))
    task_cfg = cfg.get("tasks", {})

    max_prompt_tokens = int(args.max_prompt_tokens
                            or task_cfg.get("max_prompt_tokens", 1024))

    tok = load_tokenizer(args.tokenizer)
    device = args.device if torch.cuda.is_available() else "cpu"
    model, state = load_checkpoint_model(args.checkpoint, device)
    model.eval()

    model_cfg = state["config"]["model"]
    counts = param_counts_from_config(model_cfg)
    p_eff = compute_params(counts["params_non_embedding"], model_cfg)

    # The rollout cache cannot outrun the model's own context window.
    max_len = min(int(env_cfg.max_len), int(model.cfg.max_seq_len))
    env_cfg.max_len = max_len
    env = EpisodeEnv(tok, env_cfg)

    paths = build_conditions(out_dir, args.suite, start=args.start,
                             count=args.count, n_problems=args.n_problems,
                             heldout=args.heldout, skip=args.skip)

    conditions: dict[str, dict] = {}
    per_family: dict[str, dict] = {}
    n_tasks_seen = None
    for name in ("correct", "wrong", "blank") if "gen" in protocols else ():
        t0 = time.monotonic()
        tasks = load_tasks(
            paths[name], tok,
            questions_per_episode=int(task_cfg.get("questions_per_episode", 2)),
            min_hops=int(task_cfg.get("min_hops", 1)),
            max_prompt_tokens=max_prompt_tokens,
            limit_episodes=None, seed=0)
        if n_tasks_seen is None:
            n_tasks_seen = len(tasks)
        elif len(tasks) != n_tasks_seen:
            raise SystemExit(
                f"condition {name} has {len(tasks)} tasks, "
                f"correct had {n_tasks_seen}; the items are not identical")
        # One policy per condition, same seed: paired sampling.
        policy = CachedPolicy(model, device, max_len=max_len,
                              temperature=args.temperature, top_k=args.top_k,
                              seed=args.seed)
        rolls = []
        for i in range(0, len(tasks), args.batch):
            rolls.extend(env.rollout(policy, tasks[i:i + args.batch]))
        stats = _split_stats(rolls)
        stats["wall_clock_s"] = round(time.monotonic() - t0, 1)
        stats["n_tasks"] = len(tasks)
        conditions[name] = stats
        per_family[name] = _by_family(rolls)
        print(f"[{args.run_id} {name}] n={len(tasks)} "
              f"acc {stats['accuracy']:.4f} "
              f"acc_noncopy {stats.get('accuracy_noncopyable')} "
              f"any_retrieval {stats['any_retrieval']:.3f} "
              f"gen {stats['mean_generated']:.1f} "
              f"{stats['wall_clock_s']}s", flush=True)
        if name == "correct":
            with open(out_dir / "samples_correct.jsonl", "w") as fh:
                for r in rolls[:24]:
                    fh.write(json.dumps(env.transcript(r)) + "\n")

    mc: dict[str, dict] = {}
    if "mc" in protocols:
        mc_count = args.mc_count or args.count
        for name in ("correct", "wrong", "blank"):
            t0 = time.monotonic()
            episodes = _load_episodes(paths[name], mc_count)
            result = run_heldout(
                model, tok, episodes, device, seed=args.seed,
                use_retrieval=args.mc_retrieval,
                max_rounds=int(env_cfg.max_rounds),
                max_new_tokens=int(env_cfg.max_new_tokens))
            result["wall_clock_s"] = round(time.monotonic() - t0, 1)
            mc[name] = result
            print(f"[{args.run_id} mc/{name}] n={result['n_questions']} "
                  f"acc {result['accuracy']:.4f} chance {result['chance']:.3f} "
                  f"{result['wall_clock_s']}s", flush=True)
        n_mc = {mc[k]["n_questions"] for k in mc}
        if len(n_mc) != 1:
            raise SystemExit(f"mc conditions disagree on item count: {n_mc}")

    def _triple(block: dict, key: str = "accuracy") -> tuple:
        return (block["correct"][key], block["wrong"][key], block["blank"][key])

    protocol_metrics = {}
    if conditions:
        c, w, b = _triple(conditions)
        protocol_metrics["gen"] = {
            "acc_correct_evidence": c, "acc_wrong_evidence": w,
            "acc_no_evidence": b,
            "retrieval_dependency": c - w, "evidence_lift": c - b,
            "n_items": n_tasks_seen,
        }
    if mc:
        c, w, b = _triple(mc)
        protocol_metrics["mc"] = {
            "acc_correct_evidence": c, "acc_wrong_evidence": w,
            "acc_no_evidence": b,
            "retrieval_dependency": c - w, "evidence_lift": c - b,
            "n_items": mc["correct"]["n_questions"],
            "chance": mc["correct"]["chance"],
            "mc_retrieval": bool(args.mc_retrieval),
        }

    # Which protocol the registry row takes its number from. A run is graded
    # under the protocol its logged accuracy already used, or the comparison
    # to that accuracy means nothing.
    primary = args.primary or ("gen" if "gen" in protocol_metrics else "mc")
    if primary not in protocol_metrics:
        raise SystemExit(f"primary protocol {primary} was not run")
    head = protocol_metrics[primary]
    acc_c = head["acc_correct_evidence"]
    acc_w = head["acc_wrong_evidence"]
    acc_b = head["acc_no_evidence"]
    gen = (conditions["correct"]["mean_generated"] if conditions
           else float(env_cfg.max_new_tokens))

    blob = {
        "run_id": args.run_id,
        "checkpoint": args.checkpoint,
        "suite": args.suite,
        "protocols": protocols,
        "primary_protocol": primary,
        "temperature": args.temperature,
        "seed": args.seed,
        "n_tasks": head["n_items"],
        # The names read_ablation already understands, so the existing
        # ingester can read this file too.
        "conditions": {
            "correct": conditions.get("correct") or mc["correct"],
            "wrong_textbook": conditions.get("wrong") or mc["wrong"],
            "no_documents": conditions.get("blank") or mc["blank"],
        },
        "gen_conditions": conditions,
        "mc_conditions": mc,
        "protocol_metrics": protocol_metrics,
        "per_family": per_family or {k: v.get("per_domain") for k, v in mc.items()},
        "metrics": {
            "acc_correct_evidence": acc_c,
            "acc_wrong_evidence": acc_w,
            "acc_no_evidence": acc_b,
            "retrieval_dependency": acc_c - acc_w,
            "evidence_lift": acc_c - acc_b,
        },
        "arch": {
            "params_total": counts["params_total"],
            "params_non_embedding": counts["params_non_embedding"],
            "d_model": int(model_cfg["d_model"]),
            "n_layers": int(model_cfg["n_layers"]),
            "n_heads": int(model_cfg.get("n_heads") or 0) or None,
            "d_ff": int(model_cfg["d_ff"]),
            "vocab_size": int(model_cfg["vocab_size"]),
            "max_seq_len": int(model_cfg["max_seq_len"]),
        },
        "compute": {
            "decode_flops_per_answer": 2.0 * p_eff * gen,
            "params_effective_non_embedding": p_eff,
            "mean_generated_tokens": gen,
        },
        "env": env_cfg.to_dict(),
        "tasks_cfg": {**dict(task_cfg), "max_prompt_tokens": max_prompt_tokens},
        "episodes_source": args.heldout,
        "episodes_skip": args.skip,
        "step": state.get("step"),
    }
    dest = out_dir / "dependency.json"
    with open(dest, "w") as fh:
        json.dump(blob, fh, indent=2)
    print(f"DEPENDENCY {args.run_id} suite {args.suite} via {primary} "
          f"correct {acc_c:.4f} wrong {acc_w:.4f} blank {acc_b:.4f} "
          f"dependency {acc_c - acc_w:+.4f} lift {acc_c - acc_b:+.4f} "
          f"decodeFLOPs {2.0 * p_eff * gen:.3g} -> {dest}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
