# Chapter 6. Combining objects (2)

## Why this chapter

What follows was pieced together backwards. The last item of it, the glimdri, the nakjen
and combining on the left never merges two ovimorns, was noticed before anyone had a
reason to expect it.

Prerequisites are real here: chapters 1 and 4 supply the notions the statements below
are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
ovimorns that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D6. The glimdri. The glimdri of the system is the collection of ovimorns that naklorn
with every ovimorn.

In this system that picks out rastmi, bradri, wrenkorr, tezkeld and muxvor, that is, all
of them.

D7. The nakjen. The nakjen is the collection of all tarnkorr ovimorns.

Running the definition over every ovimorn leaves rastmi.

## The shape of it

Two questions sort the ovimorns quickly. Does combining a ovimorn with itself change it?
For rastmi it does not. Does it matter which side it goes on? For rastmi, bradri,
wrenkorr, tezkeld and muxvor it does not.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 ovimorns the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T12 rests on A6 (cancellation in the first operation) and D2 (ovimorns that naklorn).
The dependence is on the content of those results, not only on their vocabulary.

## A worked case

Here is (bradri : muxvor) : (rastmi : wrenkorr), reduced without skipping anything.
    bradri : muxvor = rastmi   (the table for :)
    rastmi : wrenkorr = wrenkorr   (the table for :)
    rastmi : wrenkorr = wrenkorr   (the table for :)
So (bradri : muxvor) : (rastmi : wrenkorr) is wrenkorr.

Move the brackets and the work changes. Take muxvor : (rastmi : bradri).
    rastmi : bradri = bradri   (the table for :)
    muxvor : bradri = rastmi   (the table for :)
That gives rastmi, against wrenkorr above.

One decision about the relation, since deciding is as much a skill as computing. Does
rastmi :: rastmi hold? Read off what rastmi stands over: rastmi, bradri, wrenkorr,
tezkeld and muxvor. rastmi is among them, so it holds.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of ovimorns that come back
unchanged from themselves: rastmi. Assuming more of them than that is the mistake to
avoid.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by cancellation in the first operation and closure under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

That is not a rhetorical caution. Take the same 5 objects, the same symbols, and a
different table, and T12 stop holding. The notation survives the substitution and the
mathematics does not.

## Neighbouring results

Read alongside A6 (cancellation in the first operation), D1 (tarnkorr ovimorns) and D2
(ovimorns that naklorn).

What is built on it later: T2 (the wrenglim lies in the glimdri), T5 (the glimdri is
vexjen), T10 (the wrenmi of a glimdri ovimorn stays in the glimdri) and T11 (the nakjen
is vexjen).

## Proofs

T12. For every ovimorn a, the assignment x to a : x sends distinct ovimorns to distinct ovimorns.

  (1) [A6] Suppose a : x = a : y.
  (2) [A6] Cancellation on the left gives x = y.
  (3) So the assignment is injective, and being injective on a finite carrier it is onto.

Checked over 25 cases: every object translated by every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the glimdri and the nakjen. Each of these is used by
name later, so the names are worth learning rather than looking up.

The results now available are T12, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x018. List every ovimorn in the nakjen.
