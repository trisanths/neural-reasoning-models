# Chapter 3. The relation and what it orders

## Why this chapter

The practical content of this chapter is agreement of the relation with the first
operation, reflexivity of the relation and antisymmetry of the relation. It is the part
that shows up in use.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
driwrens that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A10. Agreement of the relation with the first operation. For all driwrens x, y, z: if x
<< y then (z * x) << (z * y) and (x * z) << (y * z).

A7. Reflexivity of the relation. For every driwren x: x << x.

A8. Antisymmetry of the relation. For all driwrens x and y: if x << y and y << x then x
= y.

A9. Transitivity of the relation. For all driwrens x, y, z: if x << y and y << z then x
<< z.

D4. The zelfex of a driwren. The zelfex of a driwren x is the collection of driwrens y
for which x << y holds.

Worked out for each driwren: nakquil to nakquil; soltarn to nakquil and soltarn; muxsib
to nakquil and muxsib; braovi to nakquil, soltarn and braovi; yukzel to nakquil,
soltarn, muxsib and yukzel; thraisk to nakquil, soltarn, muxsib, braovi, yukzel and
thraisk.

## The shape of it

The relation is easiest to see as a height. Each driwren casts a zelfex over what it
precedes, and the sizes of those shadows here are 1, 2, 3, 4 and 6. Sizes repeat, so the
objects do not line up in single file.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R3 rests on S2 (the Vorjen combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Evaluate (nakquil * yukzel) * thraisk. Each line below is one lookup in a table.
    nakquil * yukzel = yukzel   (the table for *)
    yukzel * thraisk = thraisk   (the table for *)
The expression comes to thraisk.

Move the brackets and the work changes. Take yukzel * (thraisk * nakquil).
    thraisk * nakquil = thraisk   (the table for *)
    yukzel * thraisk = thraisk   (the table for *)
That gives thraisk, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
muxsib << nakquil hold? Read off what muxsib stands over: nakquil and muxsib. nakquil is
among them, so it holds.

## A case that breaks

R3. It is not the case that: For all driwrens x and y, at least one of x << y and y << x
holds. It fails at x = soltarn, y = muxsib. One case is enough, and this is the earliest
one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: S2 (the Vorjen combination tables).

These results are used again in D9 (a keldumb), D13 (jenfex pairs), T10 (zelfexs are
nested along the relation) and T11 (there is at most one keldumb).

## Proofs

R3. It is not the case that: For all driwrens x and y, at least one of x << y and y << x holds.

  (1) [S2] Take the case x = soltarn, y = muxsib, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the zelfex of a driwren. Each of these is used by name
later, so the names are worth learning rather than looking up.

Do not carry forward R3. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x012. List the zelfex of soltarn.
  x013. List the zelfex of muxsib.
  x014. Which driwrens y satisfy braovi << y? Name them all.
  x015. Which driwrens y satisfy yukzel << y? Name them all.
  x016. List the zelfex of thraisk.
