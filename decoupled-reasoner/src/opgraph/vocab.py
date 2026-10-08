"""Six plan representations over the same worlds, operators and executor.

The measured result this ladder sits on is that the executor chains an induced
operator to depth eight without loss once the plan exists, and that essentially
all of the loss is in the model emitting the plan. So the plan is the only
thing that changes here. The worlds, the pages, the questions, the seeds, the
induction half of the training stream, the operator objects and `run_plan` are
untouched.

  A  english        a sentence per step, operators named by their page symbol
  B  symbolic       registers as single letters, operators named by slot, in
                    ordinary vocabulary items
  C  opcode         B exactly, with the operator slot written as a dedicated
                    token carrying a freshly initialised embedding
  D  typed          an instruction format with arity, result type, operands and
                    a destination register, so a malformed plan is detectable
                    before it is executed
  E  goalstack      D plus an obligation state maintained outside the model and
                    a hard ban on emitting termination while an obligation is
                    unresolved
  F  slots          sixteen graph slots whose fields are predicted jointly, with
                    explicit data dependency edges, refined over several passes
                    and executed in topological order

Every representation is a bijection with `Plan` on the plans this project
generates, and every one is checked both ways: `oracle_both` runs the gold plan
through the representation and back, so a lossy encoding shows up as an
oracle_both below 1.000 rather than as a quiet accuracy loss somewhere else.

Dedicated tokens live in the reserved `<|pgN|>` slots the tokenizer already
carries, so no arm resizes the embedding matrix and every arm has exactly the
same parameter count. Conditions C to F re-draw the rows of those tokens from
the model's own initialisation before fine tuning, which is what makes the
embeddings fresh. Conditions A and B touch no reserved token at all.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field

from src.opgraph.data import (IGNORE, induce_prompt, plan_prompt, direct_prompt)
from src.opgraph.invent import (OP_GLYPHS, breadth_item, make_world, seq_flat,
                                seq_paren, units_item)
from src.opgraph.opdef import Call, OpError, Operator, Var, serialize_all
from src.opgraph.plan import (BUILTIN_STEPS, Plan, PlanError, Step,
                              serialize_plan, signature_line)

REPS = ("english", "symbolic", "opcode", "typed", "goalstack", "slots")
ARM_OF_REP = {r: "ladder_" + r for r in REPS}
REP_OF_ARM = {v: k for k, v in ARM_OF_REP.items()}

MAX_OP_SLOTS = 12
MAX_REGS = 16
MAX_LIT = 100
MAX_ARITY = 7
F_SLOTS = 16
F_ROUNDS = 3


# ------------------------------------------------------- reserved token names

_ALLOC: dict[str, str] = {}
_ORDER: list[str] = []


def _reserve(name: str) -> str:
    if name in _ALLOC:
        return _ALLOC[name]
    if len(_ORDER) >= 256:
        raise RuntimeError("out of reserved tokenizer slots")
    _ALLOC[name] = f"<|pg{len(_ORDER)}|>"
    _ORDER.append(name)
    return _ALLOC[name]


OPC = [_reserve(f"op{i}") for i in range(MAX_OP_SLOTS)]
REG = [_reserve(f"r{i}") for i in range(MAX_REGS)]
LIT = [_reserve(f"n{i}") for i in range(MAX_LIT)]
ARI = {i: _reserve(f"a{i}") for i in range(1, MAX_ARITY + 1)}
TYP = {"int": _reserve("tint"), "bool": _reserve("tbool"), "str": _reserve("tstr")}
T_APPLY = _reserve("apply")
T_RET = _reserve("ret")
T_TO = _reserve("to")
T_END = _reserve("end")
T_GOAL = _reserve("goal")
T_SEP = _reserve("sep")
T_NOP = _reserve("nop")
T_NONE = _reserve("none")
T_MASK = _reserve("mask")
T_ROW = _reserve("row")
T_RETF = _reserve("retf")
T_TRUE = _reserve("vtrue")
T_FALSE = _reserve("vfalse")
SLOTID = [_reserve(f"s{i}") for i in range(F_SLOTS)]

_PG_NAME = {v: k for k, v in _ALLOC.items()}
_PG_RE = re.compile(r"<\|pg\d+\|>")

# Which reserved tokens each representation puts in the model's mouth. A
# representation re-initialises exactly these rows and nothing else.
_REP_TOKENS = {
    "english": [],
    "symbolic": [],
    "opcode": OPC,
    "typed": OPC + REG + list(ARI.values()) + list(TYP.values())
             + [T_APPLY, T_RET, T_TO, T_END, T_TRUE, T_FALSE],
    "goalstack": OPC + REG + LIT + list(ARI.values()) + list(TYP.values())
                 + [T_APPLY, T_RET, T_TO, T_END, T_GOAL, T_SEP, T_TRUE, T_FALSE],
    "slots": OPC + REG + LIT + SLOTID
             + [T_NOP, T_NONE, T_MASK, T_ROW, T_RETF, T_TRUE, T_FALSE],
}


def rep_tokens(rep: str) -> list[str]:
    """The reserved token strings one representation uses, deduplicated."""
    seen: dict[str, None] = {}
    for t in _REP_TOKENS[rep]:
        seen[t] = None
    return list(seen)


def lex(text: str) -> list[str]:
    """Split decoded text into tokens, keeping every reserved token whole.

    The tokenizer splices reserved names back verbatim, so they can abut other
    text with no space. Padding them out first makes the split unambiguous.
    """
    return _PG_RE.sub(lambda m: f" {m.group(0)} ", text).split()


class RepError(Exception):
    """A string that is not a well formed plan in this representation."""


# ----------------------------------------------------------- operator types

def param_types(op: Operator) -> tuple[str, ...]:
    """A simple type for each parameter, read off how the body uses it.

    A parameter tested as a condition is boolean, a parameter compared against
    a string is a string, everything else is an integer. That covers every
    operator this project's pages define and degrades to `int` on anything an
    induction invents that it does not.
    """
    kind: dict[str, str | None] = {p: None for p in op.params}

    def walk(e, want: str | None = None) -> None:
        if isinstance(e, Var):
            if want and kind.get(e.name) is None:
                kind[e.name] = want
            return
        if not isinstance(e, Call):
            return
        h = e.head
        if h == "if":
            walk(e.args[0], "bool")
            walk(e.args[1], want)
            walk(e.args[2], want)
        elif h in ("and", "or", "not"):
            for a in e.args:
                walk(a, "bool")
        elif h in ("=", "!="):
            other = {0: 1, 1: 0}
            for i, a in enumerate(e.args):
                o = e.args[other[i]]
                walk(a, "str" if isinstance(o, str) else None)
        else:
            for a in e.args:
                walk(a, "int")

    walk(op.body)
    for c in op.pre:
        walk(c, "bool")
    return tuple(kind[p] or "int" for p in op.params)


def _expr_type(e, ptypes: dict[str, str]) -> str:
    if isinstance(e, bool):
        return "bool"
    if isinstance(e, int):
        return "int"
    if isinstance(e, str):
        return "str"
    if isinstance(e, Var):
        return ptypes.get(e.name, "int")
    if not isinstance(e, Call):
        return "int"
    h = e.head
    if h in (">=", "<=", ">", "<", "=", "!=", "and", "or", "not"):
        return "bool"
    if h == "if":
        a = _expr_type(e.args[1], ptypes)
        b = _expr_type(e.args[2], ptypes)
        return a if a == b else "int"
    return "int"


def op_signature(op: Operator) -> tuple[tuple[str, ...], str]:
    pt = param_types(op)
    return pt, _expr_type(op.body, dict(zip(op.params, pt)))


def signature_of(ops: dict, symbol: str) -> tuple[tuple[str, ...], str]:
    if symbol in BUILTIN_STEPS:
        return ("int", "int"), "int"
    op = ops.get(symbol)
    if op is None:
        raise RepError(f"unknown operator {symbol!r}")
    return op_signature(op)


# ------------------------------------------------------------- slot binding

def slots(ops: dict) -> list[str]:
    """The canonical operator slot order, shared by prompt and plan."""
    return sorted(ops)


def slot_of(ops: dict, symbol: str) -> int:
    order = slots(ops)
    if symbol not in order:
        raise RepError(f"operator {symbol!r} is not in the table")
    i = order.index(symbol)
    if i >= MAX_OP_SLOTS:
        raise RepError(f"operator slot {i} is past the {MAX_OP_SLOTS} available")
    return i


def symbol_of_slot(ops: dict, i: int) -> str:
    order = slots(ops)
    if not 0 <= i < len(order):
        raise RepError(f"no operator in slot {i}")
    return order[i]


# --------------------------------------------------------------- plan pieces

def _reg_index(plan: Plan) -> dict[str, int]:
    return {s.target: i for i, s in enumerate(plan.steps)}


def _arg_is_temp(a) -> bool:
    return isinstance(a, str) and re.fullmatch(r"t\d+", a) is not None


def _arg_type(a, regtypes: list[str]) -> str:
    if isinstance(a, bool):
        return "bool"
    if isinstance(a, int):
        return "int"
    if isinstance(a, tuple):
        return "str"
    return "int"


ORDINALS = [
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
    "seventeen", "eighteen", "nineteen", "twenty", "twenty one", "twenty two",
    "twenty three", "twenty four", "twenty five", "twenty six",
    "twenty seven", "twenty eight", "twenty nine", "thirty", "thirty one",
    "thirty two",
]
_ORDINAL_INDEX = {w: i for i, w in enumerate(ORDINALS)}


# ================================================================ A: english

_A_STEP = re.compile(
    r"^(?:first|then|next|after that|finally)?\s*apply\s+(\S+)\s+to\s+(.+?),"
    r"\s*giving result\s+([a-z ]+?)$")
_A_ANS = re.compile(r"^the answer is\s+(.+?)$")


def _english_arg(a, regs: dict[str, int]) -> str:
    if isinstance(a, bool):
        return "true" if a else "false"
    if isinstance(a, int):
        return str(a)
    if _arg_is_temp(a):
        return "result " + ORDINALS[regs[a]]
    if isinstance(a, tuple):
        return "the word " + str(a[1])
    raise RepError(f"cannot write {a!r} in english")


def _english_join(parts: list[str]) -> str:
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + " and " + parts[-1]


def encode_english(plan: Plan, ops: dict) -> str:
    regs = _reg_index(plan)
    out = []
    for i, s in enumerate(plan.steps):
        lead = "first" if i == 0 else "then"
        args = _english_join([_english_arg(a, regs) for a in s.args])
        out.append(f"{lead} apply {s.symbol} to {args}, giving result "
                   f"{ORDINALS[i]}")
    if _arg_is_temp(plan.answer):
        out.append(f"the answer is result {ORDINALS[regs[plan.answer]]}")
    else:
        out.append(f"the answer is {plan.answer}")
    return " ; ".join(out)


def _parse_english_arg(text: str):
    t = text.strip()
    if t.startswith("result "):
        w = t[len("result "):].strip()
        if w not in _ORDINAL_INDEX:
            raise RepError(f"bad ordinal {w!r}")
        return ("reg", _ORDINAL_INDEX[w])
    if t.startswith("the word "):
        return ("lit", t[len("the word "):].strip())
    if t in ("true", "false"):
        return ("val", t == "true")
    if re.fullmatch(r"-?\d+", t):
        return ("val", int(t))
    raise RepError(f"bad english argument {t!r}")


def _split_english_args(text: str) -> list[str]:
    parts = [p for p in text.split(",")]
    tail = parts[-1].split(" and ")
    return [p.strip() for p in parts[:-1] + tail if p.strip()]


def decode_english(text: str, ops: dict) -> Plan:
    chunks = [c.strip().lower() for c in text.strip().split(";")]
    chunks = [c for c in chunks if c]
    if not chunks:
        raise RepError("empty plan")
    steps: list[Step] = []
    answer = None
    for k, c in enumerate(chunks):
        m = _A_ANS.match(c)
        if m:
            if k != len(chunks) - 1:
                raise RepError("the answer sentence must come last")
            a = _parse_english_arg(m.group(1))
            answer = a
            continue
        m = _A_STEP.match(c)
        if not m:
            raise RepError(f"bad english step {c!r}")
        symbol, args_text, ordinal = m.group(1), m.group(2), m.group(3).strip()
        if _ORDINAL_INDEX.get(ordinal) != len(steps):
            raise RepError("results must be numbered in order")
        args = [_parse_english_arg(a) for a in _split_english_args(args_text)]
        steps.append((_fix_symbol(symbol, ops), args))
    if answer is None:
        raise RepError("plan has no answer sentence")
    return _assemble(steps, answer)


# The english pass lowercases, so an operator glyph is unchanged but a worded
# operator symbol has to be matched back case insensitively.
def _fix_symbol(symbol: str, ops: dict) -> str:
    if symbol in ops or symbol in BUILTIN_STEPS:
        return symbol
    for k in ops:
        if k.lower() == symbol.lower():
            return k
    return symbol


def _assemble(steps, answer, ops: dict | None = None) -> Plan:
    """Turn (symbol, [(kind, value)]) records into a Plan with t1..tn names."""
    out: list[Step] = []
    for i, (symbol, args) in enumerate(steps):
        vals = []
        for kind, v in args:
            if kind == "reg":
                if not 0 <= v < i:
                    raise RepError("step reads a result it does not have yet")
                vals.append(f"t{v + 1}")
            elif kind == "lit":
                vals.append(("lit", v))
            else:
                vals.append(v)
        out.append(Step(f"t{i + 1}", symbol, tuple(vals)))
    kind, v = answer
    if kind == "reg":
        if not 0 <= v < len(out):
            raise RepError("the answer names a result that was never produced")
        ans = f"t{v + 1}"
    elif kind == "lit":
        ans = "'" + str(v)
    else:
        ans = "true" if v is True else "false" if v is False else str(v)
    return Plan(tuple(out), ans)


# =============================================================== B: symbolic

REG_LETTERS = [chr(ord("A") + i) for i in range(26)] + list("abcdef")


def sig_symbolic(ops: dict) -> str:
    parts = []
    for i, k in enumerate(slots(ops)):
        if i >= MAX_OP_SLOTS:
            break
        op = ops[k]
        tail = f"/{op.arity}/{op.assoc}" if op.assoc else f"/{op.arity}"
        parts.append(f"op{i}={k}{tail}")
    return " ".join(parts)


def _sym_arg(a, regs: dict[str, int]) -> str:
    if isinstance(a, bool):
        return "true" if a else "false"
    if isinstance(a, int):
        return str(a)
    if _arg_is_temp(a):
        return REG_LETTERS[regs[a]]
    if isinstance(a, tuple):
        return "'" + str(a[1])
    raise RepError(f"cannot write {a!r} symbolically")


def encode_symbolic(plan: Plan, ops: dict) -> str:
    regs = _reg_index(plan)
    out = []
    for i, s in enumerate(plan.steps):
        args = " ".join(_sym_arg(a, regs) for a in s.args)
        out.append(f"{REG_LETTERS[i]} = op{slot_of(ops, s.symbol)} {args}")
    if _arg_is_temp(plan.answer):
        out.append("ans " + REG_LETTERS[regs[plan.answer]])
    else:
        out.append("ans " + plan.answer)
    return " > ".join(out)


_LETTER_INDEX = {c: i for i, c in enumerate(REG_LETTERS)}


def _parse_sym_arg(t: str):
    if t in ("true", "false"):
        return ("val", t == "true")
    if re.fullmatch(r"-?\d+", t):
        return ("val", int(t))
    if t in _LETTER_INDEX:
        return ("reg", _LETTER_INDEX[t])
    if t.startswith("'"):
        return ("lit", t[1:])
    raise RepError(f"bad symbolic argument {t!r}")


_SLOT_WORD = re.compile(r"^op(\d+)$")


def decode_symbolic(text: str, ops: dict) -> Plan:
    chunks = [c.strip() for c in text.strip().split(">")]
    chunks = [c for c in chunks if c]
    if not chunks:
        raise RepError("empty plan")
    steps = []
    answer = None
    for k, c in enumerate(chunks):
        parts = c.split()
        if parts[0] == "ans":
            if len(parts) != 2 or k != len(chunks) - 1:
                raise RepError("ans must come last and take one value")
            answer = _parse_sym_arg(parts[1])
            continue
        if len(parts) < 3 or parts[1] != "=":
            raise RepError(f"bad symbolic step {c!r}")
        if _LETTER_INDEX.get(parts[0]) != len(steps):
            raise RepError("registers must be written in order")
        m = _SLOT_WORD.match(parts[2])
        if not m:
            raise RepError(f"bad operator slot {parts[2]!r}")
        symbol = symbol_of_slot(ops, int(m.group(1)))
        steps.append((symbol, [_parse_sym_arg(t) for t in parts[3:]]))
    if answer is None:
        raise RepError("plan has no ans")
    return _assemble(steps, answer)


# ================================================================= C: opcode

def sig_opcode(ops: dict) -> str:
    parts = []
    for i, k in enumerate(slots(ops)):
        if i >= MAX_OP_SLOTS:
            break
        op = ops[k]
        tail = f"/{op.arity}/{op.assoc}" if op.assoc else f"/{op.arity}"
        parts.append(f"{OPC[i]} {k}{tail}")
    return " ".join(parts)


def encode_opcode(plan: Plan, ops: dict) -> str:
    regs = _reg_index(plan)
    out = []
    for i, s in enumerate(plan.steps):
        args = " ".join(_sym_arg(a, regs) for a in s.args)
        out.append(f"{REG_LETTERS[i]} = {OPC[slot_of(ops, s.symbol)]} {args}")
    if _arg_is_temp(plan.answer):
        out.append("ans " + REG_LETTERS[regs[plan.answer]])
    else:
        out.append("ans " + plan.answer)
    return " > ".join(out)


def decode_opcode(text: str, ops: dict) -> Plan:
    toks = lex(text)
    chunks: list[list[str]] = [[]]
    for t in toks:
        if t == ">":
            chunks.append([])
        else:
            chunks[-1].append(t)
    chunks = [c for c in chunks if c]
    if not chunks:
        raise RepError("empty plan")
    steps = []
    answer = None
    for k, parts in enumerate(chunks):
        if parts[0] == "ans":
            if len(parts) != 2 or k != len(chunks) - 1:
                raise RepError("ans must come last and take one value")
            answer = _parse_sym_arg(parts[1])
            continue
        if len(parts) < 3 or parts[1] != "=":
            raise RepError(f"bad opcode step {parts!r}")
        if _LETTER_INDEX.get(parts[0]) != len(steps):
            raise RepError("registers must be written in order")
        name = _PG_NAME.get(parts[2], "")
        m = _SLOT_WORD.match(name)
        if not m:
            raise RepError(f"bad opcode {parts[2]!r}")
        symbol = symbol_of_slot(ops, int(m.group(1)))
        steps.append((symbol, [_parse_sym_arg(t) for t in parts[3:]]))
    if answer is None:
        raise RepError("plan has no ans")
    return _assemble(steps, answer)


# ================================================================== D: typed

def sig_typed(ops: dict) -> str:
    parts = []
    for i, k in enumerate(slots(ops)):
        if i >= MAX_OP_SLOTS:
            break
        op = ops[k]
        pt, rt = op_signature(op)
        if op.arity < 1 or op.arity > MAX_ARITY:
            continue
        body = " ".join(TYP[t] for t in pt)
        tail = f" {op.assoc}" if op.assoc else ""
        parts.append(f"{OPC[i]} {k} {ARI[op.arity]} {body} {TYP[rt]}{tail}")
    return " ".join(parts)


def _typed_arg(a, regs: dict[str, int]) -> str:
    if isinstance(a, bool):
        return T_TRUE if a else T_FALSE
    if isinstance(a, int):
        return str(a)
    if _arg_is_temp(a):
        return REG[regs[a]]
    raise RepError(f"cannot write {a!r} in the typed form")


def _typed_instructions(plan: Plan, ops: dict) -> list[str]:
    regs = _reg_index(plan)
    rtypes: list[str] = []
    out = []
    for i, s in enumerate(plan.steps):
        _, rt = signature_of(ops, s.symbol)
        rtypes.append(rt)
        if not 1 <= len(s.args) <= MAX_ARITY:
            raise RepError(f"arity {len(s.args)} is outside the typed form")
        if i >= MAX_REGS:
            raise RepError("plan is longer than the register file")
        args = " ".join(_typed_arg(a, regs) for a in s.args)
        out.append(f"{T_APPLY} {OPC[slot_of(ops, s.symbol)]} {ARI[len(s.args)]} "
                   f"{TYP[rt]} {args} {T_TO} {REG[i]}")
    if _arg_is_temp(plan.answer):
        i = regs[plan.answer]
        out.append(f"{T_RET} {TYP[rtypes[i]]} {REG[i]}")
    else:
        raise RepError("the typed form only returns a register")
    return out


def encode_typed(plan: Plan, ops: dict) -> str:
    return " ".join(ins + " " + T_END for ins in _typed_instructions(plan, ops))


def token_name(tok: str) -> str:
    """The logical name of a reserved token, or the empty string."""
    return _PG_NAME.get(tok, "")


def _name(tok: str) -> str:
    return _PG_NAME.get(tok, "")


def _parse_typed_arg(t: str):
    n = _name(t)
    if n == "vtrue":
        return ("val", True)
    if n == "vfalse":
        return ("val", False)
    m = re.fullmatch(r"r(\d+)", n)
    if m:
        return ("reg", int(m.group(1)))
    if re.fullmatch(r"-?\d+", t):
        return ("val", int(t))
    raise RepError(f"bad typed argument {t!r}")


@dataclass
class TypedPlan:
    """A decoded typed plan, keeping the declarations so they can be checked."""

    plan: Plan
    declared_arity: list[int]
    declared_type: list[str]
    return_type: str


def decode_typed(text: str, ops: dict, drop_goal: bool = False) -> Plan:
    return decode_typed_full(text, ops, drop_goal).plan


def decode_typed_full(text: str, ops: dict, drop_goal: bool = False) -> TypedPlan:
    toks = lex(text)
    if drop_goal:
        toks = _strip_goal(toks)
    groups: list[list[str]] = [[]]
    for t in toks:
        if _name(t) == "end":
            groups.append([])
        else:
            groups[-1].append(t)
    groups = [g for g in groups if g]
    if not groups:
        raise RepError("empty plan")
    steps = []
    answer = None
    arities: list[int] = []
    rtypes: list[str] = []
    ret_type = ""
    for k, g in enumerate(groups):
        head = _name(g[0])
        if head == "ret":
            if k != len(groups) - 1 or len(g) != 3:
                raise RepError("ret must come last and take a type and a register")
            ret_type = _type_name(g[1])
            answer = _parse_typed_arg(g[2])
            if answer[0] != "reg":
                raise RepError("ret takes a register")
            continue
        if head != "apply":
            raise RepError(f"bad instruction head {g[0]!r}")
        if len(g) < 6:
            raise RepError("apply is too short")
        m = re.fullmatch(r"op(\d+)", _name(g[1]))
        if not m:
            raise RepError(f"bad opcode {g[1]!r}")
        symbol = symbol_of_slot(ops, int(m.group(1)))
        ma = re.fullmatch(r"a(\d+)", _name(g[2]))
        if not ma:
            raise RepError(f"bad arity token {g[2]!r}")
        arity = int(ma.group(1))
        rtypes.append(_type_name(g[3]))
        arities.append(arity)
        if _name(g[-2]) != "to":
            raise RepError("apply must end with a destination")
        md = re.fullmatch(r"r(\d+)", _name(g[-1]))
        if not md:
            raise RepError(f"bad destination {g[-1]!r}")
        if int(md.group(1)) != len(steps):
            raise RepError("destination registers must be written in order")
        args = [_parse_typed_arg(t) for t in g[4:-2]]
        steps.append((symbol, args))
    if answer is None:
        raise RepError("plan has no ret")
    return TypedPlan(_assemble(steps, answer), arities, rtypes, ret_type)


def _type_name(tok: str) -> str:
    n = _name(tok)
    if n not in ("tint", "tbool", "tstr"):
        raise RepError(f"bad type token {tok!r}")
    return n[1:]


def _strip_goal(toks: list[str]) -> list[str]:
    out = []
    i = 0
    while i < len(toks):
        if _name(toks[i]) == "goal":
            while i < len(toks) and _name(toks[i]) != "sep":
                i += 1
            i += 1
            continue
        out.append(toks[i])
        i += 1
    return out


# ============================================================== E: goalstack

def _glyph_symbols(ops: dict) -> list[str]:
    return [k for k in ops if len(k) == 1 and k in OP_GLYPHS]


def required_applications(question: str, ops: dict) -> int:
    """How many operator applications the question's surface demands.

    Only single character operator glyphs are counted. A worded operator symbol
    is never counted, because the flag words and unit names on a page are drawn
    from the same syllable pool and can collide, and an over count would make
    the obligation unsatisfiable and stall the decoder. Under counting only
    weakens the constraint, so the rule errs that way on purpose. The floor of
    one covers the prose questions, which name no glyph at all.

    This reads the question, never the gold plan: it fixes how many operators
    are mentioned, not their order, their grouping, their operands, or the way
    the page says the operator associates.
    """
    n = sum(question.count(g) for g in _glyph_symbols(ops))
    return max(1, min(n, MAX_REGS))


def question_literals(question: str) -> set[int]:
    """Every integer written in the question, which a plan has to consume.

    The trailing guard deliberately allows a full stop after the number. The
    obvious spelling, which forbids one, quietly drops the last operand of
    every sequential question and the only operand of every procedure question,
    and it does so without failing anything: a missing obligation is always
    satisfiable, so it costs nothing at the point where it would be noticed.
    """
    return {int(m) for m in re.findall(r"(?<![\w.])\d+(?![\w])", question)}


@dataclass
class Obligations:
    """The obligation state the decoder maintains outside the model.

    Three obligations, each reported separately so it stays visible which one
    is doing the work:

      applications  as many applies as the question names operators
      literals      every integer written in the question is used as an operand
      dangling      exactly one register is live, so no produced value is left
                    unread when the plan returns
    """

    required: int
    literals: set[int]
    use_applications: bool = True
    use_literals: bool = True
    use_dangling: bool = True
    applied: int = 0
    consumed: set[int] = field(default_factory=set)
    live: set[int] = field(default_factory=set)

    @classmethod
    def for_item(cls, item, ops: dict, **kw) -> "Obligations":
        return cls(required_applications(item.text, ops),
                   question_literals(item.text), **kw)

    def open_goals(self) -> list[str]:
        out = []
        if self.use_applications and self.applied < self.required:
            out.append(f"apply x{self.required - self.applied}")
        if self.use_literals and (self.literals - self.consumed):
            out.append("use " + ",".join(str(v) for v in
                                         sorted(self.literals - self.consumed)))
        if self.use_dangling and len(self.live) != 1:
            out.append(f"live={len(self.live)}")
        return out

    def resolved(self) -> bool:
        return not self.open_goals()

    def apply_step(self, dest: int, args) -> None:
        for kind, v in args:
            if kind == "reg":
                self.live.discard(v)
            elif kind == "val" and isinstance(v, int) and not isinstance(v, bool):
                self.consumed.add(v)
        self.applied += 1
        self.live.add(dest)

    def annotation(self) -> str:
        """The state as tokens, written into the sequence by the decoder."""
        pend = max(0, self.required - self.applied) if self.use_applications else 0
        unused = len(self.literals - self.consumed) if self.use_literals else 0
        live = len(self.live)
        return (f"{T_GOAL} {LIT[min(pend, MAX_LIT - 1)]} "
                f"{LIT[min(unused, MAX_LIT - 1)]} "
                f"{LIT[min(live, MAX_LIT - 1)]} {T_SEP}")


def encode_goalstack(plan: Plan, ops: dict, item=None) -> list[tuple[str, bool]]:
    """Spans of (text, supervised). The goal annotations are never supervised.

    The model is not asked to predict the obligation state, because the state
    is not its to decide: the decoder computes it and writes it in. What the
    model reads is a running account of what is still owed.
    """
    if item is None:
        raise RepError("the goal stack form needs the question it plans for")
    ob = Obligations.for_item(item, ops)
    ins = _typed_instructions(plan, ops)
    regs = _reg_index(plan)
    spans: list[tuple[str, bool]] = []
    for i, s in enumerate(plan.steps):
        spans.append((ob.annotation(), False))
        spans.append((ins[i] + " " + T_END, True))
        args = []
        for a in s.args:
            if _arg_is_temp(a):
                args.append(("reg", regs[a]))
            elif isinstance(a, bool):
                args.append(("val", a))
            elif isinstance(a, int):
                args.append(("val", a))
            else:
                args.append(("lit", a))
        ob.apply_step(i, args)
    spans.append((ob.annotation(), False))
    spans.append((ins[-1] + " " + T_END, True))
    return spans


def goalstack_text(plan: Plan, ops: dict, item) -> str:
    return " ".join(t for t, _ in encode_goalstack(plan, ops, item))


def decode_goalstack(text: str, ops: dict) -> Plan:
    return decode_typed(text, ops, drop_goal=True)


# ================================================================== F: slots

def _f_lit(v) -> str:
    if isinstance(v, bool):
        return T_TRUE if v else T_FALSE
    if isinstance(v, int) and 0 <= v < MAX_LIT:
        return LIT[v]
    raise RepError(f"{v!r} does not fit the slot literal range")


def slot_fields(plan: Plan, ops: dict) -> list[str]:
    """The gold contents of every slot field, as reserved token strings.

    Layout: F_SLOTS slots of one opcode field and MAX_ARITY argument fields,
    then one return field. Step k of the plan lands in slot k, and an argument
    that reads step j is written as the reference token for slot j, which is
    the data dependency edge.
    """
    if len(plan.steps) > F_SLOTS:
        raise RepError("plan is longer than the slot graph")
    regs = _reg_index(plan)
    out: list[str] = []
    for k in range(F_SLOTS):
        if k < len(plan.steps):
            s = plan.steps[k]
            if len(s.args) > MAX_ARITY:
                raise RepError("arity is past the slot argument width")
            out.append(OPC[slot_of(ops, s.symbol)])
            for j in range(MAX_ARITY):
                if j < len(s.args):
                    a = s.args[j]
                    out.append(REG[regs[a]] if _arg_is_temp(a) else _f_lit(a))
                else:
                    out.append(T_NONE)
        else:
            out.append(T_NOP)
            out.extend([T_NONE] * MAX_ARITY)
    if not _arg_is_temp(plan.answer):
        raise RepError("the slot form only returns a slot")
    out.append(REG[regs[plan.answer]])
    return out


F_WIDTH = F_SLOTS * (1 + MAX_ARITY) + 1


def field_domain(i: int) -> list[str]:
    """The token domain of field i. A field is a categorical variable."""
    if i == F_WIDTH - 1:
        return REG[:F_SLOTS]
    if i % (1 + MAX_ARITY) == 0:
        return [T_NOP] + OPC
    return [T_NONE, T_TRUE, T_FALSE] + REG[:F_SLOTS] + LIT


def decode_slots(fields: list[str], ops: dict) -> Plan:
    """Read a slot assignment back as a plan, executed in topological order."""
    if len(fields) != F_WIDTH:
        raise RepError(f"expected {F_WIDTH} fields, got {len(fields)}")
    active: dict[int, tuple[str, list]] = {}
    for k in range(F_SLOTS):
        base = k * (1 + MAX_ARITY)
        opname = _name(fields[base])
        if opname == "nop":
            continue
        m = re.fullmatch(r"op(\d+)", opname)
        if not m:
            raise RepError(f"slot {k} holds {fields[base]!r} in its opcode field")
        symbol = symbol_of_slot(ops, int(m.group(1)))
        args = []
        seen_none = False
        for j in range(MAX_ARITY):
            n = _name(fields[base + 1 + j])
            if n == "none":
                seen_none = True
                continue
            if seen_none:
                raise RepError(f"slot {k} has a gap in its arguments")
            mr = re.fullmatch(r"r(\d+)", n)
            if mr:
                args.append(("reg", int(mr.group(1))))
                continue
            mn = re.fullmatch(r"n(\d+)", n)
            if mn:
                args.append(("val", int(mn.group(1))))
                continue
            if n == "vtrue":
                args.append(("val", True))
                continue
            if n == "vfalse":
                args.append(("val", False))
                continue
            raise RepError(f"slot {k} argument {j} holds {fields[base + 1 + j]!r}")
        if not args:
            raise RepError(f"slot {k} is active with no arguments")
        active[k] = (symbol, args)
    mr = re.fullmatch(r"r(\d+)", _name(fields[-1]))
    if not mr:
        raise RepError(f"the return field holds {fields[-1]!r}")
    ret = int(mr.group(1))
    if ret not in active:
        raise RepError("the return field names an inactive slot")
    for k, (_, args) in active.items():
        for kind, v in args:
            if kind == "reg" and v not in active:
                raise RepError(f"slot {k} reads inactive slot {v}")
    order = _toposort(active)
    pos = {k: i for i, k in enumerate(order)}
    steps = []
    for i, k in enumerate(order):
        symbol, args = active[k]
        vals = []
        for kind, v in args:
            vals.append(f"t{pos[v] + 1}" if kind == "reg" else v)
        steps.append(Step(f"t{i + 1}", symbol, tuple(vals)))
    return Plan(tuple(steps), f"t{pos[ret] + 1}")


def _toposort(active: dict[int, tuple[str, list]]) -> list[int]:
    state: dict[int, int] = {}
    order: list[int] = []

    def visit(k: int) -> None:
        s = state.get(k, 0)
        if s == 1:
            raise RepError("the slot graph has a cycle")
        if s == 2:
            return
        state[k] = 1
        for kind, v in active[k][1]:
            if kind == "reg":
                visit(v)
        state[k] = 2
        order.append(k)

    for k in sorted(active):
        visit(k)
    return order


# ======================================================== prompts and streams

def sig_line(rep: str, ops: dict) -> str:
    if rep == "english":
        return signature_line(ops)
    if rep == "symbolic":
        return sig_symbolic(ops)
    if rep in ("opcode", "slots"):
        return sig_opcode(ops)
    if rep in ("typed", "goalstack"):
        return sig_typed(ops)
    raise ValueError(rep)


def rep_plan_prompt(rep: str, ops: dict, question: str) -> str:
    return (f"<|world|> opgraph <|doc|> ops {sig_line(rep, ops)} "
            f"<|q|> plan {question} <|a|>")


ENCODERS = {
    "english": encode_english,
    "symbolic": encode_symbolic,
    "opcode": encode_opcode,
    "typed": encode_typed,
}
DECODERS = {
    "english": decode_english,
    "symbolic": decode_symbolic,
    "opcode": decode_opcode,
    "typed": decode_typed,
    "goalstack": decode_goalstack,
}


def encode_plan(rep: str, plan: Plan, ops: dict, item=None):
    if rep == "goalstack":
        return goalstack_text(plan, ops, item)
    if rep == "slots":
        return slot_fields(plan, ops)
    return ENCODERS[rep](plan, ops)


def decode_plan(rep: str, text, ops: dict) -> Plan:
    if rep == "slots":
        return decode_slots(text, ops)
    return DECODERS[rep](text, ops)


# ----------------------------------------------------------------- examples

@dataclass
class Record:
    """One training example, in whichever form its representation needs."""

    kind: str                      # "text" | "spans" | "slots"
    prompt: str = ""
    target: str = ""
    spans: list = field(default_factory=list)
    fields: list = field(default_factory=list)


def training_records(seed: int, rep: str) -> list[Record]:
    """One world's examples: the induction half is identical for every arm."""
    rng = random.Random(seed * 104729 + 7)
    breadth = rng.choice([1, 2, 3])
    w = make_world(seed, breadth=breadth)
    items = [seq_flat(w, rng, rng.choice([1, 2, 3])),
             seq_paren(w, rng, rng.choice([2, 3])),
             breadth_item(w, rng, breadth),
             units_item(w, rng)]
    out = [Record("text", induce_prompt(p.text), serialize_all(p.ops))
           for p in w.shuffled_pages()]
    for it in items:
        prompt = rep_plan_prompt(rep, w.ops, it.text)
        if rep == "goalstack":
            out.append(Record("spans", prompt,
                              spans=encode_goalstack(it.plan, w.ops, it)))
        elif rep == "slots":
            out.append(Record("slots", prompt,
                              fields=slot_fields(it.plan, w.ops)))
        else:
            out.append(Record("text", prompt,
                              ENCODERS[rep](it.plan, w.ops)))
    return out


