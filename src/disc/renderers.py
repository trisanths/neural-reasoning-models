"""Surface-form renderers over fixed tasks, for the template ablation.

The composition repro and the simple rule families each carry one wording. That
wording is close to the surface form the RL stage trained on, and the depth
curve in `src/disc/SLATE.md` records a large swing between the routing idiom
and a fresh abstract notation without holding presentation fixed. These
renderers separate wording from content: the same seed builds the same system
with the same tables, the same starting tokens and the same gold answers, and a
renderer decides only how those are spelled.

Two task groups are covered.

The chain task (`src/disc/minrepro.py`) is rendered by `CHAIN_RENDERERS`. The
`routing` renderer reproduces minrepro byte for byte, which is asserted in the
driver, so it is the training-matched reference. Four of the seven renderers
form a two by two over lexicon and sentence frame, which splits the template
effect into the words used and the shape they sit in:

    routing            frame A, routing words   (training surface)
    processing         frame A, assembly words
    routing_frameb     frame B, routing words
    abstract           frame B, map and token words (the "Fexharv map" style)

The remaining three are ordinary English idioms lexically far from anything in
the training mixture: a depot, a caseload and a reaction series.

The three computation-free rule families (`src/skillacq/simple.py`) are
rendered by `SIMPLE_RENDERERS`. The system object is built from the seed and
its numbers, labels and nonce words are untouched; only the prose around them
changes. `native` is the published wording.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass

from src.disc.minrepro import MinSystem, _mentions
from src.skillacq.simple import SIMPLE_FAMILIES
from src.skillacq.systems import _answer_is_copyable

# --------------------------------------------------------------- chain task


@dataclass
class ChainRenderer:
    """One wording of the chained-lookup task.

    `preamble` and `table` produce pages; `question` produces the wh-question.
    `lookup` gives the regex that reads a table line, which the keyword-nearest
    shortcut baseline needs in order to be as strong in this wording as it is
    in the routing one.
    """

    name: str
    lexicon: str
    frame: str

    def preamble(self, sys: MinSystem) -> str:
        raise NotImplementedError

    def table(self, sys: MinSystem, i: int) -> str:
        raise NotImplementedError

    def question(self, sys: MinSystem, start: str, depth: int) -> str:
        raise NotImplementedError

    def lookup(self, start: str) -> str:
        raise NotImplementedError

    def pages(self, sys: MinSystem, depth: int) -> list[str]:
        """Gold pages only, in chain order, matching minrepro.minimal_pages."""
        return [self.preamble(sys)] + [self.table(sys, i) for i in range(depth)]


class Routing(ChainRenderer):
    """The surface form the RL stage trained on, verbatim from minrepro."""

    def __init__(self):
        super().__init__("routing", "routing", "A")

    def preamble(self, sys):
        return (f"The {sys.name} referral system.\n\n"
                f"Every office in the {sys.name} system routes a request to a "
                f"desk according to the request's type. When a request is "
                f"referred on to the next office, the name of the desk that "
                f"handled it becomes its type at that next office.")

    def table(self, sys, i):
        name = sys.map_names[i]
        lines = "\n".join(f"A {k} is handled by the {sys.maps[i][k]} desk."
                          for k in sys.levels[i])
        return (f"The {name} routing table.\n\n"
                f"Requests in the {name} office are routed by their type.\n\n"
                f"{lines}")

    def question(self, sys, start, depth):
        chain = sys.map_names[:depth]
        head = f"A {start} request arrives at the {chain[0]} office."
        if depth == 1:
            return head + " Which desk handles it?"
        hops = ", then to the ".join(chain[1:])
        return (f"{head} It is then referred to the {hops} office. "
                f"Which desk handles it at the {chain[-1]} office?")

    def lookup(self, start):
        return rf"A {re.escape(start)} is handled by the (\w+) desk"


class Processing(ChainRenderer):
    """Routing's sentence frame with assembly-line words in every slot."""

    def __init__(self):
        super().__init__("processing", "assembly", "A")

    def preamble(self, sys):
        return (f"The {sys.name} assembly.\n\n"
                f"Every stage in the {sys.name} assembly processes an item at "
                f"a unit according to the item's grade. When an item is passed "
                f"on to the next stage, the name of the unit that processed it "
                f"becomes its grade at that next stage.")

    def table(self, sys, i):
        name = sys.map_names[i]
        lines = "\n".join(f"A {k} is processed by the {sys.maps[i][k]} unit."
                          for k in sys.levels[i])
        return (f"The {name} processing table.\n\n"
                f"Items in the {name} stage are processed by their grade.\n\n"
                f"{lines}")

    def question(self, sys, start, depth):
        chain = sys.map_names[:depth]
        head = f"A {start} item arrives at the {chain[0]} stage."
        if depth == 1:
            return head + " Which unit processes it?"
        hops = ", then to the ".join(chain[1:])
        return (f"{head} It is then passed to the {hops} stage. "
                f"Which unit processes it at the {chain[-1]} stage?")

    def lookup(self, start):
        return rf"A {re.escape(start)} is processed by the (\w+) unit"


