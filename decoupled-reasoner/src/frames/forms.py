"""Sentence shapes: everything about a frame that is not a word choice.

A shape fixes, per family, how the rule is stated (conditional, mapping,
table row, imperative, value-first), where the key sits relative to the
value, which voice the statement takes, how the three pages are ordered and
titled, and how the question is posed. It fixes no open-class vocabulary:
every noun and verb arrives from `src/frames/lexicon.py`, and every invented
word arrives from the `src/skillacq/simple.py` system object.

The `native` shape crossed with the `routing` lexicon reproduces the wording
in `src/skillacq/simple.py` byte for byte, in all three families.

Templates are `str.format` strings over role slots. Slot names are upper case
for lexicon roles, lower case for values that come from the system: `k` and
`v` for a mapping row, `q` for the question's key or value, `D` for the
fallback value, `G`, `SK`, `SP` for the exception family's three words, `L`,
`HI`, `LO`, `ATTR` for the threshold family's.
"""

from __future__ import annotations

from dataclasses import dataclass

# ------------------------------------------------------------ substitution

SUB_STATEMENTS = {
    "s_passive":     "A {k} is {VPART} {VPREP} the {v} {VAL}.",
    "s_passivepost": "A {k} is {VPART} {VPREP} {VAL} {v}.",
    "s_active":      "The {N} {SITE} {VSORT3} {k} to the {v} {VAL}.",
    "s_cond":        "If {A} {ENT} has {KEY} {k}, its {VAL} is {v}.",
    "s_condthen":    "If the {KEY} is {k}, then the {VAL} is {v}.",
    "s_colon":       "{k}: {v}",
    "s_pipe":        "| {k} | {v} |",
    "s_imper":       "{VIMP} {A} {k} {ENT} to the {v} {VAL}.",
    "s_rel":         "{Acap} {ENT} whose {KEY} is {k} {VGO} the {v} {VAL}.",
    "s_valfirst":    "The {v} {VAL} {VACT} any {ENT} of {KEY} {k}.",
    "s_pairs":       "{k} pairs with {v}.",
}

SUB_QUESTIONS = {
    "q_arrival":   "A {q} {ENT} {VARR} the {N} {SITE}. Which {VAL} {VACT} it?",
    "q_direct":    "Which {VAL} {VACT} {A} {q} {ENT} in the {N} {SITE}?",
    "q_keyphrase": ("{Acap} {ENT} of {KEY} {q} {VARR} the {N} {SITE}. "
                    "Which {VAL} {VACT} it?"),
    "q_imper":     ("{VIMP} {A} {q} {ENT} through the {N} {SITE}. "
                    "Name the {VAL}."),
    "q_consider":  ("Consider {A} {ENT} whose {KEY} is {q} at the {N} {SITE}. "
                    "Which {VAL} {VACT} it?"),
    "q_bywhich":   ("In the {N} {SITE}, {A} {ENT} of {KEY} {q} is {VPART} "
                    "{VPREP} which {VAL}?"),
    "q_postposed": ("Which {VAL}, in the {N} {SITE}, {VACT} {A} {ENT} of "
                    "{KEY} {q}?"),
}

# Each layout is (page 0, page 1, page 2, fallback clause). Page 1 carries
# {LINES} and {FALLBACK}; keeping the fallback clause separate lets the
# trivial-program baseline in `src/frames/parsers.py` build a reader for it
# without re-parsing the page template.
SUB_LAYOUTS = {
    "L_native": (
        "The {N} {DOM}.\n\n{ENTS} in the {N} {SITE} are {VSORT} by their {KEY}.",
        "{SECT}.\n\n{LINES}\n\n{FALLBACK}",
        "A note on precedence.\n\nThe table above is complete. Do not infer "
        "{AVAL} {VAL} from the name of {A} {ENT} {KEY}; use only the {SECTL} "
        "given here.",
        "Any {ENT} whose {KEY} is not listed {VGO} the {D} {VAL}.",
    ),
    "L_fallbackfirst": (
        "{N} {DOM}\n\nEvery {ENT} at the {N} {SITE} carries {AKEY} {KEY}.",
        "{SECT}\n\n{FALLBACK}\n\n{LINES}",
        "Scope\n\nThe list above is complete. The {KEY} of {A} {ENT} does not "
        "by itself indicate its {VAL}.",
        "Any {ENT} whose {KEY} is not listed {VGO} the {D} {VAL}.",
    ),
    "L_terse": (
        "About the {N} {DOM}.\n\nEvery {ENT} at the {N} {SITE} carries {AKEY} "
        "{KEY}, and every {KEY} has {AVAL} {VAL}.",
        "The {SECTL} list.\n\n{LINES}\n\n{FALLBACK}",
        "Note.\n\nRead the list above and nothing else. Do not guess {AVAL} "
        "{VAL} from how {AKEY} {KEY} is spelled.",
        "When {AKEY} {KEY} is not on the list, the {VAL} is {D}.",
    ),
}

