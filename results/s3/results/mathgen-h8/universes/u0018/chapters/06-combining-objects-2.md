# Chapter 7. Combining objects (2)

## Why this chapter

The practical content of this chapter is the tezka, the nakumb and combining on the left
never merges two naksols. It is the part that shows up in use.

Nothing here stands on its own. The arguments lean on chapters 1 and 5, and a reader who
has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over naksols, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D6. The tezka. The tezka of the system is the collection of naksols that glimvash with
every naksol.

Running the definition over every naksol leaves wrenpyr, vexlorn, vexnak, glimzam,
reldxil and pyrxil.

D7. The nakumb. The nakumb is the collection of all aztumb naksols.

In this system that picks out wrenpyr, which is 1 of the 6 naksols.

## The shape of it

Two questions sort the naksols quickly. Does combining a naksol with itself change it?
For wrenpyr it does not. Does it matter which side it goes on? For wrenpyr, vexlorn,
vexnak, glimzam, reldxil and pyrxil it does not.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T12 rests on A6 (cancellation in the first operation) and D2 (naksols that glimvash).
The dependence is on the content of those results, not only on their vocabulary.

## A worked case

Evaluate vexlorn % wrenpyr <> reldxil. Each line below is one lookup in a table.
    wrenpyr <> reldxil = reldxil   (the table for <>)
    vexlorn % reldxil = pyrxil   (the table for %)
The expression comes to pyrxil.

Bracketing is not cosmetic, so here is wrenpyr % (reldxil % vexlorn) for contrast.
    reldxil % vexlorn = pyrxil   (the table for %)
    wrenpyr % pyrxil = pyrxil   (the table for %)
The value is pyrxil. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
wrenpyr >- vexlorn hold? Read off what wrenpyr stands over: wrenpyr, vexlorn, vexnak,
glimzam, reldxil and pyrxil. vexlorn is among them, so it holds.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of naksols that come back
unchanged from themselves: wrenpyr. Assuming more of them than that is the mistake to
avoid.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by cancellation in the first operation and closure under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

That is not a rhetorical caution. Take the same 6 objects, the same symbols, and a
different table, and T12 stop holding. The notation survives the substitution and the
mathematics does not.

## Neighbouring results

The material this chapter borrows from: A6 (cancellation in the first operation), D1
(aztumb naksols) and D2 (naksols that glimvash).

What is built on it later: T2 (the muxisk lies in the tezka), T5 (the tezka is hobreld),
T10 (the thrapon of a tezka naksol stays in the tezka) and T11 (the nakumb is hobreld).

## Proofs

T12. For every naksol a, the assignment x to a % x sends distinct naksols to distinct naksols.

  (1) [A6] Suppose a % x = a % y.
  (2) [A6] Cancellation on the left gives x = y.
  (3) So the assignment is injective, and being injective on a finite carrier it is onto.

Checked over 36 cases: every object translated by every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the tezka and the nakumb. Later chapters state their results in these
terms and do not restate the definitions.

The results now available are T12, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x027. Write down the nakumb in full.
