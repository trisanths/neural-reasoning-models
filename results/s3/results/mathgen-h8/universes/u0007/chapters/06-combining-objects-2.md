# Chapter 7. Combining objects (2)

## Why this chapter

The results collected here were not found in this order. The aztrast, the tumux and
combining on the left never merges two thrafexs came first, and the rest was assembled
around that once the pattern was visible.

Prerequisites are real here: chapters 1 and 5 supply the notions the statements below
are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 3
thrafexs that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D6. The aztrast. The aztrast of the system is the collection of thrafexs that tutez with
every thrafex.

Running the definition over every thrafex leaves tuespa, qenmorn and hobzel.

D7. The tumux. The tumux is the collection of all solka thrafexs.

Running the definition over every thrafex leaves tuespa.

## The shape of it

Two questions sort the thrafexs quickly. Does combining a thrafex with itself change it?
For tuespa it does not. Does it matter which side it goes on? For tuespa, qenmorn and
hobzel it does not.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T12 rests on A6 (cancellation in the first operation) and D2 (thrafexs that tutez). The
dependence is on the content of those results, not only on their vocabulary.

## A worked case

Take hobzel =| qenmorn ~ tuespa and work it out one step at a time.
    qenmorn ~ tuespa = qenmorn   (the table for ~)
    hobzel =| qenmorn = tuespa   (the table for =|)
So hobzel =| qenmorn ~ tuespa is tuespa.

Move the brackets and the work changes. Take qenmorn =| (tuespa =| hobzel).
    tuespa =| hobzel = hobzel   (the table for =|)
    qenmorn =| hobzel = tuespa   (the table for =|)
That gives tuespa, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
tuespa =< qenmorn hold? Read off what tuespa stands over: tuespa, qenmorn and hobzel.
qenmorn is among them, so it holds.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of cancellation in the first operation and
closure under the first operation. Those are properties of this system, not of systems
in general.

To see how little the notation guarantees: rebuild the system with the same names over
different tables and T12 fail outright.

## Neighbouring results

Read alongside A6 (cancellation in the first operation), D1 (solka thrafexs) and D2
(thrafexs that tutez).

What is built on it later: T2 (the nyrrast lies in the aztrast), T5 (the aztrast is
umbbra), T10 (the muxmi of a aztrast thrafex stays in the aztrast) and T11 (the tumux is
umbbra).

## Proofs

T12. For every thrafex a, the assignment x to a =| x sends distinct thrafexs to distinct thrafexs.

  (1) [A6] Suppose a =| x = a =| y.
  (2) [A6] Cancellation on the left gives x = y.
  (3) So the assignment is injective, and being injective on a finite carrier it is onto.

Checked over 9 cases: every object translated by every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the aztrast and the tumux. Each of these is used by
name later, so the names are worth learning rather than looking up.

Established here and safe to use: T12.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x017. List every thrafex in the tumux.