# --------------------------------------------------------------- exception

EXC_GENERAL = {
    "g_native":   "Every {ENT} is {VGIVEP} the {G} {VAL}.",
    "g_all":      "All {ents} take the {G} {VAL}.",
    "g_default":  "By default, every {ENT} is {VGIVEP} the {G} {VAL}.",
    "g_standard": "The standard {VAL} is {G}.",
    "g_normally": "{Acap} {ENT} normally takes the {G} {VAL}.",
    "g_colon":    "Default {VAL}: {G}.",
}

EXC_SPECIAL = {
    "e_native":  ("There is one exception. {Acap} {ENT} whose {KEY} is {SK} "
                  "is {VGIVEP} the {SP} {VAL} instead."),
    "e_departs": ("One {KEY} departs from this. {Acap} {ENT} of {KEY} {SK} "
                  "takes the {SP} {VAL}."),
    "e_except":  "Except when the {KEY} is {SK}: then the {VAL} is {SP}.",
    "e_ifuse":   "If the {KEY} is {SK}, use the {SP} {VAL} instead.",
    "e_colon":   "Exception: {KEY} {SK} gives {VAL} {SP}.",
    "e_only":    ("The {SP} {VAL} is used for {ents} of {KEY} {SK}, and for "
                  "no others."),
}

EXC_QUESTIONS = {
    "qe_native":    ("{Acap} {ENT} of {KEY} {q} {VREACH3} the {N} {DOM}. "
                     "Which {VAL} does it {VRECV}?"),
    "qe_direct":    ("Which {VAL} does {A} {ENT} of {KEY} {q} {VRECV} in the "
                     "{N} {DOM}?"),
    "qe_imper":     ("{VIMP} {A} {ENT} whose {KEY} is {q} to the {N} {DOM}. "
                     "Name the {VAL}."),
    "qe_consider":  ("Consider {A} {ENT} marked {q} at the {N} {DOM}. "
                     "Which {VAL} does it {VRECV}?"),
    "qe_postposed": ("In the {N} {DOM}, which {VAL} does {A} {ENT} of {KEY} "
                     "{q} {VRECV}?"),
}

EXC_LAYOUTS = {
    "LE_native": (
        "The {N} {DOM}.\n\n{ENTS} {VREACHP} the {N} {DOM} are marked with "
        "{AKEY} {KEY} word.",
        ("The general rule.", "GEN"),
        ("The exception.", "SPC"),
    ),
    "LE_swapped": (
        "{N} {DOM}\n\nEvery {ENT} at the {N} {DOM} carries {AKEY} {KEY} word.",
        ("The exception.", "SPC"),
        ("The general rule.", "GEN"),
    ),
    "LE_terse": (
        "About the {N} {DOM}.\n\nEvery {ENT} {VREACHP} the {N} {DOM} carries "
        "{AKEY} {KEY} word.",
        ("Rule.", "GEN"),
        ("Override.", "SPC"),
    ),
}

# --------------------------------------------------------------- threshold

THR_STATEMENTS = {
    "t_native":   ("{Acap} {ENT} whose {ATTR} {MEAS} is greater than {L} is "
                   "{VCALL} {HI}. {Acap} {ENT} whose {ATTR} {MEAS} is {L} or "
                   "less is {VCALL} {LO}."),
    "t_ifelse":   ("If the {ATTR} {MEAS} exceeds {L}, the {ENT} is {VCALL} "
                   "{HI}; otherwise it is {VCALL} {LO}."),
    "t_colon":    "{MEASC} above {L}: {HI}. {MEASC} of {L} or below: {LO}.",
    "t_lowfirst": ("{Acap} {ENT} at or under {L} on {ATTR} is {VCALL} {LO}. "
                   "Above {L} it is {VCALL} {HI}."),
    "t_any":      ("Any {ENT} whose {ATTR} {MEAS} is over {L} is {VCALL} {HI}, "
                   "and any other {ENT} is {VCALL} {LO}."),
}

