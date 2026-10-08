"""Full evaluation of ladder rungs E (goalstack) and F (slots).

This is a driver, not a fork. The representations, the decoders, the obligation
state, the slot layout and the cell scorer are imported from
`src.opgraph.ladder_run` and `src.opgraph.vocab` unchanged. What this file adds
is only what the shared `scripts/vocab_eval.py` does not do:

  deeper sequential depths, out to the point where the representation itself
  can no longer hold the plan. `scripts/ef/deep_probe.py` measures that point:
  the register file is 16 wide and the slot graph is 16 slots, so depth 16 is
  the last depth whose gold plan encodes at all and depth 17 fails at encode
  time in both representations.

  a per-cell decoding budget measured from the gold plan of that cell rather
  than one number for the whole grid. At sequential depth 16 the goal stack
  writes 450 tokens of gold plan, which a flat budget of 320 could not finish
  whatever the model wrote.

  for the goal stack, the same checkpoint decoded with the ban lifted, so the
  constraint can be separated from the representation it sits on. If the ban
  never removes an argmax then E is D and the two decodes agree item for item.

  for the slots, the number of refinement passes swept at decode time, with the
  trained value reported alongside.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from collections import Counter

import torch

from src.opgraph.data import eval_worlds, make_item
from src.opgraph.ladder_run import (GoalHook, SlotDecoder, TokenGenerator,
                                    plan_outputs, score_cell)
from src.opgraph.run import Generator, induce_worlds, load_model
from src.opgraph.vocab import REPS, REP_OF_ARM, RepError, encode_plan, rep_plan_prompt, token_name
from src.train.tokenizer import load_tokenizer

GRID = {
    "sequential": [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16],
    "breadth": [1, 2, 3, 4, 5, 6],
    "novel": [2, 3, 4, 5, 6],
    "sequential_paren": [2, 3, 4, 5, 6],
    "same_page_pair": [2],
    "units": [1],
}

MIN_BUDGET = 320
BUDGET_SLACK = 1.4
# One mask-predict row: <row>, then 16 slots of (opcode + 7 arguments) each
# preceded by its slot identifier, then <retf> and the return field.
SLOT_ROW = 1 + 16 * (1 + 8) + 2


class FreeGoalHook(GoalHook):
    """The goal stack with the ban lifted and everything else identical.

    The annotations are still computed and still written into the sequence, so
    the model sees the distribution it was trained on. Only the mask on the
    sampler is gone. What separates E from D is exactly this object.
    """

    def banned(self):
        return None


class TracedGoalHook(GoalHook):
    """The enforced goal stack, recording what was taken in place of the ban.

    `constraint_bound_rate` says how often the mask removed the argmax. It does
    not say what the model then wrote, which is the difference between a
    constraint that redirects and one that only delays.
    """

    def __init__(self, tok, ops, item, flags=None):
        super().__init__(tok, ops, item, flags)
        self.replacements: Counter = Counter()
        self._pending_bind = None

    def note_bind(self, token: int) -> None:
        super().note_bind(token)
        self._pending_bind = token

    def push(self, token: int, was_forced: bool) -> None:
        if self._pending_bind is not None:
            if not was_forced:
                removed = _name(self.tok, self._pending_bind)
                took = _name(self.tok, token)
                self.replacements[f"{removed}->{took}"] += 1
            self._pending_bind = None
        super().push(token, was_forced)


def _name(tok, tid: int) -> str:
    raw = tok.decode([int(tid)])
    return token_name(raw) or raw.strip() or repr(raw)


def build_sets(kinds, depths_for, n, style):
    sets = {}
    cache = {}
    for kind in kinds:
        for depth in depths_for(kind):
            breadth = depth if kind == "breadth" else 3
            key = (kind, breadth)
            if key not in cache:
                cache[key] = eval_worlds(kind, n, breadth=breadth, style=style)
            sets[(kind, depth)] = [make_item(kind, w, depth, i)
                                   for i, w in enumerate(cache[key])]
    return sets


def cell_budget(rep, items, tok, max_seq_len):
    """The decoding budget for one cell, measured from its own gold plans."""
    longest = 0
    prompt = 0
    for it in items:
        try:
            obj = encode_plan(rep, it.plan, it.world.ops, it)
        except RepError:
            continue
        text = obj if isinstance(obj, str) else " ".join(obj)
        longest = max(longest, len(tok.encode(" " + text)) + 1)
        prompt = max(prompt, len(tok.encode(rep_plan_prompt(rep, it.world.ops,
                                                            it.text))))
    want = max(MIN_BUDGET, int(longest * BUDGET_SLACK) + 8)
    room = max_seq_len - prompt - 4
    return min(want, room), longest, prompt


def goal_plan_outputs(gen, items, induced, use_gold_ops, max_new, hook_cls):
    ops_for = (lambda it: it.world.ops) if use_gold_ops else \
        (lambda it: induced[it.world.seed].ops)
    prompts = [rep_plan_prompt("goalstack", ops_for(it), it.text) for it in items]
    hooks = [hook_cls(gen.tok, ops_for(it), it) for it in items]
    outs = gen.generate(prompts, max_new=max_new, hooks=hooks)
    return [(t, t) for _, t in outs], hooks


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--rep", default=None, choices=list(REPS))
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--batch-size", type=int, default=24)
    ap.add_argument("--slot-batch-size", type=int, default=12)
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--rounds-sweep", default="")
    ap.add_argument("--sweep-kinds", default="sequential,breadth")
    ap.add_argument("--kinds", default=",".join(GRID))
    ap.add_argument("--seq-depths", default="")
    ap.add_argument("--styles", default="0,1")
    ap.add_argument("--temperatures", default="0.0,0.8",
                    help="one output file per temperature, induction shared")
    ap.add_argument("--conditions",
                    default="plan_execute,oracle_plan,oracle_ops,oracle_both")
    ap.add_argument("--free-decode", type=int, default=1)
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    tok = load_tokenizer(args.tokenizer)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, state = load_model(args.ckpt, device)
    rep = args.rep or REP_OF_ARM.get(state.get("arm", ""), None)
    if rep is None:
        raise SystemExit("cannot tell which representation this checkpoint is")
    max_seq_len = model.cfg.max_seq_len

    grid = dict(GRID)
    if args.seq_depths:
        grid["sequential"] = [int(d) for d in args.seq_depths.split(",")]
    kinds = args.kinds.split(",")
    styles = [int(s) for s in args.styles.split(",")]
    want = args.conditions.split(",")
    sweep = [int(r) for r in args.rounds_sweep.split(",") if r]
    sweep_kinds = args.sweep_kinds.split(",")

    sets = {st: build_sets(kinds, lambda k: grid[k], args.n, st)
            for st in styles}

    temps = [float(t) for t in args.temperatures.split(",")]
    # Induction is a greedy decode in every condition and does not depend on
    # the plan decoding temperature, so it is run once per page wording and
    # shared. Running it per temperature would double the cost of the sweep
    # and could only produce the same operators twice.
    res = {t: {"config": dict(vars(args), temperature=t), "rep": rep,
               "max_seq_len": max_seq_len,
               "grid": {k: grid[k] for k in kinds},
               "checkpoint": {k: state.get(k) for k in
                              ("arm", "rep", "step", "tokens",
                               "supervised_tokens", "examples",
                               "reinit_tokens", "rounds")}}
           for t in temps}

    ind_gen = Generator(model, tok, device, batch_size=args.batch_size)
    gens = {t: TokenGenerator(model, tok, device, batch_size=args.batch_size,
                              temperature=t, seed=0) for t in temps}
    slot_decs = {args.rounds: SlotDecoder(model, tok, device,
                                          batch_size=args.slot_batch_size,
                                          rounds=args.rounds)}
    for r in sweep:
        slot_decs.setdefault(r, SlotDecoder(model, tok, device,
                                            batch_size=args.slot_batch_size,
                                            rounds=r))

    conds = (("plan_execute", False, False),
             ("oracle_plan", True, False),
             ("oracle_ops", False, True),
             ("oracle_both", True, True))

    t0 = time.time()
    for st in styles:
        worlds = {it.world.seed: it.world
                  for items in sets[st].values() for it in items}
        induced = induce_worlds(ind_gen, worlds, progress=200)
        stats = Counter()
        for ind in induced.values():
            stats["pages"] += ind.pages
            stats["pages_parsed"] += ind.parsed
            stats["gold_ops"] += ind.gold_count
            stats["induced_ops"] += len(ind.ops)
            stats["self_verified"] += ind.self_verified
            stats["exact_text"] += ind.exact
            stats["behavioural"] += ind.behavioural
        for t in temps:
            res[t][_tag("induction", st)] = dict(stats)
        print(f"[induction style={st}] {json.dumps(dict(stats))}", flush=True)

        for key, items in sets[st].items():
            budget, longest, plen = cell_budget(rep, items, tok, max_seq_len)
            for t in temps:
                res[t].setdefault("budgets", {})[
                    f"{key[0]}/{key[1]}/style{st}"] = {
                        "max_new": budget, "longest_gold": longest,
                        "prompt": plen}
            for t in temps:
                results = res[t]
                gen = gens[t]
                for name, gold_plan, gold_ops in conds:
                    if name not in want:
                        continue
                    if st != 0 and name in ("oracle_ops", "oracle_both"):
                        continue
                    if gold_plan and t != temps[0]:
                        # A gold plan is not decoded, so its cell cannot
                        # depend on the decoding temperature. Copied rather
                        # than recomputed, and identical by construction.
                        results.setdefault(_tag(name, st), {}).setdefault(
                            key[0], {})[str(key[1])] = \
                            res[temps[0]][_tag(name, st)][key[0]][str(key[1])]
                        continue
                    written, side = (None, None)
                    if not gold_plan:
                        if rep == "goalstack":
                            # The traced hook is the shared hook plus a
                            # counter, so this is the decode the harness
                            # would have run.
                            written, side = goal_plan_outputs(
                                gen, items, induced, gold_ops, budget,
                                TracedGoalHook)
                        else:
                            written, side = plan_outputs(
                                rep, gen, slot_decs[args.rounds], items,
                                induced, gold_ops, max_new=budget)
                    cell = score_cell(rep, items, written, induced,
                                      use_gold_plan=gold_plan,
                                      use_gold_ops=gold_ops, side=side)
                    if rep == "goalstack" and side is not None:
                        rep_counts: Counter = Counter()
                        for h in side:
                            rep_counts.update(h.replacements)
                        cell.extra["bind_replacements"] = dict(
                            rep_counts.most_common(8))
                    _record(results, _tag(name, st), key, cell, budget)

                if rep == "goalstack" and args.free_decode and \
                        "plan_execute" in want:
                    # The same checkpoint, the same annotations, no mask.
                    # What is left when the constraint is removed is D's
                    # decode over E's surface form.
                    written, side = goal_plan_outputs(
                        gen, items, induced, False, budget, FreeGoalHook)
                    cell = score_cell(rep, items, written, induced,
                                      use_gold_plan=False, use_gold_ops=False,
                                      side=side)
                    _record(results, _tag("plan_execute_free", st), key,
                            cell, budget)

                if rep == "slots" and sweep and key[0] in sweep_kinds:
                    for r in sweep:
                        if r == args.rounds:
                            continue
                        # One row is 147 tokens and every row so far stays in
                        # the sequence, so a deep sweep runs out of context
                        # rather than out of patience. A cell that does not
                        # fit is left out and said so, not truncated.
                        need = plen + r * SLOT_ROW + 8
                        if need > max_seq_len:
                            results.setdefault("rounds_skipped", []).append(
                                {"kind": key[0], "depth": key[1], "style": st,
                                 "rounds": r, "needed_tokens": need})
                            continue
                        written, side = plan_outputs(
                            rep, gen, slot_decs[r], items, induced, False,
                            max_new=budget)
                        cell = score_cell(rep, items, written, induced,
                                          use_gold_plan=False,
                                          use_gold_ops=False, side=side)
                        _record(results, _tag(f"plan_execute_r{r}", st), key,
                                cell, budget)
                with open(_path(args.out, t), "w") as fh:
                    json.dump(results, fh, indent=1)
            print(f"[{time.time() - t0:7.0f}s] done {key[0]} d={key[1]} "
                  f"style={st} budget={budget}", flush=True)

    rc = 0
    for t in temps:
        results = res[t]
        ob = results.get("oracle_both", {})
        bad = [(k, d, c["acc"]) for k, cells in ob.items()
               for d, c in cells.items() if c["acc"] < 1.0]
        results["oracle_both_all_one"] = not bad
        results["oracle_both_failures"] = bad
        with open(_path(args.out, t), "w") as fh:
            json.dump(results, fh, indent=1)
        print(f"[written] {_path(args.out, t)}")
        if bad:
            print(f"[STOP] oracle_both is not 1.000 in {len(bad)} cells: "
                  f"{bad[:6]}")
            rc = 2
    return rc


def _path(out: str, t: float) -> str:
    """One file per temperature, named by how it was decoded."""
    tag = {0.0: "greedy", 0.8: "sampled"}.get(t, f"t{t:g}".replace(".", ""))
    root, ext = os.path.splitext(out)
    return f"{root}_{tag}{ext}"


def _record(results, tag, key, cell, budget):
    d = cell.as_dict()
    d["max_new"] = budget
    results.setdefault(tag, {}).setdefault(key[0], {})[str(key[1])] = d
    print(f"[{tag}] {key[0]} d={key[1]} acc={cell.correct / max(1, cell.n):.3f} "
          f"parse={cell.parsed / max(1, cell.n):.3f} "
          f"typed={cell.typed / max(1, cell.n):.3f} "
          f"exact={cell.exact / max(1, cell.n):.3f}", flush=True)


def _tag(name: str, style: int) -> str:
    return name if style == 0 else name + "@para"


if __name__ == "__main__":
    raise SystemExit(main())
