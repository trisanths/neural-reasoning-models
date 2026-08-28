"""Four plan heads over the same reader, the same operators and the same executor.

The established result is that a correct plan removes the depth wall entirely
(oracle_plan is flat at 1.000 through depth eight) while a model written plan
collapses after depth three. That localises the wall in plan construction. This
module varies plan construction and nothing else.

  P1  autoregressive tokens    the existing plan_execute head, written in words
  P2  autoregressive opcodes   the same causal decode, one dedicated token per
                               operator instead of its written symbol
  P2s autoregressive slots     the same causal decode over the slot codec P3
                               uses, so P2 to P3 is not confounded by the codec
  P3  masked iterative slots   a fixed length slot array, all MASK at the start,
                               refined over several bidirectional passes in
                               which any slot may be rewritten
  P4  graph denoising          the same, with per node fields (active, opcode,
                               output register, arguments, two dependency edges)
                               and execution in topological order of the edges

Everything is discrete. A slot holds a symbol drawn from a small fixed set, so
accuracy is exact, an oracle can overwrite any slot, a counterfactual is a
single substitution, and there is no continuous space large enough to hide the
answer in.

What is shared, and must stay shared: the base checkpoint, the induction task
and its text objective, the worlds and their seeds, the questions, the operator
objects, the plan executor, the optimizer steps, and the batch size in
sequences. What differs is listed in PLANHEADS.md under "what is not matched",
and the two entries there are real: P2, P2s, P3 and P4 carry an opcode binding
column in the prompt that P1 does not need, and the three slot heads carry a
freshly initialised head module where P1 reuses the pretrained lm_head.

Every planner counts the forward passes it spends building one plan, because
without that number a win by P3 or P4 cannot be told apart from a win by
spending more compute, and the second is a much weaker claim.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field as dc_field

import torch
import torch.nn as nn
import torch.nn.functional as F

from src.opgraph.opdef import Operator
from src.opgraph.plan import (BUILTIN_STEPS, Plan, PlanError, Step, parse_plan,
                              run_plan, serialize_plan, signature_line)
from src.train.model import apply_rope

# --------------------------------------------------------------- slot schema

N_NODES = 12          # plan nodes in the fixed length array; eval depth tops at 8
A_MAX = 7             # widest arity in the worlds: score takes v plus six flags
K_MAX = 8             # induced operator symbols per world; the worlds define six
INT_MAX = 256         # literal integers a slot can name; gold plans never pass 80

BUILTIN_ORDER = ("add", "sub", "mul")

# Field kinds. The kind fixes which symbols a slot may hold and which output
# head reads it, so a slot can never be given a symbol from another field.
F_ACTIVE, F_OPCODE, F_REG, F_ARG, F_DEP, F_ANS = range(6)
N_FIELDS = 6

FIELD_SIZE = {
    F_ACTIVE: 3,                          # NO, YES, MASK
    F_OPCODE: 2 + K_MAX + len(BUILTIN_ORDER),   # EMPTY, MASK, OP_1..OP_K, add sub mul
    F_REG: 2 + N_NODES,                   # EMPTY, MASK, R_1..R_N
    F_ARG: 4 + N_NODES + INT_MAX,         # EMPTY, MASK, FALSE, TRUE, T_1..T_N, ints
    F_DEP: 2 + N_NODES,                   # NONE, MASK, NODE_1..NODE_N
    F_ANS: 4 + N_NODES + INT_MAX,         # same alphabet as an argument
}

# One global symbol id space, so the head is one embedding table and one linear
# projection. A field's logits are restricted to its own window before the
# softmax, which makes an out of field symbol structurally unreachable.
FIELD_BASE = {}
_acc = 0
for _f in range(N_FIELDS):
    FIELD_BASE[_f] = _acc
    _acc += FIELD_SIZE[_f]
N_SYMBOLS = _acc

# Local values inside a field.
A_NO, A_YES, A_MASK = 0, 1, 2
O_EMPTY, O_MASK = 0, 1
O_OP0 = 2
O_BUILTIN0 = 2 + K_MAX
R_EMPTY, R_MASK, R_REG0 = 0, 1, 2
G_EMPTY, G_MASK, G_FALSE, G_TRUE = 0, 1, 2, 3
G_TEMP0 = 4
G_INT0 = 4 + N_NODES
D_NONE, D_MASK, D_NODE0 = 0, 1, 2

MASK_LOCAL = {F_ACTIVE: A_MASK, F_OPCODE: O_MASK, F_REG: R_MASK,
              F_ARG: G_MASK, F_DEP: D_MASK, F_ANS: G_MASK}
EMPTY_LOCAL = {F_ACTIVE: A_NO, F_OPCODE: O_EMPTY, F_REG: R_EMPTY,
               F_ARG: G_EMPTY, F_DEP: D_NONE, F_ANS: G_EMPTY}


def gid(fieldkind: int, local: int) -> int:
    """Global symbol id for a value inside one field."""
    if not 0 <= local < FIELD_SIZE[fieldkind]:
        raise SlotError(f"value {local} out of range for field {fieldkind}")
    return FIELD_BASE[fieldkind] + local


class SlotError(Exception):
    """A slot array that cannot be turned into a plan."""


@dataclass(frozen=True)
class Schema:
    """The slot layout of one head: what each position is, and where it sits.

    flat (P2s, P3)   per node: opcode, then A_MAX argument slots
    graph (P4)       per node: active, opcode, output register, A_MAX argument
                     slots, then two dependency edges

    Both end on a single answer slot. The layout is fixed length in both cases,
    which is what lets every slot be predicted in one pass.
    """

    graph: bool

    @property
    def per_node(self) -> tuple:
        if self.graph:
            return (F_ACTIVE, F_OPCODE, F_REG) + (F_ARG,) * A_MAX + (F_DEP, F_DEP)
        return (F_OPCODE,) + (F_ARG,) * A_MAX

    @property
    def node_width(self) -> int:
        return len(self.per_node)

    @property
    def n_slots(self) -> int:
        return N_NODES * self.node_width + 1

    @property
    def fields(self) -> list[int]:
        return list(self.per_node) * N_NODES + [F_ANS]

    def at(self, node: int, offset: int) -> int:
        return node * self.node_width + offset

    def opcode_slot(self, node: int) -> int:
        return self.at(node, 1 if self.graph else 0)

    def active_slot(self, node: int) -> int:
        if not self.graph:
            raise SlotError("flat schema has no active field")
        return self.at(node, 0)

    def reg_slot(self, node: int) -> int:
        if not self.graph:
            raise SlotError("flat schema has no register field")
        return self.at(node, 2)

    def arg_slot(self, node: int, k: int) -> int:
        return self.at(node, (3 if self.graph else 1) + k)

    def dep_slot(self, node: int, k: int) -> int:
        if not self.graph:
            raise SlotError("flat schema has no dependency field")
        return self.at(node, 3 + A_MAX + k)

    @property
    def answer_slot(self) -> int:
        return N_NODES * self.node_width


FLAT = Schema(graph=False)
GRAPH = Schema(graph=True)
MAX_SLOTS = max(FLAT.n_slots, GRAPH.n_slots)


def schema_for(head: str) -> Schema:
    return GRAPH if head == "p4" else FLAT


# ------------------------------------------------------------ opcode binding

# Dedicated opcode symbols for P2 come out of the tokenizer's reserved block,
# so they are single ids in the vocabulary the base model already has, and no
# embedding row has to be added. The k-th operator of a world, in the sorted
# order the signature line already prints, is written with the k-th of these.
OPCODE_TOKEN_BASE = 200
OPCODE_TOKENS = [f"<|pg{OPCODE_TOKEN_BASE + i}|>" for i in range(K_MAX + len(BUILTIN_ORDER))]


def op_symbols(ops: dict) -> list[str]:
    """The operator symbols of a table, in the order the signature line prints."""
    return sorted(ops)


def opcode_token(index: int) -> str:
    return OPCODE_TOKENS[index]


def opcode_signature(ops: dict) -> str:
    """The signature line with the opcode each symbol is written with.

    P1 reads plain `signature_line`, which is what it was trained on. The three
    other heads write a plan in opcodes rather than in the page's own symbol,
    so they need the binding stated. The column adds no semantics: the symbol,
    the arity and the associativity are the same facts P1 already gets.
    """
    out = []
    for k, sym in enumerate(op_symbols(ops)):
        op = ops[sym]
        tag = f"{sym}={opcode_token(k)}/{op.arity}"
        if op.assoc:
            tag += f"/{op.assoc}"
        out.append(tag)
    for b, name in enumerate(BUILTIN_ORDER):
        out.append(f"{name}={opcode_token(K_MAX + b)}/2")
    return " ".join(out)


def plan_prompt_text(ops: dict, question: str, head: str) -> str:
    """The planning prompt. P1 keeps exactly the prompt it was trained on."""
    if head == "p1":
        return (f"<|world|> opgraph <|doc|> ops {signature_line(ops)} "
                f"<|q|> plan {question} <|a|>")
    return (f"<|world|> opgraph <|doc|> ops {opcode_signature(ops)} "
            f"<|q|> plan {question} <|a|>")


def to_opcode_text(plan_text: str, ops: dict) -> str:
    """A plan written in opcodes rather than in the page's own symbols."""
    syms = op_symbols(ops)
    index = {s: opcode_token(k) for k, s in enumerate(syms)}
    for b, name in enumerate(BUILTIN_ORDER):
        index[name] = opcode_token(K_MAX + b)
    out = []
    for chunk in plan_text.split(";"):
        parts = chunk.split()
        if len(parts) >= 3 and parts[1] == "=":
            parts[2] = index.get(parts[2], parts[2])
        out.append(" ".join(parts))
    return " ; ".join(out)


