import random

import pytest

from src.opgraph import data, invent
from src.opgraph.opdef import (OpError, parse_operator, parse_operators,
                               serialize, serialize_all, verify)
from src.opgraph.plan import (PlanError, answer_text, parse_plan, run_plan,
                              serialize_plan)


def test_operator_round_trip_and_execution():
    text = "(defop @ (x y) (% (+ (* 3 x) (* 7 y) 2) 100) (ex (7 4) 72))"
    op = parse_operator(text)
    assert op.symbol == "@" and op.arity == 2
    assert op(7, 4) == (3 * 7 + 7 * 4 + 2) % 100
    assert serialize(op) == text


def test_conditional_and_string_results():
    op = parse_operator("(defop decide (s) (if (>= s 55) 'accepted 'refused))")
    assert op(60) == "accepted"
    assert op(54) == "refused"
    assert serialize(op) == "(defop decide (s) (if (>= s 55) 'accepted 'refused))"


def test_malformed_operators_raise():
    for bad in ["(defop @ (x y) (+ x z))", "(defop @ (x) (bogus x))",
                "(defop @ (x y) (+ x y)", "defop @ (x) x",
                "(defop @ (x y) (- x y) (junk 1))"]:
        with pytest.raises(OpError):
            parse_operator(bad)


def test_verification_catches_a_wrong_induction():
    good = parse_operator("(defop @ (x y) (+ x y) (ex (7 4) 11))")
    bad = parse_operator("(defop @ (x y) (* x y) (ex (7 4) 11))")
    assert verify(good)[0] is True
    assert verify(bad)[0] is False


def test_multiple_operators_from_one_page():
    ops = parse_operators("(defop a (n) (* n 4)) (defop b (n) (* n 12))")
    assert [o.symbol for o in ops] == ["a", "b"]
    assert serialize_all(ops).count("defop") == 2


def test_plan_round_trip_and_execution():
    ops = {"@": parse_operator("(defop @ (x y) (+ x y))")}
    p = parse_plan("t1 = @ 7 4 ; t2 = @ t1 9 ; ans t2")
    assert serialize_plan(p) == "t1 = @ 7 4 ; t2 = @ t1 9 ; ans t2"
    assert run_plan(p, ops) == 20
    assert p.depth == 2


def test_plan_rejects_forward_references_and_unknown_symbols():
    with pytest.raises(PlanError):
        parse_plan("t1 = @ t2 4 ; t2 = @ 1 2 ; ans t1")
    with pytest.raises(PlanError):
        run_plan(parse_plan("t1 = ? 1 2 ; ans t1"), {})


@pytest.mark.parametrize("seed", range(25))
def test_gold_plan_reproduces_gold_answer(seed):
    rng = random.Random(seed)
    breadth = rng.choice([1, 2, 3])
    w = invent.make_world(seed, breadth=breadth)
    items = [invent.seq_flat(w, rng, 4), invent.seq_paren(w, rng, 3),
             invent.breadth_item(w, rng, breadth), invent.units_item(w, rng),
             invent.novel(w, rng, 4), invent.decide_item(w, rng)]
    for it in items:
        value = run_plan(it.plan, w.ops)
        assert answer_text(value) == it.gold, it.kind


@pytest.mark.parametrize("seed", range(15))
def test_page_worked_examples_verify_the_gold_operator(seed):
    w = invent.make_world(seed, breadth=3)
    for page in w.pages:
        for op in page.ops:
            if op.examples:
                assert verify(op)[0], (page.key, op.symbol)


@pytest.mark.parametrize("seed", range(15))
def test_gold_operators_round_trip_through_text(seed):
    w = invent.make_world(seed, breadth=2)
    for page in w.pages:
        again = parse_operators(serialize_all(page.ops))
        assert serialize_all(again) == serialize_all(page.ops)


@pytest.mark.parametrize("seed", range(20))
def test_answer_is_never_copyable_out_of_the_question(seed):
    rng = random.Random(seed + 500)
    w = invent.make_world(seed, breadth=3)
    for it in [invent.seq_flat(w, rng, 3), invent.novel(w, rng, 3),
               invent.breadth_item(w, rng, 3)]:
        assert f" {it.gold} " not in f" {it.text} "


def test_novel_items_use_two_distinct_operators():
    rng = random.Random(3)
    w = invent.make_world(11, breadth=2)
    for d in range(2, 7):
        it = invent.novel(w, rng, d)
        assert len(set(s.symbol for s in it.plan.steps)) == 2
        assert it.plan.depth == d


def test_training_examples_never_mix_two_symbols():
    for seed in range(60):
        for prompt, target in data.training_examples(seed, "opgraph"):
            if " plan " in prompt:
                syms = {c.split()[2] for c in target.split(";")
                        if "=" in c}
                assert len(syms) == 1, target


def test_two_arms_see_the_same_questions():
    for seed in range(20):
        d = data.training_examples(seed, "direct")
        o = data.training_examples(seed, "opgraph")
        qd = sorted(p.split("<|q|>")[1].split("<|a|>")[0].strip() for p, _ in d)
        qo = sorted(p.split("<|q|>")[1].replace("plan", "", 1).split("<|a|>")[0].strip()
                    for p, _ in o if " plan " in p)
        assert qd == qo


