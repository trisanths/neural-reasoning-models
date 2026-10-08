"""The acquisition test battery, taken with the source hidden.

A model that can quote a page it is still looking at has learned nothing, so
every prompt here is closed book: the chapter that defines the target item is
not in the prompt and cannot be retrieved during the battery. Six tests, all
against one item:

  reconstruction   state the rule from memory
  recognition      pick the true statement out of four
  application      one unseen easy instance
  counterexample   produce an input on which a false variant disagrees
  composition      a problem needing this item and an earlier one
  transfer         the same item behind a surface it has not been seen in

Reconstruction is the test most easily faked. Where the item has numeric
parameters the response is scored by semantics: the integers the model
writes are fitted back into the reference form and the reconstructed rule is
executed against the reference implementation on inputs the model never saw.
It passes only when the reconstructed rule computes what the real one
computes. Where the item has no numeric parameters, which is the case for the
orbit and conductor definitions, there is nothing to execute and the fallback
is token overlap against the reference statement. That fallback is weak and
is reported as semantic false, so a battery result carrying it is read with
that in mind rather than treated as proof of acquisition.

Counterexample is scored by execution too: the harness runs the model's
proposed input through the reference implementation and through the false
variant and asks whether they actually differ.
"""

from __future__ import annotations

import itertools
import random
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Callable

from src.mathgen.bench import ModelFn, extract_answer, normalize

TESTS = ("reconstruction", "recognition", "application", "counterexample",
         "composition", "transfer")

_INT_RE = re.compile(r"-?\d+")
_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]*")


def token_f1(response: str, reference: str) -> float:
    a = Counter(t.lower() for t in _WORD_RE.findall(response))
    b = Counter(t.lower() for t in _WORD_RE.findall(reference))
    if not a or not b:
        return 0.0
    overlap = sum((a & b).values())
    if not overlap:
        return 0.0
    prec, rec = overlap / sum(a.values()), overlap / sum(b.values())
    return 2 * prec * rec / (prec + rec)


def ints_in(text: str, limit: int = 12) -> list[int]:
    return [int(t) for t in _INT_RE.findall(text)][:limit]


@dataclass
class TestResult:
    test: str
    item_id: str
    correct: bool
    semantic: bool
    prompt: str
    raw: str
    detail: dict = field(default_factory=dict)


@dataclass
class Probe:
    """One item's battery: six prompts and six ways of grading a reply."""

    item_id: str
    prompts: dict
    graders: dict
    semantic: dict
    prior_item_id: str | None = None


def _choices(rng, true_stmt: str, false_stmts: list[str]) -> tuple[str, str]:
    opts = [true_stmt] + false_stmts[:3]
    order = list(range(len(opts)))
    rng.shuffle(order)
    letters = "ABCD"
    lines = []
    correct = "A"
    for pos, src in enumerate(order):
        lines.append(f"{letters[pos]}. {opts[src]}")
        if src == 0:
            correct = letters[pos]
    return "\n".join(lines), correct


def _letter(raw: str) -> str:
    m = re.search(r"(?i)\b([ABCD])\b", raw)
    return m.group(1).upper() if m else ""


