# Chapter 4. The second operation and how the two interact

## Why this chapter

So far the zelbras have been objects to be pushed around. This chapter starts asking
what they are like. We take up closure under the second operation, association of the
second operation and commutation of the second operation.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over zelbras, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A2. Closure under the second operation. For all zelbras x and y, x - y is again a
zelbra.

A3. Association of the second operation. For all zelbras x, y, z: (x - y) - z = x - (y -
z).

A4. Commutation of the second operation. For all zelbras x and y: x - y = y - x.

A5. A neutral object for the second operation. There is a zelbra tarnnyr with tarnnyr -
x = x for every x.

A6. Self combination under the second operation. For every zelbra x: x - x = x.

## The shape of it

The interesting content of a two operation system sits in the gap between them: which
one distributes over which, and which zelbras are fixed by both.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R8 rests on S2 (the Bramorn combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R9 rests on S2 (the Bramorn combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Evaluate (tarnnyr * isktez) * (cloxil * iskmi). Each line below is one lookup in a
table.
    tarnnyr * isktez = tarnnyr   (the table for *)
    cloxil * iskmi = tarnnyr   (the table for *)
    tarnnyr * tarnnyr = tarnnyr   (the table for *)
So (tarnnyr * isktez) * (cloxil * iskmi) is tarnnyr.

Move the brackets and the work changes. Take isktez * (cloxil * tarnnyr).
    cloxil * tarnnyr = cloxil   (the table for *)
    isktez * cloxil = cloxil   (the table for *)
The value is cloxil, not tarnnyr.

One decision about the relation, since deciding is as much a skill as computing. Does
cloxil <~ tarnnyr hold? Read off what cloxil stands over: cloxil, isktez and iskmi.
tarnnyr is not among them, so it fails.

## A case that breaks

R8. It is not the case that: For all zelbras x, y, z: x - (y * z) = (x - y) * (x - z),
and the same on the right. The case that settles it: x = cloxil, y = tarnnyr, z =
tarnnyr, left = cloxil, right = tarnnyr. Anyone carrying this claim over from a more
familiar system will be wrong here, and wrong in a way that propagates.

R9. It is not the case that: For all zelbras x and y: x * (x - y) = x and x - (x * y) =
x. The case that settles it: x = cloxil, y = tarnnyr, value = tarnnyr. Anyone carrying
this claim over from a more familiar system will be wrong here, and wrong in a way that
propagates.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: S2 (the Bramorn combination tables).

## Proofs

R8. It is not the case that: For all zelbras x, y, z: x - (y * z) = (x - y) * (x - z), and the same on the right.

  (1) [S2] Take the case x = cloxil, y = tarnnyr, z = tarnnyr, left = cloxil, right = tarnnyr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R9. It is not the case that: For all zelbras x and y: x * (x - y) = x and x - (x * y) = x.

  (1) [S2] Take the case x = cloxil, y = tarnnyr, value = tarnnyr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R8 and R9. These were tested and failed, and the failing cases are
recorded above.

## Exercises

No exercises here. Every question this chapter suggested turned out to be answerable
from the question itself, so all of them were discarded.
