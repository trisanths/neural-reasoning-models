"""Scripted stand-in models, and the evidence that the metrics work.

A benchmark that has never been shown to respond to the thing it claims to
measure is decoration. These stand-ins are the instrument's own
calibration: each one has exactly one faculty and is blind in the other
six, in a way that is well formed at every point, so a metric that moves
for the wrong stand-in is measuring format or luck rather than a faculty.

How a stand-in works. An answer key is built by generating the same items
the runner will generate, at the same seed and size, and indexing them by
the tail of their prompt. A stand-in that is competent at a faculty looks
its item up and answers from the item's own gold. A stand-in that is blind
at a faculty answers in exactly the right shape with a value drawn at
random from that item's own option set. Blind is therefore chance, not
silence, and parse rates stay at one throughout, so nothing in the profile
can move because a stand-in stopped speaking.

Three families.

  faculty_model(name)   competent at one faculty, blind in the other six.
                        Running all seven fills a square matrix whose
                        diagonal should be high and whose off-diagonal
                        should sit at chance. That is the sensitivity and
                        specificity claim, made checkable.

  depth_model(d)        solves composed tasks up to depth d and guesses
                        beyond it. The reported depth k* should track d,
                        which is the behavioural check on the curve that
                        the pre-registration says matters most.

  copy_model()          answers abstraction items the way the lexically
                        nearest lesson case was answered. Its same-surface
                        score is whatever text matching earns and its
                        transfer margin should be nothing, which is the
                        check that the transfer condition measures
                        construction and not matching.

A partial_model(p) is also provided, correct with probability p and blind
otherwise, so a metric can be shown to move monotonically rather than
merely to have two settings.
"""

from __future__ import annotations

import random

from src.primitives import episode as ep
from src.primitives import (
    p1_intent, p2_gap, p3_acquisition, p4_abstraction, p5_composition,
    p6_memory, p7_verification, runner,
)

TAIL = 400


def _tail(text: str) -> str:
    return text[-TAIL:]


def build_answer_key(n: int = 8, seed: int = 0, mode: str = "isolated",
                     ks=(1, 2, 3), rescue_n: int = 4) -> dict:
    """Index every item the runner will produce by the tail of its prompt.

    The tail rather than the head, because a composition item and its own
    per-step probes share a long identical prefix and would otherwise
    collide.
    """
    key: dict[str, tuple] = {}

    def put(item, role="main", question=None):
        key[_tail(question if question is not None else item.question)] = (
            item, role)

    for item in p1_intent.generate_many(n, seed=seed, mode=mode):
        put(item)
    for item in p2_gap.generate_many(n, seed=seed, mode=mode):
        put(item)
    for variant in ("direct", "recursive"):
        for item in p3_acquisition.generate_many(n, seed=seed, mode=mode,
                                                 variant=variant):
            put(item)
            if variant == "recursive":
                put(item, "hop", runner.followup_question(item))
    for condition in ("same_surface", "transfer"):
        for item in p4_abstraction.generate_many(n, seed=seed, mode=mode,
                                                 condition=condition):
            put(item)
    for kind in p5_composition.KINDS:
        items = p5_composition.generate_curve(n, kind, ks, seed=seed, mode=mode)
        for item in items:
            put(item)
        for probe in p5_composition.probe_items(items):
            put(probe, "probe")
    for item in p6_memory.generate_many(n, seed=seed, mode=mode):
        put(item)
    for item in p7_verification.generate_many(n, seed=seed, mode=mode):
        put(item)
    if rescue_n:
        for item in ep.generate_matrix(rescue_n, seed=seed):
            put(item)
    return key


# ------------------------------------------------------------ gold answers

def _gold_intent(item) -> str:
    g = item.gold
    if g["form"] == "menu":
        return (f"GOAL: {g['goal']}\n"
                f"CONSTRAINTS: {', '.join(g['constraints'])}\n"
                f"UNCERTAIN: {', '.join(g['uncertain'])}\n"
                f"CONFLICT: {g['conflict']}\n"
                f"SUCCESS: {g['success']}")
    conflict = g["conflict_key"] or "none, the request is consistent"
    return (f"GOAL: {' '.join(g['goal_need'])}\n"
            f"CONSTRAINTS: {'; '.join(g['constraint_keys'])}\n"
            f"UNCERTAIN: {' '.join(g['uncertain_keys'])}\n"
            f"CONFLICT: {conflict}\n"
            f"SUCCESS: {' '.join(g['success_need'])}")


