# Chapter 1. The objects and their notation

## Why this chapter

Work through this chapter with the tables in front of you. It covers the Clomorn
signature, the Clomorn combination tables and closure under the first operation, and
each claim can be checked by hand.

One habit to adopt: when a statement below quantifies over duthpons, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## The tables in full

The table for -. Read the left argument down the side and the right argument across the top.

          |   nakvint  rastrast   espanyr    yuksol   vorwren  vashtarn
-----------------------------------------------------------------------
  nakvint |   nakvint   nakvint   nakvint   nakvint   nakvint   nakvint
 rastrast |   nakvint  rastrast   espanyr    yuksol   vorwren  vashtarn
  espanyr |   nakvint   espanyr   vorwren   nakvint   espanyr   vorwren
   yuksol |   nakvint    yuksol   nakvint    yuksol   nakvint    yuksol
  vorwren |   nakvint   vorwren   espanyr   nakvint   vorwren   espanyr
 vashtarn |   nakvint  vashtarn   vorwren    yuksol   espanyr  rastrast

Every pair standing in the >> relation, grouped by left argument.

  nakvint >> nakvint
  rastrast >> nakvint, rastrast, espanyr, yuksol, vorwren and vashtarn
  espanyr >> nakvint, espanyr and vorwren
  yuksol >> nakvint and yuksol
  vorwren >> nakvint, espanyr and vorwren
  vashtarn >> nakvint, rastrast, espanyr, yuksol, vorwren and vashtarn

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A1. Closure under the first operation. For all duthpons x and y, x - y is again a
duthpon.

A2. Association of the first operation. For all duthpons x, y, z: (x - y) - z = x - (y -
z).

A3. Commutation of the first operation. For all duthpons x and y: x - y = y - x.

## The shape of it

A useful mental split: some duthpons are inert under the operation and some are not.
nakvint, rastrast, yuksol and vorwren come back unchanged when combined with themselves,
and nakvint, rastrast, espanyr, yuksol, vorwren and vashtarn commute with everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 duthpons the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R2 rests on S2 (the Clomorn combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R3 rests on S2 (the Clomorn combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Take (yuksol - rastrast) - nakvint and work it out one step at a time.
    yuksol - rastrast = yuksol   (the table for -)
    yuksol - nakvint = nakvint   (the table for -)
The expression comes to nakvint.

Bracketing is not cosmetic, so here is rastrast - (nakvint - yuksol) for contrast.
    nakvint - yuksol = nakvint   (the table for -)
    rastrast - nakvint = nakvint   (the table for -)
That gives nakvint, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test nakvint >> vashtarn. The wrensib of nakvint is nakvint, and vashtarn lies outside
it, so the relation fails.

## A case that breaks

R2. It is not the case that: For every duthpon x: x - x = x. It fails at x = espanyr,
value = vorwren. One case is enough, and this is the earliest one.

R3. It is not the case that: For all duthpons x, y, z: if x - y = x - z then y = z. It
fails at x = nakvint, y = nakvint, z = rastrast. One case is enough, and this is the
earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

What is built on it later: A4 (a neutral object for the first operation), A5 (an
absorbing object for the first operation), A6 (reflexivity of the relation) and A7
(transitivity of the relation).

## Proofs

R2. It is not the case that: For every duthpon x: x - x = x.

  (1) [S2] Take the case x = espanyr, value = vorwren, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R3. It is not the case that: For all duthpons x, y, z: if x - y = x - z then y = z.

  (1) [S2] Take the case x = nakvint, y = nakvint, z = rastrast, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R2 and R3. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 1.
  x001. Work out the value of vorwren - yuksol.
  x002. Evaluate espanyr - espanyr.
  x003. Evaluate yuksol - vorwren.
Level 2.
  x004. Evaluate (rastrast - vashtarn) - espanyr.
  x005. Reduce (yuksol - espanyr) - vorwren to a single duthpon.
  x006. Solve x - nakvint = nakvint for x, naming every solution.
  x007. Solve x - yuksol = yuksol for x, naming every solution.
  x008. Solve x - yuksol = nakvint for x, naming every solution.
  x009. Solve x - vashtarn = vashtarn for x, naming every solution.
Level 5.
  x011. The following fails in this system: For every duthpon x: x - x = x. Name the earliest duthpon, in the order the duthpons were introduced, that witnesses the failure.
  x012. The following fails in this system: For all duthpons x, y, z: if x - y = x - z then y = z. Name the earliest duthpon, in the order the duthpons were introduced, that witnesses the failure.
