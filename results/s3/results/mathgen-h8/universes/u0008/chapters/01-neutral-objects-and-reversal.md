# Chapter 2. Neutral objects and reversal

## Why this chapter

Anyone using this system to keep track of something will meet a neutral object for the
first operation, reversal under the first operation and the system does not have an
absorbing object for the first operation early, whether or not they go looking.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
ovimorns that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A4. A neutral object for the first operation. There is a ovimorn rastmi with rastmi : x
= x : rastmi = x for every x.

A5. Reversal under the first operation. For every ovimorn x there is a ovimorn y with x
: y = y : x = rastmi.

## The shape of it

The neutral ovimorn rastmi is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R2 rests on S2 (the Vashdri combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Evaluate (wrenkorr : bradri) : (muxvor : rastmi). Each line below is one lookup in a
table.
    wrenkorr : bradri = tezkeld   (the table for :)
    muxvor : rastmi = muxvor   (the table for :)
    tezkeld : muxvor = wrenkorr   (the table for :)
So (wrenkorr : bradri) : (muxvor : rastmi) is wrenkorr.

Move the brackets and the work changes. Take bradri : (muxvor : wrenkorr).
    muxvor : wrenkorr = bradri   (the table for :)
    bradri : bradri = wrenkorr   (the table for :)
That gives wrenkorr, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
tezkeld :: bradri hold? Read off what tezkeld stands over: rastmi, bradri, wrenkorr,
tezkeld and muxvor. bradri is among them, so it holds.

## A case that breaks

R2. There is no ovimorn z with z : x = x : z = z for every ovimorn x. The case that
settles it: reason = no absorbing element. Anyone carrying this claim over from a more
familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: S2 (the Vashdri combination tables).

These results are used again in D5 (the wrenglim), D11 (the oviovi of a ovimorn) and T1
(the wrenglim is the only one of its kind).

## Proofs

R2. There is no ovimorn z with z : x = x : z = z for every ovimorn x.

  (1) [S2] Take the case reason = no absorbing element, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R2. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

This chapter carries no exercises. Nothing in it can be asked about in a way that could
not be answered without reading it, and an exercise like that is worse than none.
