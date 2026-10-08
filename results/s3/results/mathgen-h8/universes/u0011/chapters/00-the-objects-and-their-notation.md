# Chapter 1. The objects and their notation

## Why this chapter

The present chapter develops the Vintreld signature, the Vintreld combination tables and
closure under the first operation.

The standard of proof here is exhaustion. A universal claim about aztfals covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## The tables in full

The table for &. Read the left argument down the side and the right argument across the top.

          |   korrhob    pyrnak  korrglim   lornjen    nakqen    aztclo
-----------------------------------------------------------------------
  korrhob |   korrhob    pyrnak  korrglim   lornjen    nakqen    aztclo
   pyrnak |    pyrnak    pyrnak    nakqen   lornjen    nakqen    aztclo
 korrglim |  korrglim    nakqen  korrglim    aztclo    nakqen    aztclo
  lornjen |   lornjen   lornjen    aztclo   lornjen    aztclo    aztclo
   nakqen |    nakqen    nakqen    nakqen    aztclo    nakqen    aztclo
   aztclo |    aztclo    aztclo    aztclo    aztclo    aztclo    aztclo

Every pair standing in the << relation, grouped by left argument.

  korrhob << korrhob
  pyrnak << korrhob and pyrnak
  korrglim << korrhob and korrglim
  lornjen << korrhob, pyrnak and lornjen
  nakqen << korrhob, pyrnak, korrglim and nakqen
  aztclo << korrhob, pyrnak, korrglim, lornjen, nakqen and aztclo

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A1. Closure under the first operation. For all aztfals x and y, x & y is again a aztfal.

A2. Association of the first operation. For all aztfals x, y, z: (x & y) & z = x & (y &
z).

A3. Commutation of the first operation. For all aztfals x and y: x & y = y & x.

A5. Self combination under the first operation. For every aztfal x: x & x = x.

## The shape of it

A useful mental split: some aztfals are inert under the operation and some are not.
korrhob, pyrnak, korrglim, lornjen, nakqen and aztclo come back unchanged when combined
with themselves, and korrhob, pyrnak, korrglim, lornjen, nakqen and aztclo commute with
everything.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R2 rests on S2 (the Vintreld combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take (korrglim & aztclo) & pyrnak and work it out one step at a time.
    korrglim & aztclo = aztclo   (the table for &)
    aztclo & pyrnak = aztclo   (the table for &)
The expression comes to aztclo.

Move the brackets and the work changes. Take aztclo & (pyrnak & korrglim).
    pyrnak & korrglim = nakqen   (the table for &)
    aztclo & nakqen = aztclo   (the table for &)
The value is aztclo. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test nakqen << korrhob. The tezmi of nakqen is korrhob, pyrnak, korrglim and nakqen, and
korrhob lies inside it, so the relation holds.

## A case that breaks

R2. It is not the case that: For all aztfals x, y, z: if x & y = x & z then y = z. The
case that settles it: x = pyrnak, y = korrhob, z = pyrnak. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

What is built on it later: A4 (a neutral object for the first operation), A6 (an
absorbing object for the first operation), A7 (reflexivity of the relation) and A8
(antisymmetry of the relation).

## Proofs

R2. It is not the case that: For all aztfals x, y, z: if x & y = x & z then y = z.

  (1) [S2] Take the case x = pyrnak, y = korrhob, z = pyrnak, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R2. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 2.
  x001. What aztfal does (lornjen & korrglim) & pyrnak name?
  x005. Which aztfals x satisfy x & pyrnak = nakqen? List them all.
  x006. Solve x & aztclo = aztclo for x, naming every solution.
  x007. Which aztfals x satisfy x & korrglim = nakqen? List them all.
Level 3.
  x002. Reduce (nakqen & nakqen) & (nakqen & lornjen) to a single aztfal.
  x003. Work out the value of (korrglim & korrhob) & (pyrnak & pyrnak).
  x004. What aztfal does (nakqen & nakqen) & (lornjen & lornjen) name?
Level 5.
  x009. The following fails in this system: For all aztfals x, y, z: if x & y = x & z then y = z. Name the earliest aztfal, in the order the aztfals were introduced, that witnesses the failure.
