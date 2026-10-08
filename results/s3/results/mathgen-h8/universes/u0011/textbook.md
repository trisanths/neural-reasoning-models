# The Vintreld system

What follows is a complete account of the Vintreld system. It is complete in a strong
sense: the system has 6 aztfals and finitely many facts, and every one of those facts is
settled here by inspection rather than left to argument.

The aztfals are written korrhob, pyrnak, korrglim, lornjen, nakqen and aztclo. The first
operation is written &. The relation is written <<; where it holds between two aztfals
we say the left one yields to the right one. Both operations associate to the left when
written without brackets, and brackets override that. Repeated combination is
abbreviated: x^3 means x & x & x.

A warning that will be repeated because it is the one readers ignore: nothing here is
inherited from arithmetic. Familiar names have been avoided on purpose. Where a law of
arithmetic happens to hold it is stated and checked, and where it fails a counterexample
is given.

# Chapter 1. The objects and their notation

## Why this chapter

The present chapter develops the Vintreld signature, the Vintreld combination tables and
closure under the first operation.

The standard of proof here is exhaustion. A universal claim about aztfals covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## The tables in full

The table for &. Read the left argument down the side and the right argument across the top.

          |   korrhob    pyrnak  korrglim   lornjen    nakqen    aztclo
-----------------------------------------------------------------------
  korrhob |   korrhob    pyrnak  korrglim   lornjen    nakqen    aztclo
   pyrnak |    pyrnak    pyrnak    nakqen   lornjen    nakqen    aztclo
 korrglim |  korrglim    nakqen  korrglim    aztclo    nakqen    aztclo
  lornjen |   lornjen   lornjen    aztclo   lornjen    aztclo    aztclo
   nakqen |    nakqen    nakqen    nakqen    aztclo    nakqen    aztclo
   aztclo |    aztclo    aztclo    aztclo    aztclo    aztclo    aztclo

Every pair standing in the << relation, grouped by left argument.

  korrhob << korrhob
  pyrnak << korrhob and pyrnak
  korrglim << korrhob and korrglim
  lornjen << korrhob, pyrnak and lornjen
  nakqen << korrhob, pyrnak, korrglim and nakqen
  aztclo << korrhob, pyrnak, korrglim, lornjen, nakqen and aztclo

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A1. Closure under the first operation. For all aztfals x and y, x & y is again a aztfal.

A2. Association of the first operation. For all aztfals x, y, z: (x & y) & z = x & (y &
z).

A3. Commutation of the first operation. For all aztfals x and y: x & y = y & x.

A5. Self combination under the first operation. For every aztfal x: x & x = x.

## The shape of it

