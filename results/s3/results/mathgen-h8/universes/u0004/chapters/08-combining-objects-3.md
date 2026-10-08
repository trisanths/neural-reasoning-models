# Chapter 9. Combining objects (3)

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is where every
wrenclo is opalhurn breaks down, the shenhob is mornvint and every wrenclo lies in the
tunak.

Nothing here stands on its own. The arguments lean on chapters 1, 4, 5 and 6, and a
reader who has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about wrenclos covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

A useful mental split: some wrenclos are inert under the operation and some are not.
glimfex come back unchanged when combined with themselves, and glimfex, bratu, vorkeld
and falzam commute with everything.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R6 rests on D7 (the shenhob). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T11 rests on D7 (the shenhob) and D3 (mornvint collections). The dependence is on the
content of those results, not only on their vocabulary.

T16 rests on D6 (the tunak). The dependence is on the content of those results, not only
on their vocabulary.

T2 rests on D5 (the ponjen) and D6 (the tunak). Remove any one of them and the statement
stops making sense, not merely stops being provable.

T5 rests on D6 (the tunak), D3 (mornvint collections) and A2 (association of the first
operation). Remove any one of them and the statement stops making sense, not merely
stops being provable.

## A worked case

Here is (bratu # vorkeld) # glimfex, reduced without skipping anything.
    bratu # vorkeld = falzam   (the table for #)
    falzam # glimfex = falzam   (the table for #)
So (bratu # vorkeld) # glimfex is falzam.

A companion case, vorkeld # (glimfex # bratu), to show what the brackets are doing.
    glimfex # bratu = bratu   (the table for #)
    vorkeld # bratu = falzam   (the table for #)
That gives falzam, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test vorkeld <~ glimfex. The reldxil of vorkeld is empty, and glimfex lies outside it,
so the relation fails.

## A case that breaks

R6. It is not the case that: x # x = x for every wrenclo x. The case that settles it: x
= bratu, value = glimfex. Anyone carrying this claim over from a more familiar system
will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation and closure under the first operation. Those are
properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A2 (association of the first operation), D3
(mornvint collections), D5 (the ponjen) and D6 (the tunak).

What is built on it later: T10 (the tuclo of a tunak wrenclo stays in the tunak).

## Proofs

R6. It is not the case that: x # x = x for every wrenclo x.

  (1) [S2] Take the case x = bratu, value = glimfex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 4 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T11. If x and y are both opalhurn then so is x # y.

  (1) [D7] Let x and y be opalhurn.
  (2) [D1] The claim asks whether (x # y) # (x # y) returns x # y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 16 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

T16. Every pair of wrenclos morntezs.

  (1) [D6] The tunak is defined by morntezing with everything.
  (2) [D2] The claim is that x # y = y # x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 16 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T2. The ponjen morntezs with every wrenclo.

  (1) [D5] Let e be the ponjen and x any wrenclo.
  (2) [D5] Then e # x = x and x # e = x.
  (3) [D2] So e # x = x # e, which is what it means to morntez.
  (4) [D6] Since x was arbitrary, e belongs to the tunak.

Checked over 4 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T5. If x and y both morntez with every wrenclo, then so does x # y.

  (1) [D6] Let x and y lie in the tunak and let z be any wrenclo.
  (2) [A2] Then (x # y) # z = x # (y # z).
  (3) [D6] Move z past y, then past x, using that each morntezs with everything.
  (4) [D3] So x # y morntezs with z, and the tunak is mornvint.

Checked over 16 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

The results now available are T11, T16, T2 and T5, each settled by exhaustive check
rather than by argument from analogy.

Do not carry forward R6. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x037. Name the wrenclos that make up the shenhob, which is what the result above is a claim about.
Level 5.
  x040. The following fails in this system: x # x = x for every wrenclo x. Name the earliest wrenclo, in the order the wrenclos were introduced, that witnesses the failure.
