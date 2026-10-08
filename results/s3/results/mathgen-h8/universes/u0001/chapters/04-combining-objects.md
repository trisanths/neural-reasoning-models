# Chapter 5. Combining objects

## Why this chapter

So far the drigrixs have been objects to be pushed around. This chapter starts asking
what they are like. We take up opalrast drigrixs, drigrixs that korrhob and the
mornvint.

Prerequisites are real here: chapters 1 and 2 supply the notions the statements below
are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
drigrixs that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D1. Opalrast drigrixs. A drigrix x is called opalrast when x @ x = x.

Running the definition over every drigrix leaves solvex and qenvex.

D2. Drigrixs that korrhob. Two drigrixs x and y are said to korrhob when x @ y = y @ x.

D5. The mornvint. The drigrix solvex is called the mornvint of the system. It is the
unique drigrix that leaves every drigrix unchanged under @.

Here that is solvex.

## The shape of it

Two questions sort the drigrixs quickly. Does combining a drigrix with itself change it?
For solvex and qenvex it does not. Does it matter which side it goes on? For solvex,
umbazt, glimmux, vashtez and qenvex it does not.

Neutrality is a strong condition disguised as a weak one. It fixes a single drigrix and,
through that, constrains everything that can combine with it.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 drigrixs the table is short enough to consult every time.

## Where these results come from

This chapter is groundwork. The derivations that use it start in the next one.

## A worked case

Take solvex @ umbazt + glimmux and work it out one step at a time.
    umbazt + glimmux = umbazt   (the table for +)
    solvex @ umbazt = umbazt   (the table for @)
So solvex @ umbazt + glimmux is umbazt.

A companion case, umbazt @ (glimmux @ solvex), to show what the brackets are doing.
    glimmux @ solvex = glimmux   (the table for @)
    umbazt @ glimmux = vashtez   (the table for @)
The value is vashtez, not umbazt.

Test vashtez :: glimmux. The aztdri of vashtez is solvex, and glimmux lies outside it,
so the relation fails.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation
and closure under the first operation. Those are properties of this system, not of
systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A1 (closure under the first operation) and A4 (a
neutral object for the first operation).

These results are used again in D6 (the kapon), D7 (the tezjen), D10 (qennyr drigrixs)
and T1 (the mornvint is the only one of its kind).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

Carry forward opalrast drigrixs, drigrixs that korrhob and the mornvint. Later chapters
state their results in these terms and do not restate the definitions.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 2.
  x023. Which drigrix leaves every drigrix unchanged under @?
Level 3.
  x016. List every drigrix in the opalrast.
