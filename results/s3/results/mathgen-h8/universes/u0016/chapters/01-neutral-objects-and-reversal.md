# Chapter 2. Neutral objects and reversal

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is a neutral object
for the first operation, an absorbing object for the first operation and the system does
not have reversal under the first operation.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about mornglims covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A4. A neutral object for the first operation. There is a mornglim oviazt with oviazt | x
= x | oviazt = x for every x.

A6. An absorbing object for the first operation. There is a mornglim xilwren with
xilwren | x = x | xilwren = xilwren for every x.

## The shape of it

The neutral mornglim oviazt is the one that does nothing. That sounds trivial and is
not: almost every result in this chapter is an argument about what doing nothing forces.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 mornglims the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R1 rests on S2 (the Glimzam combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Evaluate (nyrrast | oviazt) | (kapon | xilwren). Each line below is one lookup in a
table.
    nyrrast | oviazt = nyrrast   (the table for |)
    kapon | xilwren = xilwren   (the table for |)
    nyrrast | xilwren = xilwren   (the table for |)
So (nyrrast | oviazt) | (kapon | xilwren) is xilwren.

Move the brackets and the work changes. Take oviazt | (kapon | nyrrast).
    kapon | nyrrast = xilwren   (the table for |)
    oviazt | xilwren = xilwren   (the table for |)
That gives xilwren, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
xilwren <~ oviazt hold? Read off what xilwren stands over: xilwren. oviazt is not among
them, so it fails.

## A case that breaks

R1. Some mornglim x admits no mornglim y for which x | y and y | x both land on a
neutral object. It fails at x = kapon. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: S2 (the Glimzam combination tables).

What is built on it later: D5 (the vexbra) and T1 (the vexbra is the only one of its
kind).

## Proofs

R1. Some mornglim x admits no mornglim y for which x | y and y | x both land on a neutral object.

  (1) [S2] Take the case x = kapon, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R1. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 5.
  x007. The following fails in this system: Some mornglim x admits no mornglim y for which x | y and y | x both land on a neutral object. Name the earliest mornglim, in the order the mornglims were introduced, that witnesses the failure.
