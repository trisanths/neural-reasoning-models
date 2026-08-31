"""Reading a page that defines an operation, and using what it says.

This is the normalizer for the new lane, written by hand. It is handed an
episode's text and the frame id and nothing else: not the shape, not the
operation, not which pages matter. It reads the directories with the corpus
fact templates that `src/norm/parse.py` already inverts, reads the definition
page with the templates of `src/norm/opsay.py`, puts what it read into an
episode scoped `Library`, and assembles the plan the question asks for.

What it knows and what it does not is the whole point, so it is worth being
exact about it. It knows the definition grammar: three of the four wording
modes, the fixed condition vocabulary, the fixed result vocabulary. It does not
know any operation. The operator's name, how many directories it reads, which
ones, in what order, which conditions it tests, in what order, what each clause
answers and what it answers when no clause fires are all read off the page, and
there is no branch anywhere below that names a particular operation.

Every failure raises `NormError` and is reported as a refusal, so a page this
reader cannot read never becomes a guess.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.norm import oplang, opsay
from src.norm.interp import Result, run
from src.norm.lang import NormError, Table
from src.norm.parse import ParseError, patterns, read_fact
from src.norm.render import frame_by_id

SCOPE = r"([A-Z][A-Za-z0-9]*)"
WORD = r"([a-z][a-z0-9]*)"
INT = r"(-?\d+)"
FREE = r"(.*?)"


@dataclass(frozen=True)
class Read:
    ok: bool
    program: object = None
    kind: str = ""
    library: object = None
    reason: str = ""
    stage: str = ""      # which step refused: pages, definition, question, plan


# ------------------------------------------------------------- patterns

_CACHE: dict = {}


def _rx(tmpl: str, lx: dict, slots: dict):
    """A regex for one of this lane's templates, built from the template."""
    fill = dict(lx)
    names = list(slots)
    for i, n in enumerate(names):
        fill[n] = f"\x00{i}\x00"
    parts = re.split("\x00(\\d+)\x00", tmpl.format(**fill))
    rx, order = [], []
    for j, part in enumerate(parts):
        if j % 2 == 0:
            rx.append(re.escape(part))
        else:
            n = names[int(part)]
            rx.append(slots[n])
            order.append(n)
    return re.compile("^" + "".join(rx) + "$", re.S), tuple(order)


def _match(pat, order, text):
    m = pat.match(text)
    if m is None:
        return None
    out = {}
    for name, val in zip(order, m.groups()):
        if name in out and out[name] != val:
            return None
        out[name] = val
    return out


def op_patterns(fid: str) -> dict:
    if fid in _CACHE:
        return _CACHE[fid]
    fr = frame_by_id(fid)
    lx = dict(fr.lx)
    cont = re.escape(lx["container"])
    out = {
        "lx": lx,
        "dir_head": _rx("The {scope} {container}.", lx, {"scope": SCOPE}),
        "def_head": _rx(opsay.HEAD, lx, {"name": SCOPE}),
        "name": {m: _rx(opsay.NAME_LINE[m], lx, {"op": WORD})
                 for m in opsay.READ_MODES},
        "read": {m: _rx(opsay.READ_LINE[m], lx, {"op": WORD, "list": FREE})
                 for m in opsay.READ_MODES},
        "clause": {m: _rx(opsay.CLAUSE_LINE[m], lx,
                          {"op": WORD, "n": INT, "cond": FREE, "res": FREE})
                   for m in opsay.READ_MODES},
        "fallback": {m: _rx(opsay.FALLBACK_LINE[m], lx,
                            {"op": WORD, "n": INT, "res": FREE})
                     for m in opsay.READ_MODES},
        "source": re.compile(r"its " + re.escape(lx["target"])
                             + r" at the " + SCOPE + r" " + cont + r"$"),
        "src_res": re.compile(r"^the reading at the " + SCOPE + r" "
                              + cont + r"$"),
        "pair_cond": re.compile(r"^the reading at the " + SCOPE + r" " + cont
                                + r" and the reading at the " + SCOPE + r" "
                                + cont + r" (are the same|differ)$"),
        "questions": [],
    }
    for i, t in enumerate(opsay.Q_SINGLE):
        out["questions"].append(("single", i,
                                 _rx(t, lx, {"op": WORD, "k": WORD})))
    for i, t in enumerate(opsay.Q_ITER):
        out["questions"].append(("iterate", i,
                                 _rx(t, lx, {"op": WORD, "k": WORD,
                                             "n": INT})))
    for i, t in enumerate(opsay.Q_COMPOSE):
        out["questions"].append(("compose", i,
                                 _rx(t, lx, {"op1": WORD, "op2": WORD,
                                             "k": WORD})))
    _CACHE[fid] = out
    return out


