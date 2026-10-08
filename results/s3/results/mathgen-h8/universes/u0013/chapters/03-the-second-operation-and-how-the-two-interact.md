# Chapter 4. The second operation and how the two interact

## Why this chapter

The present chapter develops closure under the second operation, association of the
second operation and self combination under the second operation.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

The standard of proof here is exhaustion. A universal claim about xilzams covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A6. Closure under the second operation. For all xilzams x and y, x $ y is again a
xilzam.

A7. Association of the second operation. For all xilzams x, y, z: (x $ y) $ z = x $ (y $
z).

A8. Self combination under the second operation. For every xilzam x: x $ x = x.

## The shape of it

The interesting content of a two operation system sits in the gap between them: which
one distributes over which, and which xilzams are fixed by both.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R4 rests on S2 (the Opalopal combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R5 rests on S2 (the Opalopal combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R6 rests on S2 (the Opalopal combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R7 rests on S2 (the Opalopal combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Here is (muxovi & shennak) & (nyrfex & ovimux), reduced without skipping anything.
    muxovi & shennak = shennak   (the table for &)
    nyrfex & ovimux = shennak   (the table for &)
    shennak & shennak = shennak   (the table for &)
So (muxovi & shennak) & (nyrfex & ovimux) is shennak.

Bracketing is not cosmetic, so here is shennak & (nyrfex & muxovi) for contrast.
    nyrfex & muxovi = nyrfex   (the table for &)
    shennak & nyrfex = shennak   (the table for &)
The value is shennak. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test shennak <| nyrfex. The mivint of shennak is shennak, and nyrfex lies outside it, so
the relation fails.

## A case that breaks

R4. It is not the case that: For all xilzams x and y: x $ y = y $ x. It fails at x =
muxovi, y = nyrfex, left = nyrfex, right = muxovi. One case is enough, and this is the
earliest one.

R5. There is no xilzam that leaves every xilzam unchanged under the second operation.
The case that settles it: reason = no two sided identity exists. Anyone carrying this
claim over from a more familiar system will be wrong here, and wrong in a way that
propagates.

R6. It is not the case that: For all xilzams x, y, z: x $ (y & z) = (x $ y) & (x $ z),
and the same on the right. The case that settles it: x = nyrfex, y = muxovi, z = muxovi,
left = nyrfex, right = ovimux. Anyone carrying this claim over from a more familiar
system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: S2 (the Opalopal combination tables).

These results are used again in T15 (the second operation keeps the sibnak intact).

## Proofs

R4. It is not the case that: For all xilzams x and y: x $ y = y $ x.

  (1) [S2] Take the case x = muxovi, y = nyrfex, left = nyrfex, right = muxovi, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R5. There is no xilzam that leaves every xilzam unchanged under the second operation.

  (1) [S2] Take the case reason = no two sided identity exists, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R6. It is not the case that: For all xilzams x, y, z: x $ (y & z) = (x $ y) & (x $ z), and the same on the right.

  (1) [S2] Take the case x = nyrfex, y = muxovi, z = muxovi, left = nyrfex, right = ovimux, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R7. It is not the case that: For all xilzams x and y: x & (x $ y) = x and x $ (x & y) = x.

  (1) [S2] Take the case x = muxovi, y = nyrfex, value = nyrfex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R4, R5, R6 and R7. A later argument that quietly assumes one
of these is wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 5.
  x013. The following fails in this system: For all xilzams x and y: x $ y = y $ x. Name the earliest xilzam, in the order the xilzams were introduced, that witnesses the failure.
  x014. The following fails in this system: For all xilzams x and y: x & (x $ y) = x and x $ (x & y) = x. Name the earliest xilzam, in the order the xilzams were introduced, that witnesses the failure.