def from_opcode_text(text: str, ops: dict) -> str:
    """Undo `to_opcode_text` so the plan meets the same parser P1 meets."""
    syms = op_symbols(ops)
    back = {opcode_token(k): s for k, s in enumerate(syms)}
    for b, name in enumerate(BUILTIN_ORDER):
        back[opcode_token(K_MAX + b)] = name
    for tokname, sym in back.items():
        text = text.replace(tokname, f" {sym} ")
    # An opcode past the table's length stays as its raw token and the strict
    # parser rejects it, which is the intended outcome rather than a repair.
    return " ".join(text.split())


# ------------------------------------------------------------------- codec

def _arity_of(symbol: str, ops: dict) -> int:
    if symbol in BUILTIN_STEPS:
        return BUILTIN_STEPS[symbol][0]
    op = ops.get(symbol)
    if op is None:
        raise SlotError(f"unknown operator {symbol!r}")
    return op.arity


def encode_plan(plan: Plan, ops: dict, schema: Schema) -> list[int]:
    """A gold plan as a slot array of global symbol ids.

    Raises rather than approximating. A plan that will not fit the array is a
    plan this head cannot represent, and silently truncating one would put a
    ceiling on an arm without saying so.
    """
    syms = op_symbols(ops)
    index = {s: k for k, s in enumerate(syms)}
    if len(syms) > K_MAX:
        raise SlotError(f"world has {len(syms)} operators, over K_MAX {K_MAX}")
    if len(plan.steps) > N_NODES:
        raise SlotError(f"plan of {len(plan.steps)} steps is over N_NODES {N_NODES}")
    slots = [gid(f, EMPTY_LOCAL[f]) for f in schema.fields]
    for i, step in enumerate(plan.steps):
        if step.target != f"t{i + 1}":
            raise SlotError(f"step {i} writes {step.target}, expected t{i + 1}")
        if step.symbol in index:
            opv = O_OP0 + index[step.symbol]
        elif step.symbol in BUILTIN_STEPS:
            opv = O_BUILTIN0 + BUILTIN_ORDER.index(step.symbol)
        else:
            raise SlotError(f"plan uses {step.symbol!r}, absent from the table")
        arity = _arity_of(step.symbol, ops)
        if len(step.args) != arity:
            raise SlotError(f"{step.symbol} given {len(step.args)} of {arity} args")
        if arity > A_MAX:
            raise SlotError(f"arity {arity} is over A_MAX {A_MAX}")
        slots[schema.opcode_slot(i)] = gid(F_OPCODE, opv)
        deps: list[int] = []
        for k, a in enumerate(step.args):
            slots[schema.arg_slot(i, k)] = gid(F_ARG, _arg_local(a))
            if isinstance(a, str) and a.startswith("t"):
                d = int(a[1:]) - 1
                if d not in deps:
                    deps.append(d)
        if schema.graph:
            slots[schema.active_slot(i)] = gid(F_ACTIVE, A_YES)
            slots[schema.reg_slot(i)] = gid(F_REG, R_REG0 + i)
            if len(deps) > 2:
                raise SlotError(f"step {i} reads {len(deps)} temporaries, over two")
            for k in range(2):
                v = D_NODE0 + deps[k] if k < len(deps) else D_NONE
                slots[schema.dep_slot(i, k)] = gid(F_DEP, v)
    slots[schema.answer_slot] = gid(F_ANS, _arg_local(_answer_value(plan.answer)))
    return slots


