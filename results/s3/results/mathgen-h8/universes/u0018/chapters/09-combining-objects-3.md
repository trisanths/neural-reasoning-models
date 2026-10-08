# Chapter 10. Combining objects (3)

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is where every naksol
is aztumb breaks down, the nakumb is hobreld and every naksol lies in the tezka.

Prerequisites are real here: chapters 1, 5, 6 and 7 supply the notions the statements
below are phrased in.

The standard of proof here is exhaustion. A universal claim about naksols covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

A useful mental split: some naksols are inert under the operation and some are not.
wrenpyr come back unchanged when combined with themselves, and wrenpyr, vexlorn, vexnak,
glimzam, reldxil and pyrxil commute with everything.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R6 rests on D7 (the nakumb). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T11 rests on D7 (the nakumb) and D3 (hobreld collections). Remove any one of them and
the statement stops making sense, not merely stops being provable.

T17 rests on D6 (the tezka). The dependence is on the content of those results, not only
on their vocabulary.

T2 rests on D5 (the muxisk) and D6 (the tezka). Remove any one of them and the statement
stops making sense, not merely stops being provable.

T5 rests on D6 (the tezka), D3 (hobreld collections) and A2 (association of the first
operation). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Here is (vexlorn % glimzam) % (vexnak % pyrxil), reduced without skipping anything.
    vexlorn % glimzam = reldxil   (the table for %)
    vexnak % pyrxil = vexlorn   (the table for %)
    reldxil % vexlorn = pyrxil   (the table for %)
So (vexlorn % glimzam) % (vexnak % pyrxil) is pyrxil.

Move the brackets and the work changes. Take glimzam % (vexnak % vexlorn).
    vexnak % vexlorn = glimzam   (the table for %)
    glimzam % glimzam = wrenpyr   (the table for %)
That gives wrenpyr, against pyrxil above.

One decision about the relation, since deciding is as much a skill as computing. Does
glimzam >- glimzam hold? Read off what glimzam stands over: glimzam, reldxil and pyrxil.
glimzam is among them, so it holds.

## A case that breaks

R6. It is not the case that: x % x = x for every naksol x. The case that settles it: x =
vexlorn, value = vexnak. Anyone carrying this claim over from a more familiar system
will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation and closure under the first operation. Those are
properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A2 (association of the first operation), D3 (hobreld collections), D5
(the muxisk) and D6 (the tezka).

What is built on it later: T10 (the thrapon of a tezka naksol stays in the tezka) and
T19 (the second operation keeps the tezka intact).

## Proofs

R6. It is not the case that: x % x = x for every naksol x.

  (1) [S2] Take the case x = vexlorn, value = vexnak, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T11. If x and y are both aztumb then so is x % y.

  (1) [D7] Let x and y be aztumb.
  (2) [D1] The claim asks whether (x % y) % (x % y) returns x % y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 36 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

T17. Every pair of naksols glimvashs.

  (1) [D6] The tezka is defined by glimvashing with everything.
  (2) [D2] The claim is that x % y = y % x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T2. The muxisk glimvashs with every naksol.

  (1) [D5] Let e be the muxisk and x any naksol.
  (2) [D5] Then e % x = x and x % e = x.
  (3) [D2] So e % x = x % e, which is what it means to glimvash.
  (4) [D6] Since x was arbitrary, e belongs to the tezka.

Checked over 6 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T5. If x and y both glimvash with every naksol, then so does x % y.

  (1) [D6] Let x and y lie in the tezka and let z be any naksol.
  (2) [A2] Then (x % y) % z = x % (y % z).
  (3) [D6] Move z past y, then past x, using that each glimvashs with everything.
  (4) [D3] So x % y glimvashs with z, and the tezka is hobreld.

Checked over 36 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

The results now available are T11, T17, T2 and T5, each settled by exhaustive check
rather than by argument from analogy.

Explicitly not available: R6. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x053. This result is about the nakumb. List every naksol in it.
