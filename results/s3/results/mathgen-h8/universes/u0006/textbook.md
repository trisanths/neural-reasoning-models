# The Vexumb system

This book is about grixbras. A grixbra is not a number and not a set; it is one of
exactly 5 objects, and everything said here is said about how those 5 objects combine.

The grixbras are written mika, fexnyr, hobglim, umbtarn and mornthra. The first
operation is written @. The second is written ! and binds more tightly, so x @ y ! z
means x @ (y ! z). The relation is written %%; where it holds between two grixbras we
say the left one shadows the right one. Both operations associate to the left when
written without brackets, and brackets override that. Repeated combination is
abbreviated: x^3 means x @ x @ x.

Readers arriving from arithmetic should put it down at the door. The operations below
are defined by their tables and by nothing else. Several arithmetic habits survive the
crossing and several do not, and the text is careful to say which is which.

# Chapter 1. The objects and their notation

## Why this chapter

We turn to the Vexumb signature, the Vexumb combination tables and closure under the
first operation. The treatment is self contained given the material already established.

One habit to adopt: when a statement below quantifies over grixbras, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## The tables in full

The table for @. Read the left argument down the side and the right argument across the top.

          |      mika    fexnyr   hobglim   umbtarn  mornthra
-------------------------------------------------------------
     mika |      mika      mika      mika      mika      mika
   fexnyr |    fexnyr      mika      mika      mika      mika
  hobglim |   hobglim    fexnyr      mika      mika      mika
  umbtarn |   umbtarn   hobglim    fexnyr      mika      mika
 mornthra |  mornthra   umbtarn   hobglim    fexnyr      mika

The table for !. Read the left argument down the side and the right argument across the top.

          |      mika    fexnyr   hobglim   umbtarn  mornthra
-------------------------------------------------------------
     mika |      mika    fexnyr   hobglim   umbtarn  mornthra
   fexnyr |    fexnyr    fexnyr   hobglim   umbtarn  mornthra
  hobglim |   hobglim   hobglim   hobglim   umbtarn  mornthra
  umbtarn |   umbtarn   umbtarn   umbtarn   umbtarn  mornthra
 mornthra |  mornthra  mornthra  mornthra  mornthra  mornthra

Every pair standing in the %% relation, grouped by left argument.

  mika %% mika
  fexnyr %% fexnyr
  hobglim %% hobglim
  umbtarn %% umbtarn
  mornthra %% mornthra

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A1. Closure under the first operation. For all grixbras x and y, x @ y is again a
grixbra.

## The shape of it