def _answer_value(answer: str):
    if answer.startswith("t") and answer[1:].isdigit():
        return answer
    if answer.lstrip("-").isdigit():
        return int(answer)
    if answer in ("true", "false"):
        return answer == "true"
    raise SlotError(f"answer {answer!r} is not a temporary or an integer")


def _arg_local(a) -> int:
    if isinstance(a, bool):
        return G_TRUE if a else G_FALSE
    if isinstance(a, int):
        if not 0 <= a < INT_MAX:
            raise SlotError(f"literal {a} outside 0..{INT_MAX - 1}")
        return G_INT0 + a
    if isinstance(a, str) and a.startswith("t") and a[1:].isdigit():
        k = int(a[1:])
        if not 1 <= k <= N_NODES:
            raise SlotError(f"temporary {a} outside t1..t{N_NODES}")
        return G_TEMP0 + k - 1
    raise SlotError(f"argument {a!r} has no slot value")


def _arg_text(local: int) -> str:
    if local == G_FALSE:
        return "false"
    if local == G_TRUE:
        return "true"
    if G_TEMP0 <= local < G_TEMP0 + N_NODES:
        return f"t{local - G_TEMP0 + 1}"
    if G_INT0 <= local < G_INT0 + INT_MAX:
        return str(local - G_INT0)
    raise SlotError(f"argument slot holds {local}, which is not a value")


def local_of(slots: list[int], index: int, fields: list[int]) -> int:
    return slots[index] - FIELD_BASE[fields[index]]


