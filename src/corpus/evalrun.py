"""One decoding path for every re-measurement in this lane.

Three subcommands, all writing one json line per rollout so aggregation is a
separate pass over a file that is kept.

  gen    the episode environment of `src/rl/env.py`: the world header prompt,
         the retrieve-result loop served by the training oracle's BM25, the
         answer span. This is the path the harness gate reproduces and the
         only path this checkpoint answers on at all.
  mc     the same episodes with their pages in the prompt, candidates scored
         by summed negative log likelihood after an `<|a|>` marker. A policy
         that generates nothing usable still expresses a preference here, so
         a zero in `gen` can be told apart from a zero in what the model knows.
  plan   free continuation of a prompt that already ends in `<|a|>`, for the
         plan component, whose records carry their own prompt and target.

Greedy and sampled are both run wherever a number is reported; greedy alone
has produced false zeros on this project.
"""

from __future__ import annotations

import argparse
import json
import os
import time

import torch


def load_model(path, device):
    from src.evals.mc import load_checkpoint_model
    model, state = load_checkpoint_model(path, device)
    model.eval()
    return model, state


def generate_batch(model, tok, device, prompts, max_new, temperature, seed,
                   batch_size=32):
    """Batched decoding to <|eot|>, greedy at temperature 0."""
    from src.rl.sampler import CachedPolicy

    eot = tok.token_id("<|eot|>")
    out: list[str] = []
    for i in range(0, len(prompts), batch_size):
        window = prompts[i:i + batch_size]
        ids = [tok.encode(p) for p in window]
        width = max(len(x) for x in ids)
        cap = min(width + max_new + 2, model.cfg.max_seq_len)
        policy = CachedPolicy(model, device, max_len=cap,
                              temperature=temperature, top_k=0, seed=seed + i)
        nxt = policy.begin(ids)
        done = [False] * len(ids)
        gen: list[list[int]] = [[] for _ in ids]
        for _ in range(max_new):
            step = []
            for j, t in enumerate(nxt):
                if done[j]:
                    step.append(0)
                    continue
                if int(t) == eot:
                    done[j] = True
                    step.append(0)
                    continue
                gen[j].append(int(t))
                step.append(int(t))
            if all(done):
                break
            nxt = policy.advance(step)
        out.extend(tok.decode(g).strip() for g in gen)
    return out


# ------------------------------------------------------------------ gen


