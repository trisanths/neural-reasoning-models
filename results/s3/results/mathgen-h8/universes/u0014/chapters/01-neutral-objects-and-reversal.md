# Chapter 2. Neutral objects and reversal

## Why this chapter

So far the qenjens have been objects to be pushed around. This chapter starts asking
what they are like. We take up a neutral object for the first operation, an absorbing
object for the first operation and the system does not have reversal under the first
operation.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
qenjens that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A4. A neutral object for the first operation. There is a qenjen xilzam with xilzam + x =
x + xilzam = x for every x.

A5. An absorbing object for the first operation. There is a qenjen yuktarn with yuktarn
+ x = x + yuktarn = yuktarn for every x.

## The shape of it

The neutral qenjen xilzam is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 qenjens the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R1 rests on S2 (the Quilumb combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Here is (shentu + xilzam) + (cloreld + yuktarn), reduced without skipping anything.
    shentu + xilzam = shentu   (the table for +)
    cloreld + yuktarn = yuktarn   (the table for +)
    shentu + yuktarn = yuktarn   (the table for +)
That leaves yuktarn, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is xilzam + (cloreld + shentu) for contrast.
    cloreld + shentu = nyrazt   (the table for +)
    xilzam + nyrazt = nyrazt   (the table for +)
The value is nyrazt, not yuktarn.

One decision about the relation, since deciding is as much a skill as computing. Does
nyrazt <~ cloreld hold? Read off what nyrazt stands over: nyrazt and cloreld. cloreld is
among them, so it holds.

## A case that breaks

R1. Some qenjen x admits no qenjen y for which x + y and y + x both land on a neutral
object. It fails at x = yuktarn. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside S2 (the Quilumb combination tables).

What is built on it later: D5 (the mithra) and T1 (the mithra is the only one of its
kind).

## Proofs

R1. Some qenjen x admits no qenjen y for which x + y and y + x both land on a neutral object.

  (1) [S2] Take the case x = yuktarn, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R1. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 5.
  x007. The following fails in this system: Some qenjen x admits no qenjen y for which x + y and y + x both land on a neutral object. Name the earliest qenjen, in the order the qenjens were introduced, that witnesses the failure.