class RoutingFrameB(ChainRenderer):
    """Routing words in the abstract renderer's sentence frame."""

    def __init__(self):
        super().__init__("routing_frameb", "routing", "B")

    def preamble(self, sys):
        return (f"The {sys.name} referral system.\n\n"
                f"Every office in the {sys.name} system sends each request of "
                f"one type to a desk. When requests pass through offices in "
                f"sequence, the desk produced by one office is the type given "
                f"to the next office.")

    def table(self, sys, i):
        name = sys.map_names[i]
        lines = "\n".join(f"The {name} office sends {k} to {sys.maps[i][k]}."
                          for k in sys.levels[i])
        return (f"The {name} office.\n\n"
                f"Requests in the {name} office are sent according to the "
                f"following list.\n\n{lines}")

    def question(self, sys, start, depth):
        chain = sys.map_names[:depth]
        if depth == 1:
            return (f"Send {start} through the {chain[0]} office. "
                    f"Which desk results?")
        rest = "".join(f", then the {m} office" for m in chain[1:])
        return (f"Send {start} through the {chain[0]} office{rest}. "
                f"Which desk results?")

    def lookup(self, start):
        return rf"office sends {re.escape(start)} to (\w+)"


class Abstract(ChainRenderer):
    """The fresh notation the repro was first written in."""

    def __init__(self):
        super().__init__("abstract", "map", "B")

    def preamble(self, sys):
        return (f"The {sys.name} notation.\n\n"
                f"Every map in the {sys.name} notation sends each token of one "
                f"kind to a token of the next kind. When maps are applied in "
                f"sequence, the token produced by one map is the token given "
                f"to the next map.")

    def table(self, sys, i):
        name = sys.map_names[i]
        lines = "\n".join(f"The {name} map sends {k} to {sys.maps[i][k]}."
                          for k in sys.levels[i])
        return (f"The {name} map.\n\n"
                f"Tokens in the {name} map are sent according to the "
                f"following list.\n\n{lines}")

    def question(self, sys, start, depth):
        chain = sys.map_names[:depth]
        if depth == 1:
            return f"Apply the {chain[0]} map to {start}. Which token results?"
        rest = "".join(f", then the {m} map" for m in chain[1:])
        return (f"Apply the {chain[0]} map to {start}{rest}. "
                f"Which token results?")

    def lookup(self, start):
        return rf"map sends {re.escape(start)} to (\w+)"


class Inventory(ChainRenderer):
    """A depot network. Crates carry labels and land in bays."""

    def __init__(self):
        super().__init__("inventory", "depot", "A")

    def preamble(self, sys):
        return (f"The {sys.name} depot network.\n\n"
                f"Every depot in the {sys.name} network stores a crate in a "
                f"bay according to the crate's label. When a crate is "
                f"forwarded to the next depot, the name of the bay that stored "
                f"it becomes its label at that next depot.")

    def table(self, sys, i):
        name = sys.map_names[i]
        lines = "\n".join(
            f"A crate labelled {k} is stored in bay {sys.maps[i][k]}."
            for k in sys.levels[i])
        return (f"The {name} bay chart.\n\n"
                f"Crates in the {name} depot are stored by their label.\n\n"
                f"{lines}")

    def question(self, sys, start, depth):
        chain = sys.map_names[:depth]
        head = f"A crate labelled {start} arrives at the {chain[0]} depot."
        if depth == 1:
            return head + " Which bay stores it?"
        hops = ", then to the ".join(chain[1:])
        return (f"{head} It is then forwarded to the {hops} depot. "
                f"Which bay stores it at the {chain[-1]} depot?")

    def lookup(self, start):
        return rf"A crate labelled {re.escape(start)} is stored in bay (\w+)"


