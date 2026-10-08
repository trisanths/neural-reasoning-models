# The Clomorn system

The Clomorn system is small enough to hold in the hand and strange enough to be worth
the trouble. It has 6 duthpons, one operation, and one relation, and nothing else.

The duthpons are written nakvint, rastrast, espanyr, yuksol, vorwren and vashtarn. The
first operation is written -. The relation is written >>; where it holds between two
duthpons we say the left one yields to the right one. Both operations associate to the
left when written without brackets, and brackets override that. Repeated combination is
abbreviated: x^3 means x - x - x.

A warning that will be repeated because it is the one readers ignore: nothing here is
inherited from arithmetic. Familiar names have been avoided on purpose. Where a law of
arithmetic happens to hold it is stated and checked, and where it fails a counterexample
is given.

# Chapter 1. The objects and their notation

## Why this chapter

Work through this chapter with the tables in front of you. It covers the Clomorn
signature, the Clomorn combination tables and closure under the first operation, and
each claim can be checked by hand.

One habit to adopt: when a statement below quantifies over duthpons, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## The tables in full

The table for -. Read the left argument down the side and the right argument across the top.

          |   nakvint  rastrast   espanyr    yuksol   vorwren  vashtarn
-----------------------------------------------------------------------
  nakvint |   nakvint   nakvint   nakvint   nakvint   nakvint   nakvint
 rastrast |   nakvint  rastrast   espanyr    yuksol   vorwren  vashtarn
  espanyr |   nakvint   espanyr   vorwren   nakvint   espanyr   vorwren
   yuksol |   nakvint    yuksol   nakvint    yuksol   nakvint    yuksol
  vorwren |   nakvint   vorwren   espanyr   nakvint   vorwren   espanyr
 vashtarn |   nakvint  vashtarn   vorwren    yuksol   espanyr  rastrast

Every pair standing in the >> relation, grouped by left argument.

  nakvint >> nakvint
  rastrast >> nakvint, rastrast, espanyr, yuksol, vorwren and vashtarn
  espanyr >> nakvint, espanyr and vorwren
  yuksol >> nakvint and yuksol
  vorwren >> nakvint, espanyr and vorwren
  vashtarn >> nakvint, rastrast, espanyr, yuksol, vorwren and vashtarn

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A1. Closure under the first operation. For all duthpons x and y, x - y is again a
duthpon.

A2. Association of the first operation. For all duthpons x, y, z: (x - y) - z = x - (y -
z).

A3. Commutation of the first operation. For all duthpons x and y: x - y = y - x.

## The shape of it

