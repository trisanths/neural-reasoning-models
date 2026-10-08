# Chapter 3. The relation and what it orders

## Why this chapter

Anyone using this system to keep track of something will meet comparability of every
pair, agreement of the relation with the second operation and reflexivity of the
relation early, whether or not they go looking.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

One habit to adopt: when a statement below quantifies over zelbras, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A10. Comparability of every pair. For all zelbras x and y, at least one of x <~ y and y
<~ x holds.

A11. Agreement of the relation with the second operation. For all zelbras x, y, z: if x
<~ y then (z - x) <~ (z - y) and (x - z) <~ (y - z).

A7. Reflexivity of the relation. For every zelbra x: x <~ x.

A8. Antisymmetry of the relation. For all zelbras x and y: if x <~ y and y <~ x then x =
y.

A9. Transitivity of the relation. For all zelbras x, y, z: if x <~ y and y <~ z then x
<~ z.

D4. The opalpyr of a zelbra. The opalpyr of a zelbra x is the collection of zelbras y
for which x <~ y holds.

Worked out for each zelbra: tarnnyr to tarnnyr, cloxil, isktez and iskmi; cloxil to
cloxil, isktez and iskmi; isktez to isktez and iskmi; iskmi to iskmi.

## The shape of it

The relation is easiest to see as a height. Each zelbra casts a opalpyr over what it
shadows, and the sizes of those shadows here are 1, 2, 3 and 4. No two are the same
size, so the objects line up in a single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 zelbras the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R10 rests on S2 (the Bramorn combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Here is isktez * tarnnyr - cloxil, reduced without skipping anything.
    tarnnyr - cloxil = cloxil   (the table for -)
    isktez * cloxil = cloxil   (the table for *)
The expression comes to cloxil.

Move the brackets and the work changes. Take tarnnyr * (cloxil * isktez).
    cloxil * isktez = tarnnyr   (the table for *)
    tarnnyr * tarnnyr = tarnnyr   (the table for *)
That gives tarnnyr, against cloxil above.

Test tarnnyr <~ tarnnyr. The opalpyr of tarnnyr is tarnnyr, cloxil, isktez and iskmi,
and tarnnyr lies inside it, so the relation holds.

## A case that breaks

R10. It is not the case that: For all zelbras x, y, z: if x <~ y then (z * x) <~ (z * y)
and (x * z) <~ (y * z). It fails at x = tarnnyr, y = cloxil, z = cloxil, side = left.
One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: S2 (the Bramorn combination tables).

What is built on it later: D8 (a nakpyr), D11 (mishen pairs), T6 (opalpyrs are nested
along the relation) and T7 (there is at most one nakpyr).

## Proofs

R10. It is not the case that: For all zelbras x, y, z: if x <~ y then (z * x) <~ (z * y) and (x * z) <~ (y * z).

  (1) [S2] Take the case x = tarnnyr, y = cloxil, z = cloxil, side = left, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the opalpyr of a zelbra. Each of these is used by name
later, so the names are worth learning rather than looking up.

Explicitly not available: R10. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x019. List the opalpyr of tarnnyr.
  x020. Which zelbras y satisfy cloxil <~ y? Name them all.
  x021. Which zelbras y satisfy isktez <~ y? Name them all.
Level 5.
  x016. The following fails in this system: For all zelbras x, y, z: if x <~ y then (z * x) <~ (z * y) and (x * z) <~ (y * z). Name the earliest zelbra, in the order the zelbras were introduced, that witnesses the failure.
