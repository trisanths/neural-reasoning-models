# Chapter 3. The relation and what it orders

## Why this chapter

The present chapter develops antisymmetry of the relation, transitivity of the relation
and the espafex of a opalmi.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

One habit to adopt: when a statement below quantifies over opalmis, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A6. Antisymmetry of the relation. For all opalmis x and y: if x <~ y and y <~ x then x =
y.

A7. Transitivity of the relation. For all opalmis x, y, z: if x <~ y and y <~ z then x
<~ z.

D4. The espafex of a opalmi. The espafex of a opalmi x is the collection of opalmis y
for which x <~ y holds.

Worked out for each opalmi: keldsib to keldsib, duthzam, hobfex, iskxil and qenxil;
duthzam to duthzam; hobfex to duthzam; iskxil to duthzam; qenxil to duthzam.

## The shape of it

The relation is easiest to see as a height. Each opalmi casts a espafex over what it
covers, and the sizes of those shadows here are 1 and 5. Sizes repeat, so the objects do
not line up in single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 opalmis the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R4 rests on S2 (the Duthsol combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R5 rests on S2 (the Duthsol combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R6 rests on S2 (the Duthsol combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Here is (duthzam - keldsib) - hobfex, reduced without skipping anything.
    duthzam - keldsib = keldsib   (the table for -)
    keldsib - hobfex = keldsib   (the table for -)
The expression comes to keldsib.

Move the brackets and the work changes. Take keldsib - (hobfex - duthzam).
    hobfex - duthzam = hobfex   (the table for -)
    keldsib - hobfex = keldsib   (the table for -)
That gives keldsib, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
duthzam <~ iskxil hold? Read off what duthzam stands over: duthzam. iskxil is not among
them, so it fails.

## A case that breaks

R4. It is not the case that: For every opalmi x: x <~ x. It fails at x = hobfex. One
case is enough, and this is the earliest one.

R5. It is not the case that: For all opalmis x and y, at least one of x <~ y and y <~ x
holds. It fails at x = hobfex, y = hobfex. One case is enough, and this is the earliest
one.

R6. It is not the case that: For all opalmis x, y, z: if x <~ y then (z - x) <~ (z - y)
and (x - z) <~ (y - z). It fails at x = duthzam, y = duthzam, z = hobfex, side = left.
One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: S2 (the Duthsol combination tables).

What is built on it later: D9 (a hobsol), D13 (grixhob pairs), T9 (espafexs are nested
along the relation) and T10 (there is at most one hobsol).

## Proofs

R4. It is not the case that: For every opalmi x: x <~ x.

  (1) [S2] Take the case x = hobfex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R5. It is not the case that: For all opalmis x and y, at least one of x <~ y and y <~ x holds.

  (1) [S2] Take the case x = hobfex, y = hobfex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R6. It is not the case that: For all opalmis x, y, z: if x <~ y then (z - x) <~ (z - y) and (x - z) <~ (y - z).

  (1) [S2] Take the case x = duthzam, y = duthzam, z = hobfex, side = left, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the espafex of a opalmi. Each of these is used by name
later, so the names are worth learning rather than looking up.

Explicitly not available: R4, R5 and R6. A later argument that quietly assumes one of
these is wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x022. Which opalmis y satisfy keldsib <~ y? Name them all.
  x023. Which opalmis y satisfy hobfex <~ y? Name them all.
  x024. List the espafex of iskxil.
  x025. List the espafex of qenxil.
Level 5.
  x016. The following fails in this system: For every opalmi x: x <~ x. Name the earliest opalmi, in the order the opalmis were introduced, that witnesses the failure.
  x017. The following fails in this system: For all opalmis x and y, at least one of x <~ y and y <~ x holds. Name the earliest opalmi, in the order the opalmis were introduced, that witnesses the failure.
  x018. The following fails in this system: For all opalmis x, y, z: if x <~ y then (z - x) <~ (z - y) and (x - z) <~ (y - z). Name the earliest opalmi, in the order the opalmis were introduced, that witnesses the failure.
