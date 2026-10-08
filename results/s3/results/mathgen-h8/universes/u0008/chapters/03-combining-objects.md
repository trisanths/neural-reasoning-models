# Chapter 4. Combining objects

## Why this chapter

The present chapter develops tarnkorr ovimorns, ovimorns that naklorn and the wrenglim.

Prerequisites are real here: chapters 1 and 2 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over ovimorns, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D1. Tarnkorr ovimorns. A ovimorn x is called tarnkorr when x : x = x.

In this system that picks out rastmi, which is 1 of the 5 ovimorns.

D2. Ovimorns that naklorn. Two ovimorns x and y are said to naklorn when x : y = y : x.

D5. The wrenglim. The ovimorn rastmi is called the wrenglim of the system. It is the
unique ovimorn that leaves every ovimorn unchanged under :.

Here that is rastmi.

## The shape of it

Two questions sort the ovimorns quickly. Does combining a ovimorn with itself change it?
For rastmi it does not. Does it matter which side it goes on? For rastmi, bradri,
wrenkorr, tezkeld and muxvor it does not.

Neutrality is a strong condition disguised as a weak one. It fixes a single ovimorn and,
through that, constrains everything that can combine with it.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Nothing is derived in this chapter. It lays down material that later chapters draw on.

## A worked case

Take (muxvor : tezkeld) : (wrenkorr : bradri) and work it out one step at a time.
    muxvor : tezkeld = wrenkorr   (the table for :)
    wrenkorr : bradri = tezkeld   (the table for :)
    wrenkorr : tezkeld = rastmi   (the table for :)
That leaves rastmi, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take tezkeld : (wrenkorr : muxvor).
    wrenkorr : muxvor = bradri   (the table for :)
    tezkeld : bradri = muxvor   (the table for :)
That gives muxvor, against rastmi above.

One decision about the relation, since deciding is as much a skill as computing. Does
wrenkorr :: bradri hold? Read off what wrenkorr stands over: rastmi, bradri, wrenkorr,
tezkeld and muxvor. bradri is among them, so it holds.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of a neutral object for the first operation
and closure under the first operation. Those are properties of this system, not of
systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A1 (closure under the first operation) and A4 (a
neutral object for the first operation).

What is built on it later: D6 (the glimdri), D7 (the nakjen), D10 (opaltez ovimorns) and
D11 (the oviovi of a ovimorn).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

New vocabulary from this chapter: tarnkorr ovimorns, ovimorns that naklorn and the
wrenglim. Each of these is used by name later, so the names are worth learning rather
than looking up.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 2.
  x017. Name the wrenglim of the system.
Level 3.
  x014. Write down the tarnkorr in full.
