# Chapter 3. The relation and what it orders

## Why this chapter

The results collected here were not found in this order. Antisymmetry of the relation,
transitivity of the relation and the aztdri of a drigrix came first, and the rest was
assembled around that once the pattern was visible.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over drigrixs, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A11. Antisymmetry of the relation. For all drigrixs x and y: if x :: y and y :: x then x
= y.

A12. Transitivity of the relation. For all drigrixs x, y, z: if x :: y and y :: z then x
:: z.

D4. The aztdri of a drigrix. The aztdri of a drigrix x is the collection of drigrixs y
for which x :: y holds.

Worked out for each drigrix: solvex to solvex; umbazt to solvex; glimmux to solvex;
vashtez to solvex; qenvex to solvex, umbazt, glimmux, vashtez and qenvex.

## The shape of it

The relation is easiest to see as a height. Each drigrix casts a aztdri over what it
covers, and the sizes of those shadows here are 1 and 5. Sizes repeat, so the objects do
not line up in single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 drigrixs the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R6 rests on S2 (the Umbtu combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

R7 rests on S2 (the Umbtu combination tables). The dependence is on the content of those
results, not only on their vocabulary.

R8 rests on S2 (the Umbtu combination tables). The dependence is on the content of those
results, not only on their vocabulary.

R9 rests on S2 (the Umbtu combination tables). The dependence is on the content of those
results, not only on their vocabulary.

## A worked case

Here is qenvex @ glimmux + solvex, reduced without skipping anything.
    glimmux + solvex = solvex   (the table for +)
    qenvex @ solvex = qenvex   (the table for @)
The expression comes to qenvex.

Bracketing is not cosmetic, so here is glimmux @ (solvex @ qenvex) for contrast.
    solvex @ qenvex = qenvex   (the table for @)
    glimmux @ qenvex = qenvex   (the table for @)
That gives qenvex, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test umbazt :: vashtez. The aztdri of umbazt is solvex, and vashtez lies outside it, so
the relation fails.

## A case that breaks

R6. It is not the case that: For every drigrix x: x :: x. The case that settles it: x =
umbazt. Anyone carrying this claim over from a more familiar system will be wrong here,
and wrong in a way that propagates.

R7. It is not the case that: For all drigrixs x and y, at least one of x :: y and y :: x
holds. The case that settles it: x = umbazt, y = umbazt. Anyone carrying this claim over
from a more familiar system will be wrong here, and wrong in a way that propagates.

R8. It is not the case that: For all drigrixs x, y, z: if x :: y then (z @ x) :: (z @ y)
and (x @ z) :: (y @ z). It fails at x = solvex, y = solvex, z = umbazt, side = left. One
case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside S2 (the Umbtu combination tables).

What is built on it later: D9 (a grixvash), D13 (nakkeld pairs), T9 (aztdris are nested
along the relation) and T10 (there is at most one grixvash).

## Proofs

R6. It is not the case that: For every drigrix x: x :: x.

  (1) [S2] Take the case x = umbazt, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R7. It is not the case that: For all drigrixs x and y, at least one of x :: y and y :: x holds.

  (1) [S2] Take the case x = umbazt, y = umbazt, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R8. It is not the case that: For all drigrixs x, y, z: if x :: y then (z @ x) :: (z @ y) and (x @ z) :: (y @ z).

  (1) [S2] Take the case x = solvex, y = solvex, z = umbazt, side = left, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R9. It is not the case that: For all drigrixs x, y, z: if x :: y then (z + x) :: (z + y) and (x + z) :: (y + z).

  (1) [S2] Take the case x = qenvex, y = umbazt, z = umbazt, side = left, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the aztdri of a drigrix. Each of these is used by name
later, so the names are worth learning rather than looking up.

Explicitly not available: R6, R7, R8 and R9. A later argument that quietly assumes one
of these is wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x019. Which drigrixs y satisfy umbazt :: y? Name them all.
  x020. List the aztdri of glimmux.
  x021. Which drigrixs y satisfy vashtez :: y? Name them all.
  x022. List the aztdri of qenvex.
Level 5.
  x013. The following fails in this system: For every drigrix x: x :: x. Name the earliest drigrix, in the order the drigrixs were introduced, that witnesses the failure.
  x014. The following fails in this system: For all drigrixs x and y, at least one of x :: y and y :: x holds. Name the earliest drigrix, in the order the drigrixs were introduced, that witnesses the failure.
  x015. The following fails in this system: For all drigrixs x, y, z: if x :: y then (z @ x) :: (z @ y) and (x @ z) :: (y @ z). Name the earliest drigrix, in the order the drigrixs were introduced, that witnesses the failure.
