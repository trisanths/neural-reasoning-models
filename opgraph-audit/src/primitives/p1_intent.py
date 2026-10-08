"""Primitive 1: intent understanding.

Turn a messy, underspecified, sometimes self-contradicting request into
explicit goals, constraints, uncertainties, a named conflict and a success
condition. The item never asks for the task to be solved. Nothing in the
request can be acted on: the sites, the goods and the operations are nonce
words invented per item, and no arithmetic is possible on them.

How the request is built. A scenario draws nonce vocabulary and then picks
five constraint kinds, of which three are actually voiced by the requester.
Each voiced constraint enters the request in a colloquial paraphrase and
enters the option menu in a canonical form, so the correct option is never
a substring of the request. Each voiced constraint also contributes its
polarity-flipped twin to the menu, which shares nearly every content word
with the true option. The two unvoiced kinds contribute their canonical
form as plausible-but-never-asked distractors. Half the scenarios carry a
real contradiction and half do not, so a model that always reports a
conflict is visible as a false-alarm rate rather than scoring by habit.

CONTAMINATION CONTROL, faculty by faculty.

Composition depth: every field is a one-step restatement of one span of
the request. No field requires chaining two facts, so a model that fails
at depth two can still score one here.

Abstraction construction: nothing is induced. The isolated form gives the
model an explicit menu of candidate structures and asks only which apply;
no procedure is built or transferred.

Information acquisition: the full request is in the prompt and the chunk
list is empty. There is nothing to retrieve and no source to select.

Missing-capability recognition: the model reports contradictions inside
the request, which are textual conflicts with both sides present. It is
never asked what it itself lacks. The two objects are disjoint.

Temporary knowledge: single turn, and the request is short enough to sit
well inside any context this project trains at.

Verification and action: no trap and no computation to check. A first
reading that parses the request correctly is correct.

Format compliance: the parser accepts fields in any order and any case,
strips bullets and numbering, and the runner reports the parse rate as a
separate number, so failing the format is never silently scored as
failing to understand.
"""

from __future__ import annotations

import random

from src.primitives.common import (
    Item, guard_report, invented_words, jaccard, mean_stat, parse_fields,
    parse_labels, parse_one_label, proportion, render_menu, token_set,
)

PRIMITIVE = "intent"
FIELDS = ("GOAL", "CONSTRAINTS", "UNCERTAIN", "CONFLICT", "SUCCESS")

INSTRUCTIONS_ISOLATED = """Read the request below. Do not carry it out. Report its structure only.
Answer with exactly these five lines, using the labels from the menus:
GOAL: one goal label
CONSTRAINTS: every constraint label the request imposes, as first stated
UNCERTAIN: every label naming something the request leaves unstated
CONFLICT: the label of the contradiction in the request, or XNONE
SUCCESS: one success-condition label"""

INSTRUCTIONS_INTEGRATED = """Read the request below. Do not carry it out. Report its structure only.
Answer with exactly these five lines, in your own words:
GOAL: the single thing the requester wants done
CONSTRAINTS: every limit the request imposes as first stated, separated by semicolons
UNCERTAIN: everything the request leaves unstated that you would need
CONFLICT: the two statements in the request that contradict each other, or none
SUCCESS: the condition under which the request is satisfied"""


def _kinds(v: dict, rng: random.Random) -> list[dict]:
    """The five constraint kinds, each in three forms.

    said     the colloquial sentence the requester utters
    flipsaid the colloquial retraction, worded so that neither canonical
             option is ever a verbatim lift out of the request
    true     the canonical constraint, used as the correct option
    flip     the polarity-flipped twin, used as a near-identical distractor
    key      the token that must appear in a free-form answer
    """
    day, budget, keep, route, count = (
        v["day"], v["budget"], v["keep"], v["route"], v["count"])
    return [
        {"name": "deadline", "key": day,
         "said": f"it has to be done by {day}, that is the hard part",
         "flipsaid": f"nothing may land before {day} after all",
         "true": f"completion no later than {day}",
         "flip": f"completion no earlier than {day}"},
        {"name": "budget", "key": str(budget),
         "said": f"we cannot spend more than {budget} on this",
         "flipsaid": f"we have to clear {budget} of spend for the accounts",
         "true": f"total spend at most {budget}",
         "flip": f"total spend at least {budget}"},
        {"name": "preserve", "key": keep,
         "said": f"whatever you do, leave the {keep} stack alone",
         "flipsaid": f"the {keep} stack has to be reworked as well",
         "true": f"the {keep} stack is not to be altered",
         "flip": f"the {keep} stack is to be altered"},
        {"name": "route", "key": route,
         "said": f"everything goes through the {route} channel, nothing else",
         "flipsaid": f"use anything except the {route} channel",
         "true": f"the {route} channel is the only channel used",
         "flip": f"the {route} channel is the one channel not used"},
        {"name": "quantity", "key": str(count),
         "said": f"send {count} of them, not a unit more",
         "flipsaid": f"we will need to go past {count} units",
         "true": f"exactly {count} units are sent",
         "flip": f"more than {count} units are sent"},
    ]