def build_ladder_stream(seeds, rep: str, rng_seed: int = 0) -> list[Record]:
    pool: list[Record] = []
    for s in seeds:
        pool.extend(training_records(s, rep))
    random.Random(rng_seed).shuffle(pool)
    return pool


# ------------------------------------------------------------- tokenisation

def encode_record(tok, rec: Record, max_len: int, rounds: int = F_ROUNDS,
                  rng: random.Random | None = None):
    """Token ids and labels for one record, or None when it does not fit."""
    if rec.kind == "text":
        p = tok.encode(rec.prompt)
        t = tok.encode(" " + rec.target) + [tok.token_id("<|eot|>")]
        ids = p + t
        if len(ids) > max_len:
            return None
        return ids, [IGNORE] * len(p) + t
    if rec.kind == "spans":
        ids = tok.encode(rec.prompt)
        labels = [IGNORE] * len(ids)
        for text, supervised in rec.spans:
            piece = tok.encode(" " + text)
            ids.extend(piece)
            labels.extend(piece if supervised else [IGNORE] * len(piece))
        eot = tok.token_id("<|eot|>")
        ids.append(eot)
        labels.append(eot)
        if len(ids) > max_len:
            return None
        return ids, labels
    if rec.kind == "slots":
        return encode_slot_rows(tok, rec.prompt, rec.fields, max_len, rounds, rng)
    raise ValueError(rec.kind)


