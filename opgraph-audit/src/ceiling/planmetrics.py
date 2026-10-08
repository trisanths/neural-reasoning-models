"""What an emitted plan got right, step by step, beside the gold plan.

Answer accuracy hides the measurement this experiment needs. The ceiling is
visible in the plan the model wrote: how many steps it has, how many distinct
operator symbols it names, and whether the parts that were already correct at
depth three stay correct as depth grows.

The failure seen at novel depth two was a plan with the right operands in the
right order wired through the right temporaries, naming the first operator
symbol twice where the gold plan names two. `shape_match` is what isolates
that: the emitted plan is inlined into an expression tree, the operator
symbols are erased, and the remaining structure is compared to gold. A plan
that is shape-correct and symbol-wrong is a symbol failure and nothing else.
"""

from __future__ import annotations

from src.opgraph.plan import (BUILTIN_STEPS, PlanError, Plan, parse_plan,
                              serialize_plan)

_TEMP = lambda a: isinstance(a, str) and a.startswith("t") and a[1:].isdigit()  # noqa: E731


def tree_of(plan: Plan):
    """The plan inlined into an expression tree rooted at its answer.

    A temporary read twice duplicates its subtree, which is what a comparison
    against a gold tree wants. Steps the answer does not depend on are dropped
    and counted separately as dead steps.
    """
    by_target = {s.target: s for s in plan.steps}

    def build(node, seen):
        if _TEMP(node):
            if node not in by_target or node in seen:
                return ("?", [])
            s = by_target[node]
            return (s.symbol, [build(a, seen | {node}) for a in s.args])
        return node

    return build(plan.answer, set())


def _erase(node):
    if isinstance(node, tuple) and len(node) == 2 and isinstance(node[1], list):
        return ("*", [_erase(k) for k in node[1]])
    return node


def shape_of(node):
    """The tree with every operator symbol replaced by one placeholder."""
    return _erase(node)


def symbols_of(node) -> list:
    """Operator symbols in the inlined tree, in pre-order."""
    out: list = []
    if isinstance(node, tuple) and len(node) == 2 and isinstance(node[1], list):
        out.append(node[0])
        for k in node[1]:
            out.extend(symbols_of(k))
    return out


def literals_of(node) -> list:
    out: list = []
    if isinstance(node, tuple) and len(node) == 2 and isinstance(node[1], list):
        for k in node[1]:
            out.extend(literals_of(k))
    else:
        out.append(node)
    return out


def reachable(plan: Plan) -> set:
    by_target = {s.target: s for s in plan.steps}
    seen: set = set()
    stack = [plan.answer] if _TEMP(plan.answer) else []
    while stack:
        t = stack.pop()
        if t in seen or t not in by_target:
            continue
        seen.add(t)
        for a in by_target[t].args:
            if _TEMP(a):
                stack.append(a)
    return seen


def well_typed(plan: Plan, ops: dict) -> bool:
    """Every symbol is known and every arity matches the table it plans over."""
    for s in plan.steps:
        if s.symbol in BUILTIN_STEPS:
            if len(s.args) != BUILTIN_STEPS[s.symbol][0]:
                return False
            continue
        op = ops.get(s.symbol)
        if op is None or op.arity != len(s.args):
            return False
    return True


def measure(text: str, gold: Plan, ops: dict) -> dict:
    """Everything worth recording about one emitted plan.

    `ops` is the table the plan was written against: the induced operators
    when the model induced them, the gold operators under the ops oracle. It
    decides only whether the plan is well typed and runnable, never whether
    it is structurally right.
    """
    gold_tree = tree_of(gold)
    rec: dict = {
        "emitted": text,
        "req_steps": len(gold.steps),
        "req_symbols": len({s.symbol for s in gold.steps}),
        "parse_ok": False,
        "empty": not text.strip(),
    }
    try:
        plan = parse_plan(text)
    except PlanError as exc:
        rec["parse_error"] = str(exc)[:120]
        return rec
    tree = tree_of(plan)
    live = reachable(plan)
    syms = [s.symbol for s in plan.steps]
    rec.update({
        "parse_ok": True,
        "steps": len(plan.steps),
        "live_steps": len(live),
        "dead_steps": len(plan.steps) - len(live),
        "symbols": sorted(set(syms)),
        "n_symbols": len(set(syms)),
        "builtins": sum(1 for s in syms if s in BUILTIN_STEPS),
        "well_typed": well_typed(plan, ops),
        "exact_gold": serialize_plan(plan) == serialize_plan(gold),
        "shape_match": shape_of(tree) == shape_of(gold_tree),
        "operands_match": sorted(map(str, literals_of(tree)))
                          == sorted(map(str, literals_of(gold_tree))),
        "symbol_seq_match": symbols_of(tree) == symbols_of(gold_tree),
    })
    # The signature of the observed novel-composition failure: structure right,
    # symbols collapsed onto fewer distinct names than the question needs.
    rec["symbol_collapse"] = bool(rec["shape_match"]
                                  and not rec["symbol_seq_match"]
                                  and rec["n_symbols"] < rec["req_symbols"])
    return rec