def _blind_intent(item, rng) -> str:
    g = item.gold
    if g["form"] == "menu":
        cl, ul = g["constraint_labels"], g["uncertain_labels"]
        return (f"GOAL: {rng.choice(g['goal_labels'])}\n"
                f"CONSTRAINTS: "
                f"{', '.join(rng.sample(cl, min(3, len(cl))))}\n"
                f"UNCERTAIN: {', '.join(rng.sample(ul, min(2, len(ul))))}\n"
                f"CONFLICT: {rng.choice(g['conflict_labels'])}\n"
                f"SUCCESS: {rng.choice(g['success_labels'])}")
    return ("GOAL: something is to be done\n"
            "CONSTRAINTS: unclear\n"
            "UNCERTAIN: unclear\n"
            "CONFLICT: none\n"
            "SUCCESS: the request is met")


def _gold_gap(item) -> str:
    g = item.gold
    return f"STATUS: {g['status']}\nGAP: {g['gap']}\nSTEP: {g['step']}"


def _blind_gap(item, rng) -> str:
    return (f"STATUS: {rng.choice(['BLOCKED', 'SOLVABLE'])}\n"
            f"GAP: {rng.choice([t[0] for t in p2_gap.GAP_MENU] + ['NONE'])}\n"
            f"STEP: {rng.choice(p2_gap.STEP_LABELS)}")


def _gold_acq(item, role) -> str:
    g = item.gold
    if role == "hop":
        return f"SOURCE: {g['hop_tier']}\nQUERY: {g['hop_query']}"
    return f"SOURCE: {g['first_tier']}\nQUERY: {g['first_query']}"


def _blind_acq(item, rng) -> str:
    # The blind stand-in issues the shortcut every guard is built against:
    # it echoes the request. Its score is the copy baseline by definition.
    stem = item.question.split("What is needed.\n")[-1]
    return (f"SOURCE: {rng.choice(p3_acquisition.TIER_NAMES)}\n"
            f"QUERY: {stem.strip()}")


def _gold_label(item) -> str:
    return f"ANSWER: {item.gold['answer']}"


def _blind_label(item, rng) -> str:
    return f"ANSWER: {rng.choice(list(item.gold['labels']))}"


def _gold_verify(item) -> str:
    return f"CHECK: {item.gold['check']}\nANSWER: {item.gold['answer']}"


def _blind_verify(item, rng) -> str:
    return (f"CHECK: {rng.choice(['PASS', 'FAIL'])}\n"
            f"ANSWER: {rng.choice(list(item.gold['labels']))}")


class ScriptedModel:
    """A stand-in with a chosen set of faculties and nothing else.

    competent   the faculty names it answers from gold. Everything else is
                answered in the right shape from that item's own options.
    level       probability it uses its competence on any one item, so a
                metric can be shown to move monotonically.
    max_depth   composition items deeper than this are guessed even when
                composition is in competent, which is what the depth curve
                is checked against.
    copy        abstraction items are answered the way the lexically
                nearest lesson case was, whatever competent says.
    """

    def __init__(self, key: dict, competent=(), seed: int = 0,
                 level: float = 1.0, max_depth: int | None = None,
                 copy: bool = False):
        self.key = key
        self.competent = set(competent)
        self.rng = random.Random(seed)
        self.level = float(level)
        self.max_depth = max_depth
        self.copy = copy
        self.misses = 0

    def _able(self, primitive: str) -> bool:
        return (primitive in self.competent
                and self.rng.random() < self.level)

    def __call__(self, question: str, chunks=None) -> str:
        found = self.key.get(_tail(str(question)))
        if found is None:
            self.misses += 1
            return "ANSWER: unknown"
        item, role = found
        p = item.primitive
        rng = self.rng

        if p == "intent":
            return (_gold_intent(item) if self._able("intent")
                    else _blind_intent(item, rng))
        if p == "gap":
            return (_gold_gap(item) if self._able("gap")
                    else _blind_gap(item, rng))
        if p == "acquisition":
            return (_gold_acq(item, role) if self._able("acquisition")
                    else _blind_acq(item, rng))
        if p == "abstraction":
            if self.copy:
                ok = item.meta["copy_correct"]
                labs = list(item.gold["labels"])
                want = item.gold["answer"]
                other = [x for x in labs if x != want][0]
                return f"ANSWER: {want if ok else other}"
            return (_gold_label(item) if self._able("abstraction")
                    else _blind_label(item, rng))
        if p == "composition":
            deep = item.meta.get("k", 0)
            if role == "probe":
                # Per-step probes are single applications. A stand-in with
                # any composition ability at all answers them, which is
                # what makes the step-conditioned curve meaningful.
                able = ("composition" in self.competent
                        and rng.random() < self.level)
            else:
                able = (self._able("composition")
                        and (self.max_depth is None or deep <= self.max_depth))
            return _gold_label(item) if able else _blind_label(item, rng)
        if p == "memory":
            return (_gold_label(item) if self._able("memory")
                    else _blind_label(item, rng))
        if p == "verification":
            return (_gold_verify(item) if self._able("verification")
                    else _blind_verify(item, rng))
        if p == "episode":
            # An episode is rescued when the faculty it was losing is
            # supplied. A stand-in solves it when every faculty it lacks
            # has been oracled away for that condition.
            have = self.competent | set(item.meta["oracles"])
            return (_gold_label(item)
                    if set(ep.FACULTIES) <= have else _blind_label(item, rng))
        return "ANSWER: unknown"