class Personnel(ChainRenderer):
    """A caseload. Cases carry grades and go to reviewers."""

    def __init__(self):
        super().__init__("personnel", "caseload", "A")

    def preamble(self, sys):
        return (f"The {sys.name} caseload.\n\n"
                f"Every panel in the {sys.name} caseload gives a case to a "
                f"reviewer according to the case's grade. When a case is "
                f"escalated to the next panel, the name of the reviewer who "
                f"took it becomes its grade at that next panel.")

    def table(self, sys, i):
        name = sys.map_names[i]
        lines = "\n".join(
            f"A case of grade {k} goes to reviewer {sys.maps[i][k]}."
            for k in sys.levels[i])
        return (f"The {name} assignment sheet.\n\n"
                f"Cases in the {name} panel are assigned by their grade.\n\n"
                f"{lines}")

    def question(self, sys, start, depth):
        chain = sys.map_names[:depth]
        head = f"A case of grade {start} reaches the {chain[0]} panel."
        if depth == 1:
            return head + " Which reviewer takes it?"
        hops = ", then to the ".join(chain[1:])
        return (f"{head} It is then escalated to the {hops} panel. "
                f"Which reviewer takes it at the {chain[-1]} panel?")

    def lookup(self, start):
        return rf"A case of grade {re.escape(start)} goes to reviewer (\w+)"


class Reaction(ChainRenderer):
    """A reaction series. Samples convert into products, bath by bath."""

    def __init__(self):
        super().__init__("reaction", "reaction", "A")

    def preamble(self, sys):
        return (f"The {sys.name} reaction series.\n\n"
                f"Every bath in the {sys.name} series converts a sample into a "
                f"product according to the sample's compound. When a product "
                f"is carried into the next bath, the name of the product "
                f"becomes the compound entering that bath.")

    def table(self, sys, i):
        name = sys.map_names[i]
        lines = "\n".join(f"A sample of {k} converts into {sys.maps[i][k]}."
                          for k in sys.levels[i])
        return (f"The {name} conversion chart.\n\n"
                f"Samples in the {name} bath convert according to their "
                f"compound.\n\n{lines}")

    def question(self, sys, start, depth):
        chain = sys.map_names[:depth]
        head = f"A sample of {start} enters the {chain[0]} bath."
        if depth == 1:
            return head + " Which product forms?"
        hops = ", then the ".join(chain[1:])
        return (f"{head} It is then carried into the {hops} bath. "
                f"Which product forms in the {chain[-1]} bath?")

    def lookup(self, start):
        return rf"A sample of {re.escape(start)} converts into (\w+)"


class RoutingKeyPhrase(ChainRenderer):
    """Routing, with the key moved out of the bare-noun slot.

    One edit from `routing`: "A {k}" becomes "A request of type {k}", on the
    page and in the question alike. Every other word, and the whole rest of the
    sentence geometry, is untouched.
    """

    def __init__(self):
        super().__init__("routing_keyphrase", "routing", "A")

    def preamble(self, sys):
        return Routing().preamble(sys)

    def table(self, sys, i):
        name = sys.map_names[i]
        lines = "\n".join(
            f"A request of type {k} is handled by the {sys.maps[i][k]} desk."
            for k in sys.levels[i])
        return (f"The {name} routing table.\n\n"
                f"Requests in the {name} office are routed by their type.\n\n"
                f"{lines}")

    def question(self, sys, start, depth):
        chain = sys.map_names[:depth]
        head = (f"A request of type {start} arrives at the {chain[0]} office.")
        if depth == 1:
            return head + " Which desk handles it?"
        hops = ", then to the ".join(chain[1:])
        return (f"{head} It is then referred to the {hops} office. "
                f"Which desk handles it at the {chain[-1]} office?")

    def lookup(self, start):
        return (rf"A request of type {re.escape(start)} is handled by the "
                rf"(\w+) desk")


