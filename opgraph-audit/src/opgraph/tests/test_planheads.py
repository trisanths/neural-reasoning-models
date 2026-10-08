"""Tests for the plan heads: the codec, the corruption mixture, the masks.

Everything here runs on the CPU in a few seconds and needs no checkpoint. The
codec tests are the ones that matter most: if a gold plan cannot survive a round
trip through a head's representation, that head is capped and every number it
produces is a measurement of the cap rather than of the head.
"""

import random

import pytest
import torch

from src.opgraph import planheads as ph
from src.opgraph.data import eval_items
from src.opgraph.plan import parse_plan, run_plan, serialize_plan


def _items():
    out = []
    for kind, depths in (("sequential", [1, 3, 5, 8]), ("novel", [2, 4, 6]),
                         ("breadth", [1, 3, 6]), ("sequential_paren", [2, 5]),
                         ("same_page_pair", [2]), ("units", [1])):
        for d in depths:
            out.extend(eval_items(kind, d, 3))
    return out


ITEMS = _items()


@pytest.mark.parametrize("head", ["p2s", "p3", "p4"])
def test_gold_plan_survives_the_slot_codec(head):
    schema = ph.schema_for(head)
    for it in ITEMS:
        ops = it.world.ops
        slots = ph.encode_plan(it.plan, ops, schema)
        assert len(slots) == schema.n_slots
        text = ph.decode_plan_text(slots, ops, schema)
        plan = parse_plan(text)
        assert str(run_plan(plan, ops)) == it.gold
        assert serialize_plan(plan) == serialize_plan(it.plan)


def test_gold_plan_survives_the_opcode_text_form():
    for it in ITEMS:
        ops = it.world.ops
        text = ph.to_opcode_text(serialize_plan(it.plan), ops)
        assert all(s not in text.split() for s in ops)
        back = ph.from_opcode_text(text, ops)
        assert serialize_plan(parse_plan(back)) == serialize_plan(it.plan)


@pytest.mark.parametrize("head", ["p2s", "p3", "p4"])
def test_every_slot_holds_a_symbol_from_its_own_field(head):
    schema = ph.schema_for(head)
    fields = schema.fields
    for it in ITEMS[:40]:
        slots = ph.encode_plan(it.plan, it.world.ops, schema)
        for i, v in enumerate(slots):
            base = ph.FIELD_BASE[fields[i]]
            assert base <= v < base + ph.FIELD_SIZE[fields[i]]


def test_masked_slots_are_rejected_rather_than_repaired():
    it = ITEMS[0]
    ops = it.world.ops
    slots = ph.encode_plan(it.plan, ops, ph.FLAT)
    slots[ph.FLAT.opcode_slot(0)] = ph.gid(ph.F_OPCODE, ph.O_MASK)
    with pytest.raises(ph.SlotError):
        ph.decode_plan_text(slots, ops, ph.FLAT)
    slots = ph.encode_plan(it.plan, ops, ph.FLAT)
    slots[ph.FLAT.answer_slot] = ph.gid(ph.F_ANS, ph.G_MASK)
    with pytest.raises(ph.SlotError):
        ph.decode_plan_text(slots, ops, ph.FLAT)


def test_an_opcode_past_the_table_is_rejected():
    it = ITEMS[0]
    ops = it.world.ops
    slots = ph.encode_plan(it.plan, ops, ph.FLAT)
    slots[ph.FLAT.opcode_slot(0)] = ph.gid(ph.F_OPCODE, ph.O_OP0 + ph.K_MAX - 1)
    with pytest.raises(ph.SlotError):
        ph.decode_plan_text(slots, ops, ph.FLAT)


def test_a_gap_in_the_flat_node_prefix_is_rejected():
    it = next(i for i in ITEMS if len(i.plan.steps) >= 2)
    ops = it.world.ops
    slots = ph.encode_plan(it.plan, ops, ph.FLAT)
    slots[ph.FLAT.opcode_slot(0)] = ph.gid(ph.F_OPCODE, ph.O_EMPTY)
    with pytest.raises(ph.SlotError):
        ph.decode_plan_text(slots, ops, ph.FLAT)


