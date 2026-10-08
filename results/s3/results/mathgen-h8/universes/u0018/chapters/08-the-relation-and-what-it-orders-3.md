# Chapter 9. The relation and what it orders (3)

## Why this chapter

The present chapter develops the thrapon of a naksol, there is at most one solisk and
the system has a solisk.

Nothing here stands on its own. The arguments lean on chapters 3 and 6, and a reader who
has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about naksols covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

## What is defined here

D8. The thrapon of a naksol. The thrapon of a naksol x, written [x], is the smallest
hobreld collection that contains x.

Worked out for each naksol: wrenpyr to wrenpyr; vexlorn to wrenpyr, vexlorn, vexnak,
glimzam, reldxil and pyrxil; vexnak to wrenpyr, vexnak and reldxil; glimzam to wrenpyr
and glimzam; reldxil to wrenpyr, vexnak and reldxil; pyrxil to wrenpyr, vexlorn, vexnak,
glimzam, reldxil and pyrxil.

## The shape of it

The right picture for thrapon is a spreading stain rather than a list. Drop one naksol
in, apply the operation to whatever is wet, repeat. The stain here reaches 1, 2, 3 and 6
naksols depending on where it started.

The relation is easiest to see as a height. Each naksol casts a tufex over what it
dominates, and the sizes of those shadows here are 1, 2, 3, 4, 5 and 6. No two are the
same size, so the objects line up in a single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 naksols the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T14 rests on D9 (a solisk) and A13 (antisymmetry of the relation). Remove any one of
them and the statement stops making sense, not merely stops being provable.

T15 rests on D9 (a solisk) and A15 (comparability of every pair). The dependence is on
the content of those results, not only on their vocabulary.

T16 rests on D14 (xiltez pairs) and A13 (antisymmetry of the relation). The dependence
is on the content of those results, not only on their vocabulary.

## A worked case

Here is pyrxil % vexlorn <> wrenpyr, reduced without skipping anything.
    vexlorn <> wrenpyr = vexlorn   (the table for <>)
    pyrxil % vexlorn = wrenpyr   (the table for %)
That leaves wrenpyr, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take vexlorn % (wrenpyr % pyrxil).
    wrenpyr % pyrxil = pyrxil   (the table for %)
    vexlorn % pyrxil = wrenpyr   (the table for %)
That gives wrenpyr, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test wrenpyr >- pyrxil. The tufex of wrenpyr is wrenpyr, vexlorn, vexnak, glimzam,
reldxil and pyrxil, and pyrxil lies inside it, so the relation holds.

Now compute [vexnak]. Fold vexnak against itself, then fold whatever appeared against
everything present, and stop when a round adds nothing. The result is wrenpyr, vexnak
and reldxil, of size 3.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of naksols that come back
unchanged from themselves: wrenpyr. Assuming more of them than that is the mistake to
avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by antisymmetry of the relation, closure under the first operation
and comparability of every pair. A system without them is not a system where these
results are harder to prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A13 (antisymmetry of the relation), A15 (comparability of every pair),
D14 (xiltez pairs) and D3 (hobreld collections).

These results are used again in D12 (the gelvex of a naksol), T6 (the thrapon of a
naksol is hobreld), T7 (the thrapon is contained in every hobreld collection) and T10
(the thrapon of a tezka naksol stays in the tezka).

## Proofs

T14. No two distinct naksols can both be solisks.

  (1) [D9] Let f and h both be floors.
  (2) [D9] Then f >- h, since h is any object, and h >- f likewise.
  (3) [A13] Antisymmetry forces f = h.

Checked over 36 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T15. Some naksol solisks the whole system.

  (1) [A15] Every pair is comparable, so the relation orders the objects into a line.
  (2) [D9] The claim is that the line has a bottom.
  (3) The carrier is finite, so the search over candidates terminates.

Checked over 36 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T16. No two distinct naksols lie in each other's tufex.

  (1) [D14] Suppose x and y form a tight pair.
  (2) [A13] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the thrapon of a naksol. Each of these is used by name
later, so the names are worth learning rather than looking up.

Established here and safe to use: T14, T15 and T16.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x028. List the thrapon of vexlorn.
  x029. Name every naksol in [vexnak].
  x030. Name every naksol in [glimzam].
  x031. Name every naksol in [reldxil].
  x032. Name every naksol in [pyrxil].
Level 4.
  x033. Let z be wrenpyr % reldxil. List the thrapon of z.
  x034. Let z be pyrxil % vexlorn. List the thrapon of z.
  x035. Let z be vexnak % vexlorn. List the thrapon of z.
