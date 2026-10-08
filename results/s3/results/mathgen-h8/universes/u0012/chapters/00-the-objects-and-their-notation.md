# Chapter 1. The objects and their notation

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is the Nyrduth
signature, the Nyrduth combination tables and closure under the first operation.

One habit to adopt: when a statement below quantifies over glimyuks, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## The tables in full

The table for &. Read the left argument down the side and the right argument across the top.

         |  fexvash   kamorn  muxreld  quilisk   ovifal    kanyr
----------------------------------------------------------------
 fexvash |  fexvash   kamorn  muxreld  quilisk   ovifal    kanyr
  kamorn |   kamorn  muxreld  quilisk   ovifal    kanyr    kanyr
 muxreld |  muxreld  quilisk   ovifal    kanyr    kanyr    kanyr
 quilisk |  quilisk   ovifal    kanyr    kanyr    kanyr    kanyr
  ovifal |   ovifal    kanyr    kanyr    kanyr    kanyr    kanyr
   kanyr |    kanyr    kanyr    kanyr    kanyr    kanyr    kanyr

The table for :. Read the left argument down the side and the right argument across the top.

         |  fexvash   kamorn  muxreld  quilisk   ovifal    kanyr
----------------------------------------------------------------
 fexvash |  fexvash  fexvash  fexvash  fexvash  fexvash  fexvash
  kamorn |  fexvash   kamorn   kamorn   kamorn   kamorn   kamorn
 muxreld |  fexvash   kamorn  muxreld  muxreld  muxreld  muxreld
 quilisk |  fexvash   kamorn  muxreld  quilisk  quilisk  quilisk
  ovifal |  fexvash   kamorn  muxreld  quilisk   ovifal   ovifal
   kanyr |  fexvash   kamorn  muxreld  quilisk   ovifal    kanyr

Every pair standing in the >- relation, grouped by left argument.

  fexvash >- fexvash, kamorn, muxreld, quilisk, ovifal and kanyr
  kamorn >- kamorn, muxreld, quilisk, ovifal and kanyr
  muxreld >- muxreld, quilisk, ovifal and kanyr
  quilisk >- quilisk, ovifal and kanyr
  ovifal >- ovifal and kanyr
  kanyr >- kanyr

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A1. Closure under the first operation. For all glimyuks x and y, x & y is again a
glimyuk.

A2. Association of the first operation. For all glimyuks x, y, z: (x & y) & z = x & (y &
z).

A3. Commutation of the first operation. For all glimyuks x and y: x & y = y & x.

## The shape of it

A useful mental split: some glimyuks are inert under the operation and some are not.
fexvash and kanyr come back unchanged when combined with themselves, and fexvash,
kamorn, muxreld, quilisk, ovifal and kanyr commute with everything.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R2 rests on S2 (the Nyrduth combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R3 rests on S2 (the Nyrduth combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Take quilisk & muxreld : ovifal and work it out one step at a time.
    muxreld : ovifal = muxreld   (the table for :)
    quilisk & muxreld = kanyr   (the table for &)
So quilisk & muxreld : ovifal is kanyr.

Move the brackets and the work changes. Take muxreld & (ovifal & quilisk).
    ovifal & quilisk = kanyr   (the table for &)
    muxreld & kanyr = kanyr   (the table for &)
That gives kanyr, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test kamorn >- fexvash. The mornclo of kamorn is kamorn, muxreld, quilisk, ovifal and
kanyr, and fexvash lies outside it, so the relation fails.

## A case that breaks

R2. It is not the case that: For every glimyuk x: x & x = x. It fails at x = kamorn,
value = muxreld. One case is enough, and this is the earliest one.

R3. It is not the case that: For all glimyuks x, y, z: if x & y = x & z then y = z. The
case that settles it: x = kamorn, y = ovifal, z = kanyr. Anyone carrying this claim over
from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

What is built on it later: A4 (a neutral object for the first operation), A5 (an
absorbing object for the first operation), A6 (closure under the second operation) and
A7 (association of the second operation).

## Proofs

R2. It is not the case that: For every glimyuk x: x & x = x.

  (1) [S2] Take the case x = kamorn, value = muxreld, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R3. It is not the case that: For all glimyuks x, y, z: if x & y = x & z then y = z.

  (1) [S2] Take the case x = kamorn, y = ovifal, z = kanyr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R2 and R3. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 1.
  x001. Work out the value of kamorn & quilisk.
  x002. Work out the value of quilisk & ovifal.
Level 2.
  x003. Evaluate muxreld & muxreld : kamorn.
  x004. Evaluate (muxreld & kamorn) & fexvash.
  x006. Evaluate kamorn^2.
  x007. Which glimyuks x satisfy x & ovifal = ovifal? List them all.
  x008. Which glimyuks x satisfy x & ovifal = kanyr? List them all.
  x009. Solve x & quilisk = kanyr for x, naming every solution.
  x010. Solve x & muxreld = kanyr for x, naming every solution.
Level 3.
  x005. Evaluate (fexvash & muxreld) & (quilisk & muxreld).
  x011. Evaluate muxreld & quilisk : quilisk, minding which operation binds tighter.
Level 5.
  x013. The following fails in this system: For every glimyuk x: x & x = x. Name the earliest glimyuk, in the order the glimyuks were introduced, that witnesses the failure.
  x014. The following fails in this system: For all glimyuks x, y, z: if x & y = x & z then y = z. Name the earliest glimyuk, in the order the glimyuks were introduced, that witnesses the failure.
