# The Duthsol system

This book is about opalmis. A opalmi is not a number and not a set; it is one of exactly
5 objects, and everything said here is said about how those 5 objects combine.

The opalmis are written keldsib, duthzam, hobfex, iskxil and qenxil. The first operation
is written -. The relation is written <~; where it holds between two opalmis we say the
left one covers the right one. Both operations associate to the left when written
without brackets, and brackets override that. Repeated combination is abbreviated: x^3
means x - x - x.

Readers arriving from arithmetic should put it down at the door. The operations below
are defined by their tables and by nothing else. Several arithmetic habits survive the
crossing and several do not, and the text is careful to say which is which.

# Chapter 1. The objects and their notation

## Why this chapter

The practical content of this chapter is the Duthsol signature, the Duthsol combination
tables and closure under the first operation. It is the part that shows up in use.

The standard of proof here is exhaustion. A universal claim about opalmis covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## The tables in full

The table for -. Read the left argument down the side and the right argument across the top.

         |  keldsib  duthzam   hobfex   iskxil   qenxil
-------------------------------------------------------
 keldsib |  keldsib  keldsib  keldsib  keldsib  keldsib
 duthzam |  keldsib  duthzam   hobfex   iskxil   qenxil
  hobfex |  keldsib   hobfex   qenxil  duthzam   iskxil
  iskxil |  keldsib   iskxil  duthzam   qenxil   hobfex
  qenxil |  keldsib   qenxil   iskxil   hobfex  duthzam

Every pair standing in the <~ relation, grouped by left argument.

  keldsib <~ keldsib, duthzam, hobfex, iskxil and qenxil
  duthzam <~ duthzam
  hobfex <~ duthzam
  iskxil <~ duthzam
  qenxil <~ duthzam

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A1. Closure under the first operation. For all opalmis x and y, x - y is again a opalmi.

A2. Association of the first operation. For all opalmis x, y, z: (x - y) - z = x - (y -
z).

A3. Commutation of the first operation. For all opalmis x and y: x - y = y - x.

## The shape of it

