# The Umbtu system

The Umbtu system is small enough to hold in the hand and strange enough to be worth the
trouble. It has 5 drigrixs, two operations, and one relation, and nothing else.

The drigrixs are written solvex, umbazt, glimmux, vashtez and qenvex. The first
operation is written @. The second is written + and binds more tightly, so x @ y + z
means x @ (y + z). The relation is written ::; where it holds between two drigrixs we
say the left one covers the right one. Both operations associate to the left when
written without brackets, and brackets override that. Repeated combination is
abbreviated: x^3 means x @ x @ x.

A warning that will be repeated because it is the one readers ignore: nothing here is
inherited from arithmetic. Familiar names have been avoided on purpose. Where a law of
arithmetic happens to hold it is stated and checked, and where it fails a counterexample
is given.

# Chapter 1. The objects and their notation

## Why this chapter

We turn to the Umbtu signature, the Umbtu combination tables and closure under the first
operation. The treatment is self contained given the material already established.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
drigrixs that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## The tables in full

The table for @. Read the left argument down the side and the right argument across the top.

         |   solvex   umbazt  glimmux  vashtez   qenvex
-------------------------------------------------------
  solvex |   solvex   umbazt  glimmux  vashtez   qenvex
  umbazt |   umbazt  glimmux  vashtez   qenvex   qenvex
 glimmux |  glimmux  vashtez   qenvex   qenvex   qenvex
 vashtez |  vashtez   qenvex   qenvex   qenvex   qenvex
  qenvex |   qenvex   qenvex   qenvex   qenvex   qenvex

The table for +. Read the left argument down the side and the right argument across the top.

         |   solvex   umbazt  glimmux  vashtez   qenvex
-------------------------------------------------------
  solvex |   solvex   solvex   solvex   solvex   solvex
  umbazt |   solvex   umbazt   umbazt   umbazt   umbazt
 glimmux |   solvex   umbazt  glimmux  glimmux  glimmux
 vashtez |   solvex   umbazt  glimmux  vashtez  vashtez
  qenvex |   solvex   umbazt  glimmux  vashtez   qenvex

Every pair standing in the :: relation, grouped by left argument.

  solvex :: solvex
  umbazt :: solvex
  glimmux :: solvex
  vashtez :: solvex
  qenvex :: solvex, umbazt, glimmux, vashtez and qenvex

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A1. Closure under the first operation. For all drigrixs x and y, x @ y is again a
drigrix.

A2. Association of the first operation. For all drigrixs x, y, z: (x @ y) @ z = x @ (y @
z).

A3. Commutation of the first operation. For all drigrixs x and y: x @ y = y @ x.

## The shape of it

