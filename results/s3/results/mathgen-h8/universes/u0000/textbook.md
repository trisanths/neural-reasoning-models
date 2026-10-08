# The Ponmi system

The Ponmi system is small enough to hold in the hand and strange enough to be worth the
trouble. It has 5 vashumbs, two operations, and one relation, and nothing else.

The vashumbs are written korrvex, keldclo, glimsib, hobtez and korrdri. The first
operation is written ?. The second is written & and binds more tightly, so x ? y & z
means x ? (y & z). The relation is written %%; where it holds between two vashumbs we
say the left one governs the right one. Both operations associate to the left when
written without brackets, and brackets override that. Repeated combination is
abbreviated: x^3 means x ? x ? x.

A warning that will be repeated because it is the one readers ignore: nothing here is
inherited from arithmetic. Familiar names have been avoided on purpose. Where a law of
arithmetic happens to hold it is stated and checked, and where it fails a counterexample
is given.

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

# Chapter 2. Neutral objects and reversal

## Why this chapter

We turn to the system does not have a neutral object for the first operation, the system
does not have reversal under the first operation and the system does not have an
absorbing object for the first operation. The treatment is self contained given the
material already established.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about vashumbs covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

The neutral vashumb is the one that does nothing. That sounds trivial and is not: almost
every result in this chapter is an argument about what doing nothing forces.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R3 rests on S2 (the Ponmi combination tables). The dependence is on the content of those
results, not only on their vocabulary.

R4 rests on S2 (the Ponmi combination tables). The dependence is on the content of those
results, not only on their vocabulary.

