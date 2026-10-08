# Chapter 2. Neutral objects and reversal

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through a neutral object for the first
operation, reversal under the first operation and the system does not have an absorbing
object for the first operation.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
wrenclos that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A4. A neutral object for the first operation. There is a wrenclo glimfex with glimfex #
x = x # glimfex = x for every x.

A5. Reversal under the first operation. For every wrenclo x there is a wrenclo y with x
# y = y # x = glimfex.

## The shape of it

The neutral wrenclo glimfex is the one that does nothing. That sounds trivial and is
not: almost every result in this chapter is an argument about what doing nothing forces.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R2 rests on S2 (the Qenshen combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Here is (bratu # vorkeld) # (glimfex # falzam), reduced without skipping anything.
    bratu # vorkeld = falzam   (the table for #)
    glimfex # falzam = falzam   (the table for #)
    falzam # falzam = glimfex   (the table for #)
The expression comes to glimfex.

Move the brackets and the work changes. Take vorkeld # (glimfex # bratu).
    glimfex # bratu = bratu   (the table for #)
    vorkeld # bratu = falzam   (the table for #)
The value is falzam, not glimfex.

Test glimfex <~ vorkeld. The reldxil of glimfex is glimfex, bratu, vorkeld and falzam,
and vorkeld lies inside it, so the relation holds.

## A case that breaks

R2. There is no wrenclo z with z # x = x # z = z for every wrenclo x. The case that
settles it: reason = no absorbing element. Anyone carrying this claim over from a more
familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: S2 (the Qenshen combination tables).

These results are used again in D5 (the ponjen), D11 (the thramorn of a wrenclo) and T1
(the ponjen is the only one of its kind).

## Proofs

R2. There is no wrenclo z with z # x = x # z = z for every wrenclo x.

  (1) [S2] Take the case reason = no absorbing element, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R2. These were tested and failed, and the failing cases are
recorded above.

## Exercises

This chapter carries no exercises. Nothing in it can be asked about in a way that could
not be answered without reading it, and an exercise like that is worse than none.