def decode_plan_text(slots: list[int], ops: dict, schema: Schema) -> str:
    """A slot array as plan text, for the same strict parser every head meets.

    Nothing here repairs anything. A masked slot, an opcode past the end of the
    table, a missing argument or a cyclic dependency raises, and the caller
    records the failure rather than a wrong answer.
    """
    fields = schema.fields
    syms = op_symbols(ops)

    def sym_of(node: int) -> str | None:
        v = local_of(slots, schema.opcode_slot(node), fields)
        if v == O_EMPTY:
            return None
        if v == O_MASK:
            raise SlotError("opcode slot left masked")
        if O_OP0 <= v < O_OP0 + K_MAX:
            k = v - O_OP0
            if k >= len(syms):
                raise SlotError(f"opcode {k + 1} past the {len(syms)} operator table")
            return syms[k]
        return BUILTIN_ORDER[v - O_BUILTIN0]

    def args_of(node: int, symbol: str) -> list[str]:
        arity = _arity_of(symbol, ops)
        out = []
        for k in range(A_MAX):
            v = local_of(slots, schema.arg_slot(node, k), fields)
            if k < arity:
                if v in (G_EMPTY, G_MASK):
                    raise SlotError(f"node {node} argument {k} is empty or masked")
                out.append(_arg_text(v))
            elif v != G_EMPTY:
                raise SlotError(f"node {node} has an argument past arity {arity}")
        return out

    if schema.graph:
        active = [i for i in range(N_NODES)
                  if local_of(slots, schema.active_slot(i), fields) == A_YES]
        for i in range(N_NODES):
            if local_of(slots, schema.active_slot(i), fields) == A_MASK:
                raise SlotError("active flag left masked")
        live = set(active)
        deps: dict[int, list[int]] = {}
        regs: dict[int, int] = {}
        for i in active:
            rv = local_of(slots, schema.reg_slot(i), fields)
            if rv in (R_EMPTY, R_MASK):
                raise SlotError(f"active node {i} has no output register")
            regs[i] = rv - R_REG0 + 1
            d = []
            for k in range(2):
                dv = local_of(slots, schema.dep_slot(i, k), fields)
                if dv == D_MASK:
                    raise SlotError("dependency slot left masked")
                if dv == D_NONE:
                    continue
                j = dv - D_NODE0
                if j not in live:
                    raise SlotError(f"node {i} depends on inactive node {j}")
                if j == i:
                    raise SlotError(f"node {i} depends on itself")
                d.append(j)
            deps[i] = d
        if len(set(regs.values())) != len(regs):
            raise SlotError("two active nodes write the same register")
        order = _toposort(active, deps)
        chunks = []
        for i in order:
            symbol = sym_of(i)
            if symbol is None:
                raise SlotError(f"active node {i} has an empty opcode")
            chunks.append(f"t{regs[i]} = {symbol} " + " ".join(args_of(i, symbol)))
    else:
        chunks = []
        seen_empty = False
        for i in range(N_NODES):
            symbol = sym_of(i)
            if symbol is None:
                seen_empty = True
                continue
            if seen_empty:
                raise SlotError("an active node follows an empty one")
            chunks.append(f"t{i + 1} = {symbol} " + " ".join(args_of(i, symbol)))
    av = local_of(slots, schema.answer_slot, fields)
    if av in (G_EMPTY, G_MASK):
        raise SlotError("answer slot is empty or masked")
    chunks.append("ans " + _arg_text(av))
    return " ; ".join(chunks)


def _toposort(nodes: list[int], deps: dict[int, list[int]]) -> list[int]:
    """The lexicographically smallest topological order, one node at a time.

    Taking the whole ready frontier at once would reorder a graph whose array
    order is already topological, which would make an exactly correct P4 program
    serialise differently from the identical P1 program and cost it the exact
    gold plan diagnostic for nothing. Taking the smallest ready node repeatedly
    leaves an already sorted array alone and still sorts one that is not.
    """
    done: list[int] = []
    seen: set = set()
    remaining = set(nodes)
    while remaining:
        nxt = None
        for i in sorted(remaining):
            if all(d in seen for d in deps[i]):
                nxt = i
                break
        if nxt is None:
            raise SlotError("dependency edges form a cycle")
        done.append(nxt)
        seen.add(nxt)
        remaining.discard(nxt)
    return done


def all_masked(schema: Schema) -> list[int]:
    return [gid(f, MASK_LOCAL[f]) for f in schema.fields]


# -------------------------------------------------------------- corruption

# The mixture the repair objective is trained on. Uniform masking alone teaches
# "what symbol goes in this hole"; the other five teach "what computation makes
# this partial program globally correct", which is the question a refinement
# pass actually has to answer. Weights are a design choice and are reported
# with every result so they can be varied.
MIXTURE_FLAT = {
    "all_mask": 0.25,      # the inference time starting point, in distribution
    "random_mask": 0.25,   # a uniform hole rate drawn per example
    "transpose": 0.10,     # two active nodes swapped
    "wrong_op": 0.15,      # a semantically wrong operator substituted
    "truncate": 0.15,      # the tail of the program dropped to MASK
    "sparse": 0.10,        # a mostly empty program, one node kept at most
}
MIXTURE_GRAPH = {
    "all_mask": 0.22,
    "random_mask": 0.22,
    "transpose": 0.09,
    "wrong_op": 0.13,
    "truncate": 0.13,
    "sparse": 0.08,
    "edge_noise": 0.13,    # a dependency edge dropped, added, or misdirected
}
# On every corruption other than all_mask, an extra uniform hole rate in this
# range is drawn on top, so the model meets mixtures rather than pure types.
EXTRA_MASK_RANGE = (0.0, 0.30)


def mixture_for(head: str) -> dict:
    return dict(MIXTURE_GRAPH if head == "p4" else MIXTURE_FLAT)


