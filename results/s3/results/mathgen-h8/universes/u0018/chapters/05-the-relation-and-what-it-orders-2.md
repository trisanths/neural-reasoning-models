# Chapter 6. The relation and what it orders (2)

## Why this chapter

What follows was pieced together backwards. The last item of it, xiltez pairs, hobreld
collections and a solisk, was noticed before anyone had a reason to expect it.

Nothing here stands on its own. The arguments lean on chapters 1 and 3, and a reader who
has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
naksols that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D14. Xiltez pairs. Two distinct naksols x and y form a xiltez pair when x >- y and y >-
x both hold, that is, when each lies in the tufex of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D3. Hobreld collections. A collection S of naksols is hobreld when x % y belongs to S
for every pair x, y drawn from S.

D9. A solisk. A naksol f is a solisk when f >- y holds for every naksol y, that is, when
the tufex of f is the whole system.

In this system that picks out wrenpyr, which is 1 of the 6 naksols.

## The shape of it

Picture the thrapon as what happens when you start with one naksol and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 6 naksols, that stops. In this system the sizes it stops at are 1, 2, 3 and 6.

Think of >- as pointing downhill. The tufex of a naksol is everything downhill of it,
and those shadows here have sizes 1, 2, 3, 4, 5 and 6.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R7 rests on D4 (the tufex of a naksol). The dependence is on the content of those
results, not only on their vocabulary.

T13 rests on D4 (the tufex of a naksol) and A14 (transitivity of the relation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Take (pyrxil % wrenpyr) % (glimzam % vexlorn) and work it out one step at a time.
    pyrxil % wrenpyr = pyrxil   (the table for %)
    glimzam % vexlorn = reldxil   (the table for %)
    pyrxil % reldxil = glimzam   (the table for %)
That leaves glimzam, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take wrenpyr % (glimzam % pyrxil).
    glimzam % pyrxil = vexnak   (the table for %)
    wrenpyr % vexnak = vexnak   (the table for %)
The value is vexnak, not glimzam.

Test vexnak >- reldxil. The tufex of vexnak is vexnak, glimzam, reldxil and pyrxil, and
reldxil lies inside it, so the relation holds.

## A case that breaks

R7. It is not the case that: If x >- y then y >- x. The case that settles it: x =
wrenpyr, y = vexlorn. Anyone carrying this claim over from a more familiar system will
be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by closure under the first operation and transitivity of the
relation. A system without them is not a system where these results are harder to prove;
it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A1 (closure under the first operation), A14 (transitivity of the
relation) and D4 (the tufex of a naksol).

What is built on it later: D8 (the thrapon of a naksol), T5 (the tezka is hobreld), T6
(the thrapon of a naksol is hobreld) and T11 (the nakumb is hobreld).

## Proofs

R7. It is not the case that: If x >- y then y >- x.

  (1) [S2] Take the case x = wrenpyr, y = vexlorn, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T13. If y lies in the tufex of x, then the tufex of y is contained in the tufex of x.

  (1) [D4] Let y satisfy x >- y and let z satisfy y >- z.
  (2) [A14] Transitivity gives x >- z.
  (3) [D4] So every member of the tufex of y is a member of that of x.

Checked over 216 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward xiltez pairs, hobreld collections and a solisk. Later chapters state their
results in these terms and do not restate the definitions.

Established here and safe to use: T13.

Do not carry forward R7. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x024. How many naksols lie in the smallest hobreld collection containing vexlorn?
  x025. How many naksols lie in the smallest hobreld collection containing vexnak?
