# Chapter 1. The objects and their notation

## Why this chapter

The practical content of this chapter is the Duthsol signature, the Duthsol combination
tables and closure under the first operation. It is the part that shows up in use.

The standard of proof here is exhaustion. A universal claim about opalmis covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## The tables in full

The table for -. Read the left argument down the side and the right argument across the top.

         |  keldsib  duthzam   hobfex   iskxil   qenxil
-------------------------------------------------------
 keldsib |  keldsib  keldsib  keldsib  keldsib  keldsib
 duthzam |  keldsib  duthzam   hobfex   iskxil   qenxil
  hobfex |  keldsib   hobfex   qenxil  duthzam   iskxil
  iskxil |  keldsib   iskxil  duthzam   qenxil   hobfex
  qenxil |  keldsib   qenxil   iskxil   hobfex  duthzam

Every pair standing in the <~ relation, grouped by left argument.

  keldsib <~ keldsib, duthzam, hobfex, iskxil and qenxil
  duthzam <~ duthzam
  hobfex <~ duthzam
  iskxil <~ duthzam
  qenxil <~ duthzam

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A1. Closure under the first operation. For all opalmis x and y, x - y is again a opalmi.

A2. Association of the first operation. For all opalmis x, y, z: (x - y) - z = x - (y -
z).

A3. Commutation of the first operation. For all opalmis x and y: x - y = y - x.

## The shape of it

Two questions sort the opalmis quickly. Does combining a opalmi with itself change it?
For keldsib and duthzam it does not. Does it matter which side it goes on? For keldsib,
duthzam, hobfex, iskxil and qenxil it does not.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R2 rests on S2 (the Duthsol combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R3 rests on S2 (the Duthsol combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Take (hobfex - iskxil) - keldsib and work it out one step at a time.
    hobfex - iskxil = duthzam   (the table for -)
    duthzam - keldsib = keldsib   (the table for -)
The expression comes to keldsib.

Bracketing is not cosmetic, so here is iskxil - (keldsib - hobfex) for contrast.
    keldsib - hobfex = keldsib   (the table for -)
    iskxil - keldsib = keldsib   (the table for -)
That gives keldsib, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
keldsib <~ keldsib hold? Read off what keldsib stands over: keldsib, duthzam, hobfex,
iskxil and qenxil. keldsib is among them, so it holds.

## A case that breaks

R2. It is not the case that: For every opalmi x: x - x = x. It fails at x = hobfex,
value = qenxil. One case is enough, and this is the earliest one.

R3. It is not the case that: For all opalmis x, y, z: if x - y = x - z then y = z. The
case that settles it: x = keldsib, y = keldsib, z = duthzam. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

These results are used again in A4 (a neutral object for the first operation), A5 (an
absorbing object for the first operation), A6 (antisymmetry of the relation) and A7
(transitivity of the relation).

## Proofs

R2. It is not the case that: For every opalmi x: x - x = x.

  (1) [S2] Take the case x = hobfex, value = qenxil, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R3. It is not the case that: For all opalmis x, y, z: if x - y = x - z then y = z.

  (1) [S2] Take the case x = keldsib, y = keldsib, z = duthzam, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R2 and R3. A later argument that quietly assumes one of these
is wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 1.
  x001. Reduce hobfex - iskxil to a single opalmi.
  x002. Work out the value of iskxil - hobfex.
Level 2.
  x003. Evaluate (iskxil - iskxil) - iskxil.
  x004. Work out the value of (duthzam - iskxil) - iskxil.
  x005. Evaluate (qenxil - duthzam) - hobfex.
  x006. Evaluate hobfex^3.
  x007. Which opalmis x satisfy x - hobfex = iskxil? List them all.
  x008. Which opalmis x satisfy x - hobfex = duthzam? List them all.
  x009. Solve x - keldsib = keldsib for x, naming every solution.
  x010. Solve x - iskxil = iskxil for x, naming every solution.
  x011. Solve x - qenxil = qenxil for x, naming every solution.
  x012. Which opalmis x satisfy x - iskxil = duthzam? List them all.
Level 5.
  x014. The following fails in this system: For every opalmi x: x - x = x. Name the earliest opalmi, in the order the opalmis were introduced, that witnesses the failure.
  x015. The following fails in this system: For all opalmis x, y, z: if x - y = x - z then y = z. Name the earliest opalmi, in the order the opalmis were introduced, that witnesses the failure.
