"""E0, the re-keying rescue ladder over the minimal repro.

The repro in src/disc/minrepro.py leaves depth one at 0.5375 pass@1 and depths
two to four at exactly zero, with a stop-after-one signature. This file asks
one question about that wall: can the substrate execute lookup i at all once
the key for it is handed over, or can it only execute a lookup whose key was
written in the question it was given.

Four rungs, all on the episode files the depth curve was measured on, so the
questions, the pages, the retriever and the grader are the ones already on
record.

  R0  depth d exactly as generated. The control.
  R1  the environment re-keys. After each step the gold intermediate is
      spliced back in as a fresh depth-one sub-question, and that sub-question
      gets the evidence a depth-one episode gets: the preamble and the one
      table its office owns. A depth-d problem becomes d depth-one problems in
      every respect, which is the condition p1^d is a prediction about.
  R1w R1 with the full depth-d page set behind every sub-question. Only the
      re-keying is oracle supplied; picking which of the d tables to read is
      still the model's job. This is the stricter variant and it is not
      matched to the depth-one anchor, whose page set holds two pages.
  R2  as R1 but the key spliced in is the token the model itself named at the
      previous step. The chain is self driven; only the re-keying is done for
      it. R2w is the wide-page variant of it.
  R3  depth d as generated plus one sentence asking the model to name the desk
      at each office in turn. No environment intervention at all, which is the
      difference from R0: R0 never asks for the intermediate, R3 asks for it
      and supplies nothing.
  R3n R3 with a sentence of the same length that asks for nothing, so the cost
      of appending a sentence is measured apart from the cost of the
      instruction it carries.

Two accuracies are kept apart everywhere. chain is every step of the chain
right, which is what p1^d predicts and the number comparable to R0. final is
the last answer right; on R1 and R1w that is the depth-one anchor by
construction, because the key for the last step was handed over.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter

from src.disc.minrepro import _mentions, classify, hits_target

SUB_Q = "A {key} request arrives at the {office} office. Which desk handles it?"
R3_SUFFIX = " Name the desk at each office in turn before giving the answer."
# R3 changes the question, so any effect it has could be the instruction or
# could be the mere fact that a sentence was appended to a surface form the
# policy was trained on. R3N appends a sentence of the same length that asks
# for nothing, which separates the two.
R3N_SUFFIX = " The offices are part of the referral system described above."

RUNGS = ("r0", "r1", "r1w", "r1o", "r2", "r2w", "r3", "r3n")
GOLD_KEY = ("r1", "r1w", "r1o")
OWN_KEY = ("r2", "r2w")
WIDE_PAGES = ("r0", "r1w", "r2w", "r3", "r3n")
PLAIN = ("r0", "r3", "r3n")
ROW = re.compile(r"A (\w+) is handled by the (\w+) desk")


# --------------------------------------------------------------- problem set

def load_problems(path: str) -> list[dict]:
    """One record per question in a minimal-pages episodes file.

    The documents are kept in generator order, which minimal_pages fixes as
    preamble first and then one table per map in chain order. That ordering is
    checked, not assumed.
    """
    out: list[dict] = []
    with open(path) as fh:
        for line_no, line in enumerate(fh):
            line = line.strip()
            if not line:
                continue
            ep = json.loads(line)
            docs = ep["documents"]
            for q in ep["questions"]:
                chain = q["chain"]
                if len(docs) != len(chain) + 1:
                    raise SystemExit(f"{path}: expected {len(chain) + 1} pages, "
                                     f"found {len(docs)}")
                for i, office in enumerate(chain):
                    if not docs[i + 1]["text"].startswith(f"The {office} routing"):
                        raise SystemExit(f"{path}: page {i + 1} is not the "
                                         f"{office} table")
                tables = [dict(ROW.findall(docs[i + 1]["text"]))
                          for i in range(len(chain))]
                for i in range(len(chain)):
                    if tables[i].get(q["stages"][i]) != q["stages"][i + 1]:
                        raise SystemExit(f"{path}: table {i} does not carry "
                                         f"stage {i} of {q['qid']}")
                out.append({
                    "episode_index": line_no,
                    "qid": q["qid"],
                    "tables": tables,
                    "depth": q["depth"],
                    "text": q["text"],
                    "start": q["start"],
                    "chain": chain,
                    "stages": q["stages"],
                    "answer": q["answer"],
                    "docs": docs,
                    "alphabet": ep["alphabet"],
                    "world": ep.get("world", {}),
                })
    return out


def extract_token(answer: str, universe: list[str]) -> str | None:
    """The notation token the model's answer names, or None.

    The family idiom puts the answer last ("... the clomel desk"), and the
    traces on record are word salad with the target token at or near the end,
    so the rule is the last whole-word occurrence of any token in the
    episode's universe. Case is normalised to the canonical form, which is a
    small help the environment gives and which is recorded as such.
    """
    best: tuple[int, str] | None = None
    for t in universe:
        for m in re.finditer(rf"(?<![\w]){re.escape(t)}(?![\w])", answer,
                             re.IGNORECASE):
            if best is None or m.end() > best[0]:
                best = (m.end(), t)
    return best[1] if best else None


def named_tokens(answer: str, universe: list[str]) -> list[str]:
    """Every distinct universe token the answer names, in order of appearance.

    The shipped grader in src/rl/env.py accepts a prediction that contains the
    gold with slack, so an answer naming two desks is scored correct whenever
    either is the gold one. This is what makes that visible: length one is a
    committed answer, length two or more is a hedge.
    """
    hits: list[tuple[int, str]] = []
    for t in universe:
        m = re.search(rf"(?<![\w]){re.escape(t)}(?![\w])", answer,
                      re.IGNORECASE)
        if m:
            hits.append((m.start(), t))
    return [t for _, t in sorted(hits)]


# ------------------------------------------------------------------ rollouts

class _Chain:
    __slots__ = ("problem", "sample", "key", "answers", "step_ok", "broken",
                 "rounds", "leaked", "off_manifold", "step_strict")

    def __init__(self, problem: dict, sample: int):
        self.problem = problem
        self.sample = sample
        self.key = problem["start"]
        self.answers: list[str] = []
        self.step_ok: list[bool] = []
        self.step_strict: list[bool] = []
        self.rounds: list[int] = []
        self.broken = False
        self.leaked = False
        self.off_manifold = False


def _pages_for(problem: dict, rung: str, step: int) -> list[dict]:
    """The page set one sub-question sees.

    Three scopes. Wide is every page the depth-d episode has, in generator
    order, which puts the table the step needs at position step+1. Narrow is
    the preamble and the one table the step needs, which is the evidence a
    depth-one episode gets. Ordered keeps every page but moves the step's own
    table to position one, so page count is held fixed and only position
    moves; that is what tells a retrieval-order effect apart from a
    page-count effect.
    """
    docs = problem["docs"]
    if rung == "r1o":
        return ([docs[0], docs[step + 1]]
                + [docs[j + 1] for j in range(len(problem["chain"]))
                   if j != step])
    if rung in WIDE_PAGES:
        return docs
    return [docs[0], docs[step + 1]]


def _task(problem: dict, qtext: str, gold: str, docs: list[dict], tok):
    from src.rl.env import Task, build_prompt

    episode = {"world": problem["world"], "documents": docs, "n_context": 0}
    prompt = build_prompt(episode, {"text": qtext}, tok)
    return Task(episode_index=problem["episode_index"], qid=problem["qid"],
                question=qtext, gold=gold, prompt=prompt, documents=docs,
                domain=problem["world"].get("domain", "unknown"), hops=1)


def run_rung(model, tok, device, problems: list[dict], rung: str, *,
             samples: int, temperature: float, batch: int, max_len: int,
             max_rounds: int, max_new_tokens: int, seed: int,
             max_prompt_tokens: int) -> dict:
    """Roll one rung out over one depth and summarise it."""
    from src.rl.env import EnvConfig, EpisodeEnv, rollout_stats
    from src.rl.sampler import CachedPolicy

    env = EpisodeEnv(tok, EnvConfig(max_rounds=max_rounds,
                                    max_new_tokens=max_new_tokens,
                                    max_len=max_len))
    depth = problems[0]["depth"]
    n_steps = 1 if rung in PLAIN else depth
    chains = [_Chain(p, s) for p in problems for s in range(samples)]

    leaks = Counter()
    dropped = 0
    per_step: list[dict] = []
    traces: list[dict] = []

    for step in range(n_steps):
        live = [c for c in chains if not c.broken]
        if not live:
            per_step.append({"step": step, "n": 0})
            break
        tasks = []
        golds = []
        keyed = []
        for c in live:
            p = c.problem
            owed = None
            if rung == "r0":
                qtext, gold, docs = p["text"], p["answer"], p["docs"]
            elif rung in ("r3", "r3n"):
                suffix = R3_SUFFIX if rung == "r3" else R3N_SUFFIX
                qtext, gold, docs = p["text"] + suffix, p["answer"], p["docs"]
            else:
                key = p["stages"][step] if rung in GOLD_KEY else c.key
                qtext = SUB_Q.format(key=key, office=p["chain"][step])
                gold = p["stages"][step + 1]
                docs = _pages_for(p, rung, step)
                # What the lookup owes for the key it was actually handed,
                # which is not the gold stage once the model has drifted.
                owed = p["tables"][step].get(key)
                # The one way this experiment could fool us: a spliced
                # sub-question that names the final answer, which would let a
                # copier win. Checked on every sub-question, never filtered.
                if _mentions(p["answer"], qtext):
                    leaks["final_answer_in_subquestion"] += 1
                    c.leaked = True
                if _mentions(gold, qtext):
                    leaks["step_answer_in_subquestion"] += 1
                if key not in p["alphabet"]:
                    leaks["key_outside_universe"] += 1
                if key != p["stages"][step]:
                    c.off_manifold = True
            t = _task(p, qtext, gold, docs, tok)
            if len(t.prompt) > max_prompt_tokens:
                dropped += 1
                c.broken = True
                continue
            tasks.append(t)
            golds.append(gold)
            keyed.append(owed)
        live = [c for c in live if not c.broken]

        policy = CachedPolicy(model, device, max_len=max_len,
                              temperature=temperature,
                              seed=seed + 1009 * step + 7 * RUNGS.index(rung))
        rolls = []
        for i in range(0, len(tasks), batch):
            rolls.extend(env.rollout(policy, tasks[i:i + batch]))

        # Which page the retriever actually served, and what the lookup does
        # when it has the page it needs. This is the one measurement that
        # tells a retrieval failure apart from a lookup failure, so it is
        # taken on every rung and every step.
        gold_page = depth if rung in PLAIN else (
            step + 1 if rung in WIDE_PAGES else 1)
        served_hist = Counter()
        with_gold = [0, 0]
        without_gold = [0, 0]

        ok_n = 0
        strict_n = 0
        hedged_n = 0
        named_hist = Counter()
        keyed_ok = 0
        keyed_n = 0
        no_token = 0
        for c, r, gold, owed in zip(live, rolls, golds, keyed):
            c.answers.append(r.answer_text)
            c.rounds.append(r.n_rounds)
            ok = hits_target(r.answer_text, gold)
            c.step_ok.append(ok)
            ok_n += int(ok)
            # forced choice: the first universe token named is the answer, and
            # naming more than one counts as wrong. this is the grader that
            # cannot be satisfied by hedging.
            named = named_tokens(r.answer_text, c.problem["alphabet"])
            named_hist[len(named)] += 1
            hedged = len(named) > 1
            hedged_n += int(hedged)
            strict = (len(named) == 1 and named[0] == gold)
            c.step_strict.append(strict)
            strict_n += int(strict)
            served = [x["doc_index"] for x in r.rounds]
            for s in served:
                served_hist[s] += 1
            bucket = with_gold if gold_page in served else without_gold
            bucket[0] += 1
            bucket[1] += int(ok)
            if owed is not None:
                keyed_n += 1
                keyed_ok += int(hits_target(r.answer_text, owed))
            got = extract_token(r.answer_text, c.problem["alphabet"])
            if got is None:
                no_token += 1
            if rung in OWN_KEY:
                if got is None:
                    c.broken = True
                else:
                    c.key = got
            if len(traces) < 8 and step == n_steps - 1:
                traces.append({"question": r.task.question, "gold": r.task.gold,
                               "answer": r.answer_text,
                               "rounds": [x["query"][:60] for x in r.rounds],
                               "stop": r.stop_reason})
        stats = rollout_stats(rolls)
        per_step.append({
            "step": step, "n": len(rolls),
            # against the gold stage for this step
            "step_accuracy": ok_n / max(1, len(rolls)),
            # the same step under forced choice, and how often the answer
            # named more than one candidate at all
            "step_accuracy_forced": strict_n / max(1, len(rolls)),
            "hedge_rate": hedged_n / max(1, len(rolls)),
            "named_token_counts": dict(named_hist),
            # against what the table owes for the key the model was handed,
            # which differs from the gold stage only once R2 has drifted
            "accuracy_vs_handed_key": keyed_ok / max(1, keyed_n),
            "n_keyed": keyed_n,
            "no_token_in_answer": no_token / max(1, len(rolls)),
            "mean_rounds": stats["mean_rounds"],
            "any_retrieval": stats["any_retrieval"],
            "well_formed": stats["well_formed"],
            "gold_page": gold_page,
            "served_pages": dict(served_hist),
            "served_gold_page": with_gold[0] / max(1, len(rolls)),
            "acc_given_gold_page": with_gold[1] / max(1, with_gold[0]),
            "n_given_gold_page": with_gold[0],
            "acc_without_gold_page": without_gold[1] / max(1, without_gold[0]),
            "n_without_gold_page": without_gold[0],
        })

    # ------------------------------------------------------------- scoring
    #
    # Two numbers, never merged. chain is every step of the chain right, which
    # is what p1^d predicts and the only number comparable to R0 on a rung
    # where the environment hands the last key over. final is the last answer
    # right; on R1 and R1w that is the depth-one anchor by construction,
    # because the key for the last step was supplied.
    by_q_chain: dict[tuple[int, str], list[bool]] = {}
    by_q_final: dict[tuple[int, str], list[bool]] = {}
    by_q_chain_f: dict[tuple[int, str], list[bool]] = {}
    by_q_final_f: dict[tuple[int, str], list[bool]] = {}
    kinds = Counter()
    n_final = 0
    n_chain = 0
    n_final_f = 0
    n_chain_f = 0
    n_final_hedged = 0
    n_broken = 0
    leaked_correct = 0
    for c in chains:
        p = c.problem
        final = c.answers[-1] if c.answers else ""
        fin_ok = bool(c.answers) and hits_target(final, p["answer"])
        fin_named = named_tokens(final, p["alphabet"]) if c.answers else []
        fin_ok_f = len(fin_named) == 1 and fin_named[0] == p["answer"]
        n_final_hedged += int(len(fin_named) > 1)
        chain_ok_f = len(c.step_strict) == n_steps and all(c.step_strict)
        n_chain_f += int(chain_ok_f)
        n_final_f += int(fin_ok_f)
        by_q_chain_f.setdefault((p["episode_index"], p["qid"]),
                                []).append(chain_ok_f)
        by_q_final_f.setdefault((p["episode_index"], p["qid"]),
                                []).append(fin_ok_f)
        chain_ok = len(c.step_ok) == n_steps and all(c.step_ok)
        if not c.answers or len(c.answers) < n_steps:
            n_broken += 1
        n_final += int(fin_ok)
        n_chain += int(chain_ok)
        if c.leaked and fin_ok:
            leaked_correct += 1
        kinds[classify(final, p, p["alphabet"])] += 1
        key = (p["episode_index"], p["qid"])
        by_q_chain.setdefault(key, []).append(chain_ok)
        by_q_final.setdefault(key, []).append(fin_ok)

    n_roll = len(chains)
    n_q = len(by_q_chain)
    return {
        "rung": rung,
        "depth": depth,
        "n_steps": n_steps,
        "n_questions": n_q,
        "samples": samples,
        "n_chains": n_roll,
        "n_rollouts": sum(s.get("n", 0) for s in per_step),
        "chain_pass_at_1": n_chain / max(1, n_roll),
        "chain_pass_at_k": sum(any(v) for v in by_q_chain.values()) / max(1, n_q),
        "final_pass_at_1": n_final / max(1, n_roll),
        "final_pass_at_k": sum(any(v) for v in by_q_final.values()) / max(1, n_q),
        # the same four under forced choice, where naming more than one
        # candidate is wrong, plus how often the last answer hedged at all
        "chain_pass_at_1_forced": n_chain_f / max(1, n_roll),
        "chain_pass_at_k_forced": sum(any(v) for v in by_q_chain_f.values())
        / max(1, n_q),
        "final_pass_at_1_forced": n_final_f / max(1, n_roll),
        "final_pass_at_k_forced": sum(any(v) for v in by_q_final_f.values())
        / max(1, n_q),
        "final_hedge_rate": n_final_hedged / max(1, n_roll),
        "chance_per_step": 1.0 / max(1, len(chains[0].problem["alphabet"])),
        "chance_per_chain": (1.0 / max(1, len(chains[0].problem["alphabet"])))
        ** n_steps,
        "broken_chains": n_broken / max(1, n_roll),
        "off_manifold_keys": sum(c.off_manifold for c in chains) / max(1, n_roll),
        "classes": {k: v / max(1, n_roll) for k, v in kinds.items()},
        "per_step": per_step,
        "leaks": dict(leaks),
        "leaked_and_correct": leaked_correct,
        "dropped_long_prompts": dropped,
        "traces": traces,
    }


# ------------------------------------------------------------------ baselines

def shortcut_baselines(problems: list[dict], rung: str) -> dict:
    """What a reader with no composition gets on this rung's questions.

    most_frequent_token returns the token that appears most often on the
    pages. keyword_nearest picks the single best matching page by the training
    oracle's own BM25 and reads the row for the key it was given, which is the
    depth-one answer. depth_one_answer answers the depth-one question buried
    in the depth-d question. Chance is one over the alphabet of one level.
    """
    from src.train.retrieval import BM25Index

    hits = Counter()
    chain_hits = Counter()
    n_steps_total = 0
    n_chains = 0
    for p in problems:
        texts = [d["text"] for d in p["docs"]]
        blob = "\n".join(texts)
        counts = {a: len(re.findall(rf"(?<![\w]){re.escape(a)}(?![\w])", blob))
                  for a in p["alphabet"]}
        top_symbol = max(counts, key=lambda a: counts[a])
        n_chains += 1
        if rung in PLAIN:
            steps = [(p["text"], p["answer"], texts, p["start"])]
        else:
            steps = []
            for i, office in enumerate(p["chain"]):
                key = p["stages"][i]
                sub = SUB_Q.format(key=key, office=office)
                docs = [d["text"] for d in _pages_for(p, rung, i)]
                steps.append((sub, p["stages"][i + 1], docs, key))
        per_chain = Counter()
        for qtext, gold, docs, key in steps:
            n_steps_total += 1
            if gold == top_symbol:
                hits["most_frequent_token"] += 1
                per_chain["most_frequent_token"] += 1
            index = BM25Index(docs, reliabilities=[1.0] * len(docs))
            try:
                page = docs[index.top(qtext, exclude=set())]
            except (ValueError, IndexError):
                page = ""
            m = re.search(rf"A {re.escape(key)} is handled by the (\w+) desk",
                          page)
            if m and m.group(1) == gold:
                hits["keyword_nearest"] += 1
                per_chain["keyword_nearest"] += 1
            if gold == p["stages"][1]:
                hits["depth_one_answer"] += 1
                per_chain["depth_one_answer"] += 1
            if gold == p["start"]:
                hits["copy_start"] += 1
                per_chain["copy_start"] += 1
        for k, v in per_chain.items():
            if v == len(steps):
                chain_hits[k] += 1
    return {
        "n_steps": n_steps_total,
        "n_chains": n_chains,
        "chance": 1.0 / 6,
        "per_step": {k: v / max(1, n_steps_total) for k, v in hits.items()},
        "per_chain": {k: v / max(1, n_chains) for k, v in chain_hits.items()},
    }


# ------------------------------------------------------------------ integrity

def audit_problems(problems: list[dict]) -> dict:
    """The repro's own exclusions, re-run on exactly the questions used here."""
    viol = Counter()
    for p in problems:
        stages, gold = p["stages"], p["answer"]
        if _mentions(gold, p["text"]):
            viol["answer_in_question"] += 1
        if gold == stages[0]:
            viol["answer_is_start"] += 1
        if gold in stages[:-1]:
            viol["answer_is_intermediate"] += 1
        if len(set(stages)) != len(stages):
            viol["stages_not_distinct"] += 1
        if gold != stages[-1]:
            viol["gold_is_not_final_stage"] += 1
        for i, office in enumerate(p["chain"]):
            sub = SUB_Q.format(key=stages[i], office=office)
            if _mentions(gold, sub) and i < len(p["chain"]) - 1:
                viol["final_answer_in_gold_subquestion"] += 1
            if _mentions(stages[i + 1], sub):
                viol["step_answer_in_gold_subquestion"] += 1
        if _mentions(gold, p["text"] + R3_SUFFIX):
            viol["answer_in_r3_question"] += 1
        if _mentions(gold, p["text"] + R3N_SUFFIX):
            viol["answer_in_r3n_question"] += 1
    return {"n_questions": len(problems), "violations": dict(viol)}


