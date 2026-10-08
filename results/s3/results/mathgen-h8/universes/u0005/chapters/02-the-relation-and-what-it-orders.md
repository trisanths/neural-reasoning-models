# Chapter 3. The relation and what it orders

## Why this chapter

Work through this chapter with the tables in front of you. It covers reflexivity of the
relation, antisymmetry of the relation and transitivity of the relation, and each claim
can be checked by hand.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over jenxils, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A2. Reflexivity of the relation. For every jenxil x: x =< x.

A3. Antisymmetry of the relation. For all jenxils x and y: if x =< y and y =< x then x =
y.

A4. Transitivity of the relation. For all jenxils x, y, z: if x =< y and y =< z then x
=< z.

A5. Comparability of every pair. For all jenxils x and y, at least one of x =< y and y
=< x holds.

D4. The rastqen of a jenxil. The rastqen of a jenxil x is the collection of jenxils y
for which x =< y holds.

Worked out for each jenxil: reldvint to reldvint, wrenmux and zellum; wrenmux to wrenmux
and zellum; zellum to zellum.

## The shape of it

Think of =< as pointing downhill. The rastqen of a jenxil is everything downhill of it,
and those shadows here have sizes 1, 2 and 3.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 3 jenxils the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R8 rests on S2 (the Tarnsib combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Evaluate (zellum % wrenmux) % zellum. Each line below is one lookup in a table.
    zellum % wrenmux = wrenmux   (the table for %)
    wrenmux % zellum = reldvint   (the table for %)
So (zellum % wrenmux) % zellum is reldvint.

Bracketing is not cosmetic, so here is wrenmux % (zellum % zellum) for contrast.
    zellum % zellum = reldvint   (the table for %)
    wrenmux % reldvint = wrenmux   (the table for %)
The value is wrenmux, not reldvint.

Test reldvint =< reldvint. The rastqen of reldvint is reldvint, wrenmux and zellum, and
reldvint lies inside it, so the relation holds.

## A case that breaks

R8. It is not the case that: For all jenxils x, y, z: if x =< y then (z % x) =< (z % y)
and (x % z) =< (y % z). The case that settles it: x = reldvint, y = wrenmux, z =
wrenmux, side = left. Anyone carrying this claim over from a more familiar system will
be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside S2 (the Tarnsib combination tables).

These results are used again in D8 (a wrenwren), D11 (iskclo pairs), T5 (rastqens are
nested along the relation) and T6 (there is at most one wrenwren).

## Proofs

R8. It is not the case that: For all jenxils x, y, z: if x =< y then (z % x) =< (z % y) and (x % z) =< (y % z).

  (1) [S2] Take the case x = reldvint, y = wrenmux, z = wrenmux, side = left, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 27 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the rastqen of a jenxil. Later chapters state their results in these terms
and do not restate the definitions.

Do not carry forward R8. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 5.
  x014. The following fails in this system: For all jenxils x, y, z: if x =< y then (z % x) =< (z % y) and (x % z) =< (y % z). Name the earliest jenxil, in the order the jenxils were introduced, that witnesses the failure.
