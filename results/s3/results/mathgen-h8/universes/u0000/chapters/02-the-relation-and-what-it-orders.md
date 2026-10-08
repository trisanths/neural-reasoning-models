# Chapter 3. The relation and what it orders

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is comparability of
every pair, agreement of the relation with the second operation and reflexivity of the
relation.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
vashumbs that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A10. Comparability of every pair. For all vashumbs x and y, at least one of x %% y and y
%% x holds.

A11. Agreement of the relation with the second operation. For all vashumbs x, y, z: if x
%% y then (z & x) %% (z & y) and (x & z) %% (y & z).

A7. Reflexivity of the relation. For every vashumb x: x %% x.

A8. Antisymmetry of the relation. For all vashumbs x and y: if x %% y and y %% x then x
= y.

A9. Transitivity of the relation. For all vashumbs x, y, z: if x %% y and y %% z then x
%% z.

D4. The brasib of a vashumb. The brasib of a vashumb x is the collection of vashumbs y
for which x %% y holds.

Worked out for each vashumb: korrvex to korrvex; keldclo to korrvex and keldclo; glimsib
to korrvex, keldclo and glimsib; hobtez to korrvex, keldclo, glimsib and hobtez; korrdri
to korrvex, keldclo, glimsib, hobtez and korrdri.

## The shape of it

Think of %% as pointing downhill. The brasib of a vashumb is everything downhill of it,
and those shadows here have sizes 1, 2, 3, 4 and 5.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 vashumbs the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R10 rests on S2 (the Ponmi combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Here is keldclo ? korrdri & glimsib, reduced without skipping anything.
    korrdri & glimsib = korrdri   (the table for &)
    keldclo ? korrdri = korrvex   (the table for ?)
So keldclo ? korrdri & glimsib is korrvex.

A companion case, korrdri ? (glimsib ? keldclo), to show what the brackets are doing.
    glimsib ? keldclo = keldclo   (the table for ?)
    korrdri ? keldclo = hobtez   (the table for ?)
That gives hobtez, against korrvex above.

Test hobtez %% korrdri. The brasib of hobtez is korrvex, keldclo, glimsib and hobtez,
and korrdri lies outside it, so the relation fails.

## A case that breaks

R10. It is not the case that: For all vashumbs x, y, z: if x %% y then (z ? x) %% (z ?
y) and (x ? z) %% (y ? z). The case that settles it: x = keldclo, y = korrvex, z =
keldclo, side = left. Anyone carrying this claim over from a more familiar system will
be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside S2 (the Ponmi combination tables).

These results are used again in D8 (a vexlum), D11 (ovijen pairs), T5 (brasibs are
nested along the relation) and T6 (there is at most one vexlum).

## Proofs

R10. It is not the case that: For all vashumbs x, y, z: if x %% y then (z ? x) %% (z ? y) and (x ? z) %% (y ? z).

  (1) [S2] Take the case x = keldclo, y = korrvex, z = keldclo, side = left, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the brasib of a vashumb. Each of these is used by name
later, so the names are worth learning rather than looking up.

Do not carry forward R10. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x025. Which vashumbs y satisfy keldclo %% y? Name them all.
  x026. List the brasib of glimsib.
  x027. List the brasib of hobtez.
Level 5.
  x021. The following fails in this system: For all vashumbs x, y, z: if x %% y then (z ? x) %% (z ? y) and (x ? z) %% (y ? z). Name the earliest vashumb, in the order the vashumbs were introduced, that witnesses the failure.
