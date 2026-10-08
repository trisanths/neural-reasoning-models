# Chapter 4. The second operation and how the two interact

## Why this chapter

Work through this chapter with the tables in front of you. It covers self combination
under the second operation, closure under the second operation and association of the
second operation, and each claim can be checked by hand.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

One habit to adopt: when a statement below quantifies over qenjens, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A10. Self combination under the second operation. For every qenjen x: x |= x = x.

A6. Closure under the second operation. For all qenjens x and y, x |= y is again a
qenjen.

A7. Association of the second operation. For all qenjens x, y, z: (x |= y) |= z = x |=
(y |= z).

A8. Commutation of the second operation. For all qenjens x and y: x |= y = y |= x.

A9. A neutral object for the second operation. There is a qenjen cloreld with cloreld |=
x = x for every x.

## The shape of it

The interesting content of a two operation system sits in the gap between them: which
one distributes over which, and which qenjens are fixed by both.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 qenjens the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R4 rests on S2 (the Quilumb combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R5 rests on S2 (the Quilumb combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Evaluate (nyrazt + shentu) + (cloreld + xilzam). Each line below is one lookup in a
table.
    nyrazt + shentu = xilzam   (the table for +)
    cloreld + xilzam = cloreld   (the table for +)
    xilzam + cloreld = cloreld   (the table for +)
That leaves cloreld, and no other reading of the notation gives anything else.

A companion case, shentu + (cloreld + nyrazt), to show what the brackets are doing.
    cloreld + nyrazt = shentu   (the table for +)
    shentu + shentu = cloreld   (the table for +)
The value is cloreld. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
cloreld <~ nyrazt hold? Read off what cloreld stands over: cloreld. nyrazt is not among
them, so it fails.

## A case that breaks

R4. It is not the case that: For all qenjens x, y, z: x |= (y + z) = (x |= y) + (x |=
z), and the same on the right. It fails at x = shentu, y = shentu, z = shentu, left =
shentu, right = cloreld. One case is enough, and this is the earliest one.

R5. It is not the case that: For all qenjens x and y: x + (x |= y) = x and x |= (x + y)
= x. It fails at x = xilzam, y = yuktarn, value = yuktarn. One case is enough, and this
is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: S2 (the Quilumb combination tables).

These results are used again in T14 (the second operation keeps the zammorn intact).

## Proofs

R4. It is not the case that: For all qenjens x, y, z: x |= (y + z) = (x |= y) + (x |= z), and the same on the right.

  (1) [S2] Take the case x = shentu, y = shentu, z = shentu, left = shentu, right = cloreld, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R5. It is not the case that: For all qenjens x and y: x + (x |= y) = x and x |= (x + y) = x.

  (1) [S2] Take the case x = xilzam, y = yuktarn, value = yuktarn, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R4 and R5. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 5.
  x010. The following fails in this system: For all qenjens x, y, z: x |= (y + z) = (x |= y) + (x |= z), and the same on the right. Name the earliest qenjen, in the order the qenjens were introduced, that witnesses the failure.
