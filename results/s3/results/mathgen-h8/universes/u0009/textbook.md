# The Mornyuk system

The Mornyuk system is small enough to hold in the hand and strange enough to be worth
the trouble. It has 4 reldjens, two operations, and one relation, and nothing else.

The reldjens are written nakopal, kagel, korrreld and iskbra. The first operation is
written <>. The second is written # and binds more tightly, so x <> y # z means x <> (y
# z). The relation is written ::; where it holds between two reldjens we say the left
one yields to the right one. Both operations associate to the left when written without
brackets, and brackets override that. Repeated combination is abbreviated: x^3 means x
<> x <> x.

A warning that will be repeated because it is the one readers ignore: nothing here is
inherited from arithmetic. Familiar names have been avoided on purpose. Where a law of
arithmetic happens to hold it is stated and checked, and where it fails a counterexample
is given.

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

# Chapter 2. Neutral objects and reversal

## Why this chapter

So far the reldjens have been objects to be pushed around. This chapter starts asking
what they are like. We take up a neutral object for the first operation, an absorbing
object for the first operation and the system does not have reversal under the first
operation.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

The standard of proof here is exhaustion. A universal claim about reldjens covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A4. A neutral object for the first operation. There is a reldjen kagel with kagel <> x =
x <> kagel = x for every x.

A5. An absorbing object for the first operation. There is a reldjen nakopal with nakopal
<> x = x <> nakopal = nakopal for every x.

## The shape of it

