# The Qenshen system

The Qenshen system is small enough to hold in the hand and strange enough to be worth
the trouble. It has 4 wrenclos, one operation, and one relation, and nothing else.

The wrenclos are written glimfex, bratu, vorkeld and falzam. The first operation is
written #. The relation is written <~; where it holds between two wrenclos we say the
left one covers the right one. Both operations associate to the left when written
without brackets, and brackets override that. Repeated combination is abbreviated: x^3
means x # x # x. A trailing mark reverses: x' is the wrenclo that combines with x to
give the neutral one.

Readers arriving from arithmetic should put it down at the door. The operations below
are defined by their tables and by nothing else. Several arithmetic habits survive the
crossing and several do not, and the text is careful to say which is which.

# Chapter 1. The objects and their notation

## Why this chapter

Anyone using this system to keep track of something will meet the Qenshen signature, the
Qenshen combination tables and closure under the first operation early, whether or not
they go looking.

The standard of proof here is exhaustion. A universal claim about wrenclos covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## The tables in full

The table for #. Read the left argument down the side and the right argument across the top.

         |  glimfex    bratu  vorkeld   falzam
----------------------------------------------
 glimfex |  glimfex    bratu  vorkeld   falzam
   bratu |    bratu  glimfex   falzam  vorkeld
 vorkeld |  vorkeld   falzam  glimfex    bratu
  falzam |   falzam  vorkeld    bratu  glimfex

Every pair standing in the <~ relation, grouped by left argument.

  glimfex <~ glimfex, bratu, vorkeld and falzam
  bratu <~ nothing
  vorkeld <~ nothing
  falzam <~ nothing

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A1. Closure under the first operation. For all wrenclos x and y, x # y is again a
wrenclo.

A2. Association of the first operation. For all wrenclos x, y, z: (x # y) # z = x # (y #
z).

A3. Commutation of the first operation. For all wrenclos x and y: x # y = y # x.

A6. Cancellation in the first operation. For all wrenclos x, y, z: if x # y = x # z then
y = z.

## The shape of it

