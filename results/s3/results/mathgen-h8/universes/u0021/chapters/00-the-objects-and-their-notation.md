# Chapter 1. The objects and their notation

## Why this chapter

The present chapter develops the Quilpon signature, the Quilpon combination tables and
closure under the first operation.

One habit to adopt: when a statement below quantifies over lumpons, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## The tables in full

The table for -. Read the left argument down the side and the right argument across the top.

          |   glimtez  glimkorr   nakkorr  duthwren      kaka   mornhob
-----------------------------------------------------------------------
  glimtez |   glimtez  glimkorr   nakkorr  duthwren      kaka   mornhob
 glimkorr |  glimkorr   nakkorr  duthwren      kaka   mornhob   glimtez
  nakkorr |   nakkorr  duthwren      kaka   mornhob   glimtez  glimkorr
 duthwren |  duthwren      kaka   mornhob   glimtez  glimkorr   nakkorr
     kaka |      kaka   mornhob   glimtez  glimkorr   nakkorr  duthwren
  mornhob |   mornhob   glimtez  glimkorr   nakkorr  duthwren      kaka

Every pair standing in the >- relation, grouped by left argument.

  glimtez >- glimtez, glimkorr, nakkorr, duthwren, kaka and mornhob
  glimkorr >- glimkorr, nakkorr, duthwren, kaka and mornhob
  nakkorr >- nakkorr, duthwren, kaka and mornhob
  duthwren >- duthwren, kaka and mornhob
  kaka >- kaka and mornhob
  mornhob >- mornhob

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A1. Closure under the first operation. For all lumpons x and y, x - y is again a lumpon.

A2. Association of the first operation. For all lumpons x, y, z: (x - y) - z = x - (y -
z).

A3. Commutation of the first operation. For all lumpons x and y: x - y = y - x.

A6. Cancellation in the first operation. For all lumpons x, y, z: if x - y = x - z then
y = z.

## The shape of it

Two questions sort the lumpons quickly. Does combining a lumpon with itself change it?
For glimtez it does not. Does it matter which side it goes on? For glimtez, glimkorr,
nakkorr, duthwren, kaka and mornhob it does not.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R1 rests on S2 (the Quilpon combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Evaluate (glimkorr - nakkorr) - duthwren. Each line below is one lookup in a table.
    glimkorr - nakkorr = duthwren   (the table for -)
    duthwren - duthwren = glimtez   (the table for -)
That leaves glimtez, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is nakkorr - (duthwren - glimkorr) for contrast.
    duthwren - glimkorr = kaka   (the table for -)
    nakkorr - kaka = glimtez   (the table for -)
That gives glimtez, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test glimkorr >- nakkorr. The yukglim of glimkorr is glimkorr, nakkorr, duthwren, kaka
and mornhob, and nakkorr lies inside it, so the relation holds.

## A case that breaks

R1. It is not the case that: For every lumpon x: x - x = x. The case that settles it: x
= glimkorr, value = nakkorr. Anyone carrying this claim over from a more familiar system
will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

These results are used again in A4 (a neutral object for the first operation), A5
(reversal under the first operation), A7 (reflexivity of the relation) and A8
(antisymmetry of the relation).

## Proofs

R1. It is not the case that: For every lumpon x: x - x = x.

  (1) [S2] Take the case x = glimkorr, value = nakkorr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R1. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 1.
  x001. Evaluate glimkorr - kaka.
  x002. What lumpon does glimkorr - nakkorr name?
  x003. Reduce nakkorr - mornhob to a single lumpon.
  x004. Reduce kaka - glimkorr to a single lumpon.
  x005. Work out the value of kaka - kaka.
  x006. What lumpon does duthwren - nakkorr name?
Level 2.
  x007. What lumpon does (glimtez - duthwren) - kaka name?
  x008. What lumpon does (glimkorr - glimkorr) - glimtez name?
  x009. What lumpon does (glimkorr - duthwren) - glimtez name?
  x012. Evaluate mornhob^3.
  x013. What is kaka combined with itself 2 times under -?
  x014. Evaluate glimkorr - mornhob'.
  x015. Solve x - nakkorr = glimtez for x, naming every solution.
  x016. Which lumpons x satisfy x - nakkorr = glimkorr? List them all.
  x017. Solve x - nakkorr = mornhob for x, naming every solution.
  x018. Which lumpons x satisfy x - kaka = glimtez? List them all.
  x019. Which lumpons x satisfy x - duthwren = nakkorr? List them all.
Level 3.
  x010. Work out the value of (glimtez - kaka) - (glimtez - duthwren).
  x011. What lumpon does (duthwren - nakkorr) - (duthwren - mornhob) name?
