"""Tokens on both sides of the normalizer.

The network is handed surface text and must emit a typed structure. Both sides
are token sequences here, and neither side is a subword tokenizer.

Input side. The text is split into English words, single digits and single
punctuation marks. The English word list is the union of every frame's own
reserved set, which `src/corpus/lexicon.py:reserved_words` reads off that
frame's templates. An invented word is never in any frame's reserved set, by
construction of `Lexicon`, so the two are disjoint and a token is an invented
word exactly when it is alphabetic and outside the word list. Invented words
are bound to numbered copy slots `W0..W63` in order of first appearance, and
the surface string of each slot travels beside the ids. The network therefore
never sees a nonce spelling and never has to spell one back.

Output side. A closed vocabulary of about two hundred tokens: the definition
kinds, the field markers, the plan operations, the canonical temporary names,
the sixty-four slots and the ten digits. An integer is written `#` and then its
digits, so a value the page states is copied digit by digit rather than looked
up in a table of numbers.

`serialize` and `deserialize` are exact inverses on every program the fourteen
renderable shapes produce, and `src/norm/tests/test_ntok.py` is the gate.
"""

from __future__ import annotations

import re

from src.norm.lang import (Affine, Bands, Lit, NormError, Program, Ref, Rule,
                           Step, Table, Weights)

WORD_RE = re.compile(r"[A-Za-z]+|[0-9]|[^\sA-Za-z0-9]")

MAX_SLOTS = 64
SLOT_TOKENS = tuple(f"W{i}" for i in range(MAX_SLOTS))
DIGITS = tuple(str(i) for i in range(10))


def text_tokens(s: str) -> list:
    """Words, single digits, single punctuation marks."""
    return WORD_RE.findall(s)


class TokenizeError(NormError):
    """Text this tokenizer cannot bind to slots."""


# ------------------------------------------------------------- input side


class InputVocab:
    """English words, digits, punctuation and the copy slots."""

    def __init__(self, english):
        eng = sorted({w.lower() for w in english})
        toks = ["<pad>", "<unk>"]
        toks += list(DIGITS)
        toks += list(" .,;:()'\"-_/?!*+=[]{}<>%&@#$~`|\\^")
        for w in eng:
            toks.append(w)
            toks.append(w.capitalize())
            toks.append(w.upper())
        seen, out = set(), []
        for t in toks:
            if t not in seen:
                seen.add(t)
                out.append(t)
        self.itos = tuple(out) + SLOT_TOKENS
        self.stoi = {t: i for i, t in enumerate(self.itos)}
        self.english = frozenset(eng)
        self.pad = self.stoi["<pad>"]
        self.unk = self.stoi["<unk>"]
        self.slot0 = self.stoi["W0"]

    def __len__(self):
        return len(self.itos)

    def is_nonce(self, tok: str) -> bool:
        return tok.isalpha() and tok.lower() not in self.english

    def encode(self, text: str):
        """(ids, slot surface strings, n unknown English tokens).

        Raises TokenizeError when the text holds more than MAX_SLOTS distinct
        invented words.
        """
        ids, slots, index = [], [], {}
        n_unk = 0
        for tok in text_tokens(text):
            if self.is_nonce(tok):
                low = tok.lower()
                k = index.get(low)
                if k is None:
                    if len(slots) >= MAX_SLOTS:
                        raise TokenizeError("more invented words than slots")
                    k = len(slots)
                    index[low] = k
                    slots.append(tok)
                ids.append(self.slot0 + k)
            else:
                i = self.stoi.get(tok)
                if i is None:
                    i = self.stoi.get(tok.lower(), self.unk)
                if i == self.unk:
                    n_unk += 1
                ids.append(i)
        return ids, slots, n_unk


def english_from_frames(frames) -> frozenset:
    """The union of the frames' own reserved sets."""
    from src.corpus.lexicon import reserved_words
    out: set = set()
    for f in frames:
        out |= reserved_words(f)
    return frozenset(out)


# ------------------------------------------------------------ output side

DEF_TOKENS = ("table", "otable", "bands", "rule", "weights", "affine")
FIELD_TOKENS = ("a1", "a2", "dflt", "cuts", "labels", "gen", "exc", "in",
                "lit", "set", "endset", "true", "false", ";", "|", "#", "-")
