"""Check 6: executor independence, and the reverse leak.

Runs entirely on the dumps written by src/audit/leak_run.py. Nothing here asks
the model anything; every number is a property of what the executor was handed
and what it did with it.

  6.1  which operator OBJECT the executor invoked, by identity, per condition
  6.2  what the gold plan carries: step symbols, literal arguments, the answer
  6.3  what the model was shown under each condition
  6.4  corruption counterfactuals: break the induced operator and see whether
       oracle_plan follows it down
  6.5  the reverse leak: correct answers reached with no induced operator call,
       with a builtin, or with a plan shorter than the question
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict

from src.opgraph.opdef import Call, OpError, Operator, parse_operator
from src.opgraph.plan import (BUILTIN_STEPS, PlanError, answer_text, parse_plan,
                              run_plan, serialize_plan, signature_line)


def _norm(s) -> str:
    return str(s).strip().strip(".").strip().lower()


def load(path):
    with open(path) as fh:
        return json.load(fh)


# ------------------------------------------------------------------- 6.1

def check_identity(dump) -> dict:
    """Resolve every recorded operator call to the object it actually used."""
    ind_id, gold_id = {}, {}
    for seed, w in dump["worlds"].items():
        for sym, i in w["induced_ids"].items():
            ind_id[i] = (seed, sym)
        for sym, i in w["gold_ids"].items():
            gold_id[i] = (seed, sym)
    shared = set(ind_id) & set(gold_id)
    out = {"n_worlds": len(dump["worlds"]),
           "induced_object_ids": len(ind_id), "gold_object_ids": len(gold_id),
           "ids_shared_between_tables": len(shared), "per_cond": {}}
    tally = defaultdict(Counter)
    tables = defaultdict(Counter)
    for c in dump["calls"]:
        cond = c.get("cond")
        if c.get("marker"):
            ids = set(c["table_ids"].values())
            n_i = len(ids & set(ind_id))
            n_g = len(ids & set(gold_id))
            tables[cond][f"table_induced={n_i}_gold={n_g}"] += 1
            continue
        if c.get("missing"):
            tally[cond]["lookup_missed"] += 1
            continue
        i = c["op_id"]
        if i in ind_id and i in gold_id:
            tally[cond]["ambiguous"] += 1
        elif i in ind_id:
            tally[cond]["induced_object"] += 1
        elif i in gold_id:
            tally[cond]["gold_object"] += 1
        else:
            tally[cond]["unknown_object"] += 1
    for cond in tally:
        out["per_cond"][cond] = {"calls": dict(tally[cond]),
                                 "tables": dict(tables[cond])}
    return out


# ------------------------------------------------------------------- 6.2

def check_gold_plans(dump) -> dict:
    out = {}
    for d, rec in dump["items"].items():
        stats = Counter()
        for gp, gold, qtext in zip(rec["gold_plans"], rec["gold"], rec["texts"]):
            p = parse_plan(gp)
            stats["plans"] += 1
            stats["steps"] += len(p.steps)
            for s in p.steps:
                if s.symbol in BUILTIN_STEPS:
                    stats["builtin_steps"] += 1
                else:
                    stats["operator_steps"] += 1
                for a in s.args:
                    if isinstance(a, str) and a.startswith("t"):
                        stats["temp_args"] += 1
                    else:
                        stats["literal_args"] += 1
            if not p.steps:
                stats["plans_with_no_step"] += 1
            if p.answer.lstrip("-").isdigit() or p.answer.startswith("'"):
                stats["ans_is_literal"] += 1
            else:
                stats["ans_is_temporary"] += 1
            if _norm(gold) in [_norm(x) for x in gp.replace(";", " ").split()]:
                stats["gold_answer_token_in_plan"] += 1
            # does any literal in the plan equal an intermediate value?
            env = {}
            inter = set()
            for s in p.steps:
                pass
            lits = set()
            for s in p.steps:
                for a in s.args:
                    if isinstance(a, int) and not isinstance(a, bool):
                        lits.add(a)
            qnums = set()
            for t in qtext.replace("(", " ").replace(")", " ").replace(".", " ").split():
                if t.lstrip("-").isdigit():
                    qnums.add(int(t))
            if lits - qnums:
                stats["plans_with_literal_not_in_question"] += 1
        out[d] = dict(stats)
    return out


def gold_intermediates_leak(dump) -> dict:
    """Do any gold-plan literals coincide with the values the plan computes?"""
    out = {}
    for d, rec in dump["items"].items():
        seeds = rec["seeds"]
        n_leak = n = 0
        for gp, seed in zip(rec["gold_plans"], seeds):
            w = dump["worlds"][str(seed)]
            ops = {k: parse_operator(v) for k, v in w["gold"].items()}
            p = parse_plan(gp)
            env, inter = {}, []
            try:
                for s in p.steps:
                    args = [env[a] if isinstance(a, str) and a.startswith("t") else a
                            for a in s.args]
                    v = ops[s.symbol](*args) if s.symbol not in BUILTIN_STEPS \
                        else BUILTIN_STEPS[s.symbol][1](*args)
                    env[s.target] = v
                    inter.append(v)
            except (OpError, KeyError):
                continue
            lits = {a for s in p.steps for a in s.args
                    if isinstance(a, int) and not isinstance(a, bool)}
            n += 1
            # a literal argument that equals a value the plan itself produces
            # would mean the plan hands over work the executor was meant to do
            if lits & set(inter[:-1]):
                n_leak += 1
        out[d] = {"n": n, "plans_whose_literal_matches_an_intermediate": n_leak}
    return out


# ------------------------------------------------------------------- 6.4

def _corrupt(op: Operator, mode: str) -> Operator:
    if mode == "plus_one":
        return Operator(op.symbol, op.params, Call("+", (op.body, 1)),
                        op.pre, op.post, (), op.assoc)
    if mode == "identity":
        from src.opgraph.opdef import Var
        return Operator(op.symbol, op.params, Var(op.params[0]),
                        (), (), (), op.assoc)
    if mode == "constant":
        return Operator(op.symbol, op.params, 0, (), (), (), op.assoc)
    if mode == "flip_assoc":
        return Operator(op.symbol, op.params, op.body, op.pre, op.post,
                        op.examples, "right" if op.assoc == "left" else "left")
    raise ValueError(mode)


def counterfactuals(dump) -> dict:
    modes = ["as_induced", "gold", "plus_one", "identity", "constant", "empty"]
    out = {}
    for d, rec in dump["items"].items():
        row = {}
        for mode in modes:
            ok = 0
            for gp, gold, seed in zip(rec["gold_plans"], rec["gold"], rec["seeds"]):
                w = dump["worlds"][str(seed)]
                if mode == "empty":
                    ops = {}
                elif mode == "gold":
                    ops = {k: parse_operator(v) for k, v in w["gold"].items()}
                else:
                    ops = {k: parse_operator(v) for k, v in w["induced"].items()}
                    if mode != "as_induced":
                        ops = {k: _corrupt(v, mode) for k, v in ops.items()}
                try:
                    v = run_plan(parse_plan(gp), ops)
                except (PlanError, OpError):
                    continue
                ok += _norm(answer_text(v)) == _norm(gold)
            row[mode] = round(ok / len(rec["gold_plans"]), 4)
        out[d] = row
    return out


# ------------------------------------------------------------------- 6.5

def reverse_leak(dump) -> dict:
    out = {}
    for d, rec in dump["items"].items():
        row = {}
        for cond, c in rec["conds"].items():
            st = Counter()
            for plan_text, ok in zip(c["plans"], c["ok"]):
                st["items"] += 1
                st["correct"] += bool(ok)
                try:
                    p = parse_plan(plan_text)
                except PlanError:
                    st["unparsable"] += 1
                    continue
                nop = sum(1 for s in p.steps if s.symbol not in BUILTIN_STEPS)
                nbi = sum(1 for s in p.steps if s.symbol in BUILTIN_STEPS)
                st["operator_calls"] += nop
                st["builtin_calls"] += nbi
                if nop == 0:
                    st["plans_with_no_operator_call"] += 1
                    if ok:
                        st["CORRECT_with_no_operator_call"] += 1
                if nbi:
                    st["plans_using_builtin"] += 1
                    if ok:
                        st["CORRECT_using_builtin"] += 1
                if not p.steps:
                    st["plans_with_zero_steps"] += 1
                    if ok:
                        st["CORRECT_with_zero_steps"] += 1
                if len(p.steps) < int(d) and ok:
                    st["CORRECT_with_plan_shorter_than_depth"] += 1
                st["step_len_%d" % len(p.steps)] += 1
            row[cond] = dict(st)
        out[d] = row
    return out


# ------------------------------------------------------------------- assoc

def assoc_contingency(dump) -> dict:
    """At depths the model can still reach, does its plan track gold assoc?"""
    out = {}
    for d, rec in dump["items"].items():
        if int(d) not in (2, 3):
            continue
        tab = Counter()
        for plan_text, assoc, ok in zip(rec["conds"]["plan_execute"]["plans"],
                                        rec["assoc"], rec["conds"]["plan_execute"]["ok"]):
            try:
                p = parse_plan(plan_text)
            except PlanError:
                tab[(assoc, "unparsable")] += 1
                continue
            if len(p.steps) < 2:
                tab[(assoc, "short")] += 1
                continue
            s2 = p.steps[1]
            first_is_temp = isinstance(s2.args[0], str) and s2.args[0].startswith("t")
            got = "left" if first_is_temp else "right"
            tab[(assoc, got)] += 1
        n = sum(tab.values())
        agree = sum(v for (g, m), v in tab.items() if g == m)
        out[d] = {"n": n, "model_matches_gold_assoc": agree,
                  "rate": round(agree / n, 4) if n else None,
                  "table": {f"gold={a}|model={b}": v for (a, b), v in sorted(tab.items())}}
    return out


def main() -> int:
    path = sys.argv[1]
    dump = load(path)
    out = {
        "source": path,
        "induction": dump.get("induction"),
        "c61_identity": check_identity(dump),
        "c62_gold_plans": check_gold_plans(dump),
        "c62_intermediate_leak": gold_intermediates_leak(dump),
        "c63_prompts": _prompt_summary(dump),
        "c64_counterfactuals": counterfactuals(dump),
        "c65_reverse_leak": reverse_leak(dump),
        "assoc": assoc_contingency(dump),
    }
    dest = sys.argv[2] if len(sys.argv) > 2 else path.replace(".json", "_analysis.json")
    with open(dest, "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps(out["c61_identity"], indent=1))
    print("counterfactuals:", json.dumps(out["c64_counterfactuals"], indent=1))
    print("assoc:", json.dumps(out["assoc"], indent=1))
    print("[written]", dest)
    return 0


def _prompt_summary(dump) -> dict:
    ps = dump.get("prompts") or []
    by = defaultdict(lambda: {"generate_calls": 0, "prompts": 0, "sample": None})
    for p in ps:
        k = str(p.get("cond"))
        by[k]["generate_calls"] += 1
        by[k]["prompts"] += p["n"]
        if by[k]["sample"] is None and p["sample"]:
            by[k]["sample"] = p["sample"][0][:400]
    return dict(by)


if __name__ == "__main__":
    raise SystemExit(main())
