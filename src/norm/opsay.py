"""The page that defines an operation, and the question that uses it.

The directories an operation reads are ordinary corpus pages: they are written
by `src/corpus/frames_default.py` through `Frame.page`, so they are byte
identical to what the corpus writes for a two directory agreement instance and
the normalizer has read thousands of them. Only two things in an episode are
new: the page that states the operation, and the question that names it.

The definition page has four wording modes. Three of them, `protocol`, `list`
and `imperative`, are the ones `src/norm/opread.py` was written against. The
fourth, `relative`, is written here and is never read: it is the control that
says what a hand written reader costs when the wording moves, which is the
whole reason the architecture puts a network in front of the library.

Everything that varies with the frame varies here too. The nouns come from that
frame's own lexicon, the question form follows the frame's question axis, and
the definition page sits before or after the directories according to an axis
of its own. What does not vary is the condition and result vocabulary, which is
fixed by `src/norm/oplang.py` and is the same in all four modes.
"""

from __future__ import annotations

from src.corpus.relations import Fact
from src.norm.render import frame_by_id, frames

NUMBER = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}

MODES = ("protocol", "list", "imperative", "relative")
READ_MODES = ("protocol", "list", "imperative")
HELD_MODE = "relative"

NAME_LINE = {
    "protocol": "This {system} states one operation, written {op}.",
    "list": "Operation: {op}.",
    "imperative": "Use the operation {op} as set out here.",
    "relative": "The operation this {system} is for is the one written {op}.",
}

READ_LINE = {
    "protocol": "To take the {op} of a {item}, read {list}.",
    "list": "The {op} of a {item} is computed from {list}.",
    "imperative": "To give the {op} of a {item}, take {list}.",
    "relative": "The readings a {item} brings to this {system} are {list}.",
}

CLAUSE_LINE = {
    "protocol": "If {cond}, the {op} of that {item} is {res}.",
    "list": "Rule {n}. When {cond}, {op} is {res}.",
    "imperative": "When {cond}, give {res} as the {op}.",
    "relative": "A {item} for which {cond} is one whose {op} is {res}.",
}

FALLBACK_LINE = {
    "protocol": "Otherwise the {op} of that {item} is {res}.",
    "list": "Rule {n}. In any other case, {op} is {res}.",
    "imperative": "In every other case give {res} as the {op}.",
    "relative": "A {item} that fits none of these is one whose {op} is {res}.",
}

HEAD = "The {name} {system}."

Q_SINGLE = (
    "What is the {op} of the {k} {item}?",
    "Give the {op} of the {k} {item}.",
    "For the {k} {item}, state its {op}.",
    "A {k} {item} arrives. What is its {op}?",
)

Q_ITER = (
    "Take the {op} of the {k} {item}, then the {op} of that answer, and go on "
    "in the same way for {n} rounds in all. What is the last answer?",
    "Apply {op} to the {k} {item}, then to each answer in turn, {n} times in "
    "all. Give the last answer.",
    "Starting from the {k} {item}, take {op} {n} times over, feeding each "
    "answer back in. What comes out?",
    "The {k} {item} is put through {op} {n} times, each pass reading the "
    "answer of the one before. What is the final answer?",
)

Q_COMPOSE = (
    "What is the {op2} of the {op1} of the {k} {item}?",
    "Take the {op1} of the {k} {item}, then give the {op2} of that answer.",
    "For the {k} {item}, state the {op2} of its {op1}.",
    "A {k} {item} arrives. What is the {op2} of its {op1}?",
)

_QFORMS = None


def qforms() -> tuple:
    """The frame bank's question axis, in a fixed order."""
    global _QFORMS
    if _QFORMS is None:
        fr, _ = frames()
        _QFORMS = tuple(sorted({f.qform for f in fr}))
    return _QFORMS


def qindex(fid: str) -> int:
    fr = frame_by_id(fid)
    return qforms().index(fr.qform)


# ------------------------------------------------------------- phrasing


def _join(parts) -> str:
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + " and " + parts[-1]


def reading_list(fid: str, sources) -> str:
    lx = frame_by_id(fid).lx
    return _join([f"its {lx['target']} at the {s} {lx['container']}"
                  for s in sources])


def cond_phrase(fid: str, cond, sources) -> str:
    lx = frame_by_id(fid).lx
    m = len(sources)
    words = NUMBER[m]
    if cond[0] == "all_same":
        return (f"the {words} readings are the same" if m == 2
                else f"all {words} readings are the same")
    if cond[0] == "all_diff":
        return (f"the {words} readings differ" if m == 2
                else f"no two of the {words} readings are the same")
    a, b = sources[cond[1] - 1], sources[cond[2] - 1]
    tail = "are the same" if cond[0] == "same" else "differ"
    return (f"the reading at the {a} {lx['container']} and the reading at "
            f"the {b} {lx['container']} {tail}")


def res_phrase(fid: str, res, sources) -> str:
    lx = frame_by_id(fid).lx
    if res[0] == "src":
        return f"the reading at the {sources[res[1] - 1]} {lx['container']}"
    if res[0] == "shared":
        return "that shared reading"
    return str(res[1])


# ------------------------------------------------------------ the pages


def definition_page(spec, fid: str, mode: str, page_name: str) -> str:
    """The page that states one operation, in one wording mode."""
    fr = frame_by_id(fid)
    lx = fr.lx
    lines = [fr._fmt(HEAD, name=page_name),
             fr._fmt(NAME_LINE[mode], op=spec.name),
             fr._fmt(READ_LINE[mode], op=spec.name,
                     list=reading_list(fid, spec.sources))]
    n = 1
    for cond, res in spec.clauses:
        lines.append(fr._fmt(CLAUSE_LINE[mode], op=spec.name, n=n,
                             cond=cond_phrase(fid, cond, spec.sources),
                             res=res_phrase(fid, res, spec.sources)))
        n += 1
    lines.append(fr._fmt(FALLBACK_LINE[mode], op=spec.name, n=n,
                         res=res_phrase(fid, spec.fallback, spec.sources)))
    return lines[0] + "\n\n" + "\n".join(lines[1:])


def directory_page(table, fid: str, preamble_level: int = 1) -> str:
    """One directory, written by the corpus frame itself."""
    fr = frame_by_id(fid)
    facts = [Fact("assoc", table.name, k, v) for k, v in table.entries]
    return fr.page(table.name, facts, preamble_level)


def question_single(spec, fid: str, key: str) -> str:
    fr = frame_by_id(fid)
    return fr._fmt(Q_SINGLE[qindex(fid)], op=spec.name, k=key)


def question_iterate(spec, fid: str, key: str, n: int) -> str:
    fr = frame_by_id(fid)
    return fr._fmt(Q_ITER[qindex(fid)], op=spec.name, k=key, n=n)


def question_compose(sp1, sp2, fid: str, key: str) -> str:
    fr = frame_by_id(fid)
    return fr._fmt(Q_COMPOSE[qindex(fid)], op1=sp1.name, op2=sp2.name, k=key)


def episode_text(pages, definition_pages, question: str,
                 def_pos: str = "last") -> str:
    """One episode's serving text: directories, the definition, the question.

    Nothing marks where a page ends except the sentences themselves, which is
    the serving form `src/norm/render.py` already uses.
    """
    blocks = list(pages)
    if def_pos == "first":
        blocks = list(definition_pages) + blocks
    else:
        blocks = blocks + list(definition_pages)
    return "\n\n".join(blocks + [question])
