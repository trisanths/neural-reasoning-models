"""Running the model: greedy decoding, induction, planning, execution.

The five conditions this module supports are the whole point of the design.

  direct_all      the model answers from all four pages, which is the failure
                  under investigation, restated
  direct_oracle   the model answers with only the pages the question needs,
                  which is the gold source chapter rescue
  plan_execute    the model induces an operator from each page, then writes a
                  plan, then the executor runs the plan
  oracle_plan     the gold plan is supplied and the model only induces, so a
                  failure here is induction or execution and not composition
  oracle_ops      the gold operators are supplied and the model only plans, so
                  a failure here is composition and nothing else
  oracle_both     nothing is asked of the model; the executor alone answers,
                  which must be 1.000 or the harness is broken

Induction is cached per world, because one world serves many questions and
re-inducing the same page would only add sampling noise to the comparison.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import torch

from src.opgraph.data import (direct_prompt, induce_prompt, plan_prompt,
                              trace_prompt)
from src.opgraph.opdef import OpError, Operator, parse_operators, verify
from src.opgraph.plan import (PlanError, answer_text, parse_plan, run_plan,
                              trace_answer)
from src.rl.sampler import CachedPolicy

EOT = "<|eot|>"


class Generator:
    """Greedy batched decoding through the repo's cached sampler."""

    def __init__(self, model, tok, device="cuda", batch_size: int = 16):
        self.model = model
        self.tok = tok
        self.device = device
        self.batch_size = batch_size
        self.eot_id = tok.token_id(EOT)

    def generate(self, prompts: list[str], max_new: int = 96) -> list[str]:
        out: list[str] = []
        for i in range(0, len(prompts), self.batch_size):
            out.extend(self._batch(prompts[i:i + self.batch_size], max_new))
        return out

    def _batch(self, prompts: list[str], max_new: int) -> list[str]:
        ids = [self.tok.encode(p) for p in prompts]
        width = max(len(x) for x in ids)
        cap = min(width + max_new + 2, self.model.cfg.max_seq_len)
        policy = CachedPolicy(self.model, self.device, max_len=cap,
                              temperature=0.0, seed=0)
        nxt = policy.begin(ids)
        done = [False] * len(ids)
        gen: list[list[int]] = [[] for _ in ids]
        for _ in range(max_new):
            step = []
            for i, t in enumerate(nxt):
                if done[i]:
                    step.append(0)
                    continue
                if t == self.eot_id:
                    done[i] = True
                    step.append(0)
                    continue
                gen[i].append(int(t))
                step.append(int(t))
            if all(done):
                break
            nxt = policy.advance(step)
        return [self.tok.decode(g).strip() for g in gen]


# ------------------------------------------------------------- induction

@dataclass
class Induction:
    """What one world's pages produced, and how well it went."""

    ops: dict = field(default_factory=dict)
    parsed: int = 0
    pages: int = 0
    self_verified: int = 0
    exact: int = 0
    behavioural: int = 0
    gold_count: int = 0


def _probes(arity: int):
    if arity == 1:
        return [(3,), (7,), (11,), (0,), (25,)]
    if arity == 2:
        return [(7, 4), (12, 5), (3, 9), (1, 1), (11, 2), (2, 11), (0, 6)]
    # score has one integer and the rest boolean.
    out = []
    for base in (20, 47, 63):
        for mask in range(2 ** (arity - 1)):
            out.append((base,) + tuple(bool(mask >> i & 1) for i in range(arity - 1)))
    return out


