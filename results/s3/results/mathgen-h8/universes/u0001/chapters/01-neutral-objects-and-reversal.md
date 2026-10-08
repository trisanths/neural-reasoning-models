# Chapter 2. Neutral objects and reversal

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is a neutral object
for the first operation, an absorbing object for the first operation and the system does
not have reversal under the first operation.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

The standard of proof here is exhaustion. A universal claim about drigrixs covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A4. A neutral object for the first operation. There is a drigrix solvex with solvex @ x
= x @ solvex = x for every x.

A5. An absorbing object for the first operation. There is a drigrix qenvex with qenvex @
x = x @ qenvex = qenvex for every x.

## The shape of it

Neutrality is a strong condition disguised as a weak one. It fixes a single drigrix and,
through that, constrains everything that can combine with it.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 drigrixs the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R1 rests on S2 (the Umbtu combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

## A worked case

Here is (qenvex @ vashtez) @ (umbazt @ glimmux), reduced without skipping anything.
    qenvex @ vashtez = qenvex   (the table for @)
    umbazt @ glimmux = vashtez   (the table for @)
    qenvex @ vashtez = qenvex   (the table for @)
So (qenvex @ vashtez) @ (umbazt @ glimmux) is qenvex.

Move the brackets and the work changes. Take vashtez @ (umbazt @ qenvex).
    umbazt @ qenvex = qenvex   (the table for @)
    vashtez @ qenvex = qenvex   (the table for @)
The value is qenvex. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test vashtez :: vashtez. The aztdri of vashtez is solvex, and vashtez lies outside it,
so the relation fails.

## A case that breaks

R1. Some drigrix x admits no drigrix y for which x @ y and y @ x both land on a neutral
object. The case that settles it: x = umbazt. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: S2 (the Umbtu combination tables).

These results are used again in D5 (the mornvint) and T1 (the mornvint is the only one
of its kind).

## Proofs

R1. Some drigrix x admits no drigrix y for which x @ y and y @ x both land on a neutral object.

  (1) [S2] Take the case x = umbazt, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R1. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 5.
  x010. The following fails in this system: Some drigrix x admits no drigrix y for which x @ y and y @ x both land on a neutral object. Name the earliest drigrix, in the order the drigrixs were introduced, that witnesses the failure.
