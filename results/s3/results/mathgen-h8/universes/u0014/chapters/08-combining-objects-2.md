# Chapter 9. Combining objects (2)

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is where every qenjen
is tufal breaks down, every qenjen lies in the zammorn and the mithra lies in the
zammorn.

Prerequisites are real here: chapters 1, 5, 6 and 7 supply the notions the statements
below are phrased in.

The standard of proof here is exhaustion. A universal claim about qenjens covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

A useful mental split: some qenjens are inert under the operation and some are not.
yuktarn and xilzam come back unchanged when combined with themselves, and yuktarn,
xilzam, shentu, nyrazt and cloreld commute with everything.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R8 rests on D7 (the vexfex). The dependence is on the content of those results, not only
on their vocabulary.

T13 rests on D6 (the zammorn). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T2 rests on D5 (the mithra) and D6 (the zammorn). Remove any one of them and the
statement stops making sense, not merely stops being provable.

T3 rests on D6 (the zammorn), D3 (rastdri collections) and A2 (association of the first
operation). The dependence is on the content of those results, not only on their
vocabulary.

T8 rests on D7 (the vexfex) and D3 (rastdri collections). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Here is xilzam + shentu |= yuktarn, reduced without skipping anything.
    shentu |= yuktarn = yuktarn   (the table for |=)
    xilzam + yuktarn = yuktarn   (the table for +)
So xilzam + shentu |= yuktarn is yuktarn.

A companion case, shentu + (yuktarn + xilzam), to show what the brackets are doing.
    yuktarn + xilzam = yuktarn   (the table for +)
    shentu + yuktarn = yuktarn   (the table for +)
The value is yuktarn. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
cloreld <~ cloreld hold? Read off what cloreld stands over: cloreld. cloreld is among
them, so it holds.

## A case that breaks

R8. It is not the case that: x + x = x for every qenjen x. The case that settles it: x =
shentu, value = cloreld. Anyone carrying this claim over from a more familiar system
will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by a neutral object for the first operation, association of the
first operation and closure under the first operation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A2 (association of the first operation), D3 (rastdri collections), D5
(the mithra) and D6 (the zammorn).

These results are used again in T7 (the kaduth of a zammorn qenjen stays in the zammorn)
and T14 (the second operation keeps the zammorn intact).

## Proofs

R8. It is not the case that: x + x = x for every qenjen x.

  (1) [S2] Take the case x = shentu, value = cloreld, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T13. Every pair of qenjens braumbs.

  (1) [D6] The zammorn is defined by braumbing with everything.
  (2) [D2] The claim is that x + y = y + x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T2. The mithra braumbs with every qenjen.

  (1) [D5] Let e be the mithra and x any qenjen.
  (2) [D5] Then e + x = x and x + e = x.
  (3) [D2] So e + x = x + e, which is what it means to braumb.
  (4) [D6] Since x was arbitrary, e belongs to the zammorn.

Checked over 5 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. If x and y both braumb with every qenjen, then so does x + y.

  (1) [D6] Let x and y lie in the zammorn and let z be any qenjen.
  (2) [A2] Then (x + y) + z = x + (y + z).
  (3) [D6] Move z past y, then past x, using that each braumbs with everything.
  (4) [D3] So x + y braumbs with z, and the zammorn is rastdri.

Checked over 25 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

T8. If x and y are both tufal then so is x + y.

  (1) [D7] Let x and y be tufal.
  (2) [D1] The claim asks whether (x + y) + (x + y) returns x + y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 25 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

The results now available are T13, T2, T3 and T8, each settled by exhaustive check
rather than by argument from analogy.

Do not carry forward R8. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x036. This result is about the vexfex. List every qenjen in it.
Level 5.
  x037. The following fails in this system: x + x = x for every qenjen x. Name the earliest qenjen, in the order the qenjens were introduced, that witnesses the failure.
