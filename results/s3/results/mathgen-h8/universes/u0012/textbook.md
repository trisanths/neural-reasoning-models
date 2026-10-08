# The Nyrduth system

The Nyrduth system is small enough to hold in the hand and strange enough to be worth
the trouble. It has 6 glimyuks, two operations, and one relation, and nothing else.

The glimyuks are written fexvash, kamorn, muxreld, quilisk, ovifal and kanyr. The first
operation is written &. The second is written : and binds more tightly, so x & y : z
means x & (y : z). The relation is written >-; where it holds between two glimyuks we
say the left one precedes the right one. Both operations associate to the left when
written without brackets, and brackets override that. Repeated combination is
abbreviated: x^3 means x & x & x.

A warning that will be repeated because it is the one readers ignore: nothing here is
inherited from arithmetic. Familiar names have been avoided on purpose. Where a law of
arithmetic happens to hold it is stated and checked, and where it fails a counterexample
is given.

# Chapter 1. The objects and their notation

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is the Nyrduth
signature, the Nyrduth combination tables and closure under the first operation.

One habit to adopt: when a statement below quantifies over glimyuks, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## The tables in full

The table for &. Read the left argument down the side and the right argument across the top.

         |  fexvash   kamorn  muxreld  quilisk   ovifal    kanyr
----------------------------------------------------------------
 fexvash |  fexvash   kamorn  muxreld  quilisk   ovifal    kanyr
  kamorn |   kamorn  muxreld  quilisk   ovifal    kanyr    kanyr
 muxreld |  muxreld  quilisk   ovifal    kanyr    kanyr    kanyr
 quilisk |  quilisk   ovifal    kanyr    kanyr    kanyr    kanyr
  ovifal |   ovifal    kanyr    kanyr    kanyr    kanyr    kanyr
   kanyr |    kanyr    kanyr    kanyr    kanyr    kanyr    kanyr

The table for :. Read the left argument down the side and the right argument across the top.

         |  fexvash   kamorn  muxreld  quilisk   ovifal    kanyr
----------------------------------------------------------------
 fexvash |  fexvash  fexvash  fexvash  fexvash  fexvash  fexvash
  kamorn |  fexvash   kamorn   kamorn   kamorn   kamorn   kamorn
 muxreld |  fexvash   kamorn  muxreld  muxreld  muxreld  muxreld
 quilisk |  fexvash   kamorn  muxreld  quilisk  quilisk  quilisk
  ovifal |  fexvash   kamorn  muxreld  quilisk   ovifal   ovifal
   kanyr |  fexvash   kamorn  muxreld  quilisk   ovifal    kanyr

Every pair standing in the >- relation, grouped by left argument.

  fexvash >- fexvash, kamorn, muxreld, quilisk, ovifal and kanyr
  kamorn >- kamorn, muxreld, quilisk, ovifal and kanyr
  muxreld >- muxreld, quilisk, ovifal and kanyr
  quilisk >- quilisk, ovifal and kanyr
  ovifal >- ovifal and kanyr
  kanyr >- kanyr

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A1. Closure under the first operation. For all glimyuks x and y, x & y is again a
glimyuk.

A2. Association of the first operation. For all glimyuks x, y, z: (x & y) & z = x & (y &
z).

A3. Commutation of the first operation. For all glimyuks x and y: x & y = y & x.

## The shape of it

