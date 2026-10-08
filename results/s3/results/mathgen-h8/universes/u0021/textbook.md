# The Quilpon system

This book is about lumpons. A lumpon is not a number and not a set; it is one of exactly
6 objects, and everything said here is said about how those 6 objects combine.

The lumpons are written glimtez, glimkorr, nakkorr, duthwren, kaka and mornhob. The
first operation is written -. The relation is written >-; where it holds between two
lumpons we say the left one precedes the right one. Both operations associate to the
left when written without brackets, and brackets override that. Repeated combination is
abbreviated: x^3 means x - x - x. A trailing mark reverses: x' is the lumpon that
combines with x to give the neutral one.

Readers arriving from arithmetic should put it down at the door. The operations below
are defined by their tables and by nothing else. Several arithmetic habits survive the
crossing and several do not, and the text is careful to say which is which.

# Chapter 1. The objects and their notation

## Why this chapter

The present chapter develops the Quilpon signature, the Quilpon combination tables and
closure under the first operation.

One habit to adopt: when a statement below quantifies over lumpons, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## The tables in full

The table for -. Read the left argument down the side and the right argument across the top.

          |   glimtez  glimkorr   nakkorr  duthwren      kaka   mornhob
-----------------------------------------------------------------------
  glimtez |   glimtez  glimkorr   nakkorr  duthwren      kaka   mornhob
 glimkorr |  glimkorr   nakkorr  duthwren      kaka   mornhob   glimtez
  nakkorr |   nakkorr  duthwren      kaka   mornhob   glimtez  glimkorr
 duthwren |  duthwren      kaka   mornhob   glimtez  glimkorr   nakkorr
     kaka |      kaka   mornhob   glimtez  glimkorr   nakkorr  duthwren
  mornhob |   mornhob   glimtez  glimkorr   nakkorr  duthwren      kaka

Every pair standing in the >- relation, grouped by left argument.

  glimtez >- glimtez, glimkorr, nakkorr, duthwren, kaka and mornhob
  glimkorr >- glimkorr, nakkorr, duthwren, kaka and mornhob
  nakkorr >- nakkorr, duthwren, kaka and mornhob
  duthwren >- duthwren, kaka and mornhob
  kaka >- kaka and mornhob
  mornhob >- mornhob

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A1. Closure under the first operation. For all lumpons x and y, x - y is again a lumpon.

A2. Association of the first operation. For all lumpons x, y, z: (x - y) - z = x - (y -
z).

A3. Commutation of the first operation. For all lumpons x and y: x - y = y - x.

A6. Cancellation in the first operation. For all lumpons x, y, z: if x - y = x - z then
y = z.

## The shape of it