class RoutingPostValue(ChainRenderer):
    """Routing, with the value moved after its noun instead of before it.

    One edit from `routing`: "the {v} desk" becomes "desk {v}" on the table
    line. The question is `routing`'s question, word for word.
    """

    def __init__(self):
        super().__init__("routing_postvalue", "routing", "A")

    def preamble(self, sys):
        return (f"The {sys.name} referral system.\n\n"
                f"Every office in the {sys.name} system routes a request to a "
                f"desk according to the request's type. When a request is "
                f"referred on to the next office, the name of the desk that "
                f"handled it becomes its type at that next office.")

    def table(self, sys, i):
        name = sys.map_names[i]
        lines = "\n".join(f"A {k} is handled by desk {sys.maps[i][k]}."
                          for k in sys.levels[i])
        return (f"The {name} routing table.\n\n"
                f"Requests in the {name} office are routed by their type.\n\n"
                f"{lines}")

    def question(self, sys, start, depth):
        return Routing().question(sys, start, depth)

    def lookup(self, start):
        return rf"A {re.escape(start)} is handled by desk (\w+)"


CHAIN_RENDERERS: dict[str, ChainRenderer] = {
    r.name: r for r in (Routing(), Processing(), RoutingFrameB(), Abstract(),
                        Inventory(), Personnel(), Reaction(),
                        RoutingKeyPhrase(), RoutingPostValue())
}


def chain_problems(sys: MinSystem, rng: random.Random, depth: int,
                   n: int) -> list[dict]:
    """minrepro's rejection sampler, made renderer independent.

    The original rejects a problem when the gold token appears in the rendered
    question. That test depends on the wording, so running it per renderer
    would leave the renderers with different question sets. The tokens a
    question can name are the same in every renderer here, namely the starting
    token, the map names and the system name, so the test is applied to that
    set instead. The driver re-runs the original per-renderer test on the
    rendered text and reports violations rather than dropping items.
    """
    out: list[dict] = []
    starts = list(sys.starts)
    rng.shuffle(starts)
    named = set(sys.map_names) | {sys.name}
    for start in starts:
        if len(out) >= n:
            break
        stages = sys.run(start, depth)
        gold = stages[-1]
        if len(set(stages)) != len(stages):
            continue
        if depth > 1 and gold == sys.maps[depth - 1].get(start):
            continue
        if gold in named or gold == start:
            continue
        out.append({
            "qid": f"d{depth}_{len(out)}",
            "kind": f"chain{depth}",
            "depth": depth,
            "start": start,
            "chain": sys.map_names[:depth],
            "stages": stages,
            "answer": gold,
        })
    return out