def corrupt(slots: list[int], schema: Schema, n_ops: int, rng: random.Random,
            mixture: dict) -> tuple[list[int], str]:
    """One corrupted copy of a gold slot array, and the type that made it."""
    fields = schema.fields
    kinds = list(mixture)
    weights = [mixture[k] for k in kinds]
    kind = rng.choices(kinds, weights=weights, k=1)[0]
    out = list(slots)
    nodes = _active_nodes(slots, schema)

    def mask_node(i: int) -> None:
        for off in range(schema.node_width):
            j = schema.at(i, off)
            out[j] = gid(fields[j], MASK_LOCAL[fields[j]])

    if kind == "all_mask":
        return all_masked(schema), kind
    if kind == "transpose" and len(nodes) >= 2:
        a, b = rng.sample(nodes, 2)
        for off in range(schema.node_width):
            ja, jb = schema.at(a, off), schema.at(b, off)
            out[ja], out[jb] = out[jb], out[ja]
    elif kind == "wrong_op" and nodes:
        choices = [O_OP0 + k for k in range(min(n_ops, K_MAX))]
        choices += [O_BUILTIN0 + b for b in range(len(BUILTIN_ORDER))]
        for i in rng.sample(nodes, min(len(nodes), rng.choice([1, 1, 2]))):
            j = schema.opcode_slot(i)
            alt = [c for c in choices if gid(F_OPCODE, c) != slots[j]]
            if alt:
                out[j] = gid(F_OPCODE, rng.choice(alt))
    elif kind == "truncate" and nodes:
        keep = rng.randrange(0, len(nodes))
        for i in nodes[keep:]:
            mask_node(i)
        out[schema.answer_slot] = gid(F_ANS, G_MASK)
    elif kind == "sparse":
        keep = rng.choice([0, 1])
        for i in nodes[keep:]:
            mask_node(i)
        out[schema.answer_slot] = gid(F_ANS, G_MASK)
    elif kind == "edge_noise" and schema.graph and nodes:
        for i in rng.sample(nodes, min(len(nodes), rng.choice([1, 2]))):
            k = rng.choice([0, 1])
            j = schema.dep_slot(i, k)
            pick = rng.random()
            if pick < 0.34:
                out[j] = gid(F_DEP, D_NONE)
            elif pick < 0.67:
                out[j] = gid(F_DEP, D_NODE0 + rng.randrange(N_NODES))
            else:
                out[j] = gid(F_DEP, D_MASK)

    rate = (rng.uniform(0.10, 1.0) if kind == "random_mask"
            else rng.uniform(*EXTRA_MASK_RANGE))
    for j in range(len(out)):
        if rng.random() < rate:
            out[j] = gid(fields[j], MASK_LOCAL[fields[j]])
    return out, kind


def _active_nodes(slots: list[int], schema: Schema) -> list[int]:
    fields = schema.fields
    out = []
    for i in range(N_NODES):
        v = local_of(slots, schema.opcode_slot(i), fields)
        if v not in (O_EMPTY, O_MASK):
            out.append(i)
    return out


# ------------------------------------------------------------------- head

class SlotPlanHead(nn.Module):
    """The only new parameters in P2s, P3 and P4.

    A symbol embedding over the global slot alphabet, a field kind embedding, a
    slot position embedding, and one linear projection back to the alphabet.
    About 1.4M parameters against the backbone's 350M. P1 and P2 use the
    pretrained lm_head instead and add nothing.
    """

    def __init__(self, d_model: int):
        super().__init__()
        self.sym_emb = nn.Embedding(N_SYMBOLS, d_model)
        self.field_emb = nn.Embedding(N_FIELDS, d_model)
        self.pos_emb = nn.Embedding(MAX_SLOTS + 1, d_model)
        self.out = nn.Linear(d_model, N_SYMBOLS, bias=False)
        for m in (self.sym_emb, self.field_emb, self.pos_emb):
            nn.init.normal_(m.weight, mean=0.0, std=0.02)
        nn.init.normal_(self.out.weight, mean=0.0, std=0.02)
        nn.init.zeros_(self.field_emb.weight)
        nn.init.zeros_(self.pos_emb.weight)

    def embed(self, sym: torch.Tensor, fieldkind: torch.Tensor,
              pos: torch.Tensor) -> torch.Tensor:
        return self.sym_emb(sym) + self.field_emb(fieldkind) + self.pos_emb(pos)


def field_logit_mask(fields: list[int], device) -> torch.Tensor:
    """(S, N_SYMBOLS) boolean: which symbols each slot is allowed to hold.

    Applied before every softmax, at training and at inference, so a slot can
    never take a symbol belonging to another field and the accuracy of a field
    is never diluted by mass parked outside it.
    """
    m = torch.zeros(len(fields), N_SYMBOLS, dtype=torch.bool, device=device)
    for i, f in enumerate(fields):
        m[i, FIELD_BASE[f]:FIELD_BASE[f] + FIELD_SIZE[f]] = True
    return m


# ----------------------------------------------------- masked trunk, counted

class ForwardCounter:
    """Counts one stack invocation per call, by watching the token embedding.

    Every path through the backbone, including the key/value cached decoder in
    src/rl/sampler.py which inlines the blocks rather than calling them, passes
    through model.tok_emb exactly once per invocation. Hooking there is what
    lets the reported forward count be checked against the model itself rather
    than against the bookkeeping that produced it.
    """

    def __init__(self, model):
        self.model = model
        self.count = 0
        self._handle = None

    def __enter__(self):
        def hook(_m, _i, _o):
            self.count += 1
        self._handle = self.model.tok_emb.register_forward_hook(hook)
        return self

    def __exit__(self, *exc):
        self._handle.remove()
        self._handle = None
        return False


def build_mask(width: int, prompt_width: int, key_ok: torch.Tensor,
               causal_slots: bool) -> torch.Tensor:
    """Attention mask for [pad][prompt][slots].

    The prompt is causal, which is how the backbone was pretrained. The slot
    region sees the whole prompt and, under P3 and P4, every slot including
    itself and the ones after it, which is what "conditioned on every other
    slot" requires and what a causal decoder cannot do. Under P2s the slot
    region stays causal, which is the point of that arm.

    The diagonal is forced open so a padding row still attends to something.
    Without it a fully masked row softmaxes to NaN and the NaN reaches every
    later position through the key/value it writes.
    """
    device = key_ok.device
    rows = torch.arange(width, device=device).view(-1, 1)
    cols = torch.arange(width, device=device).view(1, -1)
    causal = cols <= rows
    if causal_slots:
        struct = causal
    else:
        struct = causal | (rows >= prompt_width)
    m = key_ok[:, None, None, :] & struct[None, None, :, :]
    eye = torch.eye(width, dtype=torch.bool, device=device)[None, None]
    return m | eye


