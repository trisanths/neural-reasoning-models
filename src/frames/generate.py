"""The frame generator: lexicon x shape, over the src/skillacq rule systems.

A `Frame` is a `src.disc.renderers.SimpleRenderer` in every way that matters,
so a frame can be handed straight to `renderers.simple_episode`. That is
deliberate. The episode file format, the random draw order that fixes which
problems survive rejection, the distractor page, the twin page and the
candidate list all come from the published instrument rather than a lookalike,
so a generated frame and a hand-written renderer are directly comparable and
the gold answers for a seed cannot drift.

The frame decides only how the system is spelled. The system itself is
`src/skillacq/simple.py`, untouched: same invented words, same numbers, same
table entries, same problems, same gold answers.
"""

from __future__ import annotations

import json
import os
import random
import re

from src.disc.renderers import SimpleRenderer, simple_episode
from src.frames.forms import (EXC_GENERAL, EXC_LAYOUTS, EXC_QUESTIONS,
                              EXC_SPECIAL, NATIVE_SHAPE, SHAPES,
                              SUB_LAYOUTS, SUB_QUESTIONS, SUB_STATEMENTS,
                              THR_EXAMPLE, THR_LAYOUTS, THR_QUESTIONS,
                              THR_STATEMENTS, Shape)
from src.frames.lexicon import (LEXICONS, NATIVE_LEXICON, Lexicon, art, cap,
                                plural)

FAMILIES = ("substitution_rule", "exception_rule", "threshold_rule")

# Sentinels for building a reader regex out of a template.
SENT_A = "ZZAZZ"
SENT_B = "ZZBZZ"

# The two families that carry the surface-form conclusion. `threshold_rule` is
# a grading artifact in the native wording (it hedges on every greedy answer,
# see src/disc/TEMPLATE.md section "What the shipped grader counts"), so it is
# generated but never mixed into a headline.
LOAD_BEARING = ("substitution_rule", "exception_rule")


