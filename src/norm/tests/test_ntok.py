"""The gate on the target serialisation: it must be exact both ways."""

import random
import unittest

from src.norm import gen
from src.norm.lang import NormError
from src.norm.ndata import build_example, split_frames
from src.norm.ntok import (InputVocab, OutVocab, deserialize,
                           english_from_frames, serialize, text_tokens)
from src.norm.render import SHAPES, frames, render


class SerialiseRoundTrip(unittest.TestCase):
    def test_every_shape_every_frame_group(self):
        fr, _ = frames()
        iv = InputVocab(english_from_frames(fr))
        ov = OutVocab()
        groups = split_frames()
        rng = random.Random(11)
        n = bad = 0
        for group, fids in groups.items():
            for shape in SHAPES:
                for _ in range(3):
                    fid = rng.choice(fids)
                    e = build_example(fid, shape, rng.randrange(1 << 40),
                                      rng.randrange(0, 9))
                    if e is None:
                        bad += 1
                        continue
                    toks = ov.decode(e["out"][1:-1])
                    back = deserialize(toks, e["slots"])
                    self.assertEqual(back, e["prog"],
                                     f"{group} {shape} {fid}")
                    n += 1
        self.assertGreater(n, 200)
        self.assertLess(bad, n * 0.05)

    def test_nonce_and_english_are_disjoint(self):
        fr, _ = frames()
        iv = InputVocab(english_from_frames(fr))
        rng = random.Random(3)
        for _ in range(30):
            f = fr[rng.randrange(len(fr))]
            lex = gen.lexicon_for(f.fid, rng)
            p = gen.make(rng.choice(SHAPES), rng, lex)
            r = render(p, f.fid, rng.randrange(0, 9))
            ids, slots, n_unk = iv.encode(r["text"])
            self.assertEqual(n_unk, 0, f"unknown English in {f.fid}")
            low = {s.lower() for s in slots}
            self.assertEqual(low & iv.english, set())

    def test_a_broken_target_is_refused_not_guessed(self):
        ov = OutVocab()
        for toks in (["table", "W0", "a1", ";"],
                     ["table", "W99", "a1", ";", "|", "|", "|", "t1"],
                     ["bands", "W0", "W1", "cuts", "labels", "W2"],
                     ["|", "|", "t1", "@lookup", "W0", "x", ";", "|"],
                     []):
            with self.assertRaises(NormError):
                deserialize(toks, ["Aa", "bb", "cc"])


if __name__ == "__main__":
    unittest.main()
