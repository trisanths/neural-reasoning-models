# Chapter 1. The objects and their notation

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is the Vorjen
signature, the Vorjen combination tables and closure under the first operation.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
driwrens that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## The tables in full

The table for *. Read the left argument down the side and the right argument across the top.

         |  nakquil  soltarn   muxsib   braovi   yukzel  thraisk
----------------------------------------------------------------
 nakquil |  nakquil  soltarn   muxsib   braovi   yukzel  thraisk
 soltarn |  soltarn  soltarn   yukzel   braovi   yukzel  thraisk
  muxsib |   muxsib   yukzel   muxsib  thraisk   yukzel  thraisk
  braovi |   braovi   braovi  thraisk   braovi  thraisk  thraisk
  yukzel |   yukzel   yukzel   yukzel  thraisk   yukzel  thraisk
 thraisk |  thraisk  thraisk  thraisk  thraisk  thraisk  thraisk

Every pair standing in the << relation, grouped by left argument.

  nakquil << nakquil
  soltarn << nakquil and soltarn
  muxsib << nakquil and muxsib
  braovi << nakquil, soltarn and braovi
  yukzel << nakquil, soltarn, muxsib and yukzel
  thraisk << nakquil, soltarn, muxsib, braovi, yukzel and thraisk

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A1. Closure under the first operation. For all driwrens x and y, x * y is again a
driwren.

A2. Association of the first operation. For all driwrens x, y, z: (x * y) * z = x * (y *
z).

A3. Commutation of the first operation. For all driwrens x and y: x * y = y * x.

A5. Self combination under the first operation. For every driwren x: x * x = x.

## The shape of it

A useful mental split: some driwrens are inert under the operation and some are not.
nakquil, soltarn, muxsib, braovi, yukzel and thraisk come back unchanged when combined
with themselves, and nakquil, soltarn, muxsib, braovi, yukzel and thraisk commute with
everything.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R2 rests on S2 (the Vorjen combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Take (braovi * soltarn) * yukzel and work it out one step at a time.
    braovi * soltarn = braovi   (the table for *)
    braovi * yukzel = thraisk   (the table for *)
So (braovi * soltarn) * yukzel is thraisk.

Bracketing is not cosmetic, so here is soltarn * (yukzel * braovi) for contrast.
    yukzel * braovi = thraisk   (the table for *)
    soltarn * thraisk = thraisk   (the table for *)
The value is thraisk. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
yukzel << nakquil hold? Read off what yukzel stands over: nakquil, soltarn, muxsib and
yukzel. nakquil is among them, so it holds.

## A case that breaks

R2. It is not the case that: For all driwrens x, y, z: if x * y = x * z then y = z. The
case that settles it: x = soltarn, y = nakquil, z = soltarn. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

What is built on it later: A4 (a neutral object for the first operation), A6 (an
absorbing object for the first operation), A7 (reflexivity of the relation) and A8
(antisymmetry of the relation).

## Proofs

R2. It is not the case that: For all driwrens x, y, z: if x * y = x * z then y = z.

  (1) [S2] Take the case x = soltarn, y = nakquil, z = soltarn, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R2. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 1.
  x001. Evaluate yukzel * braovi.
Level 2.
  x002. Work out the value of (yukzel * braovi) * braovi.
  x003. Solve x * soltarn = yukzel for x, naming every solution.
  x004. Solve x * muxsib = yukzel for x, naming every solution.
  x005. Which driwrens x satisfy x * thraisk = thraisk? List them all.
  x006. Solve x * muxsib = thraisk for x, naming every solution.
Level 5.
  x008. The following fails in this system: For all driwrens x, y, z: if x * y = x * z then y = z. Name the earliest driwren, in the order the driwrens were introduced, that witnesses the failure.
