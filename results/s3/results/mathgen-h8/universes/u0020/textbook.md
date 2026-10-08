# The Vintfex system

This book is about shenopals. A shenopal is not a number and not a set; it is one of
exactly 5 objects, and everything said here is said about how those 5 objects combine.

The shenopals are written opallorn, qenthra, grixlum, vorpon and pontu. The first
operation is written %. The second is written & and binds more tightly, so x % y & z
means x % (y & z). The relation is written ::; where it holds between two shenopals we
say the left one yields to the right one. Both operations associate to the left when
written without brackets, and brackets override that. Repeated combination is
abbreviated: x^3 means x % x % x.

Readers arriving from arithmetic should put it down at the door. The operations below
are defined by their tables and by nothing else. Several arithmetic habits survive the
crossing and several do not, and the text is careful to say which is which.

# Chapter 1. The objects and their notation

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through the Vintfex signature, the
Vintfex combination tables and closure under the first operation.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
shenopals that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## The tables in full

The table for %. Read the left argument down the side and the right argument across the top.

          |  opallorn   qenthra   grixlum    vorpon     pontu
-------------------------------------------------------------
 opallorn |  opallorn  opallorn  opallorn  opallorn  opallorn
  qenthra |   qenthra  opallorn  opallorn  opallorn  opallorn
  grixlum |   grixlum   qenthra  opallorn  opallorn  opallorn
   vorpon |    vorpon   grixlum   qenthra  opallorn  opallorn
    pontu |     pontu    vorpon   grixlum   qenthra  opallorn

The table for &. Read the left argument down the side and the right argument across the top.

          |  opallorn   qenthra   grixlum    vorpon     pontu
-------------------------------------------------------------
 opallorn |  opallorn   qenthra   grixlum    vorpon     pontu
  qenthra |   qenthra   qenthra   grixlum    vorpon     pontu
  grixlum |   grixlum   grixlum   grixlum    vorpon     pontu
   vorpon |    vorpon    vorpon    vorpon    vorpon     pontu
    pontu |     pontu     pontu     pontu     pontu     pontu

Every pair standing in the :: relation, grouped by left argument.

  opallorn :: opallorn, qenthra, grixlum, vorpon and pontu
  qenthra :: qenthra, grixlum, vorpon and pontu
  grixlum :: grixlum, vorpon and pontu
  vorpon :: vorpon and pontu
  pontu :: pontu

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A1. Closure under the first operation. For all shenopals x and y, x % y is again a
shenopal.

## The shape of it

