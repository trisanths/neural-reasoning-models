# Chapter 4. The second operation and how the two interact

## Why this chapter

What follows was pieced together backwards. The last item of it, closure under the
second operation, association of the second operation and commutation of the second
operation, was noticed before anyone had a reason to expect it.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
shenopals that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A2. Closure under the second operation. For all shenopals x and y, x & y is again a
shenopal.

A3. Association of the second operation. For all shenopals x, y, z: (x & y) & z = x & (y
& z).

A4. Commutation of the second operation. For all shenopals x and y: x & y = y & x.

A5. A neutral object for the second operation. There is a shenopal opallorn with
opallorn & x = x for every x.

A6. Self combination under the second operation. For every shenopal x: x & x = x.

## The shape of it

The interesting content of a two operation system sits in the gap between them: which
one distributes over which, and which shenopals are fixed by both.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 shenopals the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R8 rests on S2 (the Vintfex combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R9 rests on S2 (the Vintfex combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Here is (opallorn % pontu) % (grixlum % qenthra), reduced without skipping anything.
    opallorn % pontu = opallorn   (the table for %)
    grixlum % qenthra = qenthra   (the table for %)
    opallorn % qenthra = opallorn   (the table for %)
The expression comes to opallorn.

A companion case, pontu % (grixlum % opallorn), to show what the brackets are doing.
    grixlum % opallorn = grixlum   (the table for %)
    pontu % grixlum = grixlum   (the table for %)
That gives grixlum, against opallorn above.

Test vorpon :: opallorn. The muxsib of vorpon is vorpon and pontu, and opallorn lies
outside it, so the relation fails.

## A case that breaks

R8. It is not the case that: For all shenopals x, y, z: x & (y % z) = (x & y) % (x & z),
and the same on the right. It fails at x = qenthra, y = opallorn, z = opallorn, left =
qenthra, right = opallorn. One case is enough, and this is the earliest one.

R9. It is not the case that: For all shenopals x and y: x % (x & y) = x and x & (x % y)
= x. It fails at x = qenthra, y = opallorn, value = opallorn. One case is enough, and
this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: S2 (the Vintfex combination tables).

## Proofs

R8. It is not the case that: For all shenopals x, y, z: x & (y % z) = (x & y) % (x & z), and the same on the right.

  (1) [S2] Take the case x = qenthra, y = opallorn, z = opallorn, left = qenthra, right = opallorn, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R9. It is not the case that: For all shenopals x and y: x % (x & y) = x and x & (x % y) = x.

  (1) [S2] Take the case x = qenthra, y = opallorn, value = opallorn, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R8 and R9. These were tested and failed, and the failing cases are
recorded above.

## Exercises

No exercises here. Every question this chapter suggested turned out to be answerable
from the question itself, so all of them were discarded.
