# Chapter 3. The relation and what it orders

## Why this chapter

What follows was pieced together backwards. The last item of it, comparability of every
pair, reflexivity of the relation and antisymmetry of the relation, was noticed before
anyone had a reason to expect it.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

The standard of proof here is exhaustion. A universal claim about lumpons covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A10. Comparability of every pair. For all lumpons x and y, at least one of x >- y and y
>- x holds.

A7. Reflexivity of the relation. For every lumpon x: x >- x.

A8. Antisymmetry of the relation. For all lumpons x and y: if x >- y and y >- x then x =
y.

A9. Transitivity of the relation. For all lumpons x, y, z: if x >- y and y >- z then x
>- z.

D4. The yukglim of a lumpon. The yukglim of a lumpon x is the collection of lumpons y
for which x >- y holds.

Worked out for each lumpon: glimtez to glimtez, glimkorr, nakkorr, duthwren, kaka and
mornhob; glimkorr to glimkorr, nakkorr, duthwren, kaka and mornhob; nakkorr to nakkorr,
duthwren, kaka and mornhob; duthwren to duthwren, kaka and mornhob; kaka to kaka and
mornhob; mornhob to mornhob.

## The shape of it

The relation is easiest to see as a height. Each lumpon casts a yukglim over what it
precedes, and the sizes of those shadows here are 1, 2, 3, 4, 5 and 6. No two are the
same size, so the objects line up in a single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 lumpons the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R3 rests on S2 (the Quilpon combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Evaluate (kaka - duthwren) - glimtez. Each line below is one lookup in a table.
    kaka - duthwren = glimkorr   (the table for -)
    glimkorr - glimtez = glimkorr   (the table for -)
The expression comes to glimkorr.

A companion case, duthwren - (glimtez - kaka), to show what the brackets are doing.
    glimtez - kaka = kaka   (the table for -)
    duthwren - kaka = glimkorr   (the table for -)
The value is glimkorr. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test glimkorr >- kaka. The yukglim of glimkorr is glimkorr, nakkorr, duthwren, kaka and
mornhob, and kaka lies inside it, so the relation holds.

## A case that breaks

R3. It is not the case that: For all lumpons x, y, z: if x >- y then (z - x) >- (z - y)
and (x - z) >- (y - z). It fails at x = glimtez, y = glimkorr, z = mornhob, side = left.
One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside S2 (the Quilpon combination tables).

These results are used again in D9 (a aztlum), D14 (cloka pairs), T13 (yukglims are
nested along the relation) and T14 (there is at most one aztlum).

## Proofs

R3. It is not the case that: For all lumpons x, y, z: if x >- y then (z - x) >- (z - y) and (x - z) >- (y - z).

  (1) [S2] Take the case x = glimtez, y = glimkorr, z = mornhob, side = left, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the yukglim of a lumpon. Later chapters state their results in these terms
and do not restate the definitions.

Do not carry forward R3. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 5.
  x020. The following fails in this system: For all lumpons x, y, z: if x >- y then (z - x) >- (z - y) and (x - z) >- (y - z). Name the earliest lumpon, in the order the lumpons were introduced, that witnesses the failure.