# --------------------------------------------------------------------------
# probes
# --------------------------------------------------------------------------
def probe_core(u, rng: random.Random) -> Probe:
    """The product itself: three integer parameters, so fully executable."""
    p, c = u.p, u.calc
    name, g = p.name, p.g_core
    pairs = [(rng.randrange(2, p.modulus), rng.randrange(2, p.modulus))
             for _ in range(6)]

    def grade_reconstruction(raw: str) -> tuple[bool, dict]:
        cand = ints_in(raw)
        for a2, b2, c2 in itertools.permutations(cand, 3):
            if all((a2 * x * y + b2 * (x + y) + c2) % p.modulus == c.core(x, y)
                   for x, y in pairs):
                return True, {"fitted": [a2, b2, c2]}
        for a2, b2, c2 in itertools.product(cand, repeat=3):
            if all((a2 * x * y + b2 * (x + y) + c2) % p.modulus == c.core(x, y)
                   for x, y in pairs):
                return True, {"fitted": [a2, b2, c2]}
        return False, {"ints": cand}

    true_stmt = (f"x {g} y is {p.a} times x times y, plus {p.b} times the sum "
                 f"of x and y, plus {p.c}, reduced modulo {p.modulus}")
    false = [
        (f"x {g} y is {(p.a % p.modulus) + 1} times x times y, plus {p.b} times "
         f"the sum of x and y, plus {p.c}, reduced modulo {p.modulus}"),
        (f"x {g} y is {p.a} times x times y, plus {p.b} times the sum of x and "
         f"y, plus {(p.c + 7) % p.modulus}, reduced modulo {p.modulus}"),
        (f"x {g} y is {p.a} times x times y, minus {p.b} times the sum of x and "
         f"y, plus {p.c}, reduced modulo {p.modulus}"),
    ]
    mc, letter = _choices(rng, true_stmt, false)

    ax, ay = rng.randrange(2, 9), rng.randrange(2, 9)
    tx, ty = rng.randrange(2, 9), rng.randrange(2, 9)

    # The false claim has to hold almost everywhere, or a guessed input
    # refutes it. This one fails on about one pair in M.
    ce_chance = sum(1 for x in range(p.modulus) for y in range(p.modulus)
                    if c.core(x, y) == x) / (p.modulus ** 2)

    def grade_counterexample(raw: str) -> tuple[bool, dict]:
        nums = ints_in(raw, 4)
        if len(nums) < 2:
            return False, {"parsed": nums, "chance": ce_chance}
        x, y = nums[0] % p.modulus, nums[1] % p.modulus
        return c.core(x, y) == x, {"x": x, "y": y, "product": c.core(x, y),
                                   "chance": ce_chance}

    cx = rng.randrange(2, p.modulus)
    while (p.a * cx + p.b) % p.modulus == 0:
        cx = rng.randrange(2, p.modulus)
    cy = rng.randrange(2, p.modulus)
    cz = c.core(cx, cy)

    return Probe(
        item_id="i_core",
        prior_item_id="i_march",
        prompts={
            "reconstruction": (
                f"From memory, state the rule for the {g} product of the {name} "
                f"calculus. Give the arithmetic in full, including the modulus."),
            "recognition": (
                f"One of these states the {g} product of the {name} calculus "
                f"correctly.\n{mc}\nAnswer with the letter alone."),
            "application": (
                f"From memory, evaluate {ax} {g} {ay} in the {name} calculus.\n"
                f"Answer:"),
            "counterexample": (
                f"Someone claims that in the {name} calculus x {g} y is never "
                f"equal to x itself. Give one pair of readings where it is, "
                f"written as x,y.\nAnswer:"),
            "composition": (
                f"In the {name} calculus, the reading y satisfies "
                f"{cx} {g} y = {cz}. What is y?\nAnswer:"),
            "transfer": (
                f"A dial in the {name} workshop shows two readings, {tx} and "
                f"{ty}. The workshop combines a pair of readings by the "
                f"calculus's own product and shows the result. What does it "
                f"show?\nAnswer:"),
        },
        graders={
            "reconstruction": grade_reconstruction,
            "recognition": lambda raw: (_letter(raw) == letter, {"want": letter}),
            "application": lambda raw: (
                extract_answer(raw, "int") == str(c.core(ax, ay)),
                {"want": c.core(ax, ay)}),
            "counterexample": grade_counterexample,
            "composition": lambda raw: (
                extract_answer(raw, "int") == str(cy), {"want": cy}),
            "transfer": lambda raw: (
                extract_answer(raw, "int") == str(c.core(tx, ty)),
                {"want": c.core(tx, ty)}),
        },
        semantic={t: True for t in TESTS},
    )