def slot_row_ids(tok, fields: list[str], mask_at: set[int]) -> tuple[list, list]:
    """One refinement row: structure tokens, contents, and the label mask."""
    mid = tok.token_id(T_MASK)
    ids = [tok.token_id(T_ROW)]
    labels = [IGNORE]
    for k in range(F_SLOTS):
        ids.append(tok.token_id(SLOTID[k]))
        labels.append(IGNORE)
        for j in range(1 + MAX_ARITY):
            i = k * (1 + MAX_ARITY) + j
            gold = tok.token_id(fields[i])
            if i in mask_at:
                ids.append(mid)
                labels.append(gold)
            else:
                ids.append(gold)
                labels.append(IGNORE)
    ids.append(tok.token_id(T_RETF))
    labels.append(IGNORE)
    i = F_WIDTH - 1
    gold = tok.token_id(fields[i])
    if i in mask_at:
        ids.append(mid)
        labels.append(gold)
    else:
        ids.append(gold)
        labels.append(IGNORE)
    return ids, labels


def encode_slot_rows(tok, prompt: str, fields: list[str], max_len: int,
                     rounds: int, rng: random.Random | None):
    rng = rng or random.Random(0)
    ids = tok.encode(prompt)
    labels = [IGNORE] * len(ids)
    everything = set(range(F_WIDTH))
    for r in range(rounds):
        committed = int(F_WIDTH * r / rounds)
        keep = set(rng.sample(sorted(everything), committed)) if committed else set()
        row_ids, row_labels = slot_row_ids(tok, fields, everything - keep)
        ids.extend(row_ids)
        labels.extend(row_labels)
    if len(ids) > max_len:
        return None
    return ids, labels