A useful mental split: some aztfals are inert under the operation and some are not.
korrhob, pyrnak, korrglim, lornjen, nakqen and aztclo come back unchanged when combined
with themselves, and korrhob, pyrnak, korrglim, lornjen, nakqen and aztclo commute with
everything.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R2 rests on S2 (the Vintreld combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take (korrglim & aztclo) & pyrnak and work it out one step at a time.
    korrglim & aztclo = aztclo   (the table for &)
    aztclo & pyrnak = aztclo   (the table for &)
The expression comes to aztclo.

Move the brackets and the work changes. Take aztclo & (pyrnak & korrglim).
    pyrnak & korrglim = nakqen   (the table for &)
    aztclo & nakqen = aztclo   (the table for &)
The value is aztclo. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test nakqen << korrhob. The tezmi of nakqen is korrhob, pyrnak, korrglim and nakqen, and
korrhob lies inside it, so the relation holds.

## A case that breaks

R2. It is not the case that: For all aztfals x, y, z: if x & y = x & z then y = z. The
case that settles it: x = pyrnak, y = korrhob, z = pyrnak. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

What is built on it later: A4 (a neutral object for the first operation), A6 (an
absorbing object for the first operation), A7 (reflexivity of the relation) and A8
(antisymmetry of the relation).

## Proofs

R2. It is not the case that: For all aztfals x, y, z: if x & y = x & z then y = z.

  (1) [S2] Take the case x = pyrnak, y = korrhob, z = pyrnak, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R2. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 2.
  x001. What aztfal does (lornjen & korrglim) & pyrnak name?
  x005. Which aztfals x satisfy x & pyrnak = nakqen? List them all.
  x006. Solve x & aztclo = aztclo for x, naming every solution.
  x007. Which aztfals x satisfy x & korrglim = nakqen? List them all.
Level 3.
  x002. Reduce (nakqen & nakqen) & (nakqen & lornjen) to a single aztfal.
  x003. Work out the value of (korrglim & korrhob) & (pyrnak & pyrnak).
  x004. What aztfal does (nakqen & nakqen) & (lornjen & lornjen) name?
Level 5.
  x009. The following fails in this system: For all aztfals x, y, z: if x & y = x & z then y = z. Name the earliest aztfal, in the order the aztfals were introduced, that witnesses the failure.

# Chapter 2. Neutral objects and reversal

## Why this chapter

Work through this chapter with the tables in front of you. It covers a neutral object
for the first operation, an absorbing object for the first operation and the system does
not have reversal under the first operation, and each claim can be checked by hand.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
aztfals that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A4. A neutral object for the first operation. There is a aztfal korrhob with korrhob & x
= x & korrhob = x for every x.

A6. An absorbing object for the first operation. There is a aztfal aztclo with aztclo &
x = x & aztclo = aztclo for every x.

## The shape of it

Neutrality is a strong condition disguised as a weak one. It fixes a single aztfal and,
through that, constrains everything that can combine with it.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R1 rests on S2 (the Vintreld combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take (korrglim & nakqen) & (aztclo & pyrnak) and work it out one step at a time.
    korrglim & nakqen = nakqen   (the table for &)
    aztclo & pyrnak = aztclo   (the table for &)
    nakqen & aztclo = aztclo   (the table for &)
So (korrglim & nakqen) & (aztclo & pyrnak) is aztclo.

A companion case, nakqen & (aztclo & korrglim), to show what the brackets are doing.
    aztclo & korrglim = aztclo   (the table for &)
    nakqen & aztclo = aztclo   (the table for &)
That gives aztclo, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test lornjen << korrglim. The tezmi of lornjen is korrhob, pyrnak and lornjen, and
korrglim lies outside it, so the relation fails.

## A case that breaks

R1. Some aztfal x admits no aztfal y for which x & y and y & x both land on a neutral
object. It fails at x = pyrnak. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside S2 (the Vintreld combination tables).

These results are used again in D5 (the nyrvor) and T1 (the nyrvor is the only one of
its kind).

## Proofs

R1. Some aztfal x admits no aztfal y for which x & y and y & x both land on a neutral object.

  (1) [S2] Take the case x = pyrnak, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R1. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 5.
  x008. The following fails in this system: Some aztfal x admits no aztfal y for which x & y and y & x both land on a neutral object. Name the earliest aztfal, in the order the aztfals were introduced, that witnesses the failure.

# Chapter 3. The relation and what it orders

## Why this chapter

What follows was pieced together backwards. The last item of it, agreement of the
relation with the first operation, reflexivity of the relation and antisymmetry of the
relation, was noticed before anyone had a reason to expect it.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

One habit to adopt: when a statement below quantifies over aztfals, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A10. Agreement of the relation with the first operation. For all aztfals x, y, z: if x
<< y then (z & x) << (z & y) and (x & z) << (y & z).

A7. Reflexivity of the relation. For every aztfal x: x << x.

A8. Antisymmetry of the relation. For all aztfals x and y: if x << y and y << x then x =
y.

A9. Transitivity of the relation. For all aztfals x, y, z: if x << y and y << z then x
<< z.

D4. The tezmi of a aztfal. The tezmi of a aztfal x is the collection of aztfals y for
which x << y holds.

Worked out for each aztfal: korrhob to korrhob; pyrnak to korrhob and pyrnak; korrglim
to korrhob and korrglim; lornjen to korrhob, pyrnak and lornjen; nakqen to korrhob,
pyrnak, korrglim and nakqen; aztclo to korrhob, pyrnak, korrglim, lornjen, nakqen and
aztclo.

## The shape of it

The relation is easiest to see as a height. Each aztfal casts a tezmi over what it
yields to, and the sizes of those shadows here are 1, 2, 3, 4 and 6. Sizes repeat, so
the objects do not line up in single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 aztfals the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R3 rests on S2 (the Vintreld combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Take (lornjen & korrhob) & pyrnak and work it out one step at a time.
    lornjen & korrhob = lornjen   (the table for &)
    lornjen & pyrnak = lornjen   (the table for &)
The expression comes to lornjen.

Move the brackets and the work changes. Take korrhob & (pyrnak & lornjen).
    pyrnak & lornjen = lornjen   (the table for &)
    korrhob & lornjen = lornjen   (the table for &)
That gives lornjen, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test aztclo << aztclo. The tezmi of aztclo is korrhob, pyrnak, korrglim, lornjen, nakqen
and aztclo, and aztclo lies inside it, so the relation holds.

## A case that breaks

R3. It is not the case that: For all aztfals x and y, at least one of x << y and y << x
holds. The case that settles it: x = pyrnak, y = korrglim. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: S2 (the Vintreld combination tables).

What is built on it later: D9 (a tarntez), D13 (grixespa pairs), T10 (tezmis are nested
along the relation) and T11 (there is at most one tarntez).

## Proofs

R3. It is not the case that: For all aztfals x and y, at least one of x << y and y << x holds.

  (1) [S2] Take the case x = pyrnak, y = korrglim, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the tezmi of a aztfal. Each of these is used by name
later, so the names are worth learning rather than looking up.

Explicitly not available: R3. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x013. Which aztfals y satisfy pyrnak << y? Name them all.
  x014. List the tezmi of korrglim.
  x015. Which aztfals y satisfy lornjen << y? Name them all.
  x016. Which aztfals y satisfy nakqen << y? Name them all.
  x017. Which aztfals y satisfy aztclo << y? Name them all.

# Chapter 4. Combining objects

## Why this chapter

The practical content of this chapter is vorduth aztfals, aztfals that muxzel and the
nyrvor. It is the part that shows up in use.

Nothing here stands on its own. The arguments lean on chapters 1 and 2, and a reader who
has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about aztfals covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

## What is defined here

D1. Vorduth aztfals. A aztfal x is called vorduth when x & x = x.

In this system that picks out korrhob, pyrnak, korrglim, lornjen, nakqen and aztclo,
that is, all of them.

D2. Aztfals that muxzel. Two aztfals x and y are said to muxzel when x & y = y & x.

D5. The nyrvor. The aztfal korrhob is called the nyrvor of the system. It is the unique
aztfal that leaves every aztfal unchanged under &.

Here that is korrhob.

## The shape of it

Two questions sort the aztfals quickly. Does combining a aztfal with itself change it?
For korrhob, pyrnak, korrglim, lornjen, nakqen and aztclo it does not. Does it matter
which side it goes on? For korrhob, pyrnak, korrglim, lornjen, nakqen and aztclo it does
not.

Neutrality is a strong condition disguised as a weak one. It fixes a single aztfal and,
through that, constrains everything that can combine with it.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 aztfals the table is short enough to consult every time.

## Where these results come from

This chapter is groundwork. The derivations that use it start in the next one.

## A worked case

Evaluate (aztclo & nakqen) & (lornjen & pyrnak). Each line below is one lookup in a
table.
    aztclo & nakqen = aztclo   (the table for &)
    lornjen & pyrnak = lornjen   (the table for &)
    aztclo & lornjen = aztclo   (the table for &)
That leaves aztclo, and no other reading of the notation gives anything else.

A companion case, nakqen & (lornjen & aztclo), to show what the brackets are doing.
    lornjen & aztclo = aztclo   (the table for &)
    nakqen & aztclo = aztclo   (the table for &)
The value is aztclo. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
korrhob << pyrnak hold? Read off what korrhob stands over: korrhob. pyrnak is not among
them, so it fails.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of aztfals that come back
unchanged from themselves: korrhob, pyrnak, korrglim, lornjen, nakqen and aztclo.
Assuming more of them than that is the mistake to avoid.

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

What is built on it later: D6 (the nakpyr), D7 (the iskopal), D10 (zelgel aztfals) and
T1 (the nyrvor is the only one of its kind).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

Carry forward vorduth aztfals, aztfals that muxzel and the nyrvor. Later chapters state
their results in these terms and do not restate the definitions.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 2.
  x018. Name the nyrvor of the system.
Level 3.
  x010. Write down the vorduth in full.

# Chapter 5. The relation and what it orders (2)

## Why this chapter

So far the aztfals have been objects to be pushed around. This chapter starts asking
what they are like. We take up grixespa pairs, vintpon collections and a tarntez.

Prerequisites are real here: chapters 1 and 3 supply the notions the statements below
are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
aztfals that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D13. Grixespa pairs. Two distinct aztfals x and y form a grixespa pair when x << y and y
<< x both hold, that is, when each lies in the tezmi of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D3. Vintpon collections. A collection S of aztfals is vintpon when x & y belongs to S
for every pair x, y drawn from S.

D9. A tarntez. A aztfal f is a tarntez when f << y holds for every aztfal y, that is,
when the tezmi of f is the whole system.

In this system that picks out aztclo, which is 1 of the 6 aztfals.

## The shape of it

The right picture for quilnak is a spreading stain rather than a list. Drop one aztfal
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 aztfals
depending on where it started.

The relation is easiest to see as a height. Each aztfal casts a tezmi over what it
yields to, and the sizes of those shadows here are 1, 2, 3, 4 and 6. Sizes repeat, so
the objects do not line up in single file.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R5 rests on D4 (the tezmi of a aztfal). The dependence is on the content of those
results, not only on their vocabulary.

T10 rests on D4 (the tezmi of a aztfal) and A9 (transitivity of the relation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

T12 rests on D4 (the tezmi of a aztfal) and A10 (agreement of the relation with the
first operation). Remove any one of them and the statement stops making sense, not
merely stops being provable.

## A worked case

Evaluate (nakqen & aztclo) & lornjen. Each line below is one lookup in a table.
    nakqen & aztclo = aztclo   (the table for &)
    aztclo & lornjen = aztclo   (the table for &)
So (nakqen & aztclo) & lornjen is aztclo.

Bracketing is not cosmetic, so here is aztclo & (lornjen & nakqen) for contrast.
    lornjen & nakqen = aztclo   (the table for &)
    aztclo & aztclo = aztclo   (the table for &)
That gives aztclo, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
lornjen << pyrnak hold? Read off what lornjen stands over: korrhob, pyrnak and lornjen.
pyrnak is among them, so it holds.

## A case that breaks

R5. It is not the case that: If x << y then y << x. It fails at x = pyrnak, y = korrhob.
One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of agreement of the relation with the first
operation, closure under the first operation and transitivity of the relation. Those are
properties of this system, not of systems in general.

To see how little the notation guarantees: rebuild the system with the same names over
different tables and T12 fail outright.

## Neighbouring results

The material this chapter borrows from: A1 (closure under the first operation), A10
(agreement of the relation with the first operation), A9 (transitivity of the relation)
and D4 (the tezmi of a aztfal).

What is built on it later: D8 (the quilnak of a aztfal), T3 (the nakpyr is vintpon), T4
(the quilnak of a aztfal is vintpon) and T9 (the iskopal is vintpon).

## Proofs

R5. It is not the case that: If x << y then y << x.

  (1) [S2] Take the case x = pyrnak, y = korrhob, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T10. If y lies in the tezmi of x, then the tezmi of y is contained in the tezmi of x.

  (1) [D4] Let y satisfy x << y and let z satisfy y << z.
  (2) [A9] Transitivity gives x << z.
  (3) [D4] So every member of the tezmi of y is a member of that of x.

Checked over 216 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T12. If x << y then (x & z) << (y & z) for every aztfal z.

  (1) [D4] Let y lie in the tezmi of x.
  (2) [A10] Compatibility applies the operation to both sides at once.
  (3) Nothing else is needed, since z was arbitrary.

Checked over 216 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward grixespa pairs, vintpon collections and a tarntez. Later chapters state
their results in these terms and do not restate the definitions.

The results now available are T10 and T12, each settled by exhaustive check rather than
by argument from analogy.

Explicitly not available: R5. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x011. How many aztfals lie in the smallest vintpon collection containing pyrnak?
  x012. How many aztfals lie in the smallest vintpon collection containing korrglim?
Level 4.
  x021. Write down the tarntez in full.
  x035. The result above concerns tezmis. List the tezmi of pyrnak.
  x036. The result above concerns tezmis. List the tezmi of korrglim.
Level 5.
  x038. The following fails in this system: If x << y then y << x. Name the earliest aztfal, in the order the aztfals were introduced, that witnesses the failure.

# Chapter 6. Neutral objects and reversal (2)

## Why this chapter

The present chapter develops zelgel aztfals, the nakpyr and the iskopal.

Prerequisites are real here: chapters 2 and 4 supply the notions the statements below
are phrased in.

The standard of proof here is exhaustion. A universal claim about aztfals covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D10. Zelgel aztfals. A aztfal x is zelgel when x & x equals the nyrvor.

In this system that picks out korrhob, which is 1 of the 6 aztfals.

D6. The nakpyr. The nakpyr of the system is the collection of aztfals that muxzel with
every aztfal.

Running the definition over every aztfal leaves korrhob, pyrnak, korrglim, lornjen,
nakqen and aztclo.

D7. The iskopal. The iskopal is the collection of all vorduth aztfals.

Running the definition over every aztfal leaves korrhob, pyrnak, korrglim, lornjen,
nakqen and aztclo.

## The shape of it

A useful mental split: some aztfals are inert under the operation and some are not.
korrhob, pyrnak, korrglim, lornjen, nakqen and aztclo come back unchanged when combined
with themselves, and korrhob, pyrnak, korrglim, lornjen, nakqen and aztclo commute with
everything.

The neutral aztfal korrhob is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R6 rests on D5 (the nyrvor). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T1 rests on D5 (the nyrvor) and A4 (a neutral object for the first operation). The
dependence is on the content of those results, not only on their vocabulary.

## A worked case

Take (lornjen & korrglim) & (nakqen & korrhob) and work it out one step at a time.
    lornjen & korrglim = aztclo   (the table for &)
    nakqen & korrhob = nakqen   (the table for &)
    aztclo & nakqen = aztclo   (the table for &)
So (lornjen & korrglim) & (nakqen & korrhob) is aztclo.

Move the brackets and the work changes. Take korrglim & (nakqen & lornjen).
    nakqen & lornjen = aztclo   (the table for &)
    korrglim & aztclo = aztclo   (the table for &)
The value is aztclo. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test korrglim << korrglim. The tezmi of korrglim is korrhob and korrglim, and korrglim
lies inside it, so the relation holds.

## A case that breaks

R6. It is not the case that: e & x equals the nyrvor for every aztfal x. The case that
settles it: anchor = korrhob, x = pyrnak, value = pyrnak. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation
and closure under the first operation. Those are properties of this system, not of
systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A4 (a neutral object for the first operation),
D1 (vorduth aztfals), D2 (aztfals that muxzel) and D5 (the nyrvor).

What is built on it later: T2 (the nyrvor lies in the nakpyr), T3 (the nakpyr is
vintpon), T8 (the quilnak of a nakpyr aztfal stays in the nakpyr) and T9 (the iskopal is
vintpon).

## Proofs

R6. It is not the case that: e & x equals the nyrvor for every aztfal x.

  (1) [S2] Take the case anchor = korrhob, x = pyrnak, value = pyrnak, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T1. There is exactly one aztfal e with e & x = x & e = x for every aztfal x.

  (1) [D5] Suppose e and f both leave every aztfal unchanged.
  (2) [A4] Then e & f = f, reading e as neutral on the left.
  (3) [A4] And e & f = e, reading f as neutral on the right.
  (4) So e = f, and the two suppositions describe the same object.

Checked over 36 cases: every object paired with every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward zelgel aztfals, the nakpyr and the iskopal. Later chapters state their
results in these terms and do not restate the definitions.

Established here and safe to use: T1.

Explicitly not available: R6. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x019. List every aztfal in the nakpyr.
  x020. Which aztfals make up the iskopal? Name them all.
  x022. Which aztfals make up the zelgel? Name them all.
Level 5.
  x039. The following fails in this system: e & x equals the nyrvor for every aztfal x. Name the earliest aztfal, in the order the aztfals were introduced, that witnesses the failure.

# Chapter 7. The relation and what it orders (3)

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is the quilnak of a
aztfal, there is at most one tarntez and no grixespa pairs exist.

Prerequisites are real here: chapters 3 and 5 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over aztfals, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D8. The quilnak of a aztfal. The quilnak of a aztfal x, written [x], is the smallest
vintpon collection that contains x.

Worked out for each aztfal: korrhob to korrhob; pyrnak to pyrnak; korrglim to korrglim;
lornjen to lornjen; nakqen to nakqen; aztclo to aztclo.

## The shape of it

Picture the quilnak as what happens when you start with one aztfal and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 6 aztfals, that stops. In this system the sizes it stops at are 1.

Think of << as pointing downhill. The tezmi of a aztfal is everything downhill of it,
and those shadows here have sizes 1, 2, 3, 4 and 6.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 aztfals the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T11 rests on D9 (a tarntez) and A8 (antisymmetry of the relation). The dependence is on
the content of those results, not only on their vocabulary.

T13 rests on D13 (grixespa pairs) and A8 (antisymmetry of the relation). The dependence
is on the content of those results, not only on their vocabulary.

## A worked case

Here is (nakqen & aztclo) & korrhob, reduced without skipping anything.
    nakqen & aztclo = aztclo   (the table for &)
    aztclo & korrhob = aztclo   (the table for &)
The expression comes to aztclo.

A companion case, aztclo & (korrhob & nakqen), to show what the brackets are doing.
    korrhob & nakqen = nakqen   (the table for &)
    aztclo & nakqen = aztclo   (the table for &)
The value is aztclo. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test korrglim << pyrnak. The tezmi of korrglim is korrhob and korrglim, and pyrnak lies
outside it, so the relation fails.

Now compute [aztclo]. Fold aztclo against itself, then fold whatever appeared against
everything present, and stop when a round adds nothing. The result is aztclo, of size 1.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of aztfals that come back
unchanged from themselves: korrhob, pyrnak, korrglim, lornjen, nakqen and aztclo.
Assuming more of them than that is the mistake to avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by antisymmetry of the relation and closure under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A8 (antisymmetry of the relation), D13 (grixespa pairs), D3 (vintpon
collections) and D9 (a tarntez).

These results are used again in D11 (the duthnyr of a aztfal), T4 (the quilnak of a
aztfal is vintpon), T5 (the quilnak is contained in every vintpon collection) and T8
(the quilnak of a nakpyr aztfal stays in the nakpyr).

## Proofs

T11. No two distinct aztfals can both be tarntezs.

  (1) [D9] Let f and h both be floors.
  (2) [D9] Then f << h, since h is any object, and h << f likewise.
  (3) [A8] Antisymmetry forces f = h.

Checked over 36 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T13. No two distinct aztfals lie in each other's tezmi.

  (1) [D13] Suppose x and y form a tight pair.
  (2) [A8] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the quilnak of a aztfal. Later chapters state their results in these terms
and do not restate the definitions.

Established here and safe to use: T11 and T13.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x037. Name the aztfals that make up the tarntez, which is what the result above is a claim about.

# Chapter 8. Combining objects (2)

## Why this chapter

What follows was pieced together backwards. The last item of it, every aztfal lies in
the nakpyr, every aztfal is vorduth and the nyrvor lies in the nakpyr, was noticed
before anyone had a reason to expect it.

Prerequisites are real here: chapters 1, 4, 5 and 6 supply the notions the statements
below are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
aztfals that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

A useful mental split: some aztfals are inert under the operation and some are not.
korrhob, pyrnak, korrglim, lornjen, nakqen and aztclo come back unchanged when combined
with themselves, and korrhob, pyrnak, korrglim, lornjen, nakqen and aztclo commute with
everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 aztfals the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T14 rests on D6 (the nakpyr). The dependence is on the content of those results, not
only on their vocabulary.

T15 rests on D7 (the iskopal). The dependence is on the content of those results, not
only on their vocabulary.

T2 rests on D5 (the nyrvor) and D6 (the nakpyr). The dependence is on the content of
those results, not only on their vocabulary.

T3 rests on D6 (the nakpyr), D3 (vintpon collections) and A2 (association of the first
operation). The dependence is on the content of those results, not only on their
vocabulary.

T9 rests on D7 (the iskopal) and D3 (vintpon collections). The dependence is on the
content of those results, not only on their vocabulary.

## A worked case

Evaluate (aztclo & lornjen) & (korrglim & korrhob). Each line below is one lookup in a
table.
    aztclo & lornjen = aztclo   (the table for &)
    korrglim & korrhob = korrglim   (the table for &)
    aztclo & korrglim = aztclo   (the table for &)
The expression comes to aztclo.

Bracketing is not cosmetic, so here is lornjen & (korrglim & aztclo) for contrast.
    korrglim & aztclo = aztclo   (the table for &)
    lornjen & aztclo = aztclo   (the table for &)
That gives aztclo, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
lornjen << nakqen hold? Read off what lornjen stands over: korrhob, pyrnak and lornjen.
nakqen is not among them, so it fails.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of aztfals that come back
unchanged from themselves: korrhob, pyrnak, korrglim, lornjen, nakqen and aztclo.
Assuming more of them than that is the mistake to avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation and closure under the first operation. Those are
properties of this system, not of systems in general.

That is not a rhetorical caution. Take the same 6 objects, the same symbols, and a
different table, and T15 stop holding. The notation survives the substitution and the
mathematics does not.

## Neighbouring results

Read alongside A2 (association of the first operation), D3 (vintpon collections), D5
(the nyrvor) and D6 (the nakpyr).

What is built on it later: T8 (the quilnak of a nakpyr aztfal stays in the nakpyr).

## Proofs

T14. Every pair of aztfals muxzels.

  (1) [D6] The nakpyr is defined by muxzeling with everything.
  (2) [D2] The claim is that x & y = y & x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T15. x & x = x for every aztfal x.

  (1) [D1] Being vorduth is the condition x & x = x.
  (2) [D7] The claim is that the iskopal is the whole system.
  (3) Only the diagonal of the table is involved.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T2. The nyrvor muxzels with every aztfal.

  (1) [D5] Let e be the nyrvor and x any aztfal.
  (2) [D5] Then e & x = x and x & e = x.
  (3) [D2] So e & x = x & e, which is what it means to muxzel.
  (4) [D6] Since x was arbitrary, e belongs to the nakpyr.

Checked over 6 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. If x and y both muxzel with every aztfal, then so does x & y.

  (1) [D6] Let x and y lie in the nakpyr and let z be any aztfal.
  (2) [A2] Then (x & y) & z = x & (y & z).
  (3) [D6] Move z past y, then past x, using that each muxzels with everything.
  (4) [D3] So x & y muxzels with z, and the nakpyr is vintpon.

Checked over 36 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

T9. If x and y are both vorduth then so is x & y.

  (1) [D7] Let x and y be vorduth.
  (2) [D1] The claim asks whether (x & y) & (x & y) returns x & y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 36 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Established here and safe to use: T14, T15, T2, T3 and T9.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x031. Name the aztfals that make up the nakpyr, which is what the result above is a claim about.
  x034. This result is about the iskopal. List every aztfal in it.

# Chapter 9. Collections that close on themselves

## Why this chapter

Anyone using this system to keep track of something will meet the duthnyr of a aztfal,
the quilnak of a aztfal is vintpon and the quilnak of a nakpyr aztfal stays in the
nakpyr early, whether or not they go looking.

Prerequisites are real here: chapters 5, 6, 7 and 8 supply the notions the statements
below are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
aztfals that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D11. The duthnyr of a aztfal. The duthnyr of a aztfal x is the number of aztfals in its
quilnak [x].

Worked out for each aztfal: korrhob to 1; pyrnak to 1; korrglim to 1; lornjen to 1;
nakqen to 1; aztclo to 1.

## The shape of it

Picture the quilnak as what happens when you start with one aztfal and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 6 aztfals, that stops. In this system the sizes it stops at are 1.

A useful mental split: some aztfals are inert under the operation and some are not.
korrhob, pyrnak, korrglim, lornjen, nakqen and aztclo come back unchanged when combined
with themselves, and korrhob, pyrnak, korrglim, lornjen, nakqen and aztclo commute with
everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 aztfals the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T4 rests on D8 (the quilnak of a aztfal) and D3 (vintpon collections). Remove any one of
them and the statement stops making sense, not merely stops being provable.

T8 rests on D8 (the quilnak of a aztfal), D6 (the nakpyr) and T3 (the nakpyr is
vintpon). Remove any one of them and the statement stops making sense, not merely stops
being provable.

## A worked case

Take (korrglim & aztclo) & lornjen and work it out one step at a time.
    korrglim & aztclo = aztclo   (the table for &)
    aztclo & lornjen = aztclo   (the table for &)
The expression comes to aztclo.

A companion case, aztclo & (lornjen & korrglim), to show what the brackets are doing.
    lornjen & korrglim = aztclo   (the table for &)
    aztclo & aztclo = aztclo   (the table for &)
The value is aztclo. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
korrglim << pyrnak hold? Read off what korrglim stands over: korrhob and korrglim.
pyrnak is not among them, so it fails.

A second case, this time a quilnak. Start from lornjen. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is lornjen, so the
duthnyr of lornjen is 1.

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

Read alongside D3 (vintpon collections), D6 (the nakpyr), D8 (the quilnak of a aztfal)
and T3 (the nakpyr is vintpon).

These results are used again in D12 (the korrfex), T5 (the quilnak is contained in every
vintpon collection), T6 (a aztfal is vorduth exactly when its duthnyr is one) and T7
(the duthnyr divides the number of aztfals).

## Proofs

T4. For every aztfal x, the collection [x] is vintpon.

  (1) [D8] [x] is built by taking x and closing under &.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 216 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

T8. If x lies in the nakpyr then every aztfal of [x] lies in the nakpyr.

  (1) [T3] The nakpyr is vintpon.
  (2) [D8] [x] is the smallest vintpon collection containing x.
  (3) A smallest such collection sits inside any other, and the nakpyr is one.

Checked over 36 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the duthnyr of a aztfal. Each of these is used by name
later, so the names are worth learning rather than looking up.

Established here and safe to use: T4 and T8.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x023. How many aztfals lie in [pyrnak]?
  x024. How many aztfals lie in [korrglim]?
  x025. What is the duthnyr of lornjen?
  x026. How many aztfals lie in [nakqen]?
  x027. What is the duthnyr of aztclo?
Level 4.
  x033. Name the aztfals that make up the nakpyr, which is what the result above is a claim about.
Level 5.
  x028. Let z be (pyrnak & korrglim) & pyrnak. What is the duthnyr of z?
  x029. Let z be (nakqen & aztclo) & nakqen. What is the duthnyr of z?

# Chapter 10. Collections that close on themselves (2)

## Why this chapter

So far the aztfals have been objects to be pushed around. This chapter starts asking
what they are like. We take up the korrfex, where some aztfal reaches every other breaks
down and the quilnak is contained in every vintpon collection.

Prerequisites are real here: chapters 4, 7 and 9 supply the notions the statements below
are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
aztfals that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D12. The korrfex. The korrfex of the system is the collection of aztfals whose duthnyr
is largest.

Running the definition over every aztfal leaves korrhob, pyrnak, korrglim, lornjen,
nakqen and aztclo.

## The shape of it

The right picture for quilnak is a spreading stain rather than a list. Drop one aztfal
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 aztfals
depending on where it started.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R4 rests on D8 (the quilnak of a aztfal) and D11 (the duthnyr of a aztfal). Remove any
one of them and the statement stops making sense, not merely stops being provable.

T5 rests on D8 (the quilnak of a aztfal) and T4 (the quilnak of a aztfal is vintpon).
The dependence is on the content of those results, not only on their vocabulary.

T6 rests on D1 (vorduth aztfals), D11 (the duthnyr of a aztfal) and T4 (the quilnak of a
aztfal is vintpon). Remove any one of them and the statement stops making sense, not
merely stops being provable.

T7 rests on D11 (the duthnyr of a aztfal) and T4 (the quilnak of a aztfal is vintpon).
The dependence is on the content of those results, not only on their vocabulary.

## A worked case

Evaluate (pyrnak & korrglim) & (korrhob & lornjen). Each line below is one lookup in a
table.
    pyrnak & korrglim = nakqen   (the table for &)
    korrhob & lornjen = lornjen   (the table for &)
    nakqen & lornjen = aztclo   (the table for &)
That leaves aztclo, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is korrglim & (korrhob & pyrnak) for contrast.
    korrhob & pyrnak = pyrnak   (the table for &)
    korrglim & pyrnak = nakqen   (the table for &)
The value is nakqen, not aztclo.

Test lornjen << korrglim. The tezmi of lornjen is korrhob, pyrnak and lornjen, and
korrglim lies outside it, so the relation fails.

## A case that breaks

R4. It is not the case that: There is a aztfal whose quilnak is the whole system. It
fails at largest_span = 1, size = 6. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: D1 (vorduth aztfals), D11 (the duthnyr of a
aztfal), D8 (the quilnak of a aztfal) and T4 (the quilnak of a aztfal is vintpon).

## Proofs

R4. It is not the case that: There is a aztfal whose quilnak is the whole system.

  (1) [S2] Take the case largest_span = 1, size = 6, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T5. If S is vintpon and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 270 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T6. x & x = x holds if and only if [x] contains x alone.

  (1) [D1] If x & x = x then {x} is already closed under &.
  (2) [T4] So [x] = {x} and the duthnyr is one.
  (3) [D11] Conversely a span of one object must contain x & x, which is then x.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T7. For every aztfal x, the duthnyr of x divides 6.

  (1) [T4] [x] is a vintpon collection.
  (2) [D11] Its size is the duthnyr of x.
  (3) The claim is that this size always divides 6.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the korrfex. Later chapters state their results in these terms and do not
restate the definitions.

The results now available are T5, T6 and T7, each settled by exhaustive check rather
than by argument from analogy.

Explicitly not available: R4. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x030. Which aztfals make up the korrfex? Name them all.
  x032. What is the largest duthnyr any aztfal has?
