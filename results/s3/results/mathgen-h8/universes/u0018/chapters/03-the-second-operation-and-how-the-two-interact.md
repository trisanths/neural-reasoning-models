# Chapter 4. The second operation and how the two interact

## Why this chapter

We turn to a neutral object for the second operation, self combination under the second
operation and closure under the second operation. The treatment is self contained given
the material already established.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over naksols, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A10. A neutral object for the second operation. There is a naksol wrenpyr with wrenpyr
<> x = x for every x.

A11. Self combination under the second operation. For every naksol x: x <> x = x.

A7. Closure under the second operation. For all naksols x and y, x <> y is again a
naksol.

A8. Association of the second operation. For all naksols x, y, z: (x <> y) <> z = x <>
(y <> z).

A9. Commutation of the second operation. For all naksols x and y: x <> y = y <> x.

## The shape of it

With two operations the question stops being what each does and becomes how they
interfere. <> binds tighter, so the interference shows up whenever a bracket is left
off.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 naksols the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R3 rests on S2 (the Nyrazt combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

R4 rests on S2 (the Nyrazt combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Evaluate (glimzam % pyrxil) % (wrenpyr % vexnak). Each line below is one lookup in a
table.
    glimzam % pyrxil = vexnak   (the table for %)
    wrenpyr % vexnak = vexnak   (the table for %)
    vexnak % vexnak = reldxil   (the table for %)
That leaves reldxil, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take pyrxil % (wrenpyr % glimzam).
    wrenpyr % glimzam = glimzam   (the table for %)
    pyrxil % glimzam = vexnak   (the table for %)
That gives vexnak, against reldxil above.

One decision about the relation, since deciding is as much a skill as computing. Does
vexnak >- vexlorn hold? Read off what vexnak stands over: vexnak, glimzam, reldxil and
pyrxil. vexlorn is not among them, so it fails.

## A case that breaks

R3. It is not the case that: For all naksols x, y, z: x <> (y % z) = (x <> y) % (x <>
z), and the same on the right. It fails at x = vexlorn, y = wrenpyr, z = wrenpyr, left =
vexlorn, right = vexnak. One case is enough, and this is the earliest one.

R4. It is not the case that: For all naksols x and y: x % (x <> y) = x and x <> (x % y)
= x. The case that settles it: x = wrenpyr, y = vexlorn, value = vexlorn. Anyone
carrying this claim over from a more familiar system will be wrong here, and wrong in a
way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside S2 (the Nyrazt combination tables).

What is built on it later: T19 (the second operation keeps the tezka intact).

## Proofs

R3. It is not the case that: For all naksols x, y, z: x <> (y % z) = (x <> y) % (x <> z), and the same on the right.

  (1) [S2] Take the case x = vexlorn, y = wrenpyr, z = wrenpyr, left = vexlorn, right = vexnak, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R4. It is not the case that: For all naksols x and y: x % (x <> y) = x and x <> (x % y) = x.

  (1) [S2] Take the case x = wrenpyr, y = vexlorn, value = vexlorn, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R3 and R4. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 5.
  x021. The following fails in this system: For all naksols x and y: x % (x <> y) = x and x <> (x % y) = x. Name the earliest naksol, in the order the naksols were introduced, that witnesses the failure.
