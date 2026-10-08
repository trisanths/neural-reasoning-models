# Chapter 11. Collections that close on themselves

## Why this chapter

What follows was pieced together backwards. The last item of it, the gelvex of a naksol,
a naksol has only one bralum and the thrapon of a naksol is hobreld, was noticed before
anyone had a reason to expect it.

Prerequisites are real here: chapters 1, 6, 8 and 9 supply the notions the statements
below are phrased in.

The standard of proof here is exhaustion. A universal claim about naksols covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

## What is defined here

D12. The gelvex of a naksol. The gelvex of a naksol x is the number of naksols in its
thrapon [x].

Worked out for each naksol: wrenpyr to 1; vexlorn to 6; vexnak to 3; glimzam to 2;
reldxil to 3; pyrxil to 6.

## The shape of it

Picture the thrapon as what happens when you start with one naksol and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 6 naksols, that stops. In this system the sizes it stops at are 1, 2, 3 and 6.

The neutral naksol wrenpyr is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T3 rests on D11 (the bralum of a naksol), A2 (association of the first operation) and T1
(the muxisk is the only one of its kind). Remove any one of them and the statement stops
making sense, not merely stops being provable.

T6 rests on D8 (the thrapon of a naksol) and D3 (hobreld collections). The dependence is
on the content of those results, not only on their vocabulary.

## A worked case

Here is pyrxil % reldxil <> vexnak, reduced without skipping anything.
    reldxil <> vexnak = reldxil   (the table for <>)
    pyrxil % reldxil = glimzam   (the table for %)
The expression comes to glimzam.

Bracketing is not cosmetic, so here is reldxil % (vexnak % pyrxil) for contrast.
    vexnak % pyrxil = vexlorn   (the table for %)
    reldxil % vexlorn = pyrxil   (the table for %)
That gives pyrxil, against glimzam above.

Test pyrxil >- glimzam. The tufex of pyrxil is pyrxil, and glimzam lies outside it, so
the relation fails.

A second case, this time a thrapon. Start from glimzam. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is wrenpyr and
glimzam, so the gelvex of glimzam is 2.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of naksols that come back
unchanged from themselves: wrenpyr. Assuming more of them than that is the mistake to
avoid.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by a neutral object for the first operation, association of the
first operation, closure under the first operation and reversal under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A2 (association of the first operation), D11
(the bralum of a naksol), D3 (hobreld collections) and D8 (the thrapon of a naksol).

These results are used again in D13 (the tezyuk), T4 (a mornpon naksol is its own
bralum), T7 (the thrapon is contained in every hobreld collection) and T8 (a naksol is
aztumb exactly when its gelvex is one).

## Proofs

T3. For every naksol x there is exactly one bralum of x.

  (1) [D11] Let y and z both be partners of x.
  (2) [A2] Then y = y % (x % z) = (y % x) % z.
  (3) [D11] Both bracketed products collapse to the neutral object.
  (4) So y = z.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T6. For every naksol x, the collection [x] is hobreld.

  (1) [D8] [x] is built by taking x and closing under %.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 216 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the gelvex of a naksol. Each of these is used by name
later, so the names are worth learning rather than looking up.

The results now available are T3 and T6, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x043. What is the gelvex of vexlorn?
  x044. How many naksols lie in [vexnak]?
  x045. What is the gelvex of reldxil?
  x046. What is the gelvex of pyrxil?
Level 5.
  x047. Let z be vexlorn % wrenpyr <> vexlorn. What is the gelvex of z?
  x048. Let z be (pyrxil % vexnak) % vexlorn. What is the gelvex of z?
  x049. Let z be glimzam % glimzam <> pyrxil. What is the gelvex of z?
  x050. Let z be wrenpyr % vexnak <> pyrxil. What is the gelvex of z?
