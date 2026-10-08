# Chapter 3. The relation and what it orders

## Why this chapter

The present chapter develops reflexivity of the relation, antisymmetry of the relation
and transitivity of the relation.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
reldjens that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A10. Reflexivity of the relation. For every reldjen x: x :: x.

A11. Antisymmetry of the relation. For all reldjens x and y: if x :: y and y :: x then x
= y.

A12. Transitivity of the relation. For all reldjens x, y, z: if x :: y and y :: z then x
:: z.

A13. Comparability of every pair. For all reldjens x and y, at least one of x :: y and y
:: x holds.

D4. The drivor of a reldjen. The drivor of a reldjen x is the collection of reldjens y
for which x :: y holds.

Worked out for each reldjen: nakopal to nakopal, kagel, korrreld and iskbra; kagel to
kagel, korrreld and iskbra; korrreld to korrreld and iskbra; iskbra to iskbra.

## The shape of it

The relation is easiest to see as a height. Each reldjen casts a drivor over what it
yields to, and the sizes of those shadows here are 1, 2, 3 and 4. No two are the same
size, so the objects line up in a single file.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R7 rests on S2 (the Mornyuk combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R8 rests on S2 (the Mornyuk combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take korrreld <> nakopal # iskbra and work it out one step at a time.
    nakopal # iskbra = iskbra   (the table for #)
    korrreld <> iskbra = korrreld   (the table for <>)
So korrreld <> nakopal # iskbra is korrreld.

Move the brackets and the work changes. Take nakopal <> (iskbra <> korrreld).
    iskbra <> korrreld = korrreld   (the table for <>)
    nakopal <> korrreld = nakopal   (the table for <>)
That gives nakopal, against korrreld above.

Test korrreld :: korrreld. The drivor of korrreld is korrreld and iskbra, and korrreld
lies inside it, so the relation holds.

## A case that breaks

R7. It is not the case that: For all reldjens x, y, z: if x :: y then (z <> x) :: (z <>
y) and (x <> z) :: (y <> z). The case that settles it: x = kagel, y = korrreld, z =
korrreld, side = left. Anyone carrying this claim over from a more familiar system will
be wrong here, and wrong in a way that propagates.

R8. It is not the case that: For all reldjens x, y, z: if x :: y then (z # x) :: (z # y)
and (x # z) :: (y # z). The case that settles it: x = nakopal, y = kagel, z = iskbra,
side = left. Anyone carrying this claim over from a more familiar system will be wrong
here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: S2 (the Mornyuk combination tables).

What is built on it later: D9 (a thrapyr), D13 (korrjen pairs), T10 (drivors are nested
along the relation) and T11 (there is at most one thrapyr).

## Proofs

R7. It is not the case that: For all reldjens x, y, z: if x :: y then (z <> x) :: (z <> y) and (x <> z) :: (y <> z).

  (1) [S2] Take the case x = kagel, y = korrreld, z = korrreld, side = left, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R8. It is not the case that: For all reldjens x, y, z: if x :: y then (z # x) :: (z # y) and (x # z) :: (y # z).

  (1) [S2] Take the case x = nakopal, y = kagel, z = iskbra, side = left, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the drivor of a reldjen. Each of these is used by name
later, so the names are worth learning rather than looking up.

Do not carry forward R7 and R8. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 5.
  x012. The following fails in this system: For all reldjens x, y, z: if x :: y then (z <> x) :: (z <> y) and (x <> z) :: (y <> z). Name the earliest reldjen, in the order the reldjens were introduced, that witnesses the failure.