def test_graph_execution_follows_the_dependency_edges_not_the_array_order():
    """Node zero reads what node one writes, so the emitted plan runs one first."""
    it = next(i for i in ITEMS if i.kind == "sequential")
    ops = it.world.ops
    sym = sorted(ops)[0]
    while ops[sym].arity != 2:
        sym = sorted(ops)[sorted(ops).index(sym) + 1]
    k = sorted(ops).index(sym)
    s = ph.GRAPH
    slots = [ph.gid(f, ph.EMPTY_LOCAL[f]) for f in s.fields]
    for node, (reg, args, deps) in enumerate((
            (1, [ph.G_TEMP0 + 1, ph.G_INT0 + 5], [ph.D_NODE0 + 1, ph.D_NONE]),
            (2, [ph.G_INT0 + 3, ph.G_INT0 + 4], [ph.D_NONE, ph.D_NONE]))):
        slots[s.active_slot(node)] = ph.gid(ph.F_ACTIVE, ph.A_YES)
        slots[s.opcode_slot(node)] = ph.gid(ph.F_OPCODE, ph.O_OP0 + k)
        slots[s.reg_slot(node)] = ph.gid(ph.F_REG, ph.R_REG0 + reg - 1)
        for j, a in enumerate(args):
            slots[s.arg_slot(node, j)] = ph.gid(ph.F_ARG, a)
        for j, d in enumerate(deps):
            slots[s.dep_slot(node, j)] = ph.gid(ph.F_DEP, d)
    slots[s.answer_slot] = ph.gid(ph.F_ANS, ph.G_TEMP0)
    text = ph.decode_plan_text(slots, ops, s)
    assert text.split(";")[0].strip().startswith("t2 =")
    assert run_plan(parse_plan(text), ops) == ops[sym](ops[sym](3, 4), 5)


def test_a_dependency_cycle_is_rejected():
    it = next(i for i in ITEMS if len(i.plan.steps) >= 2)
    ops = it.world.ops
    s = ph.GRAPH
    slots = ph.encode_plan(it.plan, ops, s)
    slots[s.dep_slot(0, 0)] = ph.gid(ph.F_DEP, ph.D_NODE0 + 1)
    slots[s.dep_slot(1, 0)] = ph.gid(ph.F_DEP, ph.D_NODE0 + 0)
    with pytest.raises(ph.SlotError):
        ph.decode_plan_text(slots, ops, s)


def test_two_active_nodes_cannot_share_a_register():
    it = next(i for i in ITEMS if len(i.plan.steps) >= 2)
    ops = it.world.ops
    s = ph.GRAPH
    slots = ph.encode_plan(it.plan, ops, s)
    slots[s.reg_slot(1)] = slots[s.reg_slot(0)]
    with pytest.raises(ph.SlotError):
        ph.decode_plan_text(slots, ops, s)


@pytest.mark.parametrize("head", ["p3", "p4"])
def test_corruption_draws_every_declared_type_and_stays_in_field(head):
    schema = ph.schema_for(head)
    mixture = ph.mixture_for(head)
    rng = random.Random(0)
    seen = set()
    fields = schema.fields
    for _ in range(400):
        it = rng.choice(ITEMS)
        gold = ph.encode_plan(it.plan, it.world.ops, schema)
        bad, kind = ph.corrupt(gold, schema, len(it.world.ops), rng, mixture)
        seen.add(kind)
        assert len(bad) == len(gold)
        for i, v in enumerate(bad):
            base = ph.FIELD_BASE[fields[i]]
            assert base <= v < base + ph.FIELD_SIZE[fields[i]]
    assert seen == set(mixture)


def test_all_mask_is_in_the_training_distribution():
    """The inference time starting point has to be a corruption the head saw."""
    schema = ph.FLAT
    rng = random.Random(1)
    gold = ph.encode_plan(ITEMS[0].plan, ITEMS[0].world.ops, schema)
    hits = 0
    for _ in range(200):
        bad, kind = ph.corrupt(gold, schema, 6, rng, ph.MIXTURE_FLAT)
        if kind == "all_mask":
            hits += 1
            assert bad == ph.all_masked(schema)
    assert hits > 0


