# Chapter 3. The relation and what it orders

## Why this chapter

What follows was pieced together backwards. The last item of it, agreement of the
relation with the first operation, reflexivity of the relation and antisymmetry of the
relation, was noticed before anyone had a reason to expect it.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

One habit to adopt: when a statement below quantifies over aztfals, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A10. Agreement of the relation with the first operation. For all aztfals x, y, z: if x
<< y then (z & x) << (z & y) and (x & z) << (y & z).

A7. Reflexivity of the relation. For every aztfal x: x << x.

A8. Antisymmetry of the relation. For all aztfals x and y: if x << y and y << x then x =
y.

A9. Transitivity of the relation. For all aztfals x, y, z: if x << y and y << z then x
<< z.

D4. The tezmi of a aztfal. The tezmi of a aztfal x is the collection of aztfals y for
which x << y holds.

Worked out for each aztfal: korrhob to korrhob; pyrnak to korrhob and pyrnak; korrglim
to korrhob and korrglim; lornjen to korrhob, pyrnak and lornjen; nakqen to korrhob,
pyrnak, korrglim and nakqen; aztclo to korrhob, pyrnak, korrglim, lornjen, nakqen and
aztclo.

## The shape of it

The relation is easiest to see as a height. Each aztfal casts a tezmi over what it
yields to, and the sizes of those shadows here are 1, 2, 3, 4 and 6. Sizes repeat, so
the objects do not line up in single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 aztfals the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R3 rests on S2 (the Vintreld combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Take (lornjen & korrhob) & pyrnak and work it out one step at a time.
    lornjen & korrhob = lornjen   (the table for &)
    lornjen & pyrnak = lornjen   (the table for &)
The expression comes to lornjen.

Move the brackets and the work changes. Take korrhob & (pyrnak & lornjen).
    pyrnak & lornjen = lornjen   (the table for &)
    korrhob & lornjen = lornjen   (the table for &)
That gives lornjen, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test aztclo << aztclo. The tezmi of aztclo is korrhob, pyrnak, korrglim, lornjen, nakqen
and aztclo, and aztclo lies inside it, so the relation holds.

## A case that breaks

R3. It is not the case that: For all aztfals x and y, at least one of x << y and y << x
holds. The case that settles it: x = pyrnak, y = korrglim. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: S2 (the Vintreld combination tables).

What is built on it later: D9 (a tarntez), D13 (grixespa pairs), T10 (tezmis are nested
along the relation) and T11 (there is at most one tarntez).

## Proofs

R3. It is not the case that: For all aztfals x and y, at least one of x << y and y << x holds.

  (1) [S2] Take the case x = pyrnak, y = korrglim, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the tezmi of a aztfal. Each of these is used by name
later, so the names are worth learning rather than looking up.

Explicitly not available: R3. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x013. Which aztfals y satisfy pyrnak << y? Name them all.
  x014. List the tezmi of korrglim.
  x015. Which aztfals y satisfy lornjen << y? Name them all.
  x016. Which aztfals y satisfy nakqen << y? Name them all.
  x017. Which aztfals y satisfy aztclo << y? Name them all.