def test_eval_items_are_disjoint_worlds_from_training():
    train_seeds = set(range(100_000))
    items = data.eval_items("sequential", 4, 8)
    assert all(it.world.seed not in train_seeds for it in items)
    assert all(it.plan.depth == 4 for it in items)


def test_eval_worlds_are_shared_across_depths_of_one_kind():
    a = data.eval_items("novel", 2, 6)
    b = data.eval_items("novel", 5, 6)
    assert [x.world.seed for x in a] == [x.world.seed for x in b]
    assert all(x.plan.depth == 5 for x in b)


def test_breadth_worlds_track_the_breadth():
    for b in (1, 4, 6):
        items = data.eval_items("breadth", b, 4)
        for it in items:
            assert it.world.ops["score"].arity == b + 1


def test_written_out_trace_matches_the_executed_answer():
    from src.opgraph.plan import trace_answer, trace_text
    rng = random.Random(9)
    w = invent.make_world(77, breadth=3)
    for it in [invent.seq_flat(w, rng, 5), invent.novel(w, rng, 4),
               invent.breadth_item(w, rng, 3), invent.decide_item(w, rng)]:
        text = trace_text(it.plan, w.ops)
        assert trace_answer(text) == it.gold, it.kind
        assert text.count("->") == it.plan.depth


def test_trace_arm_sees_the_same_questions_as_the_direct_arm():
    for seed in range(20):
        d = data.training_examples(seed, "direct")
        t = data.training_examples(seed, "trace")
        qd = sorted(p.split("<|q|>")[1].split("<|a|>")[0].strip() for p, _ in d)
        qt = sorted(p.split("<|q|>")[1].replace("trace", "", 1).split("<|a|>")[0].strip()
                    for p, _ in t)
        assert qd == qt


def test_operator_symbol_is_never_the_equals_sign():
    for seed in range(200):
        w = invent.make_world(seed, breadth=2)
        assert "=" not in [p.glyph for p in w.pages if p.key.startswith("binop:")]


@pytest.mark.parametrize("seed", range(20))
def test_paraphrased_pages_define_the_same_operators(seed):
    from src.opgraph.opdef import serialize_expr
    a = invent.make_world(seed, breadth=3, style=0)
    b = invent.make_world(seed, breadth=3, style=1)
    assert sorted(a.ops) == sorted(b.ops)
    for sym in a.ops:
        assert a.ops[sym].params == b.ops[sym].params
        assert serialize_expr(a.ops[sym].body) == serialize_expr(b.ops[sym].body)
    assert [p.text for p in a.pages] != [p.text for p in b.pages]


@pytest.mark.parametrize("seed", range(12))
def test_paraphrased_pages_still_verify_their_worked_examples(seed):
    w = invent.make_world(seed, breadth=3, style=1)
    for page in w.pages:
        for op in page.ops:
            if op.examples:
                assert verify(op)[0], (page.key, op.symbol)


@pytest.mark.parametrize("seed", range(12))
def test_paraphrased_worlds_answer_the_same_questions(seed):
    a = data.eval_items("sequential", 3, 4, style=0)
    b = data.eval_items("sequential", 3, 4, style=1)
    assert [x.text for x in a] == [x.text for x in b]
    assert [x.gold for x in a] == [x.gold for x in b]


def test_associativity_round_trips_and_reaches_the_scheduler():
    from src.opgraph.plan import signature_line
    text = "(defop @ (x y) (+ x y) (assoc right) (ex (7 4) 11))"
    op = parse_operator(text)
    assert op.assoc == "right"
    assert serialize(op) == text
    assert signature_line({"@": op}) == "@/2/right"
    plain = parse_operator("(defop score (v) v)")
    assert signature_line({"score": plain}) == "score/1"
    with pytest.raises(OpError):
        parse_operator("(defop @ (x y) (+ x y) (assoc sideways))")


@pytest.mark.parametrize("seed", range(15))
def test_binary_operators_carry_the_associativity_their_page_states(seed):
    w = invent.make_world(seed, breadth=2)
    for page in w.pages:
        if not page.key.startswith("binop:"):
            continue
        op = page.ops[0]
        assert op.assoc in ("left", "right")
        stated = "right to left" if page.right_assoc else "left to right"
        assert stated in page.text
        assert op.assoc == ("right" if page.right_assoc else "left")


def test_stepwise_examples_reconstruct_the_whole_plan():
    from src.opgraph.data import step_examples
    from src.opgraph.plan import parse_plan
    rng = random.Random(4)
    w = invent.make_world(31, breadth=2)
    for it in [invent.seq_flat(w, rng, 5), invent.novel(w, rng, 4),
               invent.breadth_item(w, rng, 2)]:
        ex = step_examples(w.ops, it.text, it.plan)
        assert len(ex) == it.plan.depth + 1
        rebuilt = " ; ".join(t for _, t in ex)
        assert parse_plan(rebuilt) == it.plan
        assert ex[-1][1].startswith("ans")
        # every prompt carries exactly the steps emitted before it
        for k, (prompt, _) in enumerate(ex):
            assert prompt.count("=") == k


def test_stepwise_arm_and_plan_arm_share_their_induction_examples():
    for seed in range(15):
        a = [e for e in data.training_examples(seed, "opgraph") if "induce" in e[0]]
        b = [e for e in data.training_examples(seed, "opgraph_step") if "induce" in e[0]]
        assert a == b
