# Chapter 9. Combining objects (2)

## Why this chapter

Anyone using this system to keep track of something will meet where every drigrix is
opalrast breaks down, every drigrix lies in the kapon and the mornvint lies in the kapon
early, whether or not they go looking.

Prerequisites are real here: chapters 1, 5, 6 and 7 supply the notions the statements
below are phrased in.

One habit to adopt: when a statement below quantifies over drigrixs, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

Two questions sort the drigrixs quickly. Does combining a drigrix with itself change it?
For solvex and qenvex it does not. Does it matter which side it goes on? For solvex,
umbazt, glimmux, vashtez and qenvex it does not.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 drigrixs the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R11 rests on D7 (the tezjen). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T12 rests on D6 (the kapon). The dependence is on the content of those results, not only
on their vocabulary.

T2 rests on D5 (the mornvint) and D6 (the kapon). Remove any one of them and the
statement stops making sense, not merely stops being provable.

T3 rests on D6 (the kapon), D3 (vexfex collections) and A2 (association of the first
operation). Remove any one of them and the statement stops making sense, not merely
stops being provable.

T8 rests on D7 (the tezjen) and D3 (vexfex collections). The dependence is on the
content of those results, not only on their vocabulary.

## A worked case

Here is umbazt @ qenvex + solvex, reduced without skipping anything.
    qenvex + solvex = solvex   (the table for +)
    umbazt @ solvex = umbazt   (the table for @)
So umbazt @ qenvex + solvex is umbazt.

Bracketing is not cosmetic, so here is qenvex @ (solvex @ umbazt) for contrast.
    solvex @ umbazt = umbazt   (the table for @)
    qenvex @ umbazt = qenvex   (the table for @)
The value is qenvex, not umbazt.

Test glimmux :: vashtez. The aztdri of glimmux is solvex, and vashtez lies outside it,
so the relation fails.

## A case that breaks

R11. It is not the case that: x @ x = x for every drigrix x. The case that settles it: x
= umbazt, value = glimmux. Anyone carrying this claim over from a more familiar system
will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by a neutral object for the first operation, association of the
first operation and closure under the first operation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A2 (association of the first operation), D3
(vexfex collections), D5 (the mornvint) and D6 (the kapon).

These results are used again in T7 (the vintmux of a kapon drigrix stays in the kapon)
and T13 (the second operation keeps the kapon intact).

## Proofs

R11. It is not the case that: x @ x = x for every drigrix x.

  (1) [S2] Take the case x = umbazt, value = glimmux, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T12. Every pair of drigrixs korrhobs.

  (1) [D6] The kapon is defined by korrhobing with everything.
  (2) [D2] The claim is that x @ y = y @ x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T2. The mornvint korrhobs with every drigrix.

  (1) [D5] Let e be the mornvint and x any drigrix.
  (2) [D5] Then e @ x = x and x @ e = x.
  (3) [D2] So e @ x = x @ e, which is what it means to korrhob.
  (4) [D6] Since x was arbitrary, e belongs to the kapon.

Checked over 5 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. If x and y both korrhob with every drigrix, then so does x @ y.

  (1) [D6] Let x and y lie in the kapon and let z be any drigrix.
  (2) [A2] Then (x @ y) @ z = x @ (y @ z).
  (3) [D6] Move z past y, then past x, using that each korrhobs with everything.
  (4) [D3] So x @ y korrhobs with z, and the kapon is vexfex.

Checked over 25 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

T8. If x and y are both opalrast then so is x @ y.

  (1) [D7] Let x and y be opalrast.
  (2) [D1] The claim asks whether (x @ y) @ (x @ y) returns x @ y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 25 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Established here and safe to use: T12, T2, T3 and T8.

Explicitly not available: R11. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x043. Name the drigrixs that make up the tezjen, which is what the result above is a claim about.
Level 5.
  x047. The following fails in this system: x @ x = x for every drigrix x. Name the earliest drigrix, in the order the drigrixs were introduced, that witnesses the failure.