# ------------------------------------------------------- the definition


def _sources(P: dict, text: str) -> tuple:
    """The directories a reading list names, in the order it names them."""
    parts = [p.strip() for p in re.split(r", | and ", text) if p.strip()]
    out = []
    for p in parts:
        m = P["source"].match(p)
        if m is None:
            raise NormError(f"cannot read the reading {p!r}")
        out.append(m.group(1))
    if len(out) < 2:
        raise NormError("an operation reads at least two directories")
    return tuple(out)


def _cond(P: dict, text: str, sources) -> tuple:
    m = len(sources)
    words = opsay.NUMBER[m]
    if text == (f"the {words} readings are the same" if m == 2
                else f"all {words} readings are the same"):
        return ("all_same",)
    if text == (f"the {words} readings differ" if m == 2
                else f"no two of the {words} readings are the same"):
        return ("all_diff",)
    g = P["pair_cond"].match(text)
    if g is None:
        raise NormError(f"cannot read the condition {text!r}")
    a, b, tail = g.group(1), g.group(2), g.group(3)
    if a not in sources or b not in sources:
        raise NormError("a condition names a directory the operation "
                        "does not read")
    i, j = sources.index(a) + 1, sources.index(b) + 1
    return (("same" if tail == "are the same" else "diff"), i, j)


def _result(P: dict, text: str, sources, cond) -> tuple:
    g = P["src_res"].match(text)
    if g is not None:
        s = g.group(1)
        if s not in sources:
            raise NormError("a result names a directory the operation "
                            "does not read")
        return ("src", sources.index(s) + 1)
    if text == "that shared reading":
        if cond is None or not oplang.is_same_cond(cond):
            raise NormError("a shared reading is named where nothing "
                            "was found shared")
        return ("shared", oplang.shared_index(cond))
    if re.fullmatch(r"[a-z][a-z0-9]*", text):
        return ("word", text)
    raise NormError(f"cannot read the result {text!r}")


def read_definition(P: dict, name: str, lines) -> object:
    """One definition page as a specification. The mode is inferred, not given."""
    for mode in opsay.READ_MODES:
        got = _match(*P["name"][mode], lines[0])
        if got is None:
            continue
        op = got["op"]
        got = _match(*P["read"][mode], lines[1])
        if got is None or got["op"] != op:
            raise NormError("the page names an operation and then reads for "
                            "a different one")
        sources = _sources(P, got["list"])
        clauses = []
        fallback = None
        for k, line in enumerate(lines[2:]):
            g = _match(*P["clause"][mode], line)
            if g is not None:
                if fallback is not None:
                    raise NormError("a clause is stated after the last case")
                if g["op"] != op:
                    raise NormError("a clause names another operation")
                if "n" in g and int(g["n"]) != len(clauses) + 1:
                    raise NormError("the clauses are not in order")
                cond = _cond(P, g["cond"], sources)
                clauses.append((cond, _result(P, g["res"], sources, cond)))
                continue
            g = _match(*P["fallback"][mode], line)
            if g is None:
                raise NormError(f"cannot read the line {line!r}")
            if g["op"] != op:
                raise NormError("the last case names another operation")
            if fallback is not None:
                raise NormError("the page states two last cases")
            fallback = _result(P, g["res"], sources, None)
        if not clauses:
            raise NormError("the page states no condition")
        if fallback is None:
            raise NormError("the page states no last case")
        return oplang.OpSpec(op, sources, tuple(clauses), fallback)
    raise NormError("no definition template reads this page")


# ------------------------------------------------------------- the text