OPS = ("lookup", "lookup_ordered", "invert", "odd_one_out", "prefer", "band",
       "weigh", "rule", "step", "add", "sub", "mul", "call")
OP_TOKENS = tuple(f"@{o}" for o in OPS)
TEMPS = (("x", "y")
         + tuple(f"t{i}" for i in range(1, 17))
         + tuple(f"w{i}" for i in range(1, 9))
         + tuple(f"c{i}" for i in range(1, 9))
         + tuple(f"s{i}" for i in range(1, 9)))


class OutVocab:
    """The closed target vocabulary."""

    def __init__(self):
        toks = ["<pad>", "<bos>", "<eos>"]
        toks += list(DIGITS)
        toks += list(FIELD_TOKENS)
        toks += list(DEF_TOKENS)
        toks += list(OP_TOKENS)
        toks += list(TEMPS)
        toks += list(SLOT_TOKENS)
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


# ------------------------------------------------------------- serialising


def _num_tokens(v: int) -> list:
    out = ["#"]
    if v < 0:
        out.append("-")
        v = -v
    out.extend(list(str(v)))
    return out


def _value_tokens(v, slot_of) -> list:
    if isinstance(v, bool):
        return ["true" if v else "false"]
    if isinstance(v, int):
        return _num_tokens(v)
    if isinstance(v, tuple):
        out = ["set"]
        for x in v:
            out.extend(_value_tokens(x, slot_of))
        out.append("endset")
        return out
    if isinstance(v, str):
        return [slot_of(v)]
    raise NormError(f"no target tokens for value {v!r}")


def _def_tokens(d, slot_of) -> list:
    if d.kind == "table":
        out = ["otable" if d.ordered else "table", slot_of(d.name)]
        out.append("a2" if d.key_arity == 2 else "a1")
        for k, v in d.entries:
            if isinstance(k, tuple):
                for part in k:
                    out.append(slot_of(part))
            else:
                out.extend(_value_tokens(k, slot_of))
            out.extend(_value_tokens(v, slot_of))
        if d.default is not None:
            out.append("dflt")
            out.extend(_value_tokens(d.default, slot_of))
        return out + [";"]
    if d.kind == "bands":
        out = ["bands", slot_of(d.name), slot_of(d.attr), "cuts"]
        for c in d.cuts:
            out.extend(_num_tokens(c))
        out.append("labels")
        for lab in d.labels:
            out.append(slot_of(lab))
        return out + [";"]
    if d.kind == "rule":
        out = ["rule", slot_of(d.name), "gen"]
        out.extend(_value_tokens(d.general, slot_of))
        for k, v in d.exceptions:
            out.append("exc")
            out.extend(_value_tokens(k, slot_of))
            out.extend(_value_tokens(v, slot_of))
        return out + [";"]
    if d.kind == "weights":
        out = ["weights", slot_of(d.name)]
        for k, v in d.entries:
            out.extend(_value_tokens(k, slot_of))
            out.extend(_num_tokens(v))
        return out + [";"]
    if d.kind == "affine":
        out = ["affine", slot_of(d.name)]
        for x in (d.a, d.b, d.m):
            out.extend(_num_tokens(x))
        return out + [";"]
    raise NormError(f"no target tokens for definition kind {d.kind!r}")


def serialize(p: Program, slots) -> list:
    """Target tokens for one program, given the slot surface strings."""
    index = {s.lower(): i for i, s in enumerate(slots)}

    def slot_of(sym: str) -> str:
        k = index.get(str(sym).lower())
        if k is None:
            raise TokenizeError(f"symbol {sym!r} is not a slot of the text")
        return SLOT_TOKENS[k]

    out = []
    for d in p.defs:
        out.extend(_def_tokens(d, slot_of))
    out.append("|")
    for n, v in p.inputs:
        if n not in TEMPS:
            raise NormError(f"input name {n!r} is not a canonical temporary")
        out.extend(["in", n])
        out.extend(_value_tokens(v, slot_of))
        out.append(";")
    out.append("|")
    for s in p.steps:
        if s.out not in TEMPS:
            raise NormError(f"temporary {s.out!r} is not canonical")
        if s.op not in OPS:
            raise NormError(f"unknown operation {s.op!r}")
        out.extend([s.out, f"@{s.op}"])
        for a in s.args:
            if isinstance(a, Ref):
                out.append(a.name)
            elif isinstance(a, Lit):
                out.append("lit")
                out.extend(_value_tokens(a.value, slot_of))
            elif isinstance(a, str):
                out.append(slot_of(a))
            else:
                raise NormError(f"unknown argument {a!r}")
        out.append(";")
    out.append("|")
    out.append(p.answer)
    return out


