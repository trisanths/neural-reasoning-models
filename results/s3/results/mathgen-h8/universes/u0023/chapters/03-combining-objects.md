# Chapter 4. Combining objects

## Why this chapter

We turn to shenfal vintzams, vintzams that tuwren and reldjen collections. The treatment
is self contained given the material already established.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
vintzams that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D1. Shenfal vintzams. A vintzam x is called shenfal when x : x = x.

Running the definition over every vintzam leaves hurnvash.

D2. Vintzams that tuwren. Two vintzams x and y are said to tuwren when x : y = y : x.

D3. Reldjen collections. A collection S of vintzams is reldjen when x : y belongs to S
for every pair x, y drawn from S.

## The shape of it

Picture the zamsol as what happens when you start with one vintzam and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 6 vintzams, that stops. In this system the sizes it stops at are 1 and 2.

Two questions sort the vintzams quickly. Does combining a vintzam with itself change it?
For hurnvash it does not. Does it matter which side it goes on? It always does.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Nothing is derived in this chapter. It lays down material that later chapters draw on.

## A worked case

Evaluate (pyryuk : hurnvash) : (ovijen : drishen). Each line below is one lookup in a
table.
    pyryuk : hurnvash = pyryuk   (the table for :)
    ovijen : drishen = pyryuk   (the table for :)
    pyryuk : pyryuk = hurnvash   (the table for :)
So (pyryuk : hurnvash) : (ovijen : drishen) is hurnvash.

A companion case, hurnvash : (ovijen : pyryuk), to show what the brackets are doing.
    ovijen : pyryuk = drishen   (the table for :)
    hurnvash : drishen = hurnvash   (the table for :)
The value is hurnvash. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
duthsib :: duthsib hold? Read off what duthsib stands over: hurnvash. duthsib is not
among them, so it fails.

## A case that breaks

A quick guard against a common slip: pyryuk : ovijen is hurnvash while ovijen : pyryuk
is drishen. Order is not decoration in this system.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by closure under the first operation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A1 (closure under the first operation).

These results are used again in D5 (the falwren), D6 (the vextarn), D7 (the zamsol of a
vintzam) and T1 (the zamsol of a vintzam is reldjen).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

Carry forward shenfal vintzams, vintzams that tuwren and reldjen collections. Later
chapters state their results in these terms and do not restate the definitions.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x023. List every vintzam in the shenfal.
  x024. How many vintzams lie in the smallest reldjen collection containing duthsib?
  x025. How many vintzams lie in the smallest reldjen collection containing drishen?
