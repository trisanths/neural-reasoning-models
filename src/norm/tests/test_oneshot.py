"""The gates on the one shot lane.

Four things have to hold or the acquisition numbers mean nothing: the reader
must recover the operation the page states for every operation the grammar can
state, it must refuse rather than guess when a page is missing or written in a
wording it has no template for, the library must refuse two pages that state
different operations under one name, and the extended target language must be
exact both ways so that a wrong answer from the network is a wrong structure
and not a lost one.
"""

import os
import random
import sys
import unittest

from src.norm import ndata, oplang, opread, opsay, optok, opitems
from src.norm.interp import run
from src.norm.lang import NormError
from src.norm.ntok import InputVocab, english_from_frames
from src.norm.render import frames

FIDS = ("abstract.conditional.key_first.cloze.scope_first",
        "routing.table_row.value_first.wh.scope_last",
        "depot.imperative.key_first.imperative.scope_first")


def _instance(sk, fid, seed):
    return opitems.draw_instance(sk, fid, seed)


class ReaderRecoversEveryOperation(unittest.TestCase):
    def test_one_clause_space(self):
        """Every operation statable with one clause, read back exactly."""
        space = oplang.distinct_space(1)
        self.assertEqual(len(space), 144)
        bad = []
        for i, sk in enumerate(space):
            fid = FIDS[i % len(FIDS)]
            inst = _instance(sk, fid, 900 + i)
            if inst is None:
                continue
            mode = opsay.READ_MODES[i % len(opsay.READ_MODES)]
            e = opitems.episode(inst, fid, "single", inst["keys"][0],
                                mode=mode,
                                def_pos=("first", "last")[i % 2])
            if e is None:
                continue
            got = opread.read(e["text"], fid)
            if not got.ok:
                bad.append((i, got.reason))
                continue
            spec = got.library.get(inst["spec"].name)
            if spec != inst["spec"]:
                bad.append((i, f"{spec} != {inst['spec']}"))
        self.assertEqual(bad, [])

    def test_answers_match_the_interpreter(self):
        space = oplang.distinct_space(1)
        rng = random.Random(3)
        for i in rng.sample(range(len(space)), 40):
            fid = FIDS[i % len(FIDS)]
            inst = _instance(space[i], fid, 1300 + i)
            if inst is None:
                continue
            for key in inst["keys"][:3]:
                e = opitems.episode(inst, fid, "single", key)
                if e is None:
                    continue
                got = opread.answer(e["text"], fid)
                self.assertEqual(got["state"], "ran", got.get("reason"))
                self.assertEqual(got["answer"], e["gold"])


class RefusesRatherThanGuesses(unittest.TestCase):
    def test_held_wording_is_refused(self):
        sk = oplang.distinct_space(1)[7]
        inst = _instance(sk, FIDS[0], 55)
        e = opitems.episode(inst, FIDS[0], "single", inst["keys"][0],
                            mode=opsay.HELD_MODE)
        got = opread.read(e["text"], FIDS[0])
        self.assertFalse(got.ok)
        self.assertEqual(got.stage, "definition")

    def test_missing_definition_is_refused(self):
        sk = oplang.distinct_space(1)[9]
        inst = _instance(sk, FIDS[0], 56)
        pages = [opsay.directory_page(t, FIDS[0]) for t in inst["tables"]]
        q = opsay.question_single(inst["spec"], FIDS[0], inst["keys"][0])
        text = opsay.episode_text(pages, [], q)
        got = opread.read(text, FIDS[0])
        self.assertFalse(got.ok)
        self.assertEqual(got.stage, "plan")

    def test_two_pages_one_name_two_operations(self):
        lib = oplang.Library()
        a = oplang.OpSpec("zol", ("A", "B"),
                          ((("all_same",), ("shared", 1)),), ("src", 2))
        b = oplang.OpSpec("zol", ("A", "B"),
                          ((("all_same",), ("shared", 1)),), ("src", 1))
        lib.add(a)
        lib.add(a)
        self.assertEqual(len(lib), 1)
        self.assertEqual(lib.n_pages, 2)
        with self.assertRaises(NormError):
            lib.add(b)

    def test_unknown_operation_is_refused(self):
        lib = oplang.Library()
        with self.assertRaises(NormError):
            lib.get("nosuchop")


