# Chapter 3. The relation and what it orders

## Why this chapter

The present chapter develops reflexivity of the relation, antisymmetry of the relation
and transitivity of the relation.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over qenjens, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A11. Reflexivity of the relation. For every qenjen x: x <~ x.

A12. Antisymmetry of the relation. For all qenjens x and y: if x <~ y and y <~ x then x
= y.

A13. Transitivity of the relation. For all qenjens x, y, z: if x <~ y and y <~ z then x
<~ z.

A14. Comparability of every pair. For all qenjens x and y, at least one of x <~ y and y
<~ x holds.

A15. Agreement of the relation with the second operation. For all qenjens x, y, z: if x
<~ y then (z |= x) <~ (z |= y) and (x |= z) <~ (y |= z).

D4. The opalglim of a qenjen. The opalglim of a qenjen x is the collection of qenjens y
for which x <~ y holds.

Worked out for each qenjen: yuktarn to yuktarn, xilzam, shentu, nyrazt and cloreld;
xilzam to xilzam, shentu, nyrazt and cloreld; shentu to shentu, nyrazt and cloreld;
nyrazt to nyrazt and cloreld; cloreld to cloreld.

## The shape of it

The relation is easiest to see as a height. Each qenjen casts a opalglim over what it
answers to, and the sizes of those shadows here are 1, 2, 3, 4 and 5. No two are the
same size, so the objects line up in a single file.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R6 rests on S2 (the Quilumb combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take nyrazt + cloreld |= shentu and work it out one step at a time.
    cloreld |= shentu = shentu   (the table for |=)
    nyrazt + shentu = xilzam   (the table for +)
That leaves xilzam, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is cloreld + (shentu + nyrazt) for contrast.
    shentu + nyrazt = xilzam   (the table for +)
    cloreld + xilzam = cloreld   (the table for +)
That gives cloreld, against xilzam above.

Test nyrazt <~ xilzam. The opalglim of nyrazt is nyrazt and cloreld, and xilzam lies
outside it, so the relation fails.

## A case that breaks

R6. It is not the case that: For all qenjens x, y, z: if x <~ y then (z + x) <~ (z + y)
and (x + z) <~ (y + z). It fails at x = xilzam, y = shentu, z = nyrazt, side = left. One
case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: S2 (the Quilumb combination tables).

What is built on it later: D9 (a tezwren), D13 (duthsib pairs), T9 (opalglims are nested
along the relation) and T10 (there is at most one tezwren).

## Proofs

R6. It is not the case that: For all qenjens x, y, z: if x <~ y then (z + x) <~ (z + y) and (x + z) <~ (y + z).

  (1) [S2] Take the case x = xilzam, y = shentu, z = nyrazt, side = left, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the opalglim of a qenjen. Later chapters state their results in these
terms and do not restate the definitions.

Explicitly not available: R6. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 5.
  x011. The following fails in this system: For all qenjens x, y, z: if x <~ y then (z + x) <~ (z + y) and (x + z) <~ (y + z). Name the earliest qenjen, in the order the qenjens were introduced, that witnesses the failure.
