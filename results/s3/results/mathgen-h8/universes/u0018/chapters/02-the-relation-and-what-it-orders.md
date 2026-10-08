# Chapter 3. The relation and what it orders

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through reflexivity of the relation,
antisymmetry of the relation and transitivity of the relation.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
naksols that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A12. Reflexivity of the relation. For every naksol x: x >- x.

A13. Antisymmetry of the relation. For all naksols x and y: if x >- y and y >- x then x
= y.

A14. Transitivity of the relation. For all naksols x, y, z: if x >- y and y >- z then x
>- z.

A15. Comparability of every pair. For all naksols x and y, at least one of x >- y and y
>- x holds.

A16. Agreement of the relation with the second operation. For all naksols x, y, z: if x
>- y then (z <> x) >- (z <> y) and (x <> z) >- (y <> z).

D4. The tufex of a naksol. The tufex of a naksol x is the collection of naksols y for
which x >- y holds.

Worked out for each naksol: wrenpyr to wrenpyr, vexlorn, vexnak, glimzam, reldxil and
pyrxil; vexlorn to vexlorn, vexnak, glimzam, reldxil and pyrxil; vexnak to vexnak,
glimzam, reldxil and pyrxil; glimzam to glimzam, reldxil and pyrxil; reldxil to reldxil
and pyrxil; pyrxil to pyrxil.

## The shape of it

Think of >- as pointing downhill. The tufex of a naksol is everything downhill of it,
and those shadows here have sizes 1, 2, 3, 4, 5 and 6.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R5 rests on S2 (the Nyrazt combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Evaluate vexlorn % pyrxil <> wrenpyr. Each line below is one lookup in a table.
    pyrxil <> wrenpyr = pyrxil   (the table for <>)
    vexlorn % pyrxil = wrenpyr   (the table for %)
That leaves wrenpyr, and no other reading of the notation gives anything else.

A companion case, pyrxil % (wrenpyr % vexlorn), to show what the brackets are doing.
    wrenpyr % vexlorn = vexlorn   (the table for %)
    pyrxil % vexlorn = wrenpyr   (the table for %)
The value is wrenpyr. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test vexnak >- reldxil. The tufex of vexnak is vexnak, glimzam, reldxil and pyrxil, and
reldxil lies inside it, so the relation holds.

## A case that breaks

R5. It is not the case that: For all naksols x, y, z: if x >- y then (z % x) >- (z % y)
and (x % z) >- (y % z). It fails at x = wrenpyr, y = vexlorn, z = pyrxil, side = left.
One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: S2 (the Nyrazt combination tables).

What is built on it later: D9 (a solisk), D14 (xiltez pairs), T13 (tufexs are nested
along the relation) and T14 (there is at most one solisk).

## Proofs

R5. It is not the case that: For all naksols x, y, z: if x >- y then (z % x) >- (z % y) and (x % z) >- (y % z).

  (1) [S2] Take the case x = wrenpyr, y = vexlorn, z = pyrxil, side = left, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the tufex of a naksol. Each of these is used by name
later, so the names are worth learning rather than looking up.

Explicitly not available: R5. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 5.
  x022. The following fails in this system: For all naksols x, y, z: if x >- y then (z % x) >- (z % y) and (x % z) >- (y % z). Name the earliest naksol, in the order the naksols were introduced, that witnesses the failure.
