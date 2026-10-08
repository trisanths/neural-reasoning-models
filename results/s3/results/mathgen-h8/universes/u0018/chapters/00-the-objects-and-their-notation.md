# Chapter 1. The objects and their notation

## Why this chapter

The results collected here were not found in this order. The Nyrazt signature, the
Nyrazt combination tables and closure under the first operation came first, and the rest
was assembled around that once the pattern was visible.

The standard of proof here is exhaustion. A universal claim about naksols covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## The tables in full

The table for %. Read the left argument down the side and the right argument across the top.

         |  wrenpyr  vexlorn   vexnak  glimzam  reldxil   pyrxil
----------------------------------------------------------------
 wrenpyr |  wrenpyr  vexlorn   vexnak  glimzam  reldxil   pyrxil
 vexlorn |  vexlorn   vexnak  glimzam  reldxil   pyrxil  wrenpyr
  vexnak |   vexnak  glimzam  reldxil   pyrxil  wrenpyr  vexlorn
 glimzam |  glimzam  reldxil   pyrxil  wrenpyr  vexlorn   vexnak
 reldxil |  reldxil   pyrxil  wrenpyr  vexlorn   vexnak  glimzam
  pyrxil |   pyrxil  wrenpyr  vexlorn   vexnak  glimzam  reldxil

The table for <>. Read the left argument down the side and the right argument across the top.

         |  wrenpyr  vexlorn   vexnak  glimzam  reldxil   pyrxil
----------------------------------------------------------------
 wrenpyr |  wrenpyr  vexlorn   vexnak  glimzam  reldxil   pyrxil
 vexlorn |  vexlorn  vexlorn   vexnak  glimzam  reldxil   pyrxil
  vexnak |   vexnak   vexnak   vexnak  glimzam  reldxil   pyrxil
 glimzam |  glimzam  glimzam  glimzam  glimzam  reldxil   pyrxil
 reldxil |  reldxil  reldxil  reldxil  reldxil  reldxil   pyrxil
  pyrxil |   pyrxil   pyrxil   pyrxil   pyrxil   pyrxil   pyrxil

Every pair standing in the >- relation, grouped by left argument.

  wrenpyr >- wrenpyr, vexlorn, vexnak, glimzam, reldxil and pyrxil
  vexlorn >- vexlorn, vexnak, glimzam, reldxil and pyrxil
  vexnak >- vexnak, glimzam, reldxil and pyrxil
  glimzam >- glimzam, reldxil and pyrxil
  reldxil >- reldxil and pyrxil
  pyrxil >- pyrxil

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A1. Closure under the first operation. For all naksols x and y, x % y is again a naksol.

A2. Association of the first operation. For all naksols x, y, z: (x % y) % z = x % (y %
z).

A3. Commutation of the first operation. For all naksols x and y: x % y = y % x.

A6. Cancellation in the first operation. For all naksols x, y, z: if x % y = x % z then
y = z.

## The shape of it

Two questions sort the naksols quickly. Does combining a naksol with itself change it?
For wrenpyr it does not. Does it matter which side it goes on? For wrenpyr, vexlorn,
vexnak, glimzam, reldxil and pyrxil it does not.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 naksols the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R1 rests on S2 (the Nyrazt combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

## A worked case

Here is pyrxil % vexnak <> wrenpyr, reduced without skipping anything.
    vexnak <> wrenpyr = vexnak   (the table for <>)
    pyrxil % vexnak = vexlorn   (the table for %)
So pyrxil % vexnak <> wrenpyr is vexlorn.

A companion case, vexnak % (wrenpyr % pyrxil), to show what the brackets are doing.
    wrenpyr % pyrxil = pyrxil   (the table for %)
    vexnak % pyrxil = vexlorn   (the table for %)
That gives vexlorn, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test wrenpyr >- vexlorn. The tufex of wrenpyr is wrenpyr, vexlorn, vexnak, glimzam,
reldxil and pyrxil, and vexlorn lies inside it, so the relation holds.

## A case that breaks

R1. It is not the case that: For every naksol x: x % x = x. It fails at x = vexlorn,
value = vexnak. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

What is built on it later: A4 (a neutral object for the first operation), A5 (reversal
under the first operation), A7 (closure under the second operation) and A8 (association
of the second operation).

## Proofs

R1. It is not the case that: For every naksol x: x % x = x.

  (1) [S2] Take the case x = vexlorn, value = vexnak, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R1. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 1.
  x001. Evaluate reldxil % reldxil.
  x002. What naksol does vexnak % pyrxil name?
  x003. What naksol does reldxil % vexlorn name?
  x004. Work out the value of pyrxil % reldxil.
  x005. Work out the value of vexnak % reldxil.
  x006. Evaluate pyrxil % vexnak.
Level 2.
  x007. Work out the value of reldxil % pyrxil <> reldxil.
  x008. Evaluate (vexlorn % wrenpyr) % vexnak.
  x009. What naksol does (glimzam % vexnak) % vexnak name?
  x010. Work out the value of (vexnak % pyrxil) % glimzam.
  x012. What is reldxil combined with itself 3 times under %?
  x013. Evaluate vexnak^3.
  x014. Evaluate pyrxil % vexlorn'.
  x015. Evaluate pyrxil % glimzam'.
  x016. Which naksols x satisfy x % reldxil = pyrxil? List them all.
  x017. Which naksols x satisfy x % glimzam = pyrxil? List them all.
  x018. Which naksols x satisfy x % glimzam = glimzam? List them all.
  x019. Which naksols x satisfy x % vexnak = vexlorn? List them all.
Level 3.
  x011. What naksol does (vexnak % vexlorn) % (reldxil % reldxil) name?
  x020. Evaluate vexnak % vexlorn <> wrenpyr, minding which operation binds tighter.
