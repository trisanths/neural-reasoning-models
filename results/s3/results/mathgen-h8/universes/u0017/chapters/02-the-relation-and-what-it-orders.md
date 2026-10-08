# Chapter 3. The relation and what it orders

## Why this chapter

Anyone using this system to keep track of something will meet reflexivity of the
relation, transitivity of the relation and agreement of the relation with the first
operation early, whether or not they go looking.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
duthpons that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A6. Reflexivity of the relation. For every duthpon x: x >> x.

A7. Transitivity of the relation. For all duthpons x, y, z: if x >> y and y >> z then x
>> z.

A8. Agreement of the relation with the first operation. For all duthpons x, y, z: if x
>> y then (z - x) >> (z - y) and (x - z) >> (y - z).

D4. The wrensib of a duthpon. The wrensib of a duthpon x is the collection of duthpons y
for which x >> y holds.

Worked out for each duthpon: nakvint to nakvint; rastrast to nakvint, rastrast, espanyr,
yuksol, vorwren and vashtarn; espanyr to nakvint, espanyr and vorwren; yuksol to nakvint
and yuksol; vorwren to nakvint, espanyr and vorwren; vashtarn to nakvint, rastrast,
espanyr, yuksol, vorwren and vashtarn.

## The shape of it

The relation is easiest to see as a height. Each duthpon casts a wrensib over what it
yields to, and the sizes of those shadows here are 1, 2, 3 and 6. Sizes repeat, so the
objects do not line up in single file.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R4 rests on S2 (the Clomorn combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R5 rests on S2 (the Clomorn combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Here is (vorwren - yuksol) - nakvint, reduced without skipping anything.
    vorwren - yuksol = nakvint   (the table for -)
    nakvint - nakvint = nakvint   (the table for -)
The expression comes to nakvint.

Bracketing is not cosmetic, so here is yuksol - (nakvint - vorwren) for contrast.
    nakvint - vorwren = nakvint   (the table for -)
    yuksol - nakvint = nakvint   (the table for -)
The value is nakvint. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test rastrast >> yuksol. The wrensib of rastrast is nakvint, rastrast, espanyr, yuksol,
vorwren and vashtarn, and yuksol lies inside it, so the relation holds.

## A case that breaks

R4. It is not the case that: For all duthpons x and y: if x >> y and y >> x then x = y.
The case that settles it: x = rastrast, y = vashtarn. Anyone carrying this claim over
from a more familiar system will be wrong here, and wrong in a way that propagates.

R5. It is not the case that: For all duthpons x and y, at least one of x >> y and y >> x
holds. The case that settles it: x = espanyr, y = yuksol. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside S2 (the Clomorn combination tables).

What is built on it later: D9 (a pyrlorn), D13 (iskmorn pairs), T10 (wrensibs are nested
along the relation) and T11 (the relation survives combination on the right).

## Proofs

R4. It is not the case that: For all duthpons x and y: if x >> y and y >> x then x = y.

  (1) [S2] Take the case x = rastrast, y = vashtarn, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R5. It is not the case that: For all duthpons x and y, at least one of x >> y and y >> x holds.

  (1) [S2] Take the case x = espanyr, y = yuksol, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the wrensib of a duthpon. Each of these is used by
name later, so the names are worth learning rather than looking up.

Do not carry forward R4 and R5. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x018. Which duthpons y satisfy rastrast >> y? Name them all.
  x019. List the wrensib of espanyr.
  x020. List the wrensib of yuksol.
  x021. List the wrensib of vorwren.
Level 5.
  x013. The following fails in this system: For all duthpons x and y: if x >> y and y >> x then x = y. Name the earliest duthpon, in the order the duthpons were introduced, that witnesses the failure.
  x014. The following fails in this system: For all duthpons x and y, at least one of x >> y and y >> x holds. Name the earliest duthpon, in the order the duthpons were introduced, that witnesses the failure.