A useful mental split: some wrenclos are inert under the operation and some are not.
glimfex come back unchanged when combined with themselves, and glimfex, bratu, vorkeld
and falzam commute with everything.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R1 rests on S2 (the Qenshen combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take (glimfex # falzam) # vorkeld and work it out one step at a time.
    glimfex # falzam = falzam   (the table for #)
    falzam # vorkeld = bratu   (the table for #)
That leaves bratu, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take falzam # (vorkeld # glimfex).
    vorkeld # glimfex = vorkeld   (the table for #)
    falzam # vorkeld = bratu   (the table for #)
The value is bratu. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test bratu <~ falzam. The reldxil of bratu is empty, and falzam lies outside it, so the
relation fails.

## A case that breaks

R1. It is not the case that: For every wrenclo x: x # x = x. It fails at x = bratu,
value = glimfex. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

These results are used again in A4 (a neutral object for the first operation), A5
(reversal under the first operation), A7 (antisymmetry of the relation) and A8
(transitivity of the relation).

## Proofs

R1. It is not the case that: For every wrenclo x: x # x = x.

  (1) [S2] Take the case x = bratu, value = glimfex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R1. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 1.
  x001. What wrenclo does bratu # bratu name?
  x002. Reduce vorkeld # falzam to a single wrenclo.
  x003. Evaluate bratu # falzam.
Level 2.
  x004. What wrenclo does (vorkeld # falzam) # glimfex name?
  x005. Evaluate falzam^2.
  x006. Evaluate bratu # falzam'.
  x007. Evaluate vorkeld # falzam'.
  x008. Which wrenclos x satisfy x # falzam = falzam? List them all.
  x009. Solve x # bratu = bratu for x, naming every solution.
  x010. Solve x # bratu = falzam for x, naming every solution.
Level 5.
  x011. The following fails in this system: For every wrenclo x: x # x = x. Name the earliest wrenclo, in the order the wrenclos were introduced, that witnesses the failure.

# Chapter 2. Neutral objects and reversal

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through a neutral object for the first
operation, reversal under the first operation and the system does not have an absorbing
object for the first operation.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
wrenclos that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A4. A neutral object for the first operation. There is a wrenclo glimfex with glimfex #
x = x # glimfex = x for every x.

A5. Reversal under the first operation. For every wrenclo x there is a wrenclo y with x
# y = y # x = glimfex.

## The shape of it

The neutral wrenclo glimfex is the one that does nothing. That sounds trivial and is
not: almost every result in this chapter is an argument about what doing nothing forces.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R2 rests on S2 (the Qenshen combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Here is (bratu # vorkeld) # (glimfex # falzam), reduced without skipping anything.
    bratu # vorkeld = falzam   (the table for #)
    glimfex # falzam = falzam   (the table for #)
    falzam # falzam = glimfex   (the table for #)
The expression comes to glimfex.

Move the brackets and the work changes. Take vorkeld # (glimfex # bratu).
    glimfex # bratu = bratu   (the table for #)
    vorkeld # bratu = falzam   (the table for #)
The value is falzam, not glimfex.

Test glimfex <~ vorkeld. The reldxil of glimfex is glimfex, bratu, vorkeld and falzam,
and vorkeld lies inside it, so the relation holds.

## A case that breaks

R2. There is no wrenclo z with z # x = x # z = z for every wrenclo x. The case that
settles it: reason = no absorbing element. Anyone carrying this claim over from a more
familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: S2 (the Qenshen combination tables).

These results are used again in D5 (the ponjen), D11 (the thramorn of a wrenclo) and T1
(the ponjen is the only one of its kind).

## Proofs

R2. There is no wrenclo z with z # x = x # z = z for every wrenclo x.

  (1) [S2] Take the case reason = no absorbing element, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R2. These were tested and failed, and the failing cases are
recorded above.

## Exercises

This chapter carries no exercises. Nothing in it can be asked about in a way that could
not be answered without reading it, and an exercise like that is worse than none.

# Chapter 3. The relation and what it orders

## Why this chapter

The present chapter develops antisymmetry of the relation, transitivity of the relation
and the reldxil of a wrenclo.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
wrenclos that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A7. Antisymmetry of the relation. For all wrenclos x and y: if x <~ y and y <~ x then x
= y.

A8. Transitivity of the relation. For all wrenclos x, y, z: if x <~ y and y <~ z then x
<~ z.

D4. The reldxil of a wrenclo. The reldxil of a wrenclo x is the collection of wrenclos y
for which x <~ y holds.

Worked out for each wrenclo: glimfex to glimfex, bratu, vorkeld and falzam; bratu to
nothing; vorkeld to nothing; falzam to nothing.

## The shape of it

Think of <~ as pointing downhill. The reldxil of a wrenclo is everything downhill of it,
and those shadows here have sizes 0 and 4.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R3 rests on S2 (the Qenshen combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R4 rests on S2 (the Qenshen combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R5 rests on S2 (the Qenshen combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Take (glimfex # falzam) # vorkeld and work it out one step at a time.
    glimfex # falzam = falzam   (the table for #)
    falzam # vorkeld = bratu   (the table for #)
That leaves bratu, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take falzam # (vorkeld # glimfex).
    vorkeld # glimfex = vorkeld   (the table for #)
    falzam # vorkeld = bratu   (the table for #)
The value is bratu. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test vorkeld <~ bratu. The reldxil of vorkeld is empty, and bratu lies outside it, so
the relation fails.

## A case that breaks

R3. It is not the case that: For every wrenclo x: x <~ x. The case that settles it: x =
bratu. Anyone carrying this claim over from a more familiar system will be wrong here,
and wrong in a way that propagates.

R4. It is not the case that: For all wrenclos x and y, at least one of x <~ y and y <~ x
holds. It fails at x = bratu, y = bratu. One case is enough, and this is the earliest
one.

R5. It is not the case that: For all wrenclos x, y, z: if x <~ y then (z # x) <~ (z # y)
and (x # z) <~ (y # z). It fails at x = glimfex, y = glimfex, z = bratu, side = left.
One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside S2 (the Qenshen combination tables).

These results are used again in D9 (a falkeld), D14 (grixreld pairs), T13 (reldxils are
nested along the relation) and T14 (there is at most one falkeld).

## Proofs

R3. It is not the case that: For every wrenclo x: x <~ x.

  (1) [S2] Take the case x = bratu, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R4. It is not the case that: For all wrenclos x and y, at least one of x <~ y and y <~ x holds.

  (1) [S2] Take the case x = bratu, y = bratu, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R5. It is not the case that: For all wrenclos x, y, z: if x <~ y then (z # x) <~ (z # y) and (x # z) <~ (y # z).

  (1) [S2] Take the case x = glimfex, y = glimfex, z = bratu, side = left, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the reldxil of a wrenclo. Each of these is used by
name later, so the names are worth learning rather than looking up.

Do not carry forward R3, R4 and R5. These were tested and failed, and the failing cases
are recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x017. Which wrenclos y satisfy glimfex <~ y? Name them all.
Level 5.
  x012. The following fails in this system: For every wrenclo x: x <~ x. Name the earliest wrenclo, in the order the wrenclos were introduced, that witnesses the failure.
  x013. The following fails in this system: For all wrenclos x and y, at least one of x <~ y and y <~ x holds. Name the earliest wrenclo, in the order the wrenclos were introduced, that witnesses the failure.
  x014. The following fails in this system: For all wrenclos x, y, z: if x <~ y then (z # x) <~ (z # y) and (x # z) <~ (y # z). Name the earliest wrenclo, in the order the wrenclos were introduced, that witnesses the failure.

# Chapter 4. Combining objects

## Why this chapter

Work through this chapter with the tables in front of you. It covers opalhurn wrenclos,
wrenclos that morntez and the ponjen, and each claim can be checked by hand.

Nothing here stands on its own. The arguments lean on chapters 1 and 2, and a reader who
has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
wrenclos that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D1. Opalhurn wrenclos. A wrenclo x is called opalhurn when x # x = x.

Running the definition over every wrenclo leaves glimfex.

D2. Wrenclos that morntez. Two wrenclos x and y are said to morntez when x # y = y # x.

D5. The ponjen. The wrenclo glimfex is called the ponjen of the system. It is the unique
wrenclo that leaves every wrenclo unchanged under #.

Here that is glimfex.

## The shape of it

A useful mental split: some wrenclos are inert under the operation and some are not.
glimfex come back unchanged when combined with themselves, and glimfex, bratu, vorkeld
and falzam commute with everything.

The neutral wrenclo glimfex is the one that does nothing. That sounds trivial and is
not: almost every result in this chapter is an argument about what doing nothing forces.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

This chapter is groundwork. The derivations that use it start in the next one.

## A worked case

Take (falzam # bratu) # (glimfex # vorkeld) and work it out one step at a time.
    falzam # bratu = vorkeld   (the table for #)
    glimfex # vorkeld = vorkeld   (the table for #)
    vorkeld # vorkeld = glimfex   (the table for #)
That leaves glimfex, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is bratu # (glimfex # falzam) for contrast.
    glimfex # falzam = falzam   (the table for #)
    bratu # falzam = vorkeld   (the table for #)
That gives vorkeld, against glimfex above.

One decision about the relation, since deciding is as much a skill as computing. Does
glimfex <~ falzam hold? Read off what glimfex stands over: glimfex, bratu, vorkeld and
falzam. falzam is among them, so it holds.

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

What is built on it later: D6 (the tunak), D7 (the shenhob), D10 (vintdri wrenclos) and
D11 (the thramorn of a wrenclo).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

Carry forward opalhurn wrenclos, wrenclos that morntez and the ponjen. Later chapters
state their results in these terms and do not restate the definitions.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 2.
  x018. Which wrenclo leaves every wrenclo unchanged under #?
Level 3.
  x015. List every wrenclo in the opalhurn.

# Chapter 5. The relation and what it orders (2)

## Why this chapter

What follows was pieced together backwards. The last item of it, grixreld pairs,
mornvint collections and a falkeld, was noticed before anyone had a reason to expect it.

Nothing here stands on its own. The arguments lean on chapters 1 and 3, and a reader who
has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
wrenclos that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D14. Grixreld pairs. Two distinct wrenclos x and y form a grixreld pair when x <~ y and
y <~ x both hold, that is, when each lies in the reldxil of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D3. Mornvint collections. A collection S of wrenclos is mornvint when x # y belongs to S
for every pair x, y drawn from S.

D9. A falkeld. A wrenclo f is a falkeld when f <~ y holds for every wrenclo y, that is,
when the reldxil of f is the whole system.

Running the definition over every wrenclo leaves glimfex.

## The shape of it

The right picture for tuclo is a spreading stain rather than a list. Drop one wrenclo
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
wrenclos depending on where it started.

The relation is easiest to see as a height. Each wrenclo casts a reldxil over what it
covers, and the sizes of those shadows here are 0 and 4. Sizes repeat, so the objects do
not line up in single file.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R8 rests on D4 (the reldxil of a wrenclo). Remove any one of them and the statement
stops making sense, not merely stops being provable.

T13 rests on D4 (the reldxil of a wrenclo) and A8 (transitivity of the relation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Take (vorkeld # falzam) # glimfex and work it out one step at a time.
    vorkeld # falzam = bratu   (the table for #)
    bratu # glimfex = bratu   (the table for #)
That leaves bratu, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is falzam # (glimfex # vorkeld) for contrast.
    glimfex # vorkeld = vorkeld   (the table for #)
    falzam # vorkeld = bratu   (the table for #)
The value is bratu. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test glimfex <~ bratu. The reldxil of glimfex is glimfex, bratu, vorkeld and falzam, and
bratu lies inside it, so the relation holds.

## A case that breaks

R8. It is not the case that: If x <~ y then y <~ x. It fails at x = glimfex, y = bratu.
One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by closure under the first operation and transitivity of the
relation. A system without them is not a system where these results are harder to prove;
it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A1 (closure under the first operation), A8
(transitivity of the relation) and D4 (the reldxil of a wrenclo).

What is built on it later: D8 (the tuclo of a wrenclo), T5 (the tunak is mornvint), T6
(the tuclo of a wrenclo is mornvint) and T11 (the shenhob is mornvint).

## Proofs

R8. It is not the case that: If x <~ y then y <~ x.

  (1) [S2] Take the case x = glimfex, y = bratu, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 16 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T13. If y lies in the reldxil of x, then the reldxil of y is contained in the reldxil of x.

  (1) [D4] Let y satisfy x <~ y and let z satisfy y <~ z.
  (2) [A8] Transitivity gives x <~ z.
  (3) [D4] So every member of the reldxil of y is a member of that of x.

Checked over 64 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward grixreld pairs, mornvint collections and a falkeld. Later chapters state
their results in these terms and do not restate the definitions.

The results now available are T13, each settled by exhaustive check rather than by
argument from analogy.

Explicitly not available: R8. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x016. How many wrenclos lie in the smallest mornvint collection containing bratu?
Level 4.
  x026. List every wrenclo in the falkeld.
  x038. The result above concerns reldxils. List the reldxil of glimfex.
Level 5.
  x041. The following fails in this system: If x <~ y then y <~ x. Name the earliest wrenclo, in the order the wrenclos were introduced, that witnesses the failure.

# Chapter 6. Combining objects (2)

## Why this chapter

The practical content of this chapter is the tunak, the shenhob and combining on the
left never merges two wrenclos. It is the part that shows up in use.

Prerequisites are real here: chapters 1 and 4 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over wrenclos, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D6. The tunak. The tunak of the system is the collection of wrenclos that morntez with
every wrenclo.

In this system that picks out glimfex, bratu, vorkeld and falzam, that is, all of them.

D7. The shenhob. The shenhob is the collection of all opalhurn wrenclos.

In this system that picks out glimfex, which is 1 of the 4 wrenclos.

## The shape of it

A useful mental split: some wrenclos are inert under the operation and some are not.
glimfex come back unchanged when combined with themselves, and glimfex, bratu, vorkeld
and falzam commute with everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 wrenclos the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T12 rests on A6 (cancellation in the first operation) and D2 (wrenclos that morntez).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

## A worked case

Evaluate (glimfex # falzam) # (vorkeld # bratu). Each line below is one lookup in a
table.
    glimfex # falzam = falzam   (the table for #)
    vorkeld # bratu = falzam   (the table for #)
    falzam # falzam = glimfex   (the table for #)
That leaves glimfex, and no other reading of the notation gives anything else.

A companion case, falzam # (vorkeld # glimfex), to show what the brackets are doing.
    vorkeld # glimfex = vorkeld   (the table for #)
    falzam # vorkeld = bratu   (the table for #)
That gives bratu, against glimfex above.

Test falzam <~ vorkeld. The reldxil of falzam is empty, and vorkeld lies outside it, so
the relation fails.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of wrenclos that come back
unchanged from themselves: glimfex. Assuming more of them than that is the mistake to
avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of cancellation in the first operation and
closure under the first operation. Those are properties of this system, not of systems
in general.

To see how little the notation guarantees: rebuild the system with the same names over
different tables and T12 fail outright.

## Neighbouring results

The material this chapter borrows from: A6 (cancellation in the first operation), D1
(opalhurn wrenclos) and D2 (wrenclos that morntez).

What is built on it later: T2 (the ponjen lies in the tunak), T5 (the tunak is
mornvint), T10 (the tuclo of a tunak wrenclo stays in the tunak) and T11 (the shenhob is
mornvint).

## Proofs

T12. For every wrenclo a, the assignment x to a # x sends distinct wrenclos to distinct wrenclos.

  (1) [A6] Suppose a # x = a # y.
  (2) [A6] Cancellation on the left gives x = y.
  (3) So the assignment is injective, and being injective on a finite carrier it is onto.

Checked over 16 cases: every object translated by every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the tunak and the shenhob. Each of these is used by
name later, so the names are worth learning rather than looking up.

The results now available are T12, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x019. Which wrenclos make up the shenhob? Name them all.

# Chapter 7. Neutral objects and reversal (2)

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through vintdri wrenclos, the thramorn
of a wrenclo and where the ponjen swallows everything breaks down.

Nothing here stands on its own. The arguments lean on chapters 2 and 4, and a reader who
has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
wrenclos that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D10. Vintdri wrenclos. A wrenclo x is vintdri when x # x equals the ponjen.

In this system that picks out glimfex, bratu, vorkeld and falzam, that is, all of them.

D11. The thramorn of a wrenclo. A thramorn of a wrenclo x is a wrenclo y with x # y = y
# x = glimfex.

Worked out for each wrenclo: glimfex to glimfex; bratu to bratu; vorkeld to vorkeld;
falzam to falzam.

## The shape of it

Neutrality is a strong condition disguised as a weak one. It fixes a single wrenclo and,
through that, constrains everything that can combine with it.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R9 rests on D5 (the ponjen). The dependence is on the content of those results, not only
on their vocabulary.

T1 rests on D5 (the ponjen) and A4 (a neutral object for the first operation). The
dependence is on the content of those results, not only on their vocabulary.

## A worked case

Here is (glimfex # vorkeld) # bratu, reduced without skipping anything.
    glimfex # vorkeld = vorkeld   (the table for #)
    vorkeld # bratu = falzam   (the table for #)
That leaves falzam, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take vorkeld # (bratu # glimfex).
    bratu # glimfex = bratu   (the table for #)
    vorkeld # bratu = falzam   (the table for #)
That gives falzam, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test falzam <~ glimfex. The reldxil of falzam is empty, and glimfex lies outside it, so
the relation fails.

## A case that breaks

R9. It is not the case that: e # x equals the ponjen for every wrenclo x. The case that
settles it: anchor = glimfex, x = bratu, value = bratu. Anyone carrying this claim over
from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by a neutral object for the first operation, closure under the first
operation and reversal under the first operation. A system without them is not a system
where these results are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A4 (a neutral object for the first operation), A5 (reversal under the
first operation), D1 (opalhurn wrenclos) and D5 (the ponjen).

These results are used again in T3 (a wrenclo has only one thramorn) and T4 (a vintdri
wrenclo is its own thramorn).

## Proofs

R9. It is not the case that: e # x equals the ponjen for every wrenclo x.

  (1) [S2] Take the case anchor = glimfex, x = bratu, value = bratu, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 4 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T1. There is exactly one wrenclo e with e # x = x # e = x for every wrenclo x.

  (1) [D5] Suppose e and f both leave every wrenclo unchanged.
  (2) [A4] Then e # f = f, reading e as neutral on the left.
  (3) [A4] And e # f = e, reading f as neutral on the right.
  (4) So e = f, and the two suppositions describe the same object.

Checked over 16 cases: every object paired with every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward vintdri wrenclos and the thramorn of a wrenclo. Later chapters state their
results in these terms and do not restate the definitions.

Established here and safe to use: T1.

Explicitly not available: R9. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x027. Write down the vintdri in full.
Level 5.
  x028. Let z be bratu # bratu. Name the thramorn of z.
  x042. The following fails in this system: e # x equals the ponjen for every wrenclo x. Name the earliest wrenclo, in the order the wrenclos were introduced, that witnesses the failure.

# Chapter 8. The relation and what it orders (3)

## Why this chapter

The present chapter develops the tuclo of a wrenclo, there is at most one falkeld and no
grixreld pairs exist.

Prerequisites are real here: chapters 3 and 5 supply the notions the statements below
are phrased in.

The standard of proof here is exhaustion. A universal claim about wrenclos covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

## What is defined here

D8. The tuclo of a wrenclo. The tuclo of a wrenclo x, written [x], is the smallest
mornvint collection that contains x.

Worked out for each wrenclo: glimfex to glimfex; bratu to glimfex and bratu; vorkeld to
glimfex and vorkeld; falzam to glimfex and falzam.

## The shape of it

Picture the tuclo as what happens when you start with one wrenclo and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 4 wrenclos, that stops. In this system the sizes it stops at are 1 and 2.

The relation is easiest to see as a height. Each wrenclo casts a reldxil over what it
covers, and the sizes of those shadows here are 0 and 4. Sizes repeat, so the objects do
not line up in single file.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T14 rests on D9 (a falkeld) and A7 (antisymmetry of the relation). The dependence is on
the content of those results, not only on their vocabulary.

T15 rests on D14 (grixreld pairs) and A7 (antisymmetry of the relation). Remove any one
of them and the statement stops making sense, not merely stops being provable.

## A worked case

Evaluate (falzam # glimfex) # (vorkeld # bratu). Each line below is one lookup in a
table.
    falzam # glimfex = falzam   (the table for #)
    vorkeld # bratu = falzam   (the table for #)
    falzam # falzam = glimfex   (the table for #)
So (falzam # glimfex) # (vorkeld # bratu) is glimfex.

Move the brackets and the work changes. Take glimfex # (vorkeld # falzam).
    vorkeld # falzam = bratu   (the table for #)
    glimfex # bratu = bratu   (the table for #)
The value is bratu, not glimfex.

One decision about the relation, since deciding is as much a skill as computing. Does
vorkeld <~ falzam hold? Read off what vorkeld stands over: nothing at all. falzam is not
among them, so it fails.

A second case, this time a tuclo. Start from falzam. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is glimfex and falzam,
so the iskkorr of falzam is 2.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by antisymmetry of the relation and closure under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A7 (antisymmetry of the relation), D14 (grixreld pairs), D3 (mornvint
collections) and D9 (a falkeld).

These results are used again in D12 (the iskkorr of a wrenclo), T6 (the tuclo of a
wrenclo is mornvint), T7 (the tuclo is contained in every mornvint collection) and T10
(the tuclo of a tunak wrenclo stays in the tunak).

## Proofs

T14. No two distinct wrenclos can both be falkelds.

  (1) [D9] Let f and h both be floors.
  (2) [D9] Then f <~ h, since h is any object, and h <~ f likewise.
  (3) [A7] Antisymmetry forces f = h.

Checked over 16 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T15. No two distinct wrenclos lie in each other's reldxil.

  (1) [D14] Suppose x and y form a tight pair.
  (2) [A7] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 16 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the tuclo of a wrenclo. Each of these is used by name
later, so the names are worth learning rather than looking up.

The results now available are T14 and T15, each settled by exhaustive check rather than
by argument from analogy.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x020. Name every wrenclo in [bratu].
  x021. List the tuclo of vorkeld.
  x022. List the tuclo of falzam.
Level 4.
  x023. Let z be bratu # falzam. List the tuclo of z.
  x024. Let z be falzam # falzam. List the tuclo of z.
  x025. Let z be bratu # glimfex. List the tuclo of z.
  x039. Name the wrenclos that make up the falkeld, which is what the result above is a claim about.

# Chapter 9. Combining objects (3)

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is where every
wrenclo is opalhurn breaks down, the shenhob is mornvint and every wrenclo lies in the
tunak.

Nothing here stands on its own. The arguments lean on chapters 1, 4, 5 and 6, and a
reader who has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about wrenclos covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

A useful mental split: some wrenclos are inert under the operation and some are not.
glimfex come back unchanged when combined with themselves, and glimfex, bratu, vorkeld
and falzam commute with everything.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R6 rests on D7 (the shenhob). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T11 rests on D7 (the shenhob) and D3 (mornvint collections). The dependence is on the
content of those results, not only on their vocabulary.

T16 rests on D6 (the tunak). The dependence is on the content of those results, not only
on their vocabulary.

T2 rests on D5 (the ponjen) and D6 (the tunak). Remove any one of them and the statement
stops making sense, not merely stops being provable.

T5 rests on D6 (the tunak), D3 (mornvint collections) and A2 (association of the first
operation). Remove any one of them and the statement stops making sense, not merely
stops being provable.

## A worked case

Here is (bratu # vorkeld) # glimfex, reduced without skipping anything.
    bratu # vorkeld = falzam   (the table for #)
    falzam # glimfex = falzam   (the table for #)
So (bratu # vorkeld) # glimfex is falzam.

A companion case, vorkeld # (glimfex # bratu), to show what the brackets are doing.
    glimfex # bratu = bratu   (the table for #)
    vorkeld # bratu = falzam   (the table for #)
That gives falzam, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test vorkeld <~ glimfex. The reldxil of vorkeld is empty, and glimfex lies outside it,
so the relation fails.

## A case that breaks

R6. It is not the case that: x # x = x for every wrenclo x. The case that settles it: x
= bratu, value = glimfex. Anyone carrying this claim over from a more familiar system
will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation and closure under the first operation. Those are
properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A2 (association of the first operation), D3
(mornvint collections), D5 (the ponjen) and D6 (the tunak).

What is built on it later: T10 (the tuclo of a tunak wrenclo stays in the tunak).

## Proofs

R6. It is not the case that: x # x = x for every wrenclo x.

  (1) [S2] Take the case x = bratu, value = glimfex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 4 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T11. If x and y are both opalhurn then so is x # y.

  (1) [D7] Let x and y be opalhurn.
  (2) [D1] The claim asks whether (x # y) # (x # y) returns x # y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 16 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

T16. Every pair of wrenclos morntezs.

  (1) [D6] The tunak is defined by morntezing with everything.
  (2) [D2] The claim is that x # y = y # x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 16 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T2. The ponjen morntezs with every wrenclo.

  (1) [D5] Let e be the ponjen and x any wrenclo.
  (2) [D5] Then e # x = x and x # e = x.
  (3) [D2] So e # x = x # e, which is what it means to morntez.
  (4) [D6] Since x was arbitrary, e belongs to the tunak.

Checked over 4 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T5. If x and y both morntez with every wrenclo, then so does x # y.

  (1) [D6] Let x and y lie in the tunak and let z be any wrenclo.
  (2) [A2] Then (x # y) # z = x # (y # z).
  (3) [D6] Move z past y, then past x, using that each morntezs with everything.
  (4) [D3] So x # y morntezs with z, and the tunak is mornvint.

Checked over 16 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

The results now available are T11, T16, T2 and T5, each settled by exhaustive check
rather than by argument from analogy.

Do not carry forward R6. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x037. Name the wrenclos that make up the shenhob, which is what the result above is a claim about.
Level 5.
  x040. The following fails in this system: x # x = x for every wrenclo x. Name the earliest wrenclo, in the order the wrenclos were introduced, that witnesses the failure.

# Chapter 10. Collections that close on themselves

## Why this chapter

What follows was pieced together backwards. The last item of it, the iskkorr of a
wrenclo, a wrenclo has only one thramorn and the tuclo of a wrenclo is mornvint, was
noticed before anyone had a reason to expect it.

Prerequisites are real here: chapters 1, 5, 7 and 8 supply the notions the statements
below are phrased in.

The standard of proof here is exhaustion. A universal claim about wrenclos covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

## What is defined here

D12. The iskkorr of a wrenclo. The iskkorr of a wrenclo x is the number of wrenclos in
its tuclo [x].

Worked out for each wrenclo: glimfex to 1; bratu to 2; vorkeld to 2; falzam to 2.

## The shape of it

Picture the tuclo as what happens when you start with one wrenclo and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 4 wrenclos, that stops. In this system the sizes it stops at are 1 and 2.

The neutral wrenclo glimfex is the one that does nothing. That sounds trivial and is
not: almost every result in this chapter is an argument about what doing nothing forces.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T3 rests on D11 (the thramorn of a wrenclo), A2 (association of the first operation) and
T1 (the ponjen is the only one of its kind). Remove any one of them and the statement
stops making sense, not merely stops being provable.

T6 rests on D8 (the tuclo of a wrenclo) and D3 (mornvint collections). Remove any one of
them and the statement stops making sense, not merely stops being provable.

## A worked case

Here is (vorkeld # glimfex) # (falzam # bratu), reduced without skipping anything.
    vorkeld # glimfex = vorkeld   (the table for #)
    falzam # bratu = vorkeld   (the table for #)
    vorkeld # vorkeld = glimfex   (the table for #)
The expression comes to glimfex.

Move the brackets and the work changes. Take glimfex # (falzam # vorkeld).
    falzam # vorkeld = bratu   (the table for #)
    glimfex # bratu = bratu   (the table for #)
The value is bratu, not glimfex.

Test vorkeld <~ glimfex. The reldxil of vorkeld is empty, and glimfex lies outside it,
so the relation fails.

A second case, this time a tuclo. Start from bratu. Combine it with itself, add whatever
is new, and repeat until nothing is added. What survives is glimfex and bratu, so the
iskkorr of bratu is 2.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of wrenclos that come back
unchanged from themselves: glimfex. Assuming more of them than that is the mistake to
avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation, closure under the first operation and reversal under
the first operation. Those are properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A2 (association of the first operation), D11
(the thramorn of a wrenclo), D3 (mornvint collections) and D8 (the tuclo of a wrenclo).

What is built on it later: D13 (the wrennak), T4 (a vintdri wrenclo is its own
thramorn), T7 (the tuclo is contained in every mornvint collection) and T8 (a wrenclo is
opalhurn exactly when its iskkorr is one).

## Proofs

T3. For every wrenclo x there is exactly one thramorn of x.

  (1) [D11] Let y and z both be partners of x.
  (2) [A2] Then y = y # (x # z) = (y # x) # z.
  (3) [D11] Both bracketed products collapse to the neutral object.
  (4) So y = z.

Checked over 16 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T6. For every wrenclo x, the collection [x] is mornvint.

  (1) [D8] [x] is built by taking x and closing under #.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 64 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the iskkorr of a wrenclo. Later chapters state their results in these
terms and do not restate the definitions.

The results now available are T3 and T6, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x029. How many wrenclos lie in [bratu]?
  x030. How many wrenclos lie in [falzam]?
Level 5.
  x031. Let z be (glimfex # falzam) # glimfex. What is the iskkorr of z?
  x032. Let z be (glimfex # bratu) # falzam. What is the iskkorr of z?
  x033. Let z be (bratu # falzam) # falzam. What is the iskkorr of z?
  x034. Let z be (glimfex # vorkeld) # falzam. What is the iskkorr of z?

# Chapter 11. Collections that close on themselves (2)

## Why this chapter

The practical content of this chapter is the wrennak, where some wrenclo reaches every
other breaks down and the tuclo of a tunak wrenclo stays in the tunak. It is the part
that shows up in use.

Prerequisites are real here: chapters 4, 6, 7, 8, 9 and 10 supply the notions the
statements below are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
wrenclos that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D13. The wrennak. The wrennak of the system is the collection of wrenclos whose iskkorr
is largest.

Running the definition over every wrenclo leaves bratu, vorkeld and falzam.

## The shape of it

The right picture for tuclo is a spreading stain rather than a list. Drop one wrenclo
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
wrenclos depending on where it started.

Two questions sort the wrenclos quickly. Does combining a wrenclo with itself change it?
For glimfex it does not. Does it matter which side it goes on? For glimfex, bratu,
vorkeld and falzam it does not.

The neutral wrenclo glimfex is the one that does nothing. That sounds trivial and is
not: almost every result in this chapter is an argument about what doing nothing forces.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R7 rests on D8 (the tuclo of a wrenclo) and D12 (the iskkorr of a wrenclo). The
dependence is on the content of those results, not only on their vocabulary.

T10 rests on D8 (the tuclo of a wrenclo), D6 (the tunak) and T5 (the tunak is mornvint).
The dependence is on the content of those results, not only on their vocabulary.

T4 rests on D10 (vintdri wrenclos), D11 (the thramorn of a wrenclo) and T3 (a wrenclo
has only one thramorn). Remove any one of them and the statement stops making sense, not
merely stops being provable.

T7 rests on D8 (the tuclo of a wrenclo) and T6 (the tuclo of a wrenclo is mornvint). The
dependence is on the content of those results, not only on their vocabulary.

T8 rests on D1 (opalhurn wrenclos), D12 (the iskkorr of a wrenclo) and T6 (the tuclo of
a wrenclo is mornvint). The dependence is on the content of those results, not only on
their vocabulary.

T9 rests on D12 (the iskkorr of a wrenclo) and T6 (the tuclo of a wrenclo is mornvint).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

## A worked case

Here is (falzam # bratu) # vorkeld, reduced without skipping anything.
    falzam # bratu = vorkeld   (the table for #)
    vorkeld # vorkeld = glimfex   (the table for #)
The expression comes to glimfex.

Bracketing is not cosmetic, so here is bratu # (vorkeld # falzam) for contrast.
    vorkeld # falzam = bratu   (the table for #)
    bratu # bratu = glimfex   (the table for #)
That gives glimfex, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
vorkeld <~ vorkeld hold? Read off what vorkeld stands over: nothing at all. vorkeld is
not among them, so it fails.

## A case that breaks

R7. It is not the case that: There is a wrenclo whose tuclo is the whole system. The
case that settles it: largest_span = 2, size = 4. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation, closure under the first operation and reversal under
the first operation. Those are properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: D1 (opalhurn wrenclos), D10 (vintdri wrenclos),
D11 (the thramorn of a wrenclo) and D12 (the iskkorr of a wrenclo).

## Proofs

R7. It is not the case that: There is a wrenclo whose tuclo is the whole system.

  (1) [S2] Take the case largest_span = 2, size = 4, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 4 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T10. If x lies in the tunak then every wrenclo of [x] lies in the tunak.

  (1) [T5] The tunak is mornvint.
  (2) [D8] [x] is the smallest mornvint collection containing x.
  (3) A smallest such collection sits inside any other, and the tunak is one.

Checked over 16 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

T4. If x # x is the ponjen then the thramorn of x is x itself.

  (1) [D10] Let x be vintdri, so x # x is the ponjen.
  (2) [D11] That is exactly the condition for x to be a partner of x.
  (3) [T3] Partners are unique, so no other object can be one.

Checked over 4 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T7. If S is mornvint and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 20 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T8. x # x = x holds if and only if [x] contains x alone.

  (1) [D1] If x # x = x then {x} is already closed under #.
  (2) [T6] So [x] = {x} and the iskkorr is one.
  (3) [D12] Conversely a span of one object must contain x # x, which is then x.

Checked over 4 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T9. For every wrenclo x, the iskkorr of x divides 4.

  (1) [T6] [x] is a mornvint collection.
  (2) [D12] Its size is the iskkorr of x.
  (3) The claim is that this size always divides 4.

Checked over 4 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the wrennak. Each of these is used by name later, so
the names are worth learning rather than looking up.

The results now available are T10, T4, T7, T8 and T9, each settled by exhaustive check
rather than by argument from analogy.

Explicitly not available: R7. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x035. Which wrenclos make up the wrennak? Name them all.
  x036. What is the largest iskkorr any wrenclo has?
