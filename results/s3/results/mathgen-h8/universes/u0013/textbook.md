# The Opalopal system

The Opalopal system is small enough to hold in the hand and strange enough to be worth
the trouble. It has 4 xilzams, two operations, and one relation, and nothing else.

The xilzams are written muxovi, nyrfex, ovimux and shennak. The first operation is
written &. The second is written $ and binds more tightly, so x & y $ z means x & (y $
z). The relation is written <|; where it holds between two xilzams we say the left one
yields to the right one. Both operations associate to the left when written without
brackets, and brackets override that. Repeated combination is abbreviated: x^3 means x &
x & x.

A warning that will be repeated because it is the one readers ignore: nothing here is
inherited from arithmetic. Familiar names have been avoided on purpose. Where a law of
arithmetic happens to hold it is stated and checked, and where it fails a counterexample
is given.

# Chapter 1. The objects and their notation

## Why this chapter

What follows was pieced together backwards. The last item of it, the Opalopal signature,
the Opalopal combination tables and closure under the first operation, was noticed
before anyone had a reason to expect it.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
xilzams that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## The tables in full

The table for &. Read the left argument down the side and the right argument across the top.

         |   muxovi   nyrfex   ovimux  shennak
----------------------------------------------
  muxovi |   muxovi   nyrfex   ovimux  shennak
  nyrfex |   nyrfex   ovimux  shennak  shennak
  ovimux |   ovimux  shennak  shennak  shennak
 shennak |  shennak  shennak  shennak  shennak

The table for $. Read the left argument down the side and the right argument across the top.

         |   muxovi   nyrfex   ovimux  shennak
----------------------------------------------
  muxovi |   muxovi   nyrfex   ovimux  shennak
  nyrfex |   muxovi   nyrfex   ovimux  shennak
  ovimux |   muxovi   nyrfex   ovimux  shennak
 shennak |   muxovi   nyrfex   ovimux  shennak

Every pair standing in the <| relation, grouped by left argument.

  muxovi <| muxovi, nyrfex, ovimux and shennak
  nyrfex <| nyrfex, ovimux and shennak
  ovimux <| ovimux and shennak
  shennak <| shennak

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A1. Closure under the first operation. For all xilzams x and y, x & y is again a xilzam.

A2. Association of the first operation. For all xilzams x, y, z: (x & y) & z = x & (y &
z).

A3. Commutation of the first operation. For all xilzams x and y: x & y = y & x.

## The shape of it

