# Chapter 2. Neutral objects and reversal

## Why this chapter

The results collected here were not found in this order. A neutral object for the first
operation, an absorbing object for the first operation and the system does not have
reversal under the first operation came first, and the rest was assembled around that
once the pattern was visible.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
driwrens that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A4. A neutral object for the first operation. There is a driwren nakquil with nakquil *
x = x * nakquil = x for every x.

A6. An absorbing object for the first operation. There is a driwren thraisk with thraisk
* x = x * thraisk = thraisk for every x.

## The shape of it

Neutrality is a strong condition disguised as a weak one. It fixes a single driwren and,
through that, constrains everything that can combine with it.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 driwrens the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R1 rests on S2 (the Vorjen combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Take (soltarn * yukzel) * (nakquil * thraisk) and work it out one step at a time.
    soltarn * yukzel = yukzel   (the table for *)
    nakquil * thraisk = thraisk   (the table for *)
    yukzel * thraisk = thraisk   (the table for *)
So (soltarn * yukzel) * (nakquil * thraisk) is thraisk.

A companion case, yukzel * (nakquil * soltarn), to show what the brackets are doing.
    nakquil * soltarn = soltarn   (the table for *)
    yukzel * soltarn = yukzel   (the table for *)
The value is yukzel, not thraisk.

Test muxsib << nakquil. The zelfex of muxsib is nakquil and muxsib, and nakquil lies
inside it, so the relation holds.

## A case that breaks

R1. Some driwren x admits no driwren y for which x * y and y * x both land on a neutral
object. It fails at x = soltarn. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: S2 (the Vorjen combination tables).

These results are used again in D5 (the keldtu) and T1 (the keldtu is the only one of
its kind).

## Proofs

R1. Some driwren x admits no driwren y for which x * y and y * x both land on a neutral object.

  (1) [S2] Take the case x = soltarn, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R1. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 5.
  x007. The following fails in this system: Some driwren x admits no driwren y for which x * y and y * x both land on a neutral object. Name the earliest driwren, in the order the driwrens were introduced, that witnesses the failure.