def split_blocks(P: dict, chunks):
    """(directories, definitions) as (name, body lines), in page order."""
    heads = []
    for i, c in enumerate(chunks):
        got = _match(*P["dir_head"], c)
        if got is not None:
            heads.append((i, "dir", got["scope"]))
            continue
        got = _match(*P["def_head"], c)
        if got is not None:
            heads.append((i, "def", got["name"]))
    if not heads or heads[0][0] != 0:
        raise NormError("the text does not begin with a page head")
    dirs, defs = [], []
    for j, (h, kind, name) in enumerate(heads):
        stop = heads[j + 1][0] if j + 1 < len(heads) else len(chunks)
        body = chunks[h + 1:stop]
        if not body:
            raise NormError("a page states nothing")
        lines = body[-1].split("\n")
        (dirs if kind == "dir" else defs).append((name, lines))
    return dirs, defs


def read_tables(P: dict, dirs) -> dict:
    """Directories by name. A page that will not read is kept as its refusal."""
    out = {}
    for name, lines in dirs:
        if name in out:
            raise NormError(f"two directories are called {name}")
        try:
            head = P["parse"]["header"]
            if head is not None and lines and lines[0] == head:
                lines = lines[1:]
            rows = []
            for ln in lines:
                kind, payload = read_fact(P["parse"], ln)
                if kind != "assoc":
                    raise NormError(f"a directory states a {kind} line")
                rows.append(payload)
            out[name] = Table(name, tuple(rows))
        except (ParseError, NormError) as exc:
            out[name] = NormError(str(exc))
    return out


def _need(tables: dict, names):
    out = []
    for n in names:
        t = tables.get(n)
        if t is None:
            raise NormError(f"the operation reads {n}, which is not served")
        if isinstance(t, NormError):
            raise NormError(f"directory {n}: {t}")
        out.append(t)
    return tuple(out)


def read_question(P: dict, chunk: str):
    hits = []
    for kind, i, (pat, order) in P["questions"]:
        got = _match(pat, order, chunk)
        if got is not None:
            hits.append((kind, got))
    if not hits:
        raise NormError("no question template reads the question")
    if len(hits) > 1:
        raise NormError("the question reads as "
                        + " and ".join(k for k, _ in hits))
    return hits[0]


def read(text: str, fid: str) -> Read:
    """Read one episode. Every refusal says which step refused."""
    stage = "pages"
    try:
        P = op_patterns(fid)
        P["parse"] = patterns(fid)
        chunks = text.split("\n\n")
        if len(chunks) < 3:
            raise NormError("too few blocks to be a page and a question")
        dirs, defs = split_blocks(P, chunks[:-1])
        tables = read_tables(P, dirs)
        stage = "definition"
        lib = oplang.Library()
        for name, lines in defs:
            lib.add(read_definition(P, name, lines))
        stage = "question"
        kind, got = read_question(P, chunks[-1])
        stage = "plan"
        if kind == "single":
            spec = lib.get(got["op"])
            prog = oplang.program_single(spec, _need(tables, spec.sources),
                                         got["k"])
        elif kind == "iterate":
            spec = lib.get(got["op"])
            n = int(got["n"])
            if n < 1:
                raise NormError("a run of fewer than one round")
            prog = oplang.program_iterate(spec, _need(tables, spec.sources),
                                          got["k"], n)
        else:
            s1, s2 = lib.get(got["op1"]), lib.get(got["op2"])
            prog = oplang.program_compose(s1, _need(tables, s1.sources),
                                          s2, _need(tables, s2.sources),
                                          got["k"])
        return Read(True, prog, kind, lib, "", "")
    except (NormError, ParseError) as exc:
        return Read(False, None, "", None, str(exc), stage)
    except (KeyError, ValueError, IndexError) as exc:
        return Read(False, None, "", None,
                    f"{type(exc).__name__}: {exc}", stage)


def answer(text: str, fid: str) -> dict:
    """Read the episode and run it. Three outcomes and they are told apart.

    `misread` is the reader refusing, `refused` is the interpreter refusing on
    a structure that was read, and `ran` is an answer. A wrong answer under
    `ran` means the wrong structure was executed, which is a different problem
    from either refusal and is reported as one.
    """
    r = read(text, fid)
    if not r.ok:
        return {"state": "misread", "answer": "", "reason": r.reason,
                "stage": r.stage}
    out: Result = run(r.program)
    if not out.ok:
        return {"state": "refused", "answer": "", "reason": out.reason,
                "stage": "interpreter", "program": r.program,
                "library": r.library}
    return {"state": "ran", "answer": out.text, "reason": "", "stage": "",
            "program": r.program, "library": r.library}