A useful mental split: some grixbras are inert under the operation and some are not.
mika come back unchanged when combined with themselves, and none commutes with
everything.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R1 rests on S2 (the Vexumb combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R2 rests on S2 (the Vexumb combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

R5 rests on S2 (the Vexumb combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R6 rests on S2 (the Vexumb combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

## A worked case

Take hobglim @ mornthra ! mika and work it out one step at a time.
    mornthra ! mika = mornthra   (the table for !)
    hobglim @ mornthra = mika   (the table for @)
That leaves mika, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is mornthra @ (mika @ hobglim) for contrast.
    mika @ hobglim = mika   (the table for @)
    mornthra @ mika = mornthra   (the table for @)
That gives mornthra, against mika above.

Test mika %% hobglim. The yukvash of mika is mika, and hobglim lies outside it, so the
relation fails.

## A case that breaks

R1. It is not the case that: For all grixbras x, y, z: (x @ y) @ z = x @ (y @ z). The
case that settles it: x = fexnyr, y = mika, z = fexnyr, left = mika, right = fexnyr.
Anyone carrying this claim over from a more familiar system will be wrong here, and
wrong in a way that propagates.

R2. It is not the case that: For all grixbras x and y: x @ y = y @ x. The case that
settles it: x = mika, y = fexnyr, left = mika, right = fexnyr. Anyone carrying this
claim over from a more familiar system will be wrong here, and wrong in a way that
propagates.

R5. It is not the case that: For every grixbra x: x @ x = x. The case that settles it: x
= fexnyr, value = mika. Anyone carrying this claim over from a more familiar system will
be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

What is built on it later: A2 (closure under the second operation), A3 (association of
the second operation), A4 (commutation of the second operation) and A5 (a neutral object
for the second operation).

## Proofs

R1. It is not the case that: For all grixbras x, y, z: (x @ y) @ z = x @ (y @ z).

  (1) [S2] Take the case x = fexnyr, y = mika, z = fexnyr, left = mika, right = fexnyr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R2. It is not the case that: For all grixbras x and y: x @ y = y @ x.

  (1) [S2] Take the case x = mika, y = fexnyr, left = mika, right = fexnyr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R5. It is not the case that: For every grixbra x: x @ x = x.

  (1) [S2] Take the case x = fexnyr, value = mika, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R6. It is not the case that: For all grixbras x, y, z: if x @ y = x @ z then y = z.

  (1) [S2] Take the case x = mika, y = mika, z = fexnyr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R1, R2, R5 and R6. These were tested and failed, and the failing
cases are recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 1.
  x001. Work out the value of fexnyr @ hobglim.
  x002. Work out the value of umbtarn @ fexnyr.
  x003. What grixbra does umbtarn @ mornthra name?
Level 2.
  x004. Work out the value of umbtarn @ mornthra ! umbtarn.
  x005. What grixbra does hobglim @ hobglim ! umbtarn name?
  x006. What grixbra does (fexnyr @ mornthra) @ umbtarn name?
  x007. Reduce (mornthra @ hobglim) @ mornthra to a single grixbra.
  x008. Reduce (fexnyr @ fexnyr) @ hobglim to a single grixbra.
  x009. Evaluate umbtarn^3.
  x010. Evaluate mornthra^3.
  x011. What is fexnyr combined with itself 3 times under @?
  x012. Which grixbras x satisfy x @ fexnyr = mika? List them all.
  x013. Which grixbras x satisfy x @ hobglim = fexnyr? List them all.
  x014. Which grixbras x satisfy x @ umbtarn = mika? List them all.
  x015. Solve x @ hobglim = hobglim for x, naming every solution.
Level 3.
  x016. Evaluate hobglim @ mornthra ! fexnyr, minding which operation binds tighter.
  x017. Evaluate mornthra @ umbtarn ! mika, minding which operation binds tighter.
  x018. Evaluate hobglim @ mornthra ! mornthra, minding which operation binds tighter.
Level 5.
  x019. The following fails in this system: For all grixbras x, y, z: (x @ y) @ z = x @ (y @ z). Name the earliest grixbra, in the order the grixbras were introduced, that witnesses the failure.
  x020. The following fails in this system: For all grixbras x and y: x @ y = y @ x. Name the earliest grixbra, in the order the grixbras were introduced, that witnesses the failure.
  x022. The following fails in this system: For every grixbra x: x @ x = x. Name the earliest grixbra, in the order the grixbras were introduced, that witnesses the failure.
  x023. The following fails in this system: For all grixbras x, y, z: if x @ y = x @ z then y = z. Name the earliest grixbra, in the order the grixbras were introduced, that witnesses the failure.

# Chapter 2. Neutral objects and reversal

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is the system does
not have a neutral object for the first operation, the system does not have reversal
under the first operation and the system does not have an absorbing object for the first
operation.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

The standard of proof here is exhaustion. A universal claim about grixbras covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

The neutral grixbra is the one that does nothing. That sounds trivial and is not: almost
every result in this chapter is an argument about what doing nothing forces.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R3 rests on S2 (the Vexumb combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R4 rests on S2 (the Vexumb combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

R7 rests on S2 (the Vexumb combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

## A worked case

Take (mika @ mornthra) @ (hobglim @ fexnyr) and work it out one step at a time.
    mika @ mornthra = mika   (the table for @)
    hobglim @ fexnyr = fexnyr   (the table for @)
    mika @ fexnyr = mika   (the table for @)
So (mika @ mornthra) @ (hobglim @ fexnyr) is mika.

Bracketing is not cosmetic, so here is mornthra @ (hobglim @ mika) for contrast.
    hobglim @ mika = hobglim   (the table for @)
    mornthra @ hobglim = hobglim   (the table for @)
That gives hobglim, against mika above.

One decision about the relation, since deciding is as much a skill as computing. Does
hobglim %% fexnyr hold? Read off what hobglim stands over: hobglim. fexnyr is not among
them, so it fails.

## A case that breaks

R3. There is no grixbra e with e @ x = x @ e = x for every grixbra x. It fails at reason
= no two sided identity exists. One case is enough, and this is the earliest one.

R4. Some grixbra x admits no grixbra y for which x @ y and y @ x both land on a neutral
object. The case that settles it: reason = no identity, so inverses are not defined.
Anyone carrying this claim over from a more familiar system will be wrong here, and
wrong in a way that propagates.

R7. There is no grixbra z with z @ x = x @ z = z for every grixbra x. The case that
settles it: reason = no absorbing element. Anyone carrying this claim over from a more
familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside S2 (the Vexumb combination tables).

## Proofs

R3. There is no grixbra e with e @ x = x @ e = x for every grixbra x.

  (1) [S2] Take the case reason = no two sided identity exists, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R4. Some grixbra x admits no grixbra y for which x @ y and y @ x both land on a neutral object.

  (1) [S2] Take the case reason = no identity, so inverses are not defined, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R7. There is no grixbra z with z @ x = x @ z = z for every grixbra x.

  (1) [S2] Take the case reason = no absorbing element, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R3, R4 and R7. A later argument that quietly assumes one of
these is wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 5.
  x021. The following fails in this system: Some grixbra x admits no grixbra y for which x @ y and y @ x both land on a neutral object. Name the earliest grixbra, in the order the grixbras were introduced, that witnesses the failure.

# Chapter 3. The relation and what it orders

## Why this chapter

What follows was pieced together backwards. The last item of it, agreement of the
relation with the first operation, agreement of the relation with the second operation
and reflexivity of the relation, was noticed before anyone had a reason to expect it.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
grixbras that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A10. Agreement of the relation with the first operation. For all grixbras x, y, z: if x
%% y then (z @ x) %% (z @ y) and (x @ z) %% (y @ z).

A11. Agreement of the relation with the second operation. For all grixbras x, y, z: if x
%% y then (z ! x) %% (z ! y) and (x ! z) %% (y ! z).

A7. Reflexivity of the relation. For every grixbra x: x %% x.

A8. Antisymmetry of the relation. For all grixbras x and y: if x %% y and y %% x then x
= y.

A9. Transitivity of the relation. For all grixbras x, y, z: if x %% y and y %% z then x
%% z.

D4. The yukvash of a grixbra. The yukvash of a grixbra x is the collection of grixbras y
for which x %% y holds.

Worked out for each grixbra: mika to mika; fexnyr to fexnyr; hobglim to hobglim; umbtarn
to umbtarn; mornthra to mornthra.

## The shape of it

The relation is easiest to see as a height. Each grixbra casts a yukvash over what it
shadows, and the sizes of those shadows here are 1. Sizes repeat, so the objects do not
line up in single file.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R10 rests on S2 (the Vexumb combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Take umbtarn @ hobglim ! mika and work it out one step at a time.
    hobglim ! mika = hobglim   (the table for !)
    umbtarn @ hobglim = fexnyr   (the table for @)
The expression comes to fexnyr.

Move the brackets and the work changes. Take hobglim @ (mika @ umbtarn).
    mika @ umbtarn = mika   (the table for @)
    hobglim @ mika = hobglim   (the table for @)
That gives hobglim, against fexnyr above.

One decision about the relation, since deciding is as much a skill as computing. Does
hobglim %% mika hold? Read off what hobglim stands over: hobglim. mika is not among
them, so it fails.

## A case that breaks

R10. It is not the case that: For all grixbras x and y, at least one of x %% y and y %%
x holds. The case that settles it: x = mika, y = fexnyr. Anyone carrying this claim over
from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside S2 (the Vexumb combination tables).

These results are used again in D8 (a wrenreld), D11 (quilmi pairs), T5 (yukvashs are
nested along the relation) and T6 (there is at most one wrenreld).

## Proofs

R10. It is not the case that: For all grixbras x and y, at least one of x %% y and y %% x holds.

  (1) [S2] Take the case x = mika, y = fexnyr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the yukvash of a grixbra. Later chapters state their results in these
terms and do not restate the definitions.

Do not carry forward R10. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 5.
  x024. The following fails in this system: For all grixbras x and y, at least one of x %% y and y %% x holds. Name the earliest grixbra, in the order the grixbras were introduced, that witnesses the failure.

# Chapter 4. The second operation and how the two interact

## Why this chapter

Anyone using this system to keep track of something will meet closure under the second
operation, association of the second operation and commutation of the second operation
early, whether or not they go looking.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about grixbras covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A2. Closure under the second operation. For all grixbras x and y, x ! y is again a
grixbra.

A3. Association of the second operation. For all grixbras x, y, z: (x ! y) ! z = x ! (y
! z).

A4. Commutation of the second operation. For all grixbras x and y: x ! y = y ! x.

A5. A neutral object for the second operation. There is a grixbra mika with mika ! x = x
for every x.

A6. Self combination under the second operation. For every grixbra x: x ! x = x.

## The shape of it

With two operations the question stops being what each does and becomes how they
interfere. ! binds tighter, so the interference shows up whenever a bracket is left off.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 grixbras the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R8 rests on S2 (the Vexumb combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R9 rests on S2 (the Vexumb combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

## A worked case

Take (fexnyr @ hobglim) @ (mornthra @ mika) and work it out one step at a time.
    fexnyr @ hobglim = mika   (the table for @)
    mornthra @ mika = mornthra   (the table for @)
    mika @ mornthra = mika   (the table for @)
The expression comes to mika.

Bracketing is not cosmetic, so here is hobglim @ (mornthra @ fexnyr) for contrast.
    mornthra @ fexnyr = umbtarn   (the table for @)
    hobglim @ umbtarn = mika   (the table for @)
That gives mika, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test umbtarn %% mornthra. The yukvash of umbtarn is umbtarn, and mornthra lies outside
it, so the relation fails.

## A case that breaks

R8. It is not the case that: For all grixbras x, y, z: x ! (y @ z) = (x ! y) @ (x ! z),
and the same on the right. It fails at x = fexnyr, y = mika, z = mika, left = fexnyr,
right = mika. One case is enough, and this is the earliest one.

R9. It is not the case that: For all grixbras x and y: x @ (x ! y) = x and x ! (x @ y) =
x. It fails at x = fexnyr, y = mika, value = mika. One case is enough, and this is the
earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside S2 (the Vexumb combination tables).

## Proofs

R8. It is not the case that: For all grixbras x, y, z: x ! (y @ z) = (x ! y) @ (x ! z), and the same on the right.

  (1) [S2] Take the case x = fexnyr, y = mika, z = mika, left = fexnyr, right = mika, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R9. It is not the case that: For all grixbras x and y: x @ (x ! y) = x and x ! (x @ y) = x.

  (1) [S2] Take the case x = fexnyr, y = mika, value = mika, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R8 and R9. These were tested and failed, and the failing cases are
recorded above.

## Exercises

This chapter carries no exercises. Nothing in it can be asked about in a way that could
not be answered without reading it, and an exercise like that is worse than none.

# Chapter 5. Combining objects

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through reldjen grixbras, grixbras
that grixovi and umbgel collections.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about grixbras covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

## What is defined here

D1. Reldjen grixbras. A grixbra x is called reldjen when x @ x = x.

In this system that picks out mika, which is 1 of the 5 grixbras.

D2. Grixbras that grixovi. Two grixbras x and y are said to grixovi when x @ y = y @ x.

D3. Umbgel collections. A collection S of grixbras is umbgel when x @ y belongs to S for
every pair x, y drawn from S.

## The shape of it

Picture the kavor as what happens when you start with one grixbra and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 5 grixbras, that stops. In this system the sizes it stops at are 1 and 2.

A useful mental split: some grixbras are inert under the operation and some are not.
mika come back unchanged when combined with themselves, and none commutes with
everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 grixbras the table is short enough to consult every time.

## Where these results come from

This chapter is groundwork. The derivations that use it start in the next one.

## A worked case

Evaluate fexnyr @ mornthra ! umbtarn. Each line below is one lookup in a table.
    mornthra ! umbtarn = mornthra   (the table for !)
    fexnyr @ mornthra = mika   (the table for @)
The expression comes to mika.

Move the brackets and the work changes. Take mornthra @ (umbtarn @ fexnyr).
    umbtarn @ fexnyr = hobglim   (the table for @)
    mornthra @ hobglim = hobglim   (the table for @)
That gives hobglim, against mika above.

One decision about the relation, since deciding is as much a skill as computing. Does
hobglim %% mornthra hold? Read off what hobglim stands over: hobglim. mornthra is not
among them, so it fails.

## A case that breaks

A quick guard against a common slip: hobglim @ fexnyr is fexnyr while fexnyr @ hobglim
is mika. Order is not decoration in this system.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A1 (closure under the first operation).

What is built on it later: D5 (the quilquil), D6 (the ovitez), D7 (the kavor of a
grixbra) and T1 (the kavor of a grixbra is umbgel).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

New vocabulary from this chapter: reldjen grixbras, grixbras that grixovi and umbgel
collections. Each of these is used by name later, so the names are worth learning rather
than looking up.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x025. Which grixbras make up the reldjen? Name them all.
  x026. How many grixbras lie in the smallest umbgel collection containing fexnyr?
  x027. How many grixbras lie in the smallest umbgel collection containing hobglim?

# Chapter 6. The relation and what it orders (2)

## Why this chapter

We turn to quilmi pairs, a wrenreld and yukvashs are nested along the relation. The
treatment is self contained given the material already established.

Nothing here stands on its own. The arguments lean on chapter 3, and a reader who has
skipped it will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about grixbras covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

## What is defined here

D11. Quilmi pairs. Two distinct grixbras x and y form a quilmi pair when x %% y and y %%
x both hold, that is, when each lies in the yukvash of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D8. A wrenreld. A grixbra f is a wrenreld when f %% y holds for every grixbra y, that
is, when the yukvash of f is the whole system.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

## The shape of it

The relation is easiest to see as a height. Each grixbra casts a yukvash over what it
shadows, and the sizes of those shadows here are 1. Sizes repeat, so the objects do not
line up in single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 grixbras the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T5 rests on D4 (the yukvash of a grixbra) and A9 (transitivity of the relation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

T7 rests on D4 (the yukvash of a grixbra) and A10 (agreement of the relation with the
first operation). The dependence is on the content of those results, not only on their
vocabulary.

T9 rests on D4 (the yukvash of a grixbra). Remove any one of them and the statement
stops making sense, not merely stops being provable.

## A worked case

Here is (mika @ fexnyr) @ (hobglim @ mornthra), reduced without skipping anything.
    mika @ fexnyr = mika   (the table for @)
    hobglim @ mornthra = mika   (the table for @)
    mika @ mika = mika   (the table for @)
That leaves mika, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take fexnyr @ (hobglim @ mika).
    hobglim @ mika = hobglim   (the table for @)
    fexnyr @ hobglim = mika   (the table for @)
That gives mika, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
mika %% mornthra hold? Read off what mika stands over: mika. mornthra is not among them,
so it fails.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by agreement of the relation with the first operation and
transitivity of the relation. A system without them is not a system where these results
are harder to prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A10 (agreement of the relation with the first
operation), A9 (transitivity of the relation) and D4 (the yukvash of a grixbra).

These results are used again in T6 (there is at most one wrenreld) and T8 (no quilmi
pairs exist).

## Proofs

T5. If y lies in the yukvash of x, then the yukvash of y is contained in the yukvash of x.

  (1) [D4] Let y satisfy x %% y and let z satisfy y %% z.
  (2) [A9] Transitivity gives x %% z.
  (3) [D4] So every member of the yukvash of y is a member of that of x.

Checked over 125 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T7. If x %% y then (x @ z) %% (y @ z) for every grixbra z.

  (1) [D4] Let y lie in the yukvash of x.
  (2) [A10] Compatibility applies the operation to both sides at once.
  (3) Nothing else is needed, since z was arbitrary.

Checked over 125 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T9. If x %% y then y %% x.

  (1) [D4] Symmetry would mean y lies in the yukvash of x exactly when x lies in that of y.
  (2) The listed pairs settle it directly.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward quilmi pairs and a wrenreld. Later chapters state their results in these
terms and do not restate the definitions.

The results now available are T5, T7 and T9, each settled by exhaustive check rather
than by argument from analogy.

## Exercises

No exercises here. Every question this chapter suggested turned out to be answerable
from the question itself, so all of them were discarded.

# Chapter 7. Combining objects (2)

## Why this chapter

Work through this chapter with the tables in front of you. It covers the quilquil, the
ovitez and the kavor of a grixbra, and each claim can be checked by hand.

Nothing here stands on its own. The arguments lean on chapter 5, and a reader who has
skipped it will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over grixbras, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D5. The quilquil. The quilquil of the system is the collection of grixbras that grixovi
with every grixbra.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D6. The ovitez. The ovitez is the collection of all reldjen grixbras.

Running the definition over every grixbra leaves mika.

D7. The kavor of a grixbra. The kavor of a grixbra x, written [x], is the smallest
umbgel collection that contains x.

Worked out for each grixbra: mika to mika; fexnyr to mika and fexnyr; hobglim to mika
and hobglim; umbtarn to mika and umbtarn; mornthra to mika and mornthra.

## The shape of it

The right picture for kavor is a spreading stain rather than a list. Drop one grixbra
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
grixbras depending on where it started.

Two questions sort the grixbras quickly. Does combining a grixbra with itself change it?
For mika it does not. Does it matter which side it goes on? It always does.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Nothing is derived in this chapter. It lays down material that later chapters draw on.

## A worked case

Here is umbtarn @ mornthra ! hobglim, reduced without skipping anything.
    mornthra ! hobglim = mornthra   (the table for !)
    umbtarn @ mornthra = mika   (the table for @)
The expression comes to mika.

A companion case, mornthra @ (hobglim @ umbtarn), to show what the brackets are doing.
    hobglim @ umbtarn = mika   (the table for @)
    mornthra @ mika = mornthra   (the table for @)
That gives mornthra, against mika above.

Test hobglim %% hobglim. The yukvash of hobglim is hobglim, and hobglim lies inside it,
so the relation holds.

Now compute [mornthra]. Fold mornthra against itself, then fold whatever appeared
against everything present, and stop when a round adds nothing. The result is mika and
mornthra, of size 2.

## A case that breaks

A quick guard against a common slip: umbtarn @ mornthra is mika while mornthra @ umbtarn
is fexnyr. Order is not decoration in this system.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside D1 (reldjen grixbras), D2 (grixbras that grixovi) and D3 (umbgel
collections).

What is built on it later: D9 (the iskka of a grixbra), T1 (the kavor of a grixbra is
umbgel), T2 (the kavor is contained in every umbgel collection) and T4 (the ovitez is
umbgel).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

New vocabulary from this chapter: the quilquil, the ovitez and the kavor of a grixbra.
Each of these is used by name later, so the names are worth learning rather than looking
up.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x028. List every grixbra in the ovitez.
  x029. Name every grixbra in [fexnyr].
  x030. Name every grixbra in [hobglim].
  x031. List the kavor of umbtarn.
  x032. Name every grixbra in [mornthra].
Level 4.
  x033. Let z be umbtarn @ umbtarn. List the kavor of z.
  x034. Let z be fexnyr @ fexnyr. List the kavor of z.

# Chapter 8. Combining objects (3)

## Why this chapter

The results collected here were not found in this order. There is at most one wrenreld,
no quilmi pairs exist and where every grixbra lies in the quilquil breaks down came
first, and the rest was assembled around that once the pattern was visible.

Prerequisites are real here: chapters 3, 5, 6 and 7 supply the notions the statements
below are phrased in.

The standard of proof here is exhaustion. A universal claim about grixbras covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

Think of %% as pointing downhill. The yukvash of a grixbra is everything downhill of it,
and those shadows here have sizes 1.

Two questions sort the grixbras quickly. Does combining a grixbra with itself change it?
For mika it does not. Does it matter which side it goes on? It always does.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T6 rests on D8 (a wrenreld) and A8 (antisymmetry of the relation). The dependence is on
the content of those results, not only on their vocabulary.

T8 rests on D11 (quilmi pairs) and A8 (antisymmetry of the relation). The dependence is
on the content of those results, not only on their vocabulary.

R12 rests on D5 (the quilquil). Remove any one of them and the statement stops making
sense, not merely stops being provable.

R13 rests on D6 (the ovitez). The dependence is on the content of those results, not
only on their vocabulary.

T4 rests on D6 (the ovitez) and D3 (umbgel collections). The dependence is on the
content of those results, not only on their vocabulary.

## A worked case

Take (mornthra @ fexnyr) @ (mika @ hobglim) and work it out one step at a time.
    mornthra @ fexnyr = umbtarn   (the table for @)
    mika @ hobglim = mika   (the table for @)
    umbtarn @ mika = umbtarn   (the table for @)
That leaves umbtarn, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take fexnyr @ (mika @ mornthra).
    mika @ mornthra = mika   (the table for @)
    fexnyr @ mika = fexnyr   (the table for @)
The value is fexnyr, not umbtarn.

One decision about the relation, since deciding is as much a skill as computing. Does
mika %% mika hold? Read off what mika stands over: mika. mika is among them, so it
holds.

## A case that breaks

R12. It is not the case that: Every pair of grixbras grixovis. It fails at x = mika, y =
fexnyr, left = mika, right = fexnyr. One case is enough, and this is the earliest one.

R13. It is not the case that: x @ x = x for every grixbra x. It fails at x = fexnyr,
value = mika. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of antisymmetry of the relation and closure
under the first operation. Those are properties of this system, not of systems in
general.

That is not a rhetorical caution. Take the same 5 objects, the same symbols, and a
different table, and T6 and T8 stop holding. The notation survives the substitution and
the mathematics does not.

## Neighbouring results

The material this chapter borrows from: A8 (antisymmetry of the relation), D11 (quilmi
pairs), D3 (umbgel collections) and D5 (the quilquil).

## Proofs

T6. No two distinct grixbras can both be wrenrelds.

  (1) [D8] Let f and h both be floors.
  (2) [D8] Then f %% h, since h is any object, and h %% f likewise.
  (3) [A8] Antisymmetry forces f = h.

Checked over 25 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T8. No two distinct grixbras lie in each other's yukvash.

  (1) [D11] Suppose x and y form a tight pair.
  (2) [A8] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

R12. It is not the case that: Every pair of grixbras grixovis.

  (1) [S2] Take the case x = mika, y = fexnyr, left = mika, right = fexnyr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

R13. It is not the case that: x @ x = x for every grixbra x.

  (1) [S2] Take the case x = fexnyr, value = mika, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T4. If x and y are both reldjen then so is x @ y.

  (1) [D6] Let x and y be reldjen.
  (2) [D1] The claim asks whether (x @ y) @ (x @ y) returns x @ y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 25 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

The results now available are T6, T8 and T4, each settled by exhaustive check rather
than by argument from analogy.

Do not carry forward R12 and R13. These were tested and failed, and the failing cases
are recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x046. This result is about the ovitez. List every grixbra in it.
Level 5.
  x047. The following fails in this system: Every pair of grixbras grixovis. Name the earliest grixbra, in the order the grixbras were introduced, that witnesses the failure.
  x048. The following fails in this system: x @ x = x for every grixbra x. Name the earliest grixbra, in the order the grixbras were introduced, that witnesses the failure.

# Chapter 9. Collections that close on themselves

## Why this chapter

The practical content of this chapter is the iskka of a grixbra, the kavor of a grixbra
is umbgel and the tarnvash. It is the part that shows up in use.

Prerequisites are real here: chapters 5 and 7 supply the notions the statements below
are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
grixbras that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D9. The iskka of a grixbra. The iskka of a grixbra x is the number of grixbras in its
kavor [x].

Worked out for each grixbra: mika to 1; fexnyr to 2; hobglim to 2; umbtarn to 2;
mornthra to 2.

D10. The tarnvash. The tarnvash of the system is the collection of grixbras whose iskka
is largest.

Running the definition over every grixbra leaves fexnyr, hobglim, umbtarn and mornthra.

## The shape of it

The right picture for kavor is a spreading stain rather than a list. Drop one grixbra
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
grixbras depending on where it started.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T1 rests on D7 (the kavor of a grixbra) and D3 (umbgel collections). The dependence is
on the content of those results, not only on their vocabulary.

R11 rests on D9 (the iskka of a grixbra) and T1 (the kavor of a grixbra is umbgel). The
dependence is on the content of those results, not only on their vocabulary.

R14 rests on D7 (the kavor of a grixbra) and D9 (the iskka of a grixbra). Remove any one
of them and the statement stops making sense, not merely stops being provable.

T2 rests on D7 (the kavor of a grixbra) and T1 (the kavor of a grixbra is umbgel).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

T3 rests on D1 (reldjen grixbras), D9 (the iskka of a grixbra) and T1 (the kavor of a
grixbra is umbgel). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Here is fexnyr @ mornthra ! mika, reduced without skipping anything.
    mornthra ! mika = mornthra   (the table for !)
    fexnyr @ mornthra = mika   (the table for @)
The expression comes to mika.

A companion case, mornthra @ (mika @ fexnyr), to show what the brackets are doing.
    mika @ fexnyr = mika   (the table for @)
    mornthra @ mika = mornthra   (the table for @)
The value is mornthra, not mika.

Test hobglim %% hobglim. The yukvash of hobglim is hobglim, and hobglim lies inside it,
so the relation holds.

A second case, this time a kavor. Start from fexnyr. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is mika and fexnyr, so
the iskka of fexnyr is 2.

## A case that breaks

R11. It is not the case that: For every grixbra x, the iskka of x divides 5. It fails at
x = fexnyr, reach = 2, size = 5. One case is enough, and this is the earliest one.

R14. It is not the case that: There is a grixbra whose kavor is the whole system. It
fails at largest_span = 2, size = 5. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by closure under the first operation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: D1 (reldjen grixbras), D3 (umbgel collections)
and D7 (the kavor of a grixbra).

## Proofs

T1. For every grixbra x, the collection [x] is umbgel.

  (1) [D7] [x] is built by taking x and closing under @.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 125 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

R11. It is not the case that: For every grixbra x, the iskka of x divides 5.

  (1) [S2] Take the case x = fexnyr, reach = 2, size = 5, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

R14. It is not the case that: There is a grixbra whose kavor is the whole system.

  (1) [S2] Take the case largest_span = 2, size = 5, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T2. If S is umbgel and contains x, then S contains all of [x].

  (1) [D7] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 45 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. x @ x = x holds if and only if [x] contains x alone.

  (1) [D1] If x @ x = x then {x} is already closed under @.
  (2) [T1] So [x] = {x} and the iskka is one.
  (3) [D9] Conversely a span of one object must contain x @ x, which is then x.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the iskka of a grixbra and the tarnvash. Each of these
is used by name later, so the names are worth learning rather than looking up.

Established here and safe to use: T1, T2 and T3.

Do not carry forward R11 and R14. These were tested and failed, and the failing cases
are recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x035. What is the iskka of fexnyr?
  x036. What is the iskka of hobglim?
  x037. How many grixbras lie in [umbtarn]?
  x038. How many grixbras lie in [mornthra]?
Level 4.
  x043. Which grixbras make up the tarnvash? Name them all.
  x044. What is the largest iskka any grixbra has?
Level 5.
  x039. Let z be fexnyr @ mornthra ! mornthra. What is the iskka of z?
  x040. Let z be umbtarn @ mika ! hobglim. What is the iskka of z?
  x041. Let z be fexnyr @ hobglim ! fexnyr. What is the iskka of z?
  x042. Let z be (fexnyr @ mika) @ hobglim. What is the iskka of z?
  x045. The following fails in this system: For every grixbra x, the iskka of x divides 5. Name the earliest grixbra, in the order the grixbras were introduced, that witnesses the failure.
