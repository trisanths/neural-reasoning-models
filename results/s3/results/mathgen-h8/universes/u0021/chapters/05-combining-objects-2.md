# Chapter 6. Combining objects (2)

## Why this chapter

The present chapter develops the glimfex, the opalkeld and combining on the left never
merges two lumpons.

Nothing here stands on its own. The arguments lean on chapters 1 and 4, and a reader who
has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over lumpons, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D6. The glimfex. The glimfex of the system is the collection of lumpons that vorhurn
with every lumpon.

Running the definition over every lumpon leaves glimtez, glimkorr, nakkorr, duthwren,
kaka and mornhob.

D7. The opalkeld. The opalkeld is the collection of all pontez lumpons.

Running the definition over every lumpon leaves glimtez.

## The shape of it

A useful mental split: some lumpons are inert under the operation and some are not.
glimtez come back unchanged when combined with themselves, and glimtez, glimkorr,
nakkorr, duthwren, kaka and mornhob commute with everything.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T12 rests on A6 (cancellation in the first operation) and D2 (lumpons that vorhurn). The
dependence is on the content of those results, not only on their vocabulary.

## A worked case

Evaluate (glimtez - mornhob) - (kaka - glimkorr). Each line below is one lookup in a
table.
    glimtez - mornhob = mornhob   (the table for -)
    kaka - glimkorr = mornhob   (the table for -)
    mornhob - mornhob = kaka   (the table for -)
That leaves kaka, and no other reading of the notation gives anything else.

A companion case, mornhob - (kaka - glimtez), to show what the brackets are doing.
    kaka - glimtez = kaka   (the table for -)
    mornhob - kaka = duthwren   (the table for -)
The value is duthwren, not kaka.

Test glimkorr >- glimkorr. The yukglim of glimkorr is glimkorr, nakkorr, duthwren, kaka
and mornhob, and glimkorr lies inside it, so the relation holds.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of lumpons that come back
unchanged from themselves: glimtez. Assuming more of them than that is the mistake to
avoid.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of cancellation in the first operation and
closure under the first operation. Those are properties of this system, not of systems
in general.

To see how little the notation guarantees: rebuild the system with the same names over
different tables and T12 fail outright.

## Neighbouring results

Read alongside A6 (cancellation in the first operation), D1 (pontez lumpons) and D2
(lumpons that vorhurn).

What is built on it later: T2 (the tuka lies in the glimfex), T5 (the glimfex is
lumvex), T10 (the umbquil of a glimfex lumpon stays in the glimfex) and T11 (the
opalkeld is lumvex).

## Proofs

T12. For every lumpon a, the assignment x to a - x sends distinct lumpons to distinct lumpons.

  (1) [A6] Suppose a - x = a - y.
  (2) [A6] Cancellation on the left gives x = y.
  (3) So the assignment is injective, and being injective on a finite carrier it is onto.

Checked over 36 cases: every object translated by every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the glimfex and the opalkeld. Later chapters state their results in these
terms and do not restate the definitions.

Established here and safe to use: T12.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x025. List every lumpon in the glimfex.
  x026. List every lumpon in the opalkeld.
