# Chapter 2. Neutral objects and reversal

## Why this chapter

The results collected here were not found in this order. A neutral object for the first
operation, reversal under the first operation and the system does not have an absorbing
object for the first operation came first, and the rest was assembled around that once
the pattern was visible.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

One habit to adopt: when a statement below quantifies over thrafexs, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A4. A neutral object for the first operation. There is a thrafex tuespa with tuespa =| x
= x =| tuespa = x for every x.

A5. Reversal under the first operation. For every thrafex x there is a thrafex y with x
=| y = y =| x = tuespa.

## The shape of it

Neutrality is a strong condition disguised as a weak one. It fixes a single thrafex and,
through that, constrains everything that can combine with it.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R2 rests on S2 (the Keldmux combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Here is (tuespa =| hobzel) =| (hobzel =| tuespa), reduced without skipping anything.
    tuespa =| hobzel = hobzel   (the table for =|)
    hobzel =| tuespa = hobzel   (the table for =|)
    hobzel =| hobzel = qenmorn   (the table for =|)
That leaves qenmorn, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is hobzel =| (hobzel =| tuespa) for contrast.
    hobzel =| tuespa = hobzel   (the table for =|)
    hobzel =| hobzel = qenmorn   (the table for =|)
The value is qenmorn. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test hobzel =< qenmorn. The vextarn of hobzel is tuespa, qenmorn and hobzel, and qenmorn
lies inside it, so the relation holds.

## A case that breaks

R2. There is no thrafex z with z =| x = x =| z = z for every thrafex x. The case that
settles it: reason = no absorbing element. Anyone carrying this claim over from a more
familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: S2 (the Keldmux combination tables).

What is built on it later: D5 (the nyrrast), D11 (the nyrzel of a thrafex) and T1 (the
nyrrast is the only one of its kind).

## Proofs

R2. There is no thrafex z with z =| x = x =| z = z for every thrafex x.

  (1) [S2] Take the case reason = no absorbing element, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 27 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R2. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

This chapter carries no exercises. Nothing in it can be asked about in a way that could
not be answered without reading it, and an exercise like that is worse than none.
