# Chapter 1. The objects and their notation

## Why this chapter

We turn to the Umbtu signature, the Umbtu combination tables and closure under the first
operation. The treatment is self contained given the material already established.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
drigrixs that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## The tables in full

The table for @. Read the left argument down the side and the right argument across the top.

         |   solvex   umbazt  glimmux  vashtez   qenvex
-------------------------------------------------------
  solvex |   solvex   umbazt  glimmux  vashtez   qenvex
  umbazt |   umbazt  glimmux  vashtez   qenvex   qenvex
 glimmux |  glimmux  vashtez   qenvex   qenvex   qenvex
 vashtez |  vashtez   qenvex   qenvex   qenvex   qenvex
  qenvex |   qenvex   qenvex   qenvex   qenvex   qenvex

The table for +. Read the left argument down the side and the right argument across the top.

         |   solvex   umbazt  glimmux  vashtez   qenvex
-------------------------------------------------------
  solvex |   solvex   solvex   solvex   solvex   solvex
  umbazt |   solvex   umbazt   umbazt   umbazt   umbazt
 glimmux |   solvex   umbazt  glimmux  glimmux  glimmux
 vashtez |   solvex   umbazt  glimmux  vashtez  vashtez
  qenvex |   solvex   umbazt  glimmux  vashtez   qenvex

Every pair standing in the :: relation, grouped by left argument.

  solvex :: solvex
  umbazt :: solvex
  glimmux :: solvex
  vashtez :: solvex
  qenvex :: solvex, umbazt, glimmux, vashtez and qenvex

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A1. Closure under the first operation. For all drigrixs x and y, x @ y is again a
drigrix.

A2. Association of the first operation. For all drigrixs x, y, z: (x @ y) @ z = x @ (y @
z).

A3. Commutation of the first operation. For all drigrixs x and y: x @ y = y @ x.

## The shape of it

A useful mental split: some drigrixs are inert under the operation and some are not.
solvex and qenvex come back unchanged when combined with themselves, and solvex, umbazt,
glimmux, vashtez and qenvex commute with everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 drigrixs the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R2 rests on S2 (the Umbtu combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

R3 rests on S2 (the Umbtu combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

## A worked case

Evaluate umbazt @ glimmux + vashtez. Each line below is one lookup in a table.
    glimmux + vashtez = glimmux   (the table for +)
    umbazt @ glimmux = vashtez   (the table for @)
The expression comes to vashtez.

Bracketing is not cosmetic, so here is glimmux @ (vashtez @ umbazt) for contrast.
    vashtez @ umbazt = qenvex   (the table for @)
    glimmux @ qenvex = qenvex   (the table for @)
The value is qenvex, not vashtez.

One decision about the relation, since deciding is as much a skill as computing. Does
qenvex :: umbazt hold? Read off what qenvex stands over: solvex, umbazt, glimmux,
vashtez and qenvex. umbazt is among them, so it holds.

## A case that breaks

R2. It is not the case that: For every drigrix x: x @ x = x. The case that settles it: x
= umbazt, value = glimmux. Anyone carrying this claim over from a more familiar system
will be wrong here, and wrong in a way that propagates.

R3. It is not the case that: For all drigrixs x, y, z: if x @ y = x @ z then y = z. It
fails at x = umbazt, y = vashtez, z = qenvex. One case is enough, and this is the
earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

These results are used again in A4 (a neutral object for the first operation), A5 (an
absorbing object for the first operation), A6 (closure under the second operation) and
A7 (association of the second operation).

## Proofs

R2. It is not the case that: For every drigrix x: x @ x = x.

  (1) [S2] Take the case x = umbazt, value = glimmux, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R3. It is not the case that: For all drigrixs x, y, z: if x @ y = x @ z then y = z.

  (1) [S2] Take the case x = umbazt, y = vashtez, z = qenvex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R2 and R3. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 1.
  x001. What drigrix does vashtez @ vashtez name?
  x002. Reduce vashtez @ umbazt to a single drigrix.
Level 2.
  x003. Work out the value of (glimmux @ solvex) @ umbazt.
  x004. What drigrix does (umbazt @ glimmux) @ umbazt name?
  x006. Evaluate glimmux^3.
  x007. Which drigrixs x satisfy x @ qenvex = qenvex? List them all.
  x008. Which drigrixs x satisfy x @ glimmux = qenvex? List them all.
Level 3.
  x005. What drigrix does (umbazt @ solvex) @ (glimmux @ solvex) name?
  x009. Evaluate glimmux @ umbazt + qenvex, minding which operation binds tighter.
Level 5.
  x011. The following fails in this system: For every drigrix x: x @ x = x. Name the earliest drigrix, in the order the drigrixs were introduced, that witnesses the failure.
  x012. The following fails in this system: For all drigrixs x, y, z: if x @ y = x @ z then y = z. Name the earliest drigrix, in the order the drigrixs were introduced, that witnesses the failure.
