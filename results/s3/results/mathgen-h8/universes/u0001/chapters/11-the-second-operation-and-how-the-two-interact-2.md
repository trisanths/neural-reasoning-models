# Chapter 12. The second operation and how the two interact (2)

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is the second
operation keeps the kapon intact.

Prerequisites are real here: chapters 4, 7 and 9 supply the notions the statements below
are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
drigrixs that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

The interesting content of a two operation system sits in the gap between them: which
one distributes over which, and which drigrixs are fixed by both.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 drigrixs the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T13 rests on D6 (the kapon), A6 (closure under the second operation) and T3 (the kapon
is vexfex). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Here is (qenvex @ solvex) @ (vashtez @ umbazt), reduced without skipping anything.
    qenvex @ solvex = qenvex   (the table for @)
    vashtez @ umbazt = qenvex   (the table for @)
    qenvex @ qenvex = qenvex   (the table for @)
The expression comes to qenvex.

A companion case, solvex @ (vashtez @ qenvex), to show what the brackets are doing.
    vashtez @ qenvex = qenvex   (the table for @)
    solvex @ qenvex = qenvex   (the table for @)
That gives qenvex, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
glimmux :: qenvex hold? Read off what glimmux stands over: solvex. qenvex is not among
them, so it fails.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of drigrixs that come back
unchanged from themselves: solvex and qenvex. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of association of the first operation,
closure under the first operation and closure under the second operation. Those are
properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A6 (closure under the second operation), D6 (the kapon) and T3 (the kapon
is vexfex).

## Proofs

T13. If x and y lie in the kapon then so does x + y.

  (1) [T3] The kapon is already vexfex under @.
  (2) [A6] The second operation is defined on every pair.
  (3) [D6] The claim is that + respects the kapon as well.

Checked over 25 cases: every ordered pair from the core. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

The results now available are T13, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

This chapter carries no exercises. Nothing in it can be asked about in a way that could
not be answered without reading it, and an exercise like that is worse than none.