def test_field_logit_mask_opens_exactly_one_field_per_slot():
    m = ph.field_logit_mask(ph.GRAPH.fields, "cpu")
    assert m.shape == (ph.GRAPH.n_slots, ph.N_SYMBOLS)
    for i, f in enumerate(ph.GRAPH.fields):
        assert int(m[i].sum()) == ph.FIELD_SIZE[f]
        assert bool(m[i, ph.FIELD_BASE[f]])


def test_prefix_mask_lets_slots_see_each_other_and_keeps_the_prompt_causal():
    ok = torch.ones(1, 6, dtype=torch.bool)
    ok[0, 0] = False                       # one left padding column
    m = ph.build_mask(6, 3, ok, causal_slots=False)[0, 0]
    assert not bool(m[2, 3])               # a prompt row cannot read a slot
    assert bool(m[4, 5]) and bool(m[5, 4])  # slots read each other both ways
    assert not bool(m[4, 0])               # nothing reads the padding column
    assert bool(m[0, 0])                   # except the padding row itself
    c = ph.build_mask(6, 3, ok, causal_slots=True)[0, 0]
    assert not bool(c[4, 5]) and bool(c[5, 4])


def test_well_typed_catches_a_wrong_arity_and_an_unknown_symbol():
    ops = ITEMS[0].world.ops
    sym = next(s for s in ops if ops[s].arity == 2)
    assert ph.well_typed(parse_plan(f"t1 = {sym} 1 2 ; ans t1"), ops)
    assert not ph.well_typed(parse_plan(f"t1 = {sym} 1 ; ans t1"), ops)
    assert not ph.well_typed(parse_plan("t1 = zzz 1 2 ; ans t1"), ops)


def test_schema_shapes_cover_the_evaluation_grid():
    assert ph.FLAT.n_slots == ph.N_NODES * (1 + ph.A_MAX) + 1
    assert ph.GRAPH.n_slots == ph.N_NODES * (3 + ph.A_MAX + 2) + 1
    assert max(len(i.plan.steps) for i in ITEMS) <= ph.N_NODES
    assert max(len(i.world.ops) for i in ITEMS) <= ph.K_MAX


# ------------------------------------------------- the conditioning probe

def test_a_gold_graph_array_never_disagrees_with_itself():
    """P4 writes every dependency twice and the two copies must agree on gold.

    An argument naming t_k and an edge naming the node that writes t_k are the
    same fact. A predicted array can hold the two in disagreement, and such an
    array still parses and still executes, in the wrong order, giving a wrong
    answer with no error raised. The probe measures that rate, so it has to read
    zero on an array the encoder built.
    """
    from scripts.planheads_condprobe import make_one_wrong  # noqa: F401
    from scripts.planheads_slotdiag import arg_dep_disagreement

    schema = ph.schema_for("p4")
    seen = 0
    for it in eval_items("sequential", 3, 8):
        slots = ph.encode_plan(it.plan, it.world.ops, schema)
        assert arg_dep_disagreement(slots, schema) is False
        seen += 1
    assert seen


def test_a_flat_array_has_no_edges_to_disagree_about():
    from scripts.planheads_slotdiag import arg_dep_disagreement

    schema = ph.schema_for("p3")
    it = eval_items("sequential", 2, 1)[0]
    slots = ph.encode_plan(it.plan, it.world.ops, schema)
    assert arg_dep_disagreement(slots, schema) is None


def test_one_wrong_opcode_changes_exactly_one_slot():
    """The repair probe has to corrupt one opcode and nothing else, or the
    restoration rate it reports is measuring some other edit."""
    from scripts.planheads_condprobe import make_one_wrong

    rng = random.Random(3)
    schema = ph.schema_for("p3")
    for it in eval_items("sequential", 3, 6):
        gold = ph.encode_plan(it.plan, it.world.ops, schema)
        wrong, j = make_one_wrong(gold, schema, len(it.world.ops), rng)
        assert j is not None
        differ = [k for k in range(len(gold)) if gold[k] != wrong[k]]
        assert differ == [j]
        assert schema.fields[j] == ph.F_OPCODE


def test_the_slot_planner_reports_the_array_it_committed():
    """PlanOut.slots is what the probes read. An empty default on a slot head
    would make every field accuracy silently zero."""
    out = ph.PlanOut()
    assert out.slots == []
