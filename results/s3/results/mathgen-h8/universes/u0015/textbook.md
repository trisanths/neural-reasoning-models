# The Duthtarn system

The Duthtarn system is small enough to hold in the hand and strange enough to be worth
the trouble. It has 3 tezkas, two operations, and one relation, and nothing else.

The tezkas are written lumwren, vorzel and opalfex. The first operation is written ><.
The second is written | and binds more tightly, so x >< y | z means x >< (y | z). The
relation is written <~; where it holds between two tezkas we say the left one covers the
right one. Both operations associate to the left when written without brackets, and
brackets override that. Repeated combination is abbreviated: x^3 means x >< x >< x. A
trailing mark reverses: x' is the tezka that combines with x to give the neutral one.

Readers arriving from arithmetic should put it down at the door. The operations below
are defined by their tables and by nothing else. Several arithmetic habits survive the
crossing and several do not, and the text is careful to say which is which.

# Chapter 1. The objects and their notation

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through the Duthtarn signature, the
Duthtarn combination tables and closure under the first operation.

One habit to adopt: when a statement below quantifies over tezkas, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## The tables in full

The table for ><. Read the left argument down the side and the right argument across the top.

         |  lumwren   vorzel  opalfex
-------------------------------------
 lumwren |  lumwren   vorzel  opalfex
  vorzel |   vorzel  opalfex  lumwren
 opalfex |  opalfex  lumwren   vorzel

The table for |. Read the left argument down the side and the right argument across the top.

         |  lumwren   vorzel  opalfex
-------------------------------------
 lumwren |  lumwren  lumwren  lumwren
  vorzel |  lumwren   vorzel  opalfex
 opalfex |  lumwren  opalfex   vorzel

Every pair standing in the <~ relation, grouped by left argument.

  lumwren <~ lumwren, vorzel and opalfex
  vorzel <~ lumwren, vorzel and opalfex
  opalfex <~ lumwren, vorzel and opalfex

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A1. Closure under the first operation. For all tezkas x and y, x >< y is again a tezka.

A2. Association of the first operation. For all tezkas x, y, z: (x >< y) >< z = x >< (y
>< z).

A3. Commutation of the first operation. For all tezkas x and y: x >< y = y >< x.

A6. Cancellation in the first operation. For all tezkas x, y, z: if x >< y = x >< z then
y = z.

## The shape of it

