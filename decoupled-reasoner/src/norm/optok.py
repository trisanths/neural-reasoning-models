"""A target language the network can use to write down a new operation.

`src/norm/ntok.py` has six definition kinds and no way to write an operator, so
the trained normalizer cannot emit a structure for these pages however well it
reads them. This module gives it one. Eleven tokens are appended to the closed
output vocabulary, in that order and after every token the checkpoint already
has, so an existing checkpoint's output embedding is extended by rows rather
than renumbered, and its earlier target streams still mean what they meant.

The form is compact on purpose. An operation is written as its name, how many
readings it takes, its clauses in order and its last case:

    op W3 #2 clause allsame shared #1 fb src #2 ;

rather than as a general expression, which would be four times longer and would
make the network spell out an `if` tree it never has to choose the shape of.
The network is being given the easiest target that can express these pages,
because the measurement is how many examples it needs and a harder target would
be answering a different question.

`serialize` and `deserialize` here mirror the ones in `src/norm/ntok.py`; the
plan, input and answer sections are unchanged, and only the definition section
and the set of legal temporaries differ.

One of the eleven, `endop`, is reserved and never written: the `;` that closes
every other definition closes this one too. It stays in the list because the
checkpoints on the ladder were trained with the vocabulary this size and
removing it would renumber every token after it.
"""

from __future__ import annotations

from src.norm import ntok, oplang
from src.norm.lang import Lit, NormError, Program, Ref, Step
from src.norm.ntok import SLOT_TOKENS, OutVocab, TokenizeError

EXTRA = ("op", "clause", "fb", "allsame", "alldiff", "same", "diff",
         "src", "shared", "word", "endop")
EXTRA_TEMPS = (tuple(f"t{i}" for i in range(17, 65))
               + tuple(f"r{i}" for i in range(1, 17)))


class OpVocab:
    """The normalizer's vocabulary with the operator tokens appended."""

    def __init__(self):
        base = OutVocab()
        self.n_base = len(base.itos)
        toks = list(base.itos)
        for t in EXTRA + EXTRA_TEMPS:
            if t not in toks:
                toks.append(t)
        self.itos = tuple(toks)
        assert len(set(self.itos)) == len(self.itos), "duplicate output token"
        self.stoi = {t: i for i, t in enumerate(self.itos)}
        self.pad = self.stoi["<pad>"]
        self.bos = self.stoi["<bos>"]
        self.eos = self.stoi["<eos>"]

    def __len__(self):
        return len(self.itos)

    def encode(self, toks):
        return [self.stoi[t] for t in toks]

    def decode(self, ids):
        return [self.itos[i] for i in ids]


TEMPS = tuple(ntok.TEMPS) + EXTRA_TEMPS
_TEMPSET = frozenset(TEMPS)


# ------------------------------------------------------------- writing


def _res_tokens(res, slot_of) -> list:
    if res[0] == "src":
        return ["src"] + ntok._num_tokens(res[1])
    if res[0] == "shared":
        return ["shared"] + ntok._num_tokens(res[1])
    if res[0] == "word":
        return ["word", slot_of(res[1])]
    raise NormError(f"no target tokens for result {res!r}")


def _cond_tokens(cond) -> list:
    if cond[0] == "all_same":
        return ["allsame"]
    if cond[0] == "all_diff":
        return ["alldiff"]
    if cond[0] in ("same", "diff"):
        return [cond[0]] + ntok._num_tokens(cond[1]) + ntok._num_tokens(cond[2])
    raise NormError(f"no target tokens for condition {cond!r}")


def spec_tokens(spec, slot_of) -> list:
    out = ["op", slot_of(spec.name)] + ntok._num_tokens(spec.arity)
    for cond, res in spec.clauses:
        out.append("clause")
        out.extend(_cond_tokens(cond))
        out.extend(_res_tokens(res, slot_of))
    out.append("fb")
    out.extend(_res_tokens(spec.fallback, slot_of))
    return out + [";"]