def cmd_gen(args) -> int:
    from src.rl.env import EnvConfig, EpisodeEnv, load_tasks
    from src.rl.sampler import CachedPolicy
    from src.train.tokenizer import load_tokenizer

    tok = load_tokenizer(args.tokenizer)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, _ = load_model(args.checkpoint, device)
    env_cfg = EnvConfig(max_rounds=args.max_rounds,
                        max_new_tokens=args.max_new_tokens,
                        max_len=args.max_len,
                        query_max_tokens=args.query_max_tokens)
    env = EpisodeEnv(tok, env_cfg)
    tasks = load_tasks(args.episodes, tok,
                       questions_per_episode=args.questions_per_episode,
                       min_hops=args.min_hops,
                       max_prompt_tokens=args.max_prompt_tokens,
                       limit_episodes=args.limit_episodes, seed=0)
    meta = question_meta(args.episodes)
    policy_max_len = min(model.cfg.max_seq_len, args.max_len + 512)
    replicated = [(t, k) for t in tasks for k in range(args.samples)]
    replicated.sort(key=lambda pair: len(pair[0].prompt))
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    t0 = time.time()
    n = 0
    with open(args.out, "w") as sink:
        for i in range(0, len(replicated), args.batch):
            window = replicated[i:i + args.batch]
            policy = CachedPolicy(model, device, max_len=policy_max_len,
                                  temperature=args.temperature, top_k=0,
                                  seed=args.seed + i)
            rolls = env.rollout(policy, [t for t, _ in window])
            for (task, k), roll in zip(window, rolls):
                m = meta.get(f"{task.episode_index}:{task.qid}", {})
                sink.write(json.dumps({
                    "decode": args.label, "sample_index": k,
                    "ep": task.episode_index, "qid": task.qid,
                    "question": task.question, "gold": task.gold,
                    "answer": roll.answer_text,
                    "shipped_ok": bool(roll.correct),
                    "n_rounds": roll.n_rounds,
                    "chunks": [r["chunk"] for r in roll.rounds],
                    "queries": [r["query"] for r in roll.rounds],
                    "stop_reason": roll.stop_reason,
                    "n_generated": roll.n_generated,
                    "well_formed": bool(roll.info.get("well_formed", False)),
                    **m,
                }) + "\n")
                n += 1
            if (i // args.batch) % 20 == 0:
                print(f"{n}/{len(replicated)} {time.time() - t0:.0f}s", flush=True)
    print(json.dumps({"out": args.out, "rollouts": n,
                      "seconds": round(time.time() - t0, 1)}), flush=True)
    return 0


def question_meta(path: str) -> dict:
    """Every field a question carries, keyed the way load_tasks numbers them."""
    out = {}
    with open(path) as fh:
        for line_no, line in enumerate(fh):
            if not line.strip():
                continue
            ep = json.loads(line)
            served = [d["text"] for d in ep.get("documents", [])]
            for q in ep.get("questions", []):
                d = {k: v for k, v in q.items()
                     if k not in ("text", "answer", "qid")}
                d["episode_family"] = ep.get("family")
                d["episode_frame"] = ep.get("frame")
                d["episode_seed"] = ep.get("seed")
                d["n_docs"] = len(served)
                out[f"{line_no}:{q.get('qid')}"] = d
    return out


# ------------------------------------------------------------------- mc


def cmd_mc(args) -> int:
    from src.evals.mc import score_mc
    from src.rl.env import build_prompt
    from src.train.tokenizer import load_tokenizer

    tok = load_tokenizer(args.tokenizer)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, _ = load_model(args.checkpoint, device)
    sid = tok.special_ids
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    t0 = time.time()
    n = 0
    with open(args.out, "w") as sink, open(args.episodes) as fh:
        for line_no, line in enumerate(fh):
            if not line.strip():
                continue
            ep = json.loads(line)
            for q in ep.get("questions", []):
                cands = list(q.get("candidates") or [])
                if len(cands) < 2:
                    continue
                ctx = build_prompt(ep, q, tok) + [sid["<|a|>"]]
                # One seed per question (as src/evals/heldout.py does), so
                # option order and tie breaks are not the same draw on every
                # item. The choice is by mean NLL per option token
                # (src/evals/mc.py); rows say so, because before that change
                # this command chose by summed NLL with ties to index zero.
                best, nlls = score_mc(model, tok, ctx, cands, device,
                                      seed=1_000_003 * line_no + n)
                row = {k: v for k, v in q.items() if k != "text"}
                row.update({
                    "decode": "mc", "mc_rule": "mean_nll_seeded",
                    "ep": line_no, "qid": q.get("qid"),
                    "question": q["text"], "gold": q["answer"],
                    "choice": cands[best], "nlls": [round(v, 4) for v in nlls],
                    "context_tokens": len(ctx),
                    "correct": cands[best] == q["answer"],
                })
                sink.write(json.dumps(row) + "\n")
                n += 1
            if line_no % 200 == 0:
                print(f"{n} scored {time.time() - t0:.0f}s", flush=True)
    print(json.dumps({"out": args.out, "items": n,
                      "seconds": round(time.time() - t0, 1)}), flush=True)
    return 0


# ----------------------------------------------------------------- plan


def cmd_plan(args) -> int:
    from src.train.tokenizer import load_tokenizer

    tok = load_tokenizer(args.tokenizer)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, _ = load_model(args.checkpoint, device)
    rows = []
    with open(args.records) as fh:
        for i, line in enumerate(fh):
            if not line.strip():
                continue
            if args.stride and i % args.stride:
                continue
            rows.append(json.loads(line))
            if args.limit and len(rows) >= args.limit:
                break
    order = sorted(range(len(rows)), key=lambda i: len(rows[i]["prompt"]))
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    t0 = time.time()
    with open(args.out, "w") as sink:
        for s in range(0, len(order), args.batch):
            idx = order[s:s + args.batch]
            outs = generate_batch(model, tok, device,
                                  [rows[i]["prompt"] for i in idx],
                                  args.max_new_tokens, args.temperature,
                                  args.seed + s, batch_size=args.batch)
            for i, text in zip(idx, outs):
                r = dict(rows[i])
                r.pop("prompt", None)
                r.update({"decode": args.label, "emitted": text})
                sink.write(json.dumps(r) + "\n")
            if (s // args.batch) % 20 == 0:
                print(f"{s + len(idx)}/{len(order)} {time.time() - t0:.0f}s",
                      flush=True)
    print(json.dumps({"out": args.out, "n": len(order),
                      "seconds": round(time.time() - t0, 1)}), flush=True)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("gen")
    g.add_argument("--checkpoint", required=True)
    g.add_argument("--tokenizer", required=True)
    g.add_argument("--episodes", required=True)
    g.add_argument("--out", required=True)
    g.add_argument("--label", default="greedy")
    g.add_argument("--samples", type=int, default=1)
    g.add_argument("--temperature", type=float, default=0.0)
    g.add_argument("--batch", type=int, default=32)
    g.add_argument("--max-rounds", type=int, default=4)
    g.add_argument("--max-new-tokens", type=int, default=256)
    g.add_argument("--max-len", type=int, default=1280)
    g.add_argument("--query-max-tokens", type=int, default=24)
    g.add_argument("--max-prompt-tokens", type=int, default=384)
    g.add_argument("--questions-per-episode", type=int, default=2)
    g.add_argument("--min-hops", type=int, default=1)
    g.add_argument("--limit-episodes", type=int, default=None)
    g.add_argument("--seed", type=int, default=99)
    g.set_defaults(fn=cmd_gen)

    m = sub.add_parser("mc")
    m.add_argument("--checkpoint", required=True)
    m.add_argument("--tokenizer", required=True)
    m.add_argument("--episodes", required=True)
    m.add_argument("--out", required=True)
    m.set_defaults(fn=cmd_mc)

    p = sub.add_parser("plan")
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--tokenizer", required=True)
    p.add_argument("--records", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--label", default="greedy")
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--batch", type=int, default=32)
    p.add_argument("--max-new-tokens", type=int, default=640)
    p.add_argument("--stride", type=int, default=0)
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--seed", type=int, default=99)
    p.set_defaults(fn=cmd_plan)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
