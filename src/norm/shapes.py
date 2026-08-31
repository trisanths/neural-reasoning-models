"""The canonical program for each shape the frame grammar can write.

One constructor, used by the generator, by the parser and by the tests. If the
generator built a plan one way and the parser rebuilt it another, the round
trip would fail for a reason that has nothing to do with the text, so neither
of them is allowed its own copy of this.

Temporary names are part of the canonical form: `x` and `y` are the inputs,
`t1..tn` are the steps of a straight chain, and the sum chain uses `w`, `c` and
`s` for the weight read, the hop and the running total.
"""

from __future__ import annotations

from src.norm.lang import Lit, NormError, Program, Ref, Step


def assemble(shape: str, *, tables=(), bands=None, rule=None, weights=(),
             affine=None, inputs=(), n: int = 1) -> Program:
    tables = tuple(tables)
    weights = tuple(weights)
    inputs = tuple(inputs)
    first_in = inputs[0][0] if inputs else "x"

    if shape == "lookup":
        defs = tables
        steps = (Step("t1", "lookup", (tables[0].name, Ref(first_in))),)
        ans = "t1"
    elif shape == "lookup_general":
        defs = (rule,)
        steps = (Step("t1", "rule", (rule.name, Ref(first_in))),)
        ans = "t1"
    elif shape == "classify":
        defs = (bands,)
        steps = (Step("t1", "band", (bands.name, Ref(first_in))),)
        ans = "t1"
    elif shape == "inverse":
        defs = tables
        steps = (Step("t1", "invert", (tables[0].name, Ref(first_in))),)
        ans = "t1"
    elif shape == "exclusion":
        defs = tables
        steps = (Step("t1", "odd_one_out", (tables[0].name, Ref(first_in))),)
        ans = "t1"
    elif shape == "priority":
        defs = tables
        steps = (Step("t1", "lookup_ordered", (tables[0].name, Ref(first_in))),)
        ans = "t1"
    elif shape == "pair":
        defs = tables
        steps = (Step("t1", "lookup",
                      (tables[0].name, Ref(inputs[0][0]), Ref(inputs[1][0]))),)
        ans = "t1"
    elif shape == "precedence":
        defs = tables
        steps = (Step("t1", "prefer",
                      (tables[0].name, tables[1].name, Ref(first_in))),)
        ans = "t1"
    elif shape == "compose":
        defs = tables
        steps = []
        prev = first_in
        for i, t in enumerate(tables, start=1):
            steps.append(Step(f"t{i}", "lookup", (t.name, Ref(prev))))
            prev = f"t{i}"
        steps = tuple(steps)
        ans = prev
    elif shape == "iterate":
        defs = tables
        steps = []
        prev = first_in
        for i in range(1, n + 1):
            steps.append(Step(f"t{i}", "lookup", (tables[0].name, Ref(prev))))
            prev = f"t{i}"
        steps = tuple(steps)
        ans = prev
    elif shape == "apply_n":
        defs = (affine,)
        steps = []
        prev = first_in
        for i in range(1, n + 1):
            steps.append(Step(f"t{i}", "step", (affine.name, Ref(prev))))
            prev = f"t{i}"
        steps = tuple(steps)
        ans = prev
    elif shape == "lookup_then_band":
        defs = (weights[0], bands)
        steps = (Step("t1", "weigh", (weights[0].name, Ref(first_in))),
                 Step("t2", "band", (bands.name, Ref("t1"))))
        ans = "t2"
    elif shape == "band_then_lookup":
        defs = (bands, tables[0])
        steps = (Step("t1", "band", (bands.name, Ref(first_in))),
                 Step("t2", "lookup", (tables[0].name, Ref("t1"))))
        ans = "t2"
    elif shape == "sum_chain":
        defs = []
        for t, w in zip(tables, weights):
            defs.extend([t, w])
        defs = tuple(defs)
        steps = []
        prev = first_in
        acc = None
        for i, (t, w) in enumerate(zip(tables, weights), start=1):
            steps.append(Step(f"w{i}", "weigh", (w.name, Ref(prev))))
            if acc is None:
                acc = f"w{i}"
            else:
                steps.append(Step(f"s{i}", "add",
                                  (Ref(acc), Ref(f"w{i}"))))
                acc = f"s{i}"
            steps.append(Step(f"c{i}", "lookup", (t.name, Ref(prev))))
            prev = f"c{i}"
        steps = tuple(steps)
        ans = acc
    else:
        raise NormError(f"no canonical program for shape {shape!r}")
    return Program(tuple(defs), inputs, steps, ans)
