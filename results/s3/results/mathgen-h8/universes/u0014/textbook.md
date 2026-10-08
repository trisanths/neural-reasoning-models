# The Quilumb system

This book is about qenjens. A qenjen is not a number and not a set; it is one of exactly
5 objects, and everything said here is said about how those 5 objects combine.

The qenjens are written yuktarn, xilzam, shentu, nyrazt and cloreld. The first operation
is written +. The second is written |= and binds more tightly, so x + y |= z means x +
(y |= z). The relation is written <~; where it holds between two qenjens we say the left
one answers to the right one. Both operations associate to the left when written without
brackets, and brackets override that. Repeated combination is abbreviated: x^3 means x +
x + x.

Readers arriving from arithmetic should put it down at the door. The operations below
are defined by their tables and by nothing else. Several arithmetic habits survive the
crossing and several do not, and the text is careful to say which is which.

# Chapter 1. The objects and their notation

## Why this chapter

Anyone using this system to keep track of something will meet the Quilumb signature, the
Quilumb combination tables and closure under the first operation early, whether or not
they go looking.

The standard of proof here is exhaustion. A universal claim about qenjens covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## The tables in full

The table for +. Read the left argument down the side and the right argument across the top.

         |  yuktarn   xilzam   shentu   nyrazt  cloreld
-------------------------------------------------------
 yuktarn |  yuktarn  yuktarn  yuktarn  yuktarn  yuktarn
  xilzam |  yuktarn   xilzam   shentu   nyrazt  cloreld
  shentu |  yuktarn   shentu  cloreld   xilzam   nyrazt
  nyrazt |  yuktarn   nyrazt   xilzam  cloreld   shentu
 cloreld |  yuktarn  cloreld   nyrazt   shentu   xilzam

The table for |=. Read the left argument down the side and the right argument across the top.

         |  yuktarn   xilzam   shentu   nyrazt  cloreld
-------------------------------------------------------
 yuktarn |  yuktarn  yuktarn  yuktarn  yuktarn  yuktarn
  xilzam |  yuktarn   xilzam   xilzam   xilzam   xilzam
  shentu |  yuktarn   xilzam   shentu   shentu   shentu
  nyrazt |  yuktarn   xilzam   shentu   nyrazt   nyrazt
 cloreld |  yuktarn   xilzam   shentu   nyrazt  cloreld

Every pair standing in the <~ relation, grouped by left argument.

  yuktarn <~ yuktarn, xilzam, shentu, nyrazt and cloreld
  xilzam <~ xilzam, shentu, nyrazt and cloreld
  shentu <~ shentu, nyrazt and cloreld
  nyrazt <~ nyrazt and cloreld
  cloreld <~ cloreld

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A1. Closure under the first operation. For all qenjens x and y, x + y is again a qenjen.

A2. Association of the first operation. For all qenjens x, y, z: (x + y) + z = x + (y +
z).

A3. Commutation of the first operation. For all qenjens x and y: x + y = y + x.

## The shape of it

