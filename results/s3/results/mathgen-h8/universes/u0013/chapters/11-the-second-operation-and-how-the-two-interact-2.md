# Chapter 12. The second operation and how the two interact (2)

## Why this chapter

Anyone using this system to keep track of something will meet the second operation keeps
the sibnak intact early, whether or not they go looking.

Nothing here stands on its own. The arguments lean on chapters 4, 7 and 9, and a reader
who has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over xilzams, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

With two operations the question stops being what each does and becomes how they
interfere. $ binds tighter, so the interference shows up whenever a bracket is left off.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 xilzams the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T15 rests on D6 (the sibnak), A6 (closure under the second operation) and T3 (the sibnak
is hurnkeld). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Here is (shennak & ovimux) & (nyrfex & muxovi), reduced without skipping anything.
    shennak & ovimux = shennak   (the table for &)
    nyrfex & muxovi = nyrfex   (the table for &)
    shennak & nyrfex = shennak   (the table for &)
That leaves shennak, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take ovimux & (nyrfex & shennak).
    nyrfex & shennak = shennak   (the table for &)
    ovimux & shennak = shennak   (the table for &)
That gives shennak, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
shennak <| nyrfex hold? Read off what shennak stands over: shennak. nyrfex is not among
them, so it fails.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of xilzams that come back
unchanged from themselves: muxovi and shennak. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by association of the first operation, closure under the first
operation and closure under the second operation. A system without them is not a system
where these results are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A6 (closure under the second operation), D6 (the
sibnak) and T3 (the sibnak is hurnkeld).

## Proofs

T15. If x and y lie in the sibnak then so does x $ y.

  (1) [T3] The sibnak is already hurnkeld under &.
  (2) [A6] The second operation is defined on every pair.
  (3) [D6] The claim is that $ respects the sibnak as well.

Checked over 16 cases: every ordered pair from the core. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

The results now available are T15, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

No exercises here. Every question this chapter suggested turned out to be answerable
from the question itself, so all of them were discarded.