def _scenario(seed: int) -> dict:
    rng = random.Random(seed)
    w = invented_words(rng, 8)
    v = {
        "verb": rng.choice(["move", "transfer", "consolidate", "reissue"]),
        "goods": w[0], "here": w[1], "there": w[2], "other": w[3],
        "keep": w[4], "route": w[5], "who": w[6].capitalize(), "spare": w[7],
        "day": rng.choice(["Tuesday", "Friday", "the ninth", "the equinox"]),
        "budget": rng.randrange(200, 900, 50),
        "count": rng.randrange(12, 90),
    }
    v["rng"] = rng
    return v


def _goal_options(v: dict) -> tuple[list[str], int]:
    """The true goal and three minimal edits of it."""
    g = v["verb"]
    opts = [
        f"{g} the {v['goods']} batch from {v['here']} to {v['there']}",
        f"{g} the {v['keep']} batch from {v['here']} to {v['there']}",
        f"{g} the {v['goods']} batch from {v['here']} to {v['other']}",
        f"{g} the {v['goods']} batch from {v['there']} to {v['here']}",
    ]
    return opts, 0


def generate(seed: int, mode: str = "isolated") -> Item:
    """One intent item. mode isolated gives menus, integrated does not."""
    v = _scenario(seed)
    rng: random.Random = v["rng"]
    kinds = _kinds(v, rng)
    rng.shuffle(kinds)
    voiced, silent = kinds[:3], kinds[3:]

    has_conflict = (seed % 2 == 0)
    clash = rng.choice(voiced) if has_conflict else None

    lines = [
        f"{v['who']} writes: I need the {v['goods']} batch out of {v['here']} "
        f"and into {v['there']}, that is the main thing."
    ]
    for k in voiced:
        lines.append(k["said"].capitalize() + ".")
    if clash is not None:
        # The retraction is deliberately not the canonical flip text, so the
        # flip option is never a verbatim lift out of the request and the
        # menu cannot be solved by string presence.
        lines.append(f"Second thoughts on the {clash['name']}, though: "
                     f"{clash['flipsaid']}.")
    lines.append(f"Someone mentioned {v['other']} as an alternative, though I "
                 f"have no idea what they can take.")
    lines.append(f"The {v['spare']} paperwork belongs to {v['who']}, not to me.")
    tail = lines[1:]
    rng.shuffle(tail)
    request = " ".join([lines[0]] + tail)

    goal_opts, goal_gold = _goal_options(v)
    con_opts, con_gold = [], []
    for k in voiced:
        con_opts.append(k["true"])
        con_gold.append(k["true"])
        con_opts.append(k["flip"])
    for k in silent:
        con_opts.append(k["true"])
    unc_opts = [
        f"how much {v['other']} can take is not stated",
        f"who signs off on the {v['goods']} batch is not stated",
        f"the destination of the {v['goods']} batch is not stated",
        f"the origin of the {v['goods']} batch is not stated",
        f"the {v['spare']} paperwork owner is not stated",
    ]
    unc_gold = [unc_opts[0], unc_opts[1]]

    cf_true = (f"the {clash['name']} is stated both as "
               f"'{clash['true']}' and as '{clash['flip']}'") if clash else None
    others = [k for k in voiced if k is not clash]
    cf_opts = [
        f"the {others[0]['name']} and the {others[1]['name']} requirements "
        f"cannot both hold",
        f"the goal and the {others[0]['name']} requirement cannot both hold",
        f"the {v['spare']} paperwork and the goal cannot both hold",
    ]
    if cf_true:
        cf_opts.insert(rng.randrange(len(cf_opts) + 1), cf_true)

    stated = "; ".join(k["true"] for k in voiced)
    wrong_one = voiced[0]["flip"]
    suc_opts = [
        f"the {v['goods']} batch is at {v['there']} and {stated}",
        f"the {v['goods']} batch is at {v['other']} and {stated}",
        f"the {v['goods']} batch is at {v['there']} and "
        + "; ".join([wrong_one] + [k["true"] for k in voiced[1:]]),
        f"the {v['goods']} batch is at {v['there']} and {silent[0]['true']}",
    ]
    suc_gold = 0

    for pool in (goal_opts, con_opts, unc_opts, cf_opts, suc_opts):
        rng.shuffle(pool)
    goal_gold = goal_opts.index(_goal_options(v)[0][0])
    suc_gold = suc_opts.index(
        f"the {v['goods']} batch is at {v['there']} and {stated}")

    guards = {
        "goal": guard_report(request, goal_opts, goal_gold),
        "success": guard_report(request, suc_opts, suc_gold),
    }
    if cf_true:
        guards["conflict"] = guard_report(request, cf_opts,
                                          cf_opts.index(cf_true))

    if mode == "integrated":
        question = (INSTRUCTIONS_INTEGRATED + "\n\nRequest.\n" + request)
        gold = {
            "form": "free",
            "goal_need": sorted(token_set(f"{v['verb']} {v['goods']} {v['there']}")),
            "goal_avoid": sorted(token_set(f"{v['other']} {v['keep']}")),
            "constraint_keys": sorted({k["key"] for k in voiced}),
            "constraint_absent": sorted({k["key"] for k in silent}),
            "uncertain_keys": [v["other"]],
            "conflict_key": clash["name"] if clash else None,
            "success_need": sorted(token_set(f"{v['goods']} {v['there']}")),
        }
        menus = {}
    else:
        gm, gl = render_menu(goal_opts, "G")
        cm, cl = render_menu(con_opts, "C")
        um, ul = render_menu(unc_opts, "U")
        xm, xl = render_menu(cf_opts, "X")
        sm, sl = render_menu(suc_opts, "S")
        question = (
            INSTRUCTIONS_ISOLATED + "\n\nRequest.\n" + request
            + "\n\nGoal menu.\n" + gm
            + "\n\nConstraint menu.\n" + cm
            + "\n\nUnstated menu.\n" + um
            + "\n\nConflict menu (answer XNONE if the request is consistent).\n" + xm
            + "\n\nSuccess menu.\n" + sm
        )
        gold = {
            "form": "menu",
            "goal": gl[goal_gold],
            "goal_labels": gl,
            "constraints": sorted(cl[con_opts.index(t)] for t in con_gold),
            "constraint_labels": cl,
            "uncertain": sorted(ul[unc_opts.index(t)] for t in unc_gold),
            "uncertain_labels": ul,
            "conflict": xl[cf_opts.index(cf_true)] if cf_true else "XNONE",
            "conflict_labels": xl + ["XNONE"],
            "success": sl[suc_gold],
            "success_labels": sl,
        }
        menus = {"n_goal": len(gl), "n_conflict": len(xl) + 1,
                 "n_success": len(sl), "n_constraint": len(cl),
                 "n_uncertain": len(ul)}

    return Item(
        item_id=f"p1-{mode}-{seed:07d}",
        primitive=PRIMITIVE,
        variant="conflict" if has_conflict else "consistent",
        mode=mode, question=question, chunks=[], gold=gold,
        meta={"seed": seed, "has_conflict": has_conflict,
              "guards": guards, **menus},
    )