Two questions sort the opalmis quickly. Does combining a opalmi with itself change it?
For keldsib and duthzam it does not. Does it matter which side it goes on? For keldsib,
duthzam, hobfex, iskxil and qenxil it does not.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R2 rests on S2 (the Duthsol combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R3 rests on S2 (the Duthsol combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Take (hobfex - iskxil) - keldsib and work it out one step at a time.
    hobfex - iskxil = duthzam   (the table for -)
    duthzam - keldsib = keldsib   (the table for -)
The expression comes to keldsib.

Bracketing is not cosmetic, so here is iskxil - (keldsib - hobfex) for contrast.
    keldsib - hobfex = keldsib   (the table for -)
    iskxil - keldsib = keldsib   (the table for -)
That gives keldsib, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
keldsib <~ keldsib hold? Read off what keldsib stands over: keldsib, duthzam, hobfex,
iskxil and qenxil. keldsib is among them, so it holds.

## A case that breaks

R2. It is not the case that: For every opalmi x: x - x = x. It fails at x = hobfex,
value = qenxil. One case is enough, and this is the earliest one.

R3. It is not the case that: For all opalmis x, y, z: if x - y = x - z then y = z. The
case that settles it: x = keldsib, y = keldsib, z = duthzam. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

These results are used again in A4 (a neutral object for the first operation), A5 (an
absorbing object for the first operation), A6 (antisymmetry of the relation) and A7
(transitivity of the relation).

## Proofs

R2. It is not the case that: For every opalmi x: x - x = x.

  (1) [S2] Take the case x = hobfex, value = qenxil, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R3. It is not the case that: For all opalmis x, y, z: if x - y = x - z then y = z.

  (1) [S2] Take the case x = keldsib, y = keldsib, z = duthzam, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R2 and R3. A later argument that quietly assumes one of these
is wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 1.
  x001. Reduce hobfex - iskxil to a single opalmi.
  x002. Work out the value of iskxil - hobfex.
Level 2.
  x003. Evaluate (iskxil - iskxil) - iskxil.
  x004. Work out the value of (duthzam - iskxil) - iskxil.
  x005. Evaluate (qenxil - duthzam) - hobfex.
  x006. Evaluate hobfex^3.
  x007. Which opalmis x satisfy x - hobfex = iskxil? List them all.
  x008. Which opalmis x satisfy x - hobfex = duthzam? List them all.
  x009. Solve x - keldsib = keldsib for x, naming every solution.
  x010. Solve x - iskxil = iskxil for x, naming every solution.
  x011. Solve x - qenxil = qenxil for x, naming every solution.
  x012. Which opalmis x satisfy x - iskxil = duthzam? List them all.
Level 5.
  x014. The following fails in this system: For every opalmi x: x - x = x. Name the earliest opalmi, in the order the opalmis were introduced, that witnesses the failure.
  x015. The following fails in this system: For all opalmis x, y, z: if x - y = x - z then y = z. Name the earliest opalmi, in the order the opalmis were introduced, that witnesses the failure.

# Chapter 2. Neutral objects and reversal

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through a neutral object for the first
operation, an absorbing object for the first operation and the system does not have
reversal under the first operation.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about opalmis covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A4. A neutral object for the first operation. There is a opalmi duthzam with duthzam - x
= x - duthzam = x for every x.

A5. An absorbing object for the first operation. There is a opalmi keldsib with keldsib
- x = x - keldsib = keldsib for every x.

## The shape of it

The neutral opalmi duthzam is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 opalmis the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R1 rests on S2 (the Duthsol combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Here is (hobfex - qenxil) - (duthzam - keldsib), reduced without skipping anything.
    hobfex - qenxil = iskxil   (the table for -)
    duthzam - keldsib = keldsib   (the table for -)
    iskxil - keldsib = keldsib   (the table for -)
The expression comes to keldsib.

A companion case, qenxil - (duthzam - hobfex), to show what the brackets are doing.
    duthzam - hobfex = hobfex   (the table for -)
    qenxil - hobfex = iskxil   (the table for -)
That gives iskxil, against keldsib above.

Test hobfex <~ iskxil. The espafex of hobfex is duthzam, and iskxil lies outside it, so
the relation fails.

## A case that breaks

R1. Some opalmi x admits no opalmi y for which x - y and y - x both land on a neutral
object. It fails at x = keldsib. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: S2 (the Duthsol combination tables).

What is built on it later: D5 (the sibisk) and T1 (the sibisk is the only one of its
kind).

## Proofs

R1. Some opalmi x admits no opalmi y for which x - y and y - x both land on a neutral object.

  (1) [S2] Take the case x = keldsib, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R1. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 5.
  x013. The following fails in this system: Some opalmi x admits no opalmi y for which x - y and y - x both land on a neutral object. Name the earliest opalmi, in the order the opalmis were introduced, that witnesses the failure.

# Chapter 3. The relation and what it orders

## Why this chapter

The present chapter develops antisymmetry of the relation, transitivity of the relation
and the espafex of a opalmi.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

One habit to adopt: when a statement below quantifies over opalmis, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A6. Antisymmetry of the relation. For all opalmis x and y: if x <~ y and y <~ x then x =
y.

A7. Transitivity of the relation. For all opalmis x, y, z: if x <~ y and y <~ z then x
<~ z.

D4. The espafex of a opalmi. The espafex of a opalmi x is the collection of opalmis y
for which x <~ y holds.

Worked out for each opalmi: keldsib to keldsib, duthzam, hobfex, iskxil and qenxil;
duthzam to duthzam; hobfex to duthzam; iskxil to duthzam; qenxil to duthzam.

## The shape of it

The relation is easiest to see as a height. Each opalmi casts a espafex over what it
covers, and the sizes of those shadows here are 1 and 5. Sizes repeat, so the objects do
not line up in single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 opalmis the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R4 rests on S2 (the Duthsol combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R5 rests on S2 (the Duthsol combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R6 rests on S2 (the Duthsol combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Here is (duthzam - keldsib) - hobfex, reduced without skipping anything.
    duthzam - keldsib = keldsib   (the table for -)
    keldsib - hobfex = keldsib   (the table for -)
The expression comes to keldsib.

Move the brackets and the work changes. Take keldsib - (hobfex - duthzam).
    hobfex - duthzam = hobfex   (the table for -)
    keldsib - hobfex = keldsib   (the table for -)
That gives keldsib, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
duthzam <~ iskxil hold? Read off what duthzam stands over: duthzam. iskxil is not among
them, so it fails.

## A case that breaks

R4. It is not the case that: For every opalmi x: x <~ x. It fails at x = hobfex. One
case is enough, and this is the earliest one.

R5. It is not the case that: For all opalmis x and y, at least one of x <~ y and y <~ x
holds. It fails at x = hobfex, y = hobfex. One case is enough, and this is the earliest
one.

R6. It is not the case that: For all opalmis x, y, z: if x <~ y then (z - x) <~ (z - y)
and (x - z) <~ (y - z). It fails at x = duthzam, y = duthzam, z = hobfex, side = left.
One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: S2 (the Duthsol combination tables).

What is built on it later: D9 (a hobsol), D13 (grixhob pairs), T9 (espafexs are nested
along the relation) and T10 (there is at most one hobsol).

## Proofs

R4. It is not the case that: For every opalmi x: x <~ x.

  (1) [S2] Take the case x = hobfex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R5. It is not the case that: For all opalmis x and y, at least one of x <~ y and y <~ x holds.

  (1) [S2] Take the case x = hobfex, y = hobfex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R6. It is not the case that: For all opalmis x, y, z: if x <~ y then (z - x) <~ (z - y) and (x - z) <~ (y - z).

  (1) [S2] Take the case x = duthzam, y = duthzam, z = hobfex, side = left, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the espafex of a opalmi. Each of these is used by name
later, so the names are worth learning rather than looking up.

Explicitly not available: R4, R5 and R6. A later argument that quietly assumes one of
these is wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x022. Which opalmis y satisfy keldsib <~ y? Name them all.
  x023. Which opalmis y satisfy hobfex <~ y? Name them all.
  x024. List the espafex of iskxil.
  x025. List the espafex of qenxil.
Level 5.
  x016. The following fails in this system: For every opalmi x: x <~ x. Name the earliest opalmi, in the order the opalmis were introduced, that witnesses the failure.
  x017. The following fails in this system: For all opalmis x and y, at least one of x <~ y and y <~ x holds. Name the earliest opalmi, in the order the opalmis were introduced, that witnesses the failure.
  x018. The following fails in this system: For all opalmis x, y, z: if x <~ y then (z - x) <~ (z - y) and (x - z) <~ (y - z). Name the earliest opalmi, in the order the opalmis were introduced, that witnesses the failure.

# Chapter 4. Combining objects

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is qenpyr opalmis,
opalmis that siblum and the sibisk.

Prerequisites are real here: chapters 1 and 2 supply the notions the statements below
are phrased in.

The standard of proof here is exhaustion. A universal claim about opalmis covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

## What is defined here

D1. Qenpyr opalmis. A opalmi x is called qenpyr when x - x = x.

Running the definition over every opalmi leaves keldsib and duthzam.

D2. Opalmis that siblum. Two opalmis x and y are said to siblum when x - y = y - x.

D5. The sibisk. The opalmi duthzam is called the sibisk of the system. It is the unique
opalmi that leaves every opalmi unchanged under -.

Here that is duthzam.

## The shape of it

A useful mental split: some opalmis are inert under the operation and some are not.
keldsib and duthzam come back unchanged when combined with themselves, and keldsib,
duthzam, hobfex, iskxil and qenxil commute with everything.

The neutral opalmi duthzam is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 opalmis the table is short enough to consult every time.

## Where these results come from

This chapter is groundwork. The derivations that use it start in the next one.

## A worked case

Take (iskxil - keldsib) - (duthzam - hobfex) and work it out one step at a time.
    iskxil - keldsib = keldsib   (the table for -)
    duthzam - hobfex = hobfex   (the table for -)
    keldsib - hobfex = keldsib   (the table for -)
So (iskxil - keldsib) - (duthzam - hobfex) is keldsib.

A companion case, keldsib - (duthzam - iskxil), to show what the brackets are doing.
    duthzam - iskxil = iskxil   (the table for -)
    keldsib - iskxil = keldsib   (the table for -)
The value is keldsib. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test hobfex <~ hobfex. The espafex of hobfex is duthzam, and hobfex lies outside it, so
the relation fails.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of a neutral object for the first operation
and closure under the first operation. Those are properties of this system, not of
systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A1 (closure under the first operation) and A4 (a neutral object for the
first operation).

These results are used again in D6 (the zamlorn), D7 (the tarnsol), D10 (gelpyr opalmis)
and T1 (the sibisk is the only one of its kind).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

Carry forward qenpyr opalmis, opalmis that siblum and the sibisk. Later chapters state
their results in these terms and do not restate the definitions.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 2.
  x026. Name the sibisk of the system.
Level 3.
  x019. Which opalmis make up the qenpyr? Name them all.

# Chapter 5. The relation and what it orders (2)

## Why this chapter

The results collected here were not found in this order. Grixhob pairs, brarast
collections and a hobsol came first, and the rest was assembled around that once the
pattern was visible.

Nothing here stands on its own. The arguments lean on chapters 1 and 3, and a reader who
has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about opalmis covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D13. Grixhob pairs. Two distinct opalmis x and y form a grixhob pair when x <~ y and y
<~ x both hold, that is, when each lies in the espafex of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D3. Brarast collections. A collection S of opalmis is brarast when x - y belongs to S
for every pair x, y drawn from S.

D9. A hobsol. A opalmi f is a hobsol when f <~ y holds for every opalmi y, that is, when
the espafex of f is the whole system.

In this system that picks out keldsib, which is 1 of the 5 opalmis.

## The shape of it

The right picture for nakyuk is a spreading stain rather than a list. Drop one opalmi
in, apply the operation to whatever is wet, repeat. The stain here reaches 1, 2 and 4
opalmis depending on where it started.

The relation is easiest to see as a height. Each opalmi casts a espafex over what it
covers, and the sizes of those shadows here are 1 and 5. Sizes repeat, so the objects do
not line up in single file.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R10 rests on D4 (the espafex of a opalmi). Remove any one of them and the statement
stops making sense, not merely stops being provable.

T9 rests on D4 (the espafex of a opalmi) and A7 (transitivity of the relation). The
dependence is on the content of those results, not only on their vocabulary.

## A worked case

Here is (hobfex - duthzam) - qenxil, reduced without skipping anything.
    hobfex - duthzam = hobfex   (the table for -)
    hobfex - qenxil = iskxil   (the table for -)
That leaves iskxil, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is duthzam - (qenxil - hobfex) for contrast.
    qenxil - hobfex = iskxil   (the table for -)
    duthzam - iskxil = iskxil   (the table for -)
That gives iskxil, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
duthzam <~ keldsib hold? Read off what duthzam stands over: duthzam. keldsib is not
among them, so it fails.

## A case that breaks

R10. It is not the case that: If x <~ y then y <~ x. The case that settles it: x =
keldsib, y = duthzam. Anyone carrying this claim over from a more familiar system will
be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation and
transitivity of the relation. Those are properties of this system, not of systems in
general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A1 (closure under the first operation), A7 (transitivity of the relation)
and D4 (the espafex of a opalmi).

What is built on it later: D8 (the nakyuk of a opalmi), T3 (the zamlorn is brarast), T4
(the nakyuk of a opalmi is brarast) and T8 (the tarnsol is brarast).

## Proofs

R10. It is not the case that: If x <~ y then y <~ x.

  (1) [S2] Take the case x = keldsib, y = duthzam, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T9. If y lies in the espafex of x, then the espafex of y is contained in the espafex of x.

  (1) [D4] Let y satisfy x <~ y and let z satisfy y <~ z.
  (2) [A7] Transitivity gives x <~ z.
  (3) [D4] So every member of the espafex of y is a member of that of x.

Checked over 125 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward grixhob pairs, brarast collections and a hobsol. Later chapters state
their results in these terms and do not restate the definitions.

Established here and safe to use: T9.

Do not carry forward R10. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x020. How many opalmis lie in the smallest brarast collection containing duthzam?
  x021. How many opalmis lie in the smallest brarast collection containing hobfex?
Level 4.
  x032. Which opalmis make up the hobsol? Name them all.
  x046. The result above concerns espafexs. List the espafex of keldsib.
  x047. The result above concerns espafexs. List the espafex of hobfex.
Level 5.
  x050. The following fails in this system: If x <~ y then y <~ x. Name the earliest opalmi, in the order the opalmis were introduced, that witnesses the failure.

# Chapter 6. Neutral objects and reversal (2)

## Why this chapter

The practical content of this chapter is gelpyr opalmis, the zamlorn and the tarnsol. It
is the part that shows up in use.

Nothing here stands on its own. The arguments lean on chapters 2 and 4, and a reader who
has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
opalmis that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D10. Gelpyr opalmis. A opalmi x is gelpyr when x - x equals the sibisk.

In this system that picks out duthzam and qenxil, which is 2 of the 5 opalmis.

D6. The zamlorn. The zamlorn of the system is the collection of opalmis that siblum with
every opalmi.

Running the definition over every opalmi leaves keldsib, duthzam, hobfex, iskxil and
qenxil.

D7. The tarnsol. The tarnsol is the collection of all qenpyr opalmis.

Running the definition over every opalmi leaves keldsib and duthzam.

## The shape of it

Two questions sort the opalmis quickly. Does combining a opalmi with itself change it?
For keldsib and duthzam it does not. Does it matter which side it goes on? For keldsib,
duthzam, hobfex, iskxil and qenxil it does not.

Neutrality is a strong condition disguised as a weak one. It fixes a single opalmi and,
through that, constrains everything that can combine with it.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R11 rests on D5 (the sibisk). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T1 rests on D5 (the sibisk) and A4 (a neutral object for the first operation). The
dependence is on the content of those results, not only on their vocabulary.

## A worked case

Evaluate (qenxil - duthzam) - (hobfex - iskxil). Each line below is one lookup in a
table.
    qenxil - duthzam = qenxil   (the table for -)
    hobfex - iskxil = duthzam   (the table for -)
    qenxil - duthzam = qenxil   (the table for -)
The expression comes to qenxil.

Bracketing is not cosmetic, so here is duthzam - (hobfex - qenxil) for contrast.
    hobfex - qenxil = iskxil   (the table for -)
    duthzam - iskxil = iskxil   (the table for -)
The value is iskxil, not qenxil.

Test iskxil <~ duthzam. The espafex of iskxil is duthzam, and duthzam lies inside it, so
the relation holds.

## A case that breaks

R11. It is not the case that: e - x equals the sibisk for every opalmi x. The case that
settles it: anchor = duthzam, x = keldsib, value = keldsib. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of a neutral object for the first operation
and closure under the first operation. Those are properties of this system, not of
systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A4 (a neutral object for the first operation), D1 (qenpyr opalmis), D2
(opalmis that siblum) and D5 (the sibisk).

These results are used again in T2 (the sibisk lies in the zamlorn), T3 (the zamlorn is
brarast), T7 (the nakyuk of a zamlorn opalmi stays in the zamlorn) and T8 (the tarnsol
is brarast).

## Proofs

R11. It is not the case that: e - x equals the sibisk for every opalmi x.

  (1) [S2] Take the case anchor = duthzam, x = keldsib, value = keldsib, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T1. There is exactly one opalmi e with e - x = x - e = x for every opalmi x.

  (1) [D5] Suppose e and f both leave every opalmi unchanged.
  (2) [A4] Then e - f = f, reading e as neutral on the left.
  (3) [A4] And e - f = e, reading f as neutral on the right.
  (4) So e = f, and the two suppositions describe the same object.

Checked over 25 cases: every object paired with every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward gelpyr opalmis, the zamlorn and the tarnsol. Later chapters state their
results in these terms and do not restate the definitions.

Established here and safe to use: T1.

Explicitly not available: R11. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x027. Which opalmis make up the tarnsol? Name them all.
  x033. Which opalmis make up the gelpyr? Name them all.
Level 5.
  x051. The following fails in this system: e - x equals the sibisk for every opalmi x. Name the earliest opalmi, in the order the opalmis were introduced, that witnesses the failure.

# Chapter 7. The relation and what it orders (3)

## Why this chapter

So far the opalmis have been objects to be pushed around. This chapter starts asking
what they are like. We take up the nakyuk of a opalmi, there is at most one hobsol and
no grixhob pairs exist.

Prerequisites are real here: chapters 3 and 5 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over opalmis, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D8. The nakyuk of a opalmi. The nakyuk of a opalmi x, written [x], is the smallest
brarast collection that contains x.

Worked out for each opalmi: keldsib to keldsib; duthzam to duthzam; hobfex to duthzam,
hobfex, iskxil and qenxil; iskxil to duthzam, hobfex, iskxil and qenxil; qenxil to
duthzam and qenxil.

## The shape of it

The right picture for nakyuk is a spreading stain rather than a list. Drop one opalmi
in, apply the operation to whatever is wet, repeat. The stain here reaches 1, 2 and 4
opalmis depending on where it started.

The relation is easiest to see as a height. Each opalmi casts a espafex over what it
covers, and the sizes of those shadows here are 1 and 5. Sizes repeat, so the objects do
not line up in single file.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T10 rests on D9 (a hobsol) and A6 (antisymmetry of the relation). Remove any one of them
and the statement stops making sense, not merely stops being provable.

T11 rests on D13 (grixhob pairs) and A6 (antisymmetry of the relation). Remove any one
of them and the statement stops making sense, not merely stops being provable.

## A worked case

Take (hobfex - iskxil) - duthzam and work it out one step at a time.
    hobfex - iskxil = duthzam   (the table for -)
    duthzam - duthzam = duthzam   (the table for -)
That leaves duthzam, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is iskxil - (duthzam - hobfex) for contrast.
    duthzam - hobfex = hobfex   (the table for -)
    iskxil - hobfex = duthzam   (the table for -)
That gives duthzam, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
keldsib <~ qenxil hold? Read off what keldsib stands over: keldsib, duthzam, hobfex,
iskxil and qenxil. qenxil is among them, so it holds.

A second case, this time a nakyuk. Start from hobfex. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is duthzam, hobfex,
iskxil and qenxil, so the vexisk of hobfex is 4.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of opalmis that come back
unchanged from themselves: keldsib and duthzam. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of antisymmetry of the relation and closure
under the first operation. Those are properties of this system, not of systems in
general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A6 (antisymmetry of the relation), D13 (grixhob pairs), D3 (brarast
collections) and D9 (a hobsol).

What is built on it later: D11 (the vexisk of a opalmi), T4 (the nakyuk of a opalmi is
brarast), T5 (the nakyuk is contained in every brarast collection) and T7 (the nakyuk of
a zamlorn opalmi stays in the zamlorn).

## Proofs

T10. No two distinct opalmis can both be hobsols.

  (1) [D9] Let f and h both be floors.
  (2) [D9] Then f <~ h, since h is any object, and h <~ f likewise.
  (3) [A6] Antisymmetry forces f = h.

Checked over 25 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T11. No two distinct opalmis lie in each other's espafex.

  (1) [D13] Suppose x and y form a tight pair.
  (2) [A6] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the nakyuk of a opalmi. Later chapters state their results in these terms
and do not restate the definitions.

The results now available are T10 and T11, each settled by exhaustive check rather than
by argument from analogy.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x028. List the nakyuk of hobfex.
  x029. List the nakyuk of iskxil.
  x030. List the nakyuk of qenxil.
Level 4.
  x031. Let z be duthzam - iskxil. List the nakyuk of z.
  x048. This result is about the hobsol. List every opalmi in it.

# Chapter 8. Combining objects (2)

## Why this chapter

The present chapter develops where every opalmi is qenpyr breaks down, every opalmi lies
in the zamlorn and the sibisk lies in the zamlorn.

Prerequisites are real here: chapters 1, 4, 5 and 6 supply the notions the statements
below are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
opalmis that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

Two questions sort the opalmis quickly. Does combining a opalmi with itself change it?
For keldsib and duthzam it does not. Does it matter which side it goes on? For keldsib,
duthzam, hobfex, iskxil and qenxil it does not.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 opalmis the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R8 rests on D7 (the tarnsol). The dependence is on the content of those results, not
only on their vocabulary.

T12 rests on D6 (the zamlorn). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T2 rests on D5 (the sibisk) and D6 (the zamlorn). The dependence is on the content of
those results, not only on their vocabulary.

T3 rests on D6 (the zamlorn), D3 (brarast collections) and A2 (association of the first
operation). Remove any one of them and the statement stops making sense, not merely
stops being provable.

T8 rests on D7 (the tarnsol) and D3 (brarast collections). Remove any one of them and
the statement stops making sense, not merely stops being provable.

## A worked case

Evaluate (keldsib - duthzam) - (hobfex - iskxil). Each line below is one lookup in a
table.
    keldsib - duthzam = keldsib   (the table for -)
    hobfex - iskxil = duthzam   (the table for -)
    keldsib - duthzam = keldsib   (the table for -)
So (keldsib - duthzam) - (hobfex - iskxil) is keldsib.

Bracketing is not cosmetic, so here is duthzam - (hobfex - keldsib) for contrast.
    hobfex - keldsib = keldsib   (the table for -)
    duthzam - keldsib = keldsib   (the table for -)
That gives keldsib, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
duthzam <~ keldsib hold? Read off what duthzam stands over: duthzam. keldsib is not
among them, so it fails.

## A case that breaks

R8. It is not the case that: x - x = x for every opalmi x. It fails at x = hobfex, value
= qenxil. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation and closure under the first operation. Those are
properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A2 (association of the first operation), D3 (brarast collections), D5
(the sibisk) and D6 (the zamlorn).

What is built on it later: T7 (the nakyuk of a zamlorn opalmi stays in the zamlorn).

## Proofs

R8. It is not the case that: x - x = x for every opalmi x.

  (1) [S2] Take the case x = hobfex, value = qenxil, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T12. Every pair of opalmis siblums.

  (1) [D6] The zamlorn is defined by sibluming with everything.
  (2) [D2] The claim is that x - y = y - x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T2. The sibisk siblums with every opalmi.

  (1) [D5] Let e be the sibisk and x any opalmi.
  (2) [D5] Then e - x = x and x - e = x.
  (3) [D2] So e - x = x - e, which is what it means to siblum.
  (4) [D6] Since x was arbitrary, e belongs to the zamlorn.

Checked over 5 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. If x and y both siblum with every opalmi, then so does x - y.

  (1) [D6] Let x and y lie in the zamlorn and let z be any opalmi.
  (2) [A2] Then (x - y) - z = x - (y - z).
  (3) [D6] Move z past y, then past x, using that each siblums with everything.
  (4) [D3] So x - y siblums with z, and the zamlorn is brarast.

Checked over 25 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

T8. If x and y are both qenpyr then so is x - y.

  (1) [D7] Let x and y be qenpyr.
  (2) [D1] The claim asks whether (x - y) - (x - y) returns x - y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 25 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

The results now available are T12, T2, T3 and T8, each settled by exhaustive check
rather than by argument from analogy.

Explicitly not available: R8. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x045. This result is about the tarnsol. List every opalmi in it.
Level 5.
  x049. The following fails in this system: x - x = x for every opalmi x. Name the earliest opalmi, in the order the opalmis were introduced, that witnesses the failure.

# Chapter 9. Collections that close on themselves

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is the vexisk of a
opalmi, the nakyuk of a opalmi is brarast and the nakyuk of a zamlorn opalmi stays in
the zamlorn.

Nothing here stands on its own. The arguments lean on chapters 5, 6, 7 and 8, and a
reader who has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
opalmis that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D11. The vexisk of a opalmi. The vexisk of a opalmi x is the number of opalmis in its
nakyuk [x].

Worked out for each opalmi: keldsib to 1; duthzam to 1; hobfex to 4; iskxil to 4; qenxil
to 2.

## The shape of it

The right picture for nakyuk is a spreading stain rather than a list. Drop one opalmi
in, apply the operation to whatever is wet, repeat. The stain here reaches 1, 2 and 4
opalmis depending on where it started.

Two questions sort the opalmis quickly. Does combining a opalmi with itself change it?
For keldsib and duthzam it does not. Does it matter which side it goes on? For keldsib,
duthzam, hobfex, iskxil and qenxil it does not.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T4 rests on D8 (the nakyuk of a opalmi) and D3 (brarast collections). Remove any one of
them and the statement stops making sense, not merely stops being provable.

T7 rests on D8 (the nakyuk of a opalmi), D6 (the zamlorn) and T3 (the zamlorn is
brarast). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Here is (qenxil - duthzam) - keldsib, reduced without skipping anything.
    qenxil - duthzam = qenxil   (the table for -)
    qenxil - keldsib = keldsib   (the table for -)
That leaves keldsib, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take duthzam - (keldsib - qenxil).
    keldsib - qenxil = keldsib   (the table for -)
    duthzam - keldsib = keldsib   (the table for -)
The value is keldsib. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test duthzam <~ qenxil. The espafex of duthzam is duthzam, and qenxil lies outside it,
so the relation fails.

Now compute [hobfex]. Fold hobfex against itself, then fold whatever appeared against
everything present, and stop when a round adds nothing. The result is duthzam, hobfex,
iskxil and qenxil, of size 4.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by association of the first operation and closure under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside D3 (brarast collections), D6 (the zamlorn), D8 (the nakyuk of a opalmi)
and T3 (the zamlorn is brarast).

These results are used again in D12 (the duthpon), T5 (the nakyuk is contained in every
brarast collection), T6 (a opalmi is qenpyr exactly when its vexisk is one) and R7
(where the vexisk divides the number of opalmis breaks down).

## Proofs

T4. For every opalmi x, the collection [x] is brarast.

  (1) [D8] [x] is built by taking x and closing under -.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 125 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

T7. If x lies in the zamlorn then every opalmi of [x] lies in the zamlorn.

  (1) [T3] The zamlorn is brarast.
  (2) [D8] [x] is the smallest brarast collection containing x.
  (3) A smallest such collection sits inside any other, and the zamlorn is one.

Checked over 25 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the vexisk of a opalmi. Each of these is used by name
later, so the names are worth learning rather than looking up.

Established here and safe to use: T4 and T7.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x034. How many opalmis lie in [duthzam]?
  x035. How many opalmis lie in [hobfex]?
  x036. How many opalmis lie in [iskxil]?
  x037. What is the vexisk of qenxil?
Level 5.
  x038. Let z be (duthzam - keldsib) - hobfex. What is the vexisk of z?
  x039. Let z be (hobfex - hobfex) - hobfex. What is the vexisk of z?
  x040. Let z be (hobfex - keldsib) - keldsib. What is the vexisk of z?
  x041. Let z be (keldsib - hobfex) - keldsib. What is the vexisk of z?

# Chapter 10. Collections that close on themselves (2)

## Why this chapter

What follows was pieced together backwards. The last item of it, the duthpon, where the
vexisk divides the number of opalmis breaks down and where some opalmi reaches every
other breaks down, was noticed before anyone had a reason to expect it.

Nothing here stands on its own. The arguments lean on chapters 4, 7 and 9, and a reader
who has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over opalmis, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D12. The duthpon. The duthpon of the system is the collection of opalmis whose vexisk is
largest.

Running the definition over every opalmi leaves hobfex and iskxil.

## The shape of it

The right picture for nakyuk is a spreading stain rather than a list. Drop one opalmi
in, apply the operation to whatever is wet, repeat. The stain here reaches 1, 2 and 4
opalmis depending on where it started.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 opalmis the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R7 rests on D11 (the vexisk of a opalmi) and T4 (the nakyuk of a opalmi is brarast).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

R9 rests on D8 (the nakyuk of a opalmi) and D11 (the vexisk of a opalmi). Remove any one
of them and the statement stops making sense, not merely stops being provable.

T5 rests on D8 (the nakyuk of a opalmi) and T4 (the nakyuk of a opalmi is brarast).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

T6 rests on D1 (qenpyr opalmis), D11 (the vexisk of a opalmi) and T4 (the nakyuk of a
opalmi is brarast). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Take (qenxil - keldsib) - (iskxil - duthzam) and work it out one step at a time.
    qenxil - keldsib = keldsib   (the table for -)
    iskxil - duthzam = iskxil   (the table for -)
    keldsib - iskxil = keldsib   (the table for -)
So (qenxil - keldsib) - (iskxil - duthzam) is keldsib.

Bracketing is not cosmetic, so here is keldsib - (iskxil - qenxil) for contrast.
    iskxil - qenxil = hobfex   (the table for -)
    keldsib - hobfex = keldsib   (the table for -)
That gives keldsib, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
duthzam <~ hobfex hold? Read off what duthzam stands over: duthzam. hobfex is not among
them, so it fails.

## A case that breaks

R7. It is not the case that: For every opalmi x, the vexisk of x divides 5. The case
that settles it: x = hobfex, reach = 4, size = 5. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

R9. It is not the case that: There is a opalmi whose nakyuk is the whole system. It
fails at largest_span = 4, size = 5. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside D1 (qenpyr opalmis), D11 (the vexisk of a opalmi), D8 (the nakyuk of a
opalmi) and T4 (the nakyuk of a opalmi is brarast).

## Proofs

R7. It is not the case that: For every opalmi x, the vexisk of x divides 5.

  (1) [S2] Take the case x = hobfex, reach = 4, size = 5, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

R9. It is not the case that: There is a opalmi whose nakyuk is the whole system.

  (1) [S2] Take the case largest_span = 4, size = 5, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T5. If S is brarast and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 35 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T6. x - x = x holds if and only if [x] contains x alone.

  (1) [D1] If x - x = x then {x} is already closed under -.
  (2) [T4] So [x] = {x} and the vexisk is one.
  (3) [D11] Conversely a span of one object must contain x - x, which is then x.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the duthpon. Each of these is used by name later, so
the names are worth learning rather than looking up.

The results now available are T5 and T6, each settled by exhaustive check rather than by
argument from analogy.

Do not carry forward R7 and R9. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x042. List every opalmi in the duthpon.
  x043. What is the largest vexisk any opalmi has?
Level 5.
  x044. The following fails in this system: For every opalmi x, the vexisk of x divides 5. Name the earliest opalmi, in the order the opalmis were introduced, that witnesses the failure.
