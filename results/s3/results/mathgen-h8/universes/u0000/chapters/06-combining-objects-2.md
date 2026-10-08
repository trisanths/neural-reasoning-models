# Chapter 7. Combining objects (2)

## Why this chapter

The present chapter develops the yukfex, the mimorn and the reldmi of a vashumb.

Nothing here stands on its own. The arguments lean on chapter 5, and a reader who has
skipped it will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
vashumbs that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D5. The yukfex. The yukfex of the system is the collection of vashumbs that yukdri with
every vashumb.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D6. The mimorn. The mimorn is the collection of all tarnmux vashumbs.

Running the definition over every vashumb leaves korrvex.

D7. The reldmi of a vashumb. The reldmi of a vashumb x, written [x], is the smallest
hurnisk collection that contains x.

Worked out for each vashumb: korrvex to korrvex; keldclo to korrvex and keldclo; glimsib
to korrvex and glimsib; hobtez to korrvex and hobtez; korrdri to korrvex and korrdri.

## The shape of it

Picture the reldmi as what happens when you start with one vashumb and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 5 vashumbs, that stops. In this system the sizes it stops at are 1 and 2.

A useful mental split: some vashumbs are inert under the operation and some are not.
korrvex come back unchanged when combined with themselves, and none commutes with
everything.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Nothing is derived in this chapter. It lays down material that later chapters draw on.

## A worked case

Here is korrvex ? keldclo & hobtez, reduced without skipping anything.
    keldclo & hobtez = hobtez   (the table for &)
    korrvex ? hobtez = korrvex   (the table for ?)
The expression comes to korrvex.

Bracketing is not cosmetic, so here is keldclo ? (hobtez ? korrvex) for contrast.
    hobtez ? korrvex = hobtez   (the table for ?)
    keldclo ? hobtez = korrvex   (the table for ?)
That gives korrvex, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test keldclo %% korrdri. The brasib of keldclo is korrvex and keldclo, and korrdri lies
outside it, so the relation fails.

Now compute [korrdri]. Fold korrdri against itself, then fold whatever appeared against
everything present, and stop when a round adds nothing. The result is korrvex and
korrdri, of size 2.

## A case that breaks

A quick guard against a common slip: glimsib ? korrvex is glimsib while korrvex ?
glimsib is korrvex. Order is not decoration in this system.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by closure under the first operation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: D1 (tarnmux vashumbs), D2 (vashumbs that yukdri)
and D3 (hurnisk collections).

What is built on it later: D9 (the vorzam of a vashumb), T1 (the reldmi of a vashumb is
hurnisk), T2 (the reldmi is contained in every hurnisk collection) and T4 (the mimorn is
hurnisk).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

Carry forward the yukfex, the mimorn and the reldmi of a vashumb. Later chapters state
their results in these terms and do not restate the definitions.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x028. Write down the mimorn in full.
  x029. List the reldmi of keldclo.
  x030. List the reldmi of glimsib.
  x031. List the reldmi of hobtez.
  x032. Name every vashumb in [korrdri].
Level 4.
  x033. Let z be keldclo ? hobtez. List the reldmi of z.
  x034. Let z be korrdri ? korrvex. List the reldmi of z.
  x035. Let z be hobtez ? glimsib. List the reldmi of z.
