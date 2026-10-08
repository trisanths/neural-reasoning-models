# The Vorjen system

What follows is a complete account of the Vorjen system. It is complete in a strong
sense: the system has 6 driwrens and finitely many facts, and every one of those facts
is settled here by inspection rather than left to argument.

The driwrens are written nakquil, soltarn, muxsib, braovi, yukzel and thraisk. The first
operation is written *. The relation is written <<; where it holds between two driwrens
we say the left one precedes the right one. Both operations associate to the left when
written without brackets, and brackets override that. Repeated combination is
abbreviated: x^3 means x * x * x.

Readers arriving from arithmetic should put it down at the door. The operations below
are defined by their tables and by nothing else. Several arithmetic habits survive the
crossing and several do not, and the text is careful to say which is which.

# Chapter 1. The objects and their notation

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is the Vorjen
signature, the Vorjen combination tables and closure under the first operation.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
driwrens that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## The tables in full

The table for *. Read the left argument down the side and the right argument across the top.

         |  nakquil  soltarn   muxsib   braovi   yukzel  thraisk
----------------------------------------------------------------
 nakquil |  nakquil  soltarn   muxsib   braovi   yukzel  thraisk
 soltarn |  soltarn  soltarn   yukzel   braovi   yukzel  thraisk
  muxsib |   muxsib   yukzel   muxsib  thraisk   yukzel  thraisk
  braovi |   braovi   braovi  thraisk   braovi  thraisk  thraisk
  yukzel |   yukzel   yukzel   yukzel  thraisk   yukzel  thraisk
 thraisk |  thraisk  thraisk  thraisk  thraisk  thraisk  thraisk

Every pair standing in the << relation, grouped by left argument.

  nakquil << nakquil
  soltarn << nakquil and soltarn
  muxsib << nakquil and muxsib
  braovi << nakquil, soltarn and braovi
  yukzel << nakquil, soltarn, muxsib and yukzel
  thraisk << nakquil, soltarn, muxsib, braovi, yukzel and thraisk

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A1. Closure under the first operation. For all driwrens x and y, x * y is again a
driwren.

A2. Association of the first operation. For all driwrens x, y, z: (x * y) * z = x * (y *
z).

A3. Commutation of the first operation. For all driwrens x and y: x * y = y * x.

A5. Self combination under the first operation. For every driwren x: x * x = x.

## The shape of it

