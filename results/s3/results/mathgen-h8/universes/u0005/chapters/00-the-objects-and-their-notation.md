# Chapter 1. The objects and their notation

## Why this chapter

So far the jenxils have been objects to be pushed around. This chapter starts asking
what they are like. We take up the Tarnsib signature, the Tarnsib combination tables and
closure under the first operation.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 3
jenxils that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## The tables in full

The table for %. Read the left argument down the side and the right argument across the top.

          |  reldvint   wrenmux    zellum
-----------------------------------------
 reldvint |  reldvint  reldvint  reldvint
  wrenmux |   wrenmux  reldvint  reldvint
   zellum |    zellum   wrenmux  reldvint

Every pair standing in the =< relation, grouped by left argument.

  reldvint =< reldvint, wrenmux and zellum
  wrenmux =< wrenmux and zellum
  zellum =< zellum

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A1. Closure under the first operation. For all jenxils x and y, x % y is again a jenxil.

## The shape of it

Two questions sort the jenxils quickly. Does combining a jenxil with itself change it?
For reldvint it does not. Does it matter which side it goes on? It always does.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R1 rests on S2 (the Tarnsib combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R2 rests on S2 (the Tarnsib combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R5 rests on S2 (the Tarnsib combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R6 rests on S2 (the Tarnsib combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Here is (reldvint % zellum) % reldvint, reduced without skipping anything.
    reldvint % zellum = reldvint   (the table for %)
    reldvint % reldvint = reldvint   (the table for %)
So (reldvint % zellum) % reldvint is reldvint.

Bracketing is not cosmetic, so here is zellum % (reldvint % reldvint) for contrast.
    reldvint % reldvint = reldvint   (the table for %)
    zellum % reldvint = zellum   (the table for %)
The value is zellum, not reldvint.

Test zellum =< zellum. The rastqen of zellum is zellum, and zellum lies inside it, so
the relation holds.

## A case that breaks

R1. It is not the case that: For all jenxils x, y, z: (x % y) % z = x % (y % z). The
case that settles it: x = wrenmux, y = reldvint, z = wrenmux, left = reldvint, right =
wrenmux. Anyone carrying this claim over from a more familiar system will be wrong here,
and wrong in a way that propagates.

R2. It is not the case that: For all jenxils x and y: x % y = y % x. It fails at x =
reldvint, y = wrenmux, left = reldvint, right = wrenmux. One case is enough, and this is
the earliest one.

R5. It is not the case that: For every jenxil x: x % x = x. It fails at x = wrenmux,
value = reldvint. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

What is built on it later: A2 (reflexivity of the relation), A3 (antisymmetry of the
relation), A4 (transitivity of the relation) and A5 (comparability of every pair).

## Proofs

R1. It is not the case that: For all jenxils x, y, z: (x % y) % z = x % (y % z).

  (1) [S2] Take the case x = wrenmux, y = reldvint, z = wrenmux, left = reldvint, right = wrenmux, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 27 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R2. It is not the case that: For all jenxils x and y: x % y = y % x.

  (1) [S2] Take the case x = reldvint, y = wrenmux, left = reldvint, right = wrenmux, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 27 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R5. It is not the case that: For every jenxil x: x % x = x.

  (1) [S2] Take the case x = wrenmux, value = reldvint, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 27 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R6. It is not the case that: For all jenxils x, y, z: if x % y = x % z then y = z.

  (1) [S2] Take the case x = reldvint, y = reldvint, z = wrenmux, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 27 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R1, R2, R5 and R6. These were tested and failed, and the failing
cases are recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 1.
  x001. Evaluate zellum % zellum.
  x002. Evaluate wrenmux % zellum.
Level 2.
  x003. Reduce (zellum % zellum) % zellum to a single jenxil.
  x004. Evaluate (zellum % wrenmux) % wrenmux.
  x006. What is wrenmux combined with itself 3 times under %?
  x007. Solve x % wrenmux = reldvint for x, naming every solution.
  x008. Solve x % zellum = reldvint for x, naming every solution.
  x009. Which jenxils x satisfy x % wrenmux = wrenmux? List them all.
Level 3.
  x005. Work out the value of (wrenmux % wrenmux) % (zellum % zellum).
Level 5.
  x010. The following fails in this system: For all jenxils x, y, z: (x % y) % z = x % (y % z). Name the earliest jenxil, in the order the jenxils were introduced, that witnesses the failure.
  x011. The following fails in this system: For all jenxils x and y: x % y = y % x. Name the earliest jenxil, in the order the jenxils were introduced, that witnesses the failure.
  x013. The following fails in this system: For all jenxils x, y, z: if x % y = x % z then y = z. Name the earliest jenxil, in the order the jenxils were introduced, that witnesses the failure.
