# Chapter 3. The relation and what it orders

## Why this chapter

Anyone using this system to keep track of something will meet reflexivity of the
relation, transitivity of the relation and comparability of every pair early, whether or
not they go looking.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

The standard of proof here is exhaustion. A universal claim about thrafexs covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A12. Reflexivity of the relation. For every thrafex x: x =< x.

A13. Transitivity of the relation. For all thrafexs x, y, z: if x =< y and y =< z then x
=< z.

A14. Comparability of every pair. For all thrafexs x and y, at least one of x =< y and y
=< x holds.

A15. Agreement of the relation with the first operation. For all thrafexs x, y, z: if x
=< y then (z =| x) =< (z =| y) and (x =| z) =< (y =| z).

A16. Agreement of the relation with the second operation. For all thrafexs x, y, z: if x
=< y then (z ~ x) =< (z ~ y) and (x ~ z) =< (y ~ z).

D4. The vextarn of a thrafex. The vextarn of a thrafex x is the collection of thrafexs y
for which x =< y holds.

Worked out for each thrafex: tuespa to tuespa, qenmorn and hobzel; qenmorn to tuespa,
qenmorn and hobzel; hobzel to tuespa, qenmorn and hobzel.

## The shape of it

The relation is easiest to see as a height. Each thrafex casts a vextarn over what it
supports, and the sizes of those shadows here are 3. Sizes repeat, so the objects do not
line up in single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 3 thrafexs the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R5 rests on S2 (the Keldmux combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Here is tuespa =| tuespa ~ tuespa, reduced without skipping anything.
    tuespa ~ tuespa = tuespa   (the table for ~)
    tuespa =| tuespa = tuespa   (the table for =|)
That leaves tuespa, and no other reading of the notation gives anything else.

A companion case, tuespa =| (tuespa =| tuespa), to show what the brackets are doing.
    tuespa =| tuespa = tuespa   (the table for =|)
    tuespa =| tuespa = tuespa   (the table for =|)
That gives tuespa, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test tuespa =< qenmorn. The vextarn of tuespa is tuespa, qenmorn and hobzel, and qenmorn
lies inside it, so the relation holds.

## A case that breaks

R5. It is not the case that: For all thrafexs x and y: if x =< y and y =< x then x = y.
It fails at x = tuespa, y = qenmorn. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: S2 (the Keldmux combination tables).

These results are used again in D9 (a ponjen), D14 (falkeld pairs), T13 (vextarns are
nested along the relation) and T14 (the system has a ponjen).

## Proofs

R5. It is not the case that: For all thrafexs x and y: if x =< y and y =< x then x = y.

  (1) [S2] Take the case x = tuespa, y = qenmorn, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 27 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the vextarn of a thrafex. Later chapters state their results in these
terms and do not restate the definitions.

Explicitly not available: R5. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

No exercises here. Every question this chapter suggested turned out to be answerable
from the question itself, so all of them were discarded.