def generate_many(n: int, seed: int = 0, mode: str = "isolated") -> list[Item]:
    """n items, rejecting any a shortcut heuristic would solve."""
    out: list[Item] = []
    s = seed
    tried = 0
    while len(out) < n and tried < n * 40:
        tried += 1
        item = generate(s, mode=mode)
        s += 1
        if any(g["any"] for g in item.meta["guards"].values()):
            continue
        out.append(item)
    if len(out) < n:
        raise RuntimeError(f"only {len(out)} of {n} intent items passed the guard")
    return out


def _f1(found: set, gold: set) -> float:
    if not gold and not found:
        return 1.0
    if not gold or not found:
        return 0.0
    hit = len(found & gold)
    if hit == 0:
        return 0.0
    p, r = hit / len(found), hit / len(gold)
    return 2 * p * r / (p + r)


def grade(item: Item, response: str) -> dict:
    """Per-field scores for one response. Never a single pass or fail."""
    f = parse_fields(response)
    got = {k: f.get(k, "") for k in FIELDS}
    parsed = all(k in f for k in FIELDS)
    g = item.gold
    out = {"parsed": parsed, "fields_present": sum(1 for k in FIELDS if k in f)}

    if g["form"] == "menu":
        out["goal"] = float(parse_one_label(got["GOAL"], g["goal_labels"]) == g["goal"])
        out["conflict"] = float(
            parse_one_label(got["CONFLICT"], g["conflict_labels"]) == g["conflict"])
        out["success"] = float(
            parse_one_label(got["SUCCESS"], g["success_labels"]) == g["success"])
        cs = set(parse_labels(got["CONSTRAINTS"], g["constraint_labels"]))
        us = set(parse_labels(got["UNCERTAIN"], g["uncertain_labels"]))
        out["constraints"] = jaccard(cs, set(g["constraints"]))
        out["constraints_exact"] = float(cs == set(g["constraints"]))
        out["uncertain"] = jaccard(us, set(g["uncertain"]))
    else:
        gt = token_set(got["GOAL"])
        hit = all(t in gt for t in g["goal_need"])
        clean = not any(t in gt for t in g["goal_avoid"])
        out["goal"] = float(hit and clean)
        ct = token_set(got["CONSTRAINTS"])
        found = {k for k in g["constraint_keys"] if k in ct}
        spur = {k for k in g["constraint_absent"] if k in ct}
        out["constraints"] = _f1(found | spur, set(g["constraint_keys"]))
        out["constraints_exact"] = float(
            found == set(g["constraint_keys"]) and not spur)
        ut = token_set(got["UNCERTAIN"])
        out["uncertain"] = float(all(k in ut for k in g["uncertain_keys"]))
        xt = got["CONFLICT"].lower()
        if g["conflict_key"] is None:
            out["conflict"] = float(
                any(w in xt for w in ("none", "no conflict", "consistent",
                                      "xnone", "nothing")))
        else:
            out["conflict"] = float(g["conflict_key"] in xt)
        st = token_set(got["SUCCESS"])
        out["success"] = float(all(t in st for t in g["success_need"]))
    return out


