# Chapter 7. Neutral objects and reversal (2)

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is qennyr drigrixs,
the kapon and the tezjen.

Nothing here stands on its own. The arguments lean on chapters 2 and 5, and a reader who
has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over drigrixs, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D10. Qennyr drigrixs. A drigrix x is qennyr when x @ x equals the mornvint.

In this system that picks out solvex, which is 1 of the 5 drigrixs.

D6. The kapon. The kapon of the system is the collection of drigrixs that korrhob with
every drigrix.

In this system that picks out solvex, umbazt, glimmux, vashtez and qenvex, that is, all
of them.

D7. The tezjen. The tezjen is the collection of all opalrast drigrixs.

In this system that picks out solvex and qenvex, which is 2 of the 5 drigrixs.

## The shape of it

A useful mental split: some drigrixs are inert under the operation and some are not.
solvex and qenvex come back unchanged when combined with themselves, and solvex, umbazt,
glimmux, vashtez and qenvex commute with everything.

The neutral drigrix solvex is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R14 rests on D5 (the mornvint). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T1 rests on D5 (the mornvint) and A4 (a neutral object for the first operation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Take glimmux @ solvex + umbazt and work it out one step at a time.
    solvex + umbazt = solvex   (the table for +)
    glimmux @ solvex = glimmux   (the table for @)
So glimmux @ solvex + umbazt is glimmux.

Move the brackets and the work changes. Take solvex @ (umbazt @ glimmux).
    umbazt @ glimmux = vashtez   (the table for @)
    solvex @ vashtez = vashtez   (the table for @)
That gives vashtez, against glimmux above.

One decision about the relation, since deciding is as much a skill as computing. Does
qenvex :: qenvex hold? Read off what qenvex stands over: solvex, umbazt, glimmux,
vashtez and qenvex. qenvex is among them, so it holds.

## A case that breaks

R14. It is not the case that: e @ x equals the mornvint for every drigrix x. The case
that settles it: anchor = solvex, x = umbazt, value = umbazt. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of a neutral object for the first operation
and closure under the first operation. Those are properties of this system, not of
systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A4 (a neutral object for the first operation),
D1 (opalrast drigrixs), D2 (drigrixs that korrhob) and D5 (the mornvint).

These results are used again in T2 (the mornvint lies in the kapon), T3 (the kapon is
vexfex), T7 (the vintmux of a kapon drigrix stays in the kapon) and T8 (the tezjen is
vexfex).

## Proofs

R14. It is not the case that: e @ x equals the mornvint for every drigrix x.

  (1) [S2] Take the case anchor = solvex, x = umbazt, value = umbazt, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T1. There is exactly one drigrix e with e @ x = x @ e = x for every drigrix x.

  (1) [D5] Suppose e and f both leave every drigrix unchanged.
  (2) [A4] Then e @ f = f, reading e as neutral on the left.
  (3) [A4] And e @ f = e, reading f as neutral on the right.
  (4) So e = f, and the two suppositions describe the same object.

Checked over 25 cases: every object paired with every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: qennyr drigrixs, the kapon and the tezjen. Each of
these is used by name later, so the names are worth learning rather than looking up.

The results now available are T1, each settled by exhaustive check rather than by
argument from analogy.

Explicitly not available: R14. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x024. List every drigrix in the tezjen.
  x032. Which drigrixs make up the qennyr? Name them all.
Level 5.
  x049. The following fails in this system: e @ x equals the mornvint for every drigrix x. Name the earliest drigrix, in the order the drigrixs were introduced, that witnesses the failure.