def chain_episode(seed: int, depth: int, renderer: ChainRenderer,
                  n_problems: int = 8, alphabet_size: int = 6,
                  max_depth: int = 4, typed: bool = True,
                  pages_mode: str = "minimal") -> dict:
    """One RL-shaped episode. Content depends on the seed, wording on renderer.

    The rng draw order matches `minrepro.generate_episode` exactly, so the
    system, the surviving problems and the gold answers are identical across
    renderers and identical to the published instrument.

    `pages_mode` "minimal" is the published gold-pages condition, a preamble
    plus one table per step. "table_only" drops the preamble, which at depth
    one leaves a single-document store: whatever the policy asks for, the
    answering page is what comes back. That removes retrieval selection from
    the comparison, so any accuracy left over is the wording's effect on
    applying the rule rather than on finding it.
    """
    rng = random.Random(seed * 7919)
    sys = MinSystem(rng, alphabet_size=alphabet_size, max_depth=max_depth,
                    typed=typed)
    problems = chain_problems(sys, rng, depth, n_problems)
    if pages_mode == "minimal":
        docs = renderer.pages(sys, depth)
    elif pages_mode == "table_only":
        docs = [renderer.table(sys, i) for i in range(depth)]
    else:
        raise ValueError(f"unknown pages_mode {pages_mode!r}")
    return {
        "episode_id": f"tmpl-{renderer.name}-{depth}-{pages_mode}-{seed:07d}",
        "seed": seed,
        "depth": depth,
        "renderer": renderer.name,
        "alphabet_size": alphabet_size,
        "max_depth": max_depth,
        "typed": typed,
        "pages_condition": pages_mode,
        "world": {"domain": "skill_minrepro"},
        "n_context": 0,
        "documents": [{"text": p} for p in docs],
        "alphabet": sys.universe,
        "questions": [
            {
                "qid": p["qid"],
                "text": renderer.question(sys, p["start"], depth),
                "answer": p["answer"],
                "plan": [f"s{i}" for i in range(depth)],
                "type": p["kind"],
                "depth": depth,
                "start": p["start"],
                "chain": p["chain"],
                "stages": p["stages"],
            }
            for p in problems
        ],
    }


def chain_violations(ep: dict, renderer: ChainRenderer) -> dict[str, int]:
    """The per-renderer exclusions, checked on the wording actually shown."""
    v = {"answer_in_question": 0, "answer_is_start": 0,
         "answer_is_intermediate": 0, "stages_not_distinct": 0}
    for q in ep["questions"]:
        gold, stages = q["answer"], q["stages"]
        if _mentions(gold, q["text"]):
            v["answer_in_question"] += 1
        if gold == stages[0]:
            v["answer_is_start"] += 1
        if gold in stages[:-1]:
            v["answer_is_intermediate"] += 1
        if len(set(stages)) != len(stages):
            v["stages_not_distinct"] += 1
    return v


# -------------------------------------------------------- simple rule tasks


@dataclass
class SimpleRenderer:
    """One wording of the three computation-free rule families.

    `describe` returns the textbook pages for a system object built from a
    seed; `question` returns the wh-question for a problem produced by that
    same object. Every number, label and nonce word comes from the system, so
    only the prose changes between renderers.
    """

    name: str

    def describe(self, family: str, s) -> list[str]:
        return getattr(self, f"pages_{family}")(s)

    def question(self, family: str, s, p: dict) -> str:
        return getattr(self, f"q_{family}")(s, p)

    def lookup(self, s, key: str) -> str:
        """Regex reading the substitution table line for `key`."""
        raise NotImplementedError


class NativeSimple(SimpleRenderer):
    """The published wording, copied from src/skillacq/simple.py."""

    def __init__(self):
        super().__init__("native")

    def pages_threshold_rule(self, s):
        return [
            f"The {s.name} classification.\n\n"
            f"Every specimen in the {s.name} classification carries a {s.attr} "
            f"reading, which is a whole number.",
            f"The rule.\n\n"
            f"A specimen whose {s.attr} reading is greater than {s.limit} is "
            f"called {s.high}. A specimen whose {s.attr} reading is {s.limit} "
            f"or less is called {s.low}.",
            f"A worked example.\n\n"
            f"A specimen with a {s.attr} reading of {s.limit + 7} is {s.high}.",
        ]

    def q_threshold_rule(self, s, p):
        return (f"A specimen has a {s.attr} reading of {p['value']}. "
                f"In the {s.name} classification, what is it called?")

    def pages_substitution_rule(self, s):
        lines = "\n".join(f"A {k} is handled by the {v} desk."
                          for k, v in zip(s.keys, s.values))
        return [
            f"The {s.name} routing table.\n\n"
            f"Requests in the {s.name} office are routed by their type.",
            f"Routing.\n\n{lines}\n\n"
            f"Any request whose type is not listed goes to the "
            f"{s.rng_default} desk.",
            f"A note on precedence.\n\n"
            f"The table above is complete. Do not infer a desk from the name "
            f"of a request type; use only the routing given here.",
        ]

    def q_substitution_rule(self, s, p):
        return (f"A {p['key']} request arrives at the {s.name} office. "
                f"Which desk handles it?")

    def pages_exception_rule(self, s):
        return [
            f"The {s.name} protocol.\n\n"
            f"Items reaching the {s.name} protocol are marked with a category "
            f"word.",
            f"The general rule.\n\n"
            f"Every item is given the {s.general} treatment.",
            f"The exception.\n\n"
            f"There is one exception. An item whose category is "
            f"{s.special_key} is given the {s.special} treatment instead.",
        ]

    def q_exception_rule(self, s, p):
        return (f"An item of category {p['key']} reaches the {s.name} "
                f"protocol. Which treatment does it receive?")

    def lookup(self, s, key):
        return rf"A {re.escape(key)} is handled by the (\w+) desk"