def run_stack(model, x: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    """The backbone's own blocks, with an explicit mask instead of is_causal.

    model.py is not touched. The arithmetic here is Block.forward and
    Attention.forward inlined with attn_mask passed through, which is the same
    computation whenever the mask is the causal one.
    """
    cfg = model.cfg
    if cfg.recurrent is not None or model.pointer is not None:
        raise SlotError("the slot heads assume a plain decoder backbone")
    bsz, seq, _ = x.shape
    cos, sin = model.rope_cos[:seq], model.rope_sin[:seq]
    for block in model.blocks:
        h = block.attn_norm(x)
        attn = block.attn
        q = attn.wq(h).view(bsz, seq, cfg.n_heads, cfg.head_dim).transpose(1, 2)
        k = attn.wk(h).view(bsz, seq, cfg.n_heads, cfg.head_dim).transpose(1, 2)
        v = attn.wv(h).view(bsz, seq, cfg.n_heads, cfg.head_dim).transpose(1, 2)
        q, k = apply_rope(q, cos, sin), apply_rope(k, cos, sin)
        o = F.scaled_dot_product_attention(q, k, v, attn_mask=mask)
        o = o.transpose(1, 2).reshape(bsz, seq, cfg.d_model)
        x = x + attn.wo(o)
        x = x + block.mlp(block.mlp_norm(x))
    return model.final_norm(x)


def slot_forward(model, head: SlotPlanHead, prompt_ids: torch.Tensor,
                 prompt_ok: torch.Tensor, slot_sym: torch.Tensor,
                 schema: Schema, causal_slots: bool) -> torch.Tensor:
    """Hidden states for the slot region, one stack invocation.

    prompt_ids is left padded and prompt_ok marks the real tokens. The slot
    region carries no token ids at all; its inputs are the head's own symbol,
    field and position embeddings, so nothing about the plan representation
    leaks into the token vocabulary.

    Returns (B, n_slots + 1, d_model): column 0 is the last prompt position,
    columns 1.. are the slot positions. A causal head reads slot j from column
    j, which is the position before it; a bidirectional head reads slot j from
    column j + 1, which is the slot itself.
    """
    device = prompt_ids.device
    bsz, pw = prompt_ids.shape
    s = schema.n_slots
    fields = torch.tensor(schema.fields, device=device)
    pos = torch.arange(s, device=device)
    tok = model.tok_emb(prompt_ids)
    slot = head.embed(slot_sym, fields[None].expand(bsz, s), pos[None].expand(bsz, s))
    x = torch.cat([tok, slot.to(tok.dtype)], dim=1)
    ok = torch.cat([prompt_ok, torch.ones(bsz, s, dtype=torch.bool, device=device)], 1)
    mask = build_mask(pw + s, pw, ok, causal_slots)
    hidden = run_stack(model, x, mask)
    return hidden[:, pw - 1:]


def readout(hidden: torch.Tensor, causal_slots: bool) -> torch.Tensor:
    """The (B, n_slots, d_model) states aligned to the slot they predict."""
    return hidden[:, :-1] if causal_slots else hidden[:, 1:]


def slot_logits(head: SlotPlanHead, hidden: torch.Tensor,
                fmask: torch.Tensor) -> torch.Tensor:
    logits = head.out(hidden).float()
    return logits.masked_fill(~fmask[None], float("-inf"))


# --------------------------------------------------------------- diagnostics

def well_typed(plan: Plan, ops: dict) -> bool:
    """Every symbol is in the table and every arity matches."""
    for s in plan.steps:
        if s.symbol in BUILTIN_STEPS:
            n = BUILTIN_STEPS[s.symbol][0]
        elif s.symbol in ops:
            n = ops[s.symbol].arity
        else:
            return False
        if len(s.args) != n:
            return False
    return True


@dataclass
class PlanOut:
    """One constructed plan and what it cost."""

    text: str = ""
    fwd_passes: int = 0        # stack invocations spent on this plan
    slot_decisions: int = 0    # discrete symbols committed, refinements included
    position_evals: int = 0    # positions whose states were newly computed
    error: str = ""


@dataclass
class CellStats:
    n: int = 0
    correct: int = 0
    parsed: int = 0
    typed: int = 0
    exact: int = 0
    parsed_wrong: int = 0
    reasons: dict = dc_field(default_factory=dict)
    fwd: int = 0
    decisions: int = 0
    positions: int = 0

    def rate(self, k: int) -> float:
        return round(k / self.n, 4) if self.n else 0.0

    def as_dict(self) -> dict:
        return {
            "n": self.n,
            "acc": self.rate(self.correct),
            "parse_rate": self.rate(self.parsed),
            "well_typed_rate": self.rate(self.typed),
            "exact_gold_plan_rate": self.rate(self.exact),
            "parsed_but_wrong_rate": self.rate(self.parsed_wrong),
            "fwd_passes_mean": round(self.fwd / self.n, 3) if self.n else 0.0,
            "slot_decisions_mean": round(self.decisions / self.n, 3) if self.n else 0.0,
            "position_evals_mean": round(self.positions / self.n, 3) if self.n else 0.0,
            "reasons": dict(self.reasons),
        }


def grade(items, outs: list[PlanOut], ops_by_item: list[dict]) -> CellStats:
    """Correctness and the plan level diagnostics, kept apart on purpose.

    The gap between "a plan parses" and "the answer is right" is where what
    remains of the failure lives, so parse rate, well typed rate, exact gold
    plan rate and the parseable but wrong rate are reported beside accuracy and
    never folded into it.
    """
    st = CellStats()
    for it, out, ops in zip(items, outs, ops_by_item):
        st.n += 1
        st.fwd += out.fwd_passes
        st.decisions += out.slot_decisions
        st.positions += out.position_evals
        if out.error:
            _bump(st.reasons, out.error)
            continue
        try:
            plan = parse_plan(out.text)
        except PlanError:
            _bump(st.reasons, "plan_parse")
            continue
        st.parsed += 1
        if well_typed(plan, ops):
            st.typed += 1
        if serialize_plan(plan) == serialize_plan(it.plan):
            st.exact += 1
        try:
            value = run_plan(plan, ops)
        except Exception:
            _bump(st.reasons, "execute")
            st.parsed_wrong += 1
            continue
        if _norm(_as_text(value)) == _norm(it.gold):
            st.correct += 1
            _bump(st.reasons, "ok")
        else:
            st.parsed_wrong += 1
            _bump(st.reasons, "wrong_value")
    return st


def _bump(d: dict, k: str) -> None:
    d[k] = d.get(k, 0) + 1


def _as_text(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _norm(s: str) -> str:
    return str(s).strip().strip(".").strip().lower()


# ------------------------------------------------------------------ planners

class Planner:
    """Builds one plan per item and reports what each plan cost."""

    head = ""

    def build(self, model, tok, items, ops_by_item, device) -> list[PlanOut]:
        raise NotImplementedError


class GoldPlanner(Planner):
    """The gold plan, spending nothing. Used by oracle_plan and oracle_both."""

    head = "gold"

    def __init__(self, roundtrip: str | None = None):
        self.roundtrip = roundtrip

    def build(self, model, tok, items, ops_by_item, device) -> list[PlanOut]:
        outs = []
        for it, ops in zip(items, ops_by_item):
            if self.roundtrip in ("p2s", "p3", "p4"):
                schema = schema_for(self.roundtrip)
                try:
                    outs.append(PlanOut(text=decode_plan_text(
                        encode_plan(it.plan, ops, schema), ops, schema)))
                except SlotError as exc:
                    outs.append(PlanOut(error=f"codec:{exc}"))
            elif self.roundtrip == "p2":
                outs.append(PlanOut(text=from_opcode_text(
                    to_opcode_text(serialize_plan(it.plan), ops), ops)))
            else:
                outs.append(PlanOut(text=serialize_plan(it.plan)))
        return outs


class TextPlanner(Planner):
    """P1 and P2. One causal decode through the pretrained lm_head.

    P1 writes the page's own operator symbol, P2 writes the dedicated opcode
    token for it. Nothing else differs: same prompt shape, same decoder, same
    key/value cache, same stopping rule. A forward pass is one cached decode
    step, and the count charged to an item is the prompt pass plus the tokens
    that item generated before its own end of text.
    """

    def __init__(self, head: str, batch_size: int = 24, max_new: int = 160,
                 temperature: float = 0.0, seed: int = 0):
        self.head = head
        self.batch_size = batch_size
        self.max_new = max_new
        self.temperature = temperature
        self.seed = seed

    def build(self, model, tok, items, ops_by_item, device) -> list[PlanOut]:
        from src.rl.sampler import CachedPolicy
        eot = tok.token_id("<|eot|>")
        outs: list[PlanOut] = [None] * len(items)  # type: ignore[list-item]
        for lo in range(0, len(items), self.batch_size):
            chunk = list(range(lo, min(lo + self.batch_size, len(items))))
            prompts = [plan_prompt_text(ops_by_item[i], items[i].text, self.head)
                       for i in chunk]
            ids = [tok.encode(p) for p in prompts]
            width = max(len(x) for x in ids)
            cap = min(width + self.max_new + 2, model.cfg.max_seq_len)
            policy = CachedPolicy(model, device, max_len=cap,
                                  temperature=self.temperature, seed=self.seed)
            nxt = policy.begin(ids)
            done = [False] * len(chunk)
            gen: list[list[int]] = [[] for _ in chunk]
            fwd = [1] * len(chunk)          # the prompt pass
            pos = [len(x) for x in ids]     # positions read on that pass
            for _ in range(self.max_new):
                step = []
                for i, t in enumerate(nxt):
                    if done[i]:
                        step.append(0)
                        continue
                    if t == eot:
                        done[i] = True
                        step.append(0)
                        continue
                    gen[i].append(int(t))
                    step.append(int(t))
                if all(done):
                    break
                nxt = policy.advance(step)
                for i in range(len(chunk)):
                    if not done[i]:
                        fwd[i] += 1
                        pos[i] += 1
            for i, g in enumerate(chunk):
                text = tok.decode(gen[i]).strip()
                if self.head != "p1":
                    text = from_opcode_text(text, ops_by_item[g])
                outs[g] = PlanOut(text=text, fwd_passes=fwd[i],
                                  slot_decisions=len(gen[i]), position_evals=pos[i])
        return outs


class SlotPlanner(Planner):
    """P2s, P3 and P4. One plan is a fixed length array of discrete slots.

    P2s commits the slots left to right under a causal mask, one stack
    invocation per slot, which is the same generation geometry as P1 and P2 over
    the same alphabet P3 uses. P3 and P4 start from an array that is entirely
    MASK and run a fixed number of bidirectional passes. Each pass re-predicts
    every slot from every other slot and keeps the most confident share, so a
    slot committed early can be overwritten later; the last pass commits what is
    left. A forward pass is one pass over the whole array, so the count is the
    iteration count and not the plan's length.
    """

    def __init__(self, head: str, iters: int = 8, batch_size: int = 24,
                 temperature: float = 0.0, seed: int = 0):
        self.head = head
        self.schema = schema_for(head)
        self.iters = iters
        self.batch_size = batch_size
        self.temperature = temperature
        self.seed = seed

    def build(self, model, tok, items, ops_by_item, device) -> list[PlanOut]:
        outs: list[PlanOut] = [None] * len(items)  # type: ignore[list-item]
        for lo in range(0, len(items), self.batch_size):
            chunk = list(range(lo, min(lo + self.batch_size, len(items))))
            self._batch(model, tok, items, ops_by_item, device, chunk, outs)
        return outs

    def _batch(self, model, tok, items, ops_by_item, device, chunk, outs):
        head = model.plan_head
        schema = self.schema
        s = schema.n_slots
        prompts = [plan_prompt_text(ops_by_item[i], items[i].text, self.head)
                   for i in chunk]
        ids = [tok.encode(p) for p in prompts]
        pw = max(len(x) for x in ids)
        if pw + s > model.cfg.max_seq_len:
            raise SlotError("prompt plus slots exceeds the model context")
        pad = torch.zeros(len(chunk), pw, dtype=torch.long, device=device)
        ok = torch.zeros(len(chunk), pw, dtype=torch.bool, device=device)
        for i, x in enumerate(ids):
            pad[i, pw - len(x):] = torch.tensor(x, device=device)
            ok[i, pw - len(x):] = True
        fmask = field_logit_mask(schema.fields, device)
        gen = torch.Generator(device=device)
        gen.manual_seed(self.seed + chunk[0])
        cur = torch.tensor(all_masked(schema), device=device)[None].repeat(len(chunk), 1)
        causal = self.head == "p2s"
        n_fwd = s if causal else self.iters
        with torch.no_grad():
            if causal:
                for j in range(s):
                    logits = self._logits(model, head, pad, ok, cur, fmask)
                    cur[:, j] = self._pick(logits[:, j], gen)
                decisions = s
                # Under a key/value cache a causal step reads one new position.
                # This implementation recomputes instead, so the wall clock is
                # higher than the number below; the number is the inherent cost.
                positions = pw + s
            else:
                for t in range(self.iters):
                    logits = self._logits(model, head, pad, ok, cur, fmask)
                    probs = torch.softmax(logits, dim=-1)
                    pick = self._pick_all(logits, gen)
                    conf = probs.gather(2, pick[..., None]).squeeze(-1)
                    if t == self.iters - 1:
                        cur = pick
                        break
                    keep = max(1, int(round(s * (t + 1) / self.iters)))
                    order = torch.argsort(conf, dim=1, descending=True)
                    nxt = torch.tensor(all_masked(schema), device=device)[None].repeat(
                        len(chunk), 1)
                    idx = order[:, :keep]
                    nxt.scatter_(1, idx, pick.gather(1, idx))
                    cur = nxt
                decisions = self.iters * s
                # The prompt region is causal and never reads a slot, so its
                # states are the same on every pass and are charged once.
                positions = pw + s * self.iters
        arrays = cur.tolist()
        for i, g in enumerate(chunk):
            out = PlanOut(fwd_passes=n_fwd, slot_decisions=decisions,
                          position_evals=positions)
            try:
                out.text = decode_plan_text(arrays[i], ops_by_item[g], schema)
            except SlotError as exc:
                out.error = f"slot_decode:{str(exc)[:40]}"
            outs[g] = out

    def _logits(self, model, head, pad, ok, cur, fmask):
        causal = self.head == "p2s"
        with torch.autocast(device_type="cuda" if pad.is_cuda else "cpu",
                            dtype=torch.bfloat16, enabled=pad.is_cuda):
            hidden = slot_forward(model, head, pad, ok, cur, self.schema,
                                  causal_slots=causal)
        return slot_logits(head, readout(hidden, causal).float(), fmask)

    def _pick(self, logits, gen):
        if self.temperature <= 0:
            return logits.argmax(-1)
        p = torch.softmax(logits / self.temperature, dim=-1)
        return torch.multinomial(p, 1, generator=gen).squeeze(-1)

    def _pick_all(self, logits, gen):
        if self.temperature <= 0:
            return logits.argmax(-1)
        b, s, v = logits.shape
        p = torch.softmax(logits.reshape(-1, v) / self.temperature, dim=-1)
        return torch.multinomial(p, 1, generator=gen).view(b, s)


def make_planner(head: str, **kw) -> Planner:
    if head in ("p1", "p2"):
        return TextPlanner(head, batch_size=kw.get("batch_size", 24),
                           max_new=kw.get("max_new", 160),
                           temperature=kw.get("temperature", 0.0),
                           seed=kw.get("seed", 0))
    if head in ("p2s", "p3", "p4"):
        return SlotPlanner(head, iters=kw.get("iters", 8),
                           batch_size=kw.get("batch_size", 24),
                           temperature=kw.get("temperature", 0.0),
                           seed=kw.get("seed", 0))
    raise ValueError(f"unknown head {head!r}")


HEADS = ("p1", "p2", "p2s", "p3", "p4")