class LibraryIsEpisodeScoped(unittest.TestCase):
    def test_an_operation_does_not_carry_over(self):
        """A second episode that does not define the operation must refuse."""
        space = oplang.distinct_space(1)
        inst = _instance(space[11], FIDS[0], 4242)
        first = opitems.episode(inst, FIDS[0], "single", inst["keys"][0])
        got = opread.read(first["text"], FIDS[0])
        self.assertTrue(got.ok)
        self.assertIn(inst["spec"].name, got.library.ops)
        pages = [opsay.directory_page(t, FIDS[0]) for t in inst["tables"]]
        q = opsay.question_single(inst["spec"], FIDS[0], inst["keys"][1])
        again = opread.read(opsay.episode_text(pages, [], q), FIDS[0])
        self.assertFalse(again.ok)
        self.assertEqual(again.stage, "plan")


class DepthIsAList(unittest.TestCase):
    def test_sixteen_rounds_run(self):
        closed = [s for s in oplang.distinct_space(1)
                  if all(r[0] != "word" for _, r in s[0])
                  and s[1][0] != "word"]
        done = 0
        for i, sk in enumerate(closed):
            inst = opitems.draw_instance(sk, FIDS[i % len(FIDS)], 700 + i,
                                         closed=True)
            if inst is None or oplang.is_degenerate(inst["spec"],
                                                    inst["tables"],
                                                    inst["keys"]):
                continue
            p = oplang.program_iterate(inst["spec"], inst["tables"],
                                       inst["keys"][0], 16)
            r = run(p)
            self.assertTrue(r.ok, r.reason)
            self.assertEqual(len(p.steps), 16 * (inst["spec"].arity + 1))
            done += 1
            if done >= 5:
                break
        self.assertGreaterEqual(done, 5)


class ItemSetsAreReproducible(unittest.TestCase):
    """The recorded item files must come back byte for byte from the code.

    The item sets are drawn once and then answered by runs that cost hours, so
    a change that quietly redraws them would leave a report built from two
    different item sets. This rebuilds them into a temporary directory and
    compares the uncompressed bytes.
    """

    def _same(self, module_args, recorded):
        import gzip as gz
        import hashlib
        import subprocess
        import tempfile
        if not os.path.exists(recorded):
            self.skipTest(f"{recorded} has not been built")
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, os.path.basename(recorded))
            r = subprocess.run([sys.executable, "-m"] + module_args
                               + ["--out", out], capture_output=True)
            self.assertEqual(r.returncode, 0, r.stderr[-400:])
            a = hashlib.md5(gz.open(out, "rb").read()).hexdigest()
        b = hashlib.md5(gz.open(recorded, "rb").read()).hexdigest()
        self.assertEqual(a, b, f"{recorded} is not what the code now draws")

    def test_items(self):
        self._same(["src.norm.opitems"],
                   "results/norm/oneshot/items.jsonl.gz")

    def test_ladder_items(self):
        self._same(["src.norm.opladder"],
                   "results/norm/oneshot/ladder_items.jsonl.gz")


class ExtendedTargetIsExact(unittest.TestCase):
    def test_round_trip_over_the_space(self):
        fr, _ = frames()
        iv = InputVocab(english_from_frames(fr))
        ov = optok.OpVocab()
        self.assertEqual(ov.itos[:ov.n_base],
                         tuple(ndata._vocab()[1].itos))
        space = oplang.distinct_space(1)
        rng = random.Random(5)
        n = 0
        for i in rng.sample(range(len(space)), 50):
            fid = FIDS[i % len(FIDS)]
            inst = _instance(space[i], fid, 1700 + i)
            if inst is None:
                continue
            for kind, kw in (("single", {}), ("iterate", {"n": 4})):
                e = opitems.episode(inst, fid, kind, inst["keys"][0], **kw)
                if e is None:
                    continue
                from src.norm.lang import program_load
                p = program_load(e["prog"])
                ids, slots, unk = iv.encode(e["text"])
                toks = optok.serialize(p, slots, [inst["spec"]])
                self.assertEqual(optok.deserialize(toks, slots), p)
                n += 1
        self.assertGreater(n, 20)


if __name__ == "__main__":
    unittest.main()
