# The Vashdri system

This book is about ovimorns. A ovimorn is not a number and not a set; it is one of
exactly 5 objects, and everything said here is said about how those 5 objects combine.

The ovimorns are written rastmi, bradri, wrenkorr, tezkeld and muxvor. The first
operation is written :. The relation is written ::; where it holds between two ovimorns
we say the left one governs the right one. Both operations associate to the left when
written without brackets, and brackets override that. Repeated combination is
abbreviated: x^3 means x : x : x. A trailing mark reverses: x' is the ovimorn that
combines with x to give the neutral one.

Readers arriving from arithmetic should put it down at the door. The operations below
are defined by their tables and by nothing else. Several arithmetic habits survive the
crossing and several do not, and the text is careful to say which is which.

# Chapter 1. The objects and their notation

## Why this chapter

The results collected here were not found in this order. The Vashdri signature, the
Vashdri combination tables and closure under the first operation came first, and the
rest was assembled around that once the pattern was visible.

The standard of proof here is exhaustion. A universal claim about ovimorns covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## The tables in full

The table for :. Read the left argument down the side and the right argument across the top.

          |    rastmi    bradri  wrenkorr   tezkeld    muxvor
-------------------------------------------------------------
   rastmi |    rastmi    bradri  wrenkorr   tezkeld    muxvor
   bradri |    bradri  wrenkorr   tezkeld    muxvor    rastmi
 wrenkorr |  wrenkorr   tezkeld    muxvor    rastmi    bradri
  tezkeld |   tezkeld    muxvor    rastmi    bradri  wrenkorr
   muxvor |    muxvor    rastmi    bradri  wrenkorr   tezkeld

Every pair standing in the :: relation, grouped by left argument.

  rastmi :: rastmi, bradri, wrenkorr, tezkeld and muxvor
  bradri :: rastmi, bradri, wrenkorr, tezkeld and muxvor
  wrenkorr :: rastmi, bradri, wrenkorr, tezkeld and muxvor
  tezkeld :: rastmi, bradri, wrenkorr, tezkeld and muxvor
  muxvor :: rastmi, bradri, wrenkorr, tezkeld and muxvor

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A1. Closure under the first operation. For all ovimorns x and y, x : y is again a
ovimorn.

A2. Association of the first operation. For all ovimorns x, y, z: (x : y) : z = x : (y :
z).

A3. Commutation of the first operation. For all ovimorns x and y: x : y = y : x.

A6. Cancellation in the first operation. For all ovimorns x, y, z: if x : y = x : z then
y = z.

## The shape of it

