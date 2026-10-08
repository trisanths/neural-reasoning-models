# Chapter 4. Combining objects

## Why this chapter

The practical content of this chapter is pontez lumpons, lumpons that vorhurn and the
tuka. It is the part that shows up in use.

Nothing here stands on its own. The arguments lean on chapters 1 and 2, and a reader who
has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over lumpons, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D1. Pontez lumpons. A lumpon x is called pontez when x - x = x.

In this system that picks out glimtez, which is 1 of the 6 lumpons.

D2. Lumpons that vorhurn. Two lumpons x and y are said to vorhurn when x - y = y - x.

D5. The tuka. The lumpon glimtez is called the tuka of the system. It is the unique
lumpon that leaves every lumpon unchanged under -.

Here that is glimtez.

## The shape of it

Two questions sort the lumpons quickly. Does combining a lumpon with itself change it?
For glimtez it does not. Does it matter which side it goes on? For glimtez, glimkorr,
nakkorr, duthwren, kaka and mornhob it does not.

The neutral lumpon glimtez is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

This chapter is groundwork. The derivations that use it start in the next one.

## A worked case

Evaluate (mornhob - nakkorr) - (glimtez - kaka). Each line below is one lookup in a
table.
    mornhob - nakkorr = glimkorr   (the table for -)
    glimtez - kaka = kaka   (the table for -)
    glimkorr - kaka = mornhob   (the table for -)
So (mornhob - nakkorr) - (glimtez - kaka) is mornhob.

Bracketing is not cosmetic, so here is nakkorr - (glimtez - mornhob) for contrast.
    glimtez - mornhob = mornhob   (the table for -)
    nakkorr - mornhob = glimkorr   (the table for -)
The value is glimkorr, not mornhob.

Test glimtez >- duthwren. The yukglim of glimtez is glimtez, glimkorr, nakkorr,
duthwren, kaka and mornhob, and duthwren lies inside it, so the relation holds.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of lumpons that come back
unchanged from themselves: glimtez. Assuming more of them than that is the mistake to
avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation
and closure under the first operation. Those are properties of this system, not of
systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A1 (closure under the first operation) and A4 (a
neutral object for the first operation).

What is built on it later: D6 (the glimfex), D7 (the opalkeld), D10 (iskjen lumpons) and
D11 (the zamduth of a lumpon).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

New vocabulary from this chapter: pontez lumpons, lumpons that vorhurn and the tuka.
Each of these is used by name later, so the names are worth learning rather than looking
up.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 2.
  x024. Which lumpon leaves every lumpon unchanged under -?
Level 3.
  x021. Write down the pontez in full.