A useful mental split: some driwrens are inert under the operation and some are not.
nakquil, soltarn, muxsib, braovi, yukzel and thraisk come back unchanged when combined
with themselves, and nakquil, soltarn, muxsib, braovi, yukzel and thraisk commute with
everything.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R2 rests on S2 (the Vorjen combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Take (braovi * soltarn) * yukzel and work it out one step at a time.
    braovi * soltarn = braovi   (the table for *)
    braovi * yukzel = thraisk   (the table for *)
So (braovi * soltarn) * yukzel is thraisk.

Bracketing is not cosmetic, so here is soltarn * (yukzel * braovi) for contrast.
    yukzel * braovi = thraisk   (the table for *)
    soltarn * thraisk = thraisk   (the table for *)
The value is thraisk. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
yukzel << nakquil hold? Read off what yukzel stands over: nakquil, soltarn, muxsib and
yukzel. nakquil is among them, so it holds.

## A case that breaks

R2. It is not the case that: For all driwrens x, y, z: if x * y = x * z then y = z. The
case that settles it: x = soltarn, y = nakquil, z = soltarn. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

What is built on it later: A4 (a neutral object for the first operation), A6 (an
absorbing object for the first operation), A7 (reflexivity of the relation) and A8
(antisymmetry of the relation).

## Proofs

R2. It is not the case that: For all driwrens x, y, z: if x * y = x * z then y = z.

  (1) [S2] Take the case x = soltarn, y = nakquil, z = soltarn, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R2. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 1.
  x001. Evaluate yukzel * braovi.
Level 2.
  x002. Work out the value of (yukzel * braovi) * braovi.
  x003. Solve x * soltarn = yukzel for x, naming every solution.
  x004. Solve x * muxsib = yukzel for x, naming every solution.
  x005. Which driwrens x satisfy x * thraisk = thraisk? List them all.
  x006. Solve x * muxsib = thraisk for x, naming every solution.
Level 5.
  x008. The following fails in this system: For all driwrens x, y, z: if x * y = x * z then y = z. Name the earliest driwren, in the order the driwrens were introduced, that witnesses the failure.

# Chapter 2. Neutral objects and reversal

## Why this chapter

The results collected here were not found in this order. A neutral object for the first
operation, an absorbing object for the first operation and the system does not have
reversal under the first operation came first, and the rest was assembled around that
once the pattern was visible.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
driwrens that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A4. A neutral object for the first operation. There is a driwren nakquil with nakquil *
x = x * nakquil = x for every x.

A6. An absorbing object for the first operation. There is a driwren thraisk with thraisk
* x = x * thraisk = thraisk for every x.

## The shape of it

Neutrality is a strong condition disguised as a weak one. It fixes a single driwren and,
through that, constrains everything that can combine with it.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 driwrens the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R1 rests on S2 (the Vorjen combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Take (soltarn * yukzel) * (nakquil * thraisk) and work it out one step at a time.
    soltarn * yukzel = yukzel   (the table for *)
    nakquil * thraisk = thraisk   (the table for *)
    yukzel * thraisk = thraisk   (the table for *)
So (soltarn * yukzel) * (nakquil * thraisk) is thraisk.

A companion case, yukzel * (nakquil * soltarn), to show what the brackets are doing.
    nakquil * soltarn = soltarn   (the table for *)
    yukzel * soltarn = yukzel   (the table for *)
The value is yukzel, not thraisk.

Test muxsib << nakquil. The zelfex of muxsib is nakquil and muxsib, and nakquil lies
inside it, so the relation holds.

## A case that breaks

R1. Some driwren x admits no driwren y for which x * y and y * x both land on a neutral
object. It fails at x = soltarn. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: S2 (the Vorjen combination tables).

These results are used again in D5 (the keldtu) and T1 (the keldtu is the only one of
its kind).

## Proofs

R1. Some driwren x admits no driwren y for which x * y and y * x both land on a neutral object.

  (1) [S2] Take the case x = soltarn, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R1. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 5.
  x007. The following fails in this system: Some driwren x admits no driwren y for which x * y and y * x both land on a neutral object. Name the earliest driwren, in the order the driwrens were introduced, that witnesses the failure.

# Chapter 3. The relation and what it orders

## Why this chapter

The practical content of this chapter is agreement of the relation with the first
operation, reflexivity of the relation and antisymmetry of the relation. It is the part
that shows up in use.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
driwrens that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A10. Agreement of the relation with the first operation. For all driwrens x, y, z: if x
<< y then (z * x) << (z * y) and (x * z) << (y * z).

A7. Reflexivity of the relation. For every driwren x: x << x.

A8. Antisymmetry of the relation. For all driwrens x and y: if x << y and y << x then x
= y.

A9. Transitivity of the relation. For all driwrens x, y, z: if x << y and y << z then x
<< z.

D4. The zelfex of a driwren. The zelfex of a driwren x is the collection of driwrens y
for which x << y holds.

Worked out for each driwren: nakquil to nakquil; soltarn to nakquil and soltarn; muxsib
to nakquil and muxsib; braovi to nakquil, soltarn and braovi; yukzel to nakquil,
soltarn, muxsib and yukzel; thraisk to nakquil, soltarn, muxsib, braovi, yukzel and
thraisk.

## The shape of it

The relation is easiest to see as a height. Each driwren casts a zelfex over what it
precedes, and the sizes of those shadows here are 1, 2, 3, 4 and 6. Sizes repeat, so the
objects do not line up in single file.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R3 rests on S2 (the Vorjen combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Evaluate (nakquil * yukzel) * thraisk. Each line below is one lookup in a table.
    nakquil * yukzel = yukzel   (the table for *)
    yukzel * thraisk = thraisk   (the table for *)
The expression comes to thraisk.

Move the brackets and the work changes. Take yukzel * (thraisk * nakquil).
    thraisk * nakquil = thraisk   (the table for *)
    yukzel * thraisk = thraisk   (the table for *)
That gives thraisk, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
muxsib << nakquil hold? Read off what muxsib stands over: nakquil and muxsib. nakquil is
among them, so it holds.

## A case that breaks

R3. It is not the case that: For all driwrens x and y, at least one of x << y and y << x
holds. It fails at x = soltarn, y = muxsib. One case is enough, and this is the earliest
one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: S2 (the Vorjen combination tables).

These results are used again in D9 (a keldumb), D13 (jenfex pairs), T10 (zelfexs are
nested along the relation) and T11 (there is at most one keldumb).

## Proofs

R3. It is not the case that: For all driwrens x and y, at least one of x << y and y << x holds.

  (1) [S2] Take the case x = soltarn, y = muxsib, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the zelfex of a driwren. Each of these is used by name
later, so the names are worth learning rather than looking up.

Do not carry forward R3. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x012. List the zelfex of soltarn.
  x013. List the zelfex of muxsib.
  x014. Which driwrens y satisfy braovi << y? Name them all.
  x015. Which driwrens y satisfy yukzel << y? Name them all.
  x016. List the zelfex of thraisk.

# Chapter 4. Combining objects

## Why this chapter

So far the driwrens have been objects to be pushed around. This chapter starts asking
what they are like. We take up opalfal driwrens, driwrens that rastumb and the keldtu.

Nothing here stands on its own. The arguments lean on chapters 1 and 2, and a reader who
has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
driwrens that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D1. Opalfal driwrens. A driwren x is called opalfal when x * x = x.

In this system that picks out nakquil, soltarn, muxsib, braovi, yukzel and thraisk, that
is, all of them.

D2. Driwrens that rastumb. Two driwrens x and y are said to rastumb when x * y = y * x.

D5. The keldtu. The driwren nakquil is called the keldtu of the system. It is the unique
driwren that leaves every driwren unchanged under *.

Here that is nakquil.

## The shape of it

Two questions sort the driwrens quickly. Does combining a driwren with itself change it?
For nakquil, soltarn, muxsib, braovi, yukzel and thraisk it does not. Does it matter
which side it goes on? For nakquil, soltarn, muxsib, braovi, yukzel and thraisk it does
not.

The neutral driwren nakquil is the one that does nothing. That sounds trivial and is
not: almost every result in this chapter is an argument about what doing nothing forces.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 driwrens the table is short enough to consult every time.

## Where these results come from

Nothing is derived in this chapter. It lays down material that later chapters draw on.

## A worked case

Evaluate (nakquil * yukzel) * (thraisk * soltarn). Each line below is one lookup in a
table.
    nakquil * yukzel = yukzel   (the table for *)
    thraisk * soltarn = thraisk   (the table for *)
    yukzel * thraisk = thraisk   (the table for *)
That leaves thraisk, and no other reading of the notation gives anything else.

A companion case, yukzel * (thraisk * nakquil), to show what the brackets are doing.
    thraisk * nakquil = thraisk   (the table for *)
    yukzel * thraisk = thraisk   (the table for *)
That gives thraisk, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test braovi << thraisk. The zelfex of braovi is nakquil, soltarn and braovi, and thraisk
lies outside it, so the relation fails.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by a neutral object for the first operation and closure under the
first operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A1 (closure under the first operation) and A4 (a
neutral object for the first operation).

These results are used again in D6 (the iskkeld), D7 (the kami), D10 (muxlum driwrens)
and T1 (the keldtu is the only one of its kind).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

New vocabulary from this chapter: opalfal driwrens, driwrens that rastumb and the
keldtu. Each of these is used by name later, so the names are worth learning rather than
looking up.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 2.
  x017. Name the keldtu of the system.
Level 3.
  x009. Write down the opalfal in full.

# Chapter 5. The relation and what it orders (2)

## Why this chapter

We turn to jenfex pairs, reldshen collections and a keldumb. The treatment is self
contained given the material already established.

Nothing here stands on its own. The arguments lean on chapters 1 and 3, and a reader who
has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about driwrens covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D13. Jenfex pairs. Two distinct driwrens x and y form a jenfex pair when x << y and y <<
x both hold, that is, when each lies in the zelfex of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D3. Reldshen collections. A collection S of driwrens is reldshen when x * y belongs to S
for every pair x, y drawn from S.

D9. A keldumb. A driwren f is a keldumb when f << y holds for every driwren y, that is,
when the zelfex of f is the whole system.

Running the definition over every driwren leaves thraisk.

## The shape of it

The right picture for ovimorn is a spreading stain rather than a list. Drop one driwren
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 driwrens
depending on where it started.

The relation is easiest to see as a height. Each driwren casts a zelfex over what it
precedes, and the sizes of those shadows here are 1, 2, 3, 4 and 6. Sizes repeat, so the
objects do not line up in single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 driwrens the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R5 rests on D4 (the zelfex of a driwren). Remove any one of them and the statement stops
making sense, not merely stops being provable.

T10 rests on D4 (the zelfex of a driwren) and A9 (transitivity of the relation). The
dependence is on the content of those results, not only on their vocabulary.

T12 rests on D4 (the zelfex of a driwren) and A10 (agreement of the relation with the
first operation). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Evaluate (nakquil * thraisk) * muxsib. Each line below is one lookup in a table.
    nakquil * thraisk = thraisk   (the table for *)
    thraisk * muxsib = thraisk   (the table for *)
So (nakquil * thraisk) * muxsib is thraisk.

Bracketing is not cosmetic, so here is thraisk * (muxsib * nakquil) for contrast.
    muxsib * nakquil = muxsib   (the table for *)
    thraisk * muxsib = thraisk   (the table for *)
That gives thraisk, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test muxsib << nakquil. The zelfex of muxsib is nakquil and muxsib, and nakquil lies
inside it, so the relation holds.

## A case that breaks

R5. It is not the case that: If x << y then y << x. It fails at x = soltarn, y =
nakquil. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by agreement of the relation with the first operation, closure under
the first operation and transitivity of the relation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

That is not a rhetorical caution. Take the same 6 objects, the same symbols, and a
different table, and T12 stop holding. The notation survives the substitution and the
mathematics does not.

## Neighbouring results

Read alongside A1 (closure under the first operation), A10 (agreement of the relation
with the first operation), A9 (transitivity of the relation) and D4 (the zelfex of a
driwren).

These results are used again in D8 (the ovimorn of a driwren), T3 (the iskkeld is
reldshen), T4 (the ovimorn of a driwren is reldshen) and T9 (the kami is reldshen).

## Proofs

R5. It is not the case that: If x << y then y << x.

  (1) [S2] Take the case x = soltarn, y = nakquil, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T10. If y lies in the zelfex of x, then the zelfex of y is contained in the zelfex of x.

  (1) [D4] Let y satisfy x << y and let z satisfy y << z.
  (2) [A9] Transitivity gives x << z.
  (3) [D4] So every member of the zelfex of y is a member of that of x.

Checked over 216 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T12. If x << y then (x * z) << (y * z) for every driwren z.

  (1) [D4] Let y lie in the zelfex of x.
  (2) [A10] Compatibility applies the operation to both sides at once.
  (3) Nothing else is needed, since z was arbitrary.

Checked over 216 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: jenfex pairs, reldshen collections and a keldumb. Each
of these is used by name later, so the names are worth learning rather than looking up.

Established here and safe to use: T10 and T12.

Explicitly not available: R5. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x010. How many driwrens lie in the smallest reldshen collection containing soltarn?
  x011. How many driwrens lie in the smallest reldshen collection containing muxsib?
Level 4.
  x021. Write down the keldumb in full.
  x035. The result above concerns zelfexs. List the zelfex of soltarn.
  x036. The result above concerns zelfexs. List the zelfex of muxsib.
Level 5.
  x038. The following fails in this system: If x << y then y << x. Name the earliest driwren, in the order the driwrens were introduced, that witnesses the failure.

# Chapter 6. Neutral objects and reversal (2)

## Why this chapter

Work through this chapter with the tables in front of you. It covers muxlum driwrens,
the iskkeld and the kami, and each claim can be checked by hand.

Prerequisites are real here: chapters 2 and 4 supply the notions the statements below
are phrased in.

The standard of proof here is exhaustion. A universal claim about driwrens covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D10. Muxlum driwrens. A driwren x is muxlum when x * x equals the keldtu.

Running the definition over every driwren leaves nakquil.

D6. The iskkeld. The iskkeld of the system is the collection of driwrens that rastumb
with every driwren.

Running the definition over every driwren leaves nakquil, soltarn, muxsib, braovi,
yukzel and thraisk.

D7. The kami. The kami is the collection of all opalfal driwrens.

Running the definition over every driwren leaves nakquil, soltarn, muxsib, braovi,
yukzel and thraisk.

## The shape of it

Two questions sort the driwrens quickly. Does combining a driwren with itself change it?
For nakquil, soltarn, muxsib, braovi, yukzel and thraisk it does not. Does it matter
which side it goes on? For nakquil, soltarn, muxsib, braovi, yukzel and thraisk it does
not.

Neutrality is a strong condition disguised as a weak one. It fixes a single driwren and,
through that, constrains everything that can combine with it.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R6 rests on D5 (the keldtu). The dependence is on the content of those results, not only
on their vocabulary.

T1 rests on D5 (the keldtu) and A4 (a neutral object for the first operation). The
dependence is on the content of those results, not only on their vocabulary.

## A worked case

Take (yukzel * braovi) * (muxsib * thraisk) and work it out one step at a time.
    yukzel * braovi = thraisk   (the table for *)
    muxsib * thraisk = thraisk   (the table for *)
    thraisk * thraisk = thraisk   (the table for *)
The expression comes to thraisk.

Move the brackets and the work changes. Take braovi * (muxsib * yukzel).
    muxsib * yukzel = yukzel   (the table for *)
    braovi * yukzel = thraisk   (the table for *)
The value is thraisk. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test yukzel << soltarn. The zelfex of yukzel is nakquil, soltarn, muxsib and yukzel, and
soltarn lies inside it, so the relation holds.

## A case that breaks

R6. It is not the case that: e * x equals the keldtu for every driwren x. The case that
settles it: anchor = nakquil, x = soltarn, value = soltarn. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation
and closure under the first operation. Those are properties of this system, not of
systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A4 (a neutral object for the first operation), D1 (opalfal driwrens), D2
(driwrens that rastumb) and D5 (the keldtu).

What is built on it later: T2 (the keldtu lies in the iskkeld), T3 (the iskkeld is
reldshen), T8 (the ovimorn of a iskkeld driwren stays in the iskkeld) and T9 (the kami
is reldshen).

## Proofs

R6. It is not the case that: e * x equals the keldtu for every driwren x.

  (1) [S2] Take the case anchor = nakquil, x = soltarn, value = soltarn, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T1. There is exactly one driwren e with e * x = x * e = x for every driwren x.

  (1) [D5] Suppose e and f both leave every driwren unchanged.
  (2) [A4] Then e * f = f, reading e as neutral on the left.
  (3) [A4] And e * f = e, reading f as neutral on the right.
  (4) So e = f, and the two suppositions describe the same object.

Checked over 36 cases: every object paired with every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: muxlum driwrens, the iskkeld and the kami. Each of
these is used by name later, so the names are worth learning rather than looking up.

Established here and safe to use: T1.

Explicitly not available: R6. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x018. Write down the iskkeld in full.
  x019. Which driwrens make up the kami? Name them all.
  x022. List every driwren in the muxlum.
Level 5.
  x039. The following fails in this system: e * x equals the keldtu for every driwren x. Name the earliest driwren, in the order the driwrens were introduced, that witnesses the failure.

# Chapter 7. The relation and what it orders (3)

## Why this chapter

The results collected here were not found in this order. The ovimorn of a driwren, there
is at most one keldumb and no jenfex pairs exist came first, and the rest was assembled
around that once the pattern was visible.

Nothing here stands on its own. The arguments lean on chapters 3 and 5, and a reader who
has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about driwrens covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

## What is defined here

D8. The ovimorn of a driwren. The ovimorn of a driwren x, written [x], is the smallest
reldshen collection that contains x.

Worked out for each driwren: nakquil to nakquil; soltarn to soltarn; muxsib to muxsib;
braovi to braovi; yukzel to yukzel; thraisk to thraisk.

## The shape of it

The right picture for ovimorn is a spreading stain rather than a list. Drop one driwren
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 driwrens
depending on where it started.

Think of << as pointing downhill. The zelfex of a driwren is everything downhill of it,
and those shadows here have sizes 1, 2, 3, 4 and 6.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 driwrens the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T11 rests on D9 (a keldumb) and A8 (antisymmetry of the relation). Remove any one of
them and the statement stops making sense, not merely stops being provable.

T13 rests on D13 (jenfex pairs) and A8 (antisymmetry of the relation). The dependence is
on the content of those results, not only on their vocabulary.

## A worked case

Evaluate (soltarn * muxsib) * nakquil. Each line below is one lookup in a table.
    soltarn * muxsib = yukzel   (the table for *)
    yukzel * nakquil = yukzel   (the table for *)
The expression comes to yukzel.

Move the brackets and the work changes. Take muxsib * (nakquil * soltarn).
    nakquil * soltarn = soltarn   (the table for *)
    muxsib * soltarn = yukzel   (the table for *)
That gives yukzel, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test soltarn << nakquil. The zelfex of soltarn is nakquil and soltarn, and nakquil lies
inside it, so the relation holds.

A second case, this time a ovimorn. Start from yukzel. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is yukzel, so the
korrquil of yukzel is 1.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of antisymmetry of the relation and closure
under the first operation. Those are properties of this system, not of systems in
general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A8 (antisymmetry of the relation), D13 (jenfex
pairs), D3 (reldshen collections) and D9 (a keldumb).

What is built on it later: D11 (the korrquil of a driwren), T4 (the ovimorn of a driwren
is reldshen), T5 (the ovimorn is contained in every reldshen collection) and T8 (the
ovimorn of a iskkeld driwren stays in the iskkeld).

## Proofs

T11. No two distinct driwrens can both be keldumbs.

  (1) [D9] Let f and h both be floors.
  (2) [D9] Then f << h, since h is any object, and h << f likewise.
  (3) [A8] Antisymmetry forces f = h.

Checked over 36 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T13. No two distinct driwrens lie in each other's zelfex.

  (1) [D13] Suppose x and y form a tight pair.
  (2) [A8] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the ovimorn of a driwren. Each of these is used by
name later, so the names are worth learning rather than looking up.

Established here and safe to use: T11 and T13.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x020. Let z be muxsib * soltarn. List the ovimorn of z.
  x037. This result is about the keldumb. List every driwren in it.

# Chapter 8. Combining objects (2)

## Why this chapter

The practical content of this chapter is every driwren lies in the iskkeld, every
driwren is opalfal and the keldtu lies in the iskkeld. It is the part that shows up in
use.

Nothing here stands on its own. The arguments lean on chapters 1, 4, 5 and 6, and a
reader who has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
driwrens that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

A useful mental split: some driwrens are inert under the operation and some are not.
nakquil, soltarn, muxsib, braovi, yukzel and thraisk come back unchanged when combined
with themselves, and nakquil, soltarn, muxsib, braovi, yukzel and thraisk commute with
everything.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T14 rests on D6 (the iskkeld). The dependence is on the content of those results, not
only on their vocabulary.

T15 rests on D7 (the kami). Remove any one of them and the statement stops making sense,
not merely stops being provable.

T2 rests on D5 (the keldtu) and D6 (the iskkeld). Remove any one of them and the
statement stops making sense, not merely stops being provable.

T3 rests on D6 (the iskkeld), D3 (reldshen collections) and A2 (association of the first
operation). The dependence is on the content of those results, not only on their
vocabulary.

T9 rests on D7 (the kami) and D3 (reldshen collections). The dependence is on the
content of those results, not only on their vocabulary.

## A worked case

Evaluate (thraisk * muxsib) * (braovi * soltarn). Each line below is one lookup in a
table.
    thraisk * muxsib = thraisk   (the table for *)
    braovi * soltarn = braovi   (the table for *)
    thraisk * braovi = thraisk   (the table for *)
That leaves thraisk, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is muxsib * (braovi * thraisk) for contrast.
    braovi * thraisk = thraisk   (the table for *)
    muxsib * thraisk = thraisk   (the table for *)
That gives thraisk, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test thraisk << muxsib. The zelfex of thraisk is nakquil, soltarn, muxsib, braovi,
yukzel and thraisk, and muxsib lies inside it, so the relation holds.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of driwrens that come back
unchanged from themselves: nakquil, soltarn, muxsib, braovi, yukzel and thraisk.
Assuming more of them than that is the mistake to avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by a neutral object for the first operation, association of the
first operation and closure under the first operation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

That is not a rhetorical caution. Take the same 6 objects, the same symbols, and a
different table, and T15 stop holding. The notation survives the substitution and the
mathematics does not.

## Neighbouring results

The material this chapter borrows from: A2 (association of the first operation), D3
(reldshen collections), D5 (the keldtu) and D6 (the iskkeld).

What is built on it later: T8 (the ovimorn of a iskkeld driwren stays in the iskkeld).

## Proofs

T14. Every pair of driwrens rastumbs.

  (1) [D6] The iskkeld is defined by rastumbing with everything.
  (2) [D2] The claim is that x * y = y * x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T15. x * x = x for every driwren x.

  (1) [D1] Being opalfal is the condition x * x = x.
  (2) [D7] The claim is that the kami is the whole system.
  (3) Only the diagonal of the table is involved.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T2. The keldtu rastumbs with every driwren.

  (1) [D5] Let e be the keldtu and x any driwren.
  (2) [D5] Then e * x = x and x * e = x.
  (3) [D2] So e * x = x * e, which is what it means to rastumb.
  (4) [D6] Since x was arbitrary, e belongs to the iskkeld.

Checked over 6 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. If x and y both rastumb with every driwren, then so does x * y.

  (1) [D6] Let x and y lie in the iskkeld and let z be any driwren.
  (2) [A2] Then (x * y) * z = x * (y * z).
  (3) [D6] Move z past y, then past x, using that each rastumbs with everything.
  (4) [D3] So x * y rastumbs with z, and the iskkeld is reldshen.

Checked over 36 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

T9. If x and y are both opalfal then so is x * y.

  (1) [D7] Let x and y be opalfal.
  (2) [D1] The claim asks whether (x * y) * (x * y) returns x * y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 36 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

The results now available are T14, T15, T2, T3 and T9, each settled by exhaustive check
rather than by argument from analogy.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x031. This result is about the iskkeld. List every driwren in it.
  x034. This result is about the kami. List every driwren in it.

# Chapter 9. Collections that close on themselves

## Why this chapter

So far the driwrens have been objects to be pushed around. This chapter starts asking
what they are like. We take up the korrquil of a driwren, the ovimorn of a driwren is
reldshen and the ovimorn of a iskkeld driwren stays in the iskkeld.

Prerequisites are real here: chapters 5, 6, 7 and 8 supply the notions the statements
below are phrased in.

The standard of proof here is exhaustion. A universal claim about driwrens covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

## What is defined here

D11. The korrquil of a driwren. The korrquil of a driwren x is the number of driwrens in
its ovimorn [x].

Worked out for each driwren: nakquil to 1; soltarn to 1; muxsib to 1; braovi to 1;
yukzel to 1; thraisk to 1.

## The shape of it

Picture the ovimorn as what happens when you start with one driwren and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 6 driwrens, that stops. In this system the sizes it stops at are 1.

A useful mental split: some driwrens are inert under the operation and some are not.
nakquil, soltarn, muxsib, braovi, yukzel and thraisk come back unchanged when combined
with themselves, and nakquil, soltarn, muxsib, braovi, yukzel and thraisk commute with
everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 driwrens the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T4 rests on D8 (the ovimorn of a driwren) and D3 (reldshen collections). Remove any one
of them and the statement stops making sense, not merely stops being provable.

T8 rests on D8 (the ovimorn of a driwren), D6 (the iskkeld) and T3 (the iskkeld is
reldshen). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Here is (yukzel * soltarn) * thraisk, reduced without skipping anything.
    yukzel * soltarn = yukzel   (the table for *)
    yukzel * thraisk = thraisk   (the table for *)
The expression comes to thraisk.

Move the brackets and the work changes. Take soltarn * (thraisk * yukzel).
    thraisk * yukzel = thraisk   (the table for *)
    soltarn * thraisk = thraisk   (the table for *)
The value is thraisk. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
thraisk << braovi hold? Read off what thraisk stands over: nakquil, soltarn, muxsib,
braovi, yukzel and thraisk. braovi is among them, so it holds.

A second case, this time a ovimorn. Start from muxsib. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is muxsib, so the
korrquil of muxsib is 1.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of driwrens that come back
unchanged from themselves: nakquil, soltarn, muxsib, braovi, yukzel and thraisk.
Assuming more of them than that is the mistake to avoid.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of association of the first operation and
closure under the first operation. Those are properties of this system, not of systems
in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: D3 (reldshen collections), D6 (the iskkeld), D8
(the ovimorn of a driwren) and T3 (the iskkeld is reldshen).

These results are used again in D12 (the falpyr), T5 (the ovimorn is contained in every
reldshen collection), T6 (a driwren is opalfal exactly when its korrquil is one) and T7
(the korrquil divides the number of driwrens).

## Proofs

T4. For every driwren x, the collection [x] is reldshen.

  (1) [D8] [x] is built by taking x and closing under *.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 216 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

T8. If x lies in the iskkeld then every driwren of [x] lies in the iskkeld.

  (1) [T3] The iskkeld is reldshen.
  (2) [D8] [x] is the smallest reldshen collection containing x.
  (3) A smallest such collection sits inside any other, and the iskkeld is one.

Checked over 36 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the korrquil of a driwren. Each of these is used by
name later, so the names are worth learning rather than looking up.

Established here and safe to use: T4 and T8.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x023. What is the korrquil of soltarn?
  x024. What is the korrquil of muxsib?
  x025. What is the korrquil of braovi?
  x026. How many driwrens lie in [yukzel]?
  x027. How many driwrens lie in [thraisk]?
Level 4.
  x033. Name the driwrens that make up the iskkeld, which is what the result above is a claim about.
Level 5.
  x028. Let z be (yukzel * muxsib) * nakquil. What is the korrquil of z?
  x029. Let z be (yukzel * thraisk) * yukzel. What is the korrquil of z?

# Chapter 10. Collections that close on themselves (2)

## Why this chapter

The present chapter develops the falpyr, where some driwren reaches every other breaks
down and the ovimorn is contained in every reldshen collection.

Nothing here stands on its own. The arguments lean on chapters 4, 7 and 9, and a reader
who has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about driwrens covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D12. The falpyr. The falpyr of the system is the collection of driwrens whose korrquil
is largest.

In this system that picks out nakquil, soltarn, muxsib, braovi, yukzel and thraisk, that
is, all of them.

## The shape of it

Picture the ovimorn as what happens when you start with one driwren and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 6 driwrens, that stops. In this system the sizes it stops at are 1.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 driwrens the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R4 rests on D8 (the ovimorn of a driwren) and D11 (the korrquil of a driwren). The
dependence is on the content of those results, not only on their vocabulary.

T5 rests on D8 (the ovimorn of a driwren) and T4 (the ovimorn of a driwren is reldshen).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

T6 rests on D1 (opalfal driwrens), D11 (the korrquil of a driwren) and T4 (the ovimorn
of a driwren is reldshen). The dependence is on the content of those results, not only
on their vocabulary.

T7 rests on D11 (the korrquil of a driwren) and T4 (the ovimorn of a driwren is
reldshen). Remove any one of them and the statement stops making sense, not merely stops
being provable.

## A worked case

Evaluate (muxsib * thraisk) * (braovi * nakquil). Each line below is one lookup in a
table.
    muxsib * thraisk = thraisk   (the table for *)
    braovi * nakquil = braovi   (the table for *)
    thraisk * braovi = thraisk   (the table for *)
So (muxsib * thraisk) * (braovi * nakquil) is thraisk.

Bracketing is not cosmetic, so here is thraisk * (braovi * muxsib) for contrast.
    braovi * muxsib = thraisk   (the table for *)
    thraisk * thraisk = thraisk   (the table for *)
That gives thraisk, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test soltarn << thraisk. The zelfex of soltarn is nakquil and soltarn, and thraisk lies
outside it, so the relation fails.

## A case that breaks

R4. It is not the case that: There is a driwren whose ovimorn is the whole system. The
case that settles it: largest_span = 1, size = 6. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside D1 (opalfal driwrens), D11 (the korrquil of a driwren), D8 (the ovimorn
of a driwren) and T4 (the ovimorn of a driwren is reldshen).

## Proofs

R4. It is not the case that: There is a driwren whose ovimorn is the whole system.

  (1) [S2] Take the case largest_span = 1, size = 6, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T5. If S is reldshen and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 270 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T6. x * x = x holds if and only if [x] contains x alone.

  (1) [D1] If x * x = x then {x} is already closed under *.
  (2) [T4] So [x] = {x} and the korrquil is one.
  (3) [D11] Conversely a span of one object must contain x * x, which is then x.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T7. For every driwren x, the korrquil of x divides 6.

  (1) [T4] [x] is a reldshen collection.
  (2) [D11] Its size is the korrquil of x.
  (3) The claim is that this size always divides 6.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the falpyr. Later chapters state their results in these terms and do not
restate the definitions.

The results now available are T5, T6 and T7, each settled by exhaustive check rather
than by argument from analogy.

Do not carry forward R4. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x030. Write down the falpyr in full.
  x032. What is the largest korrquil any driwren has?