Two questions sort the lumpons quickly. Does combining a lumpon with itself change it?
For glimtez it does not. Does it matter which side it goes on? For glimtez, glimkorr,
nakkorr, duthwren, kaka and mornhob it does not.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R1 rests on S2 (the Quilpon combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Evaluate (glimkorr - nakkorr) - duthwren. Each line below is one lookup in a table.
    glimkorr - nakkorr = duthwren   (the table for -)
    duthwren - duthwren = glimtez   (the table for -)
That leaves glimtez, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is nakkorr - (duthwren - glimkorr) for contrast.
    duthwren - glimkorr = kaka   (the table for -)
    nakkorr - kaka = glimtez   (the table for -)
That gives glimtez, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test glimkorr >- nakkorr. The yukglim of glimkorr is glimkorr, nakkorr, duthwren, kaka
and mornhob, and nakkorr lies inside it, so the relation holds.

## A case that breaks

R1. It is not the case that: For every lumpon x: x - x = x. The case that settles it: x
= glimkorr, value = nakkorr. Anyone carrying this claim over from a more familiar system
will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

These results are used again in A4 (a neutral object for the first operation), A5
(reversal under the first operation), A7 (reflexivity of the relation) and A8
(antisymmetry of the relation).

## Proofs

R1. It is not the case that: For every lumpon x: x - x = x.

  (1) [S2] Take the case x = glimkorr, value = nakkorr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R1. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 1.
  x001. Evaluate glimkorr - kaka.
  x002. What lumpon does glimkorr - nakkorr name?
  x003. Reduce nakkorr - mornhob to a single lumpon.
  x004. Reduce kaka - glimkorr to a single lumpon.
  x005. Work out the value of kaka - kaka.
  x006. What lumpon does duthwren - nakkorr name?
Level 2.
  x007. What lumpon does (glimtez - duthwren) - kaka name?
  x008. What lumpon does (glimkorr - glimkorr) - glimtez name?
  x009. What lumpon does (glimkorr - duthwren) - glimtez name?
  x012. Evaluate mornhob^3.
  x013. What is kaka combined with itself 2 times under -?
  x014. Evaluate glimkorr - mornhob'.
  x015. Solve x - nakkorr = glimtez for x, naming every solution.
  x016. Which lumpons x satisfy x - nakkorr = glimkorr? List them all.
  x017. Solve x - nakkorr = mornhob for x, naming every solution.
  x018. Which lumpons x satisfy x - kaka = glimtez? List them all.
  x019. Which lumpons x satisfy x - duthwren = nakkorr? List them all.
Level 3.
  x010. Work out the value of (glimtez - kaka) - (glimtez - duthwren).
  x011. What lumpon does (duthwren - nakkorr) - (duthwren - mornhob) name?

# Chapter 2. Neutral objects and reversal

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is a neutral object
for the first operation, reversal under the first operation and the system does not have
an absorbing object for the first operation.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about lumpons covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A4. A neutral object for the first operation. There is a lumpon glimtez with glimtez - x
= x - glimtez = x for every x.

A5. Reversal under the first operation. For every lumpon x there is a lumpon y with x -
y = y - x = glimtez.

## The shape of it

Neutrality is a strong condition disguised as a weak one. It fixes a single lumpon and,
through that, constrains everything that can combine with it.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R2 rests on S2 (the Quilpon combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Evaluate (duthwren - mornhob) - (glimkorr - nakkorr). Each line below is one lookup in a
table.
    duthwren - mornhob = nakkorr   (the table for -)
    glimkorr - nakkorr = duthwren   (the table for -)
    nakkorr - duthwren = mornhob   (the table for -)
That leaves mornhob, and no other reading of the notation gives anything else.

A companion case, mornhob - (glimkorr - duthwren), to show what the brackets are doing.
    glimkorr - duthwren = kaka   (the table for -)
    mornhob - kaka = duthwren   (the table for -)
That gives duthwren, against mornhob above.

One decision about the relation, since deciding is as much a skill as computing. Does
glimtez >- glimtez hold? Read off what glimtez stands over: glimtez, glimkorr, nakkorr,
duthwren, kaka and mornhob. glimtez is among them, so it holds.

## A case that breaks

R2. There is no lumpon z with z - x = x - z = z for every lumpon x. It fails at reason =
no absorbing element. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: S2 (the Quilpon combination tables).

These results are used again in D5 (the tuka), D11 (the zamduth of a lumpon) and T1 (the
tuka is the only one of its kind).

## Proofs

R2. There is no lumpon z with z - x = x - z = z for every lumpon x.

  (1) [S2] Take the case reason = no absorbing element, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R2. These were tested and failed, and the failing cases are
recorded above.

## Exercises

This chapter carries no exercises. Nothing in it can be asked about in a way that could
not be answered without reading it, and an exercise like that is worse than none.

# Chapter 3. The relation and what it orders

## Why this chapter

What follows was pieced together backwards. The last item of it, comparability of every
pair, reflexivity of the relation and antisymmetry of the relation, was noticed before
anyone had a reason to expect it.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

The standard of proof here is exhaustion. A universal claim about lumpons covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A10. Comparability of every pair. For all lumpons x and y, at least one of x >- y and y
>- x holds.

A7. Reflexivity of the relation. For every lumpon x: x >- x.

A8. Antisymmetry of the relation. For all lumpons x and y: if x >- y and y >- x then x =
y.

A9. Transitivity of the relation. For all lumpons x, y, z: if x >- y and y >- z then x
>- z.

D4. The yukglim of a lumpon. The yukglim of a lumpon x is the collection of lumpons y
for which x >- y holds.

Worked out for each lumpon: glimtez to glimtez, glimkorr, nakkorr, duthwren, kaka and
mornhob; glimkorr to glimkorr, nakkorr, duthwren, kaka and mornhob; nakkorr to nakkorr,
duthwren, kaka and mornhob; duthwren to duthwren, kaka and mornhob; kaka to kaka and
mornhob; mornhob to mornhob.

## The shape of it

The relation is easiest to see as a height. Each lumpon casts a yukglim over what it
precedes, and the sizes of those shadows here are 1, 2, 3, 4, 5 and 6. No two are the
same size, so the objects line up in a single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 lumpons the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R3 rests on S2 (the Quilpon combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Evaluate (kaka - duthwren) - glimtez. Each line below is one lookup in a table.
    kaka - duthwren = glimkorr   (the table for -)
    glimkorr - glimtez = glimkorr   (the table for -)
The expression comes to glimkorr.

A companion case, duthwren - (glimtez - kaka), to show what the brackets are doing.
    glimtez - kaka = kaka   (the table for -)
    duthwren - kaka = glimkorr   (the table for -)
The value is glimkorr. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test glimkorr >- kaka. The yukglim of glimkorr is glimkorr, nakkorr, duthwren, kaka and
mornhob, and kaka lies inside it, so the relation holds.

## A case that breaks

R3. It is not the case that: For all lumpons x, y, z: if x >- y then (z - x) >- (z - y)
and (x - z) >- (y - z). It fails at x = glimtez, y = glimkorr, z = mornhob, side = left.
One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside S2 (the Quilpon combination tables).

These results are used again in D9 (a aztlum), D14 (cloka pairs), T13 (yukglims are
nested along the relation) and T14 (there is at most one aztlum).

## Proofs

R3. It is not the case that: For all lumpons x, y, z: if x >- y then (z - x) >- (z - y) and (x - z) >- (y - z).

  (1) [S2] Take the case x = glimtez, y = glimkorr, z = mornhob, side = left, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the yukglim of a lumpon. Later chapters state their results in these terms
and do not restate the definitions.

Do not carry forward R3. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 5.
  x020. The following fails in this system: For all lumpons x, y, z: if x >- y then (z - x) >- (z - y) and (x - z) >- (y - z). Name the earliest lumpon, in the order the lumpons were introduced, that witnesses the failure.

# Chapter 4. Combining objects

## Why this chapter

The practical content of this chapter is pontez lumpons, lumpons that vorhurn and the
tuka. It is the part that shows up in use.

Nothing here stands on its own. The arguments lean on chapters 1 and 2, and a reader who
has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over lumpons, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D1. Pontez lumpons. A lumpon x is called pontez when x - x = x.

In this system that picks out glimtez, which is 1 of the 6 lumpons.

D2. Lumpons that vorhurn. Two lumpons x and y are said to vorhurn when x - y = y - x.

D5. The tuka. The lumpon glimtez is called the tuka of the system. It is the unique
lumpon that leaves every lumpon unchanged under -.

Here that is glimtez.

## The shape of it

Two questions sort the lumpons quickly. Does combining a lumpon with itself change it?
For glimtez it does not. Does it matter which side it goes on? For glimtez, glimkorr,
nakkorr, duthwren, kaka and mornhob it does not.

The neutral lumpon glimtez is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

This chapter is groundwork. The derivations that use it start in the next one.

## A worked case

Evaluate (mornhob - nakkorr) - (glimtez - kaka). Each line below is one lookup in a
table.
    mornhob - nakkorr = glimkorr   (the table for -)
    glimtez - kaka = kaka   (the table for -)
    glimkorr - kaka = mornhob   (the table for -)
So (mornhob - nakkorr) - (glimtez - kaka) is mornhob.

Bracketing is not cosmetic, so here is nakkorr - (glimtez - mornhob) for contrast.
    glimtez - mornhob = mornhob   (the table for -)
    nakkorr - mornhob = glimkorr   (the table for -)
The value is glimkorr, not mornhob.

Test glimtez >- duthwren. The yukglim of glimtez is glimtez, glimkorr, nakkorr,
duthwren, kaka and mornhob, and duthwren lies inside it, so the relation holds.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of lumpons that come back
unchanged from themselves: glimtez. Assuming more of them than that is the mistake to
avoid.

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

What is built on it later: D6 (the glimfex), D7 (the opalkeld), D10 (iskjen lumpons) and
D11 (the zamduth of a lumpon).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

New vocabulary from this chapter: pontez lumpons, lumpons that vorhurn and the tuka.
Each of these is used by name later, so the names are worth learning rather than looking
up.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 2.
  x024. Which lumpon leaves every lumpon unchanged under -?
Level 3.
  x021. Write down the pontez in full.

# Chapter 5. The relation and what it orders (2)

## Why this chapter

So far the lumpons have been objects to be pushed around. This chapter starts asking
what they are like. We take up cloka pairs, lumvex collections and a aztlum.

Nothing here stands on its own. The arguments lean on chapters 1 and 3, and a reader who
has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over lumpons, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D14. Cloka pairs. Two distinct lumpons x and y form a cloka pair when x >- y and y >- x
both hold, that is, when each lies in the yukglim of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D3. Lumvex collections. A collection S of lumpons is lumvex when x - y belongs to S for
every pair x, y drawn from S.

D9. A aztlum. A lumpon f is a aztlum when f >- y holds for every lumpon y, that is, when
the yukglim of f is the whole system.

Running the definition over every lumpon leaves glimtez.

## The shape of it

Picture the umbquil as what happens when you start with one lumpon and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 6 lumpons, that stops. In this system the sizes it stops at are 1, 2, 3 and 6.

The relation is easiest to see as a height. Each lumpon casts a yukglim over what it
precedes, and the sizes of those shadows here are 1, 2, 3, 4, 5 and 6. No two are the
same size, so the objects line up in a single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 lumpons the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R5 rests on D4 (the yukglim of a lumpon). Remove any one of them and the statement stops
making sense, not merely stops being provable.

T13 rests on D4 (the yukglim of a lumpon) and A9 (transitivity of the relation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Here is (duthwren - glimtez) - nakkorr, reduced without skipping anything.
    duthwren - glimtez = duthwren   (the table for -)
    duthwren - nakkorr = mornhob   (the table for -)
That leaves mornhob, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is glimtez - (nakkorr - duthwren) for contrast.
    nakkorr - duthwren = mornhob   (the table for -)
    glimtez - mornhob = mornhob   (the table for -)
The value is mornhob. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test kaka >- kaka. The yukglim of kaka is kaka and mornhob, and kaka lies inside it, so
the relation holds.

## A case that breaks

R5. It is not the case that: If x >- y then y >- x. The case that settles it: x =
glimtez, y = glimkorr. Anyone carrying this claim over from a more familiar system will
be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation and
transitivity of the relation. Those are properties of this system, not of systems in
general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A1 (closure under the first operation), A9
(transitivity of the relation) and D4 (the yukglim of a lumpon).

What is built on it later: D8 (the umbquil of a lumpon), T5 (the glimfex is lumvex), T6
(the umbquil of a lumpon is lumvex) and T11 (the opalkeld is lumvex).

## Proofs

R5. It is not the case that: If x >- y then y >- x.

  (1) [S2] Take the case x = glimtez, y = glimkorr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T13. If y lies in the yukglim of x, then the yukglim of y is contained in the yukglim of x.

  (1) [D4] Let y satisfy x >- y and let z satisfy y >- z.
  (2) [A9] Transitivity gives x >- z.
  (3) [D4] So every member of the yukglim of y is a member of that of x.

Checked over 216 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward cloka pairs, lumvex collections and a aztlum. Later chapters state their
results in these terms and do not restate the definitions.

The results now available are T13, each settled by exhaustive check rather than by
argument from analogy.

Do not carry forward R5. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x022. How many lumpons lie in the smallest lumvex collection containing glimkorr?
  x023. How many lumpons lie in the smallest lumvex collection containing nakkorr?

# Chapter 6. Combining objects (2)

## Why this chapter

The present chapter develops the glimfex, the opalkeld and combining on the left never
merges two lumpons.

Nothing here stands on its own. The arguments lean on chapters 1 and 4, and a reader who
has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over lumpons, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D6. The glimfex. The glimfex of the system is the collection of lumpons that vorhurn
with every lumpon.

Running the definition over every lumpon leaves glimtez, glimkorr, nakkorr, duthwren,
kaka and mornhob.

D7. The opalkeld. The opalkeld is the collection of all pontez lumpons.

Running the definition over every lumpon leaves glimtez.

## The shape of it

A useful mental split: some lumpons are inert under the operation and some are not.
glimtez come back unchanged when combined with themselves, and glimtez, glimkorr,
nakkorr, duthwren, kaka and mornhob commute with everything.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T12 rests on A6 (cancellation in the first operation) and D2 (lumpons that vorhurn). The
dependence is on the content of those results, not only on their vocabulary.

## A worked case

Evaluate (glimtez - mornhob) - (kaka - glimkorr). Each line below is one lookup in a
table.
    glimtez - mornhob = mornhob   (the table for -)
    kaka - glimkorr = mornhob   (the table for -)
    mornhob - mornhob = kaka   (the table for -)
That leaves kaka, and no other reading of the notation gives anything else.

A companion case, mornhob - (kaka - glimtez), to show what the brackets are doing.
    kaka - glimtez = kaka   (the table for -)
    mornhob - kaka = duthwren   (the table for -)
The value is duthwren, not kaka.

Test glimkorr >- glimkorr. The yukglim of glimkorr is glimkorr, nakkorr, duthwren, kaka
and mornhob, and glimkorr lies inside it, so the relation holds.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of lumpons that come back
unchanged from themselves: glimtez. Assuming more of them than that is the mistake to
avoid.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of cancellation in the first operation and
closure under the first operation. Those are properties of this system, not of systems
in general.

To see how little the notation guarantees: rebuild the system with the same names over
different tables and T12 fail outright.

## Neighbouring results

Read alongside A6 (cancellation in the first operation), D1 (pontez lumpons) and D2
(lumpons that vorhurn).

What is built on it later: T2 (the tuka lies in the glimfex), T5 (the glimfex is
lumvex), T10 (the umbquil of a glimfex lumpon stays in the glimfex) and T11 (the
opalkeld is lumvex).

## Proofs

T12. For every lumpon a, the assignment x to a - x sends distinct lumpons to distinct lumpons.

  (1) [A6] Suppose a - x = a - y.
  (2) [A6] Cancellation on the left gives x = y.
  (3) So the assignment is injective, and being injective on a finite carrier it is onto.

Checked over 36 cases: every object translated by every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the glimfex and the opalkeld. Later chapters state their results in these
terms and do not restate the definitions.

Established here and safe to use: T12.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x025. List every lumpon in the glimfex.
  x026. List every lumpon in the opalkeld.

# Chapter 7. Neutral objects and reversal (2)

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is iskjen lumpons,
the zamduth of a lumpon and where the tuka swallows everything breaks down.

Nothing here stands on its own. The arguments lean on chapters 2 and 4, and a reader who
has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about lumpons covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D10. Iskjen lumpons. A lumpon x is iskjen when x - x equals the tuka.

Running the definition over every lumpon leaves glimtez and duthwren.

D11. The zamduth of a lumpon. A zamduth of a lumpon x is a lumpon y with x - y = y - x =
glimtez.

Worked out for each lumpon: glimtez to glimtez; glimkorr to mornhob; nakkorr to kaka;
duthwren to duthwren; kaka to nakkorr; mornhob to glimkorr.

## The shape of it

The neutral lumpon glimtez is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R6 rests on D5 (the tuka). Remove any one of them and the statement stops making sense,
not merely stops being provable.

T1 rests on D5 (the tuka) and A4 (a neutral object for the first operation). The
dependence is on the content of those results, not only on their vocabulary.

## A worked case

Take (duthwren - glimtez) - mornhob and work it out one step at a time.
    duthwren - glimtez = duthwren   (the table for -)
    duthwren - mornhob = nakkorr   (the table for -)
That leaves nakkorr, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is glimtez - (mornhob - duthwren) for contrast.
    mornhob - duthwren = nakkorr   (the table for -)
    glimtez - nakkorr = nakkorr   (the table for -)
The value is nakkorr. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
glimtez >- mornhob hold? Read off what glimtez stands over: glimtez, glimkorr, nakkorr,
duthwren, kaka and mornhob. mornhob is among them, so it holds.

## A case that breaks

R6. It is not the case that: e - x equals the tuka for every lumpon x. The case that
settles it: anchor = glimtez, x = glimkorr, value = glimkorr. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation,
closure under the first operation and reversal under the first operation. Those are
properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A4 (a neutral object for the first operation), A5 (reversal under the
first operation), D1 (pontez lumpons) and D5 (the tuka).

What is built on it later: T3 (a lumpon has only one zamduth) and T4 (a iskjen lumpon is
its own zamduth).

## Proofs

R6. It is not the case that: e - x equals the tuka for every lumpon x.

  (1) [S2] Take the case anchor = glimtez, x = glimkorr, value = glimkorr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T1. There is exactly one lumpon e with e - x = x - e = x for every lumpon x.

  (1) [D5] Suppose e and f both leave every lumpon unchanged.
  (2) [A4] Then e - f = f, reading e as neutral on the left.
  (3) [A4] And e - f = e, reading f as neutral on the right.
  (4) So e = f, and the two suppositions describe the same object.

Checked over 36 cases: every object paired with every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: iskjen lumpons and the zamduth of a lumpon. Each of
these is used by name later, so the names are worth learning rather than looking up.

Established here and safe to use: T1.

Do not carry forward R6. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x034. List every lumpon in the iskjen.
  x035. Which lumpon reverses glimkorr under -?
  x036. Name the zamduth of nakkorr.
  x037. Which lumpon reverses kaka under -?
  x038. Name the zamduth of mornhob.
Level 5.
  x039. Let z be glimkorr - duthwren. Name the zamduth of z.
  x040. Let z be mornhob - duthwren. Name the zamduth of z.
  x041. Let z be duthwren - mornhob. Name the zamduth of z.
  x059. The following fails in this system: e - x equals the tuka for every lumpon x. Name the earliest lumpon, in the order the lumpons were introduced, that witnesses the failure.

# Chapter 8. The relation and what it orders (3)

## Why this chapter

The results collected here were not found in this order. The umbquil of a lumpon, there
is at most one aztlum and the system has a aztlum came first, and the rest was assembled
around that once the pattern was visible.

Prerequisites are real here: chapters 3 and 5 supply the notions the statements below
are phrased in.

The standard of proof here is exhaustion. A universal claim about lumpons covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

## What is defined here

D8. The umbquil of a lumpon. The umbquil of a lumpon x, written [x], is the smallest
lumvex collection that contains x.

Worked out for each lumpon: glimtez to glimtez; glimkorr to glimtez, glimkorr, nakkorr,
duthwren, kaka and mornhob; nakkorr to glimtez, nakkorr and kaka; duthwren to glimtez
and duthwren; kaka to glimtez, nakkorr and kaka; mornhob to glimtez, glimkorr, nakkorr,
duthwren, kaka and mornhob.

## The shape of it

Picture the umbquil as what happens when you start with one lumpon and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 6 lumpons, that stops. In this system the sizes it stops at are 1, 2, 3 and 6.

Think of >- as pointing downhill. The yukglim of a lumpon is everything downhill of it,
and those shadows here have sizes 1, 2, 3, 4, 5 and 6.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T14 rests on D9 (a aztlum) and A8 (antisymmetry of the relation). The dependence is on
the content of those results, not only on their vocabulary.

T15 rests on D9 (a aztlum) and A10 (comparability of every pair). Remove any one of them
and the statement stops making sense, not merely stops being provable.

T16 rests on D14 (cloka pairs) and A8 (antisymmetry of the relation). Remove any one of
them and the statement stops making sense, not merely stops being provable.

## A worked case

Evaluate (mornhob - kaka) - (nakkorr - glimtez). Each line below is one lookup in a
table.
    mornhob - kaka = duthwren   (the table for -)
    nakkorr - glimtez = nakkorr   (the table for -)
    duthwren - nakkorr = mornhob   (the table for -)
The expression comes to mornhob.

A companion case, kaka - (nakkorr - mornhob), to show what the brackets are doing.
    nakkorr - mornhob = glimkorr   (the table for -)
    kaka - glimkorr = mornhob   (the table for -)
The value is mornhob. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test duthwren >- glimtez. The yukglim of duthwren is duthwren, kaka and mornhob, and
glimtez lies outside it, so the relation fails.

Now compute [glimkorr]. Fold glimkorr against itself, then fold whatever appeared
against everything present, and stop when a round adds nothing. The result is glimtez,
glimkorr, nakkorr, duthwren, kaka and mornhob, of size 6.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by antisymmetry of the relation, closure under the first operation
and comparability of every pair. A system without them is not a system where these
results are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A10 (comparability of every pair), A8 (antisymmetry of the relation), D14
(cloka pairs) and D3 (lumvex collections).

These results are used again in D12 (the duthovi of a lumpon), T6 (the umbquil of a
lumpon is lumvex), T7 (the umbquil is contained in every lumvex collection) and T10 (the
umbquil of a glimfex lumpon stays in the glimfex).

## Proofs

T14. No two distinct lumpons can both be aztlums.

  (1) [D9] Let f and h both be floors.
  (2) [D9] Then f >- h, since h is any object, and h >- f likewise.
  (3) [A8] Antisymmetry forces f = h.

Checked over 36 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T15. Some lumpon aztlums the whole system.

  (1) [A10] Every pair is comparable, so the relation orders the objects into a line.
  (2) [D9] The claim is that the line has a bottom.
  (3) The carrier is finite, so the search over candidates terminates.

Checked over 36 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T16. No two distinct lumpons lie in each other's yukglim.

  (1) [D14] Suppose x and y form a tight pair.
  (2) [A8] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the umbquil of a lumpon. Each of these is used by name
later, so the names are worth learning rather than looking up.

Established here and safe to use: T14, T15 and T16.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x027. List the umbquil of glimkorr.
  x028. List the umbquil of nakkorr.
  x029. List the umbquil of duthwren.
  x030. List the umbquil of kaka.
  x031. List the umbquil of mornhob.
Level 4.
  x032. Let z be duthwren - kaka. List the umbquil of z.
  x033. Let z be nakkorr - glimkorr. List the umbquil of z.

# Chapter 9. Combining objects (3)

## Why this chapter

The practical content of this chapter is where every lumpon is pontez breaks down, the
opalkeld is lumvex and every lumpon lies in the glimfex. It is the part that shows up in
use.

Nothing here stands on its own. The arguments lean on chapters 1, 4, 5 and 6, and a
reader who has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over lumpons, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

Two questions sort the lumpons quickly. Does combining a lumpon with itself change it?
For glimtez it does not. Does it matter which side it goes on? For glimtez, glimkorr,
nakkorr, duthwren, kaka and mornhob it does not.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R4 rests on D7 (the opalkeld). The dependence is on the content of those results, not
only on their vocabulary.

T11 rests on D7 (the opalkeld) and D3 (lumvex collections). The dependence is on the
content of those results, not only on their vocabulary.

T17 rests on D6 (the glimfex). The dependence is on the content of those results, not
only on their vocabulary.

T2 rests on D5 (the tuka) and D6 (the glimfex). The dependence is on the content of
those results, not only on their vocabulary.

T5 rests on D6 (the glimfex), D3 (lumvex collections) and A2 (association of the first
operation). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Take (duthwren - mornhob) - glimtez and work it out one step at a time.
    duthwren - mornhob = nakkorr   (the table for -)
    nakkorr - glimtez = nakkorr   (the table for -)
The expression comes to nakkorr.

A companion case, mornhob - (glimtez - duthwren), to show what the brackets are doing.
    glimtez - duthwren = duthwren   (the table for -)
    mornhob - duthwren = nakkorr   (the table for -)
The value is nakkorr. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test mornhob >- duthwren. The yukglim of mornhob is mornhob, and duthwren lies outside
it, so the relation fails.

## A case that breaks

R4. It is not the case that: x - x = x for every lumpon x. The case that settles it: x =
glimkorr, value = nakkorr. Anyone carrying this claim over from a more familiar system
will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation and closure under the first operation. Those are
properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A2 (association of the first operation), D3 (lumvex collections), D5 (the
tuka) and D6 (the glimfex).

These results are used again in T10 (the umbquil of a glimfex lumpon stays in the
glimfex).

## Proofs

R4. It is not the case that: x - x = x for every lumpon x.

  (1) [S2] Take the case x = glimkorr, value = nakkorr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T11. If x and y are both pontez then so is x - y.

  (1) [D7] Let x and y be pontez.
  (2) [D1] The claim asks whether (x - y) - (x - y) returns x - y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 36 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

T17. Every pair of lumpons vorhurns.

  (1) [D6] The glimfex is defined by vorhurning with everything.
  (2) [D2] The claim is that x - y = y - x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T2. The tuka vorhurns with every lumpon.

  (1) [D5] Let e be the tuka and x any lumpon.
  (2) [D5] Then e - x = x and x - e = x.
  (3) [D2] So e - x = x - e, which is what it means to vorhurn.
  (4) [D6] Since x was arbitrary, e belongs to the glimfex.

Checked over 6 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T5. If x and y both vorhurn with every lumpon, then so does x - y.

  (1) [D6] Let x and y lie in the glimfex and let z be any lumpon.
  (2) [A2] Then (x - y) - z = x - (y - z).
  (3) [D6] Move z past y, then past x, using that each vorhurns with everything.
  (4) [D3] So x - y vorhurns with z, and the glimfex is lumvex.

Checked over 36 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

The results now available are T11, T17, T2 and T5, each settled by exhaustive check
rather than by argument from analogy.

Explicitly not available: R4. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x054. This result is about the glimfex. List every lumpon in it.
  x057. Name the lumpons that make up the opalkeld, which is what the result above is a claim about.

# Chapter 10. Collections that close on themselves

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through the duthovi of a lumpon, a
lumpon has only one zamduth and the umbquil of a lumpon is lumvex.

Nothing here stands on its own. The arguments lean on chapters 1, 5, 7 and 8, and a
reader who has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
lumpons that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D12. The duthovi of a lumpon. The duthovi of a lumpon x is the number of lumpons in its
umbquil [x].

Worked out for each lumpon: glimtez to 1; glimkorr to 6; nakkorr to 3; duthwren to 2;
kaka to 3; mornhob to 6.

## The shape of it

Picture the umbquil as what happens when you start with one lumpon and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 6 lumpons, that stops. In this system the sizes it stops at are 1, 2, 3 and 6.

The neutral lumpon glimtez is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T3 rests on D11 (the zamduth of a lumpon), A2 (association of the first operation) and
T1 (the tuka is the only one of its kind). Remove any one of them and the statement
stops making sense, not merely stops being provable.

T6 rests on D8 (the umbquil of a lumpon) and D3 (lumvex collections). The dependence is
on the content of those results, not only on their vocabulary.

## A worked case

Take (glimkorr - duthwren) - (kaka - nakkorr) and work it out one step at a time.
    glimkorr - duthwren = kaka   (the table for -)
    kaka - nakkorr = glimtez   (the table for -)
    kaka - glimtez = kaka   (the table for -)
That leaves kaka, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take duthwren - (kaka - glimkorr).
    kaka - glimkorr = mornhob   (the table for -)
    duthwren - mornhob = nakkorr   (the table for -)
That gives nakkorr, against kaka above.

Test kaka >- duthwren. The yukglim of kaka is kaka and mornhob, and duthwren lies
outside it, so the relation fails.

A second case, this time a umbquil. Start from duthwren. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is glimtez and
duthwren, so the duthovi of duthwren is 2.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of lumpons that come back
unchanged from themselves: glimtez. Assuming more of them than that is the mistake to
avoid.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation, closure under the first operation and reversal under
the first operation. Those are properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A2 (association of the first operation), D11 (the zamduth of a lumpon),
D3 (lumvex collections) and D8 (the umbquil of a lumpon).

These results are used again in D13 (the vashopal), T4 (a iskjen lumpon is its own
zamduth), T7 (the umbquil is contained in every lumvex collection) and T8 (a lumpon is
pontez exactly when its duthovi is one).

## Proofs

T3. For every lumpon x there is exactly one zamduth of x.

  (1) [D11] Let y and z both be partners of x.
  (2) [A2] Then y = y - (x - z) = (y - x) - z.
  (3) [D11] Both bracketed products collapse to the neutral object.
  (4) So y = z.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T6. For every lumpon x, the collection [x] is lumvex.

  (1) [D8] [x] is built by taking x and closing under -.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 216 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the duthovi of a lumpon. Later chapters state their results in these terms
and do not restate the definitions.

Established here and safe to use: T3 and T6.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x042. How many lumpons lie in [glimkorr]?
  x043. How many lumpons lie in [nakkorr]?
  x044. What is the duthovi of duthwren?
  x045. What is the duthovi of kaka?
  x046. What is the duthovi of mornhob?
Level 5.
  x047. Let z be (mornhob - kaka) - mornhob. What is the duthovi of z?
  x048. Let z be (duthwren - duthwren) - duthwren. What is the duthovi of z?
  x049. Let z be (glimkorr - glimkorr) - duthwren. What is the duthovi of z?
  x050. Let z be (mornhob - glimtez) - kaka. What is the duthovi of z?
  x051. Let z be (glimkorr - duthwren) - glimtez. What is the duthovi of z?
  x052. Let z be (nakkorr - kaka) - nakkorr. What is the duthovi of z?

# Chapter 11. Collections that close on themselves (2)

## Why this chapter

We turn to the vashopal, the umbquil of a glimfex lumpon stays in the glimfex and some
lumpon reaches every other. The treatment is self contained given the material already
established.

Nothing here stands on its own. The arguments lean on chapters 4, 6, 7, 8, 9 and 10, and
a reader who has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about lumpons covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

## What is defined here

D13. The vashopal. The vashopal of the system is the collection of lumpons whose duthovi
is largest.

In this system that picks out glimkorr and mornhob, which is 2 of the 6 lumpons.

## The shape of it

The right picture for umbquil is a spreading stain rather than a list. Drop one lumpon
in, apply the operation to whatever is wet, repeat. The stain here reaches 1, 2, 3 and 6
lumpons depending on where it started.

Two questions sort the lumpons quickly. Does combining a lumpon with itself change it?
For glimtez it does not. Does it matter which side it goes on? For glimtez, glimkorr,
nakkorr, duthwren, kaka and mornhob it does not.

Neutrality is a strong condition disguised as a weak one. It fixes a single lumpon and,
through that, constrains everything that can combine with it.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T10 rests on D8 (the umbquil of a lumpon), D6 (the glimfex) and T5 (the glimfex is
lumvex). The dependence is on the content of those results, not only on their
vocabulary.

T18 rests on D8 (the umbquil of a lumpon) and D12 (the duthovi of a lumpon). Remove any
one of them and the statement stops making sense, not merely stops being provable.

T4 rests on D10 (iskjen lumpons), D11 (the zamduth of a lumpon) and T3 (a lumpon has
only one zamduth). Remove any one of them and the statement stops making sense, not
merely stops being provable.

T7 rests on D8 (the umbquil of a lumpon) and T6 (the umbquil of a lumpon is lumvex).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

T8 rests on D1 (pontez lumpons), D12 (the duthovi of a lumpon) and T6 (the umbquil of a
lumpon is lumvex). The dependence is on the content of those results, not only on their
vocabulary.

T9 rests on D12 (the duthovi of a lumpon) and T6 (the umbquil of a lumpon is lumvex).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

## A worked case

Take (duthwren - glimtez) - kaka and work it out one step at a time.
    duthwren - glimtez = duthwren   (the table for -)
    duthwren - kaka = glimkorr   (the table for -)
That leaves glimkorr, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take glimtez - (kaka - duthwren).
    kaka - duthwren = glimkorr   (the table for -)
    glimtez - glimkorr = glimkorr   (the table for -)
The value is glimkorr. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
kaka >- mornhob hold? Read off what kaka stands over: kaka and mornhob. mornhob is among
them, so it holds.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation, closure under the first operation and reversal under
the first operation. Those are properties of this system, not of systems in general.

That is not a rhetorical caution. Take the same 6 objects, the same symbols, and a
different table, and T18 and T9 stop holding. The notation survives the substitution and
the mathematics does not.

## Neighbouring results

Read alongside D1 (pontez lumpons), D10 (iskjen lumpons), D11 (the zamduth of a lumpon)
and D12 (the duthovi of a lumpon).

## Proofs

T10. If x lies in the glimfex then every lumpon of [x] lies in the glimfex.

  (1) [T5] The glimfex is lumvex.
  (2) [D8] [x] is the smallest lumvex collection containing x.
  (3) A smallest such collection sits inside any other, and the glimfex is one.

Checked over 36 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

T18. There is a lumpon whose umbquil is the whole system.

  (1) [D8] Compute [x] for each lumpon in turn.
  (2) [D12] The claim is that some duthovi equals 6.
  (3) The search runs over finitely many objects, so it settles.

Checked over 6 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T4. If x - x is the tuka then the zamduth of x is x itself.

  (1) [D10] Let x be iskjen, so x - x is the tuka.
  (2) [D11] That is exactly the condition for x to be a partner of x.
  (3) [T3] Partners are unique, so no other object can be one.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T7. If S is lumvex and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 24 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T8. x - x = x holds if and only if [x] contains x alone.

  (1) [D1] If x - x = x then {x} is already closed under -.
  (2) [T6] So [x] = {x} and the duthovi is one.
  (3) [D12] Conversely a span of one object must contain x - x, which is then x.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T9. For every lumpon x, the duthovi of x divides 6.

  (1) [T6] [x] is a lumvex collection.
  (2) [D12] Its size is the duthovi of x.
  (3) The claim is that this size always divides 6.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the vashopal. Each of these is used by name later, so
the names are worth learning rather than looking up.

Established here and safe to use: T10, T18, T4, T7, T8 and T9.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x053. Write down the vashopal in full.
  x055. What is the largest duthovi any lumpon has?
  x056. This result is about the glimfex. List every lumpon in it.
  x058. Which lumpon, taken earliest in the listed order, has duthovi equal to 6?