class Frame(SimpleRenderer):
    """One sampled sentence frame: a lexicon spelled in a shape."""

    def __init__(self, lexicon: Lexicon, shape: Shape):
        super().__init__(f"{lexicon.name}__{shape.name}")
        self.lexicon = lexicon
        self.shape = shape

    # ------------------------------------------------------------- slots

    def _sub_slots(self, s) -> dict:
        w = self.lexicon.sub
        return {
            "N": s.name, "DOM": w.dom, "SECT": w.sect, "SECTL": w.sect.lower(),
            "SITE": w.site, "ENT": w.ent, "ENTS": cap(plural(w.ent)),
            "ents": plural(w.ent), "KEY": w.key, "VAL": w.val,
            "VPART": w.vpart, "VPREP": w.vprep, "VACT": w.vact,
            "VIMP": w.vimp, "VSORT": w.vsort, "VSORT3": w.vsort3,
            "VARR": w.varr, "VGO": w.vgo,
            "A": art(w.ent), "Acap": cap(art(w.ent)),
            "AKEY": art(w.key), "AVAL": art(w.val),
            "D": s.rng_default,
        }

    def _exc_slots(self, s) -> dict:
        w = self.lexicon.exc
        return {
            "N": s.name, "DOM": w.dom, "ENT": w.ent, "ENTS": cap(plural(w.ent)),
            "ents": plural(w.ent), "KEY": w.key, "VAL": w.val,
            "VREACH3": w.vreach3, "VREACHP": w.vreachp, "VGIVEP": w.vgivep,
            "VRECV": w.vrecv, "VIMP": w.vimp,
            "A": art(w.ent), "Acap": cap(art(w.ent)),
            "AKEY": art(w.key), "AVAL": art(w.val),
            "G": s.general, "SK": s.special_key, "SP": s.special,
        }

    def _thr_slots(self, s) -> dict:
        w = self.lexicon.thr
        return {
            "N": s.name, "DOM": w.dom, "ENT": w.ent, "MEAS": w.meas,
            "MEASC": cap(w.meas), "VCALL": w.vcall, "VHAS": w.vhas,
            "ATTR": s.attr, "L": s.limit, "L7": s.limit + 7,
            "HI": s.high, "LO": s.low,
            "A": art(w.ent), "Acap": cap(art(w.ent)),
        }

    # ------------------------------------------------------------- pages

    def pages_substitution_rule(self, s) -> list[str]:
        sl = self._sub_slots(s)
        row = SUB_STATEMENTS[self.shape.sub_stmt]
        lines = "\n".join(row.format(k=k, v=v, **sl)
                          for k, v in zip(s.keys, s.values))
        *pages, fallback = SUB_LAYOUTS[self.shape.sub_layout]
        fb = fallback.format(**sl)
        return [t.format(LINES=lines, FALLBACK=fb, **sl) for t in pages]

    def q_substitution_rule(self, s, p: dict) -> str:
        return SUB_QUESTIONS[self.shape.sub_q].format(q=p["key"],
                                                      **self._sub_slots(s))

    def pages_exception_rule(self, s) -> list[str]:
        sl = self._exc_slots(s)
        body = {"GEN": EXC_GENERAL[self.shape.exc_gen].format(**sl),
                "SPC": EXC_SPECIAL[self.shape.exc_spc].format(**sl)}
        head, *rest = EXC_LAYOUTS[self.shape.exc_layout]
        return [head.format(**sl)] + [f"{t.format(**sl)}\n\n{body[which]}"
                                      for t, which in rest]

    def q_exception_rule(self, s, p: dict) -> str:
        return EXC_QUESTIONS[self.shape.exc_q].format(q=p["key"],
                                                      **self._exc_slots(s))

    def pages_threshold_rule(self, s) -> list[str]:
        sl = self._thr_slots(s)
        body = {"RULE": THR_STATEMENTS[self.shape.thr_stmt].format(**sl),
                "EX": THR_EXAMPLE.format(**sl)}
        head, *rest = THR_LAYOUTS[self.shape.thr_layout]
        return [head.format(**sl)] + [f"{t.format(**sl)}\n\n{body[which]}"
                                      for t, which in rest]

    def q_threshold_rule(self, s, p: dict) -> str:
        return THR_QUESTIONS[self.shape.thr_q].format(q=p["value"],
                                                      **self._thr_slots(s))

    # ------------------------------------------------- readers for the
    # trivial-program baseline. A frame can hand out the exact regex that
    # reads its own rule, which is what makes the frame-aware parser in
    # `src/frames/parsers.py` a solvability check rather than a model rival.

    @staticmethod
    def _rx(template: str, slots: dict, **fills) -> str:
        lit = template.format(**{**slots, **fills})
        return (re.escape(lit).replace(SENT_A, r"([A-Za-z]+)")
                .replace(SENT_B, r"([A-Za-z]+)"))

    def row_regex(self, s, key: str) -> str:
        return self._rx(SUB_STATEMENTS[self.shape.sub_stmt],
                        self._sub_slots(s), k=key, v=SENT_A)

    def fallback_regex(self, s) -> str:
        sl = self._sub_slots(s)
        sl["D"] = SENT_A
        return self._rx(SUB_LAYOUTS[self.shape.sub_layout][3], sl)

    def general_regex(self, s) -> str:
        sl = self._exc_slots(s)
        sl["G"] = SENT_A
        return self._rx(EXC_GENERAL[self.shape.exc_gen], sl)

    def special_regex(self, s) -> str:
        """Captures the exception's key then its value, in template order."""
        sl = self._exc_slots(s)
        sl["SK"], sl["SP"] = SENT_A, SENT_B
        tpl = EXC_SPECIAL[self.shape.exc_spc]
        order = ("key", "value") if tpl.index("{SK}") < tpl.index("{SP}") \
            else ("value", "key")
        return self._rx(tpl, sl), order

    def lookup(self, s, key: str) -> str:
        return self.row_regex(s, key)


def build_frames() -> dict[str, Frame]:
    return {f"{lx}__{sh}": Frame(LEXICONS[lx], SHAPES[sh])
            for lx in LEXICONS for sh in SHAPES}


