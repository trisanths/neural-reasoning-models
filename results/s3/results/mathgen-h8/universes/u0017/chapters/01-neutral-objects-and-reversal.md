# Chapter 2. Neutral objects and reversal

## Why this chapter

What follows was pieced together backwards. The last item of it, a neutral object for
the first operation, an absorbing object for the first operation and the system does not
have reversal under the first operation, was noticed before anyone had a reason to
expect it.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over duthpons, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A4. A neutral object for the first operation. There is a duthpon rastrast with rastrast
- x = x - rastrast = x for every x.

A5. An absorbing object for the first operation. There is a duthpon nakvint with nakvint
- x = x - nakvint = nakvint for every x.

## The shape of it

The neutral duthpon rastrast is the one that does nothing. That sounds trivial and is
not: almost every result in this chapter is an argument about what doing nothing forces.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 duthpons the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R1 rests on S2 (the Clomorn combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take (nakvint - vorwren) - (vashtarn - yuksol) and work it out one step at a time.
    nakvint - vorwren = nakvint   (the table for -)
    vashtarn - yuksol = yuksol   (the table for -)
    nakvint - yuksol = nakvint   (the table for -)
That leaves nakvint, and no other reading of the notation gives anything else.

A companion case, vorwren - (vashtarn - nakvint), to show what the brackets are doing.
    vashtarn - nakvint = nakvint   (the table for -)
    vorwren - nakvint = nakvint   (the table for -)
That gives nakvint, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test nakvint >> nakvint. The wrensib of nakvint is nakvint, and nakvint lies inside it,
so the relation holds.

## A case that breaks

R1. Some duthpon x admits no duthpon y for which x - y and y - x both land on a neutral
object. The case that settles it: x = nakvint. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: S2 (the Clomorn combination tables).

What is built on it later: D5 (the zelthra) and T1 (the zelthra is the only one of its
kind).

## Proofs

R1. Some duthpon x admits no duthpon y for which x - y and y - x both land on a neutral object.

  (1) [S2] Take the case x = nakvint, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R1. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 5.
  x010. The following fails in this system: Some duthpon x admits no duthpon y for which x - y and y - x both land on a neutral object. Name the earliest duthpon, in the order the duthpons were introduced, that witnesses the failure.