A useful mental split: some ovimorns are inert under the operation and some are not.
rastmi come back unchanged when combined with themselves, and rastmi, bradri, wrenkorr,
tezkeld and muxvor commute with everything.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R1 rests on S2 (the Vashdri combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Take (wrenkorr : rastmi) : bradri and work it out one step at a time.
    wrenkorr : rastmi = wrenkorr   (the table for :)
    wrenkorr : bradri = tezkeld   (the table for :)
The expression comes to tezkeld.

Move the brackets and the work changes. Take rastmi : (bradri : wrenkorr).
    bradri : wrenkorr = tezkeld   (the table for :)
    rastmi : tezkeld = tezkeld   (the table for :)
The value is tezkeld. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test muxvor :: bradri. The vexvint of muxvor is rastmi, bradri, wrenkorr, tezkeld and
muxvor, and bradri lies inside it, so the relation holds.

## A case that breaks

R1. It is not the case that: For every ovimorn x: x : x = x. It fails at x = bradri,
value = wrenkorr. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

These results are used again in A4 (a neutral object for the first operation), A5
(reversal under the first operation), A7 (reflexivity of the relation) and A8
(transitivity of the relation).

## Proofs

R1. It is not the case that: For every ovimorn x: x : x = x.

  (1) [S2] Take the case x = bradri, value = wrenkorr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R1. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 1.
  x001. Reduce muxvor : wrenkorr to a single ovimorn.
  x002. Reduce muxvor : muxvor to a single ovimorn.
  x003. Reduce muxvor : tezkeld to a single ovimorn.
  x004. Work out the value of bradri : muxvor.
Level 2.
  x005. Reduce (bradri : wrenkorr) : bradri to a single ovimorn.
  x006. Evaluate (tezkeld : tezkeld) : tezkeld.
  x007. Reduce (wrenkorr : rastmi) : bradri to a single ovimorn.
  x008. Work out the value of (rastmi : muxvor) : wrenkorr.
  x010. Evaluate muxvor^3.
  x011. Evaluate rastmi : muxvor'.
  x012. Solve x : tezkeld = tezkeld for x, naming every solution.
  x013. Which ovimorns x satisfy x : wrenkorr = rastmi? List them all.
Level 3.
  x009. What ovimorn does (muxvor : bradri) : (tezkeld : muxvor) name?

# Chapter 2. Neutral objects and reversal

## Why this chapter

Anyone using this system to keep track of something will meet a neutral object for the
first operation, reversal under the first operation and the system does not have an
absorbing object for the first operation early, whether or not they go looking.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
ovimorns that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A4. A neutral object for the first operation. There is a ovimorn rastmi with rastmi : x
= x : rastmi = x for every x.

A5. Reversal under the first operation. For every ovimorn x there is a ovimorn y with x
: y = y : x = rastmi.

## The shape of it

The neutral ovimorn rastmi is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R2 rests on S2 (the Vashdri combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Evaluate (wrenkorr : bradri) : (muxvor : rastmi). Each line below is one lookup in a
table.
    wrenkorr : bradri = tezkeld   (the table for :)
    muxvor : rastmi = muxvor   (the table for :)
    tezkeld : muxvor = wrenkorr   (the table for :)
So (wrenkorr : bradri) : (muxvor : rastmi) is wrenkorr.

Move the brackets and the work changes. Take bradri : (muxvor : wrenkorr).
    muxvor : wrenkorr = bradri   (the table for :)
    bradri : bradri = wrenkorr   (the table for :)
That gives wrenkorr, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
tezkeld :: bradri hold? Read off what tezkeld stands over: rastmi, bradri, wrenkorr,
tezkeld and muxvor. bradri is among them, so it holds.

## A case that breaks

R2. There is no ovimorn z with z : x = x : z = z for every ovimorn x. The case that
settles it: reason = no absorbing element. Anyone carrying this claim over from a more
familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: S2 (the Vashdri combination tables).

These results are used again in D5 (the wrenglim), D11 (the oviovi of a ovimorn) and T1
(the wrenglim is the only one of its kind).

## Proofs

R2. There is no ovimorn z with z : x = x : z = z for every ovimorn x.

  (1) [S2] Take the case reason = no absorbing element, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R2. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

This chapter carries no exercises. Nothing in it can be asked about in a way that could
not be answered without reading it, and an exercise like that is worse than none.

# Chapter 3. The relation and what it orders

## Why this chapter

So far the ovimorns have been objects to be pushed around. This chapter starts asking
what they are like. We take up agreement of the relation with the first operation,
reflexivity of the relation and transitivity of the relation.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about ovimorns covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A10. Agreement of the relation with the first operation. For all ovimorns x, y, z: if x
:: y then (z : x) :: (z : y) and (x : z) :: (y : z).

A7. Reflexivity of the relation. For every ovimorn x: x :: x.

A8. Transitivity of the relation. For all ovimorns x, y, z: if x :: y and y :: z then x
:: z.

A9. Comparability of every pair. For all ovimorns x and y, at least one of x :: y and y
:: x holds.

D4. The vexvint of a ovimorn. The vexvint of a ovimorn x is the collection of ovimorns y
for which x :: y holds.

Worked out for each ovimorn: rastmi to rastmi, bradri, wrenkorr, tezkeld and muxvor;
bradri to rastmi, bradri, wrenkorr, tezkeld and muxvor; wrenkorr to rastmi, bradri,
wrenkorr, tezkeld and muxvor; tezkeld to rastmi, bradri, wrenkorr, tezkeld and muxvor;
muxvor to rastmi, bradri, wrenkorr, tezkeld and muxvor.

## The shape of it

The relation is easiest to see as a height. Each ovimorn casts a vexvint over what it
governs, and the sizes of those shadows here are 5. Sizes repeat, so the objects do not
line up in single file.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R3 rests on S2 (the Vashdri combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take (tezkeld : rastmi) : muxvor and work it out one step at a time.
    tezkeld : rastmi = tezkeld   (the table for :)
    tezkeld : muxvor = wrenkorr   (the table for :)
The expression comes to wrenkorr.

Bracketing is not cosmetic, so here is rastmi : (muxvor : tezkeld) for contrast.
    muxvor : tezkeld = wrenkorr   (the table for :)
    rastmi : wrenkorr = wrenkorr   (the table for :)
The value is wrenkorr. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
muxvor :: wrenkorr hold? Read off what muxvor stands over: rastmi, bradri, wrenkorr,
tezkeld and muxvor. wrenkorr is among them, so it holds.

## A case that breaks

R3. It is not the case that: For all ovimorns x and y: if x :: y and y :: x then x = y.
The case that settles it: x = rastmi, y = bradri. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: S2 (the Vashdri combination tables).

What is built on it later: D9 (a wrenvor), D14 (duthlum pairs), T13 (vexvints are nested
along the relation) and T14 (the system has a wrenvor).

## Proofs

R3. It is not the case that: For all ovimorns x and y: if x :: y and y :: x then x = y.

  (1) [S2] Take the case x = rastmi, y = bradri, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the vexvint of a ovimorn. Later chapters state their results in these
terms and do not restate the definitions.

Do not carry forward R3. These were tested and failed, and the failing cases are
recorded above.

## Exercises

This chapter carries no exercises. Nothing in it can be asked about in a way that could
not be answered without reading it, and an exercise like that is worse than none.

# Chapter 4. Combining objects

## Why this chapter

The present chapter develops tarnkorr ovimorns, ovimorns that naklorn and the wrenglim.

Prerequisites are real here: chapters 1 and 2 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over ovimorns, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D1. Tarnkorr ovimorns. A ovimorn x is called tarnkorr when x : x = x.

In this system that picks out rastmi, which is 1 of the 5 ovimorns.

D2. Ovimorns that naklorn. Two ovimorns x and y are said to naklorn when x : y = y : x.

D5. The wrenglim. The ovimorn rastmi is called the wrenglim of the system. It is the
unique ovimorn that leaves every ovimorn unchanged under :.

Here that is rastmi.

## The shape of it

Two questions sort the ovimorns quickly. Does combining a ovimorn with itself change it?
For rastmi it does not. Does it matter which side it goes on? For rastmi, bradri,
wrenkorr, tezkeld and muxvor it does not.

Neutrality is a strong condition disguised as a weak one. It fixes a single ovimorn and,
through that, constrains everything that can combine with it.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Nothing is derived in this chapter. It lays down material that later chapters draw on.

## A worked case

Take (muxvor : tezkeld) : (wrenkorr : bradri) and work it out one step at a time.
    muxvor : tezkeld = wrenkorr   (the table for :)
    wrenkorr : bradri = tezkeld   (the table for :)
    wrenkorr : tezkeld = rastmi   (the table for :)
That leaves rastmi, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take tezkeld : (wrenkorr : muxvor).
    wrenkorr : muxvor = bradri   (the table for :)
    tezkeld : bradri = muxvor   (the table for :)
That gives muxvor, against rastmi above.

One decision about the relation, since deciding is as much a skill as computing. Does
wrenkorr :: bradri hold? Read off what wrenkorr stands over: rastmi, bradri, wrenkorr,
tezkeld and muxvor. bradri is among them, so it holds.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of a neutral object for the first operation
and closure under the first operation. Those are properties of this system, not of
systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A1 (closure under the first operation) and A4 (a
neutral object for the first operation).

What is built on it later: D6 (the glimdri), D7 (the nakjen), D10 (opaltez ovimorns) and
D11 (the oviovi of a ovimorn).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

New vocabulary from this chapter: tarnkorr ovimorns, ovimorns that naklorn and the
wrenglim. Each of these is used by name later, so the names are worth learning rather
than looking up.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 2.
  x017. Name the wrenglim of the system.
Level 3.
  x014. Write down the tarnkorr in full.

# Chapter 5. The relation and what it orders (2)

## Why this chapter

Work through this chapter with the tables in front of you. It covers duthlum pairs,
vexjen collections and a wrenvor, and each claim can be checked by hand.

Prerequisites are real here: chapters 1 and 3 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over ovimorns, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D14. Duthlum pairs. Two distinct ovimorns x and y form a duthlum pair when x :: y and y
:: x both hold, that is, when each lies in the vexvint of the other.

In this system that picks out rastmi, bradri, wrenkorr, tezkeld and muxvor, that is, all
of them.

D3. Vexjen collections. A collection S of ovimorns is vexjen when x : y belongs to S for
every pair x, y drawn from S.

D9. A wrenvor. A ovimorn f is a wrenvor when f :: y holds for every ovimorn y, that is,
when the vexvint of f is the whole system.

Running the definition over every ovimorn leaves rastmi, bradri, wrenkorr, tezkeld and
muxvor.

## The shape of it

The right picture for wrenmi is a spreading stain rather than a list. Drop one ovimorn
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 5
ovimorns depending on where it started.

Think of :: as pointing downhill. The vexvint of a ovimorn is everything downhill of it,
and those shadows here have sizes 5.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 ovimorns the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T13 rests on D4 (the vexvint of a ovimorn) and A8 (transitivity of the relation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

T15 rests on D4 (the vexvint of a ovimorn) and A10 (agreement of the relation with the
first operation). Remove any one of them and the statement stops making sense, not
merely stops being provable.

T18 rests on D4 (the vexvint of a ovimorn). Remove any one of them and the statement
stops making sense, not merely stops being provable.

## A worked case

Here is (rastmi : bradri) : wrenkorr, reduced without skipping anything.
    rastmi : bradri = bradri   (the table for :)
    bradri : wrenkorr = tezkeld   (the table for :)
The expression comes to tezkeld.

A companion case, bradri : (wrenkorr : rastmi), to show what the brackets are doing.
    wrenkorr : rastmi = wrenkorr   (the table for :)
    bradri : wrenkorr = tezkeld   (the table for :)
The value is tezkeld. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test muxvor :: tezkeld. The vexvint of muxvor is rastmi, bradri, wrenkorr, tezkeld and
muxvor, and tezkeld lies inside it, so the relation holds.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of agreement of the relation with the first
operation, closure under the first operation and transitivity of the relation. Those are
properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A1 (closure under the first operation), A10
(agreement of the relation with the first operation), A8 (transitivity of the relation)
and D4 (the vexvint of a ovimorn).

These results are used again in D8 (the wrenmi of a ovimorn), T5 (the glimdri is
vexjen), T6 (the wrenmi of a ovimorn is vexjen) and T11 (the nakjen is vexjen).

## Proofs

T13. If y lies in the vexvint of x, then the vexvint of y is contained in the vexvint of x.

  (1) [D4] Let y satisfy x :: y and let z satisfy y :: z.
  (2) [A8] Transitivity gives x :: z.
  (3) [D4] So every member of the vexvint of y is a member of that of x.

Checked over 125 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T15. If x :: y then (x : z) :: (y : z) for every ovimorn z.

  (1) [D4] Let y lie in the vexvint of x.
  (2) [A10] Compatibility applies the operation to both sides at once.
  (3) Nothing else is needed, since z was arbitrary.

Checked over 125 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T18. If x :: y then y :: x.

  (1) [D4] Symmetry would mean y lies in the vexvint of x exactly when x lies in that of y.
  (2) The listed pairs settle it directly.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward duthlum pairs, vexjen collections and a wrenvor. Later chapters state
their results in these terms and do not restate the definitions.

Established here and safe to use: T13, T15 and T18.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x015. How many ovimorns lie in the smallest vexjen collection containing bradri?
  x016. How many ovimorns lie in the smallest vexjen collection containing wrenkorr?

# Chapter 6. Combining objects (2)

## Why this chapter

What follows was pieced together backwards. The last item of it, the glimdri, the nakjen
and combining on the left never merges two ovimorns, was noticed before anyone had a
reason to expect it.

Prerequisites are real here: chapters 1 and 4 supply the notions the statements below
are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
ovimorns that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D6. The glimdri. The glimdri of the system is the collection of ovimorns that naklorn
with every ovimorn.

In this system that picks out rastmi, bradri, wrenkorr, tezkeld and muxvor, that is, all
of them.

D7. The nakjen. The nakjen is the collection of all tarnkorr ovimorns.

Running the definition over every ovimorn leaves rastmi.

## The shape of it

Two questions sort the ovimorns quickly. Does combining a ovimorn with itself change it?
For rastmi it does not. Does it matter which side it goes on? For rastmi, bradri,
wrenkorr, tezkeld and muxvor it does not.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 ovimorns the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T12 rests on A6 (cancellation in the first operation) and D2 (ovimorns that naklorn).
The dependence is on the content of those results, not only on their vocabulary.

## A worked case

Here is (bradri : muxvor) : (rastmi : wrenkorr), reduced without skipping anything.
    bradri : muxvor = rastmi   (the table for :)
    rastmi : wrenkorr = wrenkorr   (the table for :)
    rastmi : wrenkorr = wrenkorr   (the table for :)
So (bradri : muxvor) : (rastmi : wrenkorr) is wrenkorr.

Move the brackets and the work changes. Take muxvor : (rastmi : bradri).
    rastmi : bradri = bradri   (the table for :)
    muxvor : bradri = rastmi   (the table for :)
That gives rastmi, against wrenkorr above.

One decision about the relation, since deciding is as much a skill as computing. Does
rastmi :: rastmi hold? Read off what rastmi stands over: rastmi, bradri, wrenkorr,
tezkeld and muxvor. rastmi is among them, so it holds.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of ovimorns that come back
unchanged from themselves: rastmi. Assuming more of them than that is the mistake to
avoid.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by cancellation in the first operation and closure under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

That is not a rhetorical caution. Take the same 5 objects, the same symbols, and a
different table, and T12 stop holding. The notation survives the substitution and the
mathematics does not.

## Neighbouring results

Read alongside A6 (cancellation in the first operation), D1 (tarnkorr ovimorns) and D2
(ovimorns that naklorn).

What is built on it later: T2 (the wrenglim lies in the glimdri), T5 (the glimdri is
vexjen), T10 (the wrenmi of a glimdri ovimorn stays in the glimdri) and T11 (the nakjen
is vexjen).

## Proofs

T12. For every ovimorn a, the assignment x to a : x sends distinct ovimorns to distinct ovimorns.

  (1) [A6] Suppose a : x = a : y.
  (2) [A6] Cancellation on the left gives x = y.
  (3) So the assignment is injective, and being injective on a finite carrier it is onto.

Checked over 25 cases: every object translated by every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the glimdri and the nakjen. Each of these is used by
name later, so the names are worth learning rather than looking up.

The results now available are T12, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x018. List every ovimorn in the nakjen.

# Chapter 7. Neutral objects and reversal (2)

## Why this chapter

The practical content of this chapter is opaltez ovimorns, the oviovi of a ovimorn and
where the wrenglim swallows everything breaks down. It is the part that shows up in use.

Prerequisites are real here: chapters 2 and 4 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over ovimorns, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D10. Opaltez ovimorns. A ovimorn x is opaltez when x : x equals the wrenglim.

Running the definition over every ovimorn leaves rastmi.

D11. The oviovi of a ovimorn. A oviovi of a ovimorn x is a ovimorn y with x : y = y : x
= rastmi.

Worked out for each ovimorn: rastmi to rastmi; bradri to muxvor; wrenkorr to tezkeld;
tezkeld to wrenkorr; muxvor to bradri.

## The shape of it

Neutrality is a strong condition disguised as a weak one. It fixes a single ovimorn and,
through that, constrains everything that can combine with it.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R5 rests on D5 (the wrenglim). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T1 rests on D5 (the wrenglim) and A4 (a neutral object for the first operation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Take (tezkeld : rastmi) : wrenkorr and work it out one step at a time.
    tezkeld : rastmi = tezkeld   (the table for :)
    tezkeld : wrenkorr = rastmi   (the table for :)
So (tezkeld : rastmi) : wrenkorr is rastmi.

Move the brackets and the work changes. Take rastmi : (wrenkorr : tezkeld).
    wrenkorr : tezkeld = rastmi   (the table for :)
    rastmi : rastmi = rastmi   (the table for :)
That gives rastmi, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
bradri :: wrenkorr hold? Read off what bradri stands over: rastmi, bradri, wrenkorr,
tezkeld and muxvor. wrenkorr is among them, so it holds.

## A case that breaks

R5. It is not the case that: e : x equals the wrenglim for every ovimorn x. It fails at
anchor = rastmi, x = bradri, value = bradri. One case is enough, and this is the
earliest one.

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
first operation), D1 (tarnkorr ovimorns) and D5 (the wrenglim).

What is built on it later: T3 (a ovimorn has only one oviovi) and T4 (a opaltez ovimorn
is its own oviovi).

## Proofs

R5. It is not the case that: e : x equals the wrenglim for every ovimorn x.

  (1) [S2] Take the case anchor = rastmi, x = bradri, value = bradri, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T1. There is exactly one ovimorn e with e : x = x : e = x for every ovimorn x.

  (1) [D5] Suppose e and f both leave every ovimorn unchanged.
  (2) [A4] Then e : f = f, reading e as neutral on the left.
  (3) [A4] And e : f = e, reading f as neutral on the right.
  (4) So e = f, and the two suppositions describe the same object.

Checked over 25 cases: every object paired with every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward opaltez ovimorns and the oviovi of a ovimorn. Later chapters state their
results in these terms and do not restate the definitions.

The results now available are T1, each settled by exhaustive check rather than by
argument from analogy.

Do not carry forward R5. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x026. Write down the opaltez in full.
  x027. Which ovimorn reverses bradri under :?
  x028. Which ovimorn reverses wrenkorr under :?
  x029. Which ovimorn reverses tezkeld under :?
  x030. Which ovimorn reverses muxvor under :?
Level 5.
  x031. Let z be bradri : rastmi. Name the oviovi of z.
  x032. Let z be muxvor : muxvor. Name the oviovi of z.
  x045. The following fails in this system: e : x equals the wrenglim for every ovimorn x. Name the earliest ovimorn, in the order the ovimorns were introduced, that witnesses the failure.

# Chapter 8. Combining objects (3)

## Why this chapter

So far the ovimorns have been objects to be pushed around. This chapter starts asking
what they are like. We take up the wrenmi of a ovimorn, the system has a wrenvor and
where every ovimorn is tarnkorr breaks down.

Prerequisites are real here: chapters 1, 3, 4, 5 and 6 supply the notions the statements
below are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
ovimorns that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D8. The wrenmi of a ovimorn. The wrenmi of a ovimorn x, written [x], is the smallest
vexjen collection that contains x.

Worked out for each ovimorn: rastmi to rastmi; bradri to rastmi, bradri, wrenkorr,
tezkeld and muxvor; wrenkorr to rastmi, bradri, wrenkorr, tezkeld and muxvor; tezkeld to
rastmi, bradri, wrenkorr, tezkeld and muxvor; muxvor to rastmi, bradri, wrenkorr,
tezkeld and muxvor.

## The shape of it

The right picture for wrenmi is a spreading stain rather than a list. Drop one ovimorn
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 5
ovimorns depending on where it started.

The relation is easiest to see as a height. Each ovimorn casts a vexvint over what it
governs, and the sizes of those shadows here are 5. Sizes repeat, so the objects do not
line up in single file.

A useful mental split: some ovimorns are inert under the operation and some are not.
rastmi come back unchanged when combined with themselves, and rastmi, bradri, wrenkorr,
tezkeld and muxvor commute with everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 ovimorns the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T14 rests on D9 (a wrenvor) and A9 (comparability of every pair). Remove any one of them
and the statement stops making sense, not merely stops being provable.

R4 rests on D7 (the nakjen). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T11 rests on D7 (the nakjen) and D3 (vexjen collections). The dependence is on the
content of those results, not only on their vocabulary.

T16 rests on D6 (the glimdri). The dependence is on the content of those results, not
only on their vocabulary.

T2 rests on D5 (the wrenglim) and D6 (the glimdri). The dependence is on the content of
those results, not only on their vocabulary.

T5 rests on D6 (the glimdri), D3 (vexjen collections) and A2 (association of the first
operation). Remove any one of them and the statement stops making sense, not merely
stops being provable.

## A worked case

Here is (muxvor : bradri) : (wrenkorr : tezkeld), reduced without skipping anything.
    muxvor : bradri = rastmi   (the table for :)
    wrenkorr : tezkeld = rastmi   (the table for :)
    rastmi : rastmi = rastmi   (the table for :)
The expression comes to rastmi.

Move the brackets and the work changes. Take bradri : (wrenkorr : muxvor).
    wrenkorr : muxvor = bradri   (the table for :)
    bradri : bradri = wrenkorr   (the table for :)
The value is wrenkorr, not rastmi.

Test rastmi :: rastmi. The vexvint of rastmi is rastmi, bradri, wrenkorr, tezkeld and
muxvor, and rastmi lies inside it, so the relation holds.

A second case, this time a wrenmi. Start from wrenkorr. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is rastmi, bradri,
wrenkorr, tezkeld and muxvor, so the korropal of wrenkorr is 5.

## A case that breaks

R4. It is not the case that: x : x = x for every ovimorn x. It fails at x = bradri,
value = wrenkorr. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by a neutral object for the first operation, association of the
first operation, closure under the first operation and comparability of every pair. A
system without them is not a system where these results are harder to prove; it is a
system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A2 (association of the first operation), A9 (comparability of every
pair), D3 (vexjen collections) and D5 (the wrenglim).

These results are used again in D12 (the korropal of a ovimorn), T6 (the wrenmi of a
ovimorn is vexjen), T7 (the wrenmi is contained in every vexjen collection) and T10 (the
wrenmi of a glimdri ovimorn stays in the glimdri).

## Proofs

T14. Some ovimorn wrenvors the whole system.

  (1) [A9] Every pair is comparable, so the relation orders the objects into a line.
  (2) [D9] The claim is that the line has a bottom.
  (3) The carrier is finite, so the search over candidates terminates.

Checked over 25 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

R4. It is not the case that: x : x = x for every ovimorn x.

  (1) [S2] Take the case x = bradri, value = wrenkorr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T11. If x and y are both tarnkorr then so is x : y.

  (1) [D7] Let x and y be tarnkorr.
  (2) [D1] The claim asks whether (x : y) : (x : y) returns x : y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 25 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

T16. Every pair of ovimorns naklorns.

  (1) [D6] The glimdri is defined by naklorning with everything.
  (2) [D2] The claim is that x : y = y : x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T2. The wrenglim naklorns with every ovimorn.

  (1) [D5] Let e be the wrenglim and x any ovimorn.
  (2) [D5] Then e : x = x and x : e = x.
  (3) [D2] So e : x = x : e, which is what it means to naklorn.
  (4) [D6] Since x was arbitrary, e belongs to the glimdri.

Checked over 5 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T5. If x and y both naklorn with every ovimorn, then so does x : y.

  (1) [D6] Let x and y lie in the glimdri and let z be any ovimorn.
  (2) [A2] Then (x : y) : z = x : (y : z).
  (3) [D6] Move z past y, then past x, using that each naklorns with everything.
  (4) [D3] So x : y naklorns with z, and the glimdri is vexjen.

Checked over 25 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the wrenmi of a ovimorn. Each of these is used by name
later, so the names are worth learning rather than looking up.

Established here and safe to use: T14, T11, T16, T2 and T5.

Do not carry forward R4. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x019. List the wrenmi of bradri.
  x020. List the wrenmi of wrenkorr.
  x021. Name every ovimorn in [tezkeld].
  x022. Name every ovimorn in [muxvor].
Level 4.
  x023. Let z be rastmi : wrenkorr. List the wrenmi of z.
  x024. Let z be wrenkorr : wrenkorr. List the wrenmi of z.
  x025. Let z be bradri : bradri. List the wrenmi of z.
  x043. This result is about the nakjen. List every ovimorn in it.

# Chapter 9. Collections that close on themselves

## Why this chapter

We turn to the korropal of a ovimorn, a ovimorn has only one oviovi and the wrenmi of a
ovimorn is vexjen. The treatment is self contained given the material already
established.

Nothing here stands on its own. The arguments lean on chapters 1, 5, 7 and 8, and a
reader who has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
ovimorns that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D12. The korropal of a ovimorn. The korropal of a ovimorn x is the number of ovimorns in
its wrenmi [x].

Worked out for each ovimorn: rastmi to 1; bradri to 5; wrenkorr to 5; tezkeld to 5;
muxvor to 5.

## The shape of it

Picture the wrenmi as what happens when you start with one ovimorn and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 5 ovimorns, that stops. In this system the sizes it stops at are 1 and 5.

The neutral ovimorn rastmi is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 ovimorns the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T3 rests on D11 (the oviovi of a ovimorn), A2 (association of the first operation) and
T1 (the wrenglim is the only one of its kind). Remove any one of them and the statement
stops making sense, not merely stops being provable.

T6 rests on D8 (the wrenmi of a ovimorn) and D3 (vexjen collections). The dependence is
on the content of those results, not only on their vocabulary.

## A worked case

Evaluate (wrenkorr : tezkeld) : bradri. Each line below is one lookup in a table.
    wrenkorr : tezkeld = rastmi   (the table for :)
    rastmi : bradri = bradri   (the table for :)
So (wrenkorr : tezkeld) : bradri is bradri.

A companion case, tezkeld : (bradri : wrenkorr), to show what the brackets are doing.
    bradri : wrenkorr = tezkeld   (the table for :)
    tezkeld : tezkeld = bradri   (the table for :)
That gives bradri, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
wrenkorr :: rastmi hold? Read off what wrenkorr stands over: rastmi, bradri, wrenkorr,
tezkeld and muxvor. rastmi is among them, so it holds.

A second case, this time a wrenmi. Start from rastmi. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is rastmi, so the
korropal of rastmi is 1.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of ovimorns that come back
unchanged from themselves: rastmi. Assuming more of them than that is the mistake to
avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation, closure under the first operation and reversal under
the first operation. Those are properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A2 (association of the first operation), D11 (the oviovi of a ovimorn),
D3 (vexjen collections) and D8 (the wrenmi of a ovimorn).

What is built on it later: D13 (the kajen), T4 (a opaltez ovimorn is its own oviovi), T7
(the wrenmi is contained in every vexjen collection) and T8 (a ovimorn is tarnkorr
exactly when its korropal is one).

## Proofs

T3. For every ovimorn x there is exactly one oviovi of x.

  (1) [D11] Let y and z both be partners of x.
  (2) [A2] Then y = y : (x : z) = (y : x) : z.
  (3) [D11] Both bracketed products collapse to the neutral object.
  (4) So y = z.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T6. For every ovimorn x, the collection [x] is vexjen.

  (1) [D8] [x] is built by taking x and closing under :.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 125 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the korropal of a ovimorn. Later chapters state their results in these
terms and do not restate the definitions.

Established here and safe to use: T3 and T6.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x033. How many ovimorns lie in [bradri]?
  x034. What is the korropal of wrenkorr?
  x035. What is the korropal of tezkeld?
  x036. What is the korropal of muxvor?
Level 5.
  x037. Let z be (tezkeld : muxvor) : rastmi. What is the korropal of z?
  x038. Let z be (tezkeld : muxvor) : bradri. What is the korropal of z?
  x039. Let z be (tezkeld : wrenkorr) : bradri. What is the korropal of z?
  x040. Let z be (tezkeld : muxvor) : wrenkorr. What is the korropal of z?

# Chapter 10. Collections that close on themselves (2)

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is the kajen, the
wrenmi of a glimdri ovimorn stays in the glimdri and some ovimorn reaches every other.

Prerequisites are real here: chapters 4, 6, 7, 8 and 9 supply the notions the statements
below are phrased in.

One habit to adopt: when a statement below quantifies over ovimorns, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D13. The kajen. The kajen of the system is the collection of ovimorns whose korropal is
largest.

In this system that picks out bradri, wrenkorr, tezkeld and muxvor, which is 4 of the 5
ovimorns.

## The shape of it

The right picture for wrenmi is a spreading stain rather than a list. Drop one ovimorn
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 5
ovimorns depending on where it started.

A useful mental split: some ovimorns are inert under the operation and some are not.
rastmi come back unchanged when combined with themselves, and rastmi, bradri, wrenkorr,
tezkeld and muxvor commute with everything.

The neutral ovimorn rastmi is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T10 rests on D8 (the wrenmi of a ovimorn), D6 (the glimdri) and T5 (the glimdri is
vexjen). The dependence is on the content of those results, not only on their
vocabulary.

T17 rests on D8 (the wrenmi of a ovimorn) and D12 (the korropal of a ovimorn). The
dependence is on the content of those results, not only on their vocabulary.

T4 rests on D10 (opaltez ovimorns), D11 (the oviovi of a ovimorn) and T3 (a ovimorn has
only one oviovi). Remove any one of them and the statement stops making sense, not
merely stops being provable.

T7 rests on D8 (the wrenmi of a ovimorn) and T6 (the wrenmi of a ovimorn is vexjen).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

T8 rests on D1 (tarnkorr ovimorns), D12 (the korropal of a ovimorn) and T6 (the wrenmi
of a ovimorn is vexjen). Remove any one of them and the statement stops making sense,
not merely stops being provable.

T9 rests on D12 (the korropal of a ovimorn) and T6 (the wrenmi of a ovimorn is vexjen).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

## A worked case

Take (tezkeld : wrenkorr) : (rastmi : muxvor) and work it out one step at a time.
    tezkeld : wrenkorr = rastmi   (the table for :)
    rastmi : muxvor = muxvor   (the table for :)
    rastmi : muxvor = muxvor   (the table for :)
The expression comes to muxvor.

A companion case, wrenkorr : (rastmi : tezkeld), to show what the brackets are doing.
    rastmi : tezkeld = tezkeld   (the table for :)
    wrenkorr : tezkeld = rastmi   (the table for :)
That gives rastmi, against muxvor above.

One decision about the relation, since deciding is as much a skill as computing. Does
wrenkorr :: muxvor hold? Read off what wrenkorr stands over: rastmi, bradri, wrenkorr,
tezkeld and muxvor. muxvor is among them, so it holds.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by a neutral object for the first operation, association of the
first operation, closure under the first operation and reversal under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

That is not a rhetorical caution. Take the same 5 objects, the same symbols, and a
different table, and T17 and T9 stop holding. The notation survives the substitution and
the mathematics does not.

## Neighbouring results

The material this chapter borrows from: D1 (tarnkorr ovimorns), D10 (opaltez ovimorns),
D11 (the oviovi of a ovimorn) and D12 (the korropal of a ovimorn).

## Proofs

T10. If x lies in the glimdri then every ovimorn of [x] lies in the glimdri.

  (1) [T5] The glimdri is vexjen.
  (2) [D8] [x] is the smallest vexjen collection containing x.
  (3) A smallest such collection sits inside any other, and the glimdri is one.

Checked over 25 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

T17. There is a ovimorn whose wrenmi is the whole system.

  (1) [D8] Compute [x] for each ovimorn in turn.
  (2) [D12] The claim is that some korropal equals 5.
  (3) The search runs over finitely many objects, so it settles.

Checked over 5 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T4. If x : x is the wrenglim then the oviovi of x is x itself.

  (1) [D10] Let x be opaltez, so x : x is the wrenglim.
  (2) [D11] That is exactly the condition for x to be a partner of x.
  (3) [T3] Partners are unique, so no other object can be one.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T7. If S is vexjen and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 10 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T8. x : x = x holds if and only if [x] contains x alone.

  (1) [D1] If x : x = x then {x} is already closed under :.
  (2) [T6] So [x] = {x} and the korropal is one.
  (3) [D12] Conversely a span of one object must contain x : x, which is then x.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T9. For every ovimorn x, the korropal of x divides 5.

  (1) [T6] [x] is a vexjen collection.
  (2) [D12] Its size is the korropal of x.
  (3) The claim is that this size always divides 5.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the kajen. Later chapters state their results in these terms and do not
restate the definitions.

The results now available are T10, T17, T4, T7, T8 and T9, each settled by exhaustive
check rather than by argument from analogy.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x041. Write down the kajen in full.
  x042. What is the largest korropal any ovimorn has?
  x044. Name a ovimorn whose wrenmi is the whole system. Give the earliest such ovimorn in the order the ovimorns were introduced.
