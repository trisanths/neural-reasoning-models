"""Run the acquisition loop against a real policy on one invented universe.

The reasoner here is the trained policy, driven through the same rollout the
RL environment uses, so a call inside the loop and a call inside training walk
the same trace: the prompt is <|world|> preamble, an optional <|doc|> carrying
the compiled card, then <|q|> question, and from there the policy emits its
own <|retrieve|> queries and reads back the served chunks.

One design decision is worth stating plainly, because it bounds every number
this script produces. The loop's own searching happens in Python, not through
the policy's retrieval channel. gap.py writes the query, lesson.py ranks the
corpus, curriculum.py decides what to open next. The policy's job is narrower:
answer a question given a card and a document store. That split is deliberate
-- the policy's own queries are poor, and a loop that depended on them would
measure the policy's query writing rather than the loop -- but it means these
results say nothing about a policy that has to drive the search itself.

Baselines this script also produces, so the loop's numbers have something to
sit against:

  --rule-test   the three-condition control on the acquisition problems:
                the right pages retrievable, another chapter's pages
                retrievable, or a blank page. This is the acquisition
                condition from scripts/skill_rule_test.py, rebuilt on the
                layered universe and reported per level.
"""

from __future__ import annotations

import argparse
import json
import time

import torch

from src.acquire.loop import (LoopConfig, calibration_report, gap_calibration,
                              report, run_problem)
from src.acquire.reasoner import AnswerRequest, ConstantReasoner, SymbolicReasoner
from src.acquire.universe import build_universe
from src.evals.mc import load_checkpoint_model
from src.rl.env import EnvConfig, EpisodeEnv, Task, make_service
from src.rl.sampler import CachedPolicy
from src.train.data import render_world_preamble
from src.train.tokenizer import load_tokenizer


class PolicyReasoner:
    """The trained policy, batched through src/rl/env.py's rollout."""

    def __init__(self, checkpoint: str, tokenizer_path: str,
                 device: str = "cuda", temperature: float = 0.7,
                 seed: int = 1234, max_rounds: int = 4,
                 max_new_tokens: int = 64, max_len: int = 1024,
                 batch_size: int = 32, max_prompt_tokens: int = 700):
        self.tok = load_tokenizer(tokenizer_path)
        self.device = device
        self.model, _ = load_checkpoint_model(checkpoint, device)
        self.model.eval()
        self.env = EpisodeEnv(self.tok, EnvConfig(
            max_rounds=max_rounds, max_new_tokens=max_new_tokens,
            max_len=max_len, query_max_tokens=24))
        self.temperature = temperature
        self.seed = seed
        self.max_len = max_len
        self.batch_size = batch_size
        self.max_prompt_tokens = max_prompt_tokens
        self.calls = 0
        self.truncated_prompts = 0
        self.transcripts: list[dict] = []
        self.keep_transcripts = 0

    def _prompt(self, request: AnswerRequest) -> list[int]:
        sid = self.tok.special_ids
        ids = [sid["<|world|>"]]
        ids.extend(self.tok.encode(render_world_preamble(
            {"domain": "acquisition"})))
        if request.card:
            ids.append(sid["<|doc|>"])
            ids.extend(self.tok.encode(request.card))
        ids.append(sid["<|q|>"])
        ids.extend(self.tok.encode(request.question))
        if len(ids) > self.max_prompt_tokens:
            self.truncated_prompts += 1
            ids = ids[:self.max_prompt_tokens]
        return ids

    def answer_batch(self, requests: list[AnswerRequest]) -> list[str]:
        out: list[str] = []
        for start in range(0, len(requests), self.batch_size):
            chunk = requests[start:start + self.batch_size]
            tasks = []
            for i, req in enumerate(chunk):
                tasks.append(Task(
                    episode_index=i, qid=req.tag or "q", question=req.question,
                    gold="", prompt=self._prompt(req), documents=req.documents,
                    domain="acquisition", hops=1))
            services = [make_service(t.documents) for t in tasks]
            policy = CachedPolicy(self.model, self.device, max_len=self.max_len,
                                  temperature=self.temperature, seed=self.seed)
            rolls = self.env.rollout(policy, tasks, services=services)
            self.calls += len(rolls)
            for req, roll in zip(chunk, rolls):
                out.append(roll.answer_text)
                if len(self.transcripts) < self.keep_transcripts:
                    self.transcripts.append({
                        "tag": req.tag, "question": req.question,
                        "answer": roll.answer_text,
                        "n_rounds": roll.n_rounds,
                        "stop_reason": roll.stop_reason,
                        "queries": [r["query"] for r in roll.rounds],
                        "card_chars": len(req.card),
                    })
        return out

    def answer(self, request: AnswerRequest) -> str:
        return self.answer_batch([request])[0]


