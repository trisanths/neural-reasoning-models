# Chapter 1. The objects and their notation

## Why this chapter

Work through this chapter with the tables in front of you. It covers the Bramorn
signature, the Bramorn combination tables and closure under the first operation, and
each claim can be checked by hand.

One habit to adopt: when a statement below quantifies over zelbras, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## The tables in full

The table for *. Read the left argument down the side and the right argument across the top.

         |  tarnnyr   cloxil   isktez    iskmi
----------------------------------------------
 tarnnyr |  tarnnyr  tarnnyr  tarnnyr  tarnnyr
  cloxil |   cloxil  tarnnyr  tarnnyr  tarnnyr
  isktez |   isktez   cloxil  tarnnyr  tarnnyr
   iskmi |    iskmi   isktez   cloxil  tarnnyr

The table for -. Read the left argument down the side and the right argument across the top.

         |  tarnnyr   cloxil   isktez    iskmi
----------------------------------------------
 tarnnyr |  tarnnyr   cloxil   isktez    iskmi
  cloxil |   cloxil   cloxil   isktez    iskmi
  isktez |   isktez   isktez   isktez    iskmi
   iskmi |    iskmi    iskmi    iskmi    iskmi

Every pair standing in the <~ relation, grouped by left argument.

  tarnnyr <~ tarnnyr, cloxil, isktez and iskmi
  cloxil <~ cloxil, isktez and iskmi
  isktez <~ isktez and iskmi
  iskmi <~ iskmi

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A1. Closure under the first operation. For all zelbras x and y, x * y is again a zelbra.

## The shape of it

Two questions sort the zelbras quickly. Does combining a zelbra with itself change it?
For tarnnyr it does not. Does it matter which side it goes on? It always does.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R1 rests on S2 (the Bramorn combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R2 rests on S2 (the Bramorn combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R5 rests on S2 (the Bramorn combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R6 rests on S2 (the Bramorn combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Evaluate isktez * cloxil - iskmi. Each line below is one lookup in a table.
    cloxil - iskmi = iskmi   (the table for -)
    isktez * iskmi = tarnnyr   (the table for *)
The expression comes to tarnnyr.

A companion case, cloxil * (iskmi * isktez), to show what the brackets are doing.
    iskmi * isktez = cloxil   (the table for *)
    cloxil * cloxil = tarnnyr   (the table for *)
That gives tarnnyr, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test tarnnyr <~ isktez. The opalpyr of tarnnyr is tarnnyr, cloxil, isktez and iskmi, and
isktez lies inside it, so the relation holds.

## A case that breaks

R1. It is not the case that: For all zelbras x, y, z: (x * y) * z = x * (y * z). The
case that settles it: x = cloxil, y = tarnnyr, z = cloxil, left = tarnnyr, right =
cloxil. Anyone carrying this claim over from a more familiar system will be wrong here,
and wrong in a way that propagates.

R2. It is not the case that: For all zelbras x and y: x * y = y * x. It fails at x =
tarnnyr, y = cloxil, left = tarnnyr, right = cloxil. One case is enough, and this is the
earliest one.

R5. It is not the case that: For every zelbra x: x * x = x. The case that settles it: x
= cloxil, value = tarnnyr. Anyone carrying this claim over from a more familiar system
will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

What is built on it later: A2 (closure under the second operation), A3 (association of
the second operation), A4 (commutation of the second operation) and A5 (a neutral object
for the second operation).

## Proofs

R1. It is not the case that: For all zelbras x, y, z: (x * y) * z = x * (y * z).

  (1) [S2] Take the case x = cloxil, y = tarnnyr, z = cloxil, left = tarnnyr, right = cloxil, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R2. It is not the case that: For all zelbras x and y: x * y = y * x.

  (1) [S2] Take the case x = tarnnyr, y = cloxil, left = tarnnyr, right = cloxil, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R5. It is not the case that: For every zelbra x: x * x = x.

  (1) [S2] Take the case x = cloxil, value = tarnnyr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R6. It is not the case that: For all zelbras x, y, z: if x * y = x * z then y = z.

  (1) [S2] Take the case x = tarnnyr, y = tarnnyr, z = cloxil, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R1, R2, R5 and R6. These were tested and failed, and the failing
cases are recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 1.
  x001. Reduce cloxil * iskmi to a single zelbra.
  x002. Reduce iskmi * cloxil to a single zelbra.
  x003. Evaluate iskmi * iskmi.
  x004. Work out the value of iskmi * isktez.
  x005. Work out the value of isktez * iskmi.
Level 2.
  x006. What zelbra does iskmi * cloxil - cloxil name?
  x007. What is iskmi combined with itself 3 times under *?
  x008. Solve x * iskmi = tarnnyr for x, naming every solution.
  x009. Which zelbras x satisfy x * cloxil = tarnnyr? List them all.
  x010. Solve x * cloxil = cloxil for x, naming every solution.
Level 5.
  x011. The following fails in this system: For all zelbras x, y, z: (x * y) * z = x * (y * z). Name the earliest zelbra, in the order the zelbras were introduced, that witnesses the failure.
  x012. The following fails in this system: For all zelbras x and y: x * y = y * x. Name the earliest zelbra, in the order the zelbras were introduced, that witnesses the failure.
  x014. The following fails in this system: For every zelbra x: x * x = x. Name the earliest zelbra, in the order the zelbras were introduced, that witnesses the failure.
  x015. The following fails in this system: For all zelbras x, y, z: if x * y = x * z then y = z. Name the earliest zelbra, in the order the zelbras were introduced, that witnesses the failure.