def probe_march(u, rng: random.Random) -> Probe:
    """The reciprocal procedure: the exponent is a parameter, so executable."""
    p, c = u.p, u.calc
    name = p.name
    ks = [k for k in (3, 5, 7, 11) if k % p.modulus]

    def grade_reconstruction(raw: str) -> tuple[bool, dict]:
        for e in ints_in(raw):
            if e <= 0:
                continue
            if all(pow(k, e, p.modulus) == c.inv(k) for k in ks):
                return True, {"exponent": e}
        return False, {"ints": ints_in(raw)}

    true_stmt = (f"raise the multiplier to the power {p.modulus - 2}, reduce it, "
                 f"and scale the known value by the result")
    false = [
        (f"raise the multiplier to the power {p.modulus - 1}, reduce it, and "
         f"scale the known value by the result"),
        (f"subtract the multiplier from {p.modulus} and scale the known value "
         f"by the result"),
        (f"raise the known value to the power {p.modulus - 2} and scale the "
         f"multiplier by the result"),
    ]
    mc, letter = _choices(rng, true_stmt, false)

    k = rng.choice(ks)
    x = rng.randrange(2, p.modulus)
    z = c.scale(k, x)
    tk = rng.choice([kk for kk in ks if kk != k])
    tx = rng.randrange(2, p.modulus)
    tz = c.scale(tk, tx)

    ccx = rng.randrange(2, p.modulus)
    while (p.a * ccx + p.b) % p.modulus == 0:
        ccx = rng.randrange(2, p.modulus)
    ccy = rng.randrange(2, p.modulus)
    ccz = c.core(ccx, ccy)

    # The procedure works for every multiplier except zero. Asking for the
    # pair rather than the multiplier alone stops a model that always replies
    # with one default number from passing: the pair has to actually fail.
    ce_chance = (p.modulus - 1) / (p.modulus ** 2)

    def grade_counterexample(raw: str) -> tuple[bool, dict]:
        nums = ints_in(raw, 4)
        if len(nums) < 2:
            return False, {"parsed": nums, "chance": ce_chance}
        kk, xx = nums[0] % p.modulus, nums[1] % p.modulus
        zz = (kk * xx) % p.modulus
        recovered = (pow(kk, p.modulus - 2, p.modulus) * zz) % p.modulus
        return recovered != xx, {"k": kk, "x": xx, "recovered": recovered,
                                 "chance": ce_chance}

    return Probe(
        item_id="i_march",
        prior_item_id="i_core",
        prompts={
            "reconstruction": (
                f"From memory, state the {name} calculus's procedure for "
                f"recovering x when only the scaled value is known. Give the "
                f"exponent it uses."),
            "recognition": (
                f"One of these states that procedure correctly.\n{mc}\n"
                f"Answer with the letter alone."),
            "application": (
                f"In the {name} calculus, {k} {p.g_scale} x is {z}. "
                f"What is x?\nAnswer:"),
            "counterexample": (
                f"Someone claims the {name} calculus's recovery procedure works "
                f"for every multiplier without exception. Give one multiplier "
                f"and one reading it fails on, written as k,x.\nAnswer:"),
            "composition": (
                f"In the {name} calculus, the reading y satisfies "
                f"{ccx} {p.g_core} y = {ccz}. What is y?\nAnswer:"),
            "transfer": (
                f"A press in the {name} workshop multiplies a reading by {tk} "
                f"and reports {tz}. Which reading went in?\nAnswer:"),
        },
        graders={
            "reconstruction": grade_reconstruction,
            "recognition": lambda raw: (_letter(raw) == letter, {"want": letter}),
            "application": lambda raw: (
                extract_answer(raw, "int") == str(x), {"want": x}),
            "counterexample": grade_counterexample,
            "composition": lambda raw: (
                extract_answer(raw, "int") == str(ccy), {"want": ccy}),
            "transfer": lambda raw: (
                extract_answer(raw, "int") == str(tx), {"want": tx}),
        },
        semantic={t: True for t in TESTS},
    )


