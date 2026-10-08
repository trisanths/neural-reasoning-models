# Chapter 4. The second operation and how the two interact

## Why this chapter

What follows was pieced together backwards. The last item of it, closure under the
second operation, association of the second operation and commutation of the second
operation, was noticed before anyone had a reason to expect it.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

The standard of proof here is exhaustion. A universal claim about vashumbs covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A2. Closure under the second operation. For all vashumbs x and y, x & y is again a
vashumb.

A3. Association of the second operation. For all vashumbs x, y, z: (x & y) & z = x & (y
& z).

A4. Commutation of the second operation. For all vashumbs x and y: x & y = y & x.

A5. A neutral object for the second operation. There is a vashumb korrvex with korrvex &
x = x for every x.

A6. Self combination under the second operation. For every vashumb x: x & x = x.

## The shape of it

The interesting content of a two operation system sits in the gap between them: which
one distributes over which, and which vashumbs are fixed by both.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R8 rests on S2 (the Ponmi combination tables). The dependence is on the content of those
results, not only on their vocabulary.

R9 rests on S2 (the Ponmi combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

## A worked case

Here is (hobtez ? glimsib) ? (korrvex ? korrdri), reduced without skipping anything.
    hobtez ? glimsib = keldclo   (the table for ?)
    korrvex ? korrdri = korrvex   (the table for ?)
    keldclo ? korrvex = keldclo   (the table for ?)
So (hobtez ? glimsib) ? (korrvex ? korrdri) is keldclo.

Move the brackets and the work changes. Take glimsib ? (korrvex ? hobtez).
    korrvex ? hobtez = korrvex   (the table for ?)
    glimsib ? korrvex = glimsib   (the table for ?)
The value is glimsib, not keldclo.

Test hobtez %% korrdri. The brasib of hobtez is korrvex, keldclo, glimsib and hobtez,
and korrdri lies outside it, so the relation fails.

## A case that breaks

R8. It is not the case that: For all vashumbs x, y, z: x & (y ? z) = (x & y) ? (x & z),
and the same on the right. It fails at x = keldclo, y = korrvex, z = korrvex, left =
keldclo, right = korrvex. One case is enough, and this is the earliest one.

R9. It is not the case that: For all vashumbs x and y: x ? (x & y) = x and x & (x ? y) =
x. It fails at x = keldclo, y = korrvex, value = korrvex. One case is enough, and this
is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside S2 (the Ponmi combination tables).

## Proofs

R8. It is not the case that: For all vashumbs x, y, z: x & (y ? z) = (x & y) ? (x & z), and the same on the right.

  (1) [S2] Take the case x = keldclo, y = korrvex, z = korrvex, left = keldclo, right = korrvex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R9. It is not the case that: For all vashumbs x and y: x ? (x & y) = x and x & (x ? y) = x.

  (1) [S2] Take the case x = keldclo, y = korrvex, value = korrvex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R8 and R9. A later argument that quietly assumes one of these
is wrong, and the counterexamples above say exactly where.

## Exercises

No exercises here. Every question this chapter suggested turned out to be answerable
from the question itself, so all of them were discarded.