# ------------------------------------------------------------- parsing back


class _Cursor:
    def __init__(self, toks, slots):
        self.t = list(toks)
        self.i = 0
        self.slots = list(slots)

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else None

    def next(self):
        if self.i >= len(self.t):
            raise NormError("target ended early")
        v = self.t[self.i]
        self.i += 1
        return v

    def expect(self, tok):
        v = self.next()
        if v != tok:
            raise NormError(f"expected {tok!r}, found {v!r}")
        return v

    def sym(self):
        v = self.next()
        if not (v.startswith("W") and v[1:].isdigit()):
            raise NormError(f"expected a slot, found {v!r}")
        k = int(v[1:])
        if k >= len(self.slots):
            raise NormError(f"slot {v} is not in the text")
        return self.slots[k]

    def num(self):
        self.expect("#")
        sign = 1
        if self.peek() == "-":
            self.next()
            sign = -1
        ds = []
        while self.peek() in DIGITS:
            ds.append(self.next())
        if not ds:
            raise NormError("a number with no digits")
        return sign * int("".join(ds))

    def value(self):
        v = self.peek()
        if v == "#":
            return self.num()
        if v == "true":
            self.next()
            return True
        if v == "false":
            self.next()
            return False
        if v == "set":
            self.next()
            out = []
            while self.peek() != "endset":
                out.append(self.value())
            self.next()
            return tuple(out)
        return self.sym()


def _parse_def(c: _Cursor):
    kind = c.next()
    if kind in ("table", "otable"):
        name = c.sym()
        arity = c.next()
        if arity not in ("a1", "a2"):
            raise NormError(f"expected an arity, found {arity!r}")
        entries, default = [], None
        while c.peek() not in (";", "dflt"):
            if arity == "a2":
                k = (c.sym(), c.sym())
            else:
                k = c.value()
            entries.append((k, c.value()))
        if c.peek() == "dflt":
            c.next()
            default = c.value()
        c.expect(";")
        return Table(name, tuple(entries), default, kind == "otable")
    if kind == "bands":
        name, attr = c.sym(), c.sym()
        c.expect("cuts")
        cuts = []
        while c.peek() == "#":
            cuts.append(c.num())
        c.expect("labels")
        labels = []
        while c.peek() != ";":
            labels.append(c.sym())
        c.expect(";")
        return Bands(name, attr, tuple(cuts), tuple(labels))
    if kind == "rule":
        name = c.sym()
        c.expect("gen")
        general = c.value()
        exc = []
        while c.peek() == "exc":
            c.next()
            exc.append((c.value(), c.value()))
        c.expect(";")
        return Rule(name, general, tuple(exc))
    if kind == "weights":
        name = c.sym()
        entries = []
        while c.peek() != ";":
            entries.append((c.value(), c.num()))
        c.expect(";")
        return Weights(name, tuple(entries))
    if kind == "affine":
        name = c.sym()
        a, b, m = c.num(), c.num(), c.num()
        c.expect(";")
        return Affine(name, a, b, m)
    raise NormError(f"unknown definition kind {kind!r}")


_TEMPSET = frozenset(TEMPS)


def deserialize(toks, slots) -> Program:
    """The program these target tokens name. Raises NormError if malformed."""
    c = _Cursor(toks, slots)
    defs = []
    while c.peek() != "|":
        if c.peek() is None:
            raise NormError("target ended before the definitions closed")
        if len(defs) > 64:
            raise NormError("too many definitions")
        defs.append(_parse_def(c))
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
        if op not in OP_TOKENS:
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