THR_QUESTIONS = {
    "qt_native":   ("{Acap} {ENT} has a {ATTR} {MEAS} of {q}. In the {N} "
                    "{DOM}, what is it {VCALL}?"),
    "qt_direct":   ("In the {N} {DOM}, what is {A} {ENT} whose {ATTR} {MEAS} "
                    "is {q} {VCALL}?"),
    "qt_imper":    ("Take {A} {ENT} whose {ATTR} {MEAS} is {q} into the {N} "
                    "{DOM}. Name what it is {VCALL}."),
    "qt_consider": ("Consider {A} {ENT} with a {ATTR} {MEAS} of {q} at the "
                    "{N} {DOM}. What is it {VCALL}?"),
}

THR_LAYOUTS = {
    "LT_native": (
        "The {N} {DOM}.\n\nEvery {ENT} in the {N} {DOM} {VHAS} a {ATTR} "
        "{MEAS}, which is a whole number.",
        ("The rule.", "RULE"),
        ("A worked example.", "EX"),
    ),
    "LT_examplefirst": (
        "{N} {DOM}\n\nEvery {ENT} at the {N} {DOM} {VHAS} a {ATTR} {MEAS}, "
        "which is a whole number.",
        ("A worked example.", "EX"),
        ("The rule.", "RULE"),
    ),
    "LT_terse": (
        "About the {N} {DOM}.\n\nEvery {ENT} in the {N} {DOM} {VHAS} a {ATTR} "
        "{MEAS}, a whole number.",
        ("Rule.", "RULE"),
        ("Example.", "EX"),
    ),
}

THR_EXAMPLE = "{Acap} {ENT} with a {ATTR} {MEAS} of {L7} is {HI}."


@dataclass(frozen=True)
class Shape:
    """One coherent point in the sentence-shape space, across all families."""

    name: str
    sub_stmt: str
    sub_q: str
    sub_layout: str
    exc_gen: str
    exc_spc: str
    exc_q: str
    exc_layout: str
    thr_stmt: str
    thr_q: str
    thr_layout: str


SHAPES: dict[str, Shape] = {s.name: s for s in [
    Shape("native", "s_passive", "q_arrival", "L_native",
          "g_native", "e_native", "qe_native", "LE_native",
          "t_native", "qt_native", "LT_native"),
    Shape("postvalue", "s_passivepost", "q_arrival", "L_native",
          "g_standard", "e_native", "qe_native", "LE_native",
          "t_native", "qt_native", "LT_native"),
    Shape("keyphrase", "s_passive", "q_keyphrase", "L_native",
          "g_native", "e_native", "qe_direct", "LE_native",
          "t_native", "qt_direct", "LT_native"),
    Shape("active", "s_active", "q_direct", "L_native",
          "g_all", "e_departs", "qe_direct", "LE_native",
          "t_ifelse", "qt_direct", "LT_native"),
    Shape("conditional", "s_cond", "q_consider", "L_terse",
          "g_default", "e_ifuse", "qe_consider", "LE_terse",
          "t_ifelse", "qt_consider", "LT_terse"),
    Shape("condthen", "s_condthen", "q_bywhich", "L_terse",
          "g_normally", "e_except", "qe_postposed", "LE_terse",
          "t_any", "qt_direct", "LT_terse"),
    Shape("tablecolon", "s_colon", "q_direct", "L_fallbackfirst",
          "g_colon", "e_colon", "qe_direct", "LE_swapped",
          "t_colon", "qt_direct", "LT_examplefirst"),
    Shape("tablepipe", "s_pipe", "q_postposed", "L_fallbackfirst",
          "g_colon", "e_colon", "qe_postposed", "LE_swapped",
          "t_colon", "qt_consider", "LT_examplefirst"),
    Shape("imperative", "s_imper", "q_imper", "L_terse",
          "g_default", "e_ifuse", "qe_imper", "LE_terse",
          "t_lowfirst", "qt_imper", "LT_terse"),
    Shape("relative", "s_rel", "q_consider", "L_native",
          "g_normally", "e_departs", "qe_consider", "LE_native",
          "t_lowfirst", "qt_consider", "LT_native"),
    Shape("valuefirst", "s_valfirst", "q_postposed", "L_fallbackfirst",
          "g_standard", "e_only", "qe_postposed", "LE_swapped",
          "t_lowfirst", "qt_direct", "LT_examplefirst"),
    Shape("pairs", "s_pairs", "q_direct", "L_fallbackfirst",
          "g_all", "e_except", "qe_direct", "LE_swapped",
          "t_colon", "qt_native", "LT_examplefirst"),
]}

NATIVE_SHAPE = "native"