# ------------------------------------------------------------------------ cli

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--files", required=True,
                    help="comma separated minimal-pages episodes files")
    ap.add_argument("--rungs", default="r0,r1,r1w,r2,r2w,r3")
    ap.add_argument("--checkpoint", default="")
    ap.add_argument("--tokenizer", default="")
    ap.add_argument("--out", default="")
    ap.add_argument("--samples", type=int, default=4)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--max-len", type=int, default=1024)
    ap.add_argument("--max-prompt-tokens", type=int, default=800)
    ap.add_argument("--max-rounds", type=int, default=6)
    ap.add_argument("--max-new-tokens", type=int, default=96)
    ap.add_argument("--seed", type=int, default=99)
    ap.add_argument("--limit", type=int, default=0,
                    help="keep only the first N questions per file, for smoke")
    ap.add_argument("--audit-only", action="store_true")
    args = ap.parse_args()

    paths = [p for p in args.files.split(",") if p]
    rungs = [r for r in args.rungs.split(",") if r]
    for r in rungs:
        if r not in RUNGS:
            raise SystemExit(f"unknown rung {r!r}")

    sets = {}
    for path in paths:
        probs = load_problems(path)
        if args.limit:
            probs = probs[: args.limit]
        sets[path] = probs

    report = {"files": paths, "rungs": rungs, "audit": {}, "baselines": {},
              "cells": [],
              "config": {"samples": args.samples,
                         "temperature": args.temperature,
                         "max_len": args.max_len,
                         "max_rounds": args.max_rounds,
                         "max_new_tokens": args.max_new_tokens,
                         "seed": args.seed,
                         "r3_suffix": R3_SUFFIX,
                         "r3n_suffix": R3N_SUFFIX,
                         "sub_question": SUB_Q}}
    for path, probs in sets.items():
        report["audit"][path] = audit_problems(probs)
        for r in rungs:
            report["baselines"][f"{path}::{r}"] = shortcut_baselines(probs, r)
    print(json.dumps({"audit": report["audit"]}, indent=1), flush=True)

    if args.audit_only:
        if args.out:
            with open(args.out, "w") as fh:
                json.dump(report, fh, indent=1)
        return 0

    from src.disc.minrepro import load_policy_parts
    model, tok, device = load_policy_parts(args.checkpoint, args.tokenizer)
    for path, probs in sets.items():
        for r in rungs:
            cell = run_rung(model, tok, device, probs, r,
                            samples=args.samples, temperature=args.temperature,
                            batch=args.batch, max_len=args.max_len,
                            max_rounds=args.max_rounds,
                            max_new_tokens=args.max_new_tokens,
                            seed=args.seed,
                            max_prompt_tokens=args.max_prompt_tokens)
            cell["episodes_path"] = path
            report["cells"].append(cell)
            slim = {k: v for k, v in cell.items() if k != "traces"}
            print(json.dumps(slim), flush=True)
            if args.out:
                with open(args.out, "w") as fh:
                    json.dump(report, fh, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
