"""Long plans, and plans that use more than two distinct operator symbols.

Reading the plans the model emitted (`commit 20295e2`) found step count
tracking the question to three and then saturating, and novel composition
failing by writing the first operator symbol twice where gold names two.
Operands, ordering and register wiring were correct. Training never showed a
plan past three steps nor one using two distinct symbols, and those are the two
observed ceilings.

Both ceilings are in the training stream, not the machinery.
`src/opgraph/invent.py:_random_tree` takes an arbitrary symbol list and
`src/opgraph/data.py:training_examples` hands it `rng.choice([1, 2, 3])`
applications over a single glyph. This module calls the same constructors with
longer trees and wider symbol pools. It does not modify `src/opgraph/`.

One constraint on the other side. `src/opgraph/plan.py` sets `MAX_STEPS = 32`
and `parse_plan` refuses anything longer, and `src/opgraph/run.py` sets
`MAX_PLAN_STEPS = 24` for the stepwise scheduler. Plans longer than 32 steps
serialize correctly and execute correctly, and `parse_plan` will reject them
until that constant is raised. `verify_roundtrip` below reports exactly which
lengths the shipped parser accepts, so the corpus does not silently contain
items the eval harness cannot read.
"""

from __future__ import annotations

import random

from src.opgraph.invent import make_world
from src.opgraph.plan import (BUILTIN_STEPS, MAX_STEPS, Plan, PlanError, Step,
                              parse_plan, run_plan, serialize_plan)

VALUE_BOUND = 10 ** 9

# add, sub and mul are callable in every world. They widen the symbol pool
# without inventing anything the executor does not already accept.
BUILTIN_FNS = {
    "add": lambda a, b: a + b,
    "sub": lambda a, b: a - b,
    "mul": lambda a, b: a * b,
}

PLAN_QUESTION_FRAMES = {
    "evaluate": "Evaluate {expr}.",
    "value_of": "What is the value of {expr}?",
    "compute": "Compute {expr} and give the result.",
    "cloze": "{expr} = ____. Give the missing number.",
    "imperative": "Give the value that {expr} takes.",
    "inverted": "For {expr}: what value?",
}


def numeric_ops(world) -> dict:
    """Operators that take integers and return an integer, plus the builtins.

    Probed rather than assumed: a world's procedure page can define an operator
    that returns a label, and mixing one of those into an arithmetic tree makes
    a question with no numeric answer.
    """
    out = {}
    for sym, op in world.ops.items():
        try:
            probe = [3] * op.arity
            v = op(*probe)
        except Exception:
            continue
        if isinstance(v, bool) or not isinstance(v, int):
            continue
        out[sym] = op
    for sym, fn in BUILTIN_FNS.items():
        out[sym] = fn
    return out


def _arity(sym, ops) -> int:
    if sym in BUILTIN_STEPS:
        return BUILTIN_STEPS[sym][0]
    return ops[sym].arity


def _leaf(rng) -> int:
    return rng.randint(1, 12)


def build_tree(rng, n_steps: int, symbols, ops):
    """A tree with exactly `n_steps` applications, using every symbol given.

    Grown by grafting an application onto a uniformly chosen integer leaf,
    which is `src/opgraph/invent.py:_graft`'s rule generalised to mixed arity.
    The symbol order is shuffled so that the first `len(symbols)` grafts use
    each symbol once, after which symbols are drawn at random; that guarantees
    the realised distinct symbol count is the requested one when
    `n_steps >= len(symbols)`.
    """
    order = list(symbols)
    rng.shuffle(order)
    forced = list(order)

    def new_node(sym):
        return (sym, [_leaf(rng) for _ in range(_arity(sym, ops))])

    sym0 = forced.pop(0) if forced else rng.choice(symbols)
    node = new_node(sym0)
    for _ in range(n_steps - 1):
        sym = forced.pop(0) if forced else rng.choice(symbols)
        node = _graft_leaf(node, rng, new_node(sym))
    return node


def _graft_leaf(node, rng, new):
    leaves = []

    def walk(nd, path):
        if isinstance(nd, int):
            leaves.append(tuple(path))
            return
        for i, k in enumerate(nd[1]):
            walk(k, path + [i])

    walk(node, [])
    target = rng.choice(leaves)

    def rebuild(nd, path, idx):
        if idx == len(path):
            return new
        sym, kids = nd
        kids = list(kids)
        kids[path[idx]] = rebuild(kids[path[idx]], path, idx + 1)
        return (sym, kids)

    return rebuild(node, target, 0)


def eval_tree(node, ops):
    if isinstance(node, int):
        return node
    sym, kids = node
    vals = [eval_tree(k, ops) for k in kids]
    for v in vals:
        if abs(v) > VALUE_BOUND:
            raise OverflowError("intermediate out of bounds")
    v = ops[sym](*vals)
    if abs(v) > VALUE_BOUND:
        raise OverflowError("value out of bounds")
    return v


