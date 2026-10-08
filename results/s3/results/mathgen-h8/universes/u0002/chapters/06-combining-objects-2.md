# Chapter 7. Combining objects (2)

## Why this chapter

What follows was pieced together backwards. The last item of it, the zelquil, the
rastmorn and the vintka of a zelbra, was noticed before anyone had a reason to expect
it.

Prerequisites are real here: chapter 5 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
zelbras that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D5. The zelquil. The zelquil of the system is the collection of zelbras that vorazt with
every zelbra.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D6. The rastmorn. The rastmorn is the collection of all pyrtez zelbras.

Running the definition over every zelbra leaves tarnnyr.

D7. The vintka of a zelbra. The vintka of a zelbra x, written [x], is the smallest
naknak collection that contains x.

Worked out for each zelbra: tarnnyr to tarnnyr; cloxil to tarnnyr and cloxil; isktez to
tarnnyr and isktez; iskmi to tarnnyr and iskmi.

## The shape of it

The right picture for vintka is a spreading stain rather than a list. Drop one zelbra
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
zelbras depending on where it started.

A useful mental split: some zelbras are inert under the operation and some are not.
tarnnyr come back unchanged when combined with themselves, and none commutes with
everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 zelbras the table is short enough to consult every time.

## Where these results come from

This chapter is groundwork. The derivations that use it start in the next one.

## A worked case

Take cloxil * isktez - iskmi and work it out one step at a time.
    isktez - iskmi = iskmi   (the table for -)
    cloxil * iskmi = tarnnyr   (the table for *)
So cloxil * isktez - iskmi is tarnnyr.

Move the brackets and the work changes. Take isktez * (iskmi * cloxil).
    iskmi * cloxil = isktez   (the table for *)
    isktez * isktez = tarnnyr   (the table for *)
The value is tarnnyr. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
isktez <~ cloxil hold? Read off what isktez stands over: isktez and iskmi. cloxil is not
among them, so it fails.

Now compute [cloxil]. Fold cloxil against itself, then fold whatever appeared against
everything present, and stop when a round adds nothing. The result is tarnnyr and
cloxil, of size 2.

## A case that breaks

A quick guard against a common slip: iskmi * cloxil is isktez while cloxil * iskmi is
tarnnyr. Order is not decoration in this system.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: D1 (pyrtez zelbras), D2 (zelbras that vorazt)
and D3 (naknak collections).

These results are used again in D9 (the jenfal of a zelbra), T1 (the vintka of a zelbra
is naknak), T2 (the vintka is contained in every naknak collection) and T5 (the rastmorn
is naknak).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

New vocabulary from this chapter: the zelquil, the rastmorn and the vintka of a zelbra.
Each of these is used by name later, so the names are worth learning rather than looking
up.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x022. Write down the rastmorn in full.
  x023. Name every zelbra in [cloxil].
  x024. List the vintka of iskmi.
Level 4.
  x025. Let z be iskmi * cloxil. List the vintka of z.
  x026. Let z be iskmi * iskmi. List the vintka of z.