def row_field_positions(prompt_len: int, row: int) -> list[int]:
    """Sequence positions of the F_WIDTH content fields of one row."""
    row_len = 1 + F_SLOTS * (2 + MAX_ARITY) + 2
    base = prompt_len + row * row_len
    out = []
    p = base + 1
    for _ in range(F_SLOTS):
        p += 1
        for _ in range(1 + MAX_ARITY):
            out.append(p)
            p += 1
    p += 1
    out.append(p)
    return out


ROW_LEN = 1 + F_SLOTS * (2 + MAX_ARITY) + 2


# ------------------------------------------------------------ fresh embeddings

def reinit_tokens(model, tok, names: list[str], std: float = 0.02,
                  seed: int = 0) -> int:
    """Re-draw the input and output rows of the given reserved tokens.

    The reserved slots carry whatever the pretraining left in them. A condition
    that puts new symbols in the model's mouth should not inherit that, so the
    rows are drawn again from the same normal the model was initialised from.
    Every other parameter, and the parameter count, is untouched.
    """
    import torch

    if not names:
        return 0
    ids = [tok.token_id(n) for n in names]
    g = torch.Generator().manual_seed(seed)
    with torch.no_grad():
        for mat in (model.tok_emb.weight, model.lm_head.weight):
            w = torch.empty(len(ids), mat.shape[1])
            w.normal_(0.0, std, generator=g)
            mat[ids] = w.to(device=mat.device, dtype=mat.dtype)
    return len(ids)


