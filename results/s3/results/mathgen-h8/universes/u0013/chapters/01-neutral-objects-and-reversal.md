# Chapter 2. Neutral objects and reversal

## Why this chapter

The practical content of this chapter is a neutral object for the first operation, an
absorbing object for the first operation and the system does not have reversal under the
first operation. It is the part that shows up in use.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about xilzams covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A4. A neutral object for the first operation. There is a xilzam muxovi with muxovi & x =
x & muxovi = x for every x.

A5. An absorbing object for the first operation. There is a xilzam shennak with shennak
& x = x & shennak = shennak for every x.

## The shape of it

The neutral xilzam muxovi is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 xilzams the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R1 rests on S2 (the Opalopal combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take (ovimux & muxovi) & (nyrfex & shennak) and work it out one step at a time.
    ovimux & muxovi = ovimux   (the table for &)
    nyrfex & shennak = shennak   (the table for &)
    ovimux & shennak = shennak   (the table for &)
The expression comes to shennak.

A companion case, muxovi & (nyrfex & ovimux), to show what the brackets are doing.
    nyrfex & ovimux = shennak   (the table for &)
    muxovi & shennak = shennak   (the table for &)
That gives shennak, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
muxovi <| shennak hold? Read off what muxovi stands over: muxovi, nyrfex, ovimux and
shennak. shennak is among them, so it holds.

## A case that breaks

R1. Some xilzam x admits no xilzam y for which x & y and y & x both land on a neutral
object. The case that settles it: x = nyrfex. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside S2 (the Opalopal combination tables).

What is built on it later: D5 (the minak) and T1 (the minak is the only one of its
kind).

## Proofs

R1. Some xilzam x admits no xilzam y for which x & y and y & x both land on a neutral object.

  (1) [S2] Take the case x = nyrfex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R1. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 5.
  x010. The following fails in this system: Some xilzam x admits no xilzam y for which x & y and y & x both land on a neutral object. Name the earliest xilzam, in the order the xilzams were introduced, that witnesses the failure.
