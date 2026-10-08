# Chapter 9. Combining objects (3)

## Why this chapter

So far the zelbras have been objects to be pushed around. This chapter starts asking
what they are like. We take up where every zelbra lies in the zelquil breaks down, where
every zelbra is pyrtez breaks down and the rastmorn is naknak.

Nothing here stands on its own. The arguments lean on chapters 5 and 7, and a reader who
has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over zelbras, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

Two questions sort the zelbras quickly. Does combining a zelbra with itself change it?
For tarnnyr it does not. Does it matter which side it goes on? It always does.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 zelbras the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R11 rests on D5 (the zelquil). The dependence is on the content of those results, not
only on their vocabulary.

R12 rests on D6 (the rastmorn). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T5 rests on D6 (the rastmorn) and D3 (naknak collections). Remove any one of them and
the statement stops making sense, not merely stops being provable.

## A worked case

Here is tarnnyr * cloxil - isktez, reduced without skipping anything.
    cloxil - isktez = isktez   (the table for -)
    tarnnyr * isktez = tarnnyr   (the table for *)
That leaves tarnnyr, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is cloxil * (isktez * tarnnyr) for contrast.
    isktez * tarnnyr = isktez   (the table for *)
    cloxil * isktez = tarnnyr   (the table for *)
The value is tarnnyr. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test iskmi <~ tarnnyr. The opalpyr of iskmi is iskmi, and tarnnyr lies outside it, so
the relation fails.

## A case that breaks

R11. It is not the case that: Every pair of zelbras vorazts. The case that settles it: x
= tarnnyr, y = cloxil, left = tarnnyr, right = cloxil. Anyone carrying this claim over
from a more familiar system will be wrong here, and wrong in a way that propagates.

R12. It is not the case that: x * x = x for every zelbra x. It fails at x = cloxil,
value = tarnnyr. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by closure under the first operation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside D3 (naknak collections), D5 (the zelquil) and D6 (the rastmorn).

## Proofs

R11. It is not the case that: Every pair of zelbras vorazts.

  (1) [S2] Take the case x = tarnnyr, y = cloxil, left = tarnnyr, right = cloxil, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 16 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

R12. It is not the case that: x * x = x for every zelbra x.

  (1) [S2] Take the case x = cloxil, value = tarnnyr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 4 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T5. If x and y are both pyrtez then so is x * y.

  (1) [D6] Let x and y be pyrtez.
  (2) [D1] The claim asks whether (x * y) * (x * y) returns x * y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 16 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

The results now available are T5, each settled by exhaustive check rather than by
argument from analogy.

Do not carry forward R11 and R12. These were tested and failed, and the failing cases
are recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x036. Name the zelbras that make up the rastmorn, which is what the result above is a claim about.
Level 5.
  x041. The following fails in this system: Every pair of zelbras vorazts. Name the earliest zelbra, in the order the zelbras were introduced, that witnesses the failure.
  x042. The following fails in this system: x * x = x for every zelbra x. Name the earliest zelbra, in the order the zelbras were introduced, that witnesses the failure.