def induce_worlds(gen: Generator, worlds: dict, max_new: int = 288,
                  progress: int = 0) -> dict:
    """Induce every page of every world in one batched pass.

    All pages across all worlds go into one decoding queue, so the batch is
    full rather than four wide, and the result is keyed back by world seed.
    """
    jobs = []
    for seed, w in sorted(worlds.items()):
        for p in w.shuffled_pages():
            jobs.append((seed, p))
    texts = []
    for i in range(0, len(jobs), 512):
        chunk = jobs[i:i + 512]
        texts.extend(gen.generate([induce_prompt(p.text) for _, p in chunk],
                                  max_new=max_new))
        if progress:
            print(f"[induce] {min(i + 512, len(jobs))}/{len(jobs)} pages",
                  flush=True)
    out = {seed: Induction() for seed in worlds}
    for (seed, page), text in zip(jobs, texts):
        ind = out[seed]
        ind.pages += 1
        gold = {o.symbol: o for o in page.ops}
        ind.gold_count += len(gold)
        try:
            got = parse_operators(text)
        except OpError:
            continue
        ind.parsed += 1
        for op in got:
            if op.symbol in ind.ops:
                continue
            ind.ops[op.symbol] = op
            ok, _ = verify(op)
            if ok:
                ind.self_verified += 1
            g = gold.get(op.symbol)
            if g is None:
                continue
            if _same_text(g, op):
                ind.exact += 1
            if _same_behaviour(g, op):
                ind.behavioural += 1
    return out


def _same_text(a: Operator, b: Operator) -> bool:
    from src.opgraph.opdef import serialize_expr
    return (a.symbol == b.symbol and a.params == b.params
            and serialize_expr(a.body) == serialize_expr(b.body))


def _same_behaviour(a: Operator, b: Operator) -> bool:
    if a.symbol != b.symbol or a.arity != b.arity:
        return False
    for args in _probes(a.arity):
        try:
            va = a(*args)
        except OpError:
            va = "__err__"
        try:
            vb = b(*args)
        except OpError:
            vb = "__err__"
        if va != vb:
            return False
    return True


# ------------------------------------------------------------- conditions

def score_direct(gen: Generator, items, oracle_page: bool, max_new: int = 24):
    prompts = [direct_prompt(it.world, it.text,
                             set(it.pages) if oracle_page else None)
               for it in items]
    outs = gen.generate(prompts, max_new=max_new)
    return [_norm(o) == _norm(it.gold) for o, it in zip(outs, items)], outs


def score_trace(gen: Generator, items, oracle_page: bool, max_new: int = 256):
    """The written out baseline: same decomposition, no external executor."""
    prompts = [trace_prompt(it.world, it.text,
                            set(it.pages) if oracle_page else None)
               for it in items]
    outs = gen.generate(prompts, max_new=max_new)
    return [_norm(trace_answer(o)) == _norm(it.gold) for o, it in zip(outs, items)], outs


def score_planned(gen: Generator, items, ops_by_world: dict,
                  use_gold_plan: bool, use_gold_ops: bool, max_new: int = 144):
    """Run the plan path. Returns correctness, raw plans, and failure reasons."""
    need = [it for it in items if not use_gold_plan]
    plans: dict[int, str] = {}
    if need:
        prompts = []
        for it in need:
            ops = it.world.ops if use_gold_ops else ops_by_world[it.world.seed].ops
            prompts.append(plan_prompt(ops, it.text))
        outs = gen.generate(prompts, max_new=max_new)
        for it, o in zip(need, outs):
            plans[id(it)] = o
    correct: list[bool] = []
    reasons: list[str] = []
    texts: list[str] = []
    for it in items:
        ops = it.world.ops if use_gold_ops else ops_by_world[it.world.seed].ops
        if use_gold_plan:
            from src.opgraph.plan import serialize_plan
            ptext = serialize_plan(it.plan)
        else:
            ptext = plans[id(it)]
        texts.append(ptext)
        try:
            plan = parse_plan(ptext)
        except PlanError:
            correct.append(False)
            reasons.append("plan_parse")
            continue
        try:
            value = run_plan(plan, ops)
        except (PlanError, OpError):
            correct.append(False)
            reasons.append("execute")
            continue
        ok = _norm(answer_text(value)) == _norm(it.gold)
        correct.append(ok)
        reasons.append("ok" if ok else "wrong_value")
    return correct, texts, reasons


def _norm(s: str) -> str:
    return str(s).strip().strip(".").strip().lower()


def load_model(path: str, device: str = "cuda"):
    from src.train.model import ModelConfig, TransformerLM
    state = torch.load(path, map_location="cpu", weights_only=False)
    model = TransformerLM(ModelConfig(**state["config"]["model"]))
    model.load_state_dict(state["model"])
    model.to(device).eval()
    return model, state