A useful mental split: some xilzams are inert under the operation and some are not.
muxovi and shennak come back unchanged when combined with themselves, and muxovi,
nyrfex, ovimux and shennak commute with everything.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R2 rests on S2 (the Opalopal combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R3 rests on S2 (the Opalopal combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Here is shennak & ovimux $ nyrfex, reduced without skipping anything.
    ovimux $ nyrfex = nyrfex   (the table for $)
    shennak & nyrfex = shennak   (the table for &)
That leaves shennak, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is ovimux & (nyrfex & shennak) for contrast.
    nyrfex & shennak = shennak   (the table for &)
    ovimux & shennak = shennak   (the table for &)
That gives shennak, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
nyrfex <| ovimux hold? Read off what nyrfex stands over: nyrfex, ovimux and shennak.
ovimux is among them, so it holds.

## A case that breaks

R2. It is not the case that: For every xilzam x: x & x = x. It fails at x = nyrfex,
value = ovimux. One case is enough, and this is the earliest one.

R3. It is not the case that: For all xilzams x, y, z: if x & y = x & z then y = z. The
case that settles it: x = nyrfex, y = ovimux, z = shennak. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

What is built on it later: A4 (a neutral object for the first operation), A5 (an
absorbing object for the first operation), A6 (closure under the second operation) and
A7 (association of the second operation).

## Proofs

R2. It is not the case that: For every xilzam x: x & x = x.

  (1) [S2] Take the case x = nyrfex, value = ovimux, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R3. It is not the case that: For all xilzams x, y, z: if x & y = x & z then y = z.

  (1) [S2] Take the case x = nyrfex, y = ovimux, z = shennak, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R2 and R3. A later argument that quietly assumes one of these
is wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 1.
  x001. Evaluate nyrfex & nyrfex.
  x002. Work out the value of nyrfex & ovimux.
Level 2.
  x003. Evaluate (nyrfex & ovimux) & nyrfex.
  x004. Evaluate ovimux & ovimux $ ovimux.
  x005. Evaluate nyrfex^2.
  x006. What is nyrfex combined with itself 3 times under &?
  x007. What is ovimux combined with itself 3 times under &?
  x008. Solve x & shennak = shennak for x, naming every solution.
Level 3.
  x009. Evaluate ovimux & nyrfex $ nyrfex, minding which operation binds tighter.
Level 5.
  x011. The following fails in this system: For every xilzam x: x & x = x. Name the earliest xilzam, in the order the xilzams were introduced, that witnesses the failure.
  x012. The following fails in this system: For all xilzams x, y, z: if x & y = x & z then y = z. Name the earliest xilzam, in the order the xilzams were introduced, that witnesses the failure.

# Chapter 2. Neutral objects and reversal

## Why this chapter

The practical content of this chapter is a neutral object for the first operation, an
absorbing object for the first operation and the system does not have reversal under the
first operation. It is the part that shows up in use.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about xilzams covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A4. A neutral object for the first operation. There is a xilzam muxovi with muxovi & x =
x & muxovi = x for every x.

A5. An absorbing object for the first operation. There is a xilzam shennak with shennak
& x = x & shennak = shennak for every x.

## The shape of it

The neutral xilzam muxovi is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 xilzams the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R1 rests on S2 (the Opalopal combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take (ovimux & muxovi) & (nyrfex & shennak) and work it out one step at a time.
    ovimux & muxovi = ovimux   (the table for &)
    nyrfex & shennak = shennak   (the table for &)
    ovimux & shennak = shennak   (the table for &)
The expression comes to shennak.

A companion case, muxovi & (nyrfex & ovimux), to show what the brackets are doing.
    nyrfex & ovimux = shennak   (the table for &)
    muxovi & shennak = shennak   (the table for &)
That gives shennak, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
muxovi <| shennak hold? Read off what muxovi stands over: muxovi, nyrfex, ovimux and
shennak. shennak is among them, so it holds.

## A case that breaks

R1. Some xilzam x admits no xilzam y for which x & y and y & x both land on a neutral
object. The case that settles it: x = nyrfex. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside S2 (the Opalopal combination tables).

What is built on it later: D5 (the minak) and T1 (the minak is the only one of its
kind).

## Proofs

R1. Some xilzam x admits no xilzam y for which x & y and y & x both land on a neutral object.

  (1) [S2] Take the case x = nyrfex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R1. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 5.
  x010. The following fails in this system: Some xilzam x admits no xilzam y for which x & y and y & x both land on a neutral object. Name the earliest xilzam, in the order the xilzams were introduced, that witnesses the failure.

# Chapter 3. The relation and what it orders

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through antisymmetry of the relation,
transitivity of the relation and comparability of every pair.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
xilzams that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A10. Antisymmetry of the relation. For all xilzams x and y: if x <| y and y <| x then x
= y.

A11. Transitivity of the relation. For all xilzams x, y, z: if x <| y and y <| z then x
<| z.

A12. Comparability of every pair. For all xilzams x and y, at least one of x <| y and y
<| x holds.

A13. Agreement of the relation with the first operation. For all xilzams x, y, z: if x
<| y then (z & x) <| (z & y) and (x & z) <| (y & z).

A14. Agreement of the relation with the second operation. For all xilzams x, y, z: if x
<| y then (z $ x) <| (z $ y) and (x $ z) <| (y $ z).

A9. Reflexivity of the relation. For every xilzam x: x <| x.

D4. The mivint of a xilzam. The mivint of a xilzam x is the collection of xilzams y for
which x <| y holds.

Worked out for each xilzam: muxovi to muxovi, nyrfex, ovimux and shennak; nyrfex to
nyrfex, ovimux and shennak; ovimux to ovimux and shennak; shennak to shennak.

## The shape of it

The relation is easiest to see as a height. Each xilzam casts a mivint over what it
yields to, and the sizes of those shadows here are 1, 2, 3 and 4. No two are the same
size, so the objects line up in a single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 xilzams the table is short enough to consult every time.

## Where these results come from

Nothing is derived in this chapter. It lays down material that later chapters draw on.

## A worked case

Here is shennak & ovimux $ nyrfex, reduced without skipping anything.
    ovimux $ nyrfex = nyrfex   (the table for $)
    shennak & nyrfex = shennak   (the table for &)
The expression comes to shennak.

Bracketing is not cosmetic, so here is ovimux & (nyrfex & shennak) for contrast.
    nyrfex & shennak = shennak   (the table for &)
    ovimux & shennak = shennak   (the table for &)
That gives shennak, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
ovimux <| shennak hold? Read off what ovimux stands over: ovimux and shennak. shennak is
among them, so it holds.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of xilzams that come back
unchanged from themselves: muxovi and shennak. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: S2 (the Opalopal combination tables).

These results are used again in D9 (a umbmux), D13 (duthtu pairs), T9 (mivints are
nested along the relation) and T10 (there is at most one umbmux).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

New vocabulary from this chapter: the mivint of a xilzam. Each of these is used by name
later, so the names are worth learning rather than looking up.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x017. List the mivint of muxovi.
  x018. Which xilzams y satisfy nyrfex <| y? Name them all.
  x019. Which xilzams y satisfy ovimux <| y? Name them all.

# Chapter 4. The second operation and how the two interact

## Why this chapter

The present chapter develops closure under the second operation, association of the
second operation and self combination under the second operation.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

The standard of proof here is exhaustion. A universal claim about xilzams covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A6. Closure under the second operation. For all xilzams x and y, x $ y is again a
xilzam.

A7. Association of the second operation. For all xilzams x, y, z: (x $ y) $ z = x $ (y $
z).

A8. Self combination under the second operation. For every xilzam x: x $ x = x.

## The shape of it

The interesting content of a two operation system sits in the gap between them: which
one distributes over which, and which xilzams are fixed by both.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R4 rests on S2 (the Opalopal combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R5 rests on S2 (the Opalopal combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R6 rests on S2 (the Opalopal combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R7 rests on S2 (the Opalopal combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Here is (muxovi & shennak) & (nyrfex & ovimux), reduced without skipping anything.
    muxovi & shennak = shennak   (the table for &)
    nyrfex & ovimux = shennak   (the table for &)
    shennak & shennak = shennak   (the table for &)
So (muxovi & shennak) & (nyrfex & ovimux) is shennak.

Bracketing is not cosmetic, so here is shennak & (nyrfex & muxovi) for contrast.
    nyrfex & muxovi = nyrfex   (the table for &)
    shennak & nyrfex = shennak   (the table for &)
The value is shennak. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test shennak <| nyrfex. The mivint of shennak is shennak, and nyrfex lies outside it, so
the relation fails.

## A case that breaks

R4. It is not the case that: For all xilzams x and y: x $ y = y $ x. It fails at x =
muxovi, y = nyrfex, left = nyrfex, right = muxovi. One case is enough, and this is the
earliest one.

R5. There is no xilzam that leaves every xilzam unchanged under the second operation.
The case that settles it: reason = no two sided identity exists. Anyone carrying this
claim over from a more familiar system will be wrong here, and wrong in a way that
propagates.

R6. It is not the case that: For all xilzams x, y, z: x $ (y & z) = (x $ y) & (x $ z),
and the same on the right. The case that settles it: x = nyrfex, y = muxovi, z = muxovi,
left = nyrfex, right = ovimux. Anyone carrying this claim over from a more familiar
system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: S2 (the Opalopal combination tables).

These results are used again in T15 (the second operation keeps the sibnak intact).

## Proofs

R4. It is not the case that: For all xilzams x and y: x $ y = y $ x.

  (1) [S2] Take the case x = muxovi, y = nyrfex, left = nyrfex, right = muxovi, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R5. There is no xilzam that leaves every xilzam unchanged under the second operation.

  (1) [S2] Take the case reason = no two sided identity exists, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R6. It is not the case that: For all xilzams x, y, z: x $ (y & z) = (x $ y) & (x $ z), and the same on the right.

  (1) [S2] Take the case x = nyrfex, y = muxovi, z = muxovi, left = nyrfex, right = ovimux, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R7. It is not the case that: For all xilzams x and y: x & (x $ y) = x and x $ (x & y) = x.

  (1) [S2] Take the case x = muxovi, y = nyrfex, value = nyrfex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R4, R5, R6 and R7. A later argument that quietly assumes one
of these is wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 5.
  x013. The following fails in this system: For all xilzams x and y: x $ y = y $ x. Name the earliest xilzam, in the order the xilzams were introduced, that witnesses the failure.
  x014. The following fails in this system: For all xilzams x and y: x & (x $ y) = x and x $ (x & y) = x. Name the earliest xilzam, in the order the xilzams were introduced, that witnesses the failure.

# Chapter 5. Combining objects

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is thrami xilzams,
xilzams that reldjen and the minak.

Prerequisites are real here: chapters 1 and 2 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over xilzams, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D1. Thrami xilzams. A xilzam x is called thrami when x & x = x.

In this system that picks out muxovi and shennak, which is 2 of the 4 xilzams.

D2. Xilzams that reldjen. Two xilzams x and y are said to reldjen when x & y = y & x.

D5. The minak. The xilzam muxovi is called the minak of the system. It is the unique
xilzam that leaves every xilzam unchanged under &.

Here that is muxovi.

## The shape of it

Two questions sort the xilzams quickly. Does combining a xilzam with itself change it?
For muxovi and shennak it does not. Does it matter which side it goes on? For muxovi,
nyrfex, ovimux and shennak it does not.

Neutrality is a strong condition disguised as a weak one. It fixes a single xilzam and,
through that, constrains everything that can combine with it.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

This chapter is groundwork. The derivations that use it start in the next one.

## A worked case

Evaluate shennak & muxovi $ ovimux. Each line below is one lookup in a table.
    muxovi $ ovimux = ovimux   (the table for $)
    shennak & ovimux = shennak   (the table for &)
That leaves shennak, and no other reading of the notation gives anything else.

A companion case, muxovi & (ovimux & shennak), to show what the brackets are doing.
    ovimux & shennak = shennak   (the table for &)
    muxovi & shennak = shennak   (the table for &)
That gives shennak, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test shennak <| ovimux. The mivint of shennak is shennak, and ovimux lies outside it, so
the relation fails.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of xilzams that come back
unchanged from themselves: muxovi and shennak. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by a neutral object for the first operation and closure under the
first operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A1 (closure under the first operation) and A4 (a neutral object for the
first operation).

What is built on it later: D6 (the sibnak), D7 (the mornmi), D10 (tuvor xilzams) and T1
(the minak is the only one of its kind).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

Carry forward thrami xilzams, xilzams that reldjen and the minak. Later chapters state
their results in these terms and do not restate the definitions.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 2.
  x020. Name the minak of the system.
Level 3.
  x015. Write down the thrami in full.

# Chapter 6. The relation and what it orders (2)

## Why this chapter

The results collected here were not found in this order. Duthtu pairs, hurnkeld
collections and a umbmux came first, and the rest was assembled around that once the
pattern was visible.

Nothing here stands on its own. The arguments lean on chapters 1 and 3, and a reader who
has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over xilzams, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D13. Duthtu pairs. Two distinct xilzams x and y form a duthtu pair when x <| y and y <|
x both hold, that is, when each lies in the mivint of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D3. Hurnkeld collections. A collection S of xilzams is hurnkeld when x & y belongs to S
for every pair x, y drawn from S.

D9. A umbmux. A xilzam f is a umbmux when f <| y holds for every xilzam y, that is, when
the mivint of f is the whole system.

Running the definition over every xilzam leaves muxovi.

## The shape of it

Picture the ponwren as what happens when you start with one xilzam and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 4 xilzams, that stops. In this system the sizes it stops at are 1, 2 and 3.

Think of <| as pointing downhill. The mivint of a xilzam is everything downhill of it,
and those shadows here have sizes 1, 2, 3 and 4.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R11 rests on D4 (the mivint of a xilzam). Remove any one of them and the statement stops
making sense, not merely stops being provable.

T12 rests on D4 (the mivint of a xilzam) and A13 (agreement of the relation with the
first operation). The dependence is on the content of those results, not only on their
vocabulary.

T9 rests on D4 (the mivint of a xilzam) and A11 (transitivity of the relation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Here is (muxovi & ovimux) & (shennak & nyrfex), reduced without skipping anything.
    muxovi & ovimux = ovimux   (the table for &)
    shennak & nyrfex = shennak   (the table for &)
    ovimux & shennak = shennak   (the table for &)
That leaves shennak, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take ovimux & (shennak & muxovi).
    shennak & muxovi = shennak   (the table for &)
    ovimux & shennak = shennak   (the table for &)
The value is shennak. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test muxovi <| shennak. The mivint of muxovi is muxovi, nyrfex, ovimux and shennak, and
shennak lies inside it, so the relation holds.

## A case that breaks

R11. It is not the case that: If x <| y then y <| x. It fails at x = muxovi, y = nyrfex.
One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by agreement of the relation with the first operation, closure under
the first operation and transitivity of the relation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A1 (closure under the first operation), A11 (transitivity of the
relation), A13 (agreement of the relation with the first operation) and D4 (the mivint
of a xilzam).

These results are used again in D8 (the ponwren of a xilzam), T3 (the sibnak is
hurnkeld), T4 (the ponwren of a xilzam is hurnkeld) and T8 (the mornmi is hurnkeld).

## Proofs

R11. It is not the case that: If x <| y then y <| x.

  (1) [S2] Take the case x = muxovi, y = nyrfex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 16 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T12. If x <| y then (x & z) <| (y & z) for every xilzam z.

  (1) [D4] Let y lie in the mivint of x.
  (2) [A13] Compatibility applies the operation to both sides at once.
  (3) Nothing else is needed, since z was arbitrary.

Checked over 64 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T9. If y lies in the mivint of x, then the mivint of y is contained in the mivint of x.

  (1) [D4] Let y satisfy x <| y and let z satisfy y <| z.
  (2) [A11] Transitivity gives x <| z.
  (3) [D4] So every member of the mivint of y is a member of that of x.

Checked over 64 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward duthtu pairs, hurnkeld collections and a umbmux. Later chapters state
their results in these terms and do not restate the definitions.

Established here and safe to use: T12 and T9.

Do not carry forward R11. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x016. How many xilzams lie in the smallest hurnkeld collection containing nyrfex?
Level 4.
  x026. List every xilzam in the umbmux.
  x038. The result above concerns mivints. List the mivint of muxovi.
  x039. The result above concerns mivints. List the mivint of nyrfex.
  x040. The result above concerns mivints. List the mivint of ovimux.
Level 5.
  x043. The following fails in this system: If x <| y then y <| x. Name the earliest xilzam, in the order the xilzams were introduced, that witnesses the failure.

# Chapter 7. Neutral objects and reversal (2)

## Why this chapter

The practical content of this chapter is tuvor xilzams, the sibnak and the mornmi. It is
the part that shows up in use.

Prerequisites are real here: chapters 2 and 5 supply the notions the statements below
are phrased in.

The standard of proof here is exhaustion. A universal claim about xilzams covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D10. Tuvor xilzams. A xilzam x is tuvor when x & x equals the minak.

Running the definition over every xilzam leaves muxovi.

D6. The sibnak. The sibnak of the system is the collection of xilzams that reldjen with
every xilzam.

In this system that picks out muxovi, nyrfex, ovimux and shennak, that is, all of them.

D7. The mornmi. The mornmi is the collection of all thrami xilzams.

Running the definition over every xilzam leaves muxovi and shennak.

## The shape of it

A useful mental split: some xilzams are inert under the operation and some are not.
muxovi and shennak come back unchanged when combined with themselves, and muxovi,
nyrfex, ovimux and shennak commute with everything.

The neutral xilzam muxovi is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 xilzams the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R12 rests on D5 (the minak). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T1 rests on D5 (the minak) and A4 (a neutral object for the first operation). The
dependence is on the content of those results, not only on their vocabulary.

## A worked case

Evaluate nyrfex & shennak $ ovimux. Each line below is one lookup in a table.
    shennak $ ovimux = ovimux   (the table for $)
    nyrfex & ovimux = shennak   (the table for &)
So nyrfex & shennak $ ovimux is shennak.

Bracketing is not cosmetic, so here is shennak & (ovimux & nyrfex) for contrast.
    ovimux & nyrfex = shennak   (the table for &)
    shennak & shennak = shennak   (the table for &)
The value is shennak. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test ovimux <| muxovi. The mivint of ovimux is ovimux and shennak, and muxovi lies
outside it, so the relation fails.

## A case that breaks

R12. It is not the case that: e & x equals the minak for every xilzam x. The case that
settles it: anchor = muxovi, x = nyrfex, value = nyrfex. Anyone carrying this claim over
from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by a neutral object for the first operation and closure under the
first operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A4 (a neutral object for the first operation),
D1 (thrami xilzams), D2 (xilzams that reldjen) and D5 (the minak).

These results are used again in T2 (the minak lies in the sibnak), T3 (the sibnak is
hurnkeld), T7 (the ponwren of a sibnak xilzam stays in the sibnak) and T8 (the mornmi is
hurnkeld).

## Proofs

R12. It is not the case that: e & x equals the minak for every xilzam x.

  (1) [S2] Take the case anchor = muxovi, x = nyrfex, value = nyrfex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 4 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T1. There is exactly one xilzam e with e & x = x & e = x for every xilzam x.

  (1) [D5] Suppose e and f both leave every xilzam unchanged.
  (2) [A4] Then e & f = f, reading e as neutral on the left.
  (3) [A4] And e & f = e, reading f as neutral on the right.
  (4) So e = f, and the two suppositions describe the same object.

Checked over 16 cases: every object paired with every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward tuvor xilzams, the sibnak and the mornmi. Later chapters state their
results in these terms and do not restate the definitions.

Established here and safe to use: T1.

Explicitly not available: R12. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x021. Which xilzams make up the mornmi? Name them all.
  x027. List every xilzam in the tuvor.
Level 5.
  x044. The following fails in this system: e & x equals the minak for every xilzam x. Name the earliest xilzam, in the order the xilzams were introduced, that witnesses the failure.

# Chapter 8. The relation and what it orders (3)

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through the ponwren of a xilzam, there
is at most one umbmux and the system has a umbmux.

Prerequisites are real here: chapters 3 and 6 supply the notions the statements below
are phrased in.

The standard of proof here is exhaustion. A universal claim about xilzams covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

## What is defined here

D8. The ponwren of a xilzam. The ponwren of a xilzam x, written [x], is the smallest
hurnkeld collection that contains x.

Worked out for each xilzam: muxovi to muxovi; nyrfex to nyrfex, ovimux and shennak;
ovimux to ovimux and shennak; shennak to shennak.

## The shape of it

Picture the ponwren as what happens when you start with one xilzam and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 4 xilzams, that stops. In this system the sizes it stops at are 1, 2 and 3.

The relation is easiest to see as a height. Each xilzam casts a mivint over what it
yields to, and the sizes of those shadows here are 1, 2, 3 and 4. No two are the same
size, so the objects line up in a single file.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T10 rests on D9 (a umbmux) and A10 (antisymmetry of the relation). The dependence is on
the content of those results, not only on their vocabulary.

T11 rests on D9 (a umbmux) and A12 (comparability of every pair). Remove any one of them
and the statement stops making sense, not merely stops being provable.

T13 rests on D13 (duthtu pairs) and A10 (antisymmetry of the relation). Remove any one
of them and the statement stops making sense, not merely stops being provable.

## A worked case

Evaluate (shennak & nyrfex) & (muxovi & ovimux). Each line below is one lookup in a
table.
    shennak & nyrfex = shennak   (the table for &)
    muxovi & ovimux = ovimux   (the table for &)
    shennak & ovimux = shennak   (the table for &)
So (shennak & nyrfex) & (muxovi & ovimux) is shennak.

A companion case, nyrfex & (muxovi & shennak), to show what the brackets are doing.
    muxovi & shennak = shennak   (the table for &)
    nyrfex & shennak = shennak   (the table for &)
That gives shennak, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test muxovi <| ovimux. The mivint of muxovi is muxovi, nyrfex, ovimux and shennak, and
ovimux lies inside it, so the relation holds.

Now compute [ovimux]. Fold ovimux against itself, then fold whatever appeared against
everything present, and stop when a round adds nothing. The result is ovimux and
shennak, of size 2.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of antisymmetry of the relation, closure
under the first operation and comparability of every pair. Those are properties of this
system, not of systems in general.

That is not a rhetorical caution. Take the same 4 objects, the same symbols, and a
different table, and T10 and T13 stop holding. The notation survives the substitution
and the mathematics does not.

## Neighbouring results

Read alongside A10 (antisymmetry of the relation), A12 (comparability of every pair),
D13 (duthtu pairs) and D3 (hurnkeld collections).

These results are used again in D11 (the falisk of a xilzam), T4 (the ponwren of a
xilzam is hurnkeld), T5 (the ponwren is contained in every hurnkeld collection) and T7
(the ponwren of a sibnak xilzam stays in the sibnak).

## Proofs

T10. No two distinct xilzams can both be umbmuxs.

  (1) [D9] Let f and h both be floors.
  (2) [D9] Then f <| h, since h is any object, and h <| f likewise.
  (3) [A10] Antisymmetry forces f = h.

Checked over 16 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T11. Some xilzam umbmuxs the whole system.

  (1) [A12] Every pair is comparable, so the relation orders the objects into a line.
  (2) [D9] The claim is that the line has a bottom.
  (3) The carrier is finite, so the search over candidates terminates.

Checked over 16 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T13. No two distinct xilzams lie in each other's mivint.

  (1) [D13] Suppose x and y form a tight pair.
  (2) [A10] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 16 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the ponwren of a xilzam. Each of these is used by name
later, so the names are worth learning rather than looking up.

Established here and safe to use: T10, T11 and T13.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x022. List the ponwren of nyrfex.
  x023. List the ponwren of ovimux.
Level 4.
  x024. Let z be ovimux & nyrfex. List the ponwren of z.
  x025. Let z be nyrfex & ovimux. List the ponwren of z.
  x041. Name the xilzams that make up the umbmux, which is what the result above is a claim about.

# Chapter 9. Combining objects (2)

## Why this chapter

We turn to where every xilzam is thrami breaks down, every xilzam lies in the sibnak and
the minak lies in the sibnak. The treatment is self contained given the material already
established.

Prerequisites are real here: chapters 1, 5, 6 and 7 supply the notions the statements
below are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
xilzams that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

A useful mental split: some xilzams are inert under the operation and some are not.
muxovi and shennak come back unchanged when combined with themselves, and muxovi,
nyrfex, ovimux and shennak commute with everything.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R9 rests on D7 (the mornmi). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T14 rests on D6 (the sibnak). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T2 rests on D5 (the minak) and D6 (the sibnak). Remove any one of them and the statement
stops making sense, not merely stops being provable.

T3 rests on D6 (the sibnak), D3 (hurnkeld collections) and A2 (association of the first
operation). Remove any one of them and the statement stops making sense, not merely
stops being provable.

T8 rests on D7 (the mornmi) and D3 (hurnkeld collections). The dependence is on the
content of those results, not only on their vocabulary.

## A worked case

Take muxovi & nyrfex $ ovimux and work it out one step at a time.
    nyrfex $ ovimux = ovimux   (the table for $)
    muxovi & ovimux = ovimux   (the table for &)
So muxovi & nyrfex $ ovimux is ovimux.

Move the brackets and the work changes. Take nyrfex & (ovimux & muxovi).
    ovimux & muxovi = ovimux   (the table for &)
    nyrfex & ovimux = shennak   (the table for &)
That gives shennak, against ovimux above.

One decision about the relation, since deciding is as much a skill as computing. Does
muxovi <| ovimux hold? Read off what muxovi stands over: muxovi, nyrfex, ovimux and
shennak. ovimux is among them, so it holds.

## A case that breaks

R9. It is not the case that: x & x = x for every xilzam x. It fails at x = nyrfex, value
= ovimux. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation and closure under the first operation. Those are
properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A2 (association of the first operation), D3
(hurnkeld collections), D5 (the minak) and D6 (the sibnak).

What is built on it later: T7 (the ponwren of a sibnak xilzam stays in the sibnak) and
T15 (the second operation keeps the sibnak intact).

## Proofs

R9. It is not the case that: x & x = x for every xilzam x.

  (1) [S2] Take the case x = nyrfex, value = ovimux, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 4 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T14. Every pair of xilzams reldjens.

  (1) [D6] The sibnak is defined by reldjening with everything.
  (2) [D2] The claim is that x & y = y & x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 16 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T2. The minak reldjens with every xilzam.

  (1) [D5] Let e be the minak and x any xilzam.
  (2) [D5] Then e & x = x and x & e = x.
  (3) [D2] So e & x = x & e, which is what it means to reldjen.
  (4) [D6] Since x was arbitrary, e belongs to the sibnak.

Checked over 4 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. If x and y both reldjen with every xilzam, then so does x & y.

  (1) [D6] Let x and y lie in the sibnak and let z be any xilzam.
  (2) [A2] Then (x & y) & z = x & (y & z).
  (3) [D6] Move z past y, then past x, using that each reldjens with everything.
  (4) [D3] So x & y reldjens with z, and the sibnak is hurnkeld.

Checked over 16 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

T8. If x and y are both thrami then so is x & y.

  (1) [D7] Let x and y be thrami.
  (2) [D1] The claim asks whether (x & y) & (x & y) returns x & y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 16 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Established here and safe to use: T14, T2, T3 and T8.

Explicitly not available: R9. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x037. Name the xilzams that make up the mornmi, which is what the result above is a claim about.
Level 5.
  x042. The following fails in this system: x & x = x for every xilzam x. Name the earliest xilzam, in the order the xilzams were introduced, that witnesses the failure.

# Chapter 10. Collections that close on themselves

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is the falisk of a
xilzam, the ponwren of a xilzam is hurnkeld and the ponwren of a sibnak xilzam stays in
the sibnak.

Nothing here stands on its own. The arguments lean on chapters 6, 7, 8 and 9, and a
reader who has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
xilzams that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D11. The falisk of a xilzam. The falisk of a xilzam x is the number of xilzams in its
ponwren [x].

Worked out for each xilzam: muxovi to 1; nyrfex to 3; ovimux to 2; shennak to 1.

## The shape of it

The right picture for ponwren is a spreading stain rather than a list. Drop one xilzam
in, apply the operation to whatever is wet, repeat. The stain here reaches 1, 2 and 3
xilzams depending on where it started.

A useful mental split: some xilzams are inert under the operation and some are not.
muxovi and shennak come back unchanged when combined with themselves, and muxovi,
nyrfex, ovimux and shennak commute with everything.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T4 rests on D8 (the ponwren of a xilzam) and D3 (hurnkeld collections). Remove any one
of them and the statement stops making sense, not merely stops being provable.

T7 rests on D8 (the ponwren of a xilzam), D6 (the sibnak) and T3 (the sibnak is
hurnkeld). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Here is (nyrfex & muxovi) & (shennak & ovimux), reduced without skipping anything.
    nyrfex & muxovi = nyrfex   (the table for &)
    shennak & ovimux = shennak   (the table for &)
    nyrfex & shennak = shennak   (the table for &)
The expression comes to shennak.

Move the brackets and the work changes. Take muxovi & (shennak & nyrfex).
    shennak & nyrfex = shennak   (the table for &)
    muxovi & shennak = shennak   (the table for &)
The value is shennak. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
nyrfex <| muxovi hold? Read off what nyrfex stands over: nyrfex, ovimux and shennak.
muxovi is not among them, so it fails.

A second case, this time a ponwren. Start from muxovi. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is muxovi, so the
falisk of muxovi is 1.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of xilzams that come back
unchanged from themselves: muxovi and shennak. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by association of the first operation and closure under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: D3 (hurnkeld collections), D6 (the sibnak), D8
(the ponwren of a xilzam) and T3 (the sibnak is hurnkeld).

These results are used again in D12 (the vashquil), T5 (the ponwren is contained in
every hurnkeld collection), T6 (a xilzam is thrami exactly when its falisk is one) and
R8 (where the falisk divides the number of xilzams breaks down).

## Proofs

T4. For every xilzam x, the collection [x] is hurnkeld.

  (1) [D8] [x] is built by taking x and closing under &.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 64 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

T7. If x lies in the sibnak then every xilzam of [x] lies in the sibnak.

  (1) [T3] The sibnak is hurnkeld.
  (2) [D8] [x] is the smallest hurnkeld collection containing x.
  (3) A smallest such collection sits inside any other, and the sibnak is one.

Checked over 16 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the falisk of a xilzam. Each of these is used by name
later, so the names are worth learning rather than looking up.

Established here and safe to use: T4 and T7.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x028. How many xilzams lie in [nyrfex]?
  x029. How many xilzams lie in [shennak]?
Level 5.
  x030. Let z be (nyrfex & muxovi) & nyrfex. What is the falisk of z?
  x031. Let z be nyrfex & muxovi $ muxovi. What is the falisk of z?
  x032. Let z be (nyrfex & nyrfex) & muxovi. What is the falisk of z?
  x033. Let z be (shennak & shennak) & ovimux. What is the falisk of z?

# Chapter 11. Collections that close on themselves (2)

## Why this chapter

The results collected here were not found in this order. The vashquil, where some xilzam
reaches every other breaks down and where the falisk divides the number of xilzams
breaks down came first, and the rest was assembled around that once the pattern was
visible.

Nothing here stands on its own. The arguments lean on chapters 5, 8 and 10, and a reader
who has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over xilzams, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D12. The vashquil. The vashquil of the system is the collection of xilzams whose falisk
is largest.

Running the definition over every xilzam leaves nyrfex.

## The shape of it

Picture the ponwren as what happens when you start with one xilzam and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 4 xilzams, that stops. In this system the sizes it stops at are 1, 2 and 3.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R10 rests on D8 (the ponwren of a xilzam) and D11 (the falisk of a xilzam). The
dependence is on the content of those results, not only on their vocabulary.

R8 rests on D11 (the falisk of a xilzam) and T4 (the ponwren of a xilzam is hurnkeld).
The dependence is on the content of those results, not only on their vocabulary.

T5 rests on D8 (the ponwren of a xilzam) and T4 (the ponwren of a xilzam is hurnkeld).
The dependence is on the content of those results, not only on their vocabulary.

T6 rests on D1 (thrami xilzams), D11 (the falisk of a xilzam) and T4 (the ponwren of a
xilzam is hurnkeld). Remove any one of them and the statement stops making sense, not
merely stops being provable.

## A worked case

Here is muxovi & nyrfex $ ovimux, reduced without skipping anything.
    nyrfex $ ovimux = ovimux   (the table for $)
    muxovi & ovimux = ovimux   (the table for &)
The expression comes to ovimux.

Bracketing is not cosmetic, so here is nyrfex & (ovimux & muxovi) for contrast.
    ovimux & muxovi = ovimux   (the table for &)
    nyrfex & ovimux = shennak   (the table for &)
That gives shennak, against ovimux above.

One decision about the relation, since deciding is as much a skill as computing. Does
muxovi <| shennak hold? Read off what muxovi stands over: muxovi, nyrfex, ovimux and
shennak. shennak is among them, so it holds.

## A case that breaks

R10. It is not the case that: There is a xilzam whose ponwren is the whole system. It
fails at largest_span = 3, size = 4. One case is enough, and this is the earliest one.

R8. It is not the case that: For every xilzam x, the falisk of x divides 4. It fails at
x = nyrfex, reach = 3, size = 4. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by closure under the first operation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside D1 (thrami xilzams), D11 (the falisk of a xilzam), D8 (the ponwren of a
xilzam) and T4 (the ponwren of a xilzam is hurnkeld).

## Proofs

R10. It is not the case that: There is a xilzam whose ponwren is the whole system.

  (1) [S2] Take the case largest_span = 3, size = 4, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 4 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

R8. It is not the case that: For every xilzam x, the falisk of x divides 4.

  (1) [S2] Take the case x = nyrfex, reach = 3, size = 4, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 4 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T5. If S is hurnkeld and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 28 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T6. x & x = x holds if and only if [x] contains x alone.

  (1) [D1] If x & x = x then {x} is already closed under &.
  (2) [T4] So [x] = {x} and the falisk is one.
  (3) [D11] Conversely a span of one object must contain x & x, which is then x.

Checked over 4 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the vashquil. Later chapters state their results in these terms and do not
restate the definitions.

The results now available are T5 and T6, each settled by exhaustive check rather than by
argument from analogy.

Explicitly not available: R10 and R8. A later argument that quietly assumes one of these
is wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x034. Which xilzams make up the vashquil? Name them all.
  x035. What is the largest falisk any xilzam has?
Level 5.
  x036. The following fails in this system: For every xilzam x, the falisk of x divides 4. Name the earliest xilzam, in the order the xilzams were introduced, that witnesses the failure.

# Chapter 12. The second operation and how the two interact (2)

## Why this chapter

Anyone using this system to keep track of something will meet the second operation keeps
the sibnak intact early, whether or not they go looking.

Nothing here stands on its own. The arguments lean on chapters 4, 7 and 9, and a reader
who has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over xilzams, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

With two operations the question stops being what each does and becomes how they
interfere. $ binds tighter, so the interference shows up whenever a bracket is left off.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 xilzams the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T15 rests on D6 (the sibnak), A6 (closure under the second operation) and T3 (the sibnak
is hurnkeld). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Here is (shennak & ovimux) & (nyrfex & muxovi), reduced without skipping anything.
    shennak & ovimux = shennak   (the table for &)
    nyrfex & muxovi = nyrfex   (the table for &)
    shennak & nyrfex = shennak   (the table for &)
That leaves shennak, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take ovimux & (nyrfex & shennak).
    nyrfex & shennak = shennak   (the table for &)
    ovimux & shennak = shennak   (the table for &)
That gives shennak, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
shennak <| nyrfex hold? Read off what shennak stands over: shennak. nyrfex is not among
them, so it fails.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of xilzams that come back
unchanged from themselves: muxovi and shennak. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by association of the first operation, closure under the first
operation and closure under the second operation. A system without them is not a system
where these results are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A6 (closure under the second operation), D6 (the
sibnak) and T3 (the sibnak is hurnkeld).

## Proofs

T15. If x and y lie in the sibnak then so does x $ y.

  (1) [T3] The sibnak is already hurnkeld under &.
  (2) [A6] The second operation is defined on every pair.
  (3) [D6] The claim is that $ respects the sibnak as well.

Checked over 16 cases: every ordered pair from the core. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

The results now available are T15, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

No exercises here. Every question this chapter suggested turned out to be answerable
from the question itself, so all of them were discarded.