class AbstractSimple(SimpleRenderer):
    """A spare formal notation: items, numbers, values, pairings."""

    def __init__(self):
        super().__init__("abstract")

    def pages_threshold_rule(self, s):
        return [
            f"The {s.name} scheme.\n\n"
            f"Every item in the {s.name} scheme carries a {s.attr} number, "
            f"which is a whole number.",
            f"The condition.\n\n"
            f"An item whose {s.attr} number exceeds {s.limit} takes the value "
            f"{s.high}. An item whose {s.attr} number does not exceed "
            f"{s.limit} takes the value {s.low}.",
            f"An instance.\n\n"
            f"An item whose {s.attr} number is {s.limit + 7} takes the value "
            f"{s.high}.",
        ]

    def q_threshold_rule(self, s, p):
        return (f"An item has a {s.attr} number of {p['value']}. "
                f"Under the {s.name} scheme, which value does it take?")

    def pages_substitution_rule(self, s):
        lines = "\n".join(f"{k} pairs with {v}."
                          for k, v in zip(s.keys, s.values))
        return [
            f"The {s.name} table.\n\n"
            f"Each entry in the {s.name} table pairs a type with a value.",
            f"Entries.\n\n{lines}\n\n"
            f"Any type that is not listed pairs with {s.rng_default}.",
            f"A note on scope.\n\n"
            f"The table above is complete. Do not infer a value from the "
            f"spelling of a type; use only the pairings given here.",
        ]

    def q_substitution_rule(self, s, p):
        return (f"The type {p['key']} is presented to the {s.name} table. "
                f"Which value does it pair with?")

    def pages_exception_rule(self, s):
        return [
            f"The {s.name} rule set.\n\n"
            f"Every input to the {s.name} rule set carries a class word.",
            f"The default.\n\n"
            f"Every input takes the outcome {s.general}.",
            f"The override.\n\n"
            f"There is one override. An input whose class is {s.special_key} "
            f"takes the outcome {s.special} instead.",
        ]

    def q_exception_rule(self, s, p):
        return (f"An input of class {p['key']} is presented to the {s.name} "
                f"rule set. Which outcome does it take?")

    def lookup(self, s, key):
        return rf"{re.escape(key)} pairs with (\w+)"


