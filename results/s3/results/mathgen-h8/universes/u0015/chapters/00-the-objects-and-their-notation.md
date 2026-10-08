# Chapter 1. The objects and their notation

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through the Duthtarn signature, the
Duthtarn combination tables and closure under the first operation.

One habit to adopt: when a statement below quantifies over tezkas, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## The tables in full

The table for ><. Read the left argument down the side and the right argument across the top.

         |  lumwren   vorzel  opalfex
-------------------------------------
 lumwren |  lumwren   vorzel  opalfex
  vorzel |   vorzel  opalfex  lumwren
 opalfex |  opalfex  lumwren   vorzel

The table for |. Read the left argument down the side and the right argument across the top.

         |  lumwren   vorzel  opalfex
-------------------------------------
 lumwren |  lumwren  lumwren  lumwren
  vorzel |  lumwren   vorzel  opalfex
 opalfex |  lumwren  opalfex   vorzel

Every pair standing in the <~ relation, grouped by left argument.

  lumwren <~ lumwren, vorzel and opalfex
  vorzel <~ lumwren, vorzel and opalfex
  opalfex <~ lumwren, vorzel and opalfex

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A1. Closure under the first operation. For all tezkas x and y, x >< y is again a tezka.

A2. Association of the first operation. For all tezkas x, y, z: (x >< y) >< z = x >< (y
>< z).

A3. Commutation of the first operation. For all tezkas x and y: x >< y = y >< x.

A6. Cancellation in the first operation. For all tezkas x, y, z: if x >< y = x >< z then
y = z.

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

R1 rests on S2 (the Duthtarn combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Here is opalfex >< opalfex | vorzel, reduced without skipping anything.
    opalfex | vorzel = opalfex   (the table for |)
    opalfex >< opalfex = vorzel   (the table for ><)
So opalfex >< opalfex | vorzel is vorzel.

Move the brackets and the work changes. Take opalfex >< (vorzel >< opalfex).
    vorzel >< opalfex = lumwren   (the table for ><)
    opalfex >< lumwren = opalfex   (the table for ><)
The value is opalfex, not vorzel.

One decision about the relation, since deciding is as much a skill as computing. Does
vorzel <~ opalfex hold? Read off what vorzel stands over: lumwren, vorzel and opalfex.
opalfex is among them, so it holds.

## A case that breaks

R1. It is not the case that: For every tezka x: x >< x = x. It fails at x = vorzel,
value = opalfex. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

What is built on it later: A4 (a neutral object for the first operation), A5 (reversal
under the first operation), A7 (closure under the second operation) and A8 (association
of the second operation).

## Proofs

R1. It is not the case that: For every tezka x: x >< x = x.

  (1) [S2] Take the case x = vorzel, value = opalfex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 27 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R1. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 1.
  x001. What tezka does vorzel >< opalfex name?
  x002. Evaluate opalfex >< opalfex.
  x003. Reduce opalfex >< vorzel to a single tezka.
Level 2.
  x004. Reduce vorzel >< vorzel | opalfex to a single tezka.
  x007. Evaluate opalfex^3.
  x008. Evaluate vorzel^2.
  x009. Solve x >< vorzel = vorzel for x, naming every solution.
  x010. Which tezkas x satisfy x >< vorzel = lumwren? List them all.
Level 3.
  x005. Evaluate (lumwren >< opalfex) >< (lumwren >< opalfex).
  x006. Reduce (vorzel >< vorzel) >< (lumwren >< lumwren) to a single tezka.