def render_tree(node, top: bool = True) -> str:
    if isinstance(node, int):
        return str(node)
    sym, kids = node
    if len(kids) == 1:
        return f"{sym}({render_tree(kids[0], True)})"
    inner = " ".join(
        [render_tree(kids[0], False), sym, render_tree(kids[1], False)])
    return inner if top else f"({inner})"


def steps_from_tree(node, counter, steps):
    if isinstance(node, int):
        return node
    sym, kids = node
    args = [steps_from_tree(k, counter, steps) for k in kids]
    counter[0] += 1
    t = f"t{counter[0]}"
    steps.append(Step(t, sym, tuple(args)))
    return t


def plan_for(tree) -> Plan:
    steps: list = []
    last = steps_from_tree(tree, [0], steps)
    return Plan(tuple(steps), str(last))


def symbols_in(node) -> set:
    if isinstance(node, int):
        return set()
    sym, kids = node
    out = {sym}
    for k in kids:
        out |= symbols_in(k)
    return out


def leaves_in(node) -> list:
    if isinstance(node, int):
        return [node]
    out = []
    for k in node[1]:
        out.extend(leaves_in(k))
    return out


def intermediates(plan, ops) -> list:
    env = {}
    vals = []
    for s in plan.steps:
        args = [env[a] if isinstance(a, str) else a for a in s.args]
        v = ops[s.symbol](*args)
        env[s.target] = v
        vals.append(v)
    return vals


REJECT_REASONS = ("execute", "answer_in_prompt", "answer_is_intermediate",
                  "answer_is_leaf", "symbol_count", "value_bound")


def plan_item(seed: int, n_steps: int, n_symbols: int, qframe: str,
              rng: random.Random, breadth: int = 3, tries: int = 40):
    """One plan item, or (None, reason) when every attempt was rejected.

    The exclusions are the project's necessity checks written for this task:
    the gold value must not appear in the question text, must not be one of the
    literals the question hands over, and must not equal an intermediate the
    plan passes through, so a model that stops early or echoes an operand
    cannot score.
    """
    world = make_world(seed, breadth=breadth)
    ops = numeric_ops(world)
    pool = sorted(ops)
    if len(pool) < n_symbols:
        return None, "symbol_count"
    counts = {r: 0 for r in REJECT_REASONS}
    for _ in range(tries):
        syms = rng.sample(pool, n_symbols)
        try:
            tree = build_tree(rng, n_steps, syms, ops)
        except Exception:
            counts["execute"] += 1
            continue
        if len(symbols_in(tree)) != n_symbols:
            counts["symbol_count"] += 1
            continue
        try:
            gold = eval_tree(tree, ops)
        except OverflowError:
            counts["value_bound"] += 1
            continue
        except Exception:
            counts["execute"] += 1
            continue
        plan = plan_for(tree)
        try:
            mids = intermediates(plan, ops)
        except Exception:
            counts["execute"] += 1
            continue
        expr = render_tree(tree)
        text = PLAN_QUESTION_FRAMES[qframe].format(expr=expr)
        if str(gold) in expr.split():
            counts["answer_in_prompt"] += 1
            continue
        if gold in leaves_in(tree):
            counts["answer_is_leaf"] += 1
            continue
        if gold in mids[:-1]:
            counts["answer_is_intermediate"] += 1
            continue
        return {
            "world": world,
            "ops": ops,
            "seed": seed,
            "n_steps": n_steps,
            "n_symbols": n_symbols,
            "symbols": sorted(symbols_in(tree)),
            "qframe": qframe,
            "text": text,
            "gold": str(gold),
            "plan": plan,
            "plan_text": serialize_plan(plan),
            "intermediates": [str(v) for v in mids],
            "rejects": counts,
        }, None
    return None, counts


def verify_roundtrip(plan_text: str, ops) -> dict:
    """What the shipped parser and executor make of a plan this module wrote.

    Reported per length so the manifest can state exactly which plans the eval
    harness can read today and which need `src/opgraph/plan.py:MAX_STEPS`
    raised first.
    """
    n = len([c for c in plan_text.split(";") if c.strip()]) - 1
    out = {"n_steps": n, "parses": False, "runs": False, "value": None,
           "max_steps": MAX_STEPS}
    try:
        p = parse_plan(plan_text)
        out["parses"] = True
    except PlanError as exc:
        out["error"] = str(exc)
        return out
    try:
        out["value"] = str(run_plan(p, {k: v for k, v in ops.items()
                                        if k not in BUILTIN_STEPS}))
        out["runs"] = True
    except Exception as exc:  # noqa: BLE001
        out["error"] = str(exc)
    return out
