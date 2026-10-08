# Chapter 1. The objects and their notation

## Why this chapter

So far the vashumbs have been objects to be pushed around. This chapter starts asking
what they are like. We take up the Ponmi signature, the Ponmi combination tables and
closure under the first operation.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
vashumbs that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## The tables in full

The table for ?. Read the left argument down the side and the right argument across the top.

         |  korrvex  keldclo  glimsib   hobtez  korrdri
-------------------------------------------------------
 korrvex |  korrvex  korrvex  korrvex  korrvex  korrvex
 keldclo |  keldclo  korrvex  korrvex  korrvex  korrvex
 glimsib |  glimsib  keldclo  korrvex  korrvex  korrvex
  hobtez |   hobtez  glimsib  keldclo  korrvex  korrvex
 korrdri |  korrdri   hobtez  glimsib  keldclo  korrvex

The table for &. Read the left argument down the side and the right argument across the top.

         |  korrvex  keldclo  glimsib   hobtez  korrdri
-------------------------------------------------------
 korrvex |  korrvex  keldclo  glimsib   hobtez  korrdri
 keldclo |  keldclo  keldclo  glimsib   hobtez  korrdri
 glimsib |  glimsib  glimsib  glimsib   hobtez  korrdri
  hobtez |   hobtez   hobtez   hobtez   hobtez  korrdri
 korrdri |  korrdri  korrdri  korrdri  korrdri  korrdri

Every pair standing in the %% relation, grouped by left argument.

  korrvex %% korrvex
  keldclo %% korrvex and keldclo
  glimsib %% korrvex, keldclo and glimsib
  hobtez %% korrvex, keldclo, glimsib and hobtez
  korrdri %% korrvex, keldclo, glimsib, hobtez and korrdri

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A1. Closure under the first operation. For all vashumbs x and y, x ? y is again a
vashumb.

## The shape of it

A useful mental split: some vashumbs are inert under the operation and some are not.
korrvex come back unchanged when combined with themselves, and none commutes with
everything.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R1 rests on S2 (the Ponmi combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

R2 rests on S2 (the Ponmi combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

R5 rests on S2 (the Ponmi combination tables). The dependence is on the content of those
results, not only on their vocabulary.

R6 rests on S2 (the Ponmi combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

## A worked case

Here is glimsib ? korrvex & keldclo, reduced without skipping anything.
    korrvex & keldclo = keldclo   (the table for &)
    glimsib ? keldclo = keldclo   (the table for ?)
So glimsib ? korrvex & keldclo is keldclo.

Bracketing is not cosmetic, so here is korrvex ? (keldclo ? glimsib) for contrast.
    keldclo ? glimsib = korrvex   (the table for ?)
    korrvex ? korrvex = korrvex   (the table for ?)
That gives korrvex, against keldclo above.

Test keldclo %% keldclo. The brasib of keldclo is korrvex and keldclo, and keldclo lies
inside it, so the relation holds.

## A case that breaks

R1. It is not the case that: For all vashumbs x, y, z: (x ? y) ? z = x ? (y ? z). The
case that settles it: x = keldclo, y = korrvex, z = keldclo, left = korrvex, right =
keldclo. Anyone carrying this claim over from a more familiar system will be wrong here,
and wrong in a way that propagates.

R2. It is not the case that: For all vashumbs x and y: x ? y = y ? x. It fails at x =
korrvex, y = keldclo, left = korrvex, right = keldclo. One case is enough, and this is
the earliest one.

R5. It is not the case that: For every vashumb x: x ? x = x. It fails at x = keldclo,
value = korrvex. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

These results are used again in A2 (closure under the second operation), A3 (association
of the second operation), A4 (commutation of the second operation) and A5 (a neutral
object for the second operation).

## Proofs

R1. It is not the case that: For all vashumbs x, y, z: (x ? y) ? z = x ? (y ? z).

  (1) [S2] Take the case x = keldclo, y = korrvex, z = keldclo, left = korrvex, right = keldclo, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R2. It is not the case that: For all vashumbs x and y: x ? y = y ? x.

  (1) [S2] Take the case x = korrvex, y = keldclo, left = korrvex, right = keldclo, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R5. It is not the case that: For every vashumb x: x ? x = x.

  (1) [S2] Take the case x = keldclo, value = korrvex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R6. It is not the case that: For all vashumbs x, y, z: if x ? y = x ? z then y = z.

  (1) [S2] Take the case x = korrvex, y = korrvex, z = keldclo, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R1, R2, R5 and R6. These were tested and failed, and the failing
cases are recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 1.
  x001. Reduce hobtez ? hobtez to a single vashumb.
  x002. Evaluate keldclo ? hobtez.
  x003. Reduce keldclo ? korrdri to a single vashumb.
  x004. What vashumb does keldclo ? glimsib name?
  x005. What vashumb does korrdri ? korrdri name?
Level 2.
  x006. Evaluate (korrdri ? glimsib) ? hobtez.
  x007. Work out the value of keldclo ? korrdri & korrdri.
  x008. Work out the value of glimsib ? glimsib & korrdri.
  x010. What is glimsib combined with itself 2 times under ??
  x011. Which vashumbs x satisfy x ? hobtez = korrvex? List them all.
  x012. Which vashumbs x satisfy x ? glimsib = korrvex? List them all.
  x013. Which vashumbs x satisfy x ? keldclo = keldclo? List them all.
  x014. Which vashumbs x satisfy x ? keldclo = korrvex? List them all.
Level 3.
  x009. Reduce (keldclo ? keldclo) ? (keldclo ? hobtez) to a single vashumb.
  x015. Evaluate glimsib ? hobtez & korrdri, minding which operation binds tighter.
Level 5.
  x016. The following fails in this system: For all vashumbs x, y, z: (x ? y) ? z = x ? (y ? z). Name the earliest vashumb, in the order the vashumbs were introduced, that witnesses the failure.
  x017. The following fails in this system: For all vashumbs x and y: x ? y = y ? x. Name the earliest vashumb, in the order the vashumbs were introduced, that witnesses the failure.
  x019. The following fails in this system: For every vashumb x: x ? x = x. Name the earliest vashumb, in the order the vashumbs were introduced, that witnesses the failure.
  x020. The following fails in this system: For all vashumbs x, y, z: if x ? y = x ? z then y = z. Name the earliest vashumb, in the order the vashumbs were introduced, that witnesses the failure.