Two questions sort the shenopals quickly. Does combining a shenopal with itself change
it? For opallorn it does not. Does it matter which side it goes on? It always does.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R1 rests on S2 (the Vintfex combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R2 rests on S2 (the Vintfex combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R5 rests on S2 (the Vintfex combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R6 rests on S2 (the Vintfex combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take pontu % grixlum & vorpon and work it out one step at a time.
    grixlum & vorpon = vorpon   (the table for &)
    pontu % vorpon = qenthra   (the table for %)
That leaves qenthra, and no other reading of the notation gives anything else.

A companion case, grixlum % (vorpon % pontu), to show what the brackets are doing.
    vorpon % pontu = opallorn   (the table for %)
    grixlum % opallorn = grixlum   (the table for %)
That gives grixlum, against qenthra above.

Test pontu :: pontu. The muxsib of pontu is pontu, and pontu lies inside it, so the
relation holds.

## A case that breaks

R1. It is not the case that: For all shenopals x, y, z: (x % y) % z = x % (y % z). The
case that settles it: x = qenthra, y = opallorn, z = qenthra, left = opallorn, right =
qenthra. Anyone carrying this claim over from a more familiar system will be wrong here,
and wrong in a way that propagates.

R2. It is not the case that: For all shenopals x and y: x % y = y % x. The case that
settles it: x = opallorn, y = qenthra, left = opallorn, right = qenthra. Anyone carrying
this claim over from a more familiar system will be wrong here, and wrong in a way that
propagates.

R5. It is not the case that: For every shenopal x: x % x = x. The case that settles it:
x = qenthra, value = opallorn. Anyone carrying this claim over from a more familiar
system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

These results are used again in A2 (closure under the second operation), A3 (association
of the second operation), A4 (commutation of the second operation) and A5 (a neutral
object for the second operation).

## Proofs

R1. It is not the case that: For all shenopals x, y, z: (x % y) % z = x % (y % z).

  (1) [S2] Take the case x = qenthra, y = opallorn, z = qenthra, left = opallorn, right = qenthra, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R2. It is not the case that: For all shenopals x and y: x % y = y % x.

  (1) [S2] Take the case x = opallorn, y = qenthra, left = opallorn, right = qenthra, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R5. It is not the case that: For every shenopal x: x % x = x.

  (1) [S2] Take the case x = qenthra, value = opallorn, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R6. It is not the case that: For all shenopals x, y, z: if x % y = x % z then y = z.

  (1) [S2] Take the case x = opallorn, y = opallorn, z = qenthra, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R1, R2, R5 and R6. A later argument that quietly assumes one
of these is wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 1.
  x001. Reduce qenthra % pontu to a single shenopal.
  x002. Reduce pontu % vorpon to a single shenopal.
  x003. Reduce grixlum % grixlum to a single shenopal.
  x004. Evaluate qenthra % grixlum.
  x005. Evaluate grixlum % pontu.
  x006. Work out the value of grixlum % vorpon.
  x007. Work out the value of qenthra % qenthra.
Level 2.
  x008. What shenopal does vorpon % pontu & qenthra name?
  x009. What shenopal does (grixlum % grixlum) % grixlum name?
  x010. Work out the value of (vorpon % grixlum) % qenthra.
  x011. Evaluate grixlum^2.
  x012. What is pontu combined with itself 3 times under %?
  x013. What is qenthra combined with itself 3 times under %?
  x014. Which shenopals x satisfy x % grixlum = grixlum? List them all.
  x015. Solve x % vorpon = qenthra for x, naming every solution.
  x016. Solve x % qenthra = grixlum for x, naming every solution.
  x017. Which shenopals x satisfy x % pontu = opallorn? List them all.
  x018. Solve x % vorpon = opallorn for x, naming every solution.
Level 3.
  x019. Evaluate grixlum % grixlum & grixlum, minding which operation binds tighter.
Level 5.
  x020. The following fails in this system: For all shenopals x, y, z: (x % y) % z = x % (y % z). Name the earliest shenopal, in the order the shenopals were introduced, that witnesses the failure.
  x021. The following fails in this system: For all shenopals x and y: x % y = y % x. Name the earliest shenopal, in the order the shenopals were introduced, that witnesses the failure.
  x023. The following fails in this system: For every shenopal x: x % x = x. Name the earliest shenopal, in the order the shenopals were introduced, that witnesses the failure.
  x024. The following fails in this system: For all shenopals x, y, z: if x % y = x % z then y = z. Name the earliest shenopal, in the order the shenopals were introduced, that witnesses the failure.

# Chapter 2. Neutral objects and reversal

## Why this chapter

We turn to the system does not have a neutral object for the first operation, the system
does not have reversal under the first operation and the system does not have an
absorbing object for the first operation. The treatment is self contained given the
material already established.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about shenopals covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

The neutral shenopal is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R3 rests on S2 (the Vintfex combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R4 rests on S2 (the Vintfex combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R7 rests on S2 (the Vintfex combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take (qenthra % grixlum) % (vorpon % pontu) and work it out one step at a time.
    qenthra % grixlum = opallorn   (the table for %)
    vorpon % pontu = opallorn   (the table for %)
    opallorn % opallorn = opallorn   (the table for %)
The expression comes to opallorn.

Bracketing is not cosmetic, so here is grixlum % (vorpon % qenthra) for contrast.
    vorpon % qenthra = grixlum   (the table for %)
    grixlum % grixlum = opallorn   (the table for %)
The value is opallorn. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
vorpon :: grixlum hold? Read off what vorpon stands over: vorpon and pontu. grixlum is
not among them, so it fails.

## A case that breaks

R3. There is no shenopal e with e % x = x % e = x for every shenopal x. It fails at
reason = no two sided identity exists. One case is enough, and this is the earliest one.

R4. Some shenopal x admits no shenopal y for which x % y and y % x both land on a
neutral object. The case that settles it: reason = no identity, so inverses are not
defined. Anyone carrying this claim over from a more familiar system will be wrong here,
and wrong in a way that propagates.

R7. There is no shenopal z with z % x = x % z = z for every shenopal x. The case that
settles it: reason = no absorbing element. Anyone carrying this claim over from a more
familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside S2 (the Vintfex combination tables).

## Proofs

R3. There is no shenopal e with e % x = x % e = x for every shenopal x.

  (1) [S2] Take the case reason = no two sided identity exists, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R4. Some shenopal x admits no shenopal y for which x % y and y % x both land on a neutral object.

  (1) [S2] Take the case reason = no identity, so inverses are not defined, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R7. There is no shenopal z with z % x = x % z = z for every shenopal x.

  (1) [S2] Take the case reason = no absorbing element, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R3, R4 and R7. A later argument that quietly assumes one of
these is wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 5.
  x022. The following fails in this system: Some shenopal x admits no shenopal y for which x % y and y % x both land on a neutral object. Name the earliest shenopal, in the order the shenopals were introduced, that witnesses the failure.

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

# Chapter 4. The second operation and how the two interact

## Why this chapter

What follows was pieced together backwards. The last item of it, closure under the
second operation, association of the second operation and commutation of the second
operation, was noticed before anyone had a reason to expect it.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
shenopals that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A2. Closure under the second operation. For all shenopals x and y, x & y is again a
shenopal.

A3. Association of the second operation. For all shenopals x, y, z: (x & y) & z = x & (y
& z).

A4. Commutation of the second operation. For all shenopals x and y: x & y = y & x.

A5. A neutral object for the second operation. There is a shenopal opallorn with
opallorn & x = x for every x.

A6. Self combination under the second operation. For every shenopal x: x & x = x.

## The shape of it

The interesting content of a two operation system sits in the gap between them: which
one distributes over which, and which shenopals are fixed by both.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 shenopals the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R8 rests on S2 (the Vintfex combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R9 rests on S2 (the Vintfex combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Here is (opallorn % pontu) % (grixlum % qenthra), reduced without skipping anything.
    opallorn % pontu = opallorn   (the table for %)
    grixlum % qenthra = qenthra   (the table for %)
    opallorn % qenthra = opallorn   (the table for %)
The expression comes to opallorn.

A companion case, pontu % (grixlum % opallorn), to show what the brackets are doing.
    grixlum % opallorn = grixlum   (the table for %)
    pontu % grixlum = grixlum   (the table for %)
That gives grixlum, against opallorn above.

Test vorpon :: opallorn. The muxsib of vorpon is vorpon and pontu, and opallorn lies
outside it, so the relation fails.

## A case that breaks

R8. It is not the case that: For all shenopals x, y, z: x & (y % z) = (x & y) % (x & z),
and the same on the right. It fails at x = qenthra, y = opallorn, z = opallorn, left =
qenthra, right = opallorn. One case is enough, and this is the earliest one.

R9. It is not the case that: For all shenopals x and y: x % (x & y) = x and x & (x % y)
= x. It fails at x = qenthra, y = opallorn, value = opallorn. One case is enough, and
this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: S2 (the Vintfex combination tables).

## Proofs

R8. It is not the case that: For all shenopals x, y, z: x & (y % z) = (x & y) % (x & z), and the same on the right.

  (1) [S2] Take the case x = qenthra, y = opallorn, z = opallorn, left = qenthra, right = opallorn, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R9. It is not the case that: For all shenopals x and y: x % (x & y) = x and x & (x % y) = x.

  (1) [S2] Take the case x = qenthra, y = opallorn, value = opallorn, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R8 and R9. These were tested and failed, and the failing cases are
recorded above.

## Exercises

No exercises here. Every question this chapter suggested turned out to be answerable
from the question itself, so all of them were discarded.

# Chapter 5. Combining objects

## Why this chapter

The practical content of this chapter is grixka shenopals, shenopals that gelwren and
quilglim collections. It is the part that shows up in use.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
shenopals that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D1. Grixka shenopals. A shenopal x is called grixka when x % x = x.

In this system that picks out opallorn, which is 1 of the 5 shenopals.

D2. Shenopals that gelwren. Two shenopals x and y are said to gelwren when x % y = y %
x.

D3. Quilglim collections. A collection S of shenopals is quilglim when x % y belongs to
S for every pair x, y drawn from S.

## The shape of it

Picture the thrafex as what happens when you start with one shenopal and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 5 shenopals, that stops. In this system the sizes it stops at are 1 and 2.

Two questions sort the shenopals quickly. Does combining a shenopal with itself change
it? For opallorn it does not. Does it matter which side it goes on? It always does.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 shenopals the table is short enough to consult every time.

## Where these results come from

Nothing is derived in this chapter. It lays down material that later chapters draw on.

## A worked case

Evaluate grixlum % qenthra & opallorn. Each line below is one lookup in a table.
    qenthra & opallorn = qenthra   (the table for &)
    grixlum % qenthra = qenthra   (the table for %)
That leaves qenthra, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is qenthra % (opallorn % grixlum) for contrast.
    opallorn % grixlum = opallorn   (the table for %)
    qenthra % opallorn = qenthra   (the table for %)
The value is qenthra. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test pontu :: grixlum. The muxsib of pontu is pontu, and grixlum lies outside it, so the
relation fails.

## A case that breaks

A quick guard against a common slip: qenthra % grixlum is opallorn while grixlum %
qenthra is qenthra. Order is not decoration in this system.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A1 (closure under the first operation).

These results are used again in D5 (the shengel), D6 (the espanak), D7 (the thrafex of a
shenopal) and T1 (the thrafex of a shenopal is quilglim).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

New vocabulary from this chapter: grixka shenopals, shenopals that gelwren and quilglim
collections. Each of these is used by name later, so the names are worth learning rather
than looking up.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x026. Write down the grixka in full.
  x027. How many shenopals lie in the smallest quilglim collection containing qenthra?
  x028. How many shenopals lie in the smallest quilglim collection containing grixlum?

# Chapter 6. The relation and what it orders (2)

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through aztgel pairs, a drisol and
where the relation reads the same in both directions breaks down.

Prerequisites are real here: chapter 3 supply the notions the statements below are
phrased in.

One habit to adopt: when a statement below quantifies over shenopals, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D11. Aztgel pairs. Two distinct shenopals x and y form a aztgel pair when x :: y and y
:: x both hold, that is, when each lies in the muxsib of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D8. A drisol. A shenopal f is a drisol when f :: y holds for every shenopal y, that is,
when the muxsib of f is the whole system.

In this system that picks out opallorn, which is 1 of the 5 shenopals.

## The shape of it

Think of :: as pointing downhill. The muxsib of a shenopal is everything downhill of it,
and those shadows here have sizes 1, 2, 3, 4 and 5.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R15 rests on D4 (the muxsib of a shenopal). Remove any one of them and the statement
stops making sense, not merely stops being provable.

T5 rests on D4 (the muxsib of a shenopal) and A9 (transitivity of the relation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Here is (opallorn % vorpon) % (qenthra % pontu), reduced without skipping anything.
    opallorn % vorpon = opallorn   (the table for %)
    qenthra % pontu = opallorn   (the table for %)
    opallorn % opallorn = opallorn   (the table for %)
That leaves opallorn, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take vorpon % (qenthra % opallorn).
    qenthra % opallorn = qenthra   (the table for %)
    vorpon % qenthra = grixlum   (the table for %)
The value is grixlum, not opallorn.

One decision about the relation, since deciding is as much a skill as computing. Does
opallorn :: grixlum hold? Read off what opallorn stands over: opallorn, qenthra,
grixlum, vorpon and pontu. grixlum is among them, so it holds.

## A case that breaks

R15. It is not the case that: If x :: y then y :: x. It fails at x = opallorn, y =
qenthra. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of transitivity of the relation. Those are
properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A9 (transitivity of the relation) and D4 (the muxsib of a shenopal).

What is built on it later: T6 (there is at most one drisol), T7 (the system has a
drisol) and T8 (no aztgel pairs exist).

## Proofs

R15. It is not the case that: If x :: y then y :: x.

  (1) [S2] Take the case x = opallorn, y = qenthra, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T5. If y lies in the muxsib of x, then the muxsib of y is contained in the muxsib of x.

  (1) [D4] Let y satisfy x :: y and let z satisfy y :: z.
  (2) [A9] Transitivity gives x :: z.
  (3) [D4] So every member of the muxsib of y is a member of that of x.

Checked over 125 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: aztgel pairs and a drisol. Each of these is used by
name later, so the names are worth learning rather than looking up.

Established here and safe to use: T5.

Do not carry forward R15. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x041. List every shenopal in the drisol.
  x054. The result above concerns muxsibs. List the muxsib of opallorn.
  x055. The result above concerns muxsibs. List the muxsib of qenthra.
  x056. The result above concerns muxsibs. List the muxsib of grixlum.
Level 5.
  x060. The following fails in this system: If x :: y then y :: x. Name the earliest shenopal, in the order the shenopals were introduced, that witnesses the failure.

# Chapter 7. Combining objects (2)

## Why this chapter

The present chapter develops the shengel, the espanak and the thrafex of a shenopal.

Prerequisites are real here: chapter 5 supply the notions the statements below are
phrased in.

One habit to adopt: when a statement below quantifies over shenopals, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D5. The shengel. The shengel of the system is the collection of shenopals that gelwren
with every shenopal.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D6. The espanak. The espanak is the collection of all grixka shenopals.

In this system that picks out opallorn, which is 1 of the 5 shenopals.

D7. The thrafex of a shenopal. The thrafex of a shenopal x, written [x], is the smallest
quilglim collection that contains x.

Worked out for each shenopal: opallorn to opallorn; qenthra to opallorn and qenthra;
grixlum to opallorn and grixlum; vorpon to opallorn and vorpon; pontu to opallorn and
pontu.

## The shape of it

The right picture for thrafex is a spreading stain rather than a list. Drop one shenopal
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
shenopals depending on where it started.

Two questions sort the shenopals quickly. Does combining a shenopal with itself change
it? For opallorn it does not. Does it matter which side it goes on? It always does.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

This chapter is groundwork. The derivations that use it start in the next one.

## A worked case

Here is pontu % qenthra & grixlum, reduced without skipping anything.
    qenthra & grixlum = grixlum   (the table for &)
    pontu % grixlum = grixlum   (the table for %)
So pontu % qenthra & grixlum is grixlum.

Bracketing is not cosmetic, so here is qenthra % (grixlum % pontu) for contrast.
    grixlum % pontu = opallorn   (the table for %)
    qenthra % opallorn = qenthra   (the table for %)
That gives qenthra, against grixlum above.

Test opallorn :: grixlum. The muxsib of opallorn is opallorn, qenthra, grixlum, vorpon
and pontu, and grixlum lies inside it, so the relation holds.

Now compute [vorpon]. Fold vorpon against itself, then fold whatever appeared against
everything present, and stop when a round adds nothing. The result is opallorn and
vorpon, of size 2.

## A case that breaks

A quick guard against a common slip: qenthra % grixlum is opallorn while grixlum %
qenthra is qenthra. Order is not decoration in this system.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: D1 (grixka shenopals), D2 (shenopals that
gelwren) and D3 (quilglim collections).

These results are used again in D9 (the duthfal of a shenopal), T1 (the thrafex of a
shenopal is quilglim), T2 (the thrafex is contained in every quilglim collection) and T4
(the espanak is quilglim).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

New vocabulary from this chapter: the shengel, the espanak and the thrafex of a
shenopal. Each of these is used by name later, so the names are worth learning rather
than looking up.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x033. Write down the espanak in full.
  x034. Name every shenopal in [qenthra].
  x035. List the thrafex of grixlum.
  x036. Name every shenopal in [vorpon].
  x037. List the thrafex of pontu.
Level 4.
  x038. Let z be qenthra % grixlum. List the thrafex of z.
  x039. Let z be qenthra % pontu. List the thrafex of z.
  x040. Let z be vorpon % grixlum. List the thrafex of z.

# Chapter 8. The relation and what it orders (3)

## Why this chapter

Work through this chapter with the tables in front of you. It covers there is at most
one drisol, the system has a drisol and no aztgel pairs exist, and each claim can be
checked by hand.

Nothing here stands on its own. The arguments lean on chapters 3 and 6, and a reader who
has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over shenopals, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

Think of :: as pointing downhill. The muxsib of a shenopal is everything downhill of it,
and those shadows here have sizes 1, 2, 3, 4 and 5.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T6 rests on D8 (a drisol) and A8 (antisymmetry of the relation). The dependence is on
the content of those results, not only on their vocabulary.

T7 rests on D8 (a drisol) and A10 (comparability of every pair). The dependence is on
the content of those results, not only on their vocabulary.

T8 rests on D11 (aztgel pairs) and A8 (antisymmetry of the relation). The dependence is
on the content of those results, not only on their vocabulary.

## A worked case

Evaluate (opallorn % qenthra) % (pontu % vorpon). Each line below is one lookup in a
table.
    opallorn % qenthra = opallorn   (the table for %)
    pontu % vorpon = qenthra   (the table for %)
    opallorn % qenthra = opallorn   (the table for %)
That leaves opallorn, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is qenthra % (pontu % opallorn) for contrast.
    pontu % opallorn = pontu   (the table for %)
    qenthra % pontu = opallorn   (the table for %)
The value is opallorn. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test qenthra :: vorpon. The muxsib of qenthra is qenthra, grixlum, vorpon and pontu, and
vorpon lies inside it, so the relation holds.

## A case that breaks

A quick guard against a common slip: qenthra % pontu is opallorn while pontu % qenthra
is vorpon. Order is not decoration in this system.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by antisymmetry of the relation and comparability of every pair. A
system without them is not a system where these results are harder to prove; it is a
system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A10 (comparability of every pair), A8 (antisymmetry of the relation), D11
(aztgel pairs) and D8 (a drisol).

## Proofs

T6. No two distinct shenopals can both be drisols.

  (1) [D8] Let f and h both be floors.
  (2) [D8] Then f :: h, since h is any object, and h :: f likewise.
  (3) [A8] Antisymmetry forces f = h.

Checked over 25 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T7. Some shenopal drisols the whole system.

  (1) [A10] Every pair is comparable, so the relation orders the objects into a line.
  (2) [D8] The claim is that the line has a bottom.
  (3) The carrier is finite, so the search over candidates terminates.

Checked over 25 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T8. No two distinct shenopals lie in each other's muxsib.

  (1) [D11] Suppose x and y form a tight pair.
  (2) [A8] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

The results now available are T6, T7 and T8, each settled by exhaustive check rather
than by argument from analogy.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x057. Name the shenopals that make up the drisol, which is what the result above is a claim about.

# Chapter 9. Combining objects (3)

## Why this chapter

What follows was pieced together backwards. The last item of it, where every shenopal
lies in the shengel breaks down, where every shenopal is grixka breaks down and the
espanak is quilglim, was noticed before anyone had a reason to expect it.

Prerequisites are real here: chapters 5 and 7 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over shenopals, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

A useful mental split: some shenopals are inert under the operation and some are not.
opallorn come back unchanged when combined with themselves, and none commutes with
everything.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R12 rests on D5 (the shengel). The dependence is on the content of those results, not
only on their vocabulary.

R13 rests on D6 (the espanak). The dependence is on the content of those results, not
only on their vocabulary.

T4 rests on D6 (the espanak) and D3 (quilglim collections). Remove any one of them and
the statement stops making sense, not merely stops being provable.

## A worked case

Take grixlum % opallorn & pontu and work it out one step at a time.
    opallorn & pontu = pontu   (the table for &)
    grixlum % pontu = opallorn   (the table for %)
So grixlum % opallorn & pontu is opallorn.

Move the brackets and the work changes. Take opallorn % (pontu % grixlum).
    pontu % grixlum = grixlum   (the table for %)
    opallorn % grixlum = opallorn   (the table for %)
That gives opallorn, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
qenthra :: pontu hold? Read off what qenthra stands over: qenthra, grixlum, vorpon and
pontu. pontu is among them, so it holds.

## A case that breaks

R12. It is not the case that: Every pair of shenopals gelwrens. The case that settles
it: x = opallorn, y = qenthra, left = opallorn, right = qenthra. Anyone carrying this
claim over from a more familiar system will be wrong here, and wrong in a way that
propagates.

R13. It is not the case that: x % x = x for every shenopal x. The case that settles it:
x = qenthra, value = opallorn. Anyone carrying this claim over from a more familiar
system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by closure under the first operation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: D3 (quilglim collections), D5 (the shengel) and
D6 (the espanak).

## Proofs

R12. It is not the case that: Every pair of shenopals gelwrens.

  (1) [S2] Take the case x = opallorn, y = qenthra, left = opallorn, right = qenthra, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

R13. It is not the case that: x % x = x for every shenopal x.

  (1) [S2] Take the case x = qenthra, value = opallorn, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T4. If x and y are both grixka then so is x % y.

  (1) [D6] Let x and y be grixka.
  (2) [D1] The claim asks whether (x % y) % (x % y) returns x % y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 25 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Established here and safe to use: T4.

Explicitly not available: R12 and R13. A later argument that quietly assumes one of
these is wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x053. This result is about the espanak. List every shenopal in it.
Level 5.
  x058. The following fails in this system: Every pair of shenopals gelwrens. Name the earliest shenopal, in the order the shenopals were introduced, that witnesses the failure.
  x059. The following fails in this system: x % x = x for every shenopal x. Name the earliest shenopal, in the order the shenopals were introduced, that witnesses the failure.

# Chapter 10. Collections that close on themselves

## Why this chapter

The practical content of this chapter is the duthfal of a shenopal, the thrafex of a
shenopal is quilglim and the tarnvor. It is the part that shows up in use.

Nothing here stands on its own. The arguments lean on chapters 5 and 7, and a reader who
has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
shenopals that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D9. The duthfal of a shenopal. The duthfal of a shenopal x is the number of shenopals in
its thrafex [x].

Worked out for each shenopal: opallorn to 1; qenthra to 2; grixlum to 2; vorpon to 2;
pontu to 2.

D10. The tarnvor. The tarnvor of the system is the collection of shenopals whose duthfal
is largest.

In this system that picks out qenthra, grixlum, vorpon and pontu, which is 4 of the 5
shenopals.

## The shape of it

The right picture for thrafex is a spreading stain rather than a list. Drop one shenopal
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
shenopals depending on where it started.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 shenopals the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T1 rests on D7 (the thrafex of a shenopal) and D3 (quilglim collections). Remove any one
of them and the statement stops making sense, not merely stops being provable.

R11 rests on D9 (the duthfal of a shenopal) and T1 (the thrafex of a shenopal is
quilglim). The dependence is on the content of those results, not only on their
vocabulary.

R14 rests on D7 (the thrafex of a shenopal) and D9 (the duthfal of a shenopal). The
dependence is on the content of those results, not only on their vocabulary.

T2 rests on D7 (the thrafex of a shenopal) and T1 (the thrafex of a shenopal is
quilglim). Remove any one of them and the statement stops making sense, not merely stops
being provable.

T3 rests on D1 (grixka shenopals), D9 (the duthfal of a shenopal) and T1 (the thrafex of
a shenopal is quilglim). The dependence is on the content of those results, not only on
their vocabulary.

## A worked case

Evaluate (opallorn % grixlum) % (qenthra % vorpon). Each line below is one lookup in a
table.
    opallorn % grixlum = opallorn   (the table for %)
    qenthra % vorpon = opallorn   (the table for %)
    opallorn % opallorn = opallorn   (the table for %)
That leaves opallorn, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is grixlum % (qenthra % opallorn) for contrast.
    qenthra % opallorn = qenthra   (the table for %)
    grixlum % qenthra = qenthra   (the table for %)
The value is qenthra, not opallorn.

One decision about the relation, since deciding is as much a skill as computing. Does
pontu :: qenthra hold? Read off what pontu stands over: pontu. qenthra is not among
them, so it fails.

A second case, this time a thrafex. Start from opallorn. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is opallorn, so the
duthfal of opallorn is 1.

## A case that breaks

R11. It is not the case that: For every shenopal x, the duthfal of x divides 5. It fails
at x = qenthra, reach = 2, size = 5. One case is enough, and this is the earliest one.

R14. It is not the case that: There is a shenopal whose thrafex is the whole system. The
case that settles it: largest_span = 2, size = 5. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside D1 (grixka shenopals), D3 (quilglim collections) and D7 (the thrafex of a
shenopal).

## Proofs

T1. For every shenopal x, the collection [x] is quilglim.

  (1) [D7] [x] is built by taking x and closing under %.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 125 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

R11. It is not the case that: For every shenopal x, the duthfal of x divides 5.

  (1) [S2] Take the case x = qenthra, reach = 2, size = 5, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

R14. It is not the case that: There is a shenopal whose thrafex is the whole system.

  (1) [S2] Take the case largest_span = 2, size = 5, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T2. If S is quilglim and contains x, then S contains all of [x].

  (1) [D7] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 45 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. x % x = x holds if and only if [x] contains x alone.

  (1) [D1] If x % x = x then {x} is already closed under %.
  (2) [T1] So [x] = {x} and the duthfal is one.
  (3) [D9] Conversely a span of one object must contain x % x, which is then x.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the duthfal of a shenopal and the tarnvor. Later chapters state their
results in these terms and do not restate the definitions.

Established here and safe to use: T1, T2 and T3.

Do not carry forward R11 and R14. These were tested and failed, and the failing cases
are recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x042. What is the duthfal of qenthra?
  x043. How many shenopals lie in [grixlum]?
  x044. How many shenopals lie in [vorpon]?
  x045. What is the duthfal of pontu?
Level 4.
  x050. Write down the tarnvor in full.
  x051. What is the largest duthfal any shenopal has?
Level 5.
  x046. Let z be pontu % qenthra & grixlum. What is the duthfal of z?
  x047. Let z be vorpon % opallorn & grixlum. What is the duthfal of z?
  x048. Let z be (vorpon % grixlum) % pontu. What is the duthfal of z?
  x049. Let z be qenthra % grixlum & pontu. What is the duthfal of z?
  x052. The following fails in this system: For every shenopal x, the duthfal of x divides 5. Name the earliest shenopal, in the order the shenopals were introduced, that witnesses the failure.
