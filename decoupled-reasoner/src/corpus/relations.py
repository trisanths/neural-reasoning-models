"""Relation structures, with no prose in them.

Three relation families were trained (`substitution_rule`, `threshold_rule`,
`exception_rule`) and three untrained ones were measured at or below chance
(`inverse_table` 0.107 against 0.251, `chain_rule` 0.008 against 0.334,
`band_rule` 0.313 against 0.334, `src/falsify/probe.py`). Widening that axis
means training on many relation structures rather than three.

A structure here emits facts and questions as records, never as sentences. A
frame in `src/corpus/frames.py` turns the records into English. Keeping the two
apart is what lets the same seed produce the same gold answer under every
frame, which is the parity check the corpus reports.

Every question carries `stages`, the intermediate values in order with the
starting value first and the answer last, so the necessity audit runs the same
way on every structure.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

# ------------------------------------------------------------------- records


@dataclass
class Fact:
    """One statement a page can make.

    kind is one of:
      assoc    scope, key -> value
      assoc2   scope, (key_a, key_b) -> value
      band     scope, attr, lo, hi -> label, lo None meaning unbounded below
      default  scope -> value for anything not listed
      general  scope -> value for everything unless excepted
      except_  scope, key -> value, overriding the general
      weight   scope, key -> integer
      step     scope, an arithmetic rule applied to a number
    """

    kind: str
    scope: str
    key: object = None
    value: object = None
    lo: object = None
    hi: object = None
    attr: object = None
    rank: int = 0


@dataclass
class Question:
    """One item, with the plan that produces it and the values it passes."""

    qid: str
    kind: str
    scopes: list
    start: object
    answer: object
    stages: list
    plan: list
    attr: object = None
    key_b: object = None
    meta: dict = field(default_factory=dict)


@dataclass
class Instance:
    """One relation instance: its pages of facts and its questions."""

    family: str
    name: str
    pages: list          # list of (scope, [Fact]) in page order
    questions: list      # list[Question]
    candidates: list     # every answer the family can emit for this instance
    numeric: bool = False


def plan_ops(plan) -> list:
    return [s["op"] for s in plan]


def n_distinct_ops(plan) -> int:
    return len(set(plan_ops(plan)))


def _step(op, scope, arg, out):
    return {"op": op, "scope": scope, "arg": arg, "out": out}


# ----------------------------------------------------------------- structures
#
# Each builder takes (rng, lex, **shape) and returns an Instance. `lex` is a
# src.corpus.lexicon.Lexicon already bound to one frame's reserved words.


def substitution(rng, lex, n_keys=4, n_problems=6):
    """A stated mapping applied to a new item. One of the three trained."""
    name = lex.name()
    keys = lex.words(n_keys)
    values = lex.words(n_keys)
    fallback = lex.word()
    facts = [Fact("assoc", name, k, v) for k, v in zip(keys, values)]
    facts.append(Fact("default", name, value=fallback))
    qs = []
    for i in range(n_problems):
        if rng.random() < 0.8:
            j = rng.randrange(n_keys)
            k, a = keys[j], values[j]
        else:
            k, a = lex.word(), fallback
        qs.append(Question(f"q{i}", "lookup", [name], k, a, [k, a],
                           [_step("lookup", name, k, a)]))
    return Instance("substitution", name, [(name, facts)], qs,
                    list(values) + [fallback])


def exception_rule(rng, lex, n_problems=6):
    """A general rule plus one stated exception. One of the three trained."""
    name = lex.name()
    general = lex.word()
    special_key = lex.word()
    special = lex.word()
    facts = [Fact("general", name, value=general),
             Fact("except_", name, key=special_key, value=special)]
    qs = []
    for i in range(n_problems):
        if rng.random() < 0.5:
            cat, a = special_key, special
        else:
            cat, a = lex.word(), general
        qs.append(Question(f"q{i}", "lookup_general", [name], cat, a, [cat, a],
                           [_step("lookup", name, cat, a)]))
    return Instance("exception_rule", name, [(name, facts)], qs,
                    [general, special])


def threshold(rng, lex, n_problems=6):
    """Two bands about one stated limit. One of the three trained."""
    return _bands(rng, lex, 2, n_problems, "threshold")


def band_rule(rng, lex, n_problems=6, n_bands=3):
    """Three or more bands. Measured at 0.313 against a 0.334 floor."""
    return _bands(rng, lex, n_bands, n_problems, "band_rule")


def _bands(rng, lex, n_bands, n_problems, family):
    """Bands whose labels are equally likely.

    The band index is drawn uniformly and the reading is then drawn inside that
    band, rather than the reading being drawn uniformly over the whole range.
    The two differ: the bands are not equally wide, so a uniform reading makes
    the widest band's label the modal answer and a constant predictor beats the
    uniform floor. That would put a value blind reader above chance for a
    reason that has nothing to do with the task.
    """
    name = lex.name()
    attr = lex.word()
    labels = lex.words(n_bands)
    cuts = []
    v = rng.choice([25, 30, 35, 40])
    for _ in range(n_bands - 1):
        cuts.append(v)
        v += rng.choice([25, 30, 35])
    top = cuts[-1] + rng.choice([25, 30, 35])
    facts = []
    edges = [None] + cuts + [None]
    for i, label in enumerate(labels):
        facts.append(Fact("band", name, attr=attr, lo=edges[i], hi=edges[i + 1],
                          value=label, rank=i))
    lows = [1] + [c + 3 for c in cuts]
    highs = [c - 3 for c in cuts] + [top]
    qs = []
    for i in range(n_problems):
        idx = rng.randrange(n_bands)
        if highs[idx] < lows[idx]:
            continue
        reading = rng.randint(lows[idx], highs[idx])
        a = labels[idx]
        qs.append(Question(f"q{i}", "classify", [name], reading, a,
                           [reading, a],
                           [_step("band", name, reading, a)], attr=attr))
    return Instance(family, name, [(name, facts)], qs, list(labels))


def inverse_table(rng, lex, n_keys=4, n_problems=6):
    """The table read backwards. Measured at 0.107 against a 0.251 floor."""
    name = lex.name()
    keys = lex.words(n_keys)
    values = lex.words(n_keys)
    facts = [Fact("assoc", name, k, v) for k, v in zip(keys, values)]
    qs = []
    for i in range(n_problems):
        j = rng.randrange(n_keys)
        qs.append(Question(f"q{i}", "inverse", [name], values[j], keys[j],
                           [values[j], keys[j]],
                           [_step("invert", name, values[j], keys[j])]))
    return Instance("inverse_table", name, [(name, facts)], qs, list(keys))


def chain_rule(rng, lex, depth=2, width=4, n_problems=6):
    """`depth` stated hops, each on its own page. Measured at 0.008 (depth 2).

    Levels are typed: stage i maps level i to level i+1, so a token is a source
    on exactly one page and a target on at most one other, and the only thing
    depth adds is that the key to hop i comes from hop i-1.
    """
    name = lex.name()
    levels = [lex.words(width) for _ in range(depth + 1)]
    scopes = [lex.name() for _ in range(depth)]
    pages = []
    maps = []
    for i in range(depth):
        dst = list(levels[i + 1])
        rng.shuffle(dst)
        m = dict(zip(levels[i], dst))
        maps.append(m)
        pages.append((scopes[i], [Fact("assoc", scopes[i], k, m[k])
                                  for k in levels[i]]))
    qs = []
    starts = list(levels[0])
    rng.shuffle(starts)
    for i, s in enumerate(starts[:n_problems]):
        stages = [s]
        plan = []
        cur = s
        for d in range(depth):
            nxt = maps[d][cur]
            plan.append(_step("lookup", scopes[d], cur, nxt))
            stages.append(nxt)
            cur = nxt
        qs.append(Question(f"q{i}", "compose", scopes, s, cur, stages, plan))
    return Instance("chain_rule", name, pages, qs, list(levels[-1]))


def inverse_chain(rng, lex, depth=2, width=4, n_problems=6):
    """A composed chain read backwards: given the last value, name the first."""
    inst = chain_rule(rng, lex, depth=depth, width=width, n_problems=n_problems)
    qs = []
    for i, q in enumerate(inst.questions):
        rev = list(reversed(q.stages))
        plan = [_step("invert", s["scope"], s["out"], s["arg"])
                for s in reversed(q.plan)]
        qs.append(Question(f"q{i}", "invert_chain", list(reversed(q.scopes)),
                           q.answer, q.start, rev, plan))
    starts = [q.answer for q in qs]
    return Instance("inverse_chain", inst.name, inst.pages, qs, starts)


def transitive(rng, lex, depth=3, width=6, n_problems=6):
    """One stated graph, applied `depth` times.

    Unlike `chain_rule` the hops all live on one page, so the page does not
    tell the reader which step it is on, and the question names one scope
    however long the walk is. That is what makes this the vehicle for long
    plans: the plan is `depth` steps while the prompt stays the length of a
    depth one question, so plan length is varied without varying prompt length
    with it.

    The node set is widened to `depth + 2` so a walk of `depth` steps over a
    derangement cannot return to a node it has already visited, which keeps the
    stopped-early diagnostic unambiguous.
    """
    width = max(width, depth + 2)
    name = lex.name()
    nodes = lex.words(width)
    # A single cycle of length `width` rather than an arbitrary derangement:
    # a random derangement can contain a short cycle, and a walk that re-enters
    # one would revisit a node before `depth` steps are up.
    ring = list(nodes)
    rng.shuffle(ring)
    m = {ring[i]: ring[(i + 1) % width] for i in range(width)}
    facts = [Fact("assoc", name, k, m[k]) for k in nodes]
    qs = []
    order = list(nodes)
    rng.shuffle(order)
    for i, s in enumerate(order[:n_problems]):
        stages = [s]
        plan = []
        cur = s
        for _ in range(depth):
            nxt = m[cur]
            plan.append(_step("lookup", name, cur, nxt))
            stages.append(nxt)
            cur = nxt
        qs.append(Question(f"q{i}", "iterate", [name], s, cur, stages, plan,
                           meta={"n_applications": depth}))
    return Instance("transitive", name, [(name, facts)], qs, list(nodes))


def two_key(rng, lex, n_rows=3, n_cols=3, n_problems=6):
    """A grid: the answer needs both coordinates, not one."""
    name = lex.name()
    rows = lex.words(n_rows)
    cols = lex.words(n_cols)
    cells = {}
    vals = lex.words(n_rows * n_cols)
    t = 0
    facts = []
    for r in rows:
        for c in cols:
            cells[(r, c)] = vals[t]
            facts.append(Fact("assoc2", name, (r, c), vals[t]))
            t += 1
    qs = []
    for i in range(n_problems):
        r = rng.choice(rows)
        c = rng.choice(cols)
        a = cells[(r, c)]
        qs.append(Question(f"q{i}", "pair", [name], r, a, [r, a],
                           [_step("pair", name, (r, c), a)], key_b=c))
    return Instance("two_key", name, [(name, facts)], qs, list(vals))


def priority_list(rng, lex, n_rules=4, n_problems=6):
    """Ordered rules where the first match wins and later rules also match.

    Every item satisfies at least two rules; the stated precedence decides. A
    reader that takes the last matching line rather than the first is wrong on
    every item, which the shortcut audit scores.
    """
    name = lex.name()
    groups = lex.words(n_rules)
    values = lex.words(n_rules)
    facts = [Fact("assoc", name, g, v, rank=i)
             for i, (g, v) in enumerate(zip(groups, values))]
    facts.append(Fact("default", name, value=values[0], rank=n_rules))
    qs = []
    for i in range(n_problems):
        hits = sorted(rng.sample(range(n_rules), rng.choice([2, 2, 3])))
        first = hits[0]
        memb = [groups[h] for h in hits]
        qs.append(Question(f"q{i}", "priority", [name], tuple(memb),
                           values[first], [memb[0], values[first]],
                           [_step("priority", name, tuple(memb), values[first])],
                           meta={"matches": memb,
                                 "last_match": values[hits[-1]]}))
    return Instance("priority_list", name, [(name, facts)], qs, list(values))


def exclusion(rng, lex, n_keys=4, n_problems=6):
    """Which listed key is the one that does not map to the named value."""
    name = lex.name()
    keys = lex.words(n_keys)
    values = lex.words(2)
    assign = {}
    for k in keys:
        assign[k] = values[0]
    odd = rng.choice(keys)
    assign[odd] = values[1]
    facts = [Fact("assoc", name, k, assign[k]) for k in keys]
    qs = []
    for i in range(n_problems):
        qs.append(Question(f"q{i}", "exclusion", [name], values[0], odd,
                           [values[0], odd],
                           [_step("exclude", name, values[0], odd)]))
    return Instance("exclusion", name, [(name, facts)], qs, list(keys))


def lookup_then_band(rng, lex, n_keys=6, n_bands=3, n_problems=6):
    """A key gives a number; the number is then classified by stated bands.

    Two distinct operations in one plan, which is the two symbol case. The keys
    are spread evenly over the bands so that drawing a key uniformly draws a
    label uniformly, for the same reason `_bands` draws the band first.
    """
    name = lex.name()
    scope_a = lex.name()
    scope_b = lex.name()
    keys = lex.words(n_keys)
    labels = lex.words(n_bands)
    cuts = []
    v = rng.choice([25, 30, 35, 40])
    for _ in range(n_bands - 1):
        cuts.append(v)
        v += rng.choice([25, 30, 35])
    top = cuts[-1] + rng.choice([25, 30, 35])
    lows = [1] + [c + 3 for c in cuts]
    highs = [c - 3 for c in cuts] + [top]
    weights, bands = [], []
    for j in range(n_keys):
        idx = j % n_bands
        bands.append(idx)
        weights.append(rng.randint(lows[idx], max(lows[idx], highs[idx])))
    facts_a = [Fact("weight", scope_a, k, w) for k, w in zip(keys, weights)]
    edges = [None] + cuts + [None]
    facts_b = [Fact("band", scope_b, attr=scope_a, lo=edges[i], hi=edges[i + 1],
                    value=labels[i], rank=i) for i in range(n_bands)]
    qs = []
    for i in range(n_problems):
        j = rng.randrange(n_keys)
        k, w, a = keys[j], weights[j], labels[bands[j]]
        qs.append(Question(f"q{i}", "lookup_then_band", [scope_a, scope_b], k,
                           a, [k, w, a],
                           [_step("weigh", scope_a, k, w),
                            _step("band", scope_b, w, a)], attr=scope_a))
    return Instance("lookup_then_band", name,
                    [(scope_a, facts_a), (scope_b, facts_b)], qs, list(labels))


def band_then_lookup(rng, lex, n_bands=3, n_problems=6):
    """A reading gives a label; the label is then looked up in a second table.

    The band index is drawn uniformly, as in `_bands`.
    """
    name = lex.name()
    scope_a = lex.name()
    scope_b = lex.name()
    attr = lex.word()
    labels = lex.words(n_bands)
    values = lex.words(n_bands)
    cuts = []
    v = rng.choice([25, 30, 35, 40])
    for _ in range(n_bands - 1):
        cuts.append(v)
        v += rng.choice([25, 30, 35])
    top = cuts[-1] + rng.choice([25, 30, 35])
    lows = [1] + [c + 3 for c in cuts]
    highs = [c - 3 for c in cuts] + [top]
    edges = [None] + cuts + [None]
    facts_a = [Fact("band", scope_a, attr=attr, lo=edges[i], hi=edges[i + 1],
                    value=labels[i], rank=i) for i in range(n_bands)]
    facts_b = [Fact("assoc", scope_b, l, v) for l, v in zip(labels, values)]
    qs = []
    for i in range(n_problems):
        idx = rng.randrange(n_bands)
        if highs[idx] < lows[idx]:
            continue
        reading = rng.randint(lows[idx], highs[idx])
        lab, a = labels[idx], values[idx]
        qs.append(Question(f"q{i}", "band_then_lookup", [scope_a, scope_b],
                           reading, a, [reading, lab, a],
                           [_step("band", scope_a, reading, lab),
                            _step("lookup", scope_b, lab, a)], attr=attr))
    return Instance("band_then_lookup", name,
                    [(scope_a, facts_a), (scope_b, facts_b)], qs, list(values))


def weighted_chain(rng, lex, depth=3, width=4, n_problems=6):
    """Walk a chain and add the stated weights. The answer is a number.

    The total appears on no page, so `answer_source` for this family is
    derived by computation rather than stated in a chapter.
    """
    name = lex.name()
    levels = [lex.words(width) for _ in range(depth + 1)]
    scopes = [lex.name() for _ in range(depth)]
    pages = []
    maps, wts = [], []
    for i in range(depth):
        dst = list(levels[i + 1])
        rng.shuffle(dst)
        m = dict(zip(levels[i], dst))
        w = {k: rng.randint(2, 40) for k in levels[i]}
        maps.append(m)
        wts.append(w)
        facts = []
        for k in levels[i]:
            facts.append(Fact("assoc", scopes[i], k, m[k]))
            facts.append(Fact("weight", scopes[i], k, w[k]))
        pages.append((scopes[i], facts))
    qs = []
    starts = list(levels[0])
    rng.shuffle(starts)
    for i, s in enumerate(starts[:n_problems]):
        stages = [s]
        plan = []
        cur, total = s, 0
        for d in range(depth):
            total += wts[d][cur]
            nxt = maps[d][cur]
            plan.append(_step("accumulate", scopes[d], cur, total))
            plan.append(_step("lookup", scopes[d], cur, nxt))
            stages.append(nxt)
            cur = nxt
        stages.append(total)
        qs.append(Question(f"q{i}", "sum_chain", scopes, s, total, stages, plan))
    return Instance("weighted_chain", name, pages, qs, [], numeric=True)


def modular_apply(rng, lex, depth=3, n_problems=6):
    """A stated arithmetic step applied `depth` times. The answer is a number."""
    name = lex.name()
    scope = lex.name()
    a = rng.choice([2, 3, 4, 5])
    b = rng.choice([1, 3, 7, 9, 11])
    mod = rng.choice([97, 101, 199, 251])
    facts = [Fact("step", scope, key=("affine", a, b, mod), value=None)]
    qs = []
    for i in range(n_problems):
        x = rng.randint(2, mod - 2)
        stages = [x]
        plan = []
        cur = x
        for _ in range(depth):
            cur = (a * cur + b) % mod
            plan.append(_step("apply", scope, cur, cur))
            stages.append(cur)
        qs.append(Question(f"q{i}", "apply_n", [scope], x, cur, stages, plan,
                           meta={"a": a, "b": b, "mod": mod,
                                 "n_applications": depth}))
    return Instance("modular_apply", name, [(scope, facts)], qs, [], numeric=True)


def agreement(rng, lex, n_keys=4, n_problems=6):
    """Two tables disagree and a stated precedence rule says which one wins.

    A reader that takes the nearest matching line is right half the time by
    construction, which the shortcut audit scores directly.
    """
    name = lex.name()
    primary = lex.name()
    secondary = lex.name()
    keys = lex.words(n_keys)
    good = lex.words(n_keys)
    bad = lex.words(n_keys)
    facts_p = [Fact("assoc", primary, k, v) for k, v in zip(keys, good)]
    facts_s = [Fact("assoc", secondary, k, v) for k, v in zip(keys, bad)]
    qs = []
    for i in range(n_problems):
        j = rng.randrange(n_keys)
        qs.append(Question(f"q{i}", "precedence", [primary, secondary], keys[j],
                           good[j], [keys[j], good[j]],
                           [_step("select", primary, keys[j], good[j])],
                           meta={"loser": bad[j]}))
    return Instance("agreement", name,
                    [(primary, facts_p), (secondary, facts_s)], qs,
                    list(good) + list(bad))


# The registry. `depth` structures accept a depth argument and carry the plan
# length axis; the rest are depth one.
STRUCTURES = {
    "substitution": substitution,
    "exception_rule": exception_rule,
    "threshold": threshold,
    "band_rule": band_rule,
    "inverse_table": inverse_table,
    "chain_rule": chain_rule,
    "inverse_chain": inverse_chain,
    "transitive": transitive,
    "two_key": two_key,
    "priority_list": priority_list,
    "exclusion": exclusion,
    "lookup_then_band": lookup_then_band,
    "band_then_lookup": band_then_lookup,
    "weighted_chain": weighted_chain,
    "modular_apply": modular_apply,
    "agreement": agreement,
}

DEPTH_STRUCTURES = ("chain_rule", "inverse_chain", "transitive",
                    "weighted_chain", "modular_apply")

TRAINED_BEFORE = ("substitution", "threshold", "exception_rule")
MEASURED_FAILURES = ("inverse_table", "chain_rule", "band_rule")
NUMERIC_STRUCTURES = ("weighted_chain", "modular_apply")
