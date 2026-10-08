# Chapter 3. The relation and what it orders

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is comparability of
every pair, agreement of the relation with the second operation and reflexivity of the
relation.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
shenopals that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A10. Comparability of every pair. For all shenopals x and y, at least one of x :: y and
y :: x holds.

A11. Agreement of the relation with the second operation. For all shenopals x, y, z: if
x :: y then (z & x) :: (z & y) and (x & z) :: (y & z).

A7. Reflexivity of the relation. For every shenopal x: x :: x.

A8. Antisymmetry of the relation. For all shenopals x and y: if x :: y and y :: x then x
= y.

A9. Transitivity of the relation. For all shenopals x, y, z: if x :: y and y :: z then x
:: z.

D4. The muxsib of a shenopal. The muxsib of a shenopal x is the collection of shenopals
y for which x :: y holds.

Worked out for each shenopal: opallorn to opallorn, qenthra, grixlum, vorpon and pontu;
qenthra to qenthra, grixlum, vorpon and pontu; grixlum to grixlum, vorpon and pontu;
vorpon to vorpon and pontu; pontu to pontu.

## The shape of it

The relation is easiest to see as a height. Each shenopal casts a muxsib over what it
yields to, and the sizes of those shadows here are 1, 2, 3, 4 and 5. No two are the same
size, so the objects line up in a single file.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R10 rests on S2 (the Vintfex combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Here is vorpon % grixlum & qenthra, reduced without skipping anything.
    grixlum & qenthra = grixlum   (the table for &)
    vorpon % grixlum = qenthra   (the table for %)
That leaves qenthra, and no other reading of the notation gives anything else.

A companion case, grixlum % (qenthra % vorpon), to show what the brackets are doing.
    qenthra % vorpon = opallorn   (the table for %)
    grixlum % opallorn = grixlum   (the table for %)
That gives grixlum, against qenthra above.

One decision about the relation, since deciding is as much a skill as computing. Does
vorpon :: opallorn hold? Read off what vorpon stands over: vorpon and pontu. opallorn is
not among them, so it fails.

## A case that breaks

R10. It is not the case that: For all shenopals x, y, z: if x :: y then (z % x) :: (z %
y) and (x % z) :: (y % z). It fails at x = opallorn, y = qenthra, z = qenthra, side =
left. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside S2 (the Vintfex combination tables).

These results are used again in D8 (a drisol), D11 (aztgel pairs), T5 (muxsibs are
nested along the relation) and T6 (there is at most one drisol).

## Proofs

R10. It is not the case that: For all shenopals x, y, z: if x :: y then (z % x) :: (z % y) and (x % z) :: (y % z).

  (1) [S2] Take the case x = opallorn, y = qenthra, z = qenthra, side = left, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the muxsib of a shenopal. Later chapters state their results in these
terms and do not restate the definitions.

Explicitly not available: R10. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x029. Which shenopals y satisfy opallorn :: y? Name them all.
  x030. List the muxsib of qenthra.
  x031. List the muxsib of grixlum.
  x032. Which shenopals y satisfy vorpon :: y? Name them all.
Level 5.
  x025. The following fails in this system: For all shenopals x, y, z: if x :: y then (z % x) :: (z % y) and (x % z) :: (y % z). Name the earliest shenopal, in the order the shenopals were introduced, that witnesses the failure.