class ChoosingModel(ScriptedModel):
    """A stand-in that also answers the forced-choice channel.

    Competence carries across both channels, so the calibration matrix can
    be run on the channel a real checkpoint is actually measurable on.
    Choices are indexed by the option list rather than the prompt, since
    the forced-choice prompts are rewritten per field.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choice_key: dict[tuple, int] = {}
        self.blind_seed = kwargs.get("seed", 0)

    def learn_choices(self, pairs) -> None:
        for item, choice in pairs:
            self.choice_key[(_tail(choice["question"]),
                             tuple(choice["options"]))] = (
                choice["gold"], item.primitive, item.meta.get("k"),
                tuple(item.meta.get("oracles", ())))

    def choose_both(self, question: str, chunks=None, options=()) -> tuple:
        pick = self.choose(question, chunks, options)
        return pick, pick

    def choose(self, question: str, chunks=None, options=()) -> int:
        options = list(options)
        found = self.choice_key.get((_tail(str(question)), tuple(options)))
        if found is None:
            self.misses += 1
            return 0
        gold, primitive, k, oracles = found
        able = primitive in self.competent and self.rng.random() < self.level
        if primitive == "composition" and self.max_depth is not None:
            able = able and (k is None or k <= self.max_depth)
        if primitive == "episode":
            # Same reading as the generation channel: the episode goes
            # through when every faculty the stand-in lacks has been
            # oracled away for that condition, so the forced-choice rescue
            # matrix locates a missing faculty the same way.
            able = set(ep.FACULTIES) <= (self.competent | set(oracles))
        if able:
            return gold
        # The blind pick is drawn from a stream keyed by the prompt rather
        # than from the shared one, so it cannot pick up the order items
        # happen to be scored in. The alternative left a stand-in blind at
        # a faculty scoring twenty of twenty-four on a two-way field.
        return random.Random(f"{self.blind_seed}|{question}").randrange(
            len(options))


def faculty_model(key: dict, name: str, seed: int = 0) -> ScriptedModel:
    return ScriptedModel(key, competent=[name], seed=seed)


def blind_model(key: dict, seed: int = 0) -> ScriptedModel:
    return ScriptedModel(key, competent=[], seed=seed)


def oracle_model(key: dict, seed: int = 0) -> ScriptedModel:
    from src.primitives import PRIMITIVES
    return ScriptedModel(key, competent=PRIMITIVES, seed=seed)


def depth_model(key: dict, d: int, seed: int = 0) -> ScriptedModel:
    return ScriptedModel(key, competent=["composition"], seed=seed, max_depth=d)


def copy_model(key: dict, seed: int = 0) -> ScriptedModel:
    return ScriptedModel(key, competent=[], seed=seed, copy=True)


def partial_model(key: dict, name: str, level: float,
                  seed: int = 0) -> ScriptedModel:
    return ScriptedModel(key, competent=[name], seed=seed, level=level)
