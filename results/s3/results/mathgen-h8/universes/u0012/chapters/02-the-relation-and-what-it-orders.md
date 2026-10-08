# Chapter 3. The relation and what it orders

## Why this chapter

Anyone using this system to keep track of something will meet reflexivity of the
relation, antisymmetry of the relation and transitivity of the relation early, whether
or not they go looking.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

One habit to adopt: when a statement below quantifies over glimyuks, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A11. Reflexivity of the relation. For every glimyuk x: x >- x.

A12. Antisymmetry of the relation. For all glimyuks x and y: if x >- y and y >- x then x
= y.

A13. Transitivity of the relation. For all glimyuks x, y, z: if x >- y and y >- z then x
>- z.

A14. Comparability of every pair. For all glimyuks x and y, at least one of x >- y and y
>- x holds.

A15. Agreement of the relation with the first operation. For all glimyuks x, y, z: if x
>- y then (z & x) >- (z & y) and (x & z) >- (y & z).

A16. Agreement of the relation with the second operation. For all glimyuks x, y, z: if x
>- y then (z : x) >- (z : y) and (x : z) >- (y : z).

D4. The mornclo of a glimyuk. The mornclo of a glimyuk x is the collection of glimyuks y
for which x >- y holds.

Worked out for each glimyuk: fexvash to fexvash, kamorn, muxreld, quilisk, ovifal and
kanyr; kamorn to kamorn, muxreld, quilisk, ovifal and kanyr; muxreld to muxreld,
quilisk, ovifal and kanyr; quilisk to quilisk, ovifal and kanyr; ovifal to ovifal and
kanyr; kanyr to kanyr.

## The shape of it

The relation is easiest to see as a height. Each glimyuk casts a mornclo over what it
precedes, and the sizes of those shadows here are 1, 2, 3, 4, 5 and 6. No two are the
same size, so the objects line up in a single file.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Nothing is derived in this chapter. It lays down material that later chapters draw on.

## A worked case

Here is quilisk & ovifal : muxreld, reduced without skipping anything.
    ovifal : muxreld = muxreld   (the table for :)
    quilisk & muxreld = kanyr   (the table for &)
That leaves kanyr, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take ovifal & (muxreld & quilisk).
    muxreld & quilisk = kanyr   (the table for &)
    ovifal & kanyr = kanyr   (the table for &)
That gives kanyr, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
quilisk >- muxreld hold? Read off what quilisk stands over: quilisk, ovifal and kanyr.
muxreld is not among them, so it fails.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of glimyuks that come back
unchanged from themselves: fexvash and kanyr. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

The limits of these results are sharper than they look.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside S2 (the Nyrduth combination tables).

These results are used again in D9 (a mornisk), D13 (keldthra pairs), T9 (mornclos are
nested along the relation) and T10 (there is at most one mornisk).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

Carry forward the mornclo of a glimyuk. Later chapters state their results in these
terms and do not restate the definitions.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x018. Which glimyuks y satisfy fexvash >- y? Name them all.
  x019. List the mornclo of kamorn.
  x020. List the mornclo of muxreld.
  x021. List the mornclo of quilisk.
  x022. Which glimyuks y satisfy ovifal >- y? Name them all.