def probe_conductor(u, rng: random.Random) -> Probe:
    """A definition with no numeric parameter, so reconstruction is weak."""
    p, c = u.p, u.calc
    name = p.name
    ref = u.items["i_conductor"].statement + " " + u.items["i_orbit"].statement

    def grade_reconstruction(raw: str) -> tuple[bool, dict]:
        f1 = token_f1(raw, ref)
        return f1 >= 0.5, {"token_f1": round(f1, 4), "threshold": 0.5}

    true_stmt = (f"the count of distinct readings the repeated {p.w_pivot} "
                 f"visits, starting from the reading itself")
    false = [
        f"the largest reading the repeated {p.w_pivot} visits",
        f"the smallest reading the repeated {p.w_pivot} visits",
        f"the sum of the readings the repeated {p.w_pivot} visits",
    ]
    mc, letter = _choices(rng, true_stmt, false)

    ax = rng.randrange(2, p.modulus)
    r1, r2 = rng.randrange(2, p.modulus), rng.randrange(2, p.modulus)
    while c.conductor(r1) == c.conductor(r2):
        r2 = rng.randrange(2, p.modulus)
    winner = r1 if c.conductor(r1) > c.conductor(r2) else r2
    ones = [x for x in range(p.modulus) if c.conductor(x) == 1]
    census = ",".join(str(v) for v in ones) if ones else "none"

    # Only the readings the step leaves in place have conductor one, and the
    # universe is drawn so that there are exactly two of them.
    ce_chance = len(ones) / p.modulus

    def grade_counterexample(raw: str) -> tuple[bool, dict]:
        nums = ints_in(raw, 3)
        if not nums:
            return False, {"parsed": nums, "chance": ce_chance}
        r = nums[0] % p.modulus
        return c.conductor(r) == 1, {"reading": r, "conductor": c.conductor(r),
                                     "chance": ce_chance}

    return Probe(
        item_id="i_conductor",
        prior_item_id="i_census",
        prompts={
            "reconstruction": (
                f"From memory, state what the {p.w_conductor} of a "
                f"{p.w_reading} is in the {name} calculus."),
            "recognition": (
                f"One of these states the {p.w_conductor} correctly.\n{mc}\n"
                f"Answer with the letter alone."),
            "application": (
                f"From memory, what is the {p.w_conductor} of the "
                f"{p.w_reading} {ax} in the {name} calculus?\nAnswer:"),
            "counterexample": (
                f"Someone claims every {p.w_reading} of the {name} calculus has "
                f"a {p.w_conductor} of at least 2. Give one {p.w_reading} where "
                f"that is false.\nAnswer:"),
            "composition": (
                f"Report the {p.w_census} of the {p.w_reading}s of the {name} "
                f"calculus whose {p.w_conductor} is 1.\nAnswer:"),
            "transfer": (
                f"Of the {p.w_reading}s {r1} and {r2} in the {name} calculus, "
                f"which has the greater {p.w_conductor}?\nAnswer:"),
        },
        graders={
            "reconstruction": grade_reconstruction,
            "recognition": lambda raw: (_letter(raw) == letter, {"want": letter}),
            "application": lambda raw: (
                extract_answer(raw, "int") == str(c.conductor(ax)),
                {"want": c.conductor(ax)}),
            "counterexample": grade_counterexample,
            "composition": lambda raw: (
                normalize(extract_answer(raw, "list")) == normalize(census),
                {"want": census}),
            # A two-way comparison, so a coin flip scores a half here and the
            # report carries that.
            "transfer": lambda raw: (
                extract_answer(raw, "int") == str(winner),
                {"want": winner, "chance": 0.5}),
        },
        semantic={t: (t != "reconstruction") for t in TESTS},
    )


PROBES: dict[str, Callable] = {
    "i_core": probe_core,
    "i_march": probe_march,
    "i_conductor": probe_conductor,
}


# --------------------------------------------------------------------------
# running the battery
# --------------------------------------------------------------------------
def run_battery(model: ModelFn, universe, item_ids=None,
                seed: int = 0) -> list[TestResult]:
    """Six tests per item, source hidden, one row each."""
    rng = random.Random(seed)
    out: list[TestResult] = []
    for iid in (item_ids or sorted(PROBES)):
        probe = PROBES[iid](universe, rng)
        for test in TESTS:
            prompt = probe.prompts[test]
            raw = model(prompt)
            ok, detail = probe.graders[test](raw)
            if probe.prior_item_id and test == "composition":
                detail = {**detail, "prior_item": probe.prior_item_id}
            out.append(TestResult(test, iid, bool(ok), probe.semantic[test],
                                  prompt, raw[:400], detail))
    return out


def battery_report(results: list[TestResult]) -> dict:
    """Per item and per test. Nothing here is averaged across items."""
    per_item: dict = {}
    for r in results:
        per_item.setdefault(r.item_id, {})[r.test] = {
            "correct": r.correct, "semantic": r.semantic, "detail": r.detail}
    per_test: dict = {}
    for test in TESTS:
        rows = [r for r in results if r.test == test]
        chances = [r.detail["chance"] for r in rows if "chance" in r.detail]
        entry = {
            "n": len(rows),
            "passed": sum(r.correct for r in rows),
            "rate": sum(r.correct for r in rows) / len(rows) if rows else 0.0,
            "semantic": all(r.semantic for r in rows),
        }
        if test == "recognition":
            entry["chance"] = 0.25
        if chances:
            entry["chance"] = sum(chances) / len(chances)
        per_test[test] = entry
    gate = {iid: all(v["correct"] for v in tests.values())
            for iid, tests in per_item.items()}
    return {"per_item": per_item, "per_test": per_test, "acquired": gate}