Two questions sort the qenjens quickly. Does combining a qenjen with itself change it?
For yuktarn and xilzam it does not. Does it matter which side it goes on? For yuktarn,
xilzam, shentu, nyrazt and cloreld it does not.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R2 rests on S2 (the Quilumb combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R3 rests on S2 (the Quilumb combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take shentu + nyrazt |= xilzam and work it out one step at a time.
    nyrazt |= xilzam = xilzam   (the table for |=)
    shentu + xilzam = shentu   (the table for +)
That leaves shentu, and no other reading of the notation gives anything else.

A companion case, nyrazt + (xilzam + shentu), to show what the brackets are doing.
    xilzam + shentu = shentu   (the table for +)
    nyrazt + shentu = xilzam   (the table for +)
The value is xilzam, not shentu.

One decision about the relation, since deciding is as much a skill as computing. Does
shentu <~ cloreld hold? Read off what shentu stands over: shentu, nyrazt and cloreld.
cloreld is among them, so it holds.

## A case that breaks

R2. It is not the case that: For every qenjen x: x + x = x. It fails at x = shentu,
value = cloreld. One case is enough, and this is the earliest one.

R3. It is not the case that: For all qenjens x, y, z: if x + y = x + z then y = z. The
case that settles it: x = yuktarn, y = yuktarn, z = xilzam. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

What is built on it later: A4 (a neutral object for the first operation), A5 (an
absorbing object for the first operation), A6 (closure under the second operation) and
A7 (association of the second operation).

## Proofs

R2. It is not the case that: For every qenjen x: x + x = x.

  (1) [S2] Take the case x = shentu, value = cloreld, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R3. It is not the case that: For all qenjens x, y, z: if x + y = x + z then y = z.

  (1) [S2] Take the case x = yuktarn, y = yuktarn, z = xilzam, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R2 and R3. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 1.
  x001. Work out the value of nyrazt + nyrazt.
  x002. Evaluate nyrazt + cloreld.
  x003. What qenjen does shentu + cloreld name?
Level 2.
  x004. Evaluate cloreld^2.
  x005. What is nyrazt combined with itself 3 times under +?
  x006. Which qenjens x satisfy x + yuktarn = yuktarn? List them all.
Level 5.
  x008. The following fails in this system: For every qenjen x: x + x = x. Name the earliest qenjen, in the order the qenjens were introduced, that witnesses the failure.
  x009. The following fails in this system: For all qenjens x, y, z: if x + y = x + z then y = z. Name the earliest qenjen, in the order the qenjens were introduced, that witnesses the failure.

# Chapter 2. Neutral objects and reversal

## Why this chapter

So far the qenjens have been objects to be pushed around. This chapter starts asking
what they are like. We take up a neutral object for the first operation, an absorbing
object for the first operation and the system does not have reversal under the first
operation.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
qenjens that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A4. A neutral object for the first operation. There is a qenjen xilzam with xilzam + x =
x + xilzam = x for every x.

A5. An absorbing object for the first operation. There is a qenjen yuktarn with yuktarn
+ x = x + yuktarn = yuktarn for every x.

## The shape of it

The neutral qenjen xilzam is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 qenjens the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R1 rests on S2 (the Quilumb combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Here is (shentu + xilzam) + (cloreld + yuktarn), reduced without skipping anything.
    shentu + xilzam = shentu   (the table for +)
    cloreld + yuktarn = yuktarn   (the table for +)
    shentu + yuktarn = yuktarn   (the table for +)
That leaves yuktarn, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is xilzam + (cloreld + shentu) for contrast.
    cloreld + shentu = nyrazt   (the table for +)
    xilzam + nyrazt = nyrazt   (the table for +)
The value is nyrazt, not yuktarn.

One decision about the relation, since deciding is as much a skill as computing. Does
nyrazt <~ cloreld hold? Read off what nyrazt stands over: nyrazt and cloreld. cloreld is
among them, so it holds.

## A case that breaks

R1. Some qenjen x admits no qenjen y for which x + y and y + x both land on a neutral
object. It fails at x = yuktarn. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside S2 (the Quilumb combination tables).

What is built on it later: D5 (the mithra) and T1 (the mithra is the only one of its
kind).

## Proofs

R1. Some qenjen x admits no qenjen y for which x + y and y + x both land on a neutral object.

  (1) [S2] Take the case x = yuktarn, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R1. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 5.
  x007. The following fails in this system: Some qenjen x admits no qenjen y for which x + y and y + x both land on a neutral object. Name the earliest qenjen, in the order the qenjens were introduced, that witnesses the failure.

# Chapter 3. The relation and what it orders

## Why this chapter

The present chapter develops reflexivity of the relation, antisymmetry of the relation
and transitivity of the relation.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over qenjens, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A11. Reflexivity of the relation. For every qenjen x: x <~ x.

A12. Antisymmetry of the relation. For all qenjens x and y: if x <~ y and y <~ x then x
= y.

A13. Transitivity of the relation. For all qenjens x, y, z: if x <~ y and y <~ z then x
<~ z.

A14. Comparability of every pair. For all qenjens x and y, at least one of x <~ y and y
<~ x holds.

A15. Agreement of the relation with the second operation. For all qenjens x, y, z: if x
<~ y then (z |= x) <~ (z |= y) and (x |= z) <~ (y |= z).

D4. The opalglim of a qenjen. The opalglim of a qenjen x is the collection of qenjens y
for which x <~ y holds.

Worked out for each qenjen: yuktarn to yuktarn, xilzam, shentu, nyrazt and cloreld;
xilzam to xilzam, shentu, nyrazt and cloreld; shentu to shentu, nyrazt and cloreld;
nyrazt to nyrazt and cloreld; cloreld to cloreld.

## The shape of it

The relation is easiest to see as a height. Each qenjen casts a opalglim over what it
answers to, and the sizes of those shadows here are 1, 2, 3, 4 and 5. No two are the
same size, so the objects line up in a single file.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R6 rests on S2 (the Quilumb combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take nyrazt + cloreld |= shentu and work it out one step at a time.
    cloreld |= shentu = shentu   (the table for |=)
    nyrazt + shentu = xilzam   (the table for +)
That leaves xilzam, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is cloreld + (shentu + nyrazt) for contrast.
    shentu + nyrazt = xilzam   (the table for +)
    cloreld + xilzam = cloreld   (the table for +)
That gives cloreld, against xilzam above.

Test nyrazt <~ xilzam. The opalglim of nyrazt is nyrazt and cloreld, and xilzam lies
outside it, so the relation fails.

## A case that breaks

R6. It is not the case that: For all qenjens x, y, z: if x <~ y then (z + x) <~ (z + y)
and (x + z) <~ (y + z). It fails at x = xilzam, y = shentu, z = nyrazt, side = left. One
case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: S2 (the Quilumb combination tables).

What is built on it later: D9 (a tezwren), D13 (duthsib pairs), T9 (opalglims are nested
along the relation) and T10 (there is at most one tezwren).

## Proofs

R6. It is not the case that: For all qenjens x, y, z: if x <~ y then (z + x) <~ (z + y) and (x + z) <~ (y + z).

  (1) [S2] Take the case x = xilzam, y = shentu, z = nyrazt, side = left, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the opalglim of a qenjen. Later chapters state their results in these
terms and do not restate the definitions.

Explicitly not available: R6. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 5.
  x011. The following fails in this system: For all qenjens x, y, z: if x <~ y then (z + x) <~ (z + y) and (x + z) <~ (y + z). Name the earliest qenjen, in the order the qenjens were introduced, that witnesses the failure.

# Chapter 4. The second operation and how the two interact

## Why this chapter

Work through this chapter with the tables in front of you. It covers self combination
under the second operation, closure under the second operation and association of the
second operation, and each claim can be checked by hand.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

One habit to adopt: when a statement below quantifies over qenjens, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A10. Self combination under the second operation. For every qenjen x: x |= x = x.

A6. Closure under the second operation. For all qenjens x and y, x |= y is again a
qenjen.

A7. Association of the second operation. For all qenjens x, y, z: (x |= y) |= z = x |=
(y |= z).

A8. Commutation of the second operation. For all qenjens x and y: x |= y = y |= x.

A9. A neutral object for the second operation. There is a qenjen cloreld with cloreld |=
x = x for every x.

## The shape of it

The interesting content of a two operation system sits in the gap between them: which
one distributes over which, and which qenjens are fixed by both.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 qenjens the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R4 rests on S2 (the Quilumb combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R5 rests on S2 (the Quilumb combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Evaluate (nyrazt + shentu) + (cloreld + xilzam). Each line below is one lookup in a
table.
    nyrazt + shentu = xilzam   (the table for +)
    cloreld + xilzam = cloreld   (the table for +)
    xilzam + cloreld = cloreld   (the table for +)
That leaves cloreld, and no other reading of the notation gives anything else.

A companion case, shentu + (cloreld + nyrazt), to show what the brackets are doing.
    cloreld + nyrazt = shentu   (the table for +)
    shentu + shentu = cloreld   (the table for +)
The value is cloreld. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
cloreld <~ nyrazt hold? Read off what cloreld stands over: cloreld. nyrazt is not among
them, so it fails.

## A case that breaks

R4. It is not the case that: For all qenjens x, y, z: x |= (y + z) = (x |= y) + (x |=
z), and the same on the right. It fails at x = shentu, y = shentu, z = shentu, left =
shentu, right = cloreld. One case is enough, and this is the earliest one.

R5. It is not the case that: For all qenjens x and y: x + (x |= y) = x and x |= (x + y)
= x. It fails at x = xilzam, y = yuktarn, value = yuktarn. One case is enough, and this
is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: S2 (the Quilumb combination tables).

These results are used again in T14 (the second operation keeps the zammorn intact).

## Proofs

R4. It is not the case that: For all qenjens x, y, z: x |= (y + z) = (x |= y) + (x |= z), and the same on the right.

  (1) [S2] Take the case x = shentu, y = shentu, z = shentu, left = shentu, right = cloreld, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R5. It is not the case that: For all qenjens x and y: x + (x |= y) = x and x |= (x + y) = x.

  (1) [S2] Take the case x = xilzam, y = yuktarn, value = yuktarn, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R4 and R5. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 5.
  x010. The following fails in this system: For all qenjens x, y, z: x |= (y + z) = (x |= y) + (x |= z), and the same on the right. Name the earliest qenjen, in the order the qenjens were introduced, that witnesses the failure.

# Chapter 5. Combining objects

## Why this chapter

What follows was pieced together backwards. The last item of it, tufal qenjens, qenjens
that braumb and the mithra, was noticed before anyone had a reason to expect it.

Prerequisites are real here: chapters 1 and 2 supply the notions the statements below
are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
qenjens that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D1. Tufal qenjens. A qenjen x is called tufal when x + x = x.

In this system that picks out yuktarn and xilzam, which is 2 of the 5 qenjens.

D2. Qenjens that braumb. Two qenjens x and y are said to braumb when x + y = y + x.

D5. The mithra. The qenjen xilzam is called the mithra of the system. It is the unique
qenjen that leaves every qenjen unchanged under +.

Here that is xilzam.

## The shape of it

A useful mental split: some qenjens are inert under the operation and some are not.
yuktarn and xilzam come back unchanged when combined with themselves, and yuktarn,
xilzam, shentu, nyrazt and cloreld commute with everything.

Neutrality is a strong condition disguised as a weak one. It fixes a single qenjen and,
through that, constrains everything that can combine with it.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 qenjens the table is short enough to consult every time.

## Where these results come from

Nothing is derived in this chapter. It lays down material that later chapters draw on.

## A worked case

Here is cloreld + yuktarn |= shentu, reduced without skipping anything.
    yuktarn |= shentu = yuktarn   (the table for |=)
    cloreld + yuktarn = yuktarn   (the table for +)
The expression comes to yuktarn.

Bracketing is not cosmetic, so here is yuktarn + (shentu + cloreld) for contrast.
    shentu + cloreld = nyrazt   (the table for +)
    yuktarn + nyrazt = yuktarn   (the table for +)
That gives yuktarn, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
xilzam <~ cloreld hold? Read off what xilzam stands over: xilzam, shentu, nyrazt and
cloreld. cloreld is among them, so it holds.

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

These results are used again in D6 (the zammorn), D7 (the vexfex), D10 (glimclo qenjens)
and T1 (the mithra is the only one of its kind).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

Carry forward tufal qenjens, qenjens that braumb and the mithra. Later chapters state
their results in these terms and do not restate the definitions.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 2.
  x015. Which qenjen leaves every qenjen unchanged under +?
Level 3.
  x012. List every qenjen in the tufal.

# Chapter 6. The relation and what it orders (2)

## Why this chapter

Anyone using this system to keep track of something will meet duthsib pairs, rastdri
collections and a tezwren early, whether or not they go looking.

Prerequisites are real here: chapters 1 and 3 supply the notions the statements below
are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
qenjens that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D13. Duthsib pairs. Two distinct qenjens x and y form a duthsib pair when x <~ y and y
<~ x both hold, that is, when each lies in the opalglim of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D3. Rastdri collections. A collection S of qenjens is rastdri when x + y belongs to S
for every pair x, y drawn from S.

D9. A tezwren. A qenjen f is a tezwren when f <~ y holds for every qenjen y, that is,
when the opalglim of f is the whole system.

Running the definition over every qenjen leaves yuktarn.

## The shape of it

Picture the kaduth as what happens when you start with one qenjen and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 5 qenjens, that stops. In this system the sizes it stops at are 1, 2 and 4.

Think of <~ as pointing downhill. The opalglim of a qenjen is everything downhill of it,
and those shadows here have sizes 1, 2, 3, 4 and 5.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R10 rests on D4 (the opalglim of a qenjen). Remove any one of them and the statement
stops making sense, not merely stops being provable.

T9 rests on D4 (the opalglim of a qenjen) and A13 (transitivity of the relation). The
dependence is on the content of those results, not only on their vocabulary.

## A worked case

Take (xilzam + shentu) + (cloreld + nyrazt) and work it out one step at a time.
    xilzam + shentu = shentu   (the table for +)
    cloreld + nyrazt = shentu   (the table for +)
    shentu + shentu = cloreld   (the table for +)
So (xilzam + shentu) + (cloreld + nyrazt) is cloreld.

A companion case, shentu + (cloreld + xilzam), to show what the brackets are doing.
    cloreld + xilzam = cloreld   (the table for +)
    shentu + cloreld = nyrazt   (the table for +)
The value is nyrazt, not cloreld.

Test yuktarn <~ xilzam. The opalglim of yuktarn is yuktarn, xilzam, shentu, nyrazt and
cloreld, and xilzam lies inside it, so the relation holds.

## A case that breaks

R10. It is not the case that: If x <~ y then y <~ x. It fails at x = yuktarn, y =
xilzam. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by closure under the first operation and transitivity of the
relation. A system without them is not a system where these results are harder to prove;
it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A1 (closure under the first operation), A13 (transitivity of the
relation) and D4 (the opalglim of a qenjen).

These results are used again in D8 (the kaduth of a qenjen), T3 (the zammorn is
rastdri), T4 (the kaduth of a qenjen is rastdri) and T8 (the vexfex is rastdri).

## Proofs

R10. It is not the case that: If x <~ y then y <~ x.

  (1) [S2] Take the case x = yuktarn, y = xilzam, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T9. If y lies in the opalglim of x, then the opalglim of y is contained in the opalglim of x.

  (1) [D4] Let y satisfy x <~ y and let z satisfy y <~ z.
  (2) [A13] Transitivity gives x <~ z.
  (3) [D4] So every member of the opalglim of y is a member of that of x.

Checked over 125 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward duthsib pairs, rastdri collections and a tezwren. Later chapters state
their results in these terms and do not restate the definitions.

The results now available are T9, each settled by exhaustive check rather than by
argument from analogy.

Do not carry forward R10. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x013. How many qenjens lie in the smallest rastdri collection containing xilzam?
  x014. How many qenjens lie in the smallest rastdri collection containing shentu?

# Chapter 7. Neutral objects and reversal (2)

## Why this chapter

So far the qenjens have been objects to be pushed around. This chapter starts asking
what they are like. We take up glimclo qenjens, the zammorn and the vexfex.

Prerequisites are real here: chapters 2 and 5 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over qenjens, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D10. Glimclo qenjens. A qenjen x is glimclo when x + x equals the mithra.

In this system that picks out xilzam and cloreld, which is 2 of the 5 qenjens.

D6. The zammorn. The zammorn of the system is the collection of qenjens that braumb with
every qenjen.

In this system that picks out yuktarn, xilzam, shentu, nyrazt and cloreld, that is, all
of them.

D7. The vexfex. The vexfex is the collection of all tufal qenjens.

In this system that picks out yuktarn and xilzam, which is 2 of the 5 qenjens.

## The shape of it

A useful mental split: some qenjens are inert under the operation and some are not.
yuktarn and xilzam come back unchanged when combined with themselves, and yuktarn,
xilzam, shentu, nyrazt and cloreld commute with everything.

The neutral qenjen xilzam is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 qenjens the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R11 rests on D5 (the mithra). The dependence is on the content of those results, not
only on their vocabulary.

T1 rests on D5 (the mithra) and A4 (a neutral object for the first operation). The
dependence is on the content of those results, not only on their vocabulary.

## A worked case

Here is nyrazt + cloreld |= xilzam, reduced without skipping anything.
    cloreld |= xilzam = xilzam   (the table for |=)
    nyrazt + xilzam = nyrazt   (the table for +)
That leaves nyrazt, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is cloreld + (xilzam + nyrazt) for contrast.
    xilzam + nyrazt = nyrazt   (the table for +)
    cloreld + nyrazt = shentu   (the table for +)
The value is shentu, not nyrazt.

Test shentu <~ nyrazt. The opalglim of shentu is shentu, nyrazt and cloreld, and nyrazt
lies inside it, so the relation holds.

## A case that breaks

R11. It is not the case that: e + x equals the mithra for every qenjen x. The case that
settles it: anchor = xilzam, x = yuktarn, value = yuktarn. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by a neutral object for the first operation and closure under the
first operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A4 (a neutral object for the first operation), D1 (tufal qenjens), D2
(qenjens that braumb) and D5 (the mithra).

What is built on it later: T2 (the mithra lies in the zammorn), T3 (the zammorn is
rastdri), T7 (the kaduth of a zammorn qenjen stays in the zammorn) and T8 (the vexfex is
rastdri).

## Proofs

R11. It is not the case that: e + x equals the mithra for every qenjen x.

  (1) [S2] Take the case anchor = xilzam, x = yuktarn, value = yuktarn, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T1. There is exactly one qenjen e with e + x = x + e = x for every qenjen x.

  (1) [D5] Suppose e and f both leave every qenjen unchanged.
  (2) [A4] Then e + f = f, reading e as neutral on the left.
  (3) [A4] And e + f = e, reading f as neutral on the right.
  (4) So e = f, and the two suppositions describe the same object.

Checked over 25 cases: every object paired with every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward glimclo qenjens, the zammorn and the vexfex. Later chapters state their
results in these terms and do not restate the definitions.

The results now available are T1, each settled by exhaustive check rather than by
argument from analogy.

Do not carry forward R11. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x016. Write down the vexfex in full.
  x022. Which qenjens make up the glimclo? Name them all.
Level 5.
  x038. The following fails in this system: e + x equals the mithra for every qenjen x. Name the earliest qenjen, in the order the qenjens were introduced, that witnesses the failure.

# Chapter 8. The relation and what it orders (3)

## Why this chapter

The present chapter develops the kaduth of a qenjen, there is at most one tezwren and
the system has a tezwren.

Nothing here stands on its own. The arguments lean on chapters 3 and 6, and a reader who
has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over qenjens, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D8. The kaduth of a qenjen. The kaduth of a qenjen x, written [x], is the smallest
rastdri collection that contains x.

Worked out for each qenjen: yuktarn to yuktarn; xilzam to xilzam; shentu to xilzam,
shentu, nyrazt and cloreld; nyrazt to xilzam, shentu, nyrazt and cloreld; cloreld to
xilzam and cloreld.

## The shape of it

Picture the kaduth as what happens when you start with one qenjen and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 5 qenjens, that stops. In this system the sizes it stops at are 1, 2 and 4.

Think of <~ as pointing downhill. The opalglim of a qenjen is everything downhill of it,
and those shadows here have sizes 1, 2, 3, 4 and 5.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 qenjens the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T10 rests on D9 (a tezwren) and A12 (antisymmetry of the relation). The dependence is on
the content of those results, not only on their vocabulary.

T11 rests on D9 (a tezwren) and A14 (comparability of every pair). The dependence is on
the content of those results, not only on their vocabulary.

T12 rests on D13 (duthsib pairs) and A12 (antisymmetry of the relation). The dependence
is on the content of those results, not only on their vocabulary.

## A worked case

Evaluate (cloreld + nyrazt) + (shentu + xilzam). Each line below is one lookup in a
table.
    cloreld + nyrazt = shentu   (the table for +)
    shentu + xilzam = shentu   (the table for +)
    shentu + shentu = cloreld   (the table for +)
So (cloreld + nyrazt) + (shentu + xilzam) is cloreld.

A companion case, nyrazt + (shentu + cloreld), to show what the brackets are doing.
    shentu + cloreld = nyrazt   (the table for +)
    nyrazt + nyrazt = cloreld   (the table for +)
The value is cloreld. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
shentu <~ xilzam hold? Read off what shentu stands over: shentu, nyrazt and cloreld.
xilzam is not among them, so it fails.

A second case, this time a kaduth. Start from yuktarn. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is yuktarn, so the
korrgel of yuktarn is 1.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of qenjens that come back
unchanged from themselves: yuktarn and xilzam. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of antisymmetry of the relation, closure
under the first operation and comparability of every pair. Those are properties of this
system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A12 (antisymmetry of the relation), A14
(comparability of every pair), D13 (duthsib pairs) and D3 (rastdri collections).

These results are used again in D11 (the korrgel of a qenjen), T4 (the kaduth of a
qenjen is rastdri), T5 (the kaduth is contained in every rastdri collection) and T7 (the
kaduth of a zammorn qenjen stays in the zammorn).

## Proofs

T10. No two distinct qenjens can both be tezwrens.

  (1) [D9] Let f and h both be floors.
  (2) [D9] Then f <~ h, since h is any object, and h <~ f likewise.
  (3) [A12] Antisymmetry forces f = h.

Checked over 25 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T11. Some qenjen tezwrens the whole system.

  (1) [A14] Every pair is comparable, so the relation orders the objects into a line.
  (2) [D9] The claim is that the line has a bottom.
  (3) The carrier is finite, so the search over candidates terminates.

Checked over 25 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T12. No two distinct qenjens lie in each other's opalglim.

  (1) [D13] Suppose x and y form a tight pair.
  (2) [A12] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the kaduth of a qenjen. Later chapters state their results in these terms
and do not restate the definitions.

The results now available are T10, T11 and T12, each settled by exhaustive check rather
than by argument from analogy.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x017. List the kaduth of shentu.
  x018. Name every qenjen in [nyrazt].
  x019. List the kaduth of cloreld.
Level 4.
  x020. Let z be nyrazt + nyrazt. List the kaduth of z.
  x021. Let z be cloreld + xilzam. List the kaduth of z.

# Chapter 9. Combining objects (2)

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is where every qenjen
is tufal breaks down, every qenjen lies in the zammorn and the mithra lies in the
zammorn.

Prerequisites are real here: chapters 1, 5, 6 and 7 supply the notions the statements
below are phrased in.

The standard of proof here is exhaustion. A universal claim about qenjens covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

A useful mental split: some qenjens are inert under the operation and some are not.
yuktarn and xilzam come back unchanged when combined with themselves, and yuktarn,
xilzam, shentu, nyrazt and cloreld commute with everything.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R8 rests on D7 (the vexfex). The dependence is on the content of those results, not only
on their vocabulary.

T13 rests on D6 (the zammorn). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T2 rests on D5 (the mithra) and D6 (the zammorn). Remove any one of them and the
statement stops making sense, not merely stops being provable.

T3 rests on D6 (the zammorn), D3 (rastdri collections) and A2 (association of the first
operation). The dependence is on the content of those results, not only on their
vocabulary.

T8 rests on D7 (the vexfex) and D3 (rastdri collections). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Here is xilzam + shentu |= yuktarn, reduced without skipping anything.
    shentu |= yuktarn = yuktarn   (the table for |=)
    xilzam + yuktarn = yuktarn   (the table for +)
So xilzam + shentu |= yuktarn is yuktarn.

A companion case, shentu + (yuktarn + xilzam), to show what the brackets are doing.
    yuktarn + xilzam = yuktarn   (the table for +)
    shentu + yuktarn = yuktarn   (the table for +)
The value is yuktarn. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
cloreld <~ cloreld hold? Read off what cloreld stands over: cloreld. cloreld is among
them, so it holds.

## A case that breaks

R8. It is not the case that: x + x = x for every qenjen x. The case that settles it: x =
shentu, value = cloreld. Anyone carrying this claim over from a more familiar system
will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by a neutral object for the first operation, association of the
first operation and closure under the first operation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A2 (association of the first operation), D3 (rastdri collections), D5
(the mithra) and D6 (the zammorn).

These results are used again in T7 (the kaduth of a zammorn qenjen stays in the zammorn)
and T14 (the second operation keeps the zammorn intact).

## Proofs

R8. It is not the case that: x + x = x for every qenjen x.

  (1) [S2] Take the case x = shentu, value = cloreld, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T13. Every pair of qenjens braumbs.

  (1) [D6] The zammorn is defined by braumbing with everything.
  (2) [D2] The claim is that x + y = y + x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T2. The mithra braumbs with every qenjen.

  (1) [D5] Let e be the mithra and x any qenjen.
  (2) [D5] Then e + x = x and x + e = x.
  (3) [D2] So e + x = x + e, which is what it means to braumb.
  (4) [D6] Since x was arbitrary, e belongs to the zammorn.

Checked over 5 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. If x and y both braumb with every qenjen, then so does x + y.

  (1) [D6] Let x and y lie in the zammorn and let z be any qenjen.
  (2) [A2] Then (x + y) + z = x + (y + z).
  (3) [D6] Move z past y, then past x, using that each braumbs with everything.
  (4) [D3] So x + y braumbs with z, and the zammorn is rastdri.

Checked over 25 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

T8. If x and y are both tufal then so is x + y.

  (1) [D7] Let x and y be tufal.
  (2) [D1] The claim asks whether (x + y) + (x + y) returns x + y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 25 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

The results now available are T13, T2, T3 and T8, each settled by exhaustive check
rather than by argument from analogy.

Do not carry forward R8. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x036. This result is about the vexfex. List every qenjen in it.
Level 5.
  x037. The following fails in this system: x + x = x for every qenjen x. Name the earliest qenjen, in the order the qenjens were introduced, that witnesses the failure.

# Chapter 10. Collections that close on themselves

## Why this chapter

What follows was pieced together backwards. The last item of it, the korrgel of a
qenjen, the kaduth of a qenjen is rastdri and the kaduth of a zammorn qenjen stays in
the zammorn, was noticed before anyone had a reason to expect it.

Prerequisites are real here: chapters 6, 7, 8 and 9 supply the notions the statements
below are phrased in.

One habit to adopt: when a statement below quantifies over qenjens, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D11. The korrgel of a qenjen. The korrgel of a qenjen x is the number of qenjens in its
kaduth [x].

Worked out for each qenjen: yuktarn to 1; xilzam to 1; shentu to 4; nyrazt to 4; cloreld
to 2.

## The shape of it

The right picture for kaduth is a spreading stain rather than a list. Drop one qenjen
in, apply the operation to whatever is wet, repeat. The stain here reaches 1, 2 and 4
qenjens depending on where it started.

A useful mental split: some qenjens are inert under the operation and some are not.
yuktarn and xilzam come back unchanged when combined with themselves, and yuktarn,
xilzam, shentu, nyrazt and cloreld commute with everything.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T4 rests on D8 (the kaduth of a qenjen) and D3 (rastdri collections). The dependence is
on the content of those results, not only on their vocabulary.

T7 rests on D8 (the kaduth of a qenjen), D6 (the zammorn) and T3 (the zammorn is
rastdri). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Evaluate (xilzam + nyrazt) + (cloreld + shentu). Each line below is one lookup in a
table.
    xilzam + nyrazt = nyrazt   (the table for +)
    cloreld + shentu = nyrazt   (the table for +)
    nyrazt + nyrazt = cloreld   (the table for +)
So (xilzam + nyrazt) + (cloreld + shentu) is cloreld.

A companion case, nyrazt + (cloreld + xilzam), to show what the brackets are doing.
    cloreld + xilzam = cloreld   (the table for +)
    nyrazt + cloreld = shentu   (the table for +)
That gives shentu, against cloreld above.

One decision about the relation, since deciding is as much a skill as computing. Does
nyrazt <~ shentu hold? Read off what nyrazt stands over: nyrazt and cloreld. shentu is
not among them, so it fails.

Now compute [shentu]. Fold shentu against itself, then fold whatever appeared against
everything present, and stop when a round adds nothing. The result is xilzam, shentu,
nyrazt and cloreld, of size 4.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of qenjens that come back
unchanged from themselves: yuktarn and xilzam. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by association of the first operation and closure under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: D3 (rastdri collections), D6 (the zammorn), D8
(the kaduth of a qenjen) and T3 (the zammorn is rastdri).

These results are used again in D12 (the zelopal), T5 (the kaduth is contained in every
rastdri collection), T6 (a qenjen is tufal exactly when its korrgel is one) and R7
(where the korrgel divides the number of qenjens breaks down).

## Proofs

T4. For every qenjen x, the collection [x] is rastdri.

  (1) [D8] [x] is built by taking x and closing under +.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 125 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

T7. If x lies in the zammorn then every qenjen of [x] lies in the zammorn.

  (1) [T3] The zammorn is rastdri.
  (2) [D8] [x] is the smallest rastdri collection containing x.
  (3) A smallest such collection sits inside any other, and the zammorn is one.

Checked over 25 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the korrgel of a qenjen. Each of these is used by name
later, so the names are worth learning rather than looking up.

The results now available are T4 and T7, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x023. How many qenjens lie in [xilzam]?
  x024. How many qenjens lie in [shentu]?
  x025. How many qenjens lie in [nyrazt]?
  x026. How many qenjens lie in [cloreld]?
Level 5.
  x027. Let z be (yuktarn + nyrazt) + yuktarn. What is the korrgel of z?
  x028. Let z be nyrazt + xilzam |= shentu. What is the korrgel of z?
  x029. Let z be nyrazt + xilzam |= cloreld. What is the korrgel of z?
  x030. Let z be yuktarn + nyrazt |= xilzam. What is the korrgel of z?
  x031. Let z be (xilzam + shentu) + yuktarn. What is the korrgel of z?
  x032. Let z be xilzam + cloreld |= shentu. What is the korrgel of z?

# Chapter 11. Collections that close on themselves (2)

## Why this chapter

The practical content of this chapter is the zelopal, where the korrgel divides the
number of qenjens breaks down and where some qenjen reaches every other breaks down. It
is the part that shows up in use.

Prerequisites are real here: chapters 5, 8 and 10 supply the notions the statements
below are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
qenjens that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D12. The zelopal. The zelopal of the system is the collection of qenjens whose korrgel
is largest.

In this system that picks out shentu and nyrazt, which is 2 of the 5 qenjens.

## The shape of it

Picture the kaduth as what happens when you start with one qenjen and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 5 qenjens, that stops. In this system the sizes it stops at are 1, 2 and 4.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R7 rests on D11 (the korrgel of a qenjen) and T4 (the kaduth of a qenjen is rastdri).
The dependence is on the content of those results, not only on their vocabulary.

R9 rests on D8 (the kaduth of a qenjen) and D11 (the korrgel of a qenjen). Remove any
one of them and the statement stops making sense, not merely stops being provable.

T5 rests on D8 (the kaduth of a qenjen) and T4 (the kaduth of a qenjen is rastdri). The
dependence is on the content of those results, not only on their vocabulary.

T6 rests on D1 (tufal qenjens), D11 (the korrgel of a qenjen) and T4 (the kaduth of a
qenjen is rastdri). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Here is xilzam + cloreld |= nyrazt, reduced without skipping anything.
    cloreld |= nyrazt = nyrazt   (the table for |=)
    xilzam + nyrazt = nyrazt   (the table for +)
So xilzam + cloreld |= nyrazt is nyrazt.

Move the brackets and the work changes. Take cloreld + (nyrazt + xilzam).
    nyrazt + xilzam = nyrazt   (the table for +)
    cloreld + nyrazt = shentu   (the table for +)
That gives shentu, against nyrazt above.

Test cloreld <~ xilzam. The opalglim of cloreld is cloreld, and xilzam lies outside it,
so the relation fails.

## A case that breaks

R7. It is not the case that: For every qenjen x, the korrgel of x divides 5. The case
that settles it: x = shentu, reach = 4, size = 5. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

R9. It is not the case that: There is a qenjen whose kaduth is the whole system. It
fails at largest_span = 4, size = 5. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside D1 (tufal qenjens), D11 (the korrgel of a qenjen), D8 (the kaduth of a
qenjen) and T4 (the kaduth of a qenjen is rastdri).

## Proofs

R7. It is not the case that: For every qenjen x, the korrgel of x divides 5.

  (1) [S2] Take the case x = shentu, reach = 4, size = 5, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

R9. It is not the case that: There is a qenjen whose kaduth is the whole system.

  (1) [S2] Take the case largest_span = 4, size = 5, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T5. If S is rastdri and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 35 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T6. x + x = x holds if and only if [x] contains x alone.

  (1) [D1] If x + x = x then {x} is already closed under +.
  (2) [T4] So [x] = {x} and the korrgel is one.
  (3) [D11] Conversely a span of one object must contain x + x, which is then x.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the zelopal. Later chapters state their results in these terms and do not
restate the definitions.

Established here and safe to use: T5 and T6.

Do not carry forward R7 and R9. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x033. Write down the zelopal in full.
  x034. What is the largest korrgel any qenjen has?
Level 5.
  x035. The following fails in this system: For every qenjen x, the korrgel of x divides 5. Name the earliest qenjen, in the order the qenjens were introduced, that witnesses the failure.

# Chapter 12. The second operation and how the two interact (2)

## Why this chapter

So far the qenjens have been objects to be pushed around. This chapter starts asking
what they are like. We take up the second operation keeps the zammorn intact.

Prerequisites are real here: chapters 4, 7 and 9 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over qenjens, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

The interesting content of a two operation system sits in the gap between them: which
one distributes over which, and which qenjens are fixed by both.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T14 rests on D6 (the zammorn), A6 (closure under the second operation) and T3 (the
zammorn is rastdri). The dependence is on the content of those results, not only on
their vocabulary.

## A worked case

Here is (nyrazt + yuktarn) + (xilzam + shentu), reduced without skipping anything.
    nyrazt + yuktarn = yuktarn   (the table for +)
    xilzam + shentu = shentu   (the table for +)
    yuktarn + shentu = yuktarn   (the table for +)
So (nyrazt + yuktarn) + (xilzam + shentu) is yuktarn.

Move the brackets and the work changes. Take yuktarn + (xilzam + nyrazt).
    xilzam + nyrazt = nyrazt   (the table for +)
    yuktarn + nyrazt = yuktarn   (the table for +)
The value is yuktarn. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test nyrazt <~ cloreld. The opalglim of nyrazt is nyrazt and cloreld, and cloreld lies
inside it, so the relation holds.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of qenjens that come back
unchanged from themselves: yuktarn and xilzam. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of association of the first operation,
closure under the first operation and closure under the second operation. Those are
properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A6 (closure under the second operation), D6 (the zammorn) and T3 (the
zammorn is rastdri).

## Proofs

T14. If x and y lie in the zammorn then so does x |= y.

  (1) [T3] The zammorn is already rastdri under +.
  (2) [A6] The second operation is defined on every pair.
  (3) [D6] The claim is that |= respects the zammorn as well.

Checked over 25 cases: every ordered pair from the core. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

The results now available are T14, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

No exercises here. Every question this chapter suggested turned out to be answerable
from the question itself, so all of them were discarded.