The neutral reldjen kagel is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 reldjens the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R1 rests on S2 (the Mornyuk combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take (nakopal <> kagel) <> (korrreld <> iskbra) and work it out one step at a time.
    nakopal <> kagel = nakopal   (the table for <>)
    korrreld <> iskbra = korrreld   (the table for <>)
    nakopal <> korrreld = nakopal   (the table for <>)
That leaves nakopal, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is kagel <> (korrreld <> nakopal) for contrast.
    korrreld <> nakopal = nakopal   (the table for <>)
    kagel <> nakopal = nakopal   (the table for <>)
That gives nakopal, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test korrreld :: iskbra. The drivor of korrreld is korrreld and iskbra, and iskbra lies
inside it, so the relation holds.

## A case that breaks

R1. Some reldjen x admits no reldjen y for which x <> y and y <> x both land on a
neutral object. The case that settles it: x = nakopal. Anyone carrying this claim over
from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside S2 (the Mornyuk combination tables).

These results are used again in D5 (the lornumb) and T1 (the lornumb is the only one of
its kind).

## Proofs

R1. Some reldjen x admits no reldjen y for which x <> y and y <> x both land on a neutral object.

  (1) [S2] Take the case x = nakopal, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R1. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 5.
  x008. The following fails in this system: Some reldjen x admits no reldjen y for which x <> y and y <> x both land on a neutral object. Name the earliest reldjen, in the order the reldjens were introduced, that witnesses the failure.

# Chapter 3. The relation and what it orders

## Why this chapter

The present chapter develops reflexivity of the relation, antisymmetry of the relation
and transitivity of the relation.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
reldjens that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A10. Reflexivity of the relation. For every reldjen x: x :: x.

A11. Antisymmetry of the relation. For all reldjens x and y: if x :: y and y :: x then x
= y.

A12. Transitivity of the relation. For all reldjens x, y, z: if x :: y and y :: z then x
:: z.

A13. Comparability of every pair. For all reldjens x and y, at least one of x :: y and y
:: x holds.

D4. The drivor of a reldjen. The drivor of a reldjen x is the collection of reldjens y
for which x :: y holds.

Worked out for each reldjen: nakopal to nakopal, kagel, korrreld and iskbra; kagel to
kagel, korrreld and iskbra; korrreld to korrreld and iskbra; iskbra to iskbra.

## The shape of it

The relation is easiest to see as a height. Each reldjen casts a drivor over what it
yields to, and the sizes of those shadows here are 1, 2, 3 and 4. No two are the same
size, so the objects line up in a single file.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R7 rests on S2 (the Mornyuk combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R8 rests on S2 (the Mornyuk combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take korrreld <> nakopal # iskbra and work it out one step at a time.
    nakopal # iskbra = iskbra   (the table for #)
    korrreld <> iskbra = korrreld   (the table for <>)
So korrreld <> nakopal # iskbra is korrreld.

Move the brackets and the work changes. Take nakopal <> (iskbra <> korrreld).
    iskbra <> korrreld = korrreld   (the table for <>)
    nakopal <> korrreld = nakopal   (the table for <>)
That gives nakopal, against korrreld above.

Test korrreld :: korrreld. The drivor of korrreld is korrreld and iskbra, and korrreld
lies inside it, so the relation holds.

## A case that breaks

R7. It is not the case that: For all reldjens x, y, z: if x :: y then (z <> x) :: (z <>
y) and (x <> z) :: (y <> z). The case that settles it: x = kagel, y = korrreld, z =
korrreld, side = left. Anyone carrying this claim over from a more familiar system will
be wrong here, and wrong in a way that propagates.

R8. It is not the case that: For all reldjens x, y, z: if x :: y then (z # x) :: (z # y)
and (x # z) :: (y # z). The case that settles it: x = nakopal, y = kagel, z = iskbra,
side = left. Anyone carrying this claim over from a more familiar system will be wrong
here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: S2 (the Mornyuk combination tables).

What is built on it later: D9 (a thrapyr), D13 (korrjen pairs), T10 (drivors are nested
along the relation) and T11 (there is at most one thrapyr).

## Proofs

R7. It is not the case that: For all reldjens x, y, z: if x :: y then (z <> x) :: (z <> y) and (x <> z) :: (y <> z).

  (1) [S2] Take the case x = kagel, y = korrreld, z = korrreld, side = left, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R8. It is not the case that: For all reldjens x, y, z: if x :: y then (z # x) :: (z # y) and (x # z) :: (y # z).

  (1) [S2] Take the case x = nakopal, y = kagel, z = iskbra, side = left, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the drivor of a reldjen. Each of these is used by name
later, so the names are worth learning rather than looking up.

Do not carry forward R7 and R8. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 5.
  x012. The following fails in this system: For all reldjens x, y, z: if x :: y then (z <> x) :: (z <> y) and (x <> z) :: (y <> z). Name the earliest reldjen, in the order the reldjens were introduced, that witnesses the failure.

# Chapter 4. The second operation and how the two interact

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is closure under the
second operation, association of the second operation and commutation of the second
operation.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

One habit to adopt: when a statement below quantifies over reldjens, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A6. Closure under the second operation. For all reldjens x and y, x # y is again a
reldjen.

A7. Association of the second operation. For all reldjens x, y, z: (x # y) # z = x # (y
# z).

A8. Commutation of the second operation. For all reldjens x and y: x # y = y # x.

A9. A neutral object for the second operation. There is a reldjen nakopal with nakopal #
x = x for every x.

## The shape of it

The interesting content of a two operation system sits in the gap between them: which
one distributes over which, and which reldjens are fixed by both.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 reldjens the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R4 rests on S2 (the Mornyuk combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R5 rests on S2 (the Mornyuk combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R6 rests on S2 (the Mornyuk combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Here is (nakopal <> korrreld) <> (iskbra <> kagel), reduced without skipping anything.
    nakopal <> korrreld = nakopal   (the table for <>)
    iskbra <> kagel = iskbra   (the table for <>)
    nakopal <> iskbra = nakopal   (the table for <>)
That leaves nakopal, and no other reading of the notation gives anything else.

A companion case, korrreld <> (iskbra <> nakopal), to show what the brackets are doing.
    iskbra <> nakopal = nakopal   (the table for <>)
    korrreld <> nakopal = nakopal   (the table for <>)
That gives nakopal, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
nakopal :: nakopal hold? Read off what nakopal stands over: nakopal, kagel, korrreld and
iskbra. nakopal is among them, so it holds.

## A case that breaks

R4. It is not the case that: For every reldjen x: x # x = x. It fails at x = kagel,
value = korrreld. One case is enough, and this is the earliest one.

R5. It is not the case that: For all reldjens x, y, z: x # (y <> z) = (x # y) <> (x #
z), and the same on the right. The case that settles it: x = kagel, y = nakopal, z =
kagel, left = kagel, right = korrreld. Anyone carrying this claim over from a more
familiar system will be wrong here, and wrong in a way that propagates.

R6. It is not the case that: For all reldjens x and y: x <> (x # y) = x and x # (x <> y)
= x. It fails at x = kagel, y = kagel, value = korrreld. One case is enough, and this is
the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: S2 (the Mornyuk combination tables).

These results are used again in T15 (the second operation keeps the vashreld intact).

## Proofs

R4. It is not the case that: For every reldjen x: x # x = x.

  (1) [S2] Take the case x = kagel, value = korrreld, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R5. It is not the case that: For all reldjens x, y, z: x # (y <> z) = (x # y) <> (x # z), and the same on the right.

  (1) [S2] Take the case x = kagel, y = nakopal, z = kagel, left = kagel, right = korrreld, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R6. It is not the case that: For all reldjens x and y: x <> (x # y) = x and x # (x <> y) = x.

  (1) [S2] Take the case x = kagel, y = kagel, value = korrreld, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R4, R5 and R6. These were tested and failed, and the failing cases
are recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 5.
  x011. The following fails in this system: For every reldjen x: x # x = x. Name the earliest reldjen, in the order the reldjens were introduced, that witnesses the failure.

# Chapter 5. Combining objects

## Why this chapter

What follows was pieced together backwards. The last item of it, duthnyr reldjens,
reldjens that korrfex and the lornumb, was noticed before anyone had a reason to expect
it.

Nothing here stands on its own. The arguments lean on chapters 1 and 2, and a reader who
has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over reldjens, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D1. Duthnyr reldjens. A reldjen x is called duthnyr when x <> x = x.

Running the definition over every reldjen leaves nakopal and kagel.

D2. Reldjens that korrfex. Two reldjens x and y are said to korrfex when x <> y = y <>
x.

D5. The lornumb. The reldjen kagel is called the lornumb of the system. It is the unique
reldjen that leaves every reldjen unchanged under <>.

Here that is kagel.

## The shape of it

Two questions sort the reldjens quickly. Does combining a reldjen with itself change it?
For nakopal and kagel it does not. Does it matter which side it goes on? For nakopal,
kagel, korrreld and iskbra it does not.

Neutrality is a strong condition disguised as a weak one. It fixes a single reldjen and,
through that, constrains everything that can combine with it.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

This chapter is groundwork. The derivations that use it start in the next one.

## A worked case

Here is nakopal <> kagel # iskbra, reduced without skipping anything.
    kagel # iskbra = nakopal   (the table for #)
    nakopal <> nakopal = nakopal   (the table for <>)
So nakopal <> kagel # iskbra is nakopal.

Move the brackets and the work changes. Take kagel <> (iskbra <> nakopal).
    iskbra <> nakopal = nakopal   (the table for <>)
    kagel <> nakopal = nakopal   (the table for <>)
That gives nakopal, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
nakopal :: nakopal hold? Read off what nakopal stands over: nakopal, kagel, korrreld and
iskbra. nakopal is among them, so it holds.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of reldjens that come back
unchanged from themselves: nakopal and kagel. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation
and closure under the first operation. Those are properties of this system, not of
systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A1 (closure under the first operation) and A4 (a
neutral object for the first operation).

These results are used again in D6 (the vashreld), D7 (the umbka), D10 (driumb reldjens)
and T1 (the lornumb is the only one of its kind).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

Carry forward duthnyr reldjens, reldjens that korrfex and the lornumb. Later chapters
state their results in these terms and do not restate the definitions.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 2.
  x015. Name the lornumb of the system.
Level 3.
  x013. Which reldjens make up the duthnyr? Name them all.

# Chapter 6. The relation and what it orders (2)

## Why this chapter

The practical content of this chapter is korrjen pairs, zammorn collections and a
thrapyr. It is the part that shows up in use.

Prerequisites are real here: chapters 1 and 3 supply the notions the statements below
are phrased in.

The standard of proof here is exhaustion. A universal claim about reldjens covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D13. Korrjen pairs. Two distinct reldjens x and y form a korrjen pair when x :: y and y
:: x both hold, that is, when each lies in the drivor of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D3. Zammorn collections. A collection S of reldjens is zammorn when x <> y belongs to S
for every pair x, y drawn from S.

D9. A thrapyr. A reldjen f is a thrapyr when f :: y holds for every reldjen y, that is,
when the drivor of f is the whole system.

Running the definition over every reldjen leaves nakopal.

## The shape of it

Picture the nakgrix as what happens when you start with one reldjen and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 4 reldjens, that stops. In this system the sizes it stops at are 1 and 2.

The relation is easiest to see as a height. Each reldjen casts a drivor over what it
yields to, and the sizes of those shadows here are 1, 2, 3 and 4. No two are the same
size, so the objects line up in a single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 reldjens the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R11 rests on D4 (the drivor of a reldjen). The dependence is on the content of those
results, not only on their vocabulary.

T10 rests on D4 (the drivor of a reldjen) and A12 (transitivity of the relation). The
dependence is on the content of those results, not only on their vocabulary.

## A worked case

Here is (nakopal <> iskbra) <> (korrreld <> kagel), reduced without skipping anything.
    nakopal <> iskbra = nakopal   (the table for <>)
    korrreld <> kagel = korrreld   (the table for <>)
    nakopal <> korrreld = nakopal   (the table for <>)
So (nakopal <> iskbra) <> (korrreld <> kagel) is nakopal.

Bracketing is not cosmetic, so here is iskbra <> (korrreld <> nakopal) for contrast.
    korrreld <> nakopal = nakopal   (the table for <>)
    iskbra <> nakopal = nakopal   (the table for <>)
That gives nakopal, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
iskbra :: kagel hold? Read off what iskbra stands over: iskbra. kagel is not among them,
so it fails.

## A case that breaks

R11. It is not the case that: If x :: y then y :: x. It fails at x = nakopal, y = kagel.
One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by closure under the first operation and transitivity of the
relation. A system without them is not a system where these results are harder to prove;
it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A1 (closure under the first operation), A12 (transitivity of the
relation) and D4 (the drivor of a reldjen).

What is built on it later: D8 (the nakgrix of a reldjen), T3 (the vashreld is zammorn),
T4 (the nakgrix of a reldjen is zammorn) and T9 (the umbka is zammorn).

## Proofs

R11. It is not the case that: If x :: y then y :: x.

  (1) [S2] Take the case x = nakopal, y = kagel, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 16 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T10. If y lies in the drivor of x, then the drivor of y is contained in the drivor of x.

  (1) [D4] Let y satisfy x :: y and let z satisfy y :: z.
  (2) [A12] Transitivity gives x :: z.
  (3) [D4] So every member of the drivor of y is a member of that of x.

Checked over 64 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: korrjen pairs, zammorn collections and a thrapyr. Each
of these is used by name later, so the names are worth learning rather than looking up.

The results now available are T10, each settled by exhaustive check rather than by
argument from analogy.

Explicitly not available: R11. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x014. How many reldjens lie in the smallest zammorn collection containing kagel?

# Chapter 7. Neutral objects and reversal (2)

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through driumb reldjens, the vashreld
and the umbka.

Prerequisites are real here: chapters 2 and 5 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over reldjens, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D10. Driumb reldjens. A reldjen x is driumb when x <> x equals the lornumb.

Running the definition over every reldjen leaves kagel and iskbra.

D6. The vashreld. The vashreld of the system is the collection of reldjens that korrfex
with every reldjen.

In this system that picks out nakopal, kagel, korrreld and iskbra, that is, all of them.

D7. The umbka. The umbka is the collection of all duthnyr reldjens.

Running the definition over every reldjen leaves nakopal and kagel.

## The shape of it

Two questions sort the reldjens quickly. Does combining a reldjen with itself change it?
For nakopal and kagel it does not. Does it matter which side it goes on? For nakopal,
kagel, korrreld and iskbra it does not.

The neutral reldjen kagel is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 reldjens the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R12 rests on D5 (the lornumb). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T1 rests on D5 (the lornumb) and A4 (a neutral object for the first operation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Take korrreld <> nakopal # iskbra and work it out one step at a time.
    nakopal # iskbra = iskbra   (the table for #)
    korrreld <> iskbra = korrreld   (the table for <>)
So korrreld <> nakopal # iskbra is korrreld.

Move the brackets and the work changes. Take nakopal <> (iskbra <> korrreld).
    iskbra <> korrreld = korrreld   (the table for <>)
    nakopal <> korrreld = nakopal   (the table for <>)
The value is nakopal, not korrreld.

Test korrreld :: korrreld. The drivor of korrreld is korrreld and iskbra, and korrreld
lies inside it, so the relation holds.

## A case that breaks

R12. It is not the case that: e <> x equals the lornumb for every reldjen x. The case
that settles it: anchor = kagel, x = nakopal, value = nakopal. Anyone carrying this
claim over from a more familiar system will be wrong here, and wrong in a way that
propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation
and closure under the first operation. Those are properties of this system, not of
systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A4 (a neutral object for the first operation),
D1 (duthnyr reldjens), D2 (reldjens that korrfex) and D5 (the lornumb).

What is built on it later: T2 (the lornumb lies in the vashreld), T3 (the vashreld is
zammorn), T8 (the nakgrix of a vashreld reldjen stays in the vashreld) and T9 (the umbka
is zammorn).

## Proofs

R12. It is not the case that: e <> x equals the lornumb for every reldjen x.

  (1) [S2] Take the case anchor = kagel, x = nakopal, value = nakopal, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 4 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T1. There is exactly one reldjen e with e <> x = x <> e = x for every reldjen x.

  (1) [D5] Suppose e and f both leave every reldjen unchanged.
  (2) [A4] Then e <> f = f, reading e as neutral on the left.
  (3) [A4] And e <> f = e, reading f as neutral on the right.
  (4) So e = f, and the two suppositions describe the same object.

Checked over 16 cases: every object paired with every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward driumb reldjens, the vashreld and the umbka. Later chapters state their
results in these terms and do not restate the definitions.

The results now available are T1, each settled by exhaustive check rather than by
argument from analogy.

Do not carry forward R12. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x016. Write down the umbka in full.
  x021. Write down the driumb in full.
Level 5.
  x034. The following fails in this system: e <> x equals the lornumb for every reldjen x. Name the earliest reldjen, in the order the reldjens were introduced, that witnesses the failure.

# Chapter 8. The relation and what it orders (3)

## Why this chapter

We turn to the nakgrix of a reldjen, there is at most one thrapyr and the system has a
thrapyr. The treatment is self contained given the material already established.

Prerequisites are real here: chapters 3 and 6 supply the notions the statements below
are phrased in.

The standard of proof here is exhaustion. A universal claim about reldjens covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

## What is defined here

D8. The nakgrix of a reldjen. The nakgrix of a reldjen x, written [x], is the smallest
zammorn collection that contains x.

Worked out for each reldjen: nakopal to nakopal; kagel to kagel; korrreld to nakopal and
korrreld; iskbra to kagel and iskbra.

## The shape of it

The right picture for nakgrix is a spreading stain rather than a list. Drop one reldjen
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
reldjens depending on where it started.

Think of :: as pointing downhill. The drivor of a reldjen is everything downhill of it,
and those shadows here have sizes 1, 2, 3 and 4.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 reldjens the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T11 rests on D9 (a thrapyr) and A11 (antisymmetry of the relation). The dependence is on
the content of those results, not only on their vocabulary.

T12 rests on D9 (a thrapyr) and A13 (comparability of every pair). The dependence is on
the content of those results, not only on their vocabulary.

T13 rests on D13 (korrjen pairs) and A11 (antisymmetry of the relation). The dependence
is on the content of those results, not only on their vocabulary.

## A worked case

Take (korrreld <> iskbra) <> (nakopal <> kagel) and work it out one step at a time.
    korrreld <> iskbra = korrreld   (the table for <>)
    nakopal <> kagel = nakopal   (the table for <>)
    korrreld <> nakopal = nakopal   (the table for <>)
That leaves nakopal, and no other reading of the notation gives anything else.

A companion case, iskbra <> (nakopal <> korrreld), to show what the brackets are doing.
    nakopal <> korrreld = nakopal   (the table for <>)
    iskbra <> nakopal = nakopal   (the table for <>)
That gives nakopal, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test iskbra :: nakopal. The drivor of iskbra is iskbra, and nakopal lies outside it, so
the relation fails.

Now compute [nakopal]. Fold nakopal against itself, then fold whatever appeared against
everything present, and stop when a round adds nothing. The result is nakopal, of size
1.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of reldjens that come back
unchanged from themselves: nakopal and kagel. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of antisymmetry of the relation, closure
under the first operation and comparability of every pair. Those are properties of this
system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A11 (antisymmetry of the relation), A13
(comparability of every pair), D13 (korrjen pairs) and D3 (zammorn collections).

What is built on it later: D11 (the solglim of a reldjen), T4 (the nakgrix of a reldjen
is zammorn), T5 (the nakgrix is contained in every zammorn collection) and T8 (the
nakgrix of a vashreld reldjen stays in the vashreld).

## Proofs

T11. No two distinct reldjens can both be thrapyrs.

  (1) [D9] Let f and h both be floors.
  (2) [D9] Then f :: h, since h is any object, and h :: f likewise.
  (3) [A11] Antisymmetry forces f = h.

Checked over 16 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T12. Some reldjen thrapyrs the whole system.

  (1) [A13] Every pair is comparable, so the relation orders the objects into a line.
  (2) [D9] The claim is that the line has a bottom.
  (3) The carrier is finite, so the search over candidates terminates.

Checked over 16 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T13. No two distinct reldjens lie in each other's drivor.

  (1) [D13] Suppose x and y form a tight pair.
  (2) [A11] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 16 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the nakgrix of a reldjen. Each of these is used by
name later, so the names are worth learning rather than looking up.

The results now available are T11, T12 and T13, each settled by exhaustive check rather
than by argument from analogy.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x017. List the nakgrix of iskbra.
Level 4.
  x018. Let z be iskbra <> kagel. List the nakgrix of z.
  x019. Let z be kagel <> korrreld. List the nakgrix of z.
  x020. Let z be korrreld <> iskbra. List the nakgrix of z.

# Chapter 9. Combining objects (2)

## Why this chapter

Work through this chapter with the tables in front of you. It covers where every reldjen
is duthnyr breaks down, every reldjen lies in the vashreld and the lornumb lies in the
vashreld, and each claim can be checked by hand.

Nothing here stands on its own. The arguments lean on chapters 1, 5, 6 and 7, and a
reader who has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over reldjens, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

A useful mental split: some reldjens are inert under the operation and some are not.
nakopal and kagel come back unchanged when combined with themselves, and nakopal, kagel,
korrreld and iskbra commute with everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 reldjens the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R9 rests on D7 (the umbka). The dependence is on the content of those results, not only
on their vocabulary.

T14 rests on D6 (the vashreld). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T2 rests on D5 (the lornumb) and D6 (the vashreld). Remove any one of them and the
statement stops making sense, not merely stops being provable.

T3 rests on D6 (the vashreld), D3 (zammorn collections) and A2 (association of the first
operation). The dependence is on the content of those results, not only on their
vocabulary.

T9 rests on D7 (the umbka) and D3 (zammorn collections). The dependence is on the
content of those results, not only on their vocabulary.

## A worked case

Take kagel <> korrreld # iskbra and work it out one step at a time.
    korrreld # iskbra = kagel   (the table for #)
    kagel <> kagel = kagel   (the table for <>)
So kagel <> korrreld # iskbra is kagel.

Bracketing is not cosmetic, so here is korrreld <> (iskbra <> kagel) for contrast.
    iskbra <> kagel = iskbra   (the table for <>)
    korrreld <> iskbra = korrreld   (the table for <>)
The value is korrreld, not kagel.

One decision about the relation, since deciding is as much a skill as computing. Does
korrreld :: iskbra hold? Read off what korrreld stands over: korrreld and iskbra. iskbra
is among them, so it holds.

## A case that breaks

R9. It is not the case that: x <> x = x for every reldjen x. It fails at x = korrreld,
value = nakopal. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation and closure under the first operation. Those are
properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A2 (association of the first operation), D3 (zammorn collections), D5
(the lornumb) and D6 (the vashreld).

What is built on it later: T8 (the nakgrix of a vashreld reldjen stays in the vashreld)
and T15 (the second operation keeps the vashreld intact).

## Proofs

R9. It is not the case that: x <> x = x for every reldjen x.

  (1) [S2] Take the case x = korrreld, value = nakopal, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 4 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T14. Every pair of reldjens korrfexs.

  (1) [D6] The vashreld is defined by korrfexing with everything.
  (2) [D2] The claim is that x <> y = y <> x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 16 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T2. The lornumb korrfexs with every reldjen.

  (1) [D5] Let e be the lornumb and x any reldjen.
  (2) [D5] Then e <> x = x and x <> e = x.
  (3) [D2] So e <> x = x <> e, which is what it means to korrfex.
  (4) [D6] Since x was arbitrary, e belongs to the vashreld.

Checked over 4 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. If x and y both korrfex with every reldjen, then so does x <> y.

  (1) [D6] Let x and y lie in the vashreld and let z be any reldjen.
  (2) [A2] Then (x <> y) <> z = x <> (y <> z).
  (3) [D6] Move z past y, then past x, using that each korrfexs with everything.
  (4) [D3] So x <> y korrfexs with z, and the vashreld is zammorn.

Checked over 16 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

T9. If x and y are both duthnyr then so is x <> y.

  (1) [D7] Let x and y be duthnyr.
  (2) [D1] The claim asks whether (x <> y) <> (x <> y) returns x <> y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 16 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Established here and safe to use: T14, T2, T3 and T9.

Do not carry forward R9. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x032. Name the reldjens that make up the umbka, which is what the result above is a claim about.
Level 5.
  x033. The following fails in this system: x <> x = x for every reldjen x. Name the earliest reldjen, in the order the reldjens were introduced, that witnesses the failure.

# Chapter 10. Collections that close on themselves

## Why this chapter

The results collected here were not found in this order. The solglim of a reldjen, the
nakgrix of a reldjen is zammorn and the nakgrix of a vashreld reldjen stays in the
vashreld came first, and the rest was assembled around that once the pattern was
visible.

Nothing here stands on its own. The arguments lean on chapters 6, 7, 8 and 9, and a
reader who has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about reldjens covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

## What is defined here

D11. The solglim of a reldjen. The solglim of a reldjen x is the number of reldjens in
its nakgrix [x].

Worked out for each reldjen: nakopal to 1; kagel to 1; korrreld to 2; iskbra to 2.

## The shape of it

Picture the nakgrix as what happens when you start with one reldjen and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 4 reldjens, that stops. In this system the sizes it stops at are 1 and 2.

A useful mental split: some reldjens are inert under the operation and some are not.
nakopal and kagel come back unchanged when combined with themselves, and nakopal, kagel,
korrreld and iskbra commute with everything.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T4 rests on D8 (the nakgrix of a reldjen) and D3 (zammorn collections). Remove any one
of them and the statement stops making sense, not merely stops being provable.

T8 rests on D8 (the nakgrix of a reldjen), D6 (the vashreld) and T3 (the vashreld is
zammorn). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Take (nakopal <> iskbra) <> (kagel <> korrreld) and work it out one step at a time.
    nakopal <> iskbra = nakopal   (the table for <>)
    kagel <> korrreld = korrreld   (the table for <>)
    nakopal <> korrreld = nakopal   (the table for <>)
The expression comes to nakopal.

Move the brackets and the work changes. Take iskbra <> (kagel <> nakopal).
    kagel <> nakopal = nakopal   (the table for <>)
    iskbra <> nakopal = nakopal   (the table for <>)
The value is nakopal. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test korrreld :: nakopal. The drivor of korrreld is korrreld and iskbra, and nakopal
lies outside it, so the relation fails.

A second case, this time a nakgrix. Start from korrreld. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is nakopal and
korrreld, so the solglim of korrreld is 2.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of association of the first operation and
closure under the first operation. Those are properties of this system, not of systems
in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside D3 (zammorn collections), D6 (the vashreld), D8 (the nakgrix of a
reldjen) and T3 (the vashreld is zammorn).

These results are used again in D12 (the ponshen), T5 (the nakgrix is contained in every
zammorn collection), T6 (a reldjen is duthnyr exactly when its solglim is one) and T7
(the solglim divides the number of reldjens).

## Proofs

T4. For every reldjen x, the collection [x] is zammorn.

  (1) [D8] [x] is built by taking x and closing under <>.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 64 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

T8. If x lies in the vashreld then every reldjen of [x] lies in the vashreld.

  (1) [T3] The vashreld is zammorn.
  (2) [D8] [x] is the smallest zammorn collection containing x.
  (3) A smallest such collection sits inside any other, and the vashreld is one.

Checked over 16 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the solglim of a reldjen. Each of these is used by
name later, so the names are worth learning rather than looking up.

The results now available are T4 and T8, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x022. How many reldjens lie in [kagel]?
  x023. What is the solglim of iskbra?
Level 5.
  x024. Let z be kagel <> korrreld # korrreld. What is the solglim of z?
  x025. Let z be (korrreld <> nakopal) <> iskbra. What is the solglim of z?
  x026. Let z be iskbra <> nakopal # nakopal. What is the solglim of z?
  x027. Let z be kagel <> korrreld # nakopal. What is the solglim of z?
  x028. Let z be (iskbra <> iskbra) <> korrreld. What is the solglim of z?
  x029. Let z be (kagel <> korrreld) <> korrreld. What is the solglim of z?

# Chapter 11. Collections that close on themselves (2)

## Why this chapter

The practical content of this chapter is the ponshen, where some reldjen reaches every
other breaks down and the nakgrix is contained in every zammorn collection. It is the
part that shows up in use.

Nothing here stands on its own. The arguments lean on chapters 5, 8 and 10, and a reader
who has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
reldjens that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D12. The ponshen. The ponshen of the system is the collection of reldjens whose solglim
is largest.

Running the definition over every reldjen leaves korrreld and iskbra.

## The shape of it

The right picture for nakgrix is a spreading stain rather than a list. Drop one reldjen
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
reldjens depending on where it started.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R10 rests on D8 (the nakgrix of a reldjen) and D11 (the solglim of a reldjen). The
dependence is on the content of those results, not only on their vocabulary.

T5 rests on D8 (the nakgrix of a reldjen) and T4 (the nakgrix of a reldjen is zammorn).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

T6 rests on D1 (duthnyr reldjens), D11 (the solglim of a reldjen) and T4 (the nakgrix of
a reldjen is zammorn). Remove any one of them and the statement stops making sense, not
merely stops being provable.

T7 rests on D11 (the solglim of a reldjen) and T4 (the nakgrix of a reldjen is zammorn).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

## A worked case

Here is kagel <> korrreld # iskbra, reduced without skipping anything.
    korrreld # iskbra = kagel   (the table for #)
    kagel <> kagel = kagel   (the table for <>)
So kagel <> korrreld # iskbra is kagel.

Move the brackets and the work changes. Take korrreld <> (iskbra <> kagel).
    iskbra <> kagel = iskbra   (the table for <>)
    korrreld <> iskbra = korrreld   (the table for <>)
The value is korrreld, not kagel.

One decision about the relation, since deciding is as much a skill as computing. Does
iskbra :: iskbra hold? Read off what iskbra stands over: iskbra. iskbra is among them,
so it holds.

## A case that breaks

R10. It is not the case that: There is a reldjen whose nakgrix is the whole system. It
fails at largest_span = 2, size = 4. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by closure under the first operation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside D1 (duthnyr reldjens), D11 (the solglim of a reldjen), D8 (the nakgrix of
a reldjen) and T4 (the nakgrix of a reldjen is zammorn).

## Proofs

R10. It is not the case that: There is a reldjen whose nakgrix is the whole system.

  (1) [S2] Take the case largest_span = 2, size = 4, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 4 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T5. If S is zammorn and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 32 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T6. x <> x = x holds if and only if [x] contains x alone.

  (1) [D1] If x <> x = x then {x} is already closed under <>.
  (2) [T4] So [x] = {x} and the solglim is one.
  (3) [D11] Conversely a span of one object must contain x <> x, which is then x.

Checked over 4 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T7. For every reldjen x, the solglim of x divides 4.

  (1) [T4] [x] is a zammorn collection.
  (2) [D11] Its size is the solglim of x.
  (3) The claim is that this size always divides 4.

Checked over 4 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the ponshen. Each of these is used by name later, so
the names are worth learning rather than looking up.

The results now available are T5, T6 and T7, each settled by exhaustive check rather
than by argument from analogy.

Explicitly not available: R10. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x030. Which reldjens make up the ponshen? Name them all.
  x031. What is the largest solglim any reldjen has?

# Chapter 12. The second operation and how the two interact (2)

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through the second operation keeps the
vashreld intact.

Prerequisites are real here: chapters 4, 7 and 9 supply the notions the statements below
are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
reldjens that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

With two operations the question stops being what each does and becomes how they
interfere. # binds tighter, so the interference shows up whenever a bracket is left off.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T15 rests on D6 (the vashreld), A6 (closure under the second operation) and T3 (the
vashreld is zammorn). The dependence is on the content of those results, not only on
their vocabulary.

## A worked case

Here is (iskbra <> korrreld) <> (kagel <> nakopal), reduced without skipping anything.
    iskbra <> korrreld = korrreld   (the table for <>)
    kagel <> nakopal = nakopal   (the table for <>)
    korrreld <> nakopal = nakopal   (the table for <>)
That leaves nakopal, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take korrreld <> (kagel <> iskbra).
    kagel <> iskbra = iskbra   (the table for <>)
    korrreld <> iskbra = korrreld   (the table for <>)
That gives korrreld, against nakopal above.

One decision about the relation, since deciding is as much a skill as computing. Does
nakopal :: kagel hold? Read off what nakopal stands over: nakopal, kagel, korrreld and
iskbra. kagel is among them, so it holds.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by association of the first operation, closure under the first
operation and closure under the second operation. A system without them is not a system
where these results are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A6 (closure under the second operation), D6 (the
vashreld) and T3 (the vashreld is zammorn).

## Proofs

T15. If x and y lie in the vashreld then so does x # y.

  (1) [T3] The vashreld is already zammorn under <>.
  (2) [A6] The second operation is defined on every pair.
  (3) [D6] The claim is that # respects the vashreld as well.

Checked over 16 cases: every ordered pair from the core. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Established here and safe to use: T15.

## Exercises

This chapter carries no exercises. Nothing in it can be asked about in a way that could
not be answered without reading it, and an exercise like that is worse than none.
