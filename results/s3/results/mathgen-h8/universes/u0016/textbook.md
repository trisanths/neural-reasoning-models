# The Glimzam system

The Glimzam system is small enough to hold in the hand and strange enough to be worth
the trouble. It has 4 mornglims, one operation, and one relation, and nothing else.

The mornglims are written oviazt, kapon, nyrrast and xilwren. The first operation is
written |. The relation is written <~; where it holds between two mornglims we say the
left one dominates the right one. Both operations associate to the left when written
without brackets, and brackets override that. Repeated combination is abbreviated: x^3
means x | x | x.

A warning that will be repeated because it is the one readers ignore: nothing here is
inherited from arithmetic. Familiar names have been avoided on purpose. Where a law of
arithmetic happens to hold it is stated and checked, and where it fails a counterexample
is given.

# Chapter 1. The objects and their notation

## Why this chapter

The present chapter develops the Glimzam signature, the Glimzam combination tables and
closure under the first operation.

One habit to adopt: when a statement below quantifies over mornglims, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## The tables in full

The table for |. Read the left argument down the side and the right argument across the top.

         |   oviazt    kapon  nyrrast  xilwren
----------------------------------------------
  oviazt |   oviazt    kapon  nyrrast  xilwren
   kapon |    kapon    kapon  xilwren  xilwren
 nyrrast |  nyrrast  xilwren  nyrrast  xilwren
 xilwren |  xilwren  xilwren  xilwren  xilwren

Every pair standing in the <~ relation, grouped by left argument.

  oviazt <~ oviazt, kapon, nyrrast and xilwren
  kapon <~ kapon and xilwren
  nyrrast <~ nyrrast and xilwren
  xilwren <~ xilwren

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A1. Closure under the first operation. For all mornglims x and y, x | y is again a
mornglim.

A2. Association of the first operation. For all mornglims x, y, z: (x | y) | z = x | (y
| z).

A3. Commutation of the first operation. For all mornglims x and y: x | y = y | x.

A5. Self combination under the first operation. For every mornglim x: x | x = x.

## The shape of it