# -------------------------------------------------------------- diagnostics

def canonical(plan: Plan) -> tuple:
    """A comparable form of a plan, blind to how the temporaries are named."""
    idx = {s.target: i for i, s in enumerate(plan.steps)}
    out = []
    for s in plan.steps:
        args = tuple(("r", idx[a]) if _arg_is_temp(a) else ("v", a)
                     for a in s.args)
        out.append((s.symbol, args))
    ans = ("r", idx[plan.answer]) if _arg_is_temp(plan.answer) else ("v", plan.answer)
    return tuple(out), ans


def well_typed(plan: Plan, ops: dict) -> bool:
    """Arities and operand types agree with the operator table.

    This is computed the same way for every representation, from the decoded
    plan, so the number means the same thing across the ladder. What differs is
    that D, E and F can be checked against their own declarations before they
    are run, which the earlier rungs cannot.
    """
    regtype: dict[str, str] = {}
    try:
        for s in plan.steps:
            pt, rt = signature_of(ops, s.symbol)
            if len(s.args) != len(pt):
                return False
            for a, want in zip(s.args, pt):
                got = regtype.get(a) if _arg_is_temp(a) else _arg_type(a, [])
                if got is None or got != want:
                    return False
            regtype[s.target] = rt
        if _arg_is_temp(plan.answer) and plan.answer not in regtype:
            return False
    except RepError:
        return False
    return True


def declarations_agree(tp: TypedPlan, ops: dict) -> bool:
    """The typed form's own declarations, checked before anything is run."""
    try:
        for s, ar, rt in zip(tp.plan.steps, tp.declared_arity, tp.declared_type):
            pt, want = signature_of(ops, s.symbol)
            if ar != len(s.args) or ar != len(pt) or rt != want:
                return False
        if tp.plan.steps:
            last = {s.target: i for i, s in enumerate(tp.plan.steps)}
            i = last.get(tp.plan.answer)
            if i is None or tp.return_type != tp.declared_type[i]:
                return False
    except RepError:
        return False
    return True
