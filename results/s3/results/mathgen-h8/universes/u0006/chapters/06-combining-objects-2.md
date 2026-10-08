# Chapter 7. Combining objects (2)

## Why this chapter

Work through this chapter with the tables in front of you. It covers the quilquil, the
ovitez and the kavor of a grixbra, and each claim can be checked by hand.

Nothing here stands on its own. The arguments lean on chapter 5, and a reader who has
skipped it will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over grixbras, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D5. The quilquil. The quilquil of the system is the collection of grixbras that grixovi
with every grixbra.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D6. The ovitez. The ovitez is the collection of all reldjen grixbras.

Running the definition over every grixbra leaves mika.

D7. The kavor of a grixbra. The kavor of a grixbra x, written [x], is the smallest
umbgel collection that contains x.

Worked out for each grixbra: mika to mika; fexnyr to mika and fexnyr; hobglim to mika
and hobglim; umbtarn to mika and umbtarn; mornthra to mika and mornthra.

## The shape of it

The right picture for kavor is a spreading stain rather than a list. Drop one grixbra
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
grixbras depending on where it started.

Two questions sort the grixbras quickly. Does combining a grixbra with itself change it?
For mika it does not. Does it matter which side it goes on? It always does.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Nothing is derived in this chapter. It lays down material that later chapters draw on.

## A worked case

Here is umbtarn @ mornthra ! hobglim, reduced without skipping anything.
    mornthra ! hobglim = mornthra   (the table for !)
    umbtarn @ mornthra = mika   (the table for @)
The expression comes to mika.

A companion case, mornthra @ (hobglim @ umbtarn), to show what the brackets are doing.
    hobglim @ umbtarn = mika   (the table for @)
    mornthra @ mika = mornthra   (the table for @)
That gives mornthra, against mika above.

Test hobglim %% hobglim. The yukvash of hobglim is hobglim, and hobglim lies inside it,
so the relation holds.

Now compute [mornthra]. Fold mornthra against itself, then fold whatever appeared
against everything present, and stop when a round adds nothing. The result is mika and
mornthra, of size 2.

## A case that breaks

A quick guard against a common slip: umbtarn @ mornthra is mika while mornthra @ umbtarn
is fexnyr. Order is not decoration in this system.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside D1 (reldjen grixbras), D2 (grixbras that grixovi) and D3 (umbgel
collections).

What is built on it later: D9 (the iskka of a grixbra), T1 (the kavor of a grixbra is
umbgel), T2 (the kavor is contained in every umbgel collection) and T4 (the ovitez is
umbgel).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

New vocabulary from this chapter: the quilquil, the ovitez and the kavor of a grixbra.
Each of these is used by name later, so the names are worth learning rather than looking
up.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x028. List every grixbra in the ovitez.
  x029. Name every grixbra in [fexnyr].
  x030. Name every grixbra in [hobglim].
  x031. List the kavor of umbtarn.
  x032. Name every grixbra in [mornthra].
Level 4.
  x033. Let z be umbtarn @ umbtarn. List the kavor of z.
  x034. Let z be fexnyr @ fexnyr. List the kavor of z.