def rule_test(universe, reasoner) -> dict:
    """The three-condition control, per level.

    textbook        the chapter's pages are retrievable
    wrong_chapter   another chapter's pages are retrievable
    blank           one empty page is retrievable

    A model that scores on the blank or wrong-chapter conditions is scoring
    on something other than the material, which is the failure the registry
    lesson was about.
    """
    by_chapter = {ch.chapter_id: ch for ch in universe.chapters}
    all_docs = universe.documents()
    blank = [{"text": "This page is intentionally blank.", "reliability": 1.0,
              "page_id": "blank", "kind": "statement", "chapter": "",
              "notion": None, "level": 0, "title": "", "body": ""}]
    conditions: dict[str, list] = {"textbook": [], "wrong_chapter": [],
                                   "blank": []}
    problems = universe.problems()
    chapter_ids = [ch.chapter_id for ch in universe.chapters]
    for name in conditions:
        reqs = []
        for p in problems:
            if name == "textbook":
                docs = [d for d in all_docs if d["chapter"] == p.chapter]
            elif name == "wrong_chapter":
                other = [c for c in chapter_ids if c != p.chapter][0]
                docs = [d for d in all_docs if d["chapter"] == other]
            else:
                docs = blank
            reqs.append(AnswerRequest(question=p.text, documents=docs,
                                      card="", tag=name))
        answers = reasoner.answer_batch(reqs)
        conditions[name] = answers

    from src.acquire.selftest import _matches
    out: dict = {}
    for level in sorted({p.level for p in problems}):
        idx = [i for i, p in enumerate(problems) if p.level == level]
        cell = {"n": len(idx)}
        for name, answers in conditions.items():
            cell[name] = sum(_matches(answers[i], problems[i].answer)
                             for i in idx) / len(idx)
        out[f"L{level}"] = cell
    for ch_id in chapter_ids:
        idx = [i for i, p in enumerate(problems) if p.chapter == ch_id]
        if not idx:
            continue
        cell = {"n": len(idx)}
        for name, answers in conditions.items():
            cell[name] = sum(_matches(answers[i], problems[i].answer)
                             for i in idx) / len(idx)
        out[ch_id] = cell
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint")
    ap.add_argument("--tokenizer")
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=101)
    ap.add_argument("--chapters", type=int, default=3)
    ap.add_argument("--problem-chapters", type=int, default=2)
    ap.add_argument("--per-level", type=int, default=6)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--max-new-tokens", type=int, default=64)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--reasoner", default="policy",
                    choices=["policy", "symbolic", "constant"])
    ap.add_argument("--rule-test", action="store_true")
    ap.add_argument("--no-gate", action="store_true")
    ap.add_argument("--transcripts", type=int, default=40)
    args = ap.parse_args()

    universe = build_universe(args.seed, n_chapters=args.chapters,
                              n_per_level=args.per_level,
                              problem_chapters=args.problem_chapters)
    problems = universe.problems()
    print(f"universe: {len(universe.chapters)} chapters, "
          f"{len(universe.pages)} pages, {len(problems)} problems",
          flush=True)
    proof_summary = {
        "n": len(problems),
        "all_proofs_pass": all(p.proof["ok"] for p in problems),
        "mean_required_notions": sum(len(p.required_notions)
                                     for p in problems) / max(1, len(problems)),
        "min_choices": min((p.n_choices for p in problems), default=0),
    }
    print("proofs:", json.dumps(proof_summary), flush=True)

    if args.reasoner == "policy":
        reasoner = PolicyReasoner(
            args.checkpoint, args.tokenizer, temperature=args.temperature,
            max_new_tokens=args.max_new_tokens, batch_size=args.batch_size)
        reasoner.keep_transcripts = args.transcripts
    elif args.reasoner == "symbolic":
        reasoner = SymbolicReasoner()
    else:
        reasoner = ConstantReasoner("unknown")

    results: dict = {"seed": args.seed, "reasoner": args.reasoner,
                     "checkpoint": args.checkpoint,
                     "temperature": args.temperature,
                     "proofs": proof_summary}

    if args.rule_test:
        t0 = time.time()
        results["rule_test"] = rule_test(universe, reasoner)
        print("rule_test:", json.dumps(results["rule_test"], indent=2),
              flush=True)
        print(f"rule_test took {time.time() - t0:.0f}s", flush=True)

    cfg = LoopConfig(gate=not args.no_gate)
    by_id = {ch.chapter_id: ch for ch in universe.chapters}
    if args.limit:
        problems = problems[:args.limit]
    traces = []
    t0 = time.time()
    for i, problem in enumerate(problems):
        traces.append(run_problem(problem, by_id[problem.chapter],
                                  universe.documents(), reasoner, cfg))
        if (i + 1) % 5 == 0:
            print(f"  {i + 1}/{len(problems)} "
                  f"{time.time() - t0:.0f}s", flush=True)
    calib = []
    for problem in problems:
        calib.extend(gap_calibration(problem, by_id[problem.chapter],
                                     universe.documents(), reasoner))
    results["gap_calibration"] = calibration_report(calib)
    print("gap calibration:", json.dumps(results["gap_calibration"], indent=2),
          flush=True)
    results["loop"] = report(traces)
    results["wall_seconds"] = round(time.time() - t0, 1)

    with open(args.out, "w") as fh:
        json.dump(results, fh, indent=2)
    with open(args.out.replace(".json", "-traces.jsonl"), "w") as fh:
        for t in traces:
            fh.write(json.dumps(t.to_dict()) + "\n")
    if getattr(reasoner, "transcripts", None):
        with open(args.out.replace(".json", "-transcripts.jsonl"), "w") as fh:
            for t in reasoner.transcripts:
                fh.write(json.dumps(t) + "\n")
    print(json.dumps(results["loop"], indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