def serialize(p: Program, slots, specs) -> list:
    """Target tokens for one program. `specs` supplies the operations by name."""
    index = {s.lower(): i for i, s in enumerate(slots)}
    by_name = {s.name: s for s in specs}

    def slot_of(sym: str) -> str:
        k = index.get(str(sym).lower())
        if k is None:
            raise TokenizeError(f"symbol {sym!r} is not a slot of the text")
        return SLOT_TOKENS[k]

    out = []
    for d in p.defs:
        if d.kind == "op":
            spec = by_name.get(d.name)
            if spec is None:
                raise TokenizeError(f"no specification for operator {d.name}")
            out.extend(spec_tokens(spec, slot_of))
        else:
            out.extend(ntok._def_tokens(d, slot_of))
    out.append("|")
    for n, v in p.inputs:
        if n not in _TEMPSET:
            raise NormError(f"input name {n!r} is not a canonical temporary")
        out.extend(["in", n])
        out.extend(ntok._value_tokens(v, slot_of))
        out.append(";")
    out.append("|")
    for s in p.steps:
        if s.out not in _TEMPSET:
            raise NormError(f"temporary {s.out!r} is not canonical")
        if s.op not in ntok.OPS:
            raise NormError(f"unknown operation {s.op!r}")
        out.extend([s.out, f"@{s.op}"])
        for a in s.args:
            if isinstance(a, Ref):
                out.append(a.name)
            elif isinstance(a, Lit):
                out.append("lit")
                out.extend(ntok._value_tokens(a.value, slot_of))
            elif isinstance(a, str):
                out.append(slot_of(a))
            else:
                raise NormError(f"unknown argument {a!r}")
        out.append(";")
    out.append("|")
    out.append(p.answer)
    return out


# ------------------------------------------------------------- reading


def _read_res(c):
    kind = c.next()
    if kind in ("src", "shared"):
        return (kind, c.num())
    if kind == "word":
        return ("word", c.sym())
    raise NormError(f"unknown result token {kind!r}")


def _read_cond(c):
    kind = c.next()
    if kind == "allsame":
        return ("all_same",)
    if kind == "alldiff":
        return ("all_diff",)
    if kind in ("same", "diff"):
        return (kind, c.num(), c.num())
    raise NormError(f"unknown condition token {kind!r}")


def _parse_op(c):
    c.expect("op")
    name = c.sym()
    arity = c.num()
    if not 2 <= arity <= 6:
        raise NormError(f"an operation over {arity} readings")
    clauses = []
    while c.peek() == "clause":
        c.next()
        cond = _read_cond(c)
        clauses.append((cond, _read_res(c)))
        if len(clauses) > 8:
            raise NormError("too many clauses")
    c.expect("fb")
    fb = _read_res(c)
    c.expect(";")
    if not clauses:
        raise NormError("an operation with no clause")
    spec = oplang.OpSpec(name, tuple(f"S{i}" for i in range(1, arity + 1)),
                         tuple(clauses), fb)
    for _, r in clauses:
        if r[0] in ("src", "shared") and not 1 <= r[1] <= arity:
            raise NormError("a clause reads a directory the operation lacks")
    if fb[0] in ("src", "shared") and not 1 <= fb[1] <= arity:
        raise NormError("the last case reads a directory the operation lacks")
    for cond, _ in clauses:
        if cond[0] in ("same", "diff") and not (
                1 <= cond[1] <= arity and 1 <= cond[2] <= arity):
            raise NormError("a condition reads a directory the operation lacks")
    return oplang.to_opdef(spec)


def deserialize(toks, slots) -> Program:
    """The program these tokens name. Raises NormError if malformed."""
    c = ntok._Cursor(toks, slots)
    defs = []
    while c.peek() != "|":
        if c.peek() is None:
            raise NormError("target ended before the definitions closed")
        if len(defs) > 64:
            raise NormError("too many definitions")
        defs.append(_parse_op(c) if c.peek() == "op" else ntok._parse_def(c))
    c.expect("|")
    inputs = []
    while c.peek() != "|":
        if c.peek() is None:
            raise NormError("target ended before the inputs closed")
        c.expect("in")
        n = c.next()
        if n not in _TEMPSET:
            raise NormError(f"input name {n!r} is not a canonical temporary")
        inputs.append((n, c.value()))
        c.expect(";")
        if len(inputs) > 8:
            raise NormError("too many inputs")
    c.expect("|")
    steps = []
    while c.peek() != "|":
        if c.peek() is None:
            raise NormError("target ended before the plan closed")
        out = c.next()
        if out not in _TEMPSET:
            raise NormError(f"temporary {out!r} is not canonical")
        op = c.next()
        if op not in ntok.OP_TOKENS:
            raise NormError(f"unknown operation {op!r}")
        args = []
        while c.peek() != ";":
            if c.peek() is None:
                raise NormError("a step that never ended")
            nxt = c.peek()
            if nxt == "lit":
                c.next()
                args.append(Lit(c.value()))
            elif nxt in _TEMPSET:
                args.append(Ref(c.next()))
            else:
                args.append(c.sym())
            if len(args) > 16:
                raise NormError("too many arguments")
        c.expect(";")
        steps.append(Step(out, op[1:], tuple(args)))
        if len(steps) > 256:
            raise NormError("plan too long")
    c.expect("|")
    ans = c.next()
    if ans not in _TEMPSET:
        raise NormError(f"answer name {ans!r} is not a canonical temporary")
    if c.peek() is not None:
        raise NormError("tokens after the answer")
    return Program(tuple(defs), tuple(inputs), tuple(steps), ans)