def aggregate(items: list[Item], grades: list[dict]) -> dict:
    """Per-field statistics plus a headline that is their chance-adjusted mean."""
    if not items:
        return {"primitive": PRIMITIVE, "n": 0}
    menu = items[0].gold.get("form") == "menu"
    chance = {"goal": 1.0 / items[0].meta.get("n_goal", 4) if menu else 0.0,
              "conflict": 1.0 / items[0].meta.get("n_conflict", 4) if menu else 0.0,
              "success": 1.0 / items[0].meta.get("n_success", 4) if menu else 0.0}
    fields = {}
    for name in ("goal", "conflict", "success", "constraints_exact"):
        k = sum(int(round(gr.get(name, 0.0))) for gr in grades)
        fields[name] = proportion(k, len(grades), chance.get(name, 0.0), name)
    for name in ("constraints", "uncertain"):
        fields[name] = mean_stat([gr.get(name, 0.0) for gr in grades], name)
    parse = proportion(sum(int(gr["parsed"]) for gr in grades), len(grades), 0.0,
                       "parse_rate")
    per_variant = {}
    for var in sorted({i.variant for i in items}):
        sel = [gr for i, gr in zip(items, grades) if i.variant == var]
        per_variant[var] = proportion(
            sum(int(round(gr.get("conflict", 0.0))) for gr in sel), len(sel),
            chance.get("conflict", 0.0), f"conflict/{var}")
    headline = sum([
        fields["goal"]["adjusted"], fields["conflict"]["adjusted"],
        fields["success"]["adjusted"], fields["constraints"]["mean"],
        fields["uncertain"]["mean"],
    ]) / 5.0
    return {"primitive": PRIMITIVE, "mode": items[0].mode, "n": len(items),
            "headline": headline, "fields": fields, "parse_rate": parse,
            "per_variant": per_variant}


CONTAMINATION = __doc__
