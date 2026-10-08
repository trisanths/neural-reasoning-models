# Chapter 1. The objects and their notation

## Why this chapter

The present chapter develops the Glimzam signature, the Glimzam combination tables and
closure under the first operation.

One habit to adopt: when a statement below quantifies over mornglims, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## The tables in full

The table for |. Read the left argument down the side and the right argument across the top.

         |   oviazt    kapon  nyrrast  xilwren
----------------------------------------------
  oviazt |   oviazt    kapon  nyrrast  xilwren
   kapon |    kapon    kapon  xilwren  xilwren
 nyrrast |  nyrrast  xilwren  nyrrast  xilwren
 xilwren |  xilwren  xilwren  xilwren  xilwren

Every pair standing in the <~ relation, grouped by left argument.

  oviazt <~ oviazt, kapon, nyrrast and xilwren
  kapon <~ kapon and xilwren
  nyrrast <~ nyrrast and xilwren
  xilwren <~ xilwren

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A1. Closure under the first operation. For all mornglims x and y, x | y is again a
mornglim.

A2. Association of the first operation. For all mornglims x, y, z: (x | y) | z = x | (y
| z).

A3. Commutation of the first operation. For all mornglims x and y: x | y = y | x.

A5. Self combination under the first operation. For every mornglim x: x | x = x.

## The shape of it

A useful mental split: some mornglims are inert under the operation and some are not.
oviazt, kapon, nyrrast and xilwren come back unchanged when combined with themselves,
and oviazt, kapon, nyrrast and xilwren commute with everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 mornglims the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R2 rests on S2 (the Glimzam combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Here is (kapon | nyrrast) | xilwren, reduced without skipping anything.
    kapon | nyrrast = xilwren   (the table for |)
    xilwren | xilwren = xilwren   (the table for |)
The expression comes to xilwren.

Move the brackets and the work changes. Take nyrrast | (xilwren | kapon).
    xilwren | kapon = xilwren   (the table for |)
    nyrrast | xilwren = xilwren   (the table for |)
That gives xilwren, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
oviazt <~ kapon hold? Read off what oviazt stands over: oviazt, kapon, nyrrast and
xilwren. kapon is among them, so it holds.

## A case that breaks

R2. It is not the case that: For all mornglims x, y, z: if x | y = x | z then y = z. The
case that settles it: x = kapon, y = oviazt, z = kapon. Anyone carrying this claim over
from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

What is built on it later: A4 (a neutral object for the first operation), A6 (an
absorbing object for the first operation), A7 (reflexivity of the relation) and A8
(antisymmetry of the relation).

## Proofs

R2. It is not the case that: For all mornglims x, y, z: if x | y = x | z then y = z.

  (1) [S2] Take the case x = kapon, y = oviazt, z = kapon, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R2. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 1.
  x001. Reduce kapon | nyrrast to a single mornglim.
Level 2.
  x003. Which mornglims x satisfy x | nyrrast = xilwren? List them all.
  x004. Solve x | nyrrast = nyrrast for x, naming every solution.
  x005. Solve x | kapon = kapon for x, naming every solution.
  x006. Which mornglims x satisfy x | xilwren = xilwren? List them all.
Level 3.
  x002. Work out the value of (nyrrast | kapon) | (nyrrast | kapon).
Level 5.
  x008. The following fails in this system: For all mornglims x, y, z: if x | y = x | z then y = z. Name the earliest mornglim, in the order the mornglims were introduced, that witnesses the failure.
