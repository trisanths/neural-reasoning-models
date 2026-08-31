"""The positive control on `order_only`.

`src/norm/ndiff.py` reports that no emission is ever a mere reordering of the
gold structure. That claim is only worth anything if the comparator can see a
reordering when there is one, so these tests build reorderings by hand and
require the bucket to fire. The last two require it not to fire when the order
carries meaning or when a value has changed.
"""

import unittest

from src.norm.ndiff import bucket
from src.norm.lang import Program, Ref, Step, Table, Weights


def _prog(entries, ordered=False, defs=None):
    t = Table(name="Tab", entries=entries, ordered=ordered)
    return Program(defs=tuple(defs or (t,)), inputs=(("x", "aa"),),
                   steps=(Step(out="t1", op="lookup",
                               args=("Tab", Ref(name="x"))),),
                   answer="t1")


class TestOrderOnly(unittest.TestCase):

    def test_permuted_table_rows_are_order_only(self):
        a = _prog((("aa", "p"), ("bb", "q"), ("cc", "r")))
        b = _prog((("cc", "r"), ("aa", "p"), ("bb", "q")))
        self.assertNotEqual(a, b)
        self.assertEqual(bucket(b, a), "order_only")

    def test_permuted_weights_rows_are_order_only(self):
        w1 = Weights(name="Wt", entries=(("aa", 1), ("bb", 2)))
        w2 = Weights(name="Wt", entries=(("bb", 2), ("aa", 1)))
        t = Table(name="Tab", entries=(("aa", "p"),))
        a = _prog((("aa", "p"),), defs=(t, w1))
        b = _prog((("aa", "p"),), defs=(t, w2))
        self.assertNotEqual(a, b)
        self.assertEqual(bucket(b, a), "order_only")

    def test_permuted_definitions_are_order_only(self):
        t = Table(name="Tab", entries=(("aa", "p"),))
        w = Weights(name="Wt", entries=(("aa", 1),))
        a = _prog((("aa", "p"),), defs=(t, w))
        b = _prog((("aa", "p"),), defs=(w, t))
        self.assertNotEqual(a, b)
        self.assertEqual(bucket(b, a), "order_only")

    def test_ordered_table_keeps_its_order(self):
        a = _prog((("aa", "p"), ("bb", "q")), ordered=True)
        b = _prog((("bb", "q"), ("aa", "p")), ordered=True)
        self.assertNotEqual(bucket(b, a), "order_only")

    def test_changed_value_is_not_order_only(self):
        a = _prog((("aa", "p"), ("bb", "q")))
        b = _prog((("aa", "p"), ("bb", "r")))
        self.assertNotIn(bucket(b, a), ("order_only", "exact"))

    def test_identical_is_exact(self):
        a = _prog((("aa", "p"), ("bb", "q")))
        self.assertEqual(bucket(a, a), "exact")


if __name__ == "__main__":
    unittest.main()