A useful mental split: some drigrixs are inert under the operation and some are not.
solvex and qenvex come back unchanged when combined with themselves, and solvex, umbazt,
glimmux, vashtez and qenvex commute with everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 drigrixs the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R2 rests on S2 (the Umbtu combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

R3 rests on S2 (the Umbtu combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

## A worked case

Evaluate umbazt @ glimmux + vashtez. Each line below is one lookup in a table.
    glimmux + vashtez = glimmux   (the table for +)
    umbazt @ glimmux = vashtez   (the table for @)
The expression comes to vashtez.

Bracketing is not cosmetic, so here is glimmux @ (vashtez @ umbazt) for contrast.
    vashtez @ umbazt = qenvex   (the table for @)
    glimmux @ qenvex = qenvex   (the table for @)
The value is qenvex, not vashtez.

One decision about the relation, since deciding is as much a skill as computing. Does
qenvex :: umbazt hold? Read off what qenvex stands over: solvex, umbazt, glimmux,
vashtez and qenvex. umbazt is among them, so it holds.

## A case that breaks

R2. It is not the case that: For every drigrix x: x @ x = x. The case that settles it: x
= umbazt, value = glimmux. Anyone carrying this claim over from a more familiar system
will be wrong here, and wrong in a way that propagates.

R3. It is not the case that: For all drigrixs x, y, z: if x @ y = x @ z then y = z. It
fails at x = umbazt, y = vashtez, z = qenvex. One case is enough, and this is the
earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

These results are used again in A4 (a neutral object for the first operation), A5 (an
absorbing object for the first operation), A6 (closure under the second operation) and
A7 (association of the second operation).

## Proofs

R2. It is not the case that: For every drigrix x: x @ x = x.

  (1) [S2] Take the case x = umbazt, value = glimmux, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R3. It is not the case that: For all drigrixs x, y, z: if x @ y = x @ z then y = z.

  (1) [S2] Take the case x = umbazt, y = vashtez, z = qenvex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R2 and R3. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 1.
  x001. What drigrix does vashtez @ vashtez name?
  x002. Reduce vashtez @ umbazt to a single drigrix.
Level 2.
  x003. Work out the value of (glimmux @ solvex) @ umbazt.
  x004. What drigrix does (umbazt @ glimmux) @ umbazt name?
  x006. Evaluate glimmux^3.
  x007. Which drigrixs x satisfy x @ qenvex = qenvex? List them all.
  x008. Which drigrixs x satisfy x @ glimmux = qenvex? List them all.
Level 3.
  x005. What drigrix does (umbazt @ solvex) @ (glimmux @ solvex) name?
  x009. Evaluate glimmux @ umbazt + qenvex, minding which operation binds tighter.
Level 5.
  x011. The following fails in this system: For every drigrix x: x @ x = x. Name the earliest drigrix, in the order the drigrixs were introduced, that witnesses the failure.
  x012. The following fails in this system: For all drigrixs x, y, z: if x @ y = x @ z then y = z. Name the earliest drigrix, in the order the drigrixs were introduced, that witnesses the failure.

# Chapter 2. Neutral objects and reversal

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is a neutral object
for the first operation, an absorbing object for the first operation and the system does
not have reversal under the first operation.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

The standard of proof here is exhaustion. A universal claim about drigrixs covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A4. A neutral object for the first operation. There is a drigrix solvex with solvex @ x
= x @ solvex = x for every x.

A5. An absorbing object for the first operation. There is a drigrix qenvex with qenvex @
x = x @ qenvex = qenvex for every x.

## The shape of it

Neutrality is a strong condition disguised as a weak one. It fixes a single drigrix and,
through that, constrains everything that can combine with it.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 drigrixs the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R1 rests on S2 (the Umbtu combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

## A worked case

Here is (qenvex @ vashtez) @ (umbazt @ glimmux), reduced without skipping anything.
    qenvex @ vashtez = qenvex   (the table for @)
    umbazt @ glimmux = vashtez   (the table for @)
    qenvex @ vashtez = qenvex   (the table for @)
So (qenvex @ vashtez) @ (umbazt @ glimmux) is qenvex.

Move the brackets and the work changes. Take vashtez @ (umbazt @ qenvex).
    umbazt @ qenvex = qenvex   (the table for @)
    vashtez @ qenvex = qenvex   (the table for @)
The value is qenvex. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test vashtez :: vashtez. The aztdri of vashtez is solvex, and vashtez lies outside it,
so the relation fails.

## A case that breaks

R1. Some drigrix x admits no drigrix y for which x @ y and y @ x both land on a neutral
object. The case that settles it: x = umbazt. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: S2 (the Umbtu combination tables).

These results are used again in D5 (the mornvint) and T1 (the mornvint is the only one
of its kind).

## Proofs

R1. Some drigrix x admits no drigrix y for which x @ y and y @ x both land on a neutral object.

  (1) [S2] Take the case x = umbazt, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R1. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 5.
  x010. The following fails in this system: Some drigrix x admits no drigrix y for which x @ y and y @ x both land on a neutral object. Name the earliest drigrix, in the order the drigrixs were introduced, that witnesses the failure.

# Chapter 3. The relation and what it orders

## Why this chapter

The results collected here were not found in this order. Antisymmetry of the relation,
transitivity of the relation and the aztdri of a drigrix came first, and the rest was
assembled around that once the pattern was visible.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over drigrixs, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A11. Antisymmetry of the relation. For all drigrixs x and y: if x :: y and y :: x then x
= y.

A12. Transitivity of the relation. For all drigrixs x, y, z: if x :: y and y :: z then x
:: z.

D4. The aztdri of a drigrix. The aztdri of a drigrix x is the collection of drigrixs y
for which x :: y holds.

Worked out for each drigrix: solvex to solvex; umbazt to solvex; glimmux to solvex;
vashtez to solvex; qenvex to solvex, umbazt, glimmux, vashtez and qenvex.

## The shape of it

The relation is easiest to see as a height. Each drigrix casts a aztdri over what it
covers, and the sizes of those shadows here are 1 and 5. Sizes repeat, so the objects do
not line up in single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 drigrixs the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R6 rests on S2 (the Umbtu combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

R7 rests on S2 (the Umbtu combination tables). The dependence is on the content of those
results, not only on their vocabulary.

R8 rests on S2 (the Umbtu combination tables). The dependence is on the content of those
results, not only on their vocabulary.

R9 rests on S2 (the Umbtu combination tables). The dependence is on the content of those
results, not only on their vocabulary.

## A worked case

Here is qenvex @ glimmux + solvex, reduced without skipping anything.
    glimmux + solvex = solvex   (the table for +)
    qenvex @ solvex = qenvex   (the table for @)
The expression comes to qenvex.

Bracketing is not cosmetic, so here is glimmux @ (solvex @ qenvex) for contrast.
    solvex @ qenvex = qenvex   (the table for @)
    glimmux @ qenvex = qenvex   (the table for @)
That gives qenvex, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test umbazt :: vashtez. The aztdri of umbazt is solvex, and vashtez lies outside it, so
the relation fails.

## A case that breaks

R6. It is not the case that: For every drigrix x: x :: x. The case that settles it: x =
umbazt. Anyone carrying this claim over from a more familiar system will be wrong here,
and wrong in a way that propagates.

R7. It is not the case that: For all drigrixs x and y, at least one of x :: y and y :: x
holds. The case that settles it: x = umbazt, y = umbazt. Anyone carrying this claim over
from a more familiar system will be wrong here, and wrong in a way that propagates.

R8. It is not the case that: For all drigrixs x, y, z: if x :: y then (z @ x) :: (z @ y)
and (x @ z) :: (y @ z). It fails at x = solvex, y = solvex, z = umbazt, side = left. One
case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside S2 (the Umbtu combination tables).

What is built on it later: D9 (a grixvash), D13 (nakkeld pairs), T9 (aztdris are nested
along the relation) and T10 (there is at most one grixvash).

## Proofs

R6. It is not the case that: For every drigrix x: x :: x.

  (1) [S2] Take the case x = umbazt, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R7. It is not the case that: For all drigrixs x and y, at least one of x :: y and y :: x holds.

  (1) [S2] Take the case x = umbazt, y = umbazt, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R8. It is not the case that: For all drigrixs x, y, z: if x :: y then (z @ x) :: (z @ y) and (x @ z) :: (y @ z).

  (1) [S2] Take the case x = solvex, y = solvex, z = umbazt, side = left, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R9. It is not the case that: For all drigrixs x, y, z: if x :: y then (z + x) :: (z + y) and (x + z) :: (y + z).

  (1) [S2] Take the case x = qenvex, y = umbazt, z = umbazt, side = left, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the aztdri of a drigrix. Each of these is used by name
later, so the names are worth learning rather than looking up.

Explicitly not available: R6, R7, R8 and R9. A later argument that quietly assumes one
of these is wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x019. Which drigrixs y satisfy umbazt :: y? Name them all.
  x020. List the aztdri of glimmux.
  x021. Which drigrixs y satisfy vashtez :: y? Name them all.
  x022. List the aztdri of qenvex.
Level 5.
  x013. The following fails in this system: For every drigrix x: x :: x. Name the earliest drigrix, in the order the drigrixs were introduced, that witnesses the failure.
  x014. The following fails in this system: For all drigrixs x and y, at least one of x :: y and y :: x holds. Name the earliest drigrix, in the order the drigrixs were introduced, that witnesses the failure.
  x015. The following fails in this system: For all drigrixs x, y, z: if x :: y then (z @ x) :: (z @ y) and (x @ z) :: (y @ z). Name the earliest drigrix, in the order the drigrixs were introduced, that witnesses the failure.

# Chapter 4. The second operation and how the two interact

## Why this chapter

Anyone using this system to keep track of something will meet self combination under the
second operation, closure under the second operation and association of the second
operation early, whether or not they go looking.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
drigrixs that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A10. Self combination under the second operation. For every drigrix x: x + x = x.

A6. Closure under the second operation. For all drigrixs x and y, x + y is again a
drigrix.

A7. Association of the second operation. For all drigrixs x, y, z: (x + y) + z = x + (y
+ z).

A8. Commutation of the second operation. For all drigrixs x and y: x + y = y + x.

A9. A neutral object for the second operation. There is a drigrix qenvex with qenvex + x
= x for every x.

## The shape of it

The interesting content of a two operation system sits in the gap between them: which
one distributes over which, and which drigrixs are fixed by both.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R4 rests on S2 (the Umbtu combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

R5 rests on S2 (the Umbtu combination tables). The dependence is on the content of those
results, not only on their vocabulary.

## A worked case

Evaluate (vashtez @ qenvex) @ (glimmux @ umbazt). Each line below is one lookup in a
table.
    vashtez @ qenvex = qenvex   (the table for @)
    glimmux @ umbazt = vashtez   (the table for @)
    qenvex @ vashtez = qenvex   (the table for @)
That leaves qenvex, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is qenvex @ (glimmux @ vashtez) for contrast.
    glimmux @ vashtez = qenvex   (the table for @)
    qenvex @ qenvex = qenvex   (the table for @)
That gives qenvex, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
qenvex :: umbazt hold? Read off what qenvex stands over: solvex, umbazt, glimmux,
vashtez and qenvex. umbazt is among them, so it holds.

## A case that breaks

R4. It is not the case that: For all drigrixs x, y, z: x + (y @ z) = (x + y) @ (x + z),
and the same on the right. The case that settles it: x = umbazt, y = umbazt, z = umbazt,
left = umbazt, right = glimmux. Anyone carrying this claim over from a more familiar
system will be wrong here, and wrong in a way that propagates.

R5. It is not the case that: For all drigrixs x and y: x @ (x + y) = x and x + (x @ y) =
x. It fails at x = umbazt, y = umbazt, value = glimmux. One case is enough, and this is
the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: S2 (the Umbtu combination tables).

These results are used again in T13 (the second operation keeps the kapon intact).

## Proofs

R4. It is not the case that: For all drigrixs x, y, z: x + (y @ z) = (x + y) @ (x + z), and the same on the right.

  (1) [S2] Take the case x = umbazt, y = umbazt, z = umbazt, left = umbazt, right = glimmux, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R5. It is not the case that: For all drigrixs x and y: x @ (x + y) = x and x + (x @ y) = x.

  (1) [S2] Take the case x = umbazt, y = umbazt, value = glimmux, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R4 and R5. A later argument that quietly assumes one of these
is wrong, and the counterexamples above say exactly where.

## Exercises

No exercises here. Every question this chapter suggested turned out to be answerable
from the question itself, so all of them were discarded.

# Chapter 5. Combining objects

## Why this chapter

So far the drigrixs have been objects to be pushed around. This chapter starts asking
what they are like. We take up opalrast drigrixs, drigrixs that korrhob and the
mornvint.

Prerequisites are real here: chapters 1 and 2 supply the notions the statements below
are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
drigrixs that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D1. Opalrast drigrixs. A drigrix x is called opalrast when x @ x = x.

Running the definition over every drigrix leaves solvex and qenvex.

D2. Drigrixs that korrhob. Two drigrixs x and y are said to korrhob when x @ y = y @ x.

D5. The mornvint. The drigrix solvex is called the mornvint of the system. It is the
unique drigrix that leaves every drigrix unchanged under @.

Here that is solvex.

## The shape of it

Two questions sort the drigrixs quickly. Does combining a drigrix with itself change it?
For solvex and qenvex it does not. Does it matter which side it goes on? For solvex,
umbazt, glimmux, vashtez and qenvex it does not.

Neutrality is a strong condition disguised as a weak one. It fixes a single drigrix and,
through that, constrains everything that can combine with it.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 drigrixs the table is short enough to consult every time.

## Where these results come from

This chapter is groundwork. The derivations that use it start in the next one.

## A worked case

Take solvex @ umbazt + glimmux and work it out one step at a time.
    umbazt + glimmux = umbazt   (the table for +)
    solvex @ umbazt = umbazt   (the table for @)
So solvex @ umbazt + glimmux is umbazt.

A companion case, umbazt @ (glimmux @ solvex), to show what the brackets are doing.
    glimmux @ solvex = glimmux   (the table for @)
    umbazt @ glimmux = vashtez   (the table for @)
The value is vashtez, not umbazt.

Test vashtez :: glimmux. The aztdri of vashtez is solvex, and glimmux lies outside it,
so the relation fails.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation
and closure under the first operation. Those are properties of this system, not of
systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A1 (closure under the first operation) and A4 (a
neutral object for the first operation).

These results are used again in D6 (the kapon), D7 (the tezjen), D10 (qennyr drigrixs)
and T1 (the mornvint is the only one of its kind).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

Carry forward opalrast drigrixs, drigrixs that korrhob and the mornvint. Later chapters
state their results in these terms and do not restate the definitions.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 2.
  x023. Which drigrix leaves every drigrix unchanged under @?
Level 3.
  x016. List every drigrix in the opalrast.

# Chapter 6. The relation and what it orders (2)

## Why this chapter

The present chapter develops nakkeld pairs, vexfex collections and a grixvash.

Nothing here stands on its own. The arguments lean on chapters 1 and 3, and a reader who
has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about drigrixs covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D13. Nakkeld pairs. Two distinct drigrixs x and y form a nakkeld pair when x :: y and y
:: x both hold, that is, when each lies in the aztdri of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D3. Vexfex collections. A collection S of drigrixs is vexfex when x @ y belongs to S for
every pair x, y drawn from S.

D9. A grixvash. A drigrix f is a grixvash when f :: y holds for every drigrix y, that
is, when the aztdri of f is the whole system.

In this system that picks out qenvex, which is 1 of the 5 drigrixs.

## The shape of it

The right picture for vintmux is a spreading stain rather than a list. Drop one drigrix
in, apply the operation to whatever is wet, repeat. The stain here reaches 1, 2 and 4
drigrixs depending on where it started.

The relation is easiest to see as a height. Each drigrix casts a aztdri over what it
covers, and the sizes of those shadows here are 1 and 5. Sizes repeat, so the objects do
not line up in single file.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R13 rests on D4 (the aztdri of a drigrix). The dependence is on the content of those
results, not only on their vocabulary.

T9 rests on D4 (the aztdri of a drigrix) and A12 (transitivity of the relation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Evaluate (vashtez @ glimmux) @ (qenvex @ umbazt). Each line below is one lookup in a
table.
    vashtez @ glimmux = qenvex   (the table for @)
    qenvex @ umbazt = qenvex   (the table for @)
    qenvex @ qenvex = qenvex   (the table for @)
So (vashtez @ glimmux) @ (qenvex @ umbazt) is qenvex.

Bracketing is not cosmetic, so here is glimmux @ (qenvex @ vashtez) for contrast.
    qenvex @ vashtez = qenvex   (the table for @)
    glimmux @ qenvex = qenvex   (the table for @)
The value is qenvex. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test glimmux :: solvex. The aztdri of glimmux is solvex, and solvex lies inside it, so
the relation holds.

## A case that breaks

R13. It is not the case that: If x :: y then y :: x. It fails at x = umbazt, y = solvex.
One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of closure under the first operation and
transitivity of the relation. Those are properties of this system, not of systems in
general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A1 (closure under the first operation), A12
(transitivity of the relation) and D4 (the aztdri of a drigrix).

These results are used again in D8 (the vintmux of a drigrix), T3 (the kapon is vexfex),
T4 (the vintmux of a drigrix is vexfex) and T8 (the tezjen is vexfex).

## Proofs

R13. It is not the case that: If x :: y then y :: x.

  (1) [S2] Take the case x = umbazt, y = solvex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T9. If y lies in the aztdri of x, then the aztdri of y is contained in the aztdri of x.

  (1) [D4] Let y satisfy x :: y and let z satisfy y :: z.
  (2) [A12] Transitivity gives x :: z.
  (3) [D4] So every member of the aztdri of y is a member of that of x.

Checked over 125 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: nakkeld pairs, vexfex collections and a grixvash. Each
of these is used by name later, so the names are worth learning rather than looking up.

Established here and safe to use: T9.

Explicitly not available: R13. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x017. How many drigrixs lie in the smallest vexfex collection containing umbazt?
  x018. How many drigrixs lie in the smallest vexfex collection containing glimmux?
Level 4.
  x031. Write down the grixvash in full.
  x044. The result above concerns aztdris. List the aztdri of umbazt.
  x045. The result above concerns aztdris. List the aztdri of glimmux.
Level 5.
  x048. The following fails in this system: If x :: y then y :: x. Name the earliest drigrix, in the order the drigrixs were introduced, that witnesses the failure.

# Chapter 7. Neutral objects and reversal (2)

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is qennyr drigrixs,
the kapon and the tezjen.

Nothing here stands on its own. The arguments lean on chapters 2 and 5, and a reader who
has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over drigrixs, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D10. Qennyr drigrixs. A drigrix x is qennyr when x @ x equals the mornvint.

In this system that picks out solvex, which is 1 of the 5 drigrixs.

D6. The kapon. The kapon of the system is the collection of drigrixs that korrhob with
every drigrix.

In this system that picks out solvex, umbazt, glimmux, vashtez and qenvex, that is, all
of them.

D7. The tezjen. The tezjen is the collection of all opalrast drigrixs.

In this system that picks out solvex and qenvex, which is 2 of the 5 drigrixs.

## The shape of it

A useful mental split: some drigrixs are inert under the operation and some are not.
solvex and qenvex come back unchanged when combined with themselves, and solvex, umbazt,
glimmux, vashtez and qenvex commute with everything.

The neutral drigrix solvex is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R14 rests on D5 (the mornvint). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T1 rests on D5 (the mornvint) and A4 (a neutral object for the first operation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Take glimmux @ solvex + umbazt and work it out one step at a time.
    solvex + umbazt = solvex   (the table for +)
    glimmux @ solvex = glimmux   (the table for @)
So glimmux @ solvex + umbazt is glimmux.

Move the brackets and the work changes. Take solvex @ (umbazt @ glimmux).
    umbazt @ glimmux = vashtez   (the table for @)
    solvex @ vashtez = vashtez   (the table for @)
That gives vashtez, against glimmux above.

One decision about the relation, since deciding is as much a skill as computing. Does
qenvex :: qenvex hold? Read off what qenvex stands over: solvex, umbazt, glimmux,
vashtez and qenvex. qenvex is among them, so it holds.

## A case that breaks

R14. It is not the case that: e @ x equals the mornvint for every drigrix x. The case
that settles it: anchor = solvex, x = umbazt, value = umbazt. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of a neutral object for the first operation
and closure under the first operation. Those are properties of this system, not of
systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A4 (a neutral object for the first operation),
D1 (opalrast drigrixs), D2 (drigrixs that korrhob) and D5 (the mornvint).

These results are used again in T2 (the mornvint lies in the kapon), T3 (the kapon is
vexfex), T7 (the vintmux of a kapon drigrix stays in the kapon) and T8 (the tezjen is
vexfex).

## Proofs

R14. It is not the case that: e @ x equals the mornvint for every drigrix x.

  (1) [S2] Take the case anchor = solvex, x = umbazt, value = umbazt, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T1. There is exactly one drigrix e with e @ x = x @ e = x for every drigrix x.

  (1) [D5] Suppose e and f both leave every drigrix unchanged.
  (2) [A4] Then e @ f = f, reading e as neutral on the left.
  (3) [A4] And e @ f = e, reading f as neutral on the right.
  (4) So e = f, and the two suppositions describe the same object.

Checked over 25 cases: every object paired with every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: qennyr drigrixs, the kapon and the tezjen. Each of
these is used by name later, so the names are worth learning rather than looking up.

The results now available are T1, each settled by exhaustive check rather than by
argument from analogy.

Explicitly not available: R14. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x024. List every drigrix in the tezjen.
  x032. Which drigrixs make up the qennyr? Name them all.
Level 5.
  x049. The following fails in this system: e @ x equals the mornvint for every drigrix x. Name the earliest drigrix, in the order the drigrixs were introduced, that witnesses the failure.

# Chapter 8. The relation and what it orders (3)

## Why this chapter

The results collected here were not found in this order. The vintmux of a drigrix, there
is at most one grixvash and no nakkeld pairs exist came first, and the rest was
assembled around that once the pattern was visible.

Prerequisites are real here: chapters 3 and 6 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over drigrixs, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D8. The vintmux of a drigrix. The vintmux of a drigrix x, written [x], is the smallest
vexfex collection that contains x.

Worked out for each drigrix: solvex to solvex; umbazt to umbazt, glimmux, vashtez and
qenvex; glimmux to glimmux and qenvex; vashtez to vashtez and qenvex; qenvex to qenvex.

## The shape of it

Picture the vintmux as what happens when you start with one drigrix and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 5 drigrixs, that stops. In this system the sizes it stops at are 1, 2 and 4.

Think of :: as pointing downhill. The aztdri of a drigrix is everything downhill of it,
and those shadows here have sizes 1 and 5.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T10 rests on D9 (a grixvash) and A11 (antisymmetry of the relation). Remove any one of
them and the statement stops making sense, not merely stops being provable.

T11 rests on D13 (nakkeld pairs) and A11 (antisymmetry of the relation). The dependence
is on the content of those results, not only on their vocabulary.

## A worked case

Evaluate (vashtez @ glimmux) @ (qenvex @ solvex). Each line below is one lookup in a
table.
    vashtez @ glimmux = qenvex   (the table for @)
    qenvex @ solvex = qenvex   (the table for @)
    qenvex @ qenvex = qenvex   (the table for @)
So (vashtez @ glimmux) @ (qenvex @ solvex) is qenvex.

Move the brackets and the work changes. Take glimmux @ (qenvex @ vashtez).
    qenvex @ vashtez = qenvex   (the table for @)
    glimmux @ qenvex = qenvex   (the table for @)
The value is qenvex. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
qenvex :: vashtez hold? Read off what qenvex stands over: solvex, umbazt, glimmux,
vashtez and qenvex. vashtez is among them, so it holds.

A second case, this time a vintmux. Start from umbazt. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is umbazt, glimmux,
vashtez and qenvex, so the mornzam of umbazt is 4.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of drigrixs that come back
unchanged from themselves: solvex and qenvex. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by antisymmetry of the relation and closure under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A11 (antisymmetry of the relation), D13 (nakkeld pairs), D3 (vexfex
collections) and D9 (a grixvash).

These results are used again in D11 (the mornzam of a drigrix), T4 (the vintmux of a
drigrix is vexfex), T5 (the vintmux is contained in every vexfex collection) and T7 (the
vintmux of a kapon drigrix stays in the kapon).

## Proofs

T10. No two distinct drigrixs can both be grixvashs.

  (1) [D9] Let f and h both be floors.
  (2) [D9] Then f :: h, since h is any object, and h :: f likewise.
  (3) [A11] Antisymmetry forces f = h.

Checked over 25 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T11. No two distinct drigrixs lie in each other's aztdri.

  (1) [D13] Suppose x and y form a tight pair.
  (2) [A11] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the vintmux of a drigrix. Later chapters state their results in these
terms and do not restate the definitions.

The results now available are T10 and T11, each settled by exhaustive check rather than
by argument from analogy.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x025. Name every drigrix in [umbazt].
  x026. Name every drigrix in [glimmux].
  x027. List the vintmux of vashtez.
Level 4.
  x028. Let z be glimmux @ umbazt. List the vintmux of z.
  x029. Let z be solvex @ umbazt. List the vintmux of z.
  x030. Let z be solvex @ vashtez. List the vintmux of z.
  x046. Name the drigrixs that make up the grixvash, which is what the result above is a claim about.

# Chapter 9. Combining objects (2)

## Why this chapter

Anyone using this system to keep track of something will meet where every drigrix is
opalrast breaks down, every drigrix lies in the kapon and the mornvint lies in the kapon
early, whether or not they go looking.

Prerequisites are real here: chapters 1, 5, 6 and 7 supply the notions the statements
below are phrased in.

One habit to adopt: when a statement below quantifies over drigrixs, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

Two questions sort the drigrixs quickly. Does combining a drigrix with itself change it?
For solvex and qenvex it does not. Does it matter which side it goes on? For solvex,
umbazt, glimmux, vashtez and qenvex it does not.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 drigrixs the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R11 rests on D7 (the tezjen). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T12 rests on D6 (the kapon). The dependence is on the content of those results, not only
on their vocabulary.

T2 rests on D5 (the mornvint) and D6 (the kapon). Remove any one of them and the
statement stops making sense, not merely stops being provable.

T3 rests on D6 (the kapon), D3 (vexfex collections) and A2 (association of the first
operation). Remove any one of them and the statement stops making sense, not merely
stops being provable.

T8 rests on D7 (the tezjen) and D3 (vexfex collections). The dependence is on the
content of those results, not only on their vocabulary.

## A worked case

Here is umbazt @ qenvex + solvex, reduced without skipping anything.
    qenvex + solvex = solvex   (the table for +)
    umbazt @ solvex = umbazt   (the table for @)
So umbazt @ qenvex + solvex is umbazt.

Bracketing is not cosmetic, so here is qenvex @ (solvex @ umbazt) for contrast.
    solvex @ umbazt = umbazt   (the table for @)
    qenvex @ umbazt = qenvex   (the table for @)
The value is qenvex, not umbazt.

Test glimmux :: vashtez. The aztdri of glimmux is solvex, and vashtez lies outside it,
so the relation fails.

## A case that breaks

R11. It is not the case that: x @ x = x for every drigrix x. The case that settles it: x
= umbazt, value = glimmux. Anyone carrying this claim over from a more familiar system
will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by a neutral object for the first operation, association of the
first operation and closure under the first operation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A2 (association of the first operation), D3
(vexfex collections), D5 (the mornvint) and D6 (the kapon).

These results are used again in T7 (the vintmux of a kapon drigrix stays in the kapon)
and T13 (the second operation keeps the kapon intact).

## Proofs

R11. It is not the case that: x @ x = x for every drigrix x.

  (1) [S2] Take the case x = umbazt, value = glimmux, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T12. Every pair of drigrixs korrhobs.

  (1) [D6] The kapon is defined by korrhobing with everything.
  (2) [D2] The claim is that x @ y = y @ x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T2. The mornvint korrhobs with every drigrix.

  (1) [D5] Let e be the mornvint and x any drigrix.
  (2) [D5] Then e @ x = x and x @ e = x.
  (3) [D2] So e @ x = x @ e, which is what it means to korrhob.
  (4) [D6] Since x was arbitrary, e belongs to the kapon.

Checked over 5 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. If x and y both korrhob with every drigrix, then so does x @ y.

  (1) [D6] Let x and y lie in the kapon and let z be any drigrix.
  (2) [A2] Then (x @ y) @ z = x @ (y @ z).
  (3) [D6] Move z past y, then past x, using that each korrhobs with everything.
  (4) [D3] So x @ y korrhobs with z, and the kapon is vexfex.

Checked over 25 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

T8. If x and y are both opalrast then so is x @ y.

  (1) [D7] Let x and y be opalrast.
  (2) [D1] The claim asks whether (x @ y) @ (x @ y) returns x @ y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 25 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Established here and safe to use: T12, T2, T3 and T8.

Explicitly not available: R11. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x043. Name the drigrixs that make up the tezjen, which is what the result above is a claim about.
Level 5.
  x047. The following fails in this system: x @ x = x for every drigrix x. Name the earliest drigrix, in the order the drigrixs were introduced, that witnesses the failure.

# Chapter 10. Collections that close on themselves

## Why this chapter

So far the drigrixs have been objects to be pushed around. This chapter starts asking
what they are like. We take up the mornzam of a drigrix, the vintmux of a drigrix is
vexfex and the vintmux of a kapon drigrix stays in the kapon.

Nothing here stands on its own. The arguments lean on chapters 6, 7, 8 and 9, and a
reader who has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
drigrixs that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D11. The mornzam of a drigrix. The mornzam of a drigrix x is the number of drigrixs in
its vintmux [x].

Worked out for each drigrix: solvex to 1; umbazt to 4; glimmux to 2; vashtez to 2;
qenvex to 1.

## The shape of it

Picture the vintmux as what happens when you start with one drigrix and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 5 drigrixs, that stops. In this system the sizes it stops at are 1, 2 and 4.

A useful mental split: some drigrixs are inert under the operation and some are not.
solvex and qenvex come back unchanged when combined with themselves, and solvex, umbazt,
glimmux, vashtez and qenvex commute with everything.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T4 rests on D8 (the vintmux of a drigrix) and D3 (vexfex collections). Remove any one of
them and the statement stops making sense, not merely stops being provable.

T7 rests on D8 (the vintmux of a drigrix), D6 (the kapon) and T3 (the kapon is vexfex).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

## A worked case

Here is (glimmux @ umbazt) @ (qenvex @ vashtez), reduced without skipping anything.
    glimmux @ umbazt = vashtez   (the table for @)
    qenvex @ vashtez = qenvex   (the table for @)
    vashtez @ qenvex = qenvex   (the table for @)
So (glimmux @ umbazt) @ (qenvex @ vashtez) is qenvex.

Move the brackets and the work changes. Take umbazt @ (qenvex @ glimmux).
    qenvex @ glimmux = qenvex   (the table for @)
    umbazt @ qenvex = qenvex   (the table for @)
The value is qenvex. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
qenvex :: vashtez hold? Read off what qenvex stands over: solvex, umbazt, glimmux,
vashtez and qenvex. vashtez is among them, so it holds.

Now compute [umbazt]. Fold umbazt against itself, then fold whatever appeared against
everything present, and stop when a round adds nothing. The result is umbazt, glimmux,
vashtez and qenvex, of size 4.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of drigrixs that come back
unchanged from themselves: solvex and qenvex. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by association of the first operation and closure under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside D3 (vexfex collections), D6 (the kapon), D8 (the vintmux of a drigrix)
and T3 (the kapon is vexfex).

What is built on it later: D12 (the rastdri), T5 (the vintmux is contained in every
vexfex collection), T6 (a drigrix is opalrast exactly when its mornzam is one) and R10
(where the mornzam divides the number of drigrixs breaks down).

## Proofs

T4. For every drigrix x, the collection [x] is vexfex.

  (1) [D8] [x] is built by taking x and closing under @.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 125 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

T7. If x lies in the kapon then every drigrix of [x] lies in the kapon.

  (1) [T3] The kapon is vexfex.
  (2) [D8] [x] is the smallest vexfex collection containing x.
  (3) A smallest such collection sits inside any other, and the kapon is one.

Checked over 25 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the mornzam of a drigrix. Later chapters state their results in these
terms and do not restate the definitions.

The results now available are T4 and T7, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x033. How many drigrixs lie in [umbazt]?
  x034. What is the mornzam of glimmux?
  x035. What is the mornzam of vashtez?
  x036. How many drigrixs lie in [qenvex]?
Level 5.
  x037. Let z be umbazt @ glimmux + vashtez. What is the mornzam of z?
  x038. Let z be vashtez @ qenvex + solvex. What is the mornzam of z?
  x039. Let z be (umbazt @ vashtez) @ qenvex. What is the mornzam of z?

# Chapter 11. Collections that close on themselves (2)

## Why this chapter

We turn to the rastdri, where the mornzam divides the number of drigrixs breaks down and
where some drigrix reaches every other breaks down. The treatment is self contained
given the material already established.

Prerequisites are real here: chapters 5, 8 and 10 supply the notions the statements
below are phrased in.

One habit to adopt: when a statement below quantifies over drigrixs, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D12. The rastdri. The rastdri of the system is the collection of drigrixs whose mornzam
is largest.

In this system that picks out umbazt, which is 1 of the 5 drigrixs.

## The shape of it

Picture the vintmux as what happens when you start with one drigrix and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 5 drigrixs, that stops. In this system the sizes it stops at are 1, 2 and 4.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R10 rests on D11 (the mornzam of a drigrix) and T4 (the vintmux of a drigrix is vexfex).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

R12 rests on D8 (the vintmux of a drigrix) and D11 (the mornzam of a drigrix). The
dependence is on the content of those results, not only on their vocabulary.

T5 rests on D8 (the vintmux of a drigrix) and T4 (the vintmux of a drigrix is vexfex).
The dependence is on the content of those results, not only on their vocabulary.

T6 rests on D1 (opalrast drigrixs), D11 (the mornzam of a drigrix) and T4 (the vintmux
of a drigrix is vexfex). The dependence is on the content of those results, not only on
their vocabulary.

## A worked case

Here is umbazt @ vashtez + qenvex, reduced without skipping anything.
    vashtez + qenvex = vashtez   (the table for +)
    umbazt @ vashtez = qenvex   (the table for @)
That leaves qenvex, and no other reading of the notation gives anything else.

A companion case, vashtez @ (qenvex @ umbazt), to show what the brackets are doing.
    qenvex @ umbazt = qenvex   (the table for @)
    vashtez @ qenvex = qenvex   (the table for @)
The value is qenvex. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test vashtez :: glimmux. The aztdri of vashtez is solvex, and glimmux lies outside it,
so the relation fails.

## A case that breaks

R10. It is not the case that: For every drigrix x, the mornzam of x divides 5. The case
that settles it: x = umbazt, reach = 4, size = 5. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

R12. It is not the case that: There is a drigrix whose vintmux is the whole system. The
case that settles it: largest_span = 4, size = 5. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: D1 (opalrast drigrixs), D11 (the mornzam of a
drigrix), D8 (the vintmux of a drigrix) and T4 (the vintmux of a drigrix is vexfex).

## Proofs

R10. It is not the case that: For every drigrix x, the mornzam of x divides 5.

  (1) [S2] Take the case x = umbazt, reach = 4, size = 5, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

R12. It is not the case that: There is a drigrix whose vintmux is the whole system.

  (1) [S2] Take the case largest_span = 4, size = 5, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T5. If S is vexfex and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 55 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T6. x @ x = x holds if and only if [x] contains x alone.

  (1) [D1] If x @ x = x then {x} is already closed under @.
  (2) [T4] So [x] = {x} and the mornzam is one.
  (3) [D11] Conversely a span of one object must contain x @ x, which is then x.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the rastdri. Later chapters state their results in these terms and do not
restate the definitions.

The results now available are T5 and T6, each settled by exhaustive check rather than by
argument from analogy.

Do not carry forward R10 and R12. These were tested and failed, and the failing cases
are recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x040. Write down the rastdri in full.
  x041. What is the largest mornzam any drigrix has?
Level 5.
  x042. The following fails in this system: For every drigrix x, the mornzam of x divides 5. Name the earliest drigrix, in the order the drigrixs were introduced, that witnesses the failure.

# Chapter 12. The second operation and how the two interact (2)

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is the second
operation keeps the kapon intact.

Prerequisites are real here: chapters 4, 7 and 9 supply the notions the statements below
are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
drigrixs that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

The interesting content of a two operation system sits in the gap between them: which
one distributes over which, and which drigrixs are fixed by both.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 drigrixs the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T13 rests on D6 (the kapon), A6 (closure under the second operation) and T3 (the kapon
is vexfex). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Here is (qenvex @ solvex) @ (vashtez @ umbazt), reduced without skipping anything.
    qenvex @ solvex = qenvex   (the table for @)
    vashtez @ umbazt = qenvex   (the table for @)
    qenvex @ qenvex = qenvex   (the table for @)
The expression comes to qenvex.

A companion case, solvex @ (vashtez @ qenvex), to show what the brackets are doing.
    vashtez @ qenvex = qenvex   (the table for @)
    solvex @ qenvex = qenvex   (the table for @)
That gives qenvex, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
glimmux :: qenvex hold? Read off what glimmux stands over: solvex. qenvex is not among
them, so it fails.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of drigrixs that come back
unchanged from themselves: solvex and qenvex. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of association of the first operation,
closure under the first operation and closure under the second operation. Those are
properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A6 (closure under the second operation), D6 (the kapon) and T3 (the kapon
is vexfex).

## Proofs

T13. If x and y lie in the kapon then so does x + y.

  (1) [T3] The kapon is already vexfex under @.
  (2) [A6] The second operation is defined on every pair.
  (3) [D6] The claim is that + respects the kapon as well.

Checked over 25 cases: every ordered pair from the core. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

The results now available are T13, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

This chapter carries no exercises. Nothing in it can be asked about in a way that could
not be answered without reading it, and an exercise like that is worse than none.
