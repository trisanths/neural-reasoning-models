"""Tests for the typed core.

They pin the two properties the rest of the workflow leans on, that the round
trip is the identity and that the interpreter refuses rather than guesses, and
they pin the corpus defects this lane found so that a later change to the
corpus cannot quietly move a number without a test going red.
"""

from __future__ import annotations

import json
import unittest

from src.norm.gen import make_for
from src.norm.interp import Cannot, Result, eval_expr, run
from src.norm.lang import (Affine, Bands, Lit, OpDef, Program, Ref, Rule, Step,
                           Table, Weights, program_json, program_load)
from src.norm.parse import parse
from src.norm.render import SHAPES, classify, frames, render
from src.norm.shapes import assemble
from src.opgraph import opdef, plan as opplan
from src.opgraph.opdef import parse_expr


def sample_frames(n=24):
    fr, _ = frames()
    step = max(1, len(fr) // n)
    return fr[::step]


class TestRoundTrip(unittest.TestCase):

    def test_identity_and_rerender(self):
        for f in sample_frames(16):
            for i, shape in enumerate(SHAPES):
                p = make_for(f.fid, shape, 4242 + i)
                text = render(p, f.fid, preamble_level=i % 13)["text"]
                got = parse(text, f.fid)
                self.assertTrue(got.ok, f"{f.fid}/{shape}: {got.reason}")
                self.assertEqual(got.program, p, f"{f.fid}/{shape}")
                self.assertEqual(
                    render(got.program, f.fid, preamble_level=i % 13)["text"],
                    text, f"{f.fid}/{shape}")

    def test_classify_names_the_shape_it_was_built_as(self):
        f = sample_frames(4)[0]
        for shape in SHAPES:
            self.assertEqual(classify(make_for(f.fid, shape, 11)), shape)

    def test_json_round_trip(self):
        f = sample_frames(4)[0]
        for shape in SHAPES:
            p = make_for(f.fid, shape, 77)
            self.assertEqual(program_load(json.loads(json.dumps(
                program_json(p)))), p)

    def test_equality_sees_one_changed_entry(self):
        t = Table("T", (("a", "b"), ("c", "d")), "z")
        u = Table("T", (("a", "b"), ("c", "e")), "z")
        self.assertNotEqual(t, u)
        self.assertNotEqual(assemble("lookup", tables=[t], inputs=(("x", "a"),)),
                            assemble("lookup", tables=[u], inputs=(("x", "a"),)))

    def test_truncated_text_is_refused(self):
        f = sample_frames(4)[0]
        p = make_for(f.fid, "lookup", 9)
        text = render(p, f.fid)["text"]
        self.assertFalse(parse("\n\n".join(text.split("\n\n")[:-1]), f.fid).ok)
        self.assertFalse(parse("", f.fid).ok)


class TestInterpreterRefuses(unittest.TestCase):

    def refusal(self, program) -> str:
        r = run(program)
        self.assertFalse(r.ok, f"expected a refusal, got {r.value!r}")
        self.assertIsNone(r.value)
        return r.reason

    def test_missing_key_with_no_default(self):
        t = Table("T", (("a", "b"),))
        self.assertIn("no entry", self.refusal(
            assemble("lookup", tables=[t], inputs=(("x", "zz"),))))

    def test_default_is_used_when_stated(self):
        t = Table("T", (("a", "b"),), "fall")
        r = run(assemble("lookup", tables=[t], inputs=(("x", "zz"),)))
        self.assertTrue(r.ok)
        self.assertEqual(r.value, "fall")

    def test_two_values_for_one_key_is_a_refusal(self):
        t = Table("T", (("a", "b"), ("a", "c")))
        self.assertIn("different values", self.refusal(
            assemble("lookup", tables=[t], inputs=(("x", "a"),))))

    def test_inverse_must_be_unique(self):
        t = Table("T", (("a", "v"), ("b", "v")))
        self.assertIn("inverts", self.refusal(
            assemble("inverse", tables=[t], inputs=(("x", "v"),))))

    def test_unknown_definition(self):
        p = Program((), (("x", "a"),),
                    (Step("t1", "lookup", ("Nope", Ref("x"))),), "t1")
        self.assertIn("no table", self.refusal(p))

    def test_unknown_operation(self):
        p = Program((Table("T", (("a", "b"),)),), (("x", "a"),),
                    (Step("t1", "frobnicate", ("T", Ref("x"))),), "t1")
        self.assertIn("unknown operation", self.refusal(p))

    def test_reading_a_temporary_before_it_is_written(self):
        p = Program((Table("T", (("a", "b"),)),), (),
                    (Step("t1", "lookup", ("T", Ref("t2"))),), "t1")
        self.assertIn("before it is written", self.refusal(p))

    def test_precondition_failure(self):
        op = OpDef("f", ("n",), parse_expr("(* 2 n)"),
                   pre=(parse_expr("(>= n 0)"),))
        p = Program((op,), (("x", -3),),
                    (Step("t1", "call", ("f", Ref("x"))),), "t1")
        self.assertIn("precondition", self.refusal(p))

    def test_type_mismatch_is_a_refusal(self):
        b = Bands("B", "attr", (10,), ("lo", "hi"))
        self.assertIn("needs a number", self.refusal(
            assemble("classify", bands=b, inputs=(("x", "word"),))))

    def test_a_refusal_carries_no_answer_text(self):
        t = Table("T", (("a", "b"),))
        self.assertEqual(run(assemble("lookup", tables=[t],
                                      inputs=(("x", "zz"),))).text, "")


class TestSemantics(unittest.TestCase):

    def test_band_edges_are_low_inclusive_high_exclusive(self):
        b = Bands("B", "a", (30, 60), ("lo", "mid", "hi"))
        for x, want in ((29, "lo"), (30, "mid"), (59, "mid"), (60, "hi")):
            r = run(assemble("classify", bands=b, inputs=(("x", x),)))
            self.assertTrue(r.ok)
            self.assertEqual(r.value, want, f"at {x}")

    def test_ordered_table_takes_the_first_matching_row(self):
        t = Table("T", (("g1", "v1"), ("g2", "v2"), ("g3", "v3")), "v1", True)
        r = run(assemble("priority", tables=[t], inputs=(("x", ("g3", "g2")),)))
        self.assertTrue(r.ok)
        self.assertEqual(r.value, "v2")

    def test_exception_beats_the_general_rule(self):
        r = Rule("R", "gen", (("k", "spec"),))
        self.assertEqual(run(assemble("lookup_general", rule=r,
                                      inputs=(("x", "k"),))).value, "spec")
        self.assertEqual(run(assemble("lookup_general", rule=r,
                                      inputs=(("x", "q"),))).value, "gen")

    def test_precedence_prefers_the_first_table(self):
        a = Table("A", (("k", "good"),))
        b = Table("B", (("k", "bad"),))
        self.assertEqual(run(assemble("precedence", tables=[a, b],
                                      inputs=(("x", "k"),))).value, "good")

    def test_several_simultaneous_conditions_in_one_operator(self):
        op = OpDef("score", ("base", "marked", "flagged"),
                   parse_expr("(+ base (if marked 10 0) (if flagged -5 0))"))
        for marked, flagged, want in ((False, False, 40), (True, False, 50),
                                      (False, True, 35), (True, True, 45)):
            p = Program((op,), (("b", 40), ("m", marked), ("f", flagged)),
                        (Step("t1", "call", ("score", Ref("b"), Ref("m"),
                                             Ref("f"))),), "t1")
            self.assertEqual(run(p).value, want, f"{marked}/{flagged}")

    def test_a_plan_calling_more_than_one_distinct_operator(self):
        a = OpDef("mid", ("n",), parse_expr("(* 4 n)"))
        b = OpDef("big", ("n",), parse_expr("(* 48 n)"))
        p = Program((a, b), (("x", 3), ("y", 2)),
                    (Step("t1", "call", ("mid", Ref("x"))),
                     Step("t2", "call", ("big", Ref("y"))),
                     Step("t3", "add", (Ref("t1"), Ref("t2")))), "t3")
        self.assertEqual(run(p).value, 108)
        self.assertEqual(p.distinct_operators(), 3)


class TestUnbounded(unittest.TestCase):

    def test_plan_depth_past_the_opgraph_cap(self):
        width = 16
        nodes = [f"n{i}" for i in range(width)]
        t = Table("R", tuple((nodes[i], nodes[(i + 1) % width])
                             for i in range(width)))
        for depth in (2, 128, 129, 2000):
            p = assemble("iterate", tables=[t], inputs=(("x", nodes[0]),),
                         n=depth)
            r = run(p)
            self.assertTrue(r.ok, f"depth {depth}: {r.reason}")
            self.assertEqual(r.value, nodes[depth % width], f"depth {depth}")

    def test_the_opgraph_executor_stops_where_this_one_does_not(self):
        d = opplan.MAX_STEPS + 1
        text = " ; ".join([f"t{i} = add 1 1" for i in range(1, d + 1)]
                          + [f"ans t{d}"])
        with self.assertRaises(opplan.PlanError):
            opplan.parse_plan(text)

    def test_expression_nesting_past_the_opdef_cap(self):
        e = opdef.Var("x")
        for _ in range(5000):
            e = opdef.Call("+", (e, 1))
        self.assertEqual(eval_expr(e, {"x": 0}), 5000)
        with self.assertRaises(opdef.OpError):
            opdef.eval_expr(e, {"x": 0})


class TestCorpusDefects(unittest.TestCase):
    """Pinned so a corpus change cannot move these numbers unnoticed."""

    def test_inverse_chain_question_does_not_ask_for_its_own_gold(self):
        from src.norm.witness import witness
        w = witness(depth=2)
        self.assertNotEqual(w["answer_to_the_question_as_written"], w["gold"])
        self.assertEqual(len(w["scopes_the_question_names"]), 1)
        self.assertEqual(len(w["pages_served"]), 2)

    def test_procedure_decide_items_state_their_own_answer(self):
        import random
        from src.skillacq.systems import ProcedureSystem, _answer_is_copyable
        s = ProcedureSystem(random.Random(3))
        got = [q for q in s.problems(random.Random(4), 60)
               if q["kind"] == "decide"]
        self.assertTrue(got)
        self.assertTrue(all(_answer_is_copyable(q["answer"], q["text"])
                            for q in got))

    def test_unit_system_repeats_a_unit_name(self):
        import random
        from src.skillacq.systems import UnitSystem
        dup = sum(1 for s in range(20000)
                  if len({(u := UnitSystem(random.Random(s))).base,
                          u.mid, u.big}) < 3)
        self.assertGreater(dup, 0)
        self.assertLess(dup / 20000, 0.02)


if __name__ == "__main__":
    unittest.main()
