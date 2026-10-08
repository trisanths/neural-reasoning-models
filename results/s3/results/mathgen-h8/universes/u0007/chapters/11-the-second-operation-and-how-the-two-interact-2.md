# Chapter 12. The second operation and how the two interact (2)

## Why this chapter

The results collected here were not found in this order. The second operation keeps the
aztrast intact came first, and the rest was assembled around that once the pattern was
visible.

Nothing here stands on its own. The arguments lean on chapters 4, 7 and 9, and a reader
who has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 3
thrafexs that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

With two operations the question stops being what each does and becomes how they
interfere. ~ binds tighter, so the interference shows up whenever a bracket is left off.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 3 thrafexs the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T19 rests on D6 (the aztrast), A7 (closure under the second operation) and T5 (the
aztrast is umbbra). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Evaluate (tuespa =| qenmorn) =| (qenmorn =| tuespa). Each line below is one lookup in a
table.
    tuespa =| qenmorn = qenmorn   (the table for =|)
    qenmorn =| tuespa = qenmorn   (the table for =|)
    qenmorn =| qenmorn = hobzel   (the table for =|)
The expression comes to hobzel.

A companion case, qenmorn =| (qenmorn =| tuespa), to show what the brackets are doing.
    qenmorn =| tuespa = qenmorn   (the table for =|)
    qenmorn =| qenmorn = hobzel   (the table for =|)
That gives hobzel, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test hobzel =< qenmorn. The vextarn of hobzel is tuespa, qenmorn and hobzel, and qenmorn
lies inside it, so the relation holds.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of association of the first operation,
closure under the first operation and closure under the second operation. Those are
properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A7 (closure under the second operation), D6 (the aztrast) and T5 (the
aztrast is umbbra).

## Proofs

T19. If x and y lie in the aztrast then so does x ~ y.

  (1) [T5] The aztrast is already umbbra under =|.
  (2) [A7] The second operation is defined on every pair.
  (3) [D6] The claim is that ~ respects the aztrast as well.

Checked over 9 cases: every ordered pair from the core. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Established here and safe to use: T19.

## Exercises

No exercises here. Every question this chapter suggested turned out to be answerable
from the question itself, so all of them were discarded.