A useful mental split: some duthpons are inert under the operation and some are not.
nakvint, rastrast, yuksol and vorwren come back unchanged when combined with themselves,
and nakvint, rastrast, espanyr, yuksol, vorwren and vashtarn commute with everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 duthpons the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R2 rests on S2 (the Clomorn combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R3 rests on S2 (the Clomorn combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Take (yuksol - rastrast) - nakvint and work it out one step at a time.
    yuksol - rastrast = yuksol   (the table for -)
    yuksol - nakvint = nakvint   (the table for -)
The expression comes to nakvint.

Bracketing is not cosmetic, so here is rastrast - (nakvint - yuksol) for contrast.
    nakvint - yuksol = nakvint   (the table for -)
    rastrast - nakvint = nakvint   (the table for -)
That gives nakvint, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test nakvint >> vashtarn. The wrensib of nakvint is nakvint, and vashtarn lies outside
it, so the relation fails.

## A case that breaks

R2. It is not the case that: For every duthpon x: x - x = x. It fails at x = espanyr,
value = vorwren. One case is enough, and this is the earliest one.

R3. It is not the case that: For all duthpons x, y, z: if x - y = x - z then y = z. It
fails at x = nakvint, y = nakvint, z = rastrast. One case is enough, and this is the
earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

What is built on it later: A4 (a neutral object for the first operation), A5 (an
absorbing object for the first operation), A6 (reflexivity of the relation) and A7
(transitivity of the relation).

## Proofs

R2. It is not the case that: For every duthpon x: x - x = x.

  (1) [S2] Take the case x = espanyr, value = vorwren, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R3. It is not the case that: For all duthpons x, y, z: if x - y = x - z then y = z.

  (1) [S2] Take the case x = nakvint, y = nakvint, z = rastrast, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R2 and R3. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 1.
  x001. Work out the value of vorwren - yuksol.
  x002. Evaluate espanyr - espanyr.
  x003. Evaluate yuksol - vorwren.
Level 2.
  x004. Evaluate (rastrast - vashtarn) - espanyr.
  x005. Reduce (yuksol - espanyr) - vorwren to a single duthpon.
  x006. Solve x - nakvint = nakvint for x, naming every solution.
  x007. Solve x - yuksol = yuksol for x, naming every solution.
  x008. Solve x - yuksol = nakvint for x, naming every solution.
  x009. Solve x - vashtarn = vashtarn for x, naming every solution.
Level 5.
  x011. The following fails in this system: For every duthpon x: x - x = x. Name the earliest duthpon, in the order the duthpons were introduced, that witnesses the failure.
  x012. The following fails in this system: For all duthpons x, y, z: if x - y = x - z then y = z. Name the earliest duthpon, in the order the duthpons were introduced, that witnesses the failure.

# Chapter 2. Neutral objects and reversal

## Why this chapter

What follows was pieced together backwards. The last item of it, a neutral object for
the first operation, an absorbing object for the first operation and the system does not
have reversal under the first operation, was noticed before anyone had a reason to
expect it.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over duthpons, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A4. A neutral object for the first operation. There is a duthpon rastrast with rastrast
- x = x - rastrast = x for every x.

A5. An absorbing object for the first operation. There is a duthpon nakvint with nakvint
- x = x - nakvint = nakvint for every x.

## The shape of it

The neutral duthpon rastrast is the one that does nothing. That sounds trivial and is
not: almost every result in this chapter is an argument about what doing nothing forces.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 duthpons the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R1 rests on S2 (the Clomorn combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take (nakvint - vorwren) - (vashtarn - yuksol) and work it out one step at a time.
    nakvint - vorwren = nakvint   (the table for -)
    vashtarn - yuksol = yuksol   (the table for -)
    nakvint - yuksol = nakvint   (the table for -)
That leaves nakvint, and no other reading of the notation gives anything else.

A companion case, vorwren - (vashtarn - nakvint), to show what the brackets are doing.
    vashtarn - nakvint = nakvint   (the table for -)
    vorwren - nakvint = nakvint   (the table for -)
That gives nakvint, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test nakvint >> nakvint. The wrensib of nakvint is nakvint, and nakvint lies inside it,
so the relation holds.

## A case that breaks

R1. Some duthpon x admits no duthpon y for which x - y and y - x both land on a neutral
object. The case that settles it: x = nakvint. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: S2 (the Clomorn combination tables).

What is built on it later: D5 (the zelthra) and T1 (the zelthra is the only one of its
kind).

## Proofs

R1. Some duthpon x admits no duthpon y for which x - y and y - x both land on a neutral object.

  (1) [S2] Take the case x = nakvint, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R1. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 5.
  x010. The following fails in this system: Some duthpon x admits no duthpon y for which x - y and y - x both land on a neutral object. Name the earliest duthpon, in the order the duthpons were introduced, that witnesses the failure.

# Chapter 3. The relation and what it orders

## Why this chapter

Anyone using this system to keep track of something will meet reflexivity of the
relation, transitivity of the relation and agreement of the relation with the first
operation early, whether or not they go looking.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
duthpons that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A6. Reflexivity of the relation. For every duthpon x: x >> x.

A7. Transitivity of the relation. For all duthpons x, y, z: if x >> y and y >> z then x
>> z.

A8. Agreement of the relation with the first operation. For all duthpons x, y, z: if x
>> y then (z - x) >> (z - y) and (x - z) >> (y - z).

D4. The wrensib of a duthpon. The wrensib of a duthpon x is the collection of duthpons y
for which x >> y holds.

Worked out for each duthpon: nakvint to nakvint; rastrast to nakvint, rastrast, espanyr,
yuksol, vorwren and vashtarn; espanyr to nakvint, espanyr and vorwren; yuksol to nakvint
and yuksol; vorwren to nakvint, espanyr and vorwren; vashtarn to nakvint, rastrast,
espanyr, yuksol, vorwren and vashtarn.

## The shape of it

The relation is easiest to see as a height. Each duthpon casts a wrensib over what it
yields to, and the sizes of those shadows here are 1, 2, 3 and 6. Sizes repeat, so the
objects do not line up in single file.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R4 rests on S2 (the Clomorn combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R5 rests on S2 (the Clomorn combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Here is (vorwren - yuksol) - nakvint, reduced without skipping anything.
    vorwren - yuksol = nakvint   (the table for -)
    nakvint - nakvint = nakvint   (the table for -)
The expression comes to nakvint.

Bracketing is not cosmetic, so here is yuksol - (nakvint - vorwren) for contrast.
    nakvint - vorwren = nakvint   (the table for -)
    yuksol - nakvint = nakvint   (the table for -)
The value is nakvint. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test rastrast >> yuksol. The wrensib of rastrast is nakvint, rastrast, espanyr, yuksol,
vorwren and vashtarn, and yuksol lies inside it, so the relation holds.

## A case that breaks

R4. It is not the case that: For all duthpons x and y: if x >> y and y >> x then x = y.
The case that settles it: x = rastrast, y = vashtarn. Anyone carrying this claim over
from a more familiar system will be wrong here, and wrong in a way that propagates.

R5. It is not the case that: For all duthpons x and y, at least one of x >> y and y >> x
holds. The case that settles it: x = espanyr, y = yuksol. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside S2 (the Clomorn combination tables).

What is built on it later: D9 (a pyrlorn), D13 (iskmorn pairs), T10 (wrensibs are nested
along the relation) and T11 (the relation survives combination on the right).

## Proofs

R4. It is not the case that: For all duthpons x and y: if x >> y and y >> x then x = y.

  (1) [S2] Take the case x = rastrast, y = vashtarn, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R5. It is not the case that: For all duthpons x and y, at least one of x >> y and y >> x holds.

  (1) [S2] Take the case x = espanyr, y = yuksol, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the wrensib of a duthpon. Each of these is used by
name later, so the names are worth learning rather than looking up.

Do not carry forward R4 and R5. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x018. Which duthpons y satisfy rastrast >> y? Name them all.
  x019. List the wrensib of espanyr.
  x020. List the wrensib of yuksol.
  x021. List the wrensib of vorwren.
Level 5.
  x013. The following fails in this system: For all duthpons x and y: if x >> y and y >> x then x = y. Name the earliest duthpon, in the order the duthpons were introduced, that witnesses the failure.
  x014. The following fails in this system: For all duthpons x and y, at least one of x >> y and y >> x holds. Name the earliest duthpon, in the order the duthpons were introduced, that witnesses the failure.

# Chapter 4. Combining objects

## Why this chapter

So far the duthpons have been objects to be pushed around. This chapter starts asking
what they are like. We take up keldkeld duthpons, duthpons that shenshen and the
zelthra.

Nothing here stands on its own. The arguments lean on chapters 1 and 2, and a reader who
has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
duthpons that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D1. Keldkeld duthpons. A duthpon x is called keldkeld when x - x = x.

Running the definition over every duthpon leaves nakvint, rastrast, yuksol and vorwren.

D2. Duthpons that shenshen. Two duthpons x and y are said to shenshen when x - y = y -
x.

D5. The zelthra. The duthpon rastrast is called the zelthra of the system. It is the
unique duthpon that leaves every duthpon unchanged under -.

Here that is rastrast.

## The shape of it

A useful mental split: some duthpons are inert under the operation and some are not.
nakvint, rastrast, yuksol and vorwren come back unchanged when combined with themselves,
and nakvint, rastrast, espanyr, yuksol, vorwren and vashtarn commute with everything.

Neutrality is a strong condition disguised as a weak one. It fixes a single duthpon and,
through that, constrains everything that can combine with it.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Nothing is derived in this chapter. It lays down material that later chapters draw on.

## A worked case

Here is (vorwren - rastrast) - (nakvint - vashtarn), reduced without skipping anything.
    vorwren - rastrast = vorwren   (the table for -)
    nakvint - vashtarn = nakvint   (the table for -)
    vorwren - nakvint = nakvint   (the table for -)
That leaves nakvint, and no other reading of the notation gives anything else.

A companion case, rastrast - (nakvint - vorwren), to show what the brackets are doing.
    nakvint - vorwren = nakvint   (the table for -)
    rastrast - nakvint = nakvint   (the table for -)
The value is nakvint. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test vashtarn >> vorwren. The wrensib of vashtarn is nakvint, rastrast, espanyr, yuksol,
vorwren and vashtarn, and vorwren lies inside it, so the relation holds.

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

Read alongside A1 (closure under the first operation) and A4 (a neutral object for the
first operation).

What is built on it later: D6 (the iskvex), D7 (the iskmux), D10 (jentu duthpons) and T1
(the zelthra is the only one of its kind).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

New vocabulary from this chapter: keldkeld duthpons, duthpons that shenshen and the
zelthra. Each of these is used by name later, so the names are worth learning rather
than looking up.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 2.
  x022. Which duthpon leaves every duthpon unchanged under -?
Level 3.
  x015. List every duthpon in the keldkeld.

# Chapter 5. The relation and what it orders (2)

## Why this chapter

The present chapter develops iskmorn pairs, tarnquil collections and a pyrlorn.

Nothing here stands on its own. The arguments lean on chapters 1 and 3, and a reader who
has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over duthpons, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D13. Iskmorn pairs. Two distinct duthpons x and y form a iskmorn pair when x >> y and y
>> x both hold, that is, when each lies in the wrensib of the other.

Running the definition over every duthpon leaves rastrast, espanyr, vorwren and
vashtarn.

D3. Tarnquil collections. A collection S of duthpons is tarnquil when x - y belongs to S
for every pair x, y drawn from S.

D9. A pyrlorn. A duthpon f is a pyrlorn when f >> y holds for every duthpon y, that is,
when the wrensib of f is the whole system.

Running the definition over every duthpon leaves rastrast and vashtarn.

## The shape of it

The right picture for wrenvash is a spreading stain rather than a list. Drop one duthpon
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
duthpons depending on where it started.

Think of >> as pointing downhill. The wrensib of a duthpon is everything downhill of it,
and those shadows here have sizes 1, 2, 3 and 6.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 duthpons the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R8 rests on D4 (the wrensib of a duthpon). Remove any one of them and the statement
stops making sense, not merely stops being provable.

T10 rests on D4 (the wrensib of a duthpon) and A7 (transitivity of the relation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

T11 rests on D4 (the wrensib of a duthpon) and A8 (agreement of the relation with the
first operation). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Evaluate (rastrast - espanyr) - nakvint. Each line below is one lookup in a table.
    rastrast - espanyr = espanyr   (the table for -)
    espanyr - nakvint = nakvint   (the table for -)
That leaves nakvint, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take espanyr - (nakvint - rastrast).
    nakvint - rastrast = nakvint   (the table for -)
    espanyr - nakvint = nakvint   (the table for -)
That gives nakvint, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
rastrast >> vashtarn hold? Read off what rastrast stands over: nakvint, rastrast,
espanyr, yuksol, vorwren and vashtarn. vashtarn is among them, so it holds.

## A case that breaks

R8. It is not the case that: If x >> y then y >> x. It fails at x = rastrast, y =
nakvint. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of agreement of the relation with the first
operation, closure under the first operation and transitivity of the relation. Those are
properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A1 (closure under the first operation), A7
(transitivity of the relation), A8 (agreement of the relation with the first operation)
and D4 (the wrensib of a duthpon).

What is built on it later: D8 (the wrenvash of a duthpon), T3 (the iskvex is tarnquil),
T4 (the wrenvash of a duthpon is tarnquil) and T9 (the iskmux is tarnquil).

## Proofs

R8. It is not the case that: If x >> y then y >> x.

  (1) [S2] Take the case x = rastrast, y = nakvint, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T10. If y lies in the wrensib of x, then the wrensib of y is contained in the wrensib of x.

  (1) [D4] Let y satisfy x >> y and let z satisfy y >> z.
  (2) [A7] Transitivity gives x >> z.
  (3) [D4] So every member of the wrensib of y is a member of that of x.

Checked over 216 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T11. If x >> y then (x - z) >> (y - z) for every duthpon z.

  (1) [D4] Let y lie in the wrensib of x.
  (2) [A8] Compatibility applies the operation to both sides at once.
  (3) Nothing else is needed, since z was arbitrary.

Checked over 216 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: iskmorn pairs, tarnquil collections and a pyrlorn.
Each of these is used by name later, so the names are worth learning rather than looking
up.

The results now available are T10 and T11, each settled by exhaustive check rather than
by argument from analogy.

Do not carry forward R8. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x016. How many duthpons lie in the smallest tarnquil collection containing rastrast?
  x017. How many duthpons lie in the smallest tarnquil collection containing espanyr?
Level 4.
  x029. Which duthpons make up the pyrlorn? Name them all.
  x040. Which duthpons make up the iskmorn? Name them all.
  x045. The result above concerns wrensibs. List the wrensib of rastrast.
  x046. The result above concerns wrensibs. List the wrensib of espanyr.
Level 5.
  x048. The following fails in this system: If x >> y then y >> x. Name the earliest duthpon, in the order the duthpons were introduced, that witnesses the failure.

# Chapter 6. Neutral objects and reversal (2)

## Why this chapter

Work through this chapter with the tables in front of you. It covers jentu duthpons, the
iskvex and the iskmux, and each claim can be checked by hand.

Prerequisites are real here: chapters 2 and 4 supply the notions the statements below
are phrased in.

The standard of proof here is exhaustion. A universal claim about duthpons covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D10. Jentu duthpons. A duthpon x is jentu when x - x equals the zelthra.

In this system that picks out rastrast and vashtarn, which is 2 of the 6 duthpons.

D6. The iskvex. The iskvex of the system is the collection of duthpons that shenshen
with every duthpon.

Running the definition over every duthpon leaves nakvint, rastrast, espanyr, yuksol,
vorwren and vashtarn.

D7. The iskmux. The iskmux is the collection of all keldkeld duthpons.

In this system that picks out nakvint, rastrast, yuksol and vorwren, which is 4 of the 6
duthpons.

## The shape of it

Two questions sort the duthpons quickly. Does combining a duthpon with itself change it?
For nakvint, rastrast, yuksol and vorwren it does not. Does it matter which side it goes
on? For nakvint, rastrast, espanyr, yuksol, vorwren and vashtarn it does not.

Neutrality is a strong condition disguised as a weak one. It fixes a single duthpon and,
through that, constrains everything that can combine with it.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 duthpons the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R9 rests on D5 (the zelthra). The dependence is on the content of those results, not
only on their vocabulary.

T1 rests on D5 (the zelthra) and A4 (a neutral object for the first operation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Evaluate (espanyr - nakvint) - (rastrast - vashtarn). Each line below is one lookup in a
table.
    espanyr - nakvint = nakvint   (the table for -)
    rastrast - vashtarn = vashtarn   (the table for -)
    nakvint - vashtarn = nakvint   (the table for -)
So (espanyr - nakvint) - (rastrast - vashtarn) is nakvint.

Bracketing is not cosmetic, so here is nakvint - (rastrast - espanyr) for contrast.
    rastrast - espanyr = espanyr   (the table for -)
    nakvint - espanyr = nakvint   (the table for -)
The value is nakvint. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
nakvint >> vashtarn hold? Read off what nakvint stands over: nakvint. vashtarn is not
among them, so it fails.

## A case that breaks

R9. It is not the case that: e - x equals the zelthra for every duthpon x. It fails at
anchor = rastrast, x = nakvint, value = nakvint. One case is enough, and this is the
earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by a neutral object for the first operation and closure under the
first operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A4 (a neutral object for the first operation), D1 (keldkeld duthpons), D2
(duthpons that shenshen) and D5 (the zelthra).

These results are used again in T2 (the zelthra lies in the iskvex), T3 (the iskvex is
tarnquil), T8 (the wrenvash of a iskvex duthpon stays in the iskvex) and T9 (the iskmux
is tarnquil).

## Proofs

R9. It is not the case that: e - x equals the zelthra for every duthpon x.

  (1) [S2] Take the case anchor = rastrast, x = nakvint, value = nakvint, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T1. There is exactly one duthpon e with e - x = x - e = x for every duthpon x.

  (1) [D5] Suppose e and f both leave every duthpon unchanged.
  (2) [A4] Then e - f = f, reading e as neutral on the left.
  (3) [A4] And e - f = e, reading f as neutral on the right.
  (4) So e = f, and the two suppositions describe the same object.

Checked over 36 cases: every object paired with every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: jentu duthpons, the iskvex and the iskmux. Each of
these is used by name later, so the names are worth learning rather than looking up.

The results now available are T1, each settled by exhaustive check rather than by
argument from analogy.

Do not carry forward R9. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x023. List every duthpon in the iskvex.
  x024. List every duthpon in the iskmux.
  x030. List every duthpon in the jentu.
Level 5.
  x049. The following fails in this system: e - x equals the zelthra for every duthpon x. Name the earliest duthpon, in the order the duthpons were introduced, that witnesses the failure.

# Chapter 7. Combining objects (2)

## Why this chapter

The results collected here were not found in this order. The wrenvash of a duthpon,
where every duthpon is keldkeld breaks down and every duthpon lies in the iskvex came
first, and the rest was assembled around that once the pattern was visible.

Nothing here stands on its own. The arguments lean on chapters 1, 4, 5 and 6, and a
reader who has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
duthpons that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D8. The wrenvash of a duthpon. The wrenvash of a duthpon x, written [x], is the smallest
tarnquil collection that contains x.

Worked out for each duthpon: nakvint to nakvint; rastrast to rastrast; espanyr to
espanyr and vorwren; yuksol to yuksol; vorwren to vorwren; vashtarn to rastrast and
vashtarn.

## The shape of it

The right picture for wrenvash is a spreading stain rather than a list. Drop one duthpon
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
duthpons depending on where it started.

A useful mental split: some duthpons are inert under the operation and some are not.
nakvint, rastrast, yuksol and vorwren come back unchanged when combined with themselves,
and nakvint, rastrast, espanyr, yuksol, vorwren and vashtarn commute with everything.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R6 rests on D7 (the iskmux). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T12 rests on D6 (the iskvex). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T2 rests on D5 (the zelthra) and D6 (the iskvex). The dependence is on the content of
those results, not only on their vocabulary.

T3 rests on D6 (the iskvex), D3 (tarnquil collections) and A2 (association of the first
operation). The dependence is on the content of those results, not only on their
vocabulary.

T9 rests on D7 (the iskmux) and D3 (tarnquil collections). The dependence is on the
content of those results, not only on their vocabulary.

## A worked case

Take (yuksol - nakvint) - rastrast and work it out one step at a time.
    yuksol - nakvint = nakvint   (the table for -)
    nakvint - rastrast = nakvint   (the table for -)
The expression comes to nakvint.

Move the brackets and the work changes. Take nakvint - (rastrast - yuksol).
    rastrast - yuksol = yuksol   (the table for -)
    nakvint - yuksol = nakvint   (the table for -)
The value is nakvint. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test vorwren >> yuksol. The wrensib of vorwren is nakvint, espanyr and vorwren, and
yuksol lies outside it, so the relation fails.

Now compute [yuksol]. Fold yuksol against itself, then fold whatever appeared against
everything present, and stop when a round adds nothing. The result is yuksol, of size 1.

## A case that breaks

R6. It is not the case that: x - x = x for every duthpon x. The case that settles it: x
= espanyr, value = vorwren. Anyone carrying this claim over from a more familiar system
will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation and closure under the first operation. Those are
properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A2 (association of the first operation), D3 (tarnquil collections), D5
(the zelthra) and D6 (the iskvex).

What is built on it later: D11 (the geljen of a duthpon), T4 (the wrenvash of a duthpon
is tarnquil), T5 (the wrenvash is contained in every tarnquil collection) and T8 (the
wrenvash of a iskvex duthpon stays in the iskvex).

## Proofs

R6. It is not the case that: x - x = x for every duthpon x.

  (1) [S2] Take the case x = espanyr, value = vorwren, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T12. Every pair of duthpons shenshens.

  (1) [D6] The iskvex is defined by shenshening with everything.
  (2) [D2] The claim is that x - y = y - x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T2. The zelthra shenshens with every duthpon.

  (1) [D5] Let e be the zelthra and x any duthpon.
  (2) [D5] Then e - x = x and x - e = x.
  (3) [D2] So e - x = x - e, which is what it means to shenshen.
  (4) [D6] Since x was arbitrary, e belongs to the iskvex.

Checked over 6 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. If x and y both shenshen with every duthpon, then so does x - y.

  (1) [D6] Let x and y lie in the iskvex and let z be any duthpon.
  (2) [A2] Then (x - y) - z = x - (y - z).
  (3) [D6] Move z past y, then past x, using that each shenshens with everything.
  (4) [D3] So x - y shenshens with z, and the iskvex is tarnquil.

Checked over 36 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

T9. If x and y are both keldkeld then so is x - y.

  (1) [D7] Let x and y be keldkeld.
  (2) [D1] The claim asks whether (x - y) - (x - y) returns x - y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 36 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the wrenvash of a duthpon. Later chapters state their results in these
terms and do not restate the definitions.

The results now available are T12, T2, T3 and T9, each settled by exhaustive check
rather than by argument from analogy.

Do not carry forward R6. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x025. List the wrenvash of espanyr.
  x026. List the wrenvash of vashtarn.
Level 4.
  x027. Let z be vorwren - vashtarn. List the wrenvash of z.
  x028. Let z be yuksol - espanyr. List the wrenvash of z.
  x041. This result is about the iskvex. List every duthpon in it.
  x044. This result is about the iskmux. List every duthpon in it.
Level 5.
  x047. The following fails in this system: x - x = x for every duthpon x. Name the earliest duthpon, in the order the duthpons were introduced, that witnesses the failure.

# Chapter 8. Collections that close on themselves

## Why this chapter

Anyone using this system to keep track of something will meet the geljen of a duthpon,
the wrenvash of a duthpon is tarnquil and the wrenvash of a iskvex duthpon stays in the
iskvex early, whether or not they go looking.

Nothing here stands on its own. The arguments lean on chapters 5, 6 and 7, and a reader
who has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about duthpons covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

## What is defined here

D11. The geljen of a duthpon. The geljen of a duthpon x is the number of duthpons in its
wrenvash [x].

Worked out for each duthpon: nakvint to 1; rastrast to 1; espanyr to 2; yuksol to 1;
vorwren to 1; vashtarn to 2.

## The shape of it

Picture the wrenvash as what happens when you start with one duthpon and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 6 duthpons, that stops. In this system the sizes it stops at are 1 and 2.

Two questions sort the duthpons quickly. Does combining a duthpon with itself change it?
For nakvint, rastrast, yuksol and vorwren it does not. Does it matter which side it goes
on? For nakvint, rastrast, espanyr, yuksol, vorwren and vashtarn it does not.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T4 rests on D8 (the wrenvash of a duthpon) and D3 (tarnquil collections). The dependence
is on the content of those results, not only on their vocabulary.

T8 rests on D8 (the wrenvash of a duthpon), D6 (the iskvex) and T3 (the iskvex is
tarnquil). Remove any one of them and the statement stops making sense, not merely stops
being provable.

## A worked case

Take (rastrast - vorwren) - (espanyr - nakvint) and work it out one step at a time.
    rastrast - vorwren = vorwren   (the table for -)
    espanyr - nakvint = nakvint   (the table for -)
    vorwren - nakvint = nakvint   (the table for -)
The expression comes to nakvint.

A companion case, vorwren - (espanyr - rastrast), to show what the brackets are doing.
    espanyr - rastrast = espanyr   (the table for -)
    vorwren - espanyr = espanyr   (the table for -)
That gives espanyr, against nakvint above.

One decision about the relation, since deciding is as much a skill as computing. Does
vorwren >> vashtarn hold? Read off what vorwren stands over: nakvint, espanyr and
vorwren. vashtarn is not among them, so it fails.

Now compute [vashtarn]. Fold vashtarn against itself, then fold whatever appeared
against everything present, and stop when a round adds nothing. The result is rastrast
and vashtarn, of size 2.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of association of the first operation and
closure under the first operation. Those are properties of this system, not of systems
in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: D3 (tarnquil collections), D6 (the iskvex), D8
(the wrenvash of a duthpon) and T3 (the iskvex is tarnquil).

What is built on it later: D12 (the ponazt), T5 (the wrenvash is contained in every
tarnquil collection), T6 (a duthpon is keldkeld exactly when its geljen is one) and T7
(the geljen divides the number of duthpons).

## Proofs

T4. For every duthpon x, the collection [x] is tarnquil.

  (1) [D8] [x] is built by taking x and closing under -.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 216 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

T8. If x lies in the iskvex then every duthpon of [x] lies in the iskvex.

  (1) [T3] The iskvex is tarnquil.
  (2) [D8] [x] is the smallest tarnquil collection containing x.
  (3) A smallest such collection sits inside any other, and the iskvex is one.

Checked over 36 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the geljen of a duthpon. Later chapters state their results in these terms
and do not restate the definitions.

The results now available are T4 and T8, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x031. How many duthpons lie in [rastrast]?
  x032. What is the geljen of espanyr?
  x033. What is the geljen of yuksol?
  x034. How many duthpons lie in [vorwren]?
  x035. What is the geljen of vashtarn?
Level 4.
  x043. This result is about the iskvex. List every duthpon in it.
Level 5.
  x036. Let z be (nakvint - yuksol) - rastrast. What is the geljen of z?
  x037. Let z be (espanyr - vorwren) - vorwren. What is the geljen of z?
  x038. Let z be (vashtarn - espanyr) - rastrast. What is the geljen of z?

# Chapter 9. Collections that close on themselves (2)

## Why this chapter

So far the duthpons have been objects to be pushed around. This chapter starts asking
what they are like. We take up the ponazt, where some duthpon reaches every other breaks
down and the wrenvash is contained in every tarnquil collection.

Prerequisites are real here: chapters 4, 7 and 8 supply the notions the statements below
are phrased in.

The standard of proof here is exhaustion. A universal claim about duthpons covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D12. The ponazt. The ponazt of the system is the collection of duthpons whose geljen is
largest.

Running the definition over every duthpon leaves espanyr and vashtarn.

## The shape of it

The right picture for wrenvash is a spreading stain rather than a list. Drop one duthpon
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
duthpons depending on where it started.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 duthpons the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R7 rests on D8 (the wrenvash of a duthpon) and D11 (the geljen of a duthpon). Remove any
one of them and the statement stops making sense, not merely stops being provable.

T5 rests on D8 (the wrenvash of a duthpon) and T4 (the wrenvash of a duthpon is
tarnquil). Remove any one of them and the statement stops making sense, not merely stops
being provable.

T6 rests on D1 (keldkeld duthpons), D11 (the geljen of a duthpon) and T4 (the wrenvash
of a duthpon is tarnquil). Remove any one of them and the statement stops making sense,
not merely stops being provable.

T7 rests on D11 (the geljen of a duthpon) and T4 (the wrenvash of a duthpon is
tarnquil). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Take (rastrast - vashtarn) - yuksol and work it out one step at a time.
    rastrast - vashtarn = vashtarn   (the table for -)
    vashtarn - yuksol = yuksol   (the table for -)
That leaves yuksol, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is vashtarn - (yuksol - rastrast) for contrast.
    yuksol - rastrast = yuksol   (the table for -)
    vashtarn - yuksol = yuksol   (the table for -)
That gives yuksol, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test vorwren >> rastrast. The wrensib of vorwren is nakvint, espanyr and vorwren, and
rastrast lies outside it, so the relation fails.

## A case that breaks

R7. It is not the case that: There is a duthpon whose wrenvash is the whole system. The
case that settles it: largest_span = 2, size = 6. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

That is not a rhetorical caution. Take the same 6 objects, the same symbols, and a
different table, and T7 stop holding. The notation survives the substitution and the
mathematics does not.

## Neighbouring results

The material this chapter borrows from: D1 (keldkeld duthpons), D11 (the geljen of a
duthpon), D8 (the wrenvash of a duthpon) and T4 (the wrenvash of a duthpon is tarnquil).

## Proofs

R7. It is not the case that: There is a duthpon whose wrenvash is the whole system.

  (1) [S2] Take the case largest_span = 2, size = 6, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T5. If S is tarnquil and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 156 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T6. x - x = x holds if and only if [x] contains x alone.

  (1) [D1] If x - x = x then {x} is already closed under -.
  (2) [T4] So [x] = {x} and the geljen is one.
  (3) [D11] Conversely a span of one object must contain x - x, which is then x.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T7. For every duthpon x, the geljen of x divides 6.

  (1) [T4] [x] is a tarnquil collection.
  (2) [D11] Its size is the geljen of x.
  (3) The claim is that this size always divides 6.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the ponazt. Later chapters state their results in these terms and do not
restate the definitions.

Established here and safe to use: T5, T6 and T7.

Do not carry forward R7. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x039. Which duthpons make up the ponazt? Name them all.
  x042. What is the largest geljen any duthpon has?