class InventorySimple(SimpleRenderer):
    """A depot: crates, weights, bays, wraps."""

    def __init__(self):
        super().__init__("inventory")

    def pages_threshold_rule(self, s):
        return [
            f"The {s.name} intake.\n\n"
            f"Every crate at the {s.name} intake carries a {s.attr} weight, "
            f"which is a whole number.",
            f"The cutoff.\n\n"
            f"A crate whose {s.attr} weight is greater than {s.limit} is "
            f"stacked as {s.high}. A crate whose {s.attr} weight is {s.limit} "
            f"or less is stacked as {s.low}.",
            f"A logged crate.\n\n"
            f"A crate with a {s.attr} weight of {s.limit + 7} is stacked as "
            f"{s.high}.",
        ]

    def q_threshold_rule(self, s, p):
        return (f"A crate has a {s.attr} weight of {p['value']}. "
                f"At the {s.name} intake, how is it stacked?")

    def pages_substitution_rule(self, s):
        lines = "\n".join(f"A crate labelled {k} is stored in bay {v}."
                          for k, v in zip(s.keys, s.values))
        return [
            f"The {s.name} bay chart.\n\n"
            f"Crates at the {s.name} depot are stored by their label.",
            f"Storage.\n\n{lines}\n\n"
            f"Any crate whose label is not listed goes to bay "
            f"{s.rng_default}.",
            f"A note on the chart.\n\n"
            f"The chart above is complete. Do not guess a bay from the "
            f"wording of a label; use only the storage given here.",
        ]

    def q_substitution_rule(self, s, p):
        return (f"A crate labelled {p['key']} arrives at the {s.name} depot. "
                f"Which bay stores it?")

    def pages_exception_rule(self, s):
        return [
            f"The {s.name} packing line.\n\n"
            f"Crates reaching the {s.name} packing line are marked with a "
            f"contents word.",
            f"The standard wrap.\n\n"
            f"Every crate is given the {s.general} wrap.",
            f"The exception.\n\n"
            f"There is one exception. A crate whose contents are "
            f"{s.special_key} is given the {s.special} wrap instead.",
        ]

    def q_exception_rule(self, s, p):
        return (f"A crate of contents {p['key']} reaches the {s.name} packing "
                f"line. Which wrap does it receive?")

    def lookup(self, s, key):
        return rf"A crate labelled {re.escape(key)} is stored in bay (\w+)"


class PersonnelSimple(SimpleRenderer):
    """A panel: applicants, scores, reviewers, handling."""

    def __init__(self):
        super().__init__("personnel")

    def pages_threshold_rule(self, s):
        return [
            f"The {s.name} panel.\n\n"
            f"Every applicant before the {s.name} panel carries a {s.attr} "
            f"score, which is a whole number.",
            f"The bar.\n\n"
            f"An applicant whose {s.attr} score is greater than {s.limit} is "
            f"ranked {s.high}. An applicant whose {s.attr} score is {s.limit} "
            f"or less is ranked {s.low}.",
            f"A past applicant.\n\n"
            f"An applicant with a {s.attr} score of {s.limit + 7} is ranked "
            f"{s.high}.",
        ]

    def q_threshold_rule(self, s, p):
        return (f"An applicant has a {s.attr} score of {p['value']}. "
                f"Before the {s.name} panel, how is the applicant ranked?")

    def pages_substitution_rule(self, s):
        lines = "\n".join(f"A case of grade {k} goes to reviewer {v}."
                          for k, v in zip(s.keys, s.values))
        return [
            f"The {s.name} assignment sheet.\n\n"
            f"Cases at the {s.name} panel are assigned by their grade.",
            f"Assignments.\n\n{lines}\n\n"
            f"Any case whose grade is not listed goes to reviewer "
            f"{s.rng_default}.",
            f"A note on the sheet.\n\n"
            f"The sheet above is complete. Do not infer a reviewer from the "
            f"name of a grade; use only the assignments given here.",
        ]

    def q_substitution_rule(self, s, p):
        return (f"A case of grade {p['key']} reaches the {s.name} panel. "
                f"Which reviewer takes it?")

    def pages_exception_rule(self, s):
        return [
            f"The {s.name} review.\n\n"
            f"Files entering the {s.name} review are marked with a status "
            f"word.",
            f"The standing instruction.\n\n"
            f"Every file is given the {s.general} handling.",
            f"The exception.\n\n"
            f"There is one exception. A file whose status is {s.special_key} "
            f"is given the {s.special} handling instead.",
        ]

    def q_exception_rule(self, s, p):
        return (f"A file of status {p['key']} enters the {s.name} review. "
                f"Which handling does it receive?")

    def lookup(self, s, key):
        return rf"A case of grade {re.escape(key)} goes to reviewer (\w+)"


SIMPLE_RENDERERS: dict[str, SimpleRenderer] = {
    r.name: r for r in (NativeSimple(), AbstractSimple(), InventorySimple(),
                        PersonnelSimple())
}

SIMPLE_FAMS = sorted(SIMPLE_FAMILIES)


