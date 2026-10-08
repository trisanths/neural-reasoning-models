"""A wrong plan that passes rerender AND executes, and is caught only by identical."""
import random
from src.norm.gen import lexicon_for
from src.norm.render import render, classify, frames
from src.norm.interp import run
from src.norm.lang import Program, Step, Ref, Table
from src.norm.shapes import assemble
from src.norm.parse import parse

fid = "abstract.mapping.key_first.wh.scope_first"
rng = random.Random(11)
lex = lexicon_for(fid, rng)
n1, n2 = lex.name(), lex.name()
ks = lex.words(4)
v1 = lex.words(4)
v2 = lex.words(4)
# both tables total via a default, so every order of the chain executes
T1 = Table(n1, tuple(zip(ks, v1)), lex.word())
T2 = Table(n2, tuple(zip(ks, v2)), lex.word())
p = assemble("compose", tables=[T1, T2], inputs=(("x", ks[0]),))
# the wrong wiring: same defs, same defs order, hops swapped
q = Program(p.defs, p.inputs,
            (Step("t1", "lookup", (n2, Ref("x"))),
             Step("t2", "lookup", (n1, Ref("t1")))), "t2")
tp = render(p, fid, preamble_level=2)["text"]
tq = render(q, fid, preamble_level=2)["text"]
a, b = run(p), run(q)
print("classify p / q      :", classify(p), classify(q))
print("q == p              :", q == p, "   <- the `identical` check")
print("render(q) == render(p):", tq == tp, "  <- the `rerender` check")
print("run ok               :", a.ok, b.ok)
print("answers              :", a.value, "vs", b.value,
      "  same:", a.value == b.value, " <- the `executes` check")
print()
print("the question both render:", tp.strip().splitlines()[-1])
print()
got = parse(tp, fid)
print("the real parser recovers p:", got.ok and got.program == p)
