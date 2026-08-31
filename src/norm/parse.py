"""The reference parser: surface text back to a structure.

It is handed the rendered text and the frame id, and nothing else. It is not
handed the shape, the question key, the scopes, or any part of the structure.
Every pattern it uses is built mechanically from the frame's own templates in
`src/corpus/frames_default.py`, so the parser covers exactly the frames the
renderer writes and gains nothing from knowing what the generator drew.

This is a reference parser, not a model. It exists to close the round trip:
structure -> render -> structure. Where it cannot read something it refuses and
says why, and a refusal counts as a round trip failure rather than being
silently retried with a looser pattern.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.corpus.frames_default import (ASSOC, ASSOC2, BAND, DEFAULT, EXCEPT,
                                       GENERAL, HEADERS, PREAMBLE_HEAD,
                                       QUESTION_TABLES, STEP, WEIGHT)
from src.norm.lang import Affine, Bands, Program, Rule, Table, Weights
from src.norm.render import SHAPES, frame_by_id, frames
from src.norm.shapes import assemble

SCOPE = r"([A-Z][A-Za-z0-9]*)"
WORD = r"([a-z][a-z0-9]*)"
NAMEY = r"([A-Za-z][A-Za-z0-9]*)"
INT = r"(-?\d+)"
FREE = r"(.*?)"
RANGE = (r"(less than -?\d+|-?\d+ or more but less than -?\d+|"
         r"-?\d+ or more)")
RANGES = r"(under -?\d+|-?\d+ to -?\d+|-?\d+ and over)"
GROUPS = r"([a-z][a-z0-9]*(?:, [a-z][a-z0-9]*)* and [a-z][a-z0-9]*)"

_MARK = re.compile("\x00(\\d+)\x00")


class ParseError(Exception):
    """The text does not read as a structure in this frame."""


@dataclass(frozen=True)
class Parsed:
    ok: bool
    program: object = None
    shape: str = ""
    reason: str = ""


# ------------------------------------------------------- template inversion


def compile_template(tmpl: str, fills: dict, slots: dict):
    """A regex that reads back whatever a frame template wrote.

    `fills` are the words the frame writes literally; `slots` are the pieces
    the structure supplies, each given the pattern its type allows.
    """
    names = list(slots)
    fill = dict(fills)
    for i, n in enumerate(names):
        fill[n] = f"\x00{i}\x00"
    parts = _MARK.split(tmpl.format(**fill))
    rx, order = [], []
    for j, part in enumerate(parts):
        if j % 2 == 0:
            rx.append(re.escape(part))
        else:
            n = names[int(part)]
            rx.append(slots[n])
            order.append(n)
    return re.compile("^" + "".join(rx) + "$", re.S), tuple(order)


def _named(pat, order, text):
    m = pat.match(text)
    if m is None:
        return None
    out: dict = {}
    for name, val in zip(order, m.groups()):
        if name in out and out[name] != val:
            return None
        out[name] = val
    return out


# ----------------------------------------------------------- frame patterns

_CACHE: dict = {}


def patterns(fid: str) -> dict:
    if fid in _CACHE:
        return _CACHE[fid]
    fr = frame_by_id(fid)
    lx = dict(fr.lx)
    m, kp = fr.mode, fr.key_pos
    band_fills = dict(lx, vpass2="is called")
    facts = [
        ("step", compile_template(STEP[m], lx,
                                  {"a": INT, "b": INT, "m": INT})),
        ("except_", compile_template(EXCEPT[m], lx, {"k": WORD, "v": WORD})),
        ("general", compile_template(GENERAL[m], lx, {"v": WORD})),
        ("default", compile_template(DEFAULT[m], lx, {"v": WORD})),
        ("band", compile_template(BAND[m], band_fills,
                                  {"attr": NAMEY, "v": WORD,
                                   "range": RANGE, "range_short": RANGES})),
        ("assoc2", compile_template(ASSOC2[m], lx,
                                    {"k": WORD, "kb": WORD, "v": WORD})),
        ("weight", compile_template(WEIGHT[m], lx, {"k": WORD, "v": INT})),
        ("assoc", compile_template(ASSOC[(m, kp)], lx, {"k": WORD, "v": WORD})),
    ]
    qslots = {
        "lookup": {"k": WORD, "scope": SCOPE},
        "lookup_general": {"k": WORD, "scope": SCOPE},
        "classify": {"k": INT, "attr": NAMEY, "scope": SCOPE},
        "inverse": {"k": WORD, "scope": SCOPE},
        "compose": {"k": WORD, "first": SCOPE, "last": SCOPE,
                    "hops": FREE, "hops2": FREE},
        "iterate": {"k": WORD, "scope": SCOPE, "n": INT},
        "pair": {"k": WORD, "kb": WORD, "scope": SCOPE},
        "priority": {"k": GROUPS, "scope": SCOPE},
        "exclusion": {"k": WORD, "scope": SCOPE},
        "lookup_then_band": {"k": WORD, "first": SCOPE, "last": SCOPE},
        "band_then_lookup": {"k": INT, "attr": NAMEY,
                             "first": SCOPE, "last": SCOPE},
        "sum_chain": {"k": WORD, "first": SCOPE, "hops2": FREE},
        "apply_n": {"k": INT, "scope": SCOPE, "n": INT},
        "precedence": {"k": WORD, "first": SCOPE, "last": SCOPE},
    }
    questions = []
    for kind in SHAPES:
        first_tbl, last_tbl = QUESTION_TABLES[kind]
        tbl = first_tbl if fr.scope_pos == "scope_first" else last_tbl
        questions.append((kind, compile_template(tbl[fr.qform], lx,
                                                 qslots[kind])))
    head = compile_template(PREAMBLE_HEAD, lx, {"scope": SCOPE})
    out = {"frame": fr, "facts": facts, "questions": questions, "head": head,
           "header": fr._fmt(HEADERS[kp]) if m == "table_row" else None}
    _CACHE[fid] = out
    return out


# ------------------------------------------------------------- reading text


def _range_of(text: str):
    m = re.fullmatch(r"less than (-?\d+)", text)
    if m:
        return None, int(m.group(1))
    m = re.fullmatch(r"(-?\d+) or more but less than (-?\d+)", text)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.fullmatch(r"(-?\d+) or more", text)
    if m:
        return int(m.group(1)), None
    m = re.fullmatch(r"under (-?\d+)", text)
    if m:
        return None, int(m.group(1))
    m = re.fullmatch(r"(-?\d+) to (-?\d+)", text)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.fullmatch(r"(-?\d+) and over", text)
    if m:
        return int(m.group(1)), None
    raise ParseError(f"cannot read the range {text!r}")


def read_fact(P: dict, line: str):
    for kind, (pat, order) in P["facts"]:
        got = _named(pat, order, line)
        if got is None:
            continue
        if kind == "step":
            return kind, (int(got["a"]), int(got["b"]), int(got["m"]))
        if kind == "band":
            span = got.get("range") or got.get("range_short")
            lo, hi = _range_of(span)
            return kind, (got.get("attr"), lo, hi, got["v"])
        if kind == "weight":
            return kind, (got["k"], int(got["v"]))
        if kind == "assoc2":
            return kind, ((got["k"], got["kb"]), got["v"])
        if kind == "assoc":
            return kind, (got["k"], got["v"])
        if kind in ("default", "general"):
            return kind, got["v"]
        if kind == "except_":
            return kind, (got["k"], got["v"])
    raise ParseError(f"no fact template reads {line!r}")


def read_pages(P: dict, chunks: list) -> list:
    """(scope, [(kind, payload)]) per page, in page order."""
    hpat, horder = P["head"]
    heads = [i for i, c in enumerate(chunks)
             if _named(hpat, horder, c) is not None]
    if not heads or heads[0] != 0:
        raise ParseError("the text does not begin with a page head")
    pages = []
    for j, h in enumerate(heads):
        stop = heads[j + 1] if j + 1 < len(heads) else len(chunks)
        body = chunks[h + 1:stop]
        if not body:
            raise ParseError("a page states no rules")
        block = body[-1]
        scope = _named(hpat, horder, chunks[h])["scope"]
        lines = block.split("\n")
        if P["header"] is not None and lines and lines[0] == P["header"]:
            lines = lines[1:]
        if not lines:
            raise ParseError("a page states no rules")
        pages.append((scope, [read_fact(P, ln) for ln in lines]))
    return pages


def read_question(P: dict, chunk: str):
    hits = []
    for kind, (pat, order) in P["questions"]:
        got = _named(pat, order, chunk)
        if got is not None:
            hits.append((kind, got))
    if not hits:
        raise ParseError("no question template reads the question")
    if len(hits) > 1:
        raise ParseError("the question reads as "
                         + " and ".join(k for k, _ in hits))
    return hits[0]


def _hop_scopes(P: dict, first: str, got: dict):
    lx = P["frame"].lx
    if "hops" in got:
        text = got["hops"]
        if not text:
            return [first]
        m = re.fullmatch(r" It is then referred to the (.+) "
                         + re.escape(lx["container"]) + r"\.", text)
    else:
        text = got.get("hops2", "")
        if not text:
            return [first]
        m = re.fullmatch(r", then the (.+) " + re.escape(lx["container"]),
                         text)
    if m is None:
        raise ParseError("cannot read the hop clause")
    return [first] + m.group(1).split(", then the ")


# ------------------------------------------------------------- assembling


def _assoc_table(name, facts, ordered=False):
    entries, default = [], None
    for kind, payload in facts:
        if kind in ("assoc", "assoc2"):
            entries.append(payload)
        elif kind == "default":
            default = payload
        else:
            raise ParseError(f"a routing page states a {kind} line")
    return Table(name, tuple(entries), default, ordered)


def _bands_of(name, facts, attr):
    rows = []
    for kind, payload in facts:
        if kind != "band":
            raise ParseError(f"a banding page states a {kind} line")
        rows.append(payload)
    stated = {a for a, _, _, _ in rows if a is not None}
    if len(stated) > 1:
        raise ParseError("a banding page names two attributes")
    if stated:
        seen = stated.pop()
        if attr is not None and seen != attr:
            raise ParseError("the page and the question name different "
                             "attributes")
        attr = seen
    if attr is None:
        raise ParseError("nothing names the banded attribute")
    if rows[0][1] is not None or rows[-1][2] is not None:
        raise ParseError("the outer bands are not open")
    cuts = [hi for _, _, hi, _ in rows[:-1]]
    for i in range(1, len(rows)):
        if rows[i][1] != cuts[i - 1]:
            raise ParseError("the bands do not meet")
    return Bands(name, attr, tuple(cuts), tuple(v for _, _, _, v in rows))


def _weights_of(name, facts):
    out = []
    for kind, payload in facts:
        if kind != "weight":
            raise ParseError(f"a weights page states a {kind} line")
        out.append(payload)
    return Weights(name, tuple(out))


def _split_hop(name, facts):
    """One `sum_chain` page: its routing table and its weights, unpicked."""
    assoc, wts = [], []
    for kind, payload in facts:
        if kind == "assoc":
            assoc.append(payload)
        elif kind == "weight":
            wts.append(payload)
        else:
            raise ParseError(f"a hop page states a {kind} line")
    return Table(name, tuple(assoc)), Weights(name, tuple(wts))


def _groups(text: str) -> tuple:
    head, _, tail = text.rpartition(" and ")
    return tuple([p for p in head.split(", ") if p] + [tail])


def build(P: dict, kind: str, got: dict, pages: list) -> Program:
    names = [s for s, _ in pages]
    if kind in ("lookup", "inverse", "exclusion", "priority", "pair",
                "iterate", "classify", "lookup_general", "apply_n"):
        if len(pages) != 1:
            raise ParseError(f"{kind} wants one page, got {len(pages)}")
        if got["scope"] != names[0]:
            raise ParseError("the question names a page that is not here")
    if kind == "lookup":
        t = _assoc_table(names[0], pages[0][1])
        return assemble("lookup", tables=[t], inputs=(("x", got["k"]),))
    if kind == "inverse":
        t = _assoc_table(names[0], pages[0][1])
        return assemble("inverse", tables=[t], inputs=(("x", got["k"]),))
    if kind == "exclusion":
        t = _assoc_table(names[0], pages[0][1])
        return assemble("exclusion", tables=[t], inputs=(("x", got["k"]),))
    if kind == "priority":
        t = _assoc_table(names[0], pages[0][1], ordered=True)
        return assemble("priority", tables=[t],
                        inputs=(("x", _groups(got["k"])),))
    if kind == "pair":
        t = _assoc_table(names[0], pages[0][1])
        return assemble("pair", tables=[t],
                        inputs=(("x", got["k"]), ("y", got["kb"])))
    if kind == "iterate":
        t = _assoc_table(names[0], pages[0][1])
        return assemble("iterate", tables=[t], inputs=(("x", got["k"]),),
                        n=int(got["n"]))
    if kind == "classify":
        b = _bands_of(names[0], pages[0][1], got.get("attr"))
        return assemble("classify", bands=b, inputs=(("x", int(got["k"])),))
    if kind == "lookup_general":
        general, exc = None, []
        for k, payload in pages[0][1]:
            if k == "general":
                general = payload
            elif k == "except_":
                exc.append(payload)
            else:
                raise ParseError(f"a protocol page states a {k} line")
        if general is None:
            raise ParseError("the protocol page states no general rule")
        return assemble("lookup_general",
                        rule=Rule(names[0], general, tuple(exc)),
                        inputs=(("x", got["k"]),))
    if kind == "apply_n":
        rows = pages[0][1]
        if len(rows) != 1 or rows[0][0] != "step":
            raise ParseError("a pass page states one step line")
        a, b, m = rows[0][1]
        return assemble("apply_n", affine=Affine(names[0], a, b, m),
                        inputs=(("x", int(got["k"])),), n=int(got["n"]))
    if kind in ("compose", "sum_chain"):
        scopes = _hop_scopes(P, got["first"], got)
        if kind == "compose" and got["last"] != scopes[-1]:
            raise ParseError("the question's last hop is not the last scope")
        if scopes != names:
            raise ParseError("the hops named do not match the pages served")
        if kind == "compose":
            tables = [_assoc_table(s, f) for s, f in pages]
            return assemble("compose", tables=tables,
                            inputs=(("x", got["k"]),))
        tables, wts = [], []
        for s, f in pages:
            t, w = _split_hop(s, f)
            tables.append(t)
            wts.append(w)
        return assemble("sum_chain", tables=tables, weights=wts,
                        inputs=(("x", got["k"]),))
    if kind == "precedence":
        if names != [got["first"], got["last"]]:
            raise ParseError("the two pages are not the two named")
        a = _assoc_table(names[0], pages[0][1])
        b = _assoc_table(names[1], pages[1][1])
        return assemble("precedence", tables=[a, b],
                        inputs=(("x", got["k"]),))
    if kind == "lookup_then_band":
        if names != [got["first"], got["last"]]:
            raise ParseError("the two pages are not the two named")
        w = _weights_of(names[0], pages[0][1])
        b = _bands_of(names[1], pages[1][1], names[0])
        return assemble("lookup_then_band", weights=[w], bands=b,
                        inputs=(("x", got["k"]),))
    if kind == "band_then_lookup":
        if names != [got["first"], got["last"]]:
            raise ParseError("the two pages are not the two named")
        b = _bands_of(names[0], pages[0][1], got.get("attr"))
        t = _assoc_table(names[1], pages[1][1])
        return assemble("band_then_lookup", bands=b, tables=[t],
                        inputs=(("x", int(got["k"])),))
    raise ParseError(f"no assembly for {kind!r}")


def parse(text: str, fid: str) -> Parsed:
    """Read one rendered structure back. A refusal is never a guess."""
    try:
        P = patterns(fid)
        chunks = text.split("\n\n")
        if len(chunks) < 3:
            raise ParseError("too few blocks to be a page and a question")
        kind, got = read_question(P, chunks[-1])
        pages = read_pages(P, chunks[:-1])
        return Parsed(True, build(P, kind, got, pages), kind, "")
    except ParseError as exc:
        return Parsed(False, None, "", str(exc))
    except (KeyError, ValueError, IndexError) as exc:
        return Parsed(False, None, "", f"{type(exc).__name__}: {exc}")