A useful mental split: some mornglims are inert under the operation and some are not.
oviazt, kapon, nyrrast and xilwren come back unchanged when combined with themselves,
and oviazt, kapon, nyrrast and xilwren commute with everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 mornglims the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R2 rests on S2 (the Glimzam combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Here is (kapon | nyrrast) | xilwren, reduced without skipping anything.
    kapon | nyrrast = xilwren   (the table for |)
    xilwren | xilwren = xilwren   (the table for |)
The expression comes to xilwren.

Move the brackets and the work changes. Take nyrrast | (xilwren | kapon).
    xilwren | kapon = xilwren   (the table for |)
    nyrrast | xilwren = xilwren   (the table for |)
That gives xilwren, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
oviazt <~ kapon hold? Read off what oviazt stands over: oviazt, kapon, nyrrast and
xilwren. kapon is among them, so it holds.

## A case that breaks

R2. It is not the case that: For all mornglims x, y, z: if x | y = x | z then y = z. The
case that settles it: x = kapon, y = oviazt, z = kapon. Anyone carrying this claim over
from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

What is built on it later: A4 (a neutral object for the first operation), A6 (an
absorbing object for the first operation), A7 (reflexivity of the relation) and A8
(antisymmetry of the relation).

## Proofs

R2. It is not the case that: For all mornglims x, y, z: if x | y = x | z then y = z.

  (1) [S2] Take the case x = kapon, y = oviazt, z = kapon, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R2. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 1.
  x001. Reduce kapon | nyrrast to a single mornglim.
Level 2.
  x003. Which mornglims x satisfy x | nyrrast = xilwren? List them all.
  x004. Solve x | nyrrast = nyrrast for x, naming every solution.
  x005. Solve x | kapon = kapon for x, naming every solution.
  x006. Which mornglims x satisfy x | xilwren = xilwren? List them all.
Level 3.
  x002. Work out the value of (nyrrast | kapon) | (nyrrast | kapon).
Level 5.
  x008. The following fails in this system: For all mornglims x, y, z: if x | y = x | z then y = z. Name the earliest mornglim, in the order the mornglims were introduced, that witnesses the failure.

# Chapter 2. Neutral objects and reversal

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is a neutral object
for the first operation, an absorbing object for the first operation and the system does
not have reversal under the first operation.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about mornglims covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A4. A neutral object for the first operation. There is a mornglim oviazt with oviazt | x
= x | oviazt = x for every x.

A6. An absorbing object for the first operation. There is a mornglim xilwren with
xilwren | x = x | xilwren = xilwren for every x.

## The shape of it

The neutral mornglim oviazt is the one that does nothing. That sounds trivial and is
not: almost every result in this chapter is an argument about what doing nothing forces.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 mornglims the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R1 rests on S2 (the Glimzam combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Evaluate (nyrrast | oviazt) | (kapon | xilwren). Each line below is one lookup in a
table.
    nyrrast | oviazt = nyrrast   (the table for |)
    kapon | xilwren = xilwren   (the table for |)
    nyrrast | xilwren = xilwren   (the table for |)
So (nyrrast | oviazt) | (kapon | xilwren) is xilwren.

Move the brackets and the work changes. Take oviazt | (kapon | nyrrast).
    kapon | nyrrast = xilwren   (the table for |)
    oviazt | xilwren = xilwren   (the table for |)
That gives xilwren, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
xilwren <~ oviazt hold? Read off what xilwren stands over: xilwren. oviazt is not among
them, so it fails.

## A case that breaks

R1. Some mornglim x admits no mornglim y for which x | y and y | x both land on a
neutral object. It fails at x = kapon. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: S2 (the Glimzam combination tables).

What is built on it later: D5 (the vexbra) and T1 (the vexbra is the only one of its
kind).

## Proofs

R1. Some mornglim x admits no mornglim y for which x | y and y | x both land on a neutral object.

  (1) [S2] Take the case x = kapon, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R1. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 5.
  x007. The following fails in this system: Some mornglim x admits no mornglim y for which x | y and y | x both land on a neutral object. Name the earliest mornglim, in the order the mornglims were introduced, that witnesses the failure.

# Chapter 3. The relation and what it orders

## Why this chapter

The results collected here were not found in this order. Agreement of the relation with
the first operation, reflexivity of the relation and antisymmetry of the relation came
first, and the rest was assembled around that once the pattern was visible.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

One habit to adopt: when a statement below quantifies over mornglims, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A10. Agreement of the relation with the first operation. For all mornglims x, y, z: if x
<~ y then (z | x) <~ (z | y) and (x | z) <~ (y | z).

A7. Reflexivity of the relation. For every mornglim x: x <~ x.

A8. Antisymmetry of the relation. For all mornglims x and y: if x <~ y and y <~ x then x
= y.

A9. Transitivity of the relation. For all mornglims x, y, z: if x <~ y and y <~ z then x
<~ z.

D4. The nakhurn of a mornglim. The nakhurn of a mornglim x is the collection of
mornglims y for which x <~ y holds.

Worked out for each mornglim: oviazt to oviazt, kapon, nyrrast and xilwren; kapon to
kapon and xilwren; nyrrast to nyrrast and xilwren; xilwren to xilwren.

## The shape of it

The relation is easiest to see as a height. Each mornglim casts a nakhurn over what it
dominates, and the sizes of those shadows here are 1, 2 and 4. Sizes repeat, so the
objects do not line up in single file.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R3 rests on S2 (the Glimzam combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take (xilwren | oviazt) | kapon and work it out one step at a time.
    xilwren | oviazt = xilwren   (the table for |)
    xilwren | kapon = xilwren   (the table for |)
That leaves xilwren, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is oviazt | (kapon | xilwren) for contrast.
    kapon | xilwren = xilwren   (the table for |)
    oviazt | xilwren = xilwren   (the table for |)
That gives xilwren, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test oviazt <~ xilwren. The nakhurn of oviazt is oviazt, kapon, nyrrast and xilwren, and
xilwren lies inside it, so the relation holds.

## A case that breaks

R3. It is not the case that: For all mornglims x and y, at least one of x <~ y and y <~
x holds. It fails at x = kapon, y = nyrrast. One case is enough, and this is the
earliest one.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: S2 (the Glimzam combination tables).

What is built on it later: D9 (a duthvor), D13 (dripon pairs), T10 (nakhurns are nested
along the relation) and T11 (there is at most one duthvor).

## Proofs

R3. It is not the case that: For all mornglims x and y, at least one of x <~ y and y <~ x holds.

  (1) [S2] Take the case x = kapon, y = nyrrast, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the nakhurn of a mornglim. Later chapters state their results in these
terms and do not restate the definitions.

Explicitly not available: R3. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x013. Which mornglims y satisfy oviazt <~ y? Name them all.
  x014. List the nakhurn of kapon.
  x015. Which mornglims y satisfy nyrrast <~ y? Name them all.
Level 5.
  x009. The following fails in this system: For all mornglims x and y, at least one of x <~ y and y <~ x holds. Name the earliest mornglim, in the order the mornglims were introduced, that witnesses the failure.

# Chapter 4. Combining objects

## Why this chapter

Anyone using this system to keep track of something will meet iskzam mornglims,
mornglims that zelvex and the vexbra early, whether or not they go looking.

Prerequisites are real here: chapters 1 and 2 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over mornglims, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D1. Iskzam mornglims. A mornglim x is called iskzam when x | x = x.

In this system that picks out oviazt, kapon, nyrrast and xilwren, that is, all of them.

D2. Mornglims that zelvex. Two mornglims x and y are said to zelvex when x | y = y | x.

D5. The vexbra. The mornglim oviazt is called the vexbra of the system. It is the unique
mornglim that leaves every mornglim unchanged under |.

Here that is oviazt.

## The shape of it

A useful mental split: some mornglims are inert under the operation and some are not.
oviazt, kapon, nyrrast and xilwren come back unchanged when combined with themselves,
and oviazt, kapon, nyrrast and xilwren commute with everything.

The neutral mornglim oviazt is the one that does nothing. That sounds trivial and is
not: almost every result in this chapter is an argument about what doing nothing forces.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 mornglims the table is short enough to consult every time.

## Where these results come from

This chapter is groundwork. The derivations that use it start in the next one.

## A worked case

Take (xilwren | nyrrast) | (oviazt | kapon) and work it out one step at a time.
    xilwren | nyrrast = xilwren   (the table for |)
    oviazt | kapon = kapon   (the table for |)
    xilwren | kapon = xilwren   (the table for |)
That leaves xilwren, and no other reading of the notation gives anything else.

A companion case, nyrrast | (oviazt | xilwren), to show what the brackets are doing.
    oviazt | xilwren = xilwren   (the table for |)
    nyrrast | xilwren = xilwren   (the table for |)
The value is xilwren. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test kapon <~ xilwren. The nakhurn of kapon is kapon and xilwren, and xilwren lies
inside it, so the relation holds.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of mornglims that come back
unchanged from themselves: oviazt, kapon, nyrrast and xilwren. Assuming more of them
than that is the mistake to avoid.

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

These results are used again in D6 (the falespa), D7 (the xilka), D10 (rastshen
mornglims) and T1 (the vexbra is the only one of its kind).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

New vocabulary from this chapter: iskzam mornglims, mornglims that zelvex and the
vexbra. Each of these is used by name later, so the names are worth learning rather than
looking up.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 2.
  x016. Name the vexbra of the system.
Level 3.
  x010. Which mornglims make up the iskzam? Name them all.

# Chapter 5. The relation and what it orders (2)

## Why this chapter

So far the mornglims have been objects to be pushed around. This chapter starts asking
what they are like. We take up dripon pairs, tezdri collections and a duthvor.

Nothing here stands on its own. The arguments lean on chapters 1 and 3, and a reader who
has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
mornglims that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D13. Dripon pairs. Two distinct mornglims x and y form a dripon pair when x <~ y and y
<~ x both hold, that is, when each lies in the nakhurn of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D3. Tezdri collections. A collection S of mornglims is tezdri when x | y belongs to S
for every pair x, y drawn from S.

D9. A duthvor. A mornglim f is a duthvor when f <~ y holds for every mornglim y, that
is, when the nakhurn of f is the whole system.

Running the definition over every mornglim leaves oviazt.

## The shape of it

Picture the clobra as what happens when you start with one mornglim and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 4 mornglims, that stops. In this system the sizes it stops at are 1.

The relation is easiest to see as a height. Each mornglim casts a nakhurn over what it
dominates, and the sizes of those shadows here are 1, 2 and 4. Sizes repeat, so the
objects do not line up in single file.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R5 rests on D4 (the nakhurn of a mornglim). The dependence is on the content of those
results, not only on their vocabulary.

T10 rests on D4 (the nakhurn of a mornglim) and A9 (transitivity of the relation). The
dependence is on the content of those results, not only on their vocabulary.

T12 rests on D4 (the nakhurn of a mornglim) and A10 (agreement of the relation with the
first operation). Remove any one of them and the statement stops making sense, not
merely stops being provable.

## A worked case

Here is (kapon | oviazt) | nyrrast, reduced without skipping anything.
    kapon | oviazt = kapon   (the table for |)
    kapon | nyrrast = xilwren   (the table for |)
So (kapon | oviazt) | nyrrast is xilwren.

Bracketing is not cosmetic, so here is oviazt | (nyrrast | kapon) for contrast.
    nyrrast | kapon = xilwren   (the table for |)
    oviazt | xilwren = xilwren   (the table for |)
The value is xilwren. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
xilwren <~ kapon hold? Read off what xilwren stands over: xilwren. kapon is not among
them, so it fails.

## A case that breaks

R5. It is not the case that: If x <~ y then y <~ x. It fails at x = oviazt, y = kapon.
One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of agreement of the relation with the first
operation, closure under the first operation and transitivity of the relation. Those are
properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A1 (closure under the first operation), A10
(agreement of the relation with the first operation), A9 (transitivity of the relation)
and D4 (the nakhurn of a mornglim).

What is built on it later: D8 (the clobra of a mornglim), T3 (the falespa is tezdri), T4
(the clobra of a mornglim is tezdri) and T9 (the xilka is tezdri).

## Proofs

R5. It is not the case that: If x <~ y then y <~ x.

  (1) [S2] Take the case x = oviazt, y = kapon, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 16 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T10. If y lies in the nakhurn of x, then the nakhurn of y is contained in the nakhurn of x.

  (1) [D4] Let y satisfy x <~ y and let z satisfy y <~ z.
  (2) [A9] Transitivity gives x <~ z.
  (3) [D4] So every member of the nakhurn of y is a member of that of x.

Checked over 64 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T12. If x <~ y then (x | z) <~ (y | z) for every mornglim z.

  (1) [D4] Let y lie in the nakhurn of x.
  (2) [A10] Compatibility applies the operation to both sides at once.
  (3) Nothing else is needed, since z was arbitrary.

Checked over 64 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward dripon pairs, tezdri collections and a duthvor. Later chapters state their
results in these terms and do not restate the definitions.

Established here and safe to use: T10 and T12.

Explicitly not available: R5. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x011. How many mornglims lie in the smallest tezdri collection containing kapon?
  x012. How many mornglims lie in the smallest tezdri collection containing nyrrast?
Level 4.
  x018. List every mornglim in the duthvor.
  x029. The result above concerns nakhurns. List the nakhurn of oviazt.
  x030. The result above concerns nakhurns. List the nakhurn of kapon.
  x031. The result above concerns nakhurns. List the nakhurn of nyrrast.
Level 5.
  x033. The following fails in this system: If x <~ y then y <~ x. Name the earliest mornglim, in the order the mornglims were introduced, that witnesses the failure.

# Chapter 6. Neutral objects and reversal (2)

## Why this chapter

The present chapter develops rastshen mornglims, the falespa and the xilka.

Prerequisites are real here: chapters 2 and 4 supply the notions the statements below
are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
mornglims that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D10. Rastshen mornglims. A mornglim x is rastshen when x | x equals the vexbra.

In this system that picks out oviazt, which is 1 of the 4 mornglims.

D6. The falespa. The falespa of the system is the collection of mornglims that zelvex
with every mornglim.

Running the definition over every mornglim leaves oviazt, kapon, nyrrast and xilwren.

D7. The xilka. The xilka is the collection of all iskzam mornglims.

Running the definition over every mornglim leaves oviazt, kapon, nyrrast and xilwren.

## The shape of it

Two questions sort the mornglims quickly. Does combining a mornglim with itself change
it? For oviazt, kapon, nyrrast and xilwren it does not. Does it matter which side it
goes on? For oviazt, kapon, nyrrast and xilwren it does not.

The neutral mornglim oviazt is the one that does nothing. That sounds trivial and is
not: almost every result in this chapter is an argument about what doing nothing forces.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R6 rests on D5 (the vexbra). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T1 rests on D5 (the vexbra) and A4 (a neutral object for the first operation). The
dependence is on the content of those results, not only on their vocabulary.

## A worked case

Take (xilwren | nyrrast) | (oviazt | kapon) and work it out one step at a time.
    xilwren | nyrrast = xilwren   (the table for |)
    oviazt | kapon = kapon   (the table for |)
    xilwren | kapon = xilwren   (the table for |)
The expression comes to xilwren.

A companion case, nyrrast | (oviazt | xilwren), to show what the brackets are doing.
    oviazt | xilwren = xilwren   (the table for |)
    nyrrast | xilwren = xilwren   (the table for |)
That gives xilwren, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
oviazt <~ kapon hold? Read off what oviazt stands over: oviazt, kapon, nyrrast and
xilwren. kapon is among them, so it holds.

## A case that breaks

R6. It is not the case that: e | x equals the vexbra for every mornglim x. The case that
settles it: anchor = oviazt, x = kapon, value = kapon. Anyone carrying this claim over
from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by a neutral object for the first operation and closure under the
first operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A4 (a neutral object for the first operation), D1 (iskzam mornglims), D2
(mornglims that zelvex) and D5 (the vexbra).

What is built on it later: T2 (the vexbra lies in the falespa), T3 (the falespa is
tezdri), T8 (the clobra of a falespa mornglim stays in the falespa) and T9 (the xilka is
tezdri).

## Proofs

R6. It is not the case that: e | x equals the vexbra for every mornglim x.

  (1) [S2] Take the case anchor = oviazt, x = kapon, value = kapon, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 4 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T1. There is exactly one mornglim e with e | x = x | e = x for every mornglim x.

  (1) [D5] Suppose e and f both leave every mornglim unchanged.
  (2) [A4] Then e | f = f, reading e as neutral on the left.
  (3) [A4] And e | f = e, reading f as neutral on the right.
  (4) So e = f, and the two suppositions describe the same object.

Checked over 16 cases: every object paired with every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward rastshen mornglims, the falespa and the xilka. Later chapters state their
results in these terms and do not restate the definitions.

Established here and safe to use: T1.

Do not carry forward R6. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x017. List every mornglim in the xilka.
  x019. Which mornglims make up the rastshen? Name them all.
Level 5.
  x034. The following fails in this system: e | x equals the vexbra for every mornglim x. Name the earliest mornglim, in the order the mornglims were introduced, that witnesses the failure.

# Chapter 7. The relation and what it orders (3)

## Why this chapter

Work through this chapter with the tables in front of you. It covers the clobra of a
mornglim, there is at most one duthvor and no dripon pairs exist, and each claim can be
checked by hand.

Prerequisites are real here: chapters 3 and 5 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over mornglims, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D8. The clobra of a mornglim. The clobra of a mornglim x, written [x], is the smallest
tezdri collection that contains x.

Worked out for each mornglim: oviazt to oviazt; kapon to kapon; nyrrast to nyrrast;
xilwren to xilwren.

## The shape of it

Picture the clobra as what happens when you start with one mornglim and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 4 mornglims, that stops. In this system the sizes it stops at are 1.

Think of <~ as pointing downhill. The nakhurn of a mornglim is everything downhill of
it, and those shadows here have sizes 1, 2 and 4.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T11 rests on D9 (a duthvor) and A8 (antisymmetry of the relation). The dependence is on
the content of those results, not only on their vocabulary.

T13 rests on D13 (dripon pairs) and A8 (antisymmetry of the relation). Remove any one of
them and the statement stops making sense, not merely stops being provable.

## A worked case

Evaluate (kapon | oviazt) | nyrrast. Each line below is one lookup in a table.
    kapon | oviazt = kapon   (the table for |)
    kapon | nyrrast = xilwren   (the table for |)
The expression comes to xilwren.

A companion case, oviazt | (nyrrast | kapon), to show what the brackets are doing.
    nyrrast | kapon = xilwren   (the table for |)
    oviazt | xilwren = xilwren   (the table for |)
The value is xilwren. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test xilwren <~ nyrrast. The nakhurn of xilwren is xilwren, and nyrrast lies outside it,
so the relation fails.

A second case, this time a clobra. Start from nyrrast. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is nyrrast, so the
nakdri of nyrrast is 1.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by antisymmetry of the relation and closure under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

To see how little the notation guarantees: rebuild the system with the same names over
different tables and T11 and T13 fail outright.

## Neighbouring results

Read alongside A8 (antisymmetry of the relation), D13 (dripon pairs), D3 (tezdri
collections) and D9 (a duthvor).

These results are used again in D11 (the nakdri of a mornglim), T4 (the clobra of a
mornglim is tezdri), T5 (the clobra is contained in every tezdri collection) and T8 (the
clobra of a falespa mornglim stays in the falespa).

## Proofs

T11. No two distinct mornglims can both be duthvors.

  (1) [D9] Let f and h both be floors.
  (2) [D9] Then f <~ h, since h is any object, and h <~ f likewise.
  (3) [A8] Antisymmetry forces f = h.

Checked over 16 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T13. No two distinct mornglims lie in each other's nakhurn.

  (1) [D13] Suppose x and y form a tight pair.
  (2) [A8] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 16 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the clobra of a mornglim. Later chapters state their results in these
terms and do not restate the definitions.

The results now available are T11 and T13, each settled by exhaustive check rather than
by argument from analogy.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x032. This result is about the duthvor. List every mornglim in it.

# Chapter 8. Combining objects (2)

## Why this chapter

What follows was pieced together backwards. The last item of it, every mornglim lies in
the falespa, every mornglim is iskzam and the vexbra lies in the falespa, was noticed
before anyone had a reason to expect it.

Prerequisites are real here: chapters 1, 4, 5 and 6 supply the notions the statements
below are phrased in.

The standard of proof here is exhaustion. A universal claim about mornglims covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

A useful mental split: some mornglims are inert under the operation and some are not.
oviazt, kapon, nyrrast and xilwren come back unchanged when combined with themselves,
and oviazt, kapon, nyrrast and xilwren commute with everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 mornglims the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T14 rests on D6 (the falespa). The dependence is on the content of those results, not
only on their vocabulary.

T15 rests on D7 (the xilka). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T2 rests on D5 (the vexbra) and D6 (the falespa). The dependence is on the content of
those results, not only on their vocabulary.

T3 rests on D6 (the falespa), D3 (tezdri collections) and A2 (association of the first
operation). The dependence is on the content of those results, not only on their
vocabulary.

T9 rests on D7 (the xilka) and D3 (tezdri collections). The dependence is on the content
of those results, not only on their vocabulary.

## A worked case

Here is (kapon | xilwren) | (nyrrast | oviazt), reduced without skipping anything.
    kapon | xilwren = xilwren   (the table for |)
    nyrrast | oviazt = nyrrast   (the table for |)
    xilwren | nyrrast = xilwren   (the table for |)
So (kapon | xilwren) | (nyrrast | oviazt) is xilwren.

A companion case, xilwren | (nyrrast | kapon), to show what the brackets are doing.
    nyrrast | kapon = xilwren   (the table for |)
    xilwren | xilwren = xilwren   (the table for |)
That gives xilwren, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test kapon <~ xilwren. The nakhurn of kapon is kapon and xilwren, and xilwren lies
inside it, so the relation holds.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of mornglims that come back
unchanged from themselves: oviazt, kapon, nyrrast and xilwren. Assuming more of them
than that is the mistake to avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation and closure under the first operation. Those are
properties of this system, not of systems in general.

That is not a rhetorical caution. Take the same 4 objects, the same symbols, and a
different table, and T15 stop holding. The notation survives the substitution and the
mathematics does not.

## Neighbouring results

The material this chapter borrows from: A2 (association of the first operation), D3
(tezdri collections), D5 (the vexbra) and D6 (the falespa).

These results are used again in T8 (the clobra of a falespa mornglim stays in the
falespa).

## Proofs

T14. Every pair of mornglims zelvexs.

  (1) [D6] The falespa is defined by zelvexing with everything.
  (2) [D2] The claim is that x | y = y | x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 16 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T15. x | x = x for every mornglim x.

  (1) [D1] Being iskzam is the condition x | x = x.
  (2) [D7] The claim is that the xilka is the whole system.
  (3) Only the diagonal of the table is involved.

Checked over 4 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T2. The vexbra zelvexs with every mornglim.

  (1) [D5] Let e be the vexbra and x any mornglim.
  (2) [D5] Then e | x = x and x | e = x.
  (3) [D2] So e | x = x | e, which is what it means to zelvex.
  (4) [D6] Since x was arbitrary, e belongs to the falespa.

Checked over 4 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. If x and y both zelvex with every mornglim, then so does x | y.

  (1) [D6] Let x and y lie in the falespa and let z be any mornglim.
  (2) [A2] Then (x | y) | z = x | (y | z).
  (3) [D6] Move z past y, then past x, using that each zelvexs with everything.
  (4) [D3] So x | y zelvexs with z, and the falespa is tezdri.

Checked over 16 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

T9. If x and y are both iskzam then so is x | y.

  (1) [D7] Let x and y be iskzam.
  (2) [D1] The claim asks whether (x | y) | (x | y) returns x | y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 16 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Established here and safe to use: T14, T15, T2, T3 and T9.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x028. This result is about the xilka. List every mornglim in it.

# Chapter 9. Collections that close on themselves

## Why this chapter

The practical content of this chapter is the nakdri of a mornglim, the clobra of a
mornglim is tezdri and the clobra of a falespa mornglim stays in the falespa. It is the
part that shows up in use.

Nothing here stands on its own. The arguments lean on chapters 5, 6, 7 and 8, and a
reader who has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over mornglims, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D11. The nakdri of a mornglim. The nakdri of a mornglim x is the number of mornglims in
its clobra [x].

Worked out for each mornglim: oviazt to 1; kapon to 1; nyrrast to 1; xilwren to 1.

## The shape of it

Picture the clobra as what happens when you start with one mornglim and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 4 mornglims, that stops. In this system the sizes it stops at are 1.

Two questions sort the mornglims quickly. Does combining a mornglim with itself change
it? For oviazt, kapon, nyrrast and xilwren it does not. Does it matter which side it
goes on? For oviazt, kapon, nyrrast and xilwren it does not.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 mornglims the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T4 rests on D8 (the clobra of a mornglim) and D3 (tezdri collections). Remove any one of
them and the statement stops making sense, not merely stops being provable.

T8 rests on D8 (the clobra of a mornglim), D6 (the falespa) and T3 (the falespa is
tezdri). Remove any one of them and the statement stops making sense, not merely stops
being provable.

## A worked case

Here is (xilwren | nyrrast) | oviazt, reduced without skipping anything.
    xilwren | nyrrast = xilwren   (the table for |)
    xilwren | oviazt = xilwren   (the table for |)
That leaves xilwren, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take nyrrast | (oviazt | xilwren).
    oviazt | xilwren = xilwren   (the table for |)
    nyrrast | xilwren = xilwren   (the table for |)
That gives xilwren, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test oviazt <~ oviazt. The nakhurn of oviazt is oviazt, kapon, nyrrast and xilwren, and
oviazt lies inside it, so the relation holds.

A second case, this time a clobra. Start from nyrrast. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is nyrrast, so the
nakdri of nyrrast is 1.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by association of the first operation and closure under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: D3 (tezdri collections), D6 (the falespa), D8
(the clobra of a mornglim) and T3 (the falespa is tezdri).

These results are used again in D12 (the grixvor), T5 (the clobra is contained in every
tezdri collection), T6 (a mornglim is iskzam exactly when its nakdri is one) and T7 (the
nakdri divides the number of mornglims).

## Proofs

T4. For every mornglim x, the collection [x] is tezdri.

  (1) [D8] [x] is built by taking x and closing under |.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 64 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

T8. If x lies in the falespa then every mornglim of [x] lies in the falespa.

  (1) [T3] The falespa is tezdri.
  (2) [D8] [x] is the smallest tezdri collection containing x.
  (3) A smallest such collection sits inside any other, and the falespa is one.

Checked over 16 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the nakdri of a mornglim. Later chapters state their results in these
terms and do not restate the definitions.

Established here and safe to use: T4 and T8.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x020. What is the nakdri of kapon?
  x021. How many mornglims lie in [nyrrast]?
  x022. How many mornglims lie in [xilwren]?
Level 5.
  x023. Let z be (xilwren | xilwren) | xilwren. What is the nakdri of z?
  x024. Let z be (xilwren | oviazt) | oviazt. What is the nakdri of z?
  x025. Let z be (kapon | oviazt) | oviazt. What is the nakdri of z?

# Chapter 10. Collections that close on themselves (2)

## Why this chapter

So far the mornglims have been objects to be pushed around. This chapter starts asking
what they are like. We take up the grixvor, where some mornglim reaches every other
breaks down and the clobra is contained in every tezdri collection.

Nothing here stands on its own. The arguments lean on chapters 4, 7 and 9, and a reader
who has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
mornglims that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D12. The grixvor. The grixvor of the system is the collection of mornglims whose nakdri
is largest.

Running the definition over every mornglim leaves oviazt, kapon, nyrrast and xilwren.

## The shape of it

The right picture for clobra is a spreading stain rather than a list. Drop one mornglim
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 mornglims
depending on where it started.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R4 rests on D8 (the clobra of a mornglim) and D11 (the nakdri of a mornglim). The
dependence is on the content of those results, not only on their vocabulary.

T5 rests on D8 (the clobra of a mornglim) and T4 (the clobra of a mornglim is tezdri).
The dependence is on the content of those results, not only on their vocabulary.

T6 rests on D1 (iskzam mornglims), D11 (the nakdri of a mornglim) and T4 (the clobra of
a mornglim is tezdri). Remove any one of them and the statement stops making sense, not
merely stops being provable.

T7 rests on D11 (the nakdri of a mornglim) and T4 (the clobra of a mornglim is tezdri).
The dependence is on the content of those results, not only on their vocabulary.

## A worked case

Evaluate (oviazt | nyrrast) | (kapon | xilwren). Each line below is one lookup in a
table.
    oviazt | nyrrast = nyrrast   (the table for |)
    kapon | xilwren = xilwren   (the table for |)
    nyrrast | xilwren = xilwren   (the table for |)
That leaves xilwren, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is nyrrast | (kapon | oviazt) for contrast.
    kapon | oviazt = kapon   (the table for |)
    nyrrast | kapon = xilwren   (the table for |)
The value is xilwren. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
oviazt <~ oviazt hold? Read off what oviazt stands over: oviazt, kapon, nyrrast and
xilwren. oviazt is among them, so it holds.

## A case that breaks

R4. It is not the case that: There is a mornglim whose clobra is the whole system. The
case that settles it: largest_span = 1, size = 4. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by closure under the first operation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside D1 (iskzam mornglims), D11 (the nakdri of a mornglim), D8 (the clobra of
a mornglim) and T4 (the clobra of a mornglim is tezdri).

## Proofs

R4. It is not the case that: There is a mornglim whose clobra is the whole system.

  (1) [S2] Take the case largest_span = 1, size = 4, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 4 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T5. If S is tezdri and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 52 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T6. x | x = x holds if and only if [x] contains x alone.

  (1) [D1] If x | x = x then {x} is already closed under |.
  (2) [T4] So [x] = {x} and the nakdri is one.
  (3) [D11] Conversely a span of one object must contain x | x, which is then x.

Checked over 4 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T7. For every mornglim x, the nakdri of x divides 4.

  (1) [T4] [x] is a tezdri collection.
  (2) [D11] Its size is the nakdri of x.
  (3) The claim is that this size always divides 4.

Checked over 4 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the grixvor. Later chapters state their results in these terms and do not
restate the definitions.

Established here and safe to use: T5, T6 and T7.

Do not carry forward R4. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x026. List every mornglim in the grixvor.
  x027. What is the largest nakdri any mornglim has?