A useful mental split: some tezkas are inert under the operation and some are not.
lumwren come back unchanged when combined with themselves, and lumwren, vorzel and
opalfex commute with everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 3 tezkas the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R1 rests on S2 (the Duthtarn combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Here is opalfex >< opalfex | vorzel, reduced without skipping anything.
    opalfex | vorzel = opalfex   (the table for |)
    opalfex >< opalfex = vorzel   (the table for ><)
So opalfex >< opalfex | vorzel is vorzel.

Move the brackets and the work changes. Take opalfex >< (vorzel >< opalfex).
    vorzel >< opalfex = lumwren   (the table for ><)
    opalfex >< lumwren = opalfex   (the table for ><)
The value is opalfex, not vorzel.

One decision about the relation, since deciding is as much a skill as computing. Does
vorzel <~ opalfex hold? Read off what vorzel stands over: lumwren, vorzel and opalfex.
opalfex is among them, so it holds.

## A case that breaks

R1. It is not the case that: For every tezka x: x >< x = x. It fails at x = vorzel,
value = opalfex. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

What is built on it later: A4 (a neutral object for the first operation), A5 (reversal
under the first operation), A7 (closure under the second operation) and A8 (association
of the second operation).

## Proofs

R1. It is not the case that: For every tezka x: x >< x = x.

  (1) [S2] Take the case x = vorzel, value = opalfex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 27 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R1. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 1.
  x001. What tezka does vorzel >< opalfex name?
  x002. Evaluate opalfex >< opalfex.
  x003. Reduce opalfex >< vorzel to a single tezka.
Level 2.
  x004. Reduce vorzel >< vorzel | opalfex to a single tezka.
  x007. Evaluate opalfex^3.
  x008. Evaluate vorzel^2.
  x009. Solve x >< vorzel = vorzel for x, naming every solution.
  x010. Which tezkas x satisfy x >< vorzel = lumwren? List them all.
Level 3.
  x005. Evaluate (lumwren >< opalfex) >< (lumwren >< opalfex).
  x006. Reduce (vorzel >< vorzel) >< (lumwren >< lumwren) to a single tezka.

# Chapter 2. Neutral objects and reversal

## Why this chapter

The present chapter develops a neutral object for the first operation, reversal under
the first operation and the system does not have an absorbing object for the first
operation.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over tezkas, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A4. A neutral object for the first operation. There is a tezka lumwren with lumwren >< x
= x >< lumwren = x for every x.

A5. Reversal under the first operation. For every tezka x there is a tezka y with x >< y
= y >< x = lumwren.

## The shape of it

Neutrality is a strong condition disguised as a weak one. It fixes a single tezka and,
through that, constrains everything that can combine with it.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R2 rests on S2 (the Duthtarn combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Take (opalfex >< vorzel) >< (opalfex >< lumwren) and work it out one step at a time.
    opalfex >< vorzel = lumwren   (the table for ><)
    opalfex >< lumwren = opalfex   (the table for ><)
    lumwren >< opalfex = opalfex   (the table for ><)
That leaves opalfex, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is vorzel >< (opalfex >< opalfex) for contrast.
    opalfex >< opalfex = vorzel   (the table for ><)
    vorzel >< vorzel = opalfex   (the table for ><)
The value is opalfex. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
lumwren <~ vorzel hold? Read off what lumwren stands over: lumwren, vorzel and opalfex.
vorzel is among them, so it holds.

## A case that breaks

R2. There is no tezka z with z >< x = x >< z = z for every tezka x. The case that
settles it: reason = no absorbing element. Anyone carrying this claim over from a more
familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside S2 (the Duthtarn combination tables).

These results are used again in D5 (the yukvex), D11 (the tezzam of a tezka) and T1 (the
yukvex is the only one of its kind).

## Proofs

R2. There is no tezka z with z >< x = x >< z = z for every tezka x.

  (1) [S2] Take the case reason = no absorbing element, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 27 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R2. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

No exercises here. Every question this chapter suggested turned out to be answerable
from the question itself, so all of them were discarded.

# Chapter 3. The relation and what it orders

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is reflexivity of the
relation, transitivity of the relation and comparability of every pair.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about tezkas covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A12. Reflexivity of the relation. For every tezka x: x <~ x.

A13. Transitivity of the relation. For all tezkas x, y, z: if x <~ y and y <~ z then x
<~ z.

A14. Comparability of every pair. For all tezkas x and y, at least one of x <~ y and y
<~ x holds.

A15. Agreement of the relation with the first operation. For all tezkas x, y, z: if x <~
y then (z >< x) <~ (z >< y) and (x >< z) <~ (y >< z).

A16. Agreement of the relation with the second operation. For all tezkas x, y, z: if x
<~ y then (z | x) <~ (z | y) and (x | z) <~ (y | z).

D4. The tarnopal of a tezka. The tarnopal of a tezka x is the collection of tezkas y for
which x <~ y holds.

Worked out for each tezka: lumwren to lumwren, vorzel and opalfex; vorzel to lumwren,
vorzel and opalfex; opalfex to lumwren, vorzel and opalfex.

## The shape of it

Think of <~ as pointing downhill. The tarnopal of a tezka is everything downhill of it,
and those shadows here have sizes 3.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R5 rests on S2 (the Duthtarn combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Take lumwren >< lumwren | vorzel and work it out one step at a time.
    lumwren | vorzel = lumwren   (the table for |)
    lumwren >< lumwren = lumwren   (the table for ><)
That leaves lumwren, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take lumwren >< (vorzel >< lumwren).
    vorzel >< lumwren = vorzel   (the table for ><)
    lumwren >< vorzel = vorzel   (the table for ><)
That gives vorzel, against lumwren above.

Test opalfex <~ lumwren. The tarnopal of opalfex is lumwren, vorzel and opalfex, and
lumwren lies inside it, so the relation holds.

## A case that breaks

R5. It is not the case that: For all tezkas x and y: if x <~ y and y <~ x then x = y. It
fails at x = lumwren, y = vorzel. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside S2 (the Duthtarn combination tables).

What is built on it later: D9 (a hurnhob), D14 (thrahob pairs), T13 (tarnopals are
nested along the relation) and T14 (the system has a hurnhob).

## Proofs

R5. It is not the case that: For all tezkas x and y: if x <~ y and y <~ x then x = y.

  (1) [S2] Take the case x = lumwren, y = vorzel, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 27 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the tarnopal of a tezka. Each of these is used by name
later, so the names are worth learning rather than looking up.

Explicitly not available: R5. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

No exercises here. Every question this chapter suggested turned out to be answerable
from the question itself, so all of them were discarded.

# Chapter 4. The second operation and how the two interact

## Why this chapter

What follows was pieced together backwards. The last item of it, a neutral object for
the second operation, spreading of the second operation over the first and closure under
the second operation, was noticed before anyone had a reason to expect it.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over tezkas, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A10. A neutral object for the second operation. There is a tezka vorzel with vorzel | x
= x for every x.

A11. Spreading of the second operation over the first. For all tezkas x, y, z: x | (y ><
z) = (x | y) >< (x | z), and the same on the right.

A7. Closure under the second operation. For all tezkas x and y, x | y is again a tezka.

A8. Association of the second operation. For all tezkas x, y, z: (x | y) | z = x | (y |
z).

A9. Commutation of the second operation. For all tezkas x and y: x | y = y | x.

## The shape of it

With two operations the question stops being what each does and becomes how they
interfere. | binds tighter, so the interference shows up whenever a bracket is left off.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R3 rests on S2 (the Duthtarn combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R4 rests on S2 (the Duthtarn combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take (opalfex >< lumwren) >< (vorzel >< opalfex) and work it out one step at a time.
    opalfex >< lumwren = opalfex   (the table for ><)
    vorzel >< opalfex = lumwren   (the table for ><)
    opalfex >< lumwren = opalfex   (the table for ><)
So (opalfex >< lumwren) >< (vorzel >< opalfex) is opalfex.

Bracketing is not cosmetic, so here is lumwren >< (vorzel >< opalfex) for contrast.
    vorzel >< opalfex = lumwren   (the table for ><)
    lumwren >< lumwren = lumwren   (the table for ><)
The value is lumwren, not opalfex.

Test lumwren <~ opalfex. The tarnopal of lumwren is lumwren, vorzel and opalfex, and
opalfex lies inside it, so the relation holds.

## A case that breaks

R3. It is not the case that: For every tezka x: x | x = x. It fails at x = opalfex,
value = vorzel. One case is enough, and this is the earliest one.

R4. It is not the case that: For all tezkas x and y: x >< (x | y) = x and x | (x >< y) =
x. The case that settles it: x = vorzel, y = vorzel, value = opalfex. Anyone carrying
this claim over from a more familiar system will be wrong here, and wrong in a way that
propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: S2 (the Duthtarn combination tables).

These results are used again in T19 (the second operation keeps the drilorn intact).

## Proofs

R3. It is not the case that: For every tezka x: x | x = x.

  (1) [S2] Take the case x = opalfex, value = vorzel, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 27 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R4. It is not the case that: For all tezkas x and y: x >< (x | y) = x and x | (x >< y) = x.

  (1) [S2] Take the case x = vorzel, y = vorzel, value = opalfex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 27 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R3 and R4. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 5.
  x011. The following fails in this system: For every tezka x: x | x = x. Name the earliest tezka, in the order the tezkas were introduced, that witnesses the failure.

# Chapter 5. Combining objects

## Why this chapter

Anyone using this system to keep track of something will meet xilvash tezkas, tezkas
that espanak and the yukvex early, whether or not they go looking.

Prerequisites are real here: chapters 1 and 2 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over tezkas, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D1. Xilvash tezkas. A tezka x is called xilvash when x >< x = x.

Running the definition over every tezka leaves lumwren.

D2. Tezkas that espanak. Two tezkas x and y are said to espanak when x >< y = y >< x.

D5. The yukvex. The tezka lumwren is called the yukvex of the system. It is the unique
tezka that leaves every tezka unchanged under ><.

Here that is lumwren.

## The shape of it

A useful mental split: some tezkas are inert under the operation and some are not.
lumwren come back unchanged when combined with themselves, and lumwren, vorzel and
opalfex commute with everything.

The neutral tezka lumwren is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Nothing is derived in this chapter. It lays down material that later chapters draw on.

## A worked case

Take opalfex >< lumwren | opalfex and work it out one step at a time.
    lumwren | opalfex = lumwren   (the table for |)
    opalfex >< lumwren = opalfex   (the table for ><)
So opalfex >< lumwren | opalfex is opalfex.

Bracketing is not cosmetic, so here is lumwren >< (opalfex >< opalfex) for contrast.
    opalfex >< opalfex = vorzel   (the table for ><)
    lumwren >< vorzel = vorzel   (the table for ><)
That gives vorzel, against opalfex above.

One decision about the relation, since deciding is as much a skill as computing. Does
vorzel <~ lumwren hold? Read off what vorzel stands over: lumwren, vorzel and opalfex.
lumwren is among them, so it holds.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of tezkas that come back
unchanged from themselves: lumwren. Assuming more of them than that is the mistake to
avoid.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of a neutral object for the first operation
and closure under the first operation. Those are properties of this system, not of
systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A1 (closure under the first operation) and A4 (a neutral object for the
first operation).

What is built on it later: D6 (the drilorn), D7 (the lorngrix), D10 (hobthra tezkas) and
D11 (the tezzam of a tezka).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

Carry forward xilvash tezkas, tezkas that espanak and the yukvex. Later chapters state
their results in these terms and do not restate the definitions.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 2.
  x015. Name the yukvex of the system.
Level 3.
  x012. Write down the xilvash in full.

# Chapter 6. The relation and what it orders (2)

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through thrahob pairs, qenduth
collections and a hurnhob.

Prerequisites are real here: chapters 1 and 3 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over tezkas, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D14. Thrahob pairs. Two distinct tezkas x and y form a thrahob pair when x <~ y and y <~
x both hold, that is, when each lies in the tarnopal of the other.

In this system that picks out lumwren, vorzel and opalfex, that is, all of them.

D3. Qenduth collections. A collection S of tezkas is qenduth when x >< y belongs to S
for every pair x, y drawn from S.

D9. A hurnhob. A tezka f is a hurnhob when f <~ y holds for every tezka y, that is, when
the tarnopal of f is the whole system.

Running the definition over every tezka leaves lumwren, vorzel and opalfex.

## The shape of it

Picture the nyrpon as what happens when you start with one tezka and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 3 tezkas, that stops. In this system the sizes it stops at are 1 and 3.

Think of <~ as pointing downhill. The tarnopal of a tezka is everything downhill of it,
and those shadows here have sizes 3.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T13 rests on D4 (the tarnopal of a tezka) and A13 (transitivity of the relation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

T15 rests on D4 (the tarnopal of a tezka) and A15 (agreement of the relation with the
first operation). Remove any one of them and the statement stops making sense, not
merely stops being provable.

T18 rests on D4 (the tarnopal of a tezka). Remove any one of them and the statement
stops making sense, not merely stops being provable.

## A worked case

Take (vorzel >< vorzel) >< (vorzel >< lumwren) and work it out one step at a time.
    vorzel >< vorzel = opalfex   (the table for ><)
    vorzel >< lumwren = vorzel   (the table for ><)
    opalfex >< vorzel = lumwren   (the table for ><)
The expression comes to lumwren.

Bracketing is not cosmetic, so here is vorzel >< (vorzel >< vorzel) for contrast.
    vorzel >< vorzel = opalfex   (the table for ><)
    vorzel >< opalfex = lumwren   (the table for ><)
The value is lumwren. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
lumwren <~ lumwren hold? Read off what lumwren stands over: lumwren, vorzel and opalfex.
lumwren is among them, so it holds.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by agreement of the relation with the first operation, closure under
the first operation and transitivity of the relation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A1 (closure under the first operation), A13 (transitivity of the
relation), A15 (agreement of the relation with the first operation) and D4 (the tarnopal
of a tezka).

These results are used again in D8 (the nyrpon of a tezka), T5 (the drilorn is qenduth),
T6 (the nyrpon of a tezka is qenduth) and T11 (the lorngrix is qenduth).

## Proofs

T13. If y lies in the tarnopal of x, then the tarnopal of y is contained in the tarnopal of x.

  (1) [D4] Let y satisfy x <~ y and let z satisfy y <~ z.
  (2) [A13] Transitivity gives x <~ z.
  (3) [D4] So every member of the tarnopal of y is a member of that of x.

Checked over 27 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T15. If x <~ y then (x >< z) <~ (y >< z) for every tezka z.

  (1) [D4] Let y lie in the tarnopal of x.
  (2) [A15] Compatibility applies the operation to both sides at once.
  (3) Nothing else is needed, since z was arbitrary.

Checked over 27 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T18. If x <~ y then y <~ x.

  (1) [D4] Symmetry would mean y lies in the tarnopal of x exactly when x lies in that of y.
  (2) The listed pairs settle it directly.

Checked over 9 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: thrahob pairs, qenduth collections and a hurnhob. Each
of these is used by name later, so the names are worth learning rather than looking up.

The results now available are T13, T15 and T18, each settled by exhaustive check rather
than by argument from analogy.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x013. How many tezkas lie in the smallest qenduth collection containing vorzel?
  x014. How many tezkas lie in the smallest qenduth collection containing opalfex?

# Chapter 7. Combining objects (2)

## Why this chapter

We turn to the drilorn, the lorngrix and combining on the left never merges two tezkas.
The treatment is self contained given the material already established.

Nothing here stands on its own. The arguments lean on chapters 1 and 5, and a reader who
has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 3
tezkas that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D6. The drilorn. The drilorn of the system is the collection of tezkas that espanak with
every tezka.

Running the definition over every tezka leaves lumwren, vorzel and opalfex.

D7. The lorngrix. The lorngrix is the collection of all xilvash tezkas.

In this system that picks out lumwren, which is 1 of the 3 tezkas.

## The shape of it

A useful mental split: some tezkas are inert under the operation and some are not.
lumwren come back unchanged when combined with themselves, and lumwren, vorzel and
opalfex commute with everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 3 tezkas the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T12 rests on A6 (cancellation in the first operation) and D2 (tezkas that espanak). The
dependence is on the content of those results, not only on their vocabulary.

## A worked case

Evaluate vorzel >< vorzel | vorzel. Each line below is one lookup in a table.
    vorzel | vorzel = vorzel   (the table for |)
    vorzel >< vorzel = opalfex   (the table for ><)
The expression comes to opalfex.

A companion case, vorzel >< (vorzel >< vorzel), to show what the brackets are doing.
    vorzel >< vorzel = opalfex   (the table for ><)
    vorzel >< opalfex = lumwren   (the table for ><)
The value is lumwren, not opalfex.

Test vorzel <~ vorzel. The tarnopal of vorzel is lumwren, vorzel and opalfex, and vorzel
lies inside it, so the relation holds.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of tezkas that come back
unchanged from themselves: lumwren. Assuming more of them than that is the mistake to
avoid.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by cancellation in the first operation and closure under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

That is not a rhetorical caution. Take the same 3 objects, the same symbols, and a
different table, and T12 stop holding. The notation survives the substitution and the
mathematics does not.

## Neighbouring results

Read alongside A6 (cancellation in the first operation), D1 (xilvash tezkas) and D2
(tezkas that espanak).

What is built on it later: T2 (the yukvex lies in the drilorn), T5 (the drilorn is
qenduth), T10 (the nyrpon of a drilorn tezka stays in the drilorn) and T11 (the lorngrix
is qenduth).

## Proofs

T12. For every tezka a, the assignment x to a >< x sends distinct tezkas to distinct tezkas.

  (1) [A6] Suppose a >< x = a >< y.
  (2) [A6] Cancellation on the left gives x = y.
  (3) So the assignment is injective, and being injective on a finite carrier it is onto.

Checked over 9 cases: every object translated by every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the drilorn and the lorngrix. Later chapters state their results in these
terms and do not restate the definitions.

The results now available are T12, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x016. List every tezka in the lorngrix.

# Chapter 8. Neutral objects and reversal (2)

## Why this chapter

Work through this chapter with the tables in front of you. It covers hobthra tezkas, the
tezzam of a tezka and where the yukvex swallows everything breaks down, and each claim
can be checked by hand.

Nothing here stands on its own. The arguments lean on chapters 2 and 5, and a reader who
has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about tezkas covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D10. Hobthra tezkas. A tezka x is hobthra when x >< x equals the yukvex.

Running the definition over every tezka leaves lumwren.

D11. The tezzam of a tezka. A tezzam of a tezka x is a tezka y with x >< y = y >< x =
lumwren.

Worked out for each tezka: lumwren to lumwren; vorzel to opalfex; opalfex to vorzel.

## The shape of it

Neutrality is a strong condition disguised as a weak one. It fixes a single tezka and,
through that, constrains everything that can combine with it.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R7 rests on D5 (the yukvex). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T1 rests on D5 (the yukvex) and A4 (a neutral object for the first operation). The
dependence is on the content of those results, not only on their vocabulary.

## A worked case

Here is (lumwren >< vorzel) >< (lumwren >< opalfex), reduced without skipping anything.
    lumwren >< vorzel = vorzel   (the table for ><)
    lumwren >< opalfex = opalfex   (the table for ><)
    vorzel >< opalfex = lumwren   (the table for ><)
The expression comes to lumwren.

Move the brackets and the work changes. Take vorzel >< (lumwren >< lumwren).
    lumwren >< lumwren = lumwren   (the table for ><)
    vorzel >< lumwren = vorzel   (the table for ><)
The value is vorzel, not lumwren.

One decision about the relation, since deciding is as much a skill as computing. Does
lumwren <~ vorzel hold? Read off what lumwren stands over: lumwren, vorzel and opalfex.
vorzel is among them, so it holds.

## A case that breaks

R7. It is not the case that: e >< x equals the yukvex for every tezka x. It fails at
anchor = lumwren, x = vorzel, value = vorzel. One case is enough, and this is the
earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by a neutral object for the first operation, closure under the first
operation and reversal under the first operation. A system without them is not a system
where these results are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A4 (a neutral object for the first operation),
A5 (reversal under the first operation), D1 (xilvash tezkas) and D5 (the yukvex).

These results are used again in T3 (a tezka has only one tezzam) and T4 (a hobthra tezka
is its own tezzam).

## Proofs

R7. It is not the case that: e >< x equals the yukvex for every tezka x.

  (1) [S2] Take the case anchor = lumwren, x = vorzel, value = vorzel, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 3 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T1. There is exactly one tezka e with e >< x = x >< e = x for every tezka x.

  (1) [D5] Suppose e and f both leave every tezka unchanged.
  (2) [A4] Then e >< f = f, reading e as neutral on the left.
  (3) [A4] And e >< f = e, reading f as neutral on the right.
  (4) So e = f, and the two suppositions describe the same object.

Checked over 9 cases: every object paired with every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward hobthra tezkas and the tezzam of a tezka. Later chapters state their
results in these terms and do not restate the definitions.

Established here and safe to use: T1.

Explicitly not available: R7. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x022. Write down the hobthra in full.
  x023. Which tezka reverses vorzel under ><?
  x024. Name the tezzam of opalfex.
Level 5.
  x025. Let z be opalfex >< vorzel. Name the tezzam of z.
  x038. The following fails in this system: e >< x equals the yukvex for every tezka x. Name the earliest tezka, in the order the tezkas were introduced, that witnesses the failure.

# Chapter 9. Combining objects (3)

## Why this chapter

The results collected here were not found in this order. The nyrpon of a tezka, the
system has a hurnhob and where every tezka is xilvash breaks down came first, and the
rest was assembled around that once the pattern was visible.

Prerequisites are real here: chapters 1, 3, 5, 6 and 7 supply the notions the statements
below are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 3
tezkas that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D8. The nyrpon of a tezka. The nyrpon of a tezka x, written [x], is the smallest qenduth
collection that contains x.

Worked out for each tezka: lumwren to lumwren; vorzel to lumwren, vorzel and opalfex;
opalfex to lumwren, vorzel and opalfex.

## The shape of it

The right picture for nyrpon is a spreading stain rather than a list. Drop one tezka in,
apply the operation to whatever is wet, repeat. The stain here reaches 1 and 3 tezkas
depending on where it started.

Think of <~ as pointing downhill. The tarnopal of a tezka is everything downhill of it,
and those shadows here have sizes 3.

Two questions sort the tezkas quickly. Does combining a tezka with itself change it? For
lumwren it does not. Does it matter which side it goes on? For lumwren, vorzel and
opalfex it does not.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 3 tezkas the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T14 rests on D9 (a hurnhob) and A14 (comparability of every pair). Remove any one of
them and the statement stops making sense, not merely stops being provable.

R6 rests on D7 (the lorngrix). The dependence is on the content of those results, not
only on their vocabulary.

T11 rests on D7 (the lorngrix) and D3 (qenduth collections). The dependence is on the
content of those results, not only on their vocabulary.

T16 rests on D6 (the drilorn). The dependence is on the content of those results, not
only on their vocabulary.

T2 rests on D5 (the yukvex) and D6 (the drilorn). The dependence is on the content of
those results, not only on their vocabulary.

T5 rests on D6 (the drilorn), D3 (qenduth collections) and A2 (association of the first
operation). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Evaluate lumwren >< lumwren | lumwren. Each line below is one lookup in a table.
    lumwren | lumwren = lumwren   (the table for |)
    lumwren >< lumwren = lumwren   (the table for ><)
So lumwren >< lumwren | lumwren is lumwren.

Bracketing is not cosmetic, so here is lumwren >< (lumwren >< lumwren) for contrast.
    lumwren >< lumwren = lumwren   (the table for ><)
    lumwren >< lumwren = lumwren   (the table for ><)
That gives lumwren, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
opalfex <~ opalfex hold? Read off what opalfex stands over: lumwren, vorzel and opalfex.
opalfex is among them, so it holds.

A second case, this time a nyrpon. Start from lumwren. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is lumwren, so the
pyryuk of lumwren is 1.

## A case that breaks

R6. It is not the case that: x >< x = x for every tezka x. The case that settles it: x =
vorzel, value = opalfex. Anyone carrying this claim over from a more familiar system
will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by a neutral object for the first operation, association of the
first operation, closure under the first operation and comparability of every pair. A
system without them is not a system where these results are harder to prove; it is a
system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A14 (comparability of every pair), A2
(association of the first operation), D3 (qenduth collections) and D5 (the yukvex).

What is built on it later: D12 (the pyryuk of a tezka), T6 (the nyrpon of a tezka is
qenduth), T7 (the nyrpon is contained in every qenduth collection) and T10 (the nyrpon
of a drilorn tezka stays in the drilorn).

## Proofs

T14. Some tezka hurnhobs the whole system.

  (1) [A14] Every pair is comparable, so the relation orders the objects into a line.
  (2) [D9] The claim is that the line has a bottom.
  (3) The carrier is finite, so the search over candidates terminates.

Checked over 9 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

R6. It is not the case that: x >< x = x for every tezka x.

  (1) [S2] Take the case x = vorzel, value = opalfex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 3 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T11. If x and y are both xilvash then so is x >< y.

  (1) [D7] Let x and y be xilvash.
  (2) [D1] The claim asks whether (x >< y) >< (x >< y) returns x >< y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 9 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

T16. Every pair of tezkas espanaks.

  (1) [D6] The drilorn is defined by espanaking with everything.
  (2) [D2] The claim is that x >< y = y >< x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 9 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T2. The yukvex espanaks with every tezka.

  (1) [D5] Let e be the yukvex and x any tezka.
  (2) [D5] Then e >< x = x and x >< e = x.
  (3) [D2] So e >< x = x >< e, which is what it means to espanak.
  (4) [D6] Since x was arbitrary, e belongs to the drilorn.

Checked over 3 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T5. If x and y both espanak with every tezka, then so does x >< y.

  (1) [D6] Let x and y lie in the drilorn and let z be any tezka.
  (2) [A2] Then (x >< y) >< z = x >< (y >< z).
  (3) [D6] Move z past y, then past x, using that each espanaks with everything.
  (4) [D3] So x >< y espanaks with z, and the drilorn is qenduth.

Checked over 9 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the nyrpon of a tezka. Later chapters state their results in these terms
and do not restate the definitions.

Established here and safe to use: T14, T11, T16, T2 and T5.

Do not carry forward R6. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x017. List the nyrpon of vorzel.
  x018. Name every tezka in [opalfex].
Level 4.
  x019. Let z be vorzel >< opalfex. List the nyrpon of z.
  x020. Let z be vorzel >< lumwren. List the nyrpon of z.
  x021. Let z be opalfex >< vorzel. List the nyrpon of z.
  x036. This result is about the lorngrix. List every tezka in it.

# Chapter 10. Collections that close on themselves

## Why this chapter

Anyone using this system to keep track of something will meet the pyryuk of a tezka, a
tezka has only one tezzam and the nyrpon of a tezka is qenduth early, whether or not
they go looking.

Prerequisites are real here: chapters 1, 6, 8 and 9 supply the notions the statements
below are phrased in.

One habit to adopt: when a statement below quantifies over tezkas, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D12. The pyryuk of a tezka. The pyryuk of a tezka x is the number of tezkas in its
nyrpon [x].

Worked out for each tezka: lumwren to 1; vorzel to 3; opalfex to 3.

## The shape of it

The right picture for nyrpon is a spreading stain rather than a list. Drop one tezka in,
apply the operation to whatever is wet, repeat. The stain here reaches 1 and 3 tezkas
depending on where it started.

Neutrality is a strong condition disguised as a weak one. It fixes a single tezka and,
through that, constrains everything that can combine with it.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T3 rests on D11 (the tezzam of a tezka), A2 (association of the first operation) and T1
(the yukvex is the only one of its kind). The dependence is on the content of those
results, not only on their vocabulary.

T6 rests on D8 (the nyrpon of a tezka) and D3 (qenduth collections). The dependence is
on the content of those results, not only on their vocabulary.

## A worked case

Evaluate (vorzel >< vorzel) >< (vorzel >< vorzel). Each line below is one lookup in a
table.
    vorzel >< vorzel = opalfex   (the table for ><)
    vorzel >< vorzel = opalfex   (the table for ><)
    opalfex >< opalfex = vorzel   (the table for ><)
That leaves vorzel, and no other reading of the notation gives anything else.

A companion case, vorzel >< (vorzel >< vorzel), to show what the brackets are doing.
    vorzel >< vorzel = opalfex   (the table for ><)
    vorzel >< opalfex = lumwren   (the table for ><)
The value is lumwren, not vorzel.

One decision about the relation, since deciding is as much a skill as computing. Does
lumwren <~ vorzel hold? Read off what lumwren stands over: lumwren, vorzel and opalfex.
vorzel is among them, so it holds.

A second case, this time a nyrpon. Start from lumwren. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is lumwren, so the
pyryuk of lumwren is 1.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of tezkas that come back
unchanged from themselves: lumwren. Assuming more of them than that is the mistake to
avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by a neutral object for the first operation, association of the
first operation, closure under the first operation and reversal under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A2 (association of the first operation), D11
(the tezzam of a tezka), D3 (qenduth collections) and D8 (the nyrpon of a tezka).

What is built on it later: D13 (the duthquil), T4 (a hobthra tezka is its own tezzam),
T7 (the nyrpon is contained in every qenduth collection) and T8 (a tezka is xilvash
exactly when its pyryuk is one).

## Proofs

T3. For every tezka x there is exactly one tezzam of x.

  (1) [D11] Let y and z both be partners of x.
  (2) [A2] Then y = y >< (x >< z) = (y >< x) >< z.
  (3) [D11] Both bracketed products collapse to the neutral object.
  (4) So y = z.

Checked over 9 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T6. For every tezka x, the collection [x] is qenduth.

  (1) [D8] [x] is built by taking x and closing under ><.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 27 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the pyryuk of a tezka. Each of these is used by name
later, so the names are worth learning rather than looking up.

The results now available are T3 and T6, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x026. How many tezkas lie in [vorzel]?
  x027. How many tezkas lie in [opalfex]?
Level 5.
  x028. Let z be (lumwren >< vorzel) >< lumwren. What is the pyryuk of z?
  x029. Let z be vorzel >< lumwren | opalfex. What is the pyryuk of z?
  x030. Let z be opalfex >< vorzel | opalfex. What is the pyryuk of z?
  x031. Let z be opalfex >< vorzel | vorzel. What is the pyryuk of z?
  x032. Let z be (vorzel >< vorzel) >< lumwren. What is the pyryuk of z?
  x033. Let z be vorzel >< vorzel | lumwren. What is the pyryuk of z?

# Chapter 11. Collections that close on themselves (2)

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through the duthquil, the nyrpon of a
drilorn tezka stays in the drilorn and some tezka reaches every other.

Nothing here stands on its own. The arguments lean on chapters 5, 7, 8, 9 and 10, and a
reader who has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 3
tezkas that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D13. The duthquil. The duthquil of the system is the collection of tezkas whose pyryuk
is largest.

Running the definition over every tezka leaves vorzel and opalfex.

## The shape of it

The right picture for nyrpon is a spreading stain rather than a list. Drop one tezka in,
apply the operation to whatever is wet, repeat. The stain here reaches 1 and 3 tezkas
depending on where it started.

A useful mental split: some tezkas are inert under the operation and some are not.
lumwren come back unchanged when combined with themselves, and lumwren, vorzel and
opalfex commute with everything.

Neutrality is a strong condition disguised as a weak one. It fixes a single tezka and,
through that, constrains everything that can combine with it.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 3 tezkas the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T10 rests on D8 (the nyrpon of a tezka), D6 (the drilorn) and T5 (the drilorn is
qenduth). The dependence is on the content of those results, not only on their
vocabulary.

T17 rests on D8 (the nyrpon of a tezka) and D12 (the pyryuk of a tezka). Remove any one
of them and the statement stops making sense, not merely stops being provable.

T4 rests on D10 (hobthra tezkas), D11 (the tezzam of a tezka) and T3 (a tezka has only
one tezzam). The dependence is on the content of those results, not only on their
vocabulary.

T7 rests on D8 (the nyrpon of a tezka) and T6 (the nyrpon of a tezka is qenduth). The
dependence is on the content of those results, not only on their vocabulary.

T8 rests on D1 (xilvash tezkas), D12 (the pyryuk of a tezka) and T6 (the nyrpon of a
tezka is qenduth). Remove any one of them and the statement stops making sense, not
merely stops being provable.

T9 rests on D12 (the pyryuk of a tezka) and T6 (the nyrpon of a tezka is qenduth).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

## A worked case

Here is lumwren >< vorzel | opalfex, reduced without skipping anything.
    vorzel | opalfex = opalfex   (the table for |)
    lumwren >< opalfex = opalfex   (the table for ><)
The expression comes to opalfex.

Bracketing is not cosmetic, so here is vorzel >< (opalfex >< lumwren) for contrast.
    opalfex >< lumwren = opalfex   (the table for ><)
    vorzel >< opalfex = lumwren   (the table for ><)
The value is lumwren, not opalfex.

Test vorzel <~ lumwren. The tarnopal of vorzel is lumwren, vorzel and opalfex, and
lumwren lies inside it, so the relation holds.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of tezkas that come back
unchanged from themselves: lumwren. Assuming more of them than that is the mistake to
avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation, closure under the first operation and reversal under
the first operation. Those are properties of this system, not of systems in general.

That is not a rhetorical caution. Take the same 3 objects, the same symbols, and a
different table, and T17 and T9 stop holding. The notation survives the substitution and
the mathematics does not.

## Neighbouring results

The material this chapter borrows from: D1 (xilvash tezkas), D10 (hobthra tezkas), D11
(the tezzam of a tezka) and D12 (the pyryuk of a tezka).

## Proofs

T10. If x lies in the drilorn then every tezka of [x] lies in the drilorn.

  (1) [T5] The drilorn is qenduth.
  (2) [D8] [x] is the smallest qenduth collection containing x.
  (3) A smallest such collection sits inside any other, and the drilorn is one.

Checked over 9 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

T17. There is a tezka whose nyrpon is the whole system.

  (1) [D8] Compute [x] for each tezka in turn.
  (2) [D12] The claim is that some pyryuk equals 3.
  (3) The search runs over finitely many objects, so it settles.

Checked over 3 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T4. If x >< x is the yukvex then the tezzam of x is x itself.

  (1) [D10] Let x be hobthra, so x >< x is the yukvex.
  (2) [D11] That is exactly the condition for x to be a partner of x.
  (3) [T3] Partners are unique, so no other object can be one.

Checked over 3 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T7. If S is qenduth and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 6 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T8. x >< x = x holds if and only if [x] contains x alone.

  (1) [D1] If x >< x = x then {x} is already closed under ><.
  (2) [T6] So [x] = {x} and the pyryuk is one.
  (3) [D12] Conversely a span of one object must contain x >< x, which is then x.

Checked over 3 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T9. For every tezka x, the pyryuk of x divides 3.

  (1) [T6] [x] is a qenduth collection.
  (2) [D12] Its size is the pyryuk of x.
  (3) The claim is that this size always divides 3.

Checked over 3 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the duthquil. Each of these is used by name later, so
the names are worth learning rather than looking up.

The results now available are T10, T17, T4, T7, T8 and T9, each settled by exhaustive
check rather than by argument from analogy.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x034. Which tezkas make up the duthquil? Name them all.
  x035. What is the largest pyryuk any tezka has?
  x037. Which tezka, taken earliest in the listed order, has pyryuk equal to 3?

# Chapter 12. The second operation and how the two interact (2)

## Why this chapter

We turn to the second operation keeps the drilorn intact. The treatment is self
contained given the material already established.

Nothing here stands on its own. The arguments lean on chapters 4, 7 and 9, and a reader
who has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over tezkas, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

The interesting content of a two operation system sits in the gap between them: which
one distributes over which, and which tezkas are fixed by both.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 3 tezkas the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T19 rests on D6 (the drilorn), A7 (closure under the second operation) and T5 (the
drilorn is qenduth). Remove any one of them and the statement stops making sense, not
merely stops being provable.

## A worked case

Evaluate (lumwren >< opalfex) >< (opalfex >< lumwren). Each line below is one lookup in
a table.
    lumwren >< opalfex = opalfex   (the table for ><)
    opalfex >< lumwren = opalfex   (the table for ><)
    opalfex >< opalfex = vorzel   (the table for ><)
The expression comes to vorzel.

Bracketing is not cosmetic, so here is opalfex >< (opalfex >< lumwren) for contrast.
    opalfex >< lumwren = opalfex   (the table for ><)
    opalfex >< opalfex = vorzel   (the table for ><)
That gives vorzel, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
lumwren <~ opalfex hold? Read off what lumwren stands over: lumwren, vorzel and opalfex.
opalfex is among them, so it holds.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of association of the first operation,
closure under the first operation and closure under the second operation. Those are
properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A7 (closure under the second operation), D6 (the
drilorn) and T5 (the drilorn is qenduth).

## Proofs

T19. If x and y lie in the drilorn then so does x | y.

  (1) [T5] The drilorn is already qenduth under ><.
  (2) [A7] The second operation is defined on every pair.
  (3) [D6] The claim is that | respects the drilorn as well.

Checked over 9 cases: every ordered pair from the core. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

The results now available are T19, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

This chapter carries no exercises. Nothing in it can be asked about in a way that could
not be answered without reading it, and an exercise like that is worse than none.
