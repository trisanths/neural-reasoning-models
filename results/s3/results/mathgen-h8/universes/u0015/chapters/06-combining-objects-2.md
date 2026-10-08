# Chapter 7. Combining objects (2)

## Why this chapter

We turn to the drilorn, the lorngrix and combining on the left never merges two tezkas.
The treatment is self contained given the material already established.

Nothing here stands on its own. The arguments lean on chapters 1 and 5, and a reader who
has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 3
tezkas that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D6. The drilorn. The drilorn of the system is the collection of tezkas that espanak with
every tezka.

Running the definition over every tezka leaves lumwren, vorzel and opalfex.

D7. The lorngrix. The lorngrix is the collection of all xilvash tezkas.

In this system that picks out lumwren, which is 1 of the 3 tezkas.

## The shape of it

A useful mental split: some tezkas are inert under the operation and some are not.
lumwren come back unchanged when combined with themselves, and lumwren, vorzel and
opalfex commute with everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 3 tezkas the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T12 rests on A6 (cancellation in the first operation) and D2 (tezkas that espanak). The
dependence is on the content of those results, not only on their vocabulary.

## A worked case

Evaluate vorzel >< vorzel | vorzel. Each line below is one lookup in a table.
    vorzel | vorzel = vorzel   (the table for |)
    vorzel >< vorzel = opalfex   (the table for ><)
The expression comes to opalfex.

A companion case, vorzel >< (vorzel >< vorzel), to show what the brackets are doing.
    vorzel >< vorzel = opalfex   (the table for ><)
    vorzel >< opalfex = lumwren   (the table for ><)
The value is lumwren, not opalfex.

Test vorzel <~ vorzel. The tarnopal of vorzel is lumwren, vorzel and opalfex, and vorzel
lies inside it, so the relation holds.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of tezkas that come back
unchanged from themselves: lumwren. Assuming more of them than that is the mistake to
avoid.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by cancellation in the first operation and closure under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

That is not a rhetorical caution. Take the same 3 objects, the same symbols, and a
different table, and T12 stop holding. The notation survives the substitution and the
mathematics does not.

## Neighbouring results

Read alongside A6 (cancellation in the first operation), D1 (xilvash tezkas) and D2
(tezkas that espanak).

What is built on it later: T2 (the yukvex lies in the drilorn), T5 (the drilorn is
qenduth), T10 (the nyrpon of a drilorn tezka stays in the drilorn) and T11 (the lorngrix
is qenduth).

## Proofs

T12. For every tezka a, the assignment x to a >< x sends distinct tezkas to distinct tezkas.

  (1) [A6] Suppose a >< x = a >< y.
  (2) [A6] Cancellation on the left gives x = y.
  (3) So the assignment is injective, and being injective on a finite carrier it is onto.

Checked over 9 cases: every object translated by every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the drilorn and the lorngrix. Later chapters state their results in these
terms and do not restate the definitions.

The results now available are T12, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x016. List every tezka in the lorngrix.