def _simple_problems(s, family: str, rng: random.Random,
                     n_problems: int) -> list[dict]:
    """Problem content, wording aside.

    The family generators bake their own wording into `text`, so the content is
    lifted back out: the numeric case for a threshold, the key word for a
    substitution or an exception. Rejection uses the native wording, which is
    what the published run used, so every renderer keeps the same items.
    """
    kept: list[dict] = []
    for _ in range(12):
        if len(kept) >= n_problems:
            break
        for p in s.problems(rng, n_problems * 4):
            if _answer_is_copyable(p["answer"], p["text"]):
                continue
            rec = {"kind": p["kind"], "answer": p["answer"],
                   "native_text": p["text"]}
            if family == "threshold_rule":
                m = re.search(r"reading of (\d+)", p["text"])
                rec["value"] = int(m.group(1))
                rec["key"] = None
            elif family == "substitution_rule":
                m = re.search(r"^A (\S+) request arrives", p["text"])
                rec["key"] = m.group(1)
                rec["value"] = None
            else:
                m = re.search(r"^An item of category (\S+) reaches", p["text"])
                rec["key"] = m.group(1)
                rec["value"] = None
            kept.append(rec)
    kept = kept[:n_problems]
    for i, p in enumerate(kept):
        p["qid"] = f"p{i}"
    return kept


def simple_episode(seed: int, family: str, renderer: SimpleRenderer,
                   n_problems: int = 6, distractor: bool = True,
                   pages: str = "textbook") -> dict:
    """One RL-shaped simple-rule episode in the given wording.

    `pages` is the evidence condition: the system's own textbook, a different
    family's textbook in the same wording, or a blank page. The distractor
    pages are rendered in the same wording too, so nothing but the target
    wording separates the renderers.
    """
    rng = random.Random(seed)
    s = SIMPLE_FAMILIES[family](rng)
    problems = _simple_problems(s, family, rng, n_problems)
    gold = renderer.describe(family, s)
    own = list(gold)
    if distractor:
        other_fam = rng.choice([f for f in SIMPLE_FAMS if f != family])
        other = SIMPLE_FAMILIES[other_fam](random.Random(seed ^ 0x5EED))
        own = own + renderer.describe(other_fam, other)
        rng.shuffle(own)

    if pages == "textbook":
        docs = own
    elif pages == "gold_only":
        docs = gold
    elif pages == "wrong_textbook":
        wfam = SIMPLE_FAMS[(seed + 1) % len(SIMPLE_FAMS)]
        wrng = random.Random(seed + 777000)
        w = SIMPLE_FAMILIES[wfam](wrng)
        docs = renderer.describe(wfam, w)
        ofam = wrng.choice([f for f in SIMPLE_FAMS if f != wfam])
        o = SIMPLE_FAMILIES[ofam](random.Random((seed + 777000) ^ 0x5EED))
        docs = docs + renderer.describe(ofam, o)
        wrng.shuffle(docs)
    elif pages == "twin":
        trng = random.Random(seed + 313000)
        twin = SIMPLE_FAMILIES[family](trng)
        docs = list(gold) + renderer.describe(family, twin)
        trng.shuffle(docs)
    elif pages == "no_documents":
        docs = ["This page is intentionally blank."]
    else:
        raise ValueError(f"unknown pages condition {pages!r}")

    return {
        "episode_id": f"simp-{renderer.name}-{family}-{seed:07d}",
        "seed": seed,
        "family": family,
        "renderer": renderer.name,
        "pages_condition": pages,
        "world": {"domain": f"skill_{family}"},
        "n_context": 0,
        "documents": [{"text": p} for p in docs],
        "candidates": _candidates(s, family),
        "twin_candidates": (_candidates(twin, family)
                            if pages == "twin" else []),
        "questions": [
            {
                "qid": p["qid"],
                "text": renderer.question(family, s, p),
                "answer": p["answer"],
                "plan": [p["qid"]],
                "type": p["kind"],
            }
            for p in problems
        ],
    }


def _candidates(s, family: str) -> list[str]:
    """The answer set a reader could choose from, for the chance floor."""
    if family == "threshold_rule":
        return [s.high, s.low]
    if family == "substitution_rule":
        return list(s.values) + [s.rng_default]
    return [s.general, s.special]
