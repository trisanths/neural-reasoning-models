# Chapter 1. The objects and their notation

## Why this chapter

The practical content of this chapter is the Mornyuk signature, the Mornyuk combination
tables and closure under the first operation. It is the part that shows up in use.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
reldjens that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## The tables in full

The table for <>. Read the left argument down the side and the right argument across the top.

          |   nakopal     kagel  korrreld    iskbra
---------------------------------------------------
  nakopal |   nakopal   nakopal   nakopal   nakopal
    kagel |   nakopal     kagel  korrreld    iskbra
 korrreld |   nakopal  korrreld   nakopal  korrreld
   iskbra |   nakopal    iskbra  korrreld     kagel

The table for #. Read the left argument down the side and the right argument across the top.

          |   nakopal     kagel  korrreld    iskbra
---------------------------------------------------
  nakopal |   nakopal     kagel  korrreld    iskbra
    kagel |     kagel  korrreld    iskbra   nakopal
 korrreld |  korrreld    iskbra   nakopal     kagel
   iskbra |    iskbra   nakopal     kagel  korrreld

Every pair standing in the :: relation, grouped by left argument.

  nakopal :: nakopal, kagel, korrreld and iskbra
  kagel :: kagel, korrreld and iskbra
  korrreld :: korrreld and iskbra
  iskbra :: iskbra

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A1. Closure under the first operation. For all reldjens x and y, x <> y is again a
reldjen.

A2. Association of the first operation. For all reldjens x, y, z: (x <> y) <> z = x <>
(y <> z).

A3. Commutation of the first operation. For all reldjens x and y: x <> y = y <> x.

## The shape of it

Two questions sort the reldjens quickly. Does combining a reldjen with itself change it?
For nakopal and kagel it does not. Does it matter which side it goes on? For nakopal,
kagel, korrreld and iskbra it does not.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R2 rests on S2 (the Mornyuk combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R3 rests on S2 (the Mornyuk combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Evaluate nakopal <> korrreld # kagel. Each line below is one lookup in a table.
    korrreld # kagel = iskbra   (the table for #)
    nakopal <> iskbra = nakopal   (the table for <>)
That leaves nakopal, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take korrreld <> (kagel <> nakopal).
    kagel <> nakopal = nakopal   (the table for <>)
    korrreld <> nakopal = nakopal   (the table for <>)
The value is nakopal. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test kagel :: kagel. The drivor of kagel is kagel, korrreld and iskbra, and kagel lies
inside it, so the relation holds.

## A case that breaks

R2. It is not the case that: For every reldjen x: x <> x = x. It fails at x = korrreld,
value = nakopal. One case is enough, and this is the earliest one.

R3. It is not the case that: For all reldjens x, y, z: if x <> y = x <> z then y = z. It
fails at x = nakopal, y = nakopal, z = kagel. One case is enough, and this is the
earliest one.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

These results are used again in A4 (a neutral object for the first operation), A5 (an
absorbing object for the first operation), A6 (closure under the second operation) and
A7 (association of the second operation).

## Proofs

R2. It is not the case that: For every reldjen x: x <> x = x.

  (1) [S2] Take the case x = korrreld, value = nakopal, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R3. It is not the case that: For all reldjens x, y, z: if x <> y = x <> z then y = z.

  (1) [S2] Take the case x = nakopal, y = nakopal, z = kagel, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R2 and R3. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 1.
  x004. Evaluate korrreld # kagel.
  x005. Evaluate iskbra # kagel.
  x006. Evaluate kagel # korrreld.
Level 2.
  x001. Solve x <> korrreld = nakopal for x, naming every solution.
  x002. Which reldjens x satisfy x <> nakopal = nakopal? List them all.
  x003. Which reldjens x satisfy x <> iskbra = iskbra? List them all.
Level 3.
  x007. Evaluate kagel <> kagel # iskbra, minding which operation binds tighter.
Level 5.
  x009. The following fails in this system: For every reldjen x: x <> x = x. Name the earliest reldjen, in the order the reldjens were introduced, that witnesses the failure.
  x010. The following fails in this system: For all reldjens x, y, z: if x <> y = x <> z then y = z. Name the earliest reldjen, in the order the reldjens were introduced, that witnesses the failure.
