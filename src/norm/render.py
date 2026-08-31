"""Structure to surface text, through the corpus frame grammar.

Nothing here writes English. The sentences all come from the frame bank that
`src/corpus/frames.py:load_frames` hands over, which is the 768 frame product
of 8 lexicons, 6 statement modes, 2 key positions, 4 question forms and 2 scope
positions in `src/corpus/frames_default.py`. This module turns a
`src/norm/lang.py` program into the `Fact` and `Question` records of
`src/corpus/relations.py` and hands those to a frame, so a rendered structure
is byte identical to what the corpus would have written for the same records.

`classify` reads the plan and names which of the frame grammar's question
shapes it is. Fourteen of the fifteen shapes the grammar has templates for are
renderable and recoverable. The fifteenth, `invert_chain`, shares the
`Q_INVERSE` template with `inverse` and names only the first of its scopes, so
a chain read backwards and a single backwards lookup produce the same sentence;
`src/norm/CORE.md` records that, and `roundtrip.py --witness` prints the pair.
"""

from __future__ import annotations

from src.corpus.frames import load_frames
from src.corpus.relations import Fact, Question
from src.norm.lang import (Affine, Bands, Lit, NormError, OpDef, Program, Ref,
                           Rule, Table, Weights)

SHAPES = ("lookup", "lookup_general", "classify", "inverse", "compose",
          "iterate", "pair", "priority", "exclusion", "lookup_then_band",
          "band_then_lookup", "sum_chain", "apply_n", "precedence")

_FRAMES = None
_BY_ID = None


def frames():
    """The frame bank, loaded once. Also returns which bank supplied it."""
    global _FRAMES, _BY_ID
    if _FRAMES is None:
        fr, src = load_frames()
        _FRAMES = (tuple(fr), src)
        _BY_ID = {f.fid: f for f in fr}
    return _FRAMES


def frame_by_id(fid: str):
    frames()
    return _BY_ID[fid]


# --------------------------------------------------------------- classifying


def _tables(p: Program):
    return [d for d in p.defs if d.kind == "table"]


def classify(p: Program) -> str | None:
    """Which question shape this plan is, or None when the grammar has none."""
    ops = [s.op for s in p.steps]
    if not ops:
        return None
    uniq = set(ops)
    if ops == ["rule"]:
        return "lookup_general"
    if ops == ["band"]:
        return "classify"
    if ops == ["invert"]:
        return "inverse"
    if ops == ["odd_one_out"]:
        return "exclusion"
    if ops == ["prefer"]:
        return "precedence"
    if ops == ["lookup_ordered"]:
        return "priority"
    if ops == ["weigh", "band"]:
        return "lookup_then_band"
    if ops == ["band", "lookup"]:
        return "band_then_lookup"
    if uniq == {"step"}:
        return "apply_n"
    if uniq == {"weigh", "lookup", "add"}:
        return "sum_chain"
    if uniq == {"lookup"}:
        names = [s.args[0] for s in p.steps]
        if len(ops) == 1:
            t = _tables(p)[0]
            return "pair" if t.key_arity == 2 else "lookup"
        return "iterate" if len(set(names)) == 1 else "compose"
    return None


# ------------------------------------------------------------------- facts


def table_facts(t: Table, page: str) -> list:
    out = []
    for i, (k, v) in enumerate(t.entries):
        kind = "assoc2" if isinstance(k, tuple) else "assoc"
        out.append(Fact(kind, page, k, v, rank=i))
    if t.default is not None:
        out.append(Fact("default", page, value=t.default, rank=len(t.entries)))
    return out


def bands_facts(b: Bands, page: str) -> list:
    edges = [None] + list(b.cuts) + [None]
    return [Fact("band", page, attr=b.attr, lo=edges[i], hi=edges[i + 1],
                 value=lab, rank=i) for i, lab in enumerate(b.labels)]


def rule_facts(r: Rule, page: str) -> list:
    out = [Fact("general", page, value=r.general)]
    out += [Fact("except_", page, key=k, value=v) for k, v in r.exceptions]
    return out


def weights_facts(w: Weights, page: str) -> list:
    return [Fact("weight", page, k, v) for k, v in w.entries]


def affine_facts(a: Affine, page: str) -> list:
    return [Fact("step", page, key=("affine", a.a, a.b, a.m))]


# ------------------------------------------------------------ page layout


def _pick(p: Program, kind: str) -> list:
    return [d for d in p.defs if d.kind == kind]