FRAMES: dict[str, Frame] = build_frames()
NATIVE_FRAME = f"{NATIVE_LEXICON}__{NATIVE_SHAPE}"


# ------------------------------------------------------------------ splits


def split_frames(policy: str = "both", seed: int = 20260828,
                 test_lexicons: int = 4, test_shapes: int = 4
                 ) -> dict[str, list[str]]:
    """Partition the frame space so held-out means disjoint by construction.

    `lexicon` holds out whole lexicons, so a test frame shares no domain
    vocabulary bundle with any training frame. `shape` holds out whole
    shapes, so a test frame's sentence geometry never appears in training.
    `both` holds out on each axis and keeps only the frames that are new on
    both, which is the strict split: a test frame shares neither its words
    nor its skeleton with anything trained on.

    The native lexicon and the native shape always stay on the train side,
    because they are the trained surface and the anchor the whole comparison
    is read against.
    """
    rng = random.Random(seed)
    lex = [x for x in sorted(LEXICONS) if x != NATIVE_LEXICON]
    shp = [x for x in sorted(SHAPES) if x != NATIVE_SHAPE]
    rng.shuffle(lex)
    rng.shuffle(shp)
    lex_test = sorted(lex[:test_lexicons])
    shp_test = sorted(shp[:test_shapes])
    lex_train = sorted([NATIVE_LEXICON] + lex[test_lexicons:])
    shp_train = sorted([NATIVE_SHAPE] + shp[test_shapes:])

    train, test = [], []
    for name, fr in FRAMES.items():
        lx, sh = fr.lexicon.name, fr.shape.name
        lx_new, sh_new = lx in lex_test, sh in shp_test
        if policy == "lexicon":
            (test if lx_new else train).append(name)
        elif policy == "shape":
            (test if sh_new else train).append(name)
        elif policy == "both":
            if lx_new and sh_new:
                test.append(name)
            elif not lx_new and not sh_new:
                train.append(name)
            # frames new on exactly one axis are held out of both sides so
            # the split stays clean; they are reported as `bridge`.
        else:
            raise ValueError(f"unknown split policy {policy!r}")
    bridge = sorted(set(FRAMES) - set(train) - set(test))
    return {"policy": policy, "seed": seed,
            "test_lexicons": lex_test, "test_shapes": shp_test,
            "train_lexicons": lex_train, "train_shapes": shp_train,
            "train": sorted(train), "test": sorted(test), "bridge": bridge}


# ----------------------------------------------------------------- writing


def episodes_for(frame: Frame, family: str, seeds: list[int],
                 condition: str, n_problems: int) -> list[dict]:
    """Episodes for one frame and family, delegated to the published builder."""
    out = []
    for s in seeds:
        ep = simple_episode(s, family, frame, n_problems=n_problems,
                            pages=condition)
        ep["frame"] = frame.name
        ep["lexicon"] = frame.lexicon.name
        ep["shape"] = frame.shape.name
        out.append(ep)
    return out


def write_episodes(out_dir: str, frame_names: list[str], families: list[str],
                   seeds: list[int], conditions: list[str],
                   n_problems: int) -> list[dict]:
    os.makedirs(out_dir, exist_ok=True)
    manifest = []
    for fname in frame_names:
        fr = FRAMES[fname]
        for fam in families:
            for cond in conditions:
                eps = episodes_for(fr, fam, seeds, cond, n_problems)
                path = os.path.join(out_dir, f"frames-{fname}-{fam}-{cond}"
                                             ".jsonl")
                with open(path, "w") as fh:
                    for ep in eps:
                        fh.write(json.dumps(ep) + "\n")
                manifest.append({
                    "group": "simple", "renderer": fname, "frame": fname,
                    "lexicon": fr.lexicon.name, "shape": fr.shape.name,
                    "family": fam, "condition": cond, "path": path,
                    "episodes": len(eps),
                    "questions": sum(len(e["questions"]) for e in eps),
                    "candidates": len(eps[0]["candidates"]) if eps else 0,
                })
    with open(os.path.join(out_dir, "manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)
    return manifest
