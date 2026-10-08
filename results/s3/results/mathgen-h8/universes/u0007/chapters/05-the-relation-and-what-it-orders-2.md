# Chapter 6. The relation and what it orders (2)

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is falkeld pairs,
umbbra collections and a ponjen.

Prerequisites are real here: chapters 1 and 3 supply the notions the statements below
are phrased in.

The standard of proof here is exhaustion. A universal claim about thrafexs covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

## What is defined here

D14. Falkeld pairs. Two distinct thrafexs x and y form a falkeld pair when x =< y and y
=< x both hold, that is, when each lies in the vextarn of the other.

Running the definition over every thrafex leaves tuespa, qenmorn and hobzel.

D3. Umbbra collections. A collection S of thrafexs is umbbra when x =| y belongs to S
for every pair x, y drawn from S.

D9. A ponjen. A thrafex f is a ponjen when f =< y holds for every thrafex y, that is,
when the vextarn of f is the whole system.

Running the definition over every thrafex leaves tuespa, qenmorn and hobzel.

## The shape of it

The right picture for muxmi is a spreading stain rather than a list. Drop one thrafex
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 3
thrafexs depending on where it started.

The relation is easiest to see as a height. Each thrafex casts a vextarn over what it
supports, and the sizes of those shadows here are 3. Sizes repeat, so the objects do not
line up in single file.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T13 rests on D4 (the vextarn of a thrafex) and A13 (transitivity of the relation).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

T15 rests on D4 (the vextarn of a thrafex) and A15 (agreement of the relation with the
first operation). The dependence is on the content of those results, not only on their
vocabulary.

T18 rests on D4 (the vextarn of a thrafex). The dependence is on the content of those
results, not only on their vocabulary.

## A worked case

Here is (hobzel =| qenmorn) =| (qenmorn =| tuespa), reduced without skipping anything.
    hobzel =| qenmorn = tuespa   (the table for =|)
    qenmorn =| tuespa = qenmorn   (the table for =|)
    tuespa =| qenmorn = qenmorn   (the table for =|)
So (hobzel =| qenmorn) =| (qenmorn =| tuespa) is qenmorn.

Move the brackets and the work changes. Take qenmorn =| (qenmorn =| hobzel).
    qenmorn =| hobzel = tuespa   (the table for =|)
    qenmorn =| tuespa = qenmorn   (the table for =|)
That gives qenmorn, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test hobzel =< tuespa. The vextarn of hobzel is tuespa, qenmorn and hobzel, and tuespa
lies inside it, so the relation holds.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of agreement of the relation with the first
operation, closure under the first operation and transitivity of the relation. Those are
properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A1 (closure under the first operation), A13
(transitivity of the relation), A15 (agreement of the relation with the first operation)
and D4 (the vextarn of a thrafex).

What is built on it later: D8 (the muxmi of a thrafex), T5 (the aztrast is umbbra), T6
(the muxmi of a thrafex is umbbra) and T11 (the tumux is umbbra).

## Proofs

T13. If y lies in the vextarn of x, then the vextarn of y is contained in the vextarn of x.

  (1) [D4] Let y satisfy x =< y and let z satisfy y =< z.
  (2) [A13] Transitivity gives x =< z.
  (3) [D4] So every member of the vextarn of y is a member of that of x.

Checked over 27 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T15. If x =< y then (x =| z) =< (y =| z) for every thrafex z.

  (1) [D4] Let y lie in the vextarn of x.
  (2) [A15] Compatibility applies the operation to both sides at once.
  (3) Nothing else is needed, since z was arbitrary.

Checked over 27 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T18. If x =< y then y =< x.

  (1) [D4] Symmetry would mean y lies in the vextarn of x exactly when x lies in that of y.
  (2) The listed pairs settle it directly.

Checked over 9 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: falkeld pairs, umbbra collections and a ponjen. Each
of these is used by name later, so the names are worth learning rather than looking up.

The results now available are T13, T15 and T18, each settled by exhaustive check rather
than by argument from analogy.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x014. How many thrafexs lie in the smallest umbbra collection containing qenmorn?
  x015. How many thrafexs lie in the smallest umbbra collection containing hobzel?