R7 rests on S2 (the Ponmi combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

## A worked case

Evaluate (korrvex ? glimsib) ? (keldclo ? korrdri). Each line below is one lookup in a
table.
    korrvex ? glimsib = korrvex   (the table for ?)
    keldclo ? korrdri = korrvex   (the table for ?)
    korrvex ? korrvex = korrvex   (the table for ?)
The expression comes to korrvex.

Move the brackets and the work changes. Take glimsib ? (keldclo ? korrvex).
    keldclo ? korrvex = keldclo   (the table for ?)
    glimsib ? keldclo = keldclo   (the table for ?)
That gives keldclo, against korrvex above.

One decision about the relation, since deciding is as much a skill as computing. Does
keldclo %% hobtez hold? Read off what keldclo stands over: korrvex and keldclo. hobtez
is not among them, so it fails.

## A case that breaks

R3. There is no vashumb e with e ? x = x ? e = x for every vashumb x. The case that
settles it: reason = no two sided identity exists. Anyone carrying this claim over from
a more familiar system will be wrong here, and wrong in a way that propagates.

R4. Some vashumb x admits no vashumb y for which x ? y and y ? x both land on a neutral
object. It fails at reason = no identity, so inverses are not defined. One case is
enough, and this is the earliest one.

R7. There is no vashumb z with z ? x = x ? z = z for every vashumb x. It fails at reason
= no absorbing element. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside S2 (the Ponmi combination tables).

## Proofs

R3. There is no vashumb e with e ? x = x ? e = x for every vashumb x.

  (1) [S2] Take the case reason = no two sided identity exists, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R4. Some vashumb x admits no vashumb y for which x ? y and y ? x both land on a neutral object.

  (1) [S2] Take the case reason = no identity, so inverses are not defined, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R7. There is no vashumb z with z ? x = x ? z = z for every vashumb x.

  (1) [S2] Take the case reason = no absorbing element, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R3, R4 and R7. These were tested and failed, and the failing cases
are recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 5.
  x018. The following fails in this system: Some vashumb x admits no vashumb y for which x ? y and y ? x both land on a neutral object. Name the earliest vashumb, in the order the vashumbs were introduced, that witnesses the failure.

# Chapter 3. The relation and what it orders

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is comparability of
every pair, agreement of the relation with the second operation and reflexivity of the
relation.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
vashumbs that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A10. Comparability of every pair. For all vashumbs x and y, at least one of x %% y and y
%% x holds.

A11. Agreement of the relation with the second operation. For all vashumbs x, y, z: if x
%% y then (z & x) %% (z & y) and (x & z) %% (y & z).

A7. Reflexivity of the relation. For every vashumb x: x %% x.

A8. Antisymmetry of the relation. For all vashumbs x and y: if x %% y and y %% x then x
= y.

A9. Transitivity of the relation. For all vashumbs x, y, z: if x %% y and y %% z then x
%% z.

D4. The brasib of a vashumb. The brasib of a vashumb x is the collection of vashumbs y
for which x %% y holds.

Worked out for each vashumb: korrvex to korrvex; keldclo to korrvex and keldclo; glimsib
to korrvex, keldclo and glimsib; hobtez to korrvex, keldclo, glimsib and hobtez; korrdri
to korrvex, keldclo, glimsib, hobtez and korrdri.

## The shape of it

Think of %% as pointing downhill. The brasib of a vashumb is everything downhill of it,
and those shadows here have sizes 1, 2, 3, 4 and 5.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 vashumbs the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R10 rests on S2 (the Ponmi combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Here is keldclo ? korrdri & glimsib, reduced without skipping anything.
    korrdri & glimsib = korrdri   (the table for &)
    keldclo ? korrdri = korrvex   (the table for ?)
So keldclo ? korrdri & glimsib is korrvex.

A companion case, korrdri ? (glimsib ? keldclo), to show what the brackets are doing.
    glimsib ? keldclo = keldclo   (the table for ?)
    korrdri ? keldclo = hobtez   (the table for ?)
That gives hobtez, against korrvex above.

Test hobtez %% korrdri. The brasib of hobtez is korrvex, keldclo, glimsib and hobtez,
and korrdri lies outside it, so the relation fails.

## A case that breaks

R10. It is not the case that: For all vashumbs x, y, z: if x %% y then (z ? x) %% (z ?
y) and (x ? z) %% (y ? z). The case that settles it: x = keldclo, y = korrvex, z =
keldclo, side = left. Anyone carrying this claim over from a more familiar system will
be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside S2 (the Ponmi combination tables).

These results are used again in D8 (a vexlum), D11 (ovijen pairs), T5 (brasibs are
nested along the relation) and T6 (there is at most one vexlum).

## Proofs

R10. It is not the case that: For all vashumbs x, y, z: if x %% y then (z ? x) %% (z ? y) and (x ? z) %% (y ? z).

  (1) [S2] Take the case x = keldclo, y = korrvex, z = keldclo, side = left, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the brasib of a vashumb. Each of these is used by name
later, so the names are worth learning rather than looking up.

Do not carry forward R10. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x025. Which vashumbs y satisfy keldclo %% y? Name them all.
  x026. List the brasib of glimsib.
  x027. List the brasib of hobtez.
Level 5.
  x021. The following fails in this system: For all vashumbs x, y, z: if x %% y then (z ? x) %% (z ? y) and (x ? z) %% (y ? z). Name the earliest vashumb, in the order the vashumbs were introduced, that witnesses the failure.

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

# Chapter 5. Combining objects

## Why this chapter

The practical content of this chapter is tarnmux vashumbs, vashumbs that yukdri and
hurnisk collections. It is the part that shows up in use.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
vashumbs that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D1. Tarnmux vashumbs. A vashumb x is called tarnmux when x ? x = x.

In this system that picks out korrvex, which is 1 of the 5 vashumbs.

D2. Vashumbs that yukdri. Two vashumbs x and y are said to yukdri when x ? y = y ? x.

D3. Hurnisk collections. A collection S of vashumbs is hurnisk when x ? y belongs to S
for every pair x, y drawn from S.

## The shape of it

Picture the reldmi as what happens when you start with one vashumb and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 5 vashumbs, that stops. In this system the sizes it stops at are 1 and 2.

A useful mental split: some vashumbs are inert under the operation and some are not.
korrvex come back unchanged when combined with themselves, and none commutes with
everything.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Nothing is derived in this chapter. It lays down material that later chapters draw on.

## A worked case

Take keldclo ? korrdri & glimsib and work it out one step at a time.
    korrdri & glimsib = korrdri   (the table for &)
    keldclo ? korrdri = korrvex   (the table for ?)
That leaves korrvex, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take korrdri ? (glimsib ? keldclo).
    glimsib ? keldclo = keldclo   (the table for ?)
    korrdri ? keldclo = hobtez   (the table for ?)
That gives hobtez, against korrvex above.

Test keldclo %% keldclo. The brasib of keldclo is korrvex and keldclo, and keldclo lies
inside it, so the relation holds.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of vashumbs that come back
unchanged from themselves: korrvex. Assuming more of them than that is the mistake to
avoid.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by closure under the first operation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A1 (closure under the first operation).

What is built on it later: D5 (the yukfex), D6 (the mimorn), D7 (the reldmi of a
vashumb) and T1 (the reldmi of a vashumb is hurnisk).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

New vocabulary from this chapter: tarnmux vashumbs, vashumbs that yukdri and hurnisk
collections. Each of these is used by name later, so the names are worth learning rather
than looking up.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x022. Which vashumbs make up the tarnmux? Name them all.
  x023. How many vashumbs lie in the smallest hurnisk collection containing keldclo?
  x024. How many vashumbs lie in the smallest hurnisk collection containing glimsib?

# Chapter 6. The relation and what it orders (2)

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through ovijen pairs, a vexlum and
where the relation reads the same in both directions breaks down.

Nothing here stands on its own. The arguments lean on chapter 3, and a reader who has
skipped it will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over vashumbs, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D11. Ovijen pairs. Two distinct vashumbs x and y form a ovijen pair when x %% y and y %%
x both hold, that is, when each lies in the brasib of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D8. A vexlum. A vashumb f is a vexlum when f %% y holds for every vashumb y, that is,
when the brasib of f is the whole system.

Running the definition over every vashumb leaves korrdri.

## The shape of it

The relation is easiest to see as a height. Each vashumb casts a brasib over what it
governs, and the sizes of those shadows here are 1, 2, 3, 4 and 5. No two are the same
size, so the objects line up in a single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 vashumbs the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R15 rests on D4 (the brasib of a vashumb). Remove any one of them and the statement
stops making sense, not merely stops being provable.

T5 rests on D4 (the brasib of a vashumb) and A9 (transitivity of the relation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Take (glimsib ? hobtez) ? (keldclo ? korrdri) and work it out one step at a time.
    glimsib ? hobtez = korrvex   (the table for ?)
    keldclo ? korrdri = korrvex   (the table for ?)
    korrvex ? korrvex = korrvex   (the table for ?)
That leaves korrvex, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take hobtez ? (keldclo ? glimsib).
    keldclo ? glimsib = korrvex   (the table for ?)
    hobtez ? korrvex = hobtez   (the table for ?)
The value is hobtez, not korrvex.

Test hobtez %% keldclo. The brasib of hobtez is korrvex, keldclo, glimsib and hobtez,
and keldclo lies inside it, so the relation holds.

## A case that breaks

R15. It is not the case that: If x %% y then y %% x. It fails at x = keldclo, y =
korrvex. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by transitivity of the relation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A9 (transitivity of the relation) and D4 (the brasib of a vashumb).

What is built on it later: T6 (there is at most one vexlum), T7 (the system has a
vexlum) and T8 (no ovijen pairs exist).

## Proofs

R15. It is not the case that: If x %% y then y %% x.

  (1) [S2] Take the case x = keldclo, y = korrvex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T5. If y lies in the brasib of x, then the brasib of y is contained in the brasib of x.

  (1) [D4] Let y satisfy x %% y and let z satisfy y %% z.
  (2) [A9] Transitivity gives x %% z.
  (3) [D4] So every member of the brasib of y is a member of that of x.

Checked over 125 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: ovijen pairs and a vexlum. Each of these is used by
name later, so the names are worth learning rather than looking up.

Established here and safe to use: T5.

Do not carry forward R15. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x036. List every vashumb in the vexlum.
  x050. The result above concerns brasibs. List the brasib of keldclo.
  x051. The result above concerns brasibs. List the brasib of glimsib.
Level 5.
  x055. The following fails in this system: If x %% y then y %% x. Name the earliest vashumb, in the order the vashumbs were introduced, that witnesses the failure.

# Chapter 7. Combining objects (2)

## Why this chapter

The present chapter develops the yukfex, the mimorn and the reldmi of a vashumb.

Nothing here stands on its own. The arguments lean on chapter 5, and a reader who has
skipped it will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
vashumbs that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D5. The yukfex. The yukfex of the system is the collection of vashumbs that yukdri with
every vashumb.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D6. The mimorn. The mimorn is the collection of all tarnmux vashumbs.

Running the definition over every vashumb leaves korrvex.

D7. The reldmi of a vashumb. The reldmi of a vashumb x, written [x], is the smallest
hurnisk collection that contains x.

Worked out for each vashumb: korrvex to korrvex; keldclo to korrvex and keldclo; glimsib
to korrvex and glimsib; hobtez to korrvex and hobtez; korrdri to korrvex and korrdri.

## The shape of it

Picture the reldmi as what happens when you start with one vashumb and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 5 vashumbs, that stops. In this system the sizes it stops at are 1 and 2.

A useful mental split: some vashumbs are inert under the operation and some are not.
korrvex come back unchanged when combined with themselves, and none commutes with
everything.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Nothing is derived in this chapter. It lays down material that later chapters draw on.

## A worked case

Here is korrvex ? keldclo & hobtez, reduced without skipping anything.
    keldclo & hobtez = hobtez   (the table for &)
    korrvex ? hobtez = korrvex   (the table for ?)
The expression comes to korrvex.

Bracketing is not cosmetic, so here is keldclo ? (hobtez ? korrvex) for contrast.
    hobtez ? korrvex = hobtez   (the table for ?)
    keldclo ? hobtez = korrvex   (the table for ?)
That gives korrvex, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test keldclo %% korrdri. The brasib of keldclo is korrvex and keldclo, and korrdri lies
outside it, so the relation fails.

Now compute [korrdri]. Fold korrdri against itself, then fold whatever appeared against
everything present, and stop when a round adds nothing. The result is korrvex and
korrdri, of size 2.

## A case that breaks

A quick guard against a common slip: glimsib ? korrvex is glimsib while korrvex ?
glimsib is korrvex. Order is not decoration in this system.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by closure under the first operation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: D1 (tarnmux vashumbs), D2 (vashumbs that yukdri)
and D3 (hurnisk collections).

What is built on it later: D9 (the vorzam of a vashumb), T1 (the reldmi of a vashumb is
hurnisk), T2 (the reldmi is contained in every hurnisk collection) and T4 (the mimorn is
hurnisk).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

Carry forward the yukfex, the mimorn and the reldmi of a vashumb. Later chapters state
their results in these terms and do not restate the definitions.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x028. Write down the mimorn in full.
  x029. List the reldmi of keldclo.
  x030. List the reldmi of glimsib.
  x031. List the reldmi of hobtez.
  x032. Name every vashumb in [korrdri].
Level 4.
  x033. Let z be keldclo ? hobtez. List the reldmi of z.
  x034. Let z be korrdri ? korrvex. List the reldmi of z.
  x035. Let z be hobtez ? glimsib. List the reldmi of z.

# Chapter 8. The relation and what it orders (3)

## Why this chapter

Work through this chapter with the tables in front of you. It covers there is at most
one vexlum, the system has a vexlum and no ovijen pairs exist, and each claim can be
checked by hand.

Prerequisites are real here: chapters 3 and 6 supply the notions the statements below
are phrased in.

The standard of proof here is exhaustion. A universal claim about vashumbs covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

Think of %% as pointing downhill. The brasib of a vashumb is everything downhill of it,
and those shadows here have sizes 1, 2, 3, 4 and 5.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T6 rests on D8 (a vexlum) and A8 (antisymmetry of the relation). The dependence is on
the content of those results, not only on their vocabulary.

T7 rests on D8 (a vexlum) and A10 (comparability of every pair). Remove any one of them
and the statement stops making sense, not merely stops being provable.

T8 rests on D11 (ovijen pairs) and A8 (antisymmetry of the relation). Remove any one of
them and the statement stops making sense, not merely stops being provable.

## A worked case

Take (glimsib ? korrvex) ? (hobtez ? korrdri) and work it out one step at a time.
    glimsib ? korrvex = glimsib   (the table for ?)
    hobtez ? korrdri = korrvex   (the table for ?)
    glimsib ? korrvex = glimsib   (the table for ?)
The expression comes to glimsib.

Bracketing is not cosmetic, so here is korrvex ? (hobtez ? glimsib) for contrast.
    hobtez ? glimsib = keldclo   (the table for ?)
    korrvex ? keldclo = korrvex   (the table for ?)
That gives korrvex, against glimsib above.

One decision about the relation, since deciding is as much a skill as computing. Does
korrdri %% hobtez hold? Read off what korrdri stands over: korrvex, keldclo, glimsib,
hobtez and korrdri. hobtez is among them, so it holds.

## A case that breaks

A quick guard against a common slip: hobtez ? glimsib is keldclo while glimsib ? hobtez
is korrvex. Order is not decoration in this system.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by antisymmetry of the relation and comparability of every pair. A
system without them is not a system where these results are harder to prove; it is a
system where they are false.

That is not a rhetorical caution. Take the same 5 objects, the same symbols, and a
different table, and T6 and T8 stop holding. The notation survives the substitution and
the mathematics does not.

## Neighbouring results

Read alongside A10 (comparability of every pair), A8 (antisymmetry of the relation), D11
(ovijen pairs) and D8 (a vexlum).

## Proofs

T6. No two distinct vashumbs can both be vexlums.

  (1) [D8] Let f and h both be floors.
  (2) [D8] Then f %% h, since h is any object, and h %% f likewise.
  (3) [A8] Antisymmetry forces f = h.

Checked over 25 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T7. Some vashumb vexlums the whole system.

  (1) [A10] Every pair is comparable, so the relation orders the objects into a line.
  (2) [D8] The claim is that the line has a bottom.
  (3) The carrier is finite, so the search over candidates terminates.

Checked over 25 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T8. No two distinct vashumbs lie in each other's brasib.

  (1) [D11] Suppose x and y form a tight pair.
  (2) [A8] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

The results now available are T6, T7 and T8, each settled by exhaustive check rather
than by argument from analogy.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x052. Name the vashumbs that make up the vexlum, which is what the result above is a claim about.

# Chapter 9. Combining objects (3)

## Why this chapter

What follows was pieced together backwards. The last item of it, where every vashumb
lies in the yukfex breaks down, where every vashumb is tarnmux breaks down and the
mimorn is hurnisk, was noticed before anyone had a reason to expect it.

Prerequisites are real here: chapters 5 and 7 supply the notions the statements below
are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
vashumbs that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

Two questions sort the vashumbs quickly. Does combining a vashumb with itself change it?
For korrvex it does not. Does it matter which side it goes on? It always does.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R12 rests on D5 (the yukfex). The dependence is on the content of those results, not
only on their vocabulary.

R13 rests on D6 (the mimorn). The dependence is on the content of those results, not
only on their vocabulary.

T4 rests on D6 (the mimorn) and D3 (hurnisk collections). The dependence is on the
content of those results, not only on their vocabulary.

## A worked case

Evaluate korrdri ? keldclo & korrvex. Each line below is one lookup in a table.
    keldclo & korrvex = keldclo   (the table for &)
    korrdri ? keldclo = hobtez   (the table for ?)
That leaves hobtez, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is keldclo ? (korrvex ? korrdri) for contrast.
    korrvex ? korrdri = korrvex   (the table for ?)
    keldclo ? korrvex = keldclo   (the table for ?)
That gives keldclo, against hobtez above.

One decision about the relation, since deciding is as much a skill as computing. Does
glimsib %% hobtez hold? Read off what glimsib stands over: korrvex, keldclo and glimsib.
hobtez is not among them, so it fails.

## A case that breaks

R12. It is not the case that: Every pair of vashumbs yukdris. It fails at x = korrvex, y
= keldclo, left = korrvex, right = keldclo. One case is enough, and this is the earliest
one.

R13. It is not the case that: x ? x = x for every vashumb x. It fails at x = keldclo,
value = korrvex. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: D3 (hurnisk collections), D5 (the yukfex) and D6
(the mimorn).

## Proofs

R12. It is not the case that: Every pair of vashumbs yukdris.

  (1) [S2] Take the case x = korrvex, y = keldclo, left = korrvex, right = keldclo, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

R13. It is not the case that: x ? x = x for every vashumb x.

  (1) [S2] Take the case x = keldclo, value = korrvex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T4. If x and y are both tarnmux then so is x ? y.

  (1) [D6] Let x and y be tarnmux.
  (2) [D1] The claim asks whether (x ? y) ? (x ? y) returns x ? y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 25 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

The results now available are T4, each settled by exhaustive check rather than by
argument from analogy.

Do not carry forward R12 and R13. These were tested and failed, and the failing cases
are recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x049. This result is about the mimorn. List every vashumb in it.
Level 5.
  x053. The following fails in this system: Every pair of vashumbs yukdris. Name the earliest vashumb, in the order the vashumbs were introduced, that witnesses the failure.
  x054. The following fails in this system: x ? x = x for every vashumb x. Name the earliest vashumb, in the order the vashumbs were introduced, that witnesses the failure.

# Chapter 10. Collections that close on themselves

## Why this chapter

Anyone using this system to keep track of something will meet the vorzam of a vashumb,
the reldmi of a vashumb is hurnisk and the fexpon early, whether or not they go looking.

Prerequisites are real here: chapters 5 and 7 supply the notions the statements below
are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
vashumbs that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D9. The vorzam of a vashumb. The vorzam of a vashumb x is the number of vashumbs in its
reldmi [x].

Worked out for each vashumb: korrvex to 1; keldclo to 2; glimsib to 2; hobtez to 2;
korrdri to 2.

D10. The fexpon. The fexpon of the system is the collection of vashumbs whose vorzam is
largest.

In this system that picks out keldclo, glimsib, hobtez and korrdri, which is 4 of the 5
vashumbs.

## The shape of it

The right picture for reldmi is a spreading stain rather than a list. Drop one vashumb
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
vashumbs depending on where it started.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 vashumbs the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T1 rests on D7 (the reldmi of a vashumb) and D3 (hurnisk collections). The dependence is
on the content of those results, not only on their vocabulary.

R11 rests on D9 (the vorzam of a vashumb) and T1 (the reldmi of a vashumb is hurnisk).
The dependence is on the content of those results, not only on their vocabulary.

R14 rests on D7 (the reldmi of a vashumb) and D9 (the vorzam of a vashumb). The
dependence is on the content of those results, not only on their vocabulary.

T2 rests on D7 (the reldmi of a vashumb) and T1 (the reldmi of a vashumb is hurnisk).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

T3 rests on D1 (tarnmux vashumbs), D9 (the vorzam of a vashumb) and T1 (the reldmi of a
vashumb is hurnisk). The dependence is on the content of those results, not only on
their vocabulary.

## A worked case

Evaluate (korrvex ? glimsib) ? (keldclo ? korrdri). Each line below is one lookup in a
table.
    korrvex ? glimsib = korrvex   (the table for ?)
    keldclo ? korrdri = korrvex   (the table for ?)
    korrvex ? korrvex = korrvex   (the table for ?)
The expression comes to korrvex.

Move the brackets and the work changes. Take glimsib ? (keldclo ? korrvex).
    keldclo ? korrvex = keldclo   (the table for ?)
    glimsib ? keldclo = keldclo   (the table for ?)
The value is keldclo, not korrvex.

One decision about the relation, since deciding is as much a skill as computing. Does
keldclo %% hobtez hold? Read off what keldclo stands over: korrvex and keldclo. hobtez
is not among them, so it fails.

A second case, this time a reldmi. Start from hobtez. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is korrvex and hobtez,
so the vorzam of hobtez is 2.

## A case that breaks

R11. It is not the case that: For every vashumb x, the vorzam of x divides 5. The case
that settles it: x = keldclo, reach = 2, size = 5. Anyone carrying this claim over from
a more familiar system will be wrong here, and wrong in a way that propagates.

R14. It is not the case that: There is a vashumb whose reldmi is the whole system. It
fails at largest_span = 2, size = 5. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside D1 (tarnmux vashumbs), D3 (hurnisk collections) and D7 (the reldmi of a
vashumb).

## Proofs

T1. For every vashumb x, the collection [x] is hurnisk.

  (1) [D7] [x] is built by taking x and closing under ?.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 125 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

R11. It is not the case that: For every vashumb x, the vorzam of x divides 5.

  (1) [S2] Take the case x = keldclo, reach = 2, size = 5, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

R14. It is not the case that: There is a vashumb whose reldmi is the whole system.

  (1) [S2] Take the case largest_span = 2, size = 5, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T2. If S is hurnisk and contains x, then S contains all of [x].

  (1) [D7] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 45 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. x ? x = x holds if and only if [x] contains x alone.

  (1) [D1] If x ? x = x then {x} is already closed under ?.
  (2) [T1] So [x] = {x} and the vorzam is one.
  (3) [D9] Conversely a span of one object must contain x ? x, which is then x.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the vorzam of a vashumb and the fexpon. Later chapters state their results
in these terms and do not restate the definitions.

The results now available are T1, T2 and T3, each settled by exhaustive check rather
than by argument from analogy.

Do not carry forward R11 and R14. These were tested and failed, and the failing cases
are recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x037. How many vashumbs lie in [keldclo]?
  x038. How many vashumbs lie in [glimsib]?
  x039. What is the vorzam of hobtez?
  x040. What is the vorzam of korrdri?
Level 4.
  x046. Write down the fexpon in full.
  x047. What is the largest vorzam any vashumb has?
Level 5.
  x041. Let z be (korrdri ? korrdri) ? glimsib. What is the vorzam of z?
  x042. Let z be keldclo ? korrvex & korrvex. What is the vorzam of z?
  x043. Let z be glimsib ? korrdri & korrvex. What is the vorzam of z?
  x044. Let z be (glimsib ? glimsib) ? keldclo. What is the vorzam of z?
  x045. Let z be hobtez ? hobtez & korrvex. What is the vorzam of z?
  x048. The following fails in this system: For every vashumb x, the vorzam of x divides 5. Name the earliest vashumb, in the order the vashumbs were introduced, that witnesses the failure.