A useful mental split: some glimyuks are inert under the operation and some are not.
fexvash and kanyr come back unchanged when combined with themselves, and fexvash,
kamorn, muxreld, quilisk, ovifal and kanyr commute with everything.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R2 rests on S2 (the Nyrduth combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R3 rests on S2 (the Nyrduth combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Take quilisk & muxreld : ovifal and work it out one step at a time.
    muxreld : ovifal = muxreld   (the table for :)
    quilisk & muxreld = kanyr   (the table for &)
So quilisk & muxreld : ovifal is kanyr.

Move the brackets and the work changes. Take muxreld & (ovifal & quilisk).
    ovifal & quilisk = kanyr   (the table for &)
    muxreld & kanyr = kanyr   (the table for &)
That gives kanyr, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test kamorn >- fexvash. The mornclo of kamorn is kamorn, muxreld, quilisk, ovifal and
kanyr, and fexvash lies outside it, so the relation fails.

## A case that breaks

R2. It is not the case that: For every glimyuk x: x & x = x. It fails at x = kamorn,
value = muxreld. One case is enough, and this is the earliest one.

R3. It is not the case that: For all glimyuks x, y, z: if x & y = x & z then y = z. The
case that settles it: x = kamorn, y = ovifal, z = kanyr. Anyone carrying this claim over
from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

What is built on it later: A4 (a neutral object for the first operation), A5 (an
absorbing object for the first operation), A6 (closure under the second operation) and
A7 (association of the second operation).

## Proofs

R2. It is not the case that: For every glimyuk x: x & x = x.

  (1) [S2] Take the case x = kamorn, value = muxreld, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R3. It is not the case that: For all glimyuks x, y, z: if x & y = x & z then y = z.

  (1) [S2] Take the case x = kamorn, y = ovifal, z = kanyr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R2 and R3. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 1.
  x001. Work out the value of kamorn & quilisk.
  x002. Work out the value of quilisk & ovifal.
Level 2.
  x003. Evaluate muxreld & muxreld : kamorn.
  x004. Evaluate (muxreld & kamorn) & fexvash.
  x006. Evaluate kamorn^2.
  x007. Which glimyuks x satisfy x & ovifal = ovifal? List them all.
  x008. Which glimyuks x satisfy x & ovifal = kanyr? List them all.
  x009. Solve x & quilisk = kanyr for x, naming every solution.
  x010. Solve x & muxreld = kanyr for x, naming every solution.
Level 3.
  x005. Evaluate (fexvash & muxreld) & (quilisk & muxreld).
  x011. Evaluate muxreld & quilisk : quilisk, minding which operation binds tighter.
Level 5.
  x013. The following fails in this system: For every glimyuk x: x & x = x. Name the earliest glimyuk, in the order the glimyuks were introduced, that witnesses the failure.
  x014. The following fails in this system: For all glimyuks x, y, z: if x & y = x & z then y = z. Name the earliest glimyuk, in the order the glimyuks were introduced, that witnesses the failure.

# Chapter 2. Neutral objects and reversal

## Why this chapter

The results collected here were not found in this order. A neutral object for the first
operation, an absorbing object for the first operation and the system does not have
reversal under the first operation came first, and the rest was assembled around that
once the pattern was visible.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

One habit to adopt: when a statement below quantifies over glimyuks, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A4. A neutral object for the first operation. There is a glimyuk fexvash with fexvash &
x = x & fexvash = x for every x.

A5. An absorbing object for the first operation. There is a glimyuk kanyr with kanyr & x
= x & kanyr = kanyr for every x.

## The shape of it

The neutral glimyuk fexvash is the one that does nothing. That sounds trivial and is
not: almost every result in this chapter is an argument about what doing nothing forces.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R1 rests on S2 (the Nyrduth combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Take (kanyr & ovifal) & (muxreld & kamorn) and work it out one step at a time.
    kanyr & ovifal = kanyr   (the table for &)
    muxreld & kamorn = quilisk   (the table for &)
    kanyr & quilisk = kanyr   (the table for &)
That leaves kanyr, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is ovifal & (muxreld & kanyr) for contrast.
    muxreld & kanyr = kanyr   (the table for &)
    ovifal & kanyr = kanyr   (the table for &)
That gives kanyr, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test ovifal >- quilisk. The mornclo of ovifal is ovifal and kanyr, and quilisk lies
outside it, so the relation fails.

## A case that breaks

R1. Some glimyuk x admits no glimyuk y for which x & y and y & x both land on a neutral
object. The case that settles it: x = kamorn. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside S2 (the Nyrduth combination tables).

These results are used again in D5 (the muxclo) and T1 (the muxclo is the only one of
its kind).

## Proofs

R1. Some glimyuk x admits no glimyuk y for which x & y and y & x both land on a neutral object.

  (1) [S2] Take the case x = kamorn, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R1. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 5.
  x012. The following fails in this system: Some glimyuk x admits no glimyuk y for which x & y and y & x both land on a neutral object. Name the earliest glimyuk, in the order the glimyuks were introduced, that witnesses the failure.

# Chapter 3. The relation and what it orders

## Why this chapter

Anyone using this system to keep track of something will meet reflexivity of the
relation, antisymmetry of the relation and transitivity of the relation early, whether
or not they go looking.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

One habit to adopt: when a statement below quantifies over glimyuks, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A11. Reflexivity of the relation. For every glimyuk x: x >- x.

A12. Antisymmetry of the relation. For all glimyuks x and y: if x >- y and y >- x then x
= y.

A13. Transitivity of the relation. For all glimyuks x, y, z: if x >- y and y >- z then x
>- z.

A14. Comparability of every pair. For all glimyuks x and y, at least one of x >- y and y
>- x holds.

A15. Agreement of the relation with the first operation. For all glimyuks x, y, z: if x
>- y then (z & x) >- (z & y) and (x & z) >- (y & z).

A16. Agreement of the relation with the second operation. For all glimyuks x, y, z: if x
>- y then (z : x) >- (z : y) and (x : z) >- (y : z).

D4. The mornclo of a glimyuk. The mornclo of a glimyuk x is the collection of glimyuks y
for which x >- y holds.

Worked out for each glimyuk: fexvash to fexvash, kamorn, muxreld, quilisk, ovifal and
kanyr; kamorn to kamorn, muxreld, quilisk, ovifal and kanyr; muxreld to muxreld,
quilisk, ovifal and kanyr; quilisk to quilisk, ovifal and kanyr; ovifal to ovifal and
kanyr; kanyr to kanyr.

## The shape of it

The relation is easiest to see as a height. Each glimyuk casts a mornclo over what it
precedes, and the sizes of those shadows here are 1, 2, 3, 4, 5 and 6. No two are the
same size, so the objects line up in a single file.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Nothing is derived in this chapter. It lays down material that later chapters draw on.

## A worked case

Here is quilisk & ovifal : muxreld, reduced without skipping anything.
    ovifal : muxreld = muxreld   (the table for :)
    quilisk & muxreld = kanyr   (the table for &)
That leaves kanyr, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take ovifal & (muxreld & quilisk).
    muxreld & quilisk = kanyr   (the table for &)
    ovifal & kanyr = kanyr   (the table for &)
That gives kanyr, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
quilisk >- muxreld hold? Read off what quilisk stands over: quilisk, ovifal and kanyr.
muxreld is not among them, so it fails.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of glimyuks that come back
unchanged from themselves: fexvash and kanyr. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

The limits of these results are sharper than they look.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside S2 (the Nyrduth combination tables).

These results are used again in D9 (a mornisk), D13 (keldthra pairs), T9 (mornclos are
nested along the relation) and T10 (there is at most one mornisk).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

Carry forward the mornclo of a glimyuk. Later chapters state their results in these
terms and do not restate the definitions.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x018. Which glimyuks y satisfy fexvash >- y? Name them all.
  x019. List the mornclo of kamorn.
  x020. List the mornclo of muxreld.
  x021. List the mornclo of quilisk.
  x022. Which glimyuks y satisfy ovifal >- y? Name them all.

# Chapter 4. The second operation and how the two interact

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through self combination under the
second operation, closure under the second operation and association of the second
operation.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about glimyuks covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A10. Self combination under the second operation. For every glimyuk x: x : x = x.

A6. Closure under the second operation. For all glimyuks x and y, x : y is again a
glimyuk.

A7. Association of the second operation. For all glimyuks x, y, z: (x : y) : z = x : (y
: z).

A8. Commutation of the second operation. For all glimyuks x and y: x : y = y : x.

A9. A neutral object for the second operation. There is a glimyuk kanyr with kanyr : x =
x for every x.

## The shape of it

The interesting content of a two operation system sits in the gap between them: which
one distributes over which, and which glimyuks are fixed by both.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R4 rests on S2 (the Nyrduth combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R5 rests on S2 (the Nyrduth combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Take (ovifal & kanyr) & (kamorn & muxreld) and work it out one step at a time.
    ovifal & kanyr = kanyr   (the table for &)
    kamorn & muxreld = quilisk   (the table for &)
    kanyr & quilisk = kanyr   (the table for &)
The expression comes to kanyr.

Bracketing is not cosmetic, so here is kanyr & (kamorn & ovifal) for contrast.
    kamorn & ovifal = kanyr   (the table for &)
    kanyr & kanyr = kanyr   (the table for &)
The value is kanyr. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test muxreld >- kanyr. The mornclo of muxreld is muxreld, quilisk, ovifal and kanyr, and
kanyr lies inside it, so the relation holds.

## A case that breaks

R4. It is not the case that: For all glimyuks x, y, z: x : (y & z) = (x : y) & (x : z),
and the same on the right. The case that settles it: x = kamorn, y = kamorn, z = kamorn,
left = kamorn, right = muxreld. Anyone carrying this claim over from a more familiar
system will be wrong here, and wrong in a way that propagates.

R5. It is not the case that: For all glimyuks x and y: x & (x : y) = x and x : (x & y) =
x. The case that settles it: x = kamorn, y = kamorn, value = muxreld. Anyone carrying
this claim over from a more familiar system will be wrong here, and wrong in a way that
propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: S2 (the Nyrduth combination tables).

These results are used again in T15 (the second operation keeps the fexsol intact).

## Proofs

R4. It is not the case that: For all glimyuks x, y, z: x : (y & z) = (x : y) & (x : z), and the same on the right.

  (1) [S2] Take the case x = kamorn, y = kamorn, z = kamorn, left = kamorn, right = muxreld, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R5. It is not the case that: For all glimyuks x and y: x & (x : y) = x and x : (x & y) = x.

  (1) [S2] Take the case x = kamorn, y = kamorn, value = muxreld, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R4 and R5. These were tested and failed, and the failing cases are
recorded above.

## Exercises

No exercises here. Every question this chapter suggested turned out to be answerable
from the question itself, so all of them were discarded.

# Chapter 5. Combining objects

## Why this chapter

The present chapter develops sibtez glimyuks, glimyuks that shenovi and the muxclo.

Prerequisites are real here: chapters 1 and 2 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over glimyuks, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D1. Sibtez glimyuks. A glimyuk x is called sibtez when x & x = x.

In this system that picks out fexvash and kanyr, which is 2 of the 6 glimyuks.

D2. Glimyuks that shenovi. Two glimyuks x and y are said to shenovi when x & y = y & x.

D5. The muxclo. The glimyuk fexvash is called the muxclo of the system. It is the unique
glimyuk that leaves every glimyuk unchanged under &.

Here that is fexvash.

## The shape of it

Two questions sort the glimyuks quickly. Does combining a glimyuk with itself change it?
For fexvash and kanyr it does not. Does it matter which side it goes on? For fexvash,
kamorn, muxreld, quilisk, ovifal and kanyr it does not.

Neutrality is a strong condition disguised as a weak one. It fixes a single glimyuk and,
through that, constrains everything that can combine with it.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 glimyuks the table is short enough to consult every time.

## Where these results come from

Nothing is derived in this chapter. It lays down material that later chapters draw on.

## A worked case

Evaluate kamorn & quilisk : kanyr. Each line below is one lookup in a table.
    quilisk : kanyr = quilisk   (the table for :)
    kamorn & quilisk = ovifal   (the table for &)
So kamorn & quilisk : kanyr is ovifal.

Bracketing is not cosmetic, so here is quilisk & (kanyr & kamorn) for contrast.
    kanyr & kamorn = kanyr   (the table for &)
    quilisk & kanyr = kanyr   (the table for &)
The value is kanyr, not ovifal.

Test muxreld >- kamorn. The mornclo of muxreld is muxreld, quilisk, ovifal and kanyr,
and kamorn lies outside it, so the relation fails.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of glimyuks that come back
unchanged from themselves: fexvash and kanyr. Assuming more of them than that is the
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

These results are used again in D6 (the fexsol), D7 (the hobkorr), D10 (glimshen
glimyuks) and T1 (the muxclo is the only one of its kind).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

New vocabulary from this chapter: sibtez glimyuks, glimyuks that shenovi and the muxclo.
Each of these is used by name later, so the names are worth learning rather than looking
up.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 2.
  x023. Which glimyuk leaves every glimyuk unchanged under &?
Level 3.
  x015. Which glimyuks make up the sibtez? Name them all.

# Chapter 6. The relation and what it orders (2)

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is keldthra pairs,
tuopal collections and a mornisk.

Nothing here stands on its own. The arguments lean on chapters 1 and 3, and a reader who
has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
glimyuks that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D13. Keldthra pairs. Two distinct glimyuks x and y form a keldthra pair when x >- y and
y >- x both hold, that is, when each lies in the mornclo of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D3. Tuopal collections. A collection S of glimyuks is tuopal when x & y belongs to S for
every pair x, y drawn from S.

D9. A mornisk. A glimyuk f is a mornisk when f >- y holds for every glimyuk y, that is,
when the mornclo of f is the whole system.

In this system that picks out fexvash, which is 1 of the 6 glimyuks.

## The shape of it

The right picture for xilvor is a spreading stain rather than a list. Drop one glimyuk
in, apply the operation to whatever is wet, repeat. The stain here reaches 1, 2, 3 and 5
glimyuks depending on where it started.

Think of >- as pointing downhill. The mornclo of a glimyuk is everything downhill of it,
and those shadows here have sizes 1, 2, 3, 4, 5 and 6.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 glimyuks the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R9 rests on D4 (the mornclo of a glimyuk). The dependence is on the content of those
results, not only on their vocabulary.

T12 rests on D4 (the mornclo of a glimyuk) and A15 (agreement of the relation with the
first operation). The dependence is on the content of those results, not only on their
vocabulary.

T9 rests on D4 (the mornclo of a glimyuk) and A13 (transitivity of the relation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Here is (fexvash & ovifal) & (kanyr & quilisk), reduced without skipping anything.
    fexvash & ovifal = ovifal   (the table for &)
    kanyr & quilisk = kanyr   (the table for &)
    ovifal & kanyr = kanyr   (the table for &)
The expression comes to kanyr.

A companion case, ovifal & (kanyr & fexvash), to show what the brackets are doing.
    kanyr & fexvash = kanyr   (the table for &)
    ovifal & kanyr = kanyr   (the table for &)
The value is kanyr. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
muxreld >- kanyr hold? Read off what muxreld stands over: muxreld, quilisk, ovifal and
kanyr. kanyr is among them, so it holds.

## A case that breaks

R9. It is not the case that: If x >- y then y >- x. The case that settles it: x =
fexvash, y = kamorn. Anyone carrying this claim over from a more familiar system will be
wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of agreement of the relation with the first
operation, closure under the first operation and transitivity of the relation. Those are
properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A1 (closure under the first operation), A13
(transitivity of the relation), A15 (agreement of the relation with the first operation)
and D4 (the mornclo of a glimyuk).

These results are used again in D8 (the xilvor of a glimyuk), T3 (the fexsol is tuopal),
T4 (the xilvor of a glimyuk is tuopal) and T8 (the hobkorr is tuopal).

## Proofs

R9. It is not the case that: If x >- y then y >- x.

  (1) [S2] Take the case x = fexvash, y = kamorn, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T12. If x >- y then (x & z) >- (y & z) for every glimyuk z.

  (1) [D4] Let y lie in the mornclo of x.
  (2) [A15] Compatibility applies the operation to both sides at once.
  (3) Nothing else is needed, since z was arbitrary.

Checked over 216 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T9. If y lies in the mornclo of x, then the mornclo of y is contained in the mornclo of x.

  (1) [D4] Let y satisfy x >- y and let z satisfy y >- z.
  (2) [A13] Transitivity gives x >- z.
  (3) [D4] So every member of the mornclo of y is a member of that of x.

Checked over 216 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: keldthra pairs, tuopal collections and a mornisk. Each
of these is used by name later, so the names are worth learning rather than looking up.

Established here and safe to use: T12 and T9.

Do not carry forward R9. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x016. How many glimyuks lie in the smallest tuopal collection containing kamorn?
  x017. How many glimyuks lie in the smallest tuopal collection containing muxreld?
Level 4.
  x032. Write down the mornisk in full.
  x046. The result above concerns mornclos. List the mornclo of fexvash.
  x047. The result above concerns mornclos. List the mornclo of kamorn.
  x048. The result above concerns mornclos. List the mornclo of muxreld.
Level 5.
  x051. The following fails in this system: If x >- y then y >- x. Name the earliest glimyuk, in the order the glimyuks were introduced, that witnesses the failure.

# Chapter 7. Neutral objects and reversal (2)

## Why this chapter

What follows was pieced together backwards. The last item of it, glimshen glimyuks, the
fexsol and the hobkorr, was noticed before anyone had a reason to expect it.

Nothing here stands on its own. The arguments lean on chapters 2 and 5, and a reader who
has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about glimyuks covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D10. Glimshen glimyuks. A glimyuk x is glimshen when x & x equals the muxclo.

In this system that picks out fexvash, which is 1 of the 6 glimyuks.

D6. The fexsol. The fexsol of the system is the collection of glimyuks that shenovi with
every glimyuk.

In this system that picks out fexvash, kamorn, muxreld, quilisk, ovifal and kanyr, that
is, all of them.

D7. The hobkorr. The hobkorr is the collection of all sibtez glimyuks.

In this system that picks out fexvash and kanyr, which is 2 of the 6 glimyuks.

## The shape of it

Two questions sort the glimyuks quickly. Does combining a glimyuk with itself change it?
For fexvash and kanyr it does not. Does it matter which side it goes on? For fexvash,
kamorn, muxreld, quilisk, ovifal and kanyr it does not.

Neutrality is a strong condition disguised as a weak one. It fixes a single glimyuk and,
through that, constrains everything that can combine with it.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R10 rests on D5 (the muxclo). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T1 rests on D5 (the muxclo) and A4 (a neutral object for the first operation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Here is ovifal & fexvash : muxreld, reduced without skipping anything.
    fexvash : muxreld = fexvash   (the table for :)
    ovifal & fexvash = ovifal   (the table for &)
So ovifal & fexvash : muxreld is ovifal.

Bracketing is not cosmetic, so here is fexvash & (muxreld & ovifal) for contrast.
    muxreld & ovifal = kanyr   (the table for &)
    fexvash & kanyr = kanyr   (the table for &)
That gives kanyr, against ovifal above.

Test quilisk >- fexvash. The mornclo of quilisk is quilisk, ovifal and kanyr, and
fexvash lies outside it, so the relation fails.

## A case that breaks

R10. It is not the case that: e & x equals the muxclo for every glimyuk x. It fails at
anchor = fexvash, x = kamorn, value = kamorn. One case is enough, and this is the
earliest one.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of a neutral object for the first operation
and closure under the first operation. Those are properties of this system, not of
systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A4 (a neutral object for the first operation), D1 (sibtez glimyuks), D2
(glimyuks that shenovi) and D5 (the muxclo).

These results are used again in T2 (the muxclo lies in the fexsol), T3 (the fexsol is
tuopal), T7 (the xilvor of a fexsol glimyuk stays in the fexsol) and T8 (the hobkorr is
tuopal).

## Proofs

R10. It is not the case that: e & x equals the muxclo for every glimyuk x.

  (1) [S2] Take the case anchor = fexvash, x = kamorn, value = kamorn, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T1. There is exactly one glimyuk e with e & x = x & e = x for every glimyuk x.

  (1) [D5] Suppose e and f both leave every glimyuk unchanged.
  (2) [A4] Then e & f = f, reading e as neutral on the left.
  (3) [A4] And e & f = e, reading f as neutral on the right.
  (4) So e = f, and the two suppositions describe the same object.

Checked over 36 cases: every object paired with every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: glimshen glimyuks, the fexsol and the hobkorr. Each of
these is used by name later, so the names are worth learning rather than looking up.

Established here and safe to use: T1.

Do not carry forward R10. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x024. Write down the hobkorr in full.
  x033. Which glimyuks make up the glimshen? Name them all.
Level 5.
  x052. The following fails in this system: e & x equals the muxclo for every glimyuk x. Name the earliest glimyuk, in the order the glimyuks were introduced, that witnesses the failure.

# Chapter 8. The relation and what it orders (3)

## Why this chapter

Anyone using this system to keep track of something will meet the xilvor of a glimyuk,
there is at most one mornisk and the system has a mornisk early, whether or not they go
looking.

Nothing here stands on its own. The arguments lean on chapters 3 and 6, and a reader who
has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
glimyuks that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D8. The xilvor of a glimyuk. The xilvor of a glimyuk x, written [x], is the smallest
tuopal collection that contains x.

Worked out for each glimyuk: fexvash to fexvash; kamorn to kamorn, muxreld, quilisk,
ovifal and kanyr; muxreld to muxreld, ovifal and kanyr; quilisk to quilisk and kanyr;
ovifal to ovifal and kanyr; kanyr to kanyr.

## The shape of it

Picture the xilvor as what happens when you start with one glimyuk and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 6 glimyuks, that stops. In this system the sizes it stops at are 1, 2, 3 and 5.

The relation is easiest to see as a height. Each glimyuk casts a mornclo over what it
precedes, and the sizes of those shadows here are 1, 2, 3, 4, 5 and 6. No two are the
same size, so the objects line up in a single file.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T10 rests on D9 (a mornisk) and A12 (antisymmetry of the relation). Remove any one of
them and the statement stops making sense, not merely stops being provable.

T11 rests on D9 (a mornisk) and A14 (comparability of every pair). The dependence is on
the content of those results, not only on their vocabulary.

T13 rests on D13 (keldthra pairs) and A12 (antisymmetry of the relation). The dependence
is on the content of those results, not only on their vocabulary.

## A worked case

Take (kamorn & quilisk) & (kanyr & ovifal) and work it out one step at a time.
    kamorn & quilisk = ovifal   (the table for &)
    kanyr & ovifal = kanyr   (the table for &)
    ovifal & kanyr = kanyr   (the table for &)
So (kamorn & quilisk) & (kanyr & ovifal) is kanyr.

Move the brackets and the work changes. Take quilisk & (kanyr & kamorn).
    kanyr & kamorn = kanyr   (the table for &)
    quilisk & kanyr = kanyr   (the table for &)
The value is kanyr. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test fexvash >- kanyr. The mornclo of fexvash is fexvash, kamorn, muxreld, quilisk,
ovifal and kanyr, and kanyr lies inside it, so the relation holds.

A second case, this time a xilvor. Start from kanyr. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is kanyr, so the migel
of kanyr is 1.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by antisymmetry of the relation, closure under the first operation
and comparability of every pair. A system without them is not a system where these
results are harder to prove; it is a system where they are false.

That is not a rhetorical caution. Take the same 6 objects, the same symbols, and a
different table, and T10 and T13 stop holding. The notation survives the substitution
and the mathematics does not.

## Neighbouring results

Read alongside A12 (antisymmetry of the relation), A14 (comparability of every pair),
D13 (keldthra pairs) and D3 (tuopal collections).

These results are used again in D11 (the migel of a glimyuk), T4 (the xilvor of a
glimyuk is tuopal), T5 (the xilvor is contained in every tuopal collection) and T7 (the
xilvor of a fexsol glimyuk stays in the fexsol).

## Proofs

T10. No two distinct glimyuks can both be mornisks.

  (1) [D9] Let f and h both be floors.
  (2) [D9] Then f >- h, since h is any object, and h >- f likewise.
  (3) [A12] Antisymmetry forces f = h.

Checked over 36 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T11. Some glimyuk mornisks the whole system.

  (1) [A14] Every pair is comparable, so the relation orders the objects into a line.
  (2) [D9] The claim is that the line has a bottom.
  (3) The carrier is finite, so the search over candidates terminates.

Checked over 36 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T13. No two distinct glimyuks lie in each other's mornclo.

  (1) [D13] Suppose x and y form a tight pair.
  (2) [A12] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the xilvor of a glimyuk. Each of these is used by name
later, so the names are worth learning rather than looking up.

The results now available are T10, T11 and T13, each settled by exhaustive check rather
than by argument from analogy.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x025. List the xilvor of kamorn.
  x026. List the xilvor of muxreld.
  x027. List the xilvor of quilisk.
  x028. List the xilvor of ovifal.
Level 4.
  x029. Let z be kamorn & kamorn. List the xilvor of z.
  x030. Let z be ovifal & quilisk. List the xilvor of z.
  x031. Let z be muxreld & quilisk. List the xilvor of z.
  x049. Name the glimyuks that make up the mornisk, which is what the result above is a claim about.

# Chapter 9. Combining objects (2)

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through where every glimyuk is sibtez
breaks down, every glimyuk lies in the fexsol and the muxclo lies in the fexsol.

Prerequisites are real here: chapters 1, 5, 6 and 7 supply the notions the statements
below are phrased in.

One habit to adopt: when a statement below quantifies over glimyuks, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

A useful mental split: some glimyuks are inert under the operation and some are not.
fexvash and kanyr come back unchanged when combined with themselves, and fexvash,
kamorn, muxreld, quilisk, ovifal and kanyr commute with everything.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R7 rests on D7 (the hobkorr). The dependence is on the content of those results, not
only on their vocabulary.

T14 rests on D6 (the fexsol). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T2 rests on D5 (the muxclo) and D6 (the fexsol). Remove any one of them and the
statement stops making sense, not merely stops being provable.

T3 rests on D6 (the fexsol), D3 (tuopal collections) and A2 (association of the first
operation). Remove any one of them and the statement stops making sense, not merely
stops being provable.

T8 rests on D7 (the hobkorr) and D3 (tuopal collections). The dependence is on the
content of those results, not only on their vocabulary.

## A worked case

Evaluate kanyr & ovifal : muxreld. Each line below is one lookup in a table.
    ovifal : muxreld = muxreld   (the table for :)
    kanyr & muxreld = kanyr   (the table for &)
The expression comes to kanyr.

Move the brackets and the work changes. Take ovifal & (muxreld & kanyr).
    muxreld & kanyr = kanyr   (the table for &)
    ovifal & kanyr = kanyr   (the table for &)
The value is kanyr. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test fexvash >- kanyr. The mornclo of fexvash is fexvash, kamorn, muxreld, quilisk,
ovifal and kanyr, and kanyr lies inside it, so the relation holds.

## A case that breaks

R7. It is not the case that: x & x = x for every glimyuk x. It fails at x = kamorn,
value = muxreld. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation and closure under the first operation. Those are
properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A2 (association of the first operation), D3 (tuopal collections), D5 (the
muxclo) and D6 (the fexsol).

These results are used again in T7 (the xilvor of a fexsol glimyuk stays in the fexsol)
and T15 (the second operation keeps the fexsol intact).

## Proofs

R7. It is not the case that: x & x = x for every glimyuk x.

  (1) [S2] Take the case x = kamorn, value = muxreld, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T14. Every pair of glimyuks shenovis.

  (1) [D6] The fexsol is defined by shenoviing with everything.
  (2) [D2] The claim is that x & y = y & x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T2. The muxclo shenovis with every glimyuk.

  (1) [D5] Let e be the muxclo and x any glimyuk.
  (2) [D5] Then e & x = x and x & e = x.
  (3) [D2] So e & x = x & e, which is what it means to shenovi.
  (4) [D6] Since x was arbitrary, e belongs to the fexsol.

Checked over 6 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. If x and y both shenovi with every glimyuk, then so does x & y.

  (1) [D6] Let x and y lie in the fexsol and let z be any glimyuk.
  (2) [A2] Then (x & y) & z = x & (y & z).
  (3) [D6] Move z past y, then past x, using that each shenovis with everything.
  (4) [D3] So x & y shenovis with z, and the fexsol is tuopal.

Checked over 36 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

T8. If x and y are both sibtez then so is x & y.

  (1) [D7] Let x and y be sibtez.
  (2) [D1] The claim asks whether (x & y) & (x & y) returns x & y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 36 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Established here and safe to use: T14, T2, T3 and T8.

Explicitly not available: R7. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x045. Name the glimyuks that make up the hobkorr, which is what the result above is a claim about.
Level 5.
  x050. The following fails in this system: x & x = x for every glimyuk x. Name the earliest glimyuk, in the order the glimyuks were introduced, that witnesses the failure.

# Chapter 10. Collections that close on themselves

## Why this chapter

We turn to the migel of a glimyuk, the xilvor of a glimyuk is tuopal and the xilvor of a
fexsol glimyuk stays in the fexsol. The treatment is self contained given the material
already established.

Nothing here stands on its own. The arguments lean on chapters 6, 7, 8 and 9, and a
reader who has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
glimyuks that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D11. The migel of a glimyuk. The migel of a glimyuk x is the number of glimyuks in its
xilvor [x].

Worked out for each glimyuk: fexvash to 1; kamorn to 5; muxreld to 3; quilisk to 2;
ovifal to 2; kanyr to 1.

## The shape of it

Picture the xilvor as what happens when you start with one glimyuk and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 6 glimyuks, that stops. In this system the sizes it stops at are 1, 2, 3 and 5.

Two questions sort the glimyuks quickly. Does combining a glimyuk with itself change it?
For fexvash and kanyr it does not. Does it matter which side it goes on? For fexvash,
kamorn, muxreld, quilisk, ovifal and kanyr it does not.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 glimyuks the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T4 rests on D8 (the xilvor of a glimyuk) and D3 (tuopal collections). The dependence is
on the content of those results, not only on their vocabulary.

T7 rests on D8 (the xilvor of a glimyuk), D6 (the fexsol) and T3 (the fexsol is tuopal).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

## A worked case

Evaluate (kanyr & ovifal) & (muxreld & kamorn). Each line below is one lookup in a
table.
    kanyr & ovifal = kanyr   (the table for &)
    muxreld & kamorn = quilisk   (the table for &)
    kanyr & quilisk = kanyr   (the table for &)
That leaves kanyr, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take ovifal & (muxreld & kanyr).
    muxreld & kanyr = kanyr   (the table for &)
    ovifal & kanyr = kanyr   (the table for &)
That gives kanyr, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test kanyr >- muxreld. The mornclo of kanyr is kanyr, and muxreld lies outside it, so
the relation fails.

A second case, this time a xilvor. Start from quilisk. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is quilisk and kanyr,
so the migel of quilisk is 2.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by association of the first operation and closure under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: D3 (tuopal collections), D6 (the fexsol), D8
(the xilvor of a glimyuk) and T3 (the fexsol is tuopal).

What is built on it later: D12 (the nyrvex), T5 (the xilvor is contained in every tuopal
collection), T6 (a glimyuk is sibtez exactly when its migel is one) and R6 (where the
migel divides the number of glimyuks breaks down).

## Proofs

T4. For every glimyuk x, the collection [x] is tuopal.

  (1) [D8] [x] is built by taking x and closing under &.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 216 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

T7. If x lies in the fexsol then every glimyuk of [x] lies in the fexsol.

  (1) [T3] The fexsol is tuopal.
  (2) [D8] [x] is the smallest tuopal collection containing x.
  (3) A smallest such collection sits inside any other, and the fexsol is one.

Checked over 36 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the migel of a glimyuk. Later chapters state their results in these terms
and do not restate the definitions.

The results now available are T4 and T7, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x034. What is the migel of kamorn?
  x035. How many glimyuks lie in [muxreld]?
  x036. How many glimyuks lie in [quilisk]?
  x037. What is the migel of ovifal?
  x038. How many glimyuks lie in [kanyr]?
Level 5.
  x039. Let z be kamorn & kamorn : kanyr. What is the migel of z?
  x040. Let z be kanyr & muxreld : fexvash. What is the migel of z?
  x041. Let z be kamorn & kamorn : quilisk. What is the migel of z?

# Chapter 11. Collections that close on themselves (2)

## Why this chapter

Work through this chapter with the tables in front of you. It covers the nyrvex, where
the migel divides the number of glimyuks breaks down and where some glimyuk reaches
every other breaks down, and each claim can be checked by hand.

Prerequisites are real here: chapters 5, 8 and 10 supply the notions the statements
below are phrased in.

One habit to adopt: when a statement below quantifies over glimyuks, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D12. The nyrvex. The nyrvex of the system is the collection of glimyuks whose migel is
largest.

In this system that picks out kamorn, which is 1 of the 6 glimyuks.

## The shape of it

Picture the xilvor as what happens when you start with one glimyuk and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 6 glimyuks, that stops. In this system the sizes it stops at are 1, 2, 3 and 5.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R6 rests on D11 (the migel of a glimyuk) and T4 (the xilvor of a glimyuk is tuopal). The
dependence is on the content of those results, not only on their vocabulary.

R8 rests on D8 (the xilvor of a glimyuk) and D11 (the migel of a glimyuk). The
dependence is on the content of those results, not only on their vocabulary.

T5 rests on D8 (the xilvor of a glimyuk) and T4 (the xilvor of a glimyuk is tuopal). The
dependence is on the content of those results, not only on their vocabulary.

T6 rests on D1 (sibtez glimyuks), D11 (the migel of a glimyuk) and T4 (the xilvor of a
glimyuk is tuopal). Remove any one of them and the statement stops making sense, not
merely stops being provable.

## A worked case

Here is muxreld & quilisk : ovifal, reduced without skipping anything.
    quilisk : ovifal = quilisk   (the table for :)
    muxreld & quilisk = kanyr   (the table for &)
So muxreld & quilisk : ovifal is kanyr.

Move the brackets and the work changes. Take quilisk & (ovifal & muxreld).
    ovifal & muxreld = kanyr   (the table for &)
    quilisk & kanyr = kanyr   (the table for &)
The value is kanyr. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
muxreld >- muxreld hold? Read off what muxreld stands over: muxreld, quilisk, ovifal and
kanyr. muxreld is among them, so it holds.

## A case that breaks

R6. It is not the case that: For every glimyuk x, the migel of x divides 6. It fails at
x = kamorn, reach = 5, size = 6. One case is enough, and this is the earliest one.

R8. It is not the case that: There is a glimyuk whose xilvor is the whole system. The
case that settles it: largest_span = 5, size = 6. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: D1 (sibtez glimyuks), D11 (the migel of a
glimyuk), D8 (the xilvor of a glimyuk) and T4 (the xilvor of a glimyuk is tuopal).

## Proofs

R6. It is not the case that: For every glimyuk x, the migel of x divides 6.

  (1) [S2] Take the case x = kamorn, reach = 5, size = 6, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

R8. It is not the case that: There is a glimyuk whose xilvor is the whole system.

  (1) [S2] Take the case largest_span = 5, size = 6, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T5. If S is tuopal and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 90 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T6. x & x = x holds if and only if [x] contains x alone.

  (1) [D1] If x & x = x then {x} is already closed under &.
  (2) [T4] So [x] = {x} and the migel is one.
  (3) [D11] Conversely a span of one object must contain x & x, which is then x.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the nyrvex. Later chapters state their results in these terms and do not
restate the definitions.

The results now available are T5 and T6, each settled by exhaustive check rather than by
argument from analogy.

Do not carry forward R6 and R8. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x042. List every glimyuk in the nyrvex.
  x043. What is the largest migel any glimyuk has?
Level 5.
  x044. The following fails in this system: For every glimyuk x, the migel of x divides 6. Name the earliest glimyuk, in the order the glimyuks were introduced, that witnesses the failure.

# Chapter 12. The second operation and how the two interact (2)

## Why this chapter

What follows was pieced together backwards. The last item of it, the second operation
keeps the fexsol intact, was noticed before anyone had a reason to expect it.

Prerequisites are real here: chapters 4, 7 and 9 supply the notions the statements below
are phrased in.

The standard of proof here is exhaustion. A universal claim about glimyuks covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

The interesting content of a two operation system sits in the gap between them: which
one distributes over which, and which glimyuks are fixed by both.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T15 rests on D6 (the fexsol), A6 (closure under the second operation) and T3 (the fexsol
is tuopal). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Take (quilisk & ovifal) & (kamorn & muxreld) and work it out one step at a time.
    quilisk & ovifal = kanyr   (the table for &)
    kamorn & muxreld = quilisk   (the table for &)
    kanyr & quilisk = kanyr   (the table for &)
That leaves kanyr, and no other reading of the notation gives anything else.

A companion case, ovifal & (kamorn & quilisk), to show what the brackets are doing.
    kamorn & quilisk = ovifal   (the table for &)
    ovifal & ovifal = kanyr   (the table for &)
The value is kanyr. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test kamorn >- quilisk. The mornclo of kamorn is kamorn, muxreld, quilisk, ovifal and
kanyr, and quilisk lies inside it, so the relation holds.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of glimyuks that come back
unchanged from themselves: fexvash and kanyr. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of association of the first operation,
closure under the first operation and closure under the second operation. Those are
properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A6 (closure under the second operation), D6 (the
fexsol) and T3 (the fexsol is tuopal).

## Proofs

T15. If x and y lie in the fexsol then so does x : y.

  (1) [T3] The fexsol is already tuopal under &.
  (2) [A6] The second operation is defined on every pair.
  (3) [D6] The claim is that : respects the fexsol as well.

Checked over 36 cases: every ordered pair from the core. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Established here and safe to use: T15.

## Exercises

No exercises here. Every question this chapter suggested turned out to be answerable
from the question itself, so all of them were discarded.
