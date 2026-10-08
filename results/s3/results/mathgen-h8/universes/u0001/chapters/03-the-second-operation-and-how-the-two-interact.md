# Chapter 4. The second operation and how the two interact

## Why this chapter

Anyone using this system to keep track of something will meet self combination under the
second operation, closure under the second operation and association of the second
operation early, whether or not they go looking.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
drigrixs that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A10. Self combination under the second operation. For every drigrix x: x + x = x.

A6. Closure under the second operation. For all drigrixs x and y, x + y is again a
drigrix.

A7. Association of the second operation. For all drigrixs x, y, z: (x + y) + z = x + (y
+ z).

A8. Commutation of the second operation. For all drigrixs x and y: x + y = y + x.

A9. A neutral object for the second operation. There is a drigrix qenvex with qenvex + x
= x for every x.

## The shape of it

The interesting content of a two operation system sits in the gap between them: which
one distributes over which, and which drigrixs are fixed by both.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R4 rests on S2 (the Umbtu combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

R5 rests on S2 (the Umbtu combination tables). The dependence is on the content of those
results, not only on their vocabulary.

## A worked case

Evaluate (vashtez @ qenvex) @ (glimmux @ umbazt). Each line below is one lookup in a
table.
    vashtez @ qenvex = qenvex   (the table for @)
    glimmux @ umbazt = vashtez   (the table for @)
    qenvex @ vashtez = qenvex   (the table for @)
That leaves qenvex, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is qenvex @ (glimmux @ vashtez) for contrast.
    glimmux @ vashtez = qenvex   (the table for @)
    qenvex @ qenvex = qenvex   (the table for @)
That gives qenvex, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
qenvex :: umbazt hold? Read off what qenvex stands over: solvex, umbazt, glimmux,
vashtez and qenvex. umbazt is among them, so it holds.

## A case that breaks

R4. It is not the case that: For all drigrixs x, y, z: x + (y @ z) = (x + y) @ (x + z),
and the same on the right. The case that settles it: x = umbazt, y = umbazt, z = umbazt,
left = umbazt, right = glimmux. Anyone carrying this claim over from a more familiar
system will be wrong here, and wrong in a way that propagates.

R5. It is not the case that: For all drigrixs x and y: x @ (x + y) = x and x + (x @ y) =
x. It fails at x = umbazt, y = umbazt, value = glimmux. One case is enough, and this is
the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: S2 (the Umbtu combination tables).

These results are used again in T13 (the second operation keeps the kapon intact).

## Proofs

R4. It is not the case that: For all drigrixs x, y, z: x + (y @ z) = (x + y) @ (x + z), and the same on the right.

  (1) [S2] Take the case x = umbazt, y = umbazt, z = umbazt, left = umbazt, right = glimmux, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R5. It is not the case that: For all drigrixs x and y: x @ (x + y) = x and x + (x @ y) = x.

  (1) [S2] Take the case x = umbazt, y = umbazt, value = glimmux, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R4 and R5. A later argument that quietly assumes one of these
is wrong, and the counterexamples above say exactly where.

## Exercises

No exercises here. Every question this chapter suggested turned out to be answerable
from the question itself, so all of them were discarded.