def pages_of(p: Program, shape: str) -> list:
    """(scope, facts) in page order, laid out as the corpus lays them out."""
    if shape in ("lookup", "inverse", "iterate", "pair", "priority",
                 "exclusion"):
        t = _pick(p, "table")[0]
        return [(t.name, table_facts(t, t.name))]
    if shape == "lookup_general":
        r = _pick(p, "rule")[0]
        return [(r.name, rule_facts(r, r.name))]
    if shape == "classify":
        b = _pick(p, "bands")[0]
        return [(b.name, bands_facts(b, b.name))]
    if shape == "compose":
        return [(t.name, table_facts(t, t.name)) for t in _pick(p, "table")]
    if shape == "precedence":
        return [(t.name, table_facts(t, t.name)) for t in _pick(p, "table")]
    if shape == "lookup_then_band":
        w = _pick(p, "weights")[0]
        b = _pick(p, "bands")[0]
        return [(w.name, weights_facts(w, w.name)),
                (b.name, bands_facts(b, b.name))]
    if shape == "band_then_lookup":
        b = _pick(p, "bands")[0]
        t = _pick(p, "table")[0]
        return [(b.name, bands_facts(b, b.name)),
                (t.name, table_facts(t, t.name))]
    if shape == "apply_n":
        a = _pick(p, "affine")[0]
        return [(a.name, affine_facts(a, a.name))]
    if shape == "sum_chain":
        # One page per hop, holding that hop's routing and its weights
        # interleaved key by key, which is how `weighted_chain` writes it.
        out = []
        for t, w in zip(_pick(p, "table"), _pick(p, "weights")):
            if t.name != w.name:
                raise NormError("sum_chain writes a table and its weights on "
                                "one page, so they must share a name")
            facts = []
            wd = dict(w.entries)
            for k, v in t.entries:
                facts.append(Fact("assoc", t.name, k, v))
                facts.append(Fact("weight", t.name, k, wd[k]))
            out.append((t.name, facts))
        return out
    raise NormError(f"no page layout for shape {shape!r}")


# ---------------------------------------------------------------- question


def question_of(p: Program, shape: str) -> Question:
    """The corpus question record this program asks."""
    inputs = dict(p.inputs)
    order = [n for n, _ in p.inputs]
    start = inputs[order[0]]
    key_b = inputs[order[1]] if len(order) > 1 else None
    plan = [{"op": s.op} for s in p.steps]
    meta: dict = {}
    attr = None
    if shape in ("lookup", "inverse", "iterate", "priority", "exclusion",
                 "pair"):
        scopes = [_pick(p, "table")[0].name]
    elif shape == "lookup_general":
        scopes = [_pick(p, "rule")[0].name]
    elif shape == "classify":
        b = _pick(p, "bands")[0]
        scopes, attr = [b.name], b.attr
    elif shape in ("compose", "precedence"):
        scopes = [t.name for t in _pick(p, "table")]
    elif shape == "sum_chain":
        scopes = [t.name for t in _pick(p, "table")]
    elif shape == "lookup_then_band":
        w, b = _pick(p, "weights")[0], _pick(p, "bands")[0]
        scopes, attr = [w.name, b.name], b.attr
    elif shape == "band_then_lookup":
        b, t = _pick(p, "bands")[0], _pick(p, "table")[0]
        scopes, attr = [b.name, t.name], b.attr
    elif shape == "apply_n":
        scopes = [_pick(p, "affine")[0].name]
    else:
        raise NormError(f"no question for shape {shape!r}")
    if shape in ("iterate", "apply_n"):
        meta["n_applications"] = len(p.steps)
    if shape == "pair":
        start = inputs[order[0]]
    if shape == "priority" and not isinstance(start, tuple):
        raise NormError("a priority question starts from a set of groups")
    return Question("q0", shape, scopes, start, None, [], plan,
                    attr=attr, key_b=key_b, meta=meta)


# ------------------------------------------------------------------ render


def render(p: Program, fid: str, preamble_level: int = 1) -> dict:
    """Pages and question for one structure in one frame.

    `text` is the strict serving form: every page and then the question, joined
    the way pages are joined inside a page, so nothing marks where a page ends
    except the sentences themselves. `parse.py` is given `text` and the frame
    id, and nothing else.
    """
    frame = frame_by_id(fid)
    shape = classify(p)
    if shape is None:
        raise NormError("the frame grammar has no question for this plan")
    pages = [frame.page(scope, facts, preamble_level)
             for scope, facts in pages_of(p, shape)]
    q = frame.question(question_of(p, shape))
    return {"fid": fid, "shape": shape, "pages": pages, "question": q,
            "preamble_level": preamble_level,
            "text": "\n\n".join(list(pages) + [q])}