# --------------------------------------------------------------------------
# scripted takers, for wiring the battery up
# --------------------------------------------------------------------------
def scripted_learner(universe, competence: float = 1.0, seed: int = 0) -> ModelFn:
    """A taker that has internalised the reference implementation.

    It answers from the reference rather than from any text in the prompt, so
    a high score here means the battery's grading works, not that any model
    has acquired anything.
    """
    u = universe
    p, c = u.p, u.calc
    rng = random.Random(seed)

    def model(prompt: str) -> str:
        if rng.random() > competence:
            return "Answer: 0"
        low = prompt.lower()
        if "state the rule for" in low and p.g_core in prompt:
            return (f"x {p.g_core} y is {p.a} times x times y plus {p.b} times "
                    f"(x plus y) plus {p.c}, all reduced modulo {p.modulus}.")
        if "procedure for" in low or "state that procedure" in low:
            return (f"Raise the multiplier to the power {p.modulus - 2}, reduce "
                    f"modulo {p.modulus}, then scale the known value by it.")
        if f"what the {p.w_conductor}" in low:
            return u.items["i_conductor"].statement + " " + \
                u.items["i_orbit"].statement
        if "answer with the letter alone" in low:
            for line in prompt.split("\n"):
                m = re.match(r"^([ABCD])\.\s*(.+)$", line.strip())
                if not m:
                    continue
                letter, body = m.group(1), m.group(2)
                if str(p.modulus - 2) in body and "multiplier to the power" in body:
                    return letter
                if body.startswith(f"x {p.g_core} y is {p.a} times") and \
                        f"plus {p.c}," in body and "minus" not in body:
                    return letter
                if body.startswith("the count of distinct readings"):
                    return letter
            return "A"
        nums = ints_in(prompt, 8)
        if "give one pair of readings where it is" in low:
            for x in range(p.modulus):
                y = c.unwind(x, x)
                if y is not None:
                    return f"Answer: {x},{y}"
        if "one multiplier and one reading it fails on" in low:
            return "Answer: 0,7"
        if "where that is false" in low:
            for r in range(p.modulus):
                if c.conductor(r) == 1:
                    return f"Answer: {r}"
        m = re.search(rf"(\d+) \{re.escape(p.g_core)}? ?y = (\d+)", prompt)
        m2 = re.search(rf"(\d+) {re.escape(p.g_core)} y = (\d+)", prompt)
        if m2:
            x, z = int(m2.group(1)), int(m2.group(2))
            y = c.unwind(x, z)
            return f"Answer: {y}"
        m3 = re.search(rf"(\d+) {re.escape(p.g_core)} (\d+)", prompt)
        if m3:
            return f"Answer: {c.core(int(m3.group(1)), int(m3.group(2)))}"
        if "combines a pair of readings" in low:
            return f"Answer: {c.core(nums[0], nums[1])}"
        m4 = re.search(rf"(\d+) {re.escape(p.g_scale)} x is (\d+)", prompt)
        if m4:
            k, z = int(m4.group(1)), int(m4.group(2))
            return f"Answer: {(c.inv(k) * z) % p.modulus}"
        if "multiplies a reading by" in low and len(nums) >= 2:
            k, z = nums[0], nums[1]
            return f"Answer: {(c.inv(k) * z) % p.modulus}"
        if f"{p.w_conductor} is 1" in low:
            ones = [x for x in range(p.modulus) if c.conductor(x) == 1]
            return "Answer: " + (",".join(str(v) for v in ones) or "none")
        if "which has the greater" in low and len(nums) >= 2:
            r1, r2 = nums[-2], nums[-1]
            return f"Answer: {r1 if c.conductor(r1) > c.conductor(r2) else r2}"
        if f"{p.w_conductor} of the" in low and nums:
            return f"Answer: {c.conductor(nums[0])}"
        return "Answer: 0"

    return model
