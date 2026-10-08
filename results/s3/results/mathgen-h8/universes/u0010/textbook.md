# The Hurnglim system

The Hurnglim system is small enough to hold in the hand and strange enough to be worth
the trouble. It has 3 grixmis, one operation, and one relation, and nothing else.

The grixmis are written tezreld, vexyuk and muxlum. The first operation is written #.
The relation is written |>; where it holds between two grixmis we say the left one
refines the right one. Both operations associate to the left when written without
brackets, and brackets override that. Repeated combination is abbreviated: x^3 means x #
x # x.

A warning that will be repeated because it is the one readers ignore: nothing here is
inherited from arithmetic. Familiar names have been avoided on purpose. Where a law of
arithmetic happens to hold it is stated and checked, and where it fails a counterexample
is given.

# Chapter 1. The objects and their notation

## Why this chapter

So far the grixmis have been objects to be pushed around. This chapter starts asking
what they are like. We take up the Hurnglim signature, the Hurnglim combination tables
and closure under the first operation.

The standard of proof here is exhaustion. A universal claim about grixmis covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## The tables in full

The table for #. Read the left argument down the side and the right argument across the top.

         |  tezreld   vexyuk   muxlum
-------------------------------------
 tezreld |  tezreld  tezreld  tezreld
  vexyuk |  tezreld   vexyuk   muxlum
  muxlum |  tezreld   muxlum   vexyuk

Every pair standing in the |> relation, grouped by left argument.

  tezreld |> tezreld
  vexyuk |> tezreld, vexyuk and muxlum
  muxlum |> tezreld, vexyuk and muxlum

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A1. Closure under the first operation. For all grixmis x and y, x # y is again a grixmi.

A2. Association of the first operation. For all grixmis x, y, z: (x # y) # z = x # (y #
z).

A3. Commutation of the first operation. For all grixmis x and y: x # y = y # x.

## The shape of it

Two questions sort the grixmis quickly. Does combining a grixmi with itself change it?
For tezreld and vexyuk it does not. Does it matter which side it goes on? For tezreld,
vexyuk and muxlum it does not.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R2 rests on S2 (the Hurnglim combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R3 rests on S2 (the Hurnglim combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Evaluate (vexyuk # vexyuk) # tezreld. Each line below is one lookup in a table.
    vexyuk # vexyuk = vexyuk   (the table for #)
    vexyuk # tezreld = tezreld   (the table for #)
So (vexyuk # vexyuk) # tezreld is tezreld.

Bracketing is not cosmetic, so here is vexyuk # (tezreld # vexyuk) for contrast.
    tezreld # vexyuk = tezreld   (the table for #)
    vexyuk # tezreld = tezreld   (the table for #)
That gives tezreld, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
muxlum |> tezreld hold? Read off what muxlum stands over: tezreld, vexyuk and muxlum.
tezreld is among them, so it holds.

## A case that breaks

R2. It is not the case that: For every grixmi x: x # x = x. The case that settles it: x
= muxlum, value = vexyuk. Anyone carrying this claim over from a more familiar system
will be wrong here, and wrong in a way that propagates.

R3. It is not the case that: For all grixmis x, y, z: if x # y = x # z then y = z. The
case that settles it: x = tezreld, y = tezreld, z = vexyuk. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

These results are used again in A4 (a neutral object for the first operation), A5 (an
absorbing object for the first operation), A6 (reflexivity of the relation) and A7
(transitivity of the relation).

## Proofs

R2. It is not the case that: For every grixmi x: x # x = x.

  (1) [S2] Take the case x = muxlum, value = vexyuk, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 27 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R3. It is not the case that: For all grixmis x, y, z: if x # y = x # z then y = z.

  (1) [S2] Take the case x = tezreld, y = tezreld, z = vexyuk, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 27 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R2 and R3. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 1.
  x001. Work out the value of muxlum # muxlum.
Level 2.
  x002. Solve x # tezreld = tezreld for x, naming every solution.
  x003. Solve x # muxlum = muxlum for x, naming every solution.
Level 5.
  x005. The following fails in this system: For every grixmi x: x # x = x. Name the earliest grixmi, in the order the grixmis were introduced, that witnesses the failure.
  x006. The following fails in this system: For all grixmis x, y, z: if x # y = x # z then y = z. Name the earliest grixmi, in the order the grixmis were introduced, that witnesses the failure.

# Chapter 2. Neutral objects and reversal

## Why this chapter

The present chapter develops a neutral object for the first operation, an absorbing
object for the first operation and the system does not have reversal under the first
operation.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

One habit to adopt: when a statement below quantifies over grixmis, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A4. A neutral object for the first operation. There is a grixmi vexyuk with vexyuk # x =
x # vexyuk = x for every x.

A5. An absorbing object for the first operation. There is a grixmi tezreld with tezreld
# x = x # tezreld = tezreld for every x.

## The shape of it

Neutrality is a strong condition disguised as a weak one. It fixes a single grixmi and,
through that, constrains everything that can combine with it.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R1 rests on S2 (the Hurnglim combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take (muxlum # muxlum) # (tezreld # muxlum) and work it out one step at a time.
    muxlum # muxlum = vexyuk   (the table for #)
    tezreld # muxlum = tezreld   (the table for #)
    vexyuk # tezreld = tezreld   (the table for #)
That leaves tezreld, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is muxlum # (tezreld # muxlum) for contrast.
    tezreld # muxlum = tezreld   (the table for #)
    muxlum # tezreld = tezreld   (the table for #)
That gives tezreld, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test muxlum |> tezreld. The umbhob of muxlum is tezreld, vexyuk and muxlum, and tezreld
lies inside it, so the relation holds.

## A case that breaks

R1. Some grixmi x admits no grixmi y for which x # y and y # x both land on a neutral
object. It fails at x = tezreld. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside S2 (the Hurnglim combination tables).

These results are used again in D5 (the hobka) and T1 (the hobka is the only one of its
kind).

## Proofs

R1. Some grixmi x admits no grixmi y for which x # y and y # x both land on a neutral object.

  (1) [S2] Take the case x = tezreld, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 27 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R1. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 5.
  x004. The following fails in this system: Some grixmi x admits no grixmi y for which x # y and y # x both land on a neutral object. Name the earliest grixmi, in the order the grixmis were introduced, that witnesses the failure.

# Chapter 3. The relation and what it orders

## Why this chapter

Work through this chapter with the tables in front of you. It covers reflexivity of the
relation, transitivity of the relation and comparability of every pair, and each claim
can be checked by hand.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

One habit to adopt: when a statement below quantifies over grixmis, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A6. Reflexivity of the relation. For every grixmi x: x |> x.

A7. Transitivity of the relation. For all grixmis x, y, z: if x |> y and y |> z then x
|> z.

A8. Comparability of every pair. For all grixmis x and y, at least one of x |> y and y
|> x holds.

A9. Agreement of the relation with the first operation. For all grixmis x, y, z: if x |>
y then (z # x) |> (z # y) and (x # z) |> (y # z).

D4. The umbhob of a grixmi. The umbhob of a grixmi x is the collection of grixmis y for
which x |> y holds.

Worked out for each grixmi: tezreld to tezreld; vexyuk to tezreld, vexyuk and muxlum;
muxlum to tezreld, vexyuk and muxlum.

## The shape of it

The relation is easiest to see as a height. Each grixmi casts a umbhob over what it
refines, and the sizes of those shadows here are 1 and 3. Sizes repeat, so the objects
do not line up in single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 3 grixmis the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R4 rests on S2 (the Hurnglim combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take (vexyuk # tezreld) # vexyuk and work it out one step at a time.
    vexyuk # tezreld = tezreld   (the table for #)
    tezreld # vexyuk = tezreld   (the table for #)
The expression comes to tezreld.

Bracketing is not cosmetic, so here is tezreld # (vexyuk # vexyuk) for contrast.
    vexyuk # vexyuk = vexyuk   (the table for #)
    tezreld # vexyuk = tezreld   (the table for #)
That gives tezreld, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
muxlum |> muxlum hold? Read off what muxlum stands over: tezreld, vexyuk and muxlum.
muxlum is among them, so it holds.

## A case that breaks

R4. It is not the case that: For all grixmis x and y: if x |> y and y |> x then x = y.
It fails at x = vexyuk, y = muxlum. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: S2 (the Hurnglim combination tables).

These results are used again in D9 (a lumsib), D13 (vexjen pairs), T9 (umbhobs are
nested along the relation) and T10 (the system has a lumsib).

## Proofs

R4. It is not the case that: For all grixmis x and y: if x |> y and y |> x then x = y.

  (1) [S2] Take the case x = vexyuk, y = muxlum, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 27 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the umbhob of a grixmi. Each of these is used by name
later, so the names are worth learning rather than looking up.

Do not carry forward R4. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x011. Which grixmis y satisfy vexyuk |> y? Name them all.
Level 5.
  x007. The following fails in this system: For all grixmis x and y: if x |> y and y |> x then x = y. Name the earliest grixmi, in the order the grixmis were introduced, that witnesses the failure.

# Chapter 4. Combining objects

## Why this chapter

What follows was pieced together backwards. The last item of it, rastpon grixmis,
grixmis that shenfal and the hobka, was noticed before anyone had a reason to expect it.

Nothing here stands on its own. The arguments lean on chapters 1 and 2, and a reader who
has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about grixmis covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

## What is defined here

D1. Rastpon grixmis. A grixmi x is called rastpon when x # x = x.

Running the definition over every grixmi leaves tezreld and vexyuk.

D2. Grixmis that shenfal. Two grixmis x and y are said to shenfal when x # y = y # x.

D5. The hobka. The grixmi vexyuk is called the hobka of the system. It is the unique
grixmi that leaves every grixmi unchanged under #.

Here that is vexyuk.

## The shape of it

A useful mental split: some grixmis are inert under the operation and some are not.
tezreld and vexyuk come back unchanged when combined with themselves, and tezreld,
vexyuk and muxlum commute with everything.

Neutrality is a strong condition disguised as a weak one. It fixes a single grixmi and,
through that, constrains everything that can combine with it.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 3 grixmis the table is short enough to consult every time.

## Where these results come from

This chapter is groundwork. The derivations that use it start in the next one.

## A worked case

Evaluate (vexyuk # vexyuk) # (vexyuk # muxlum). Each line below is one lookup in a
table.
    vexyuk # vexyuk = vexyuk   (the table for #)
    vexyuk # muxlum = muxlum   (the table for #)
    vexyuk # muxlum = muxlum   (the table for #)
The expression comes to muxlum.

Bracketing is not cosmetic, so here is vexyuk # (vexyuk # vexyuk) for contrast.
    vexyuk # vexyuk = vexyuk   (the table for #)
    vexyuk # vexyuk = vexyuk   (the table for #)
That gives vexyuk, against muxlum above.

One decision about the relation, since deciding is as much a skill as computing. Does
muxlum |> tezreld hold? Read off what muxlum stands over: tezreld, vexyuk and muxlum.
tezreld is among them, so it holds.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of grixmis that come back
unchanged from themselves: tezreld and vexyuk. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by a neutral object for the first operation and closure under the
first operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A1 (closure under the first operation) and A4 (a neutral object for the
first operation).

These results are used again in D6 (the zelmorn), D7 (the korrsol), D10 (aztpyr grixmis)
and T1 (the hobka is the only one of its kind).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

Carry forward rastpon grixmis, grixmis that shenfal and the hobka. Later chapters state
their results in these terms and do not restate the definitions.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 2.
  x012. Name the hobka of the system.
Level 3.
  x008. List every grixmi in the rastpon.

# Chapter 5. The relation and what it orders (2)

## Why this chapter

Anyone using this system to keep track of something will meet vexjen pairs, vintmorn
collections and a lumsib early, whether or not they go looking.

Prerequisites are real here: chapters 1 and 3 supply the notions the statements below
are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 3
grixmis that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D13. Vexjen pairs. Two distinct grixmis x and y form a vexjen pair when x |> y and y |>
x both hold, that is, when each lies in the umbhob of the other.

Running the definition over every grixmi leaves vexyuk and muxlum.

D3. Vintmorn collections. A collection S of grixmis is vintmorn when x # y belongs to S
for every pair x, y drawn from S.

D9. A lumsib. A grixmi f is a lumsib when f |> y holds for every grixmi y, that is, when
the umbhob of f is the whole system.

In this system that picks out vexyuk and muxlum, which is 2 of the 3 grixmis.

## The shape of it

Picture the shenyuk as what happens when you start with one grixmi and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 3 grixmis, that stops. In this system the sizes it stops at are 1 and 2.

The relation is easiest to see as a height. Each grixmi casts a umbhob over what it
refines, and the sizes of those shadows here are 1 and 3. Sizes repeat, so the objects
do not line up in single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 3 grixmis the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R8 rests on D4 (the umbhob of a grixmi). The dependence is on the content of those
results, not only on their vocabulary.

T11 rests on D4 (the umbhob of a grixmi) and A9 (agreement of the relation with the
first operation). Remove any one of them and the statement stops making sense, not
merely stops being provable.

T9 rests on D4 (the umbhob of a grixmi) and A7 (transitivity of the relation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Take (muxlum # muxlum) # muxlum and work it out one step at a time.
    muxlum # muxlum = vexyuk   (the table for #)
    vexyuk # muxlum = muxlum   (the table for #)
So (muxlum # muxlum) # muxlum is muxlum.

A companion case, muxlum # (muxlum # muxlum), to show what the brackets are doing.
    muxlum # muxlum = vexyuk   (the table for #)
    muxlum # vexyuk = muxlum   (the table for #)
That gives muxlum, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test tezreld |> vexyuk. The umbhob of tezreld is tezreld, and vexyuk lies outside it, so
the relation fails.

## A case that breaks

R8. It is not the case that: If x |> y then y |> x. It fails at x = vexyuk, y = tezreld.
One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of agreement of the relation with the first
operation, closure under the first operation and transitivity of the relation. Those are
properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A1 (closure under the first operation), A7
(transitivity of the relation), A9 (agreement of the relation with the first operation)
and D4 (the umbhob of a grixmi).

What is built on it later: D8 (the shenyuk of a grixmi), T3 (the zelmorn is vintmorn),
T4 (the shenyuk of a grixmi is vintmorn) and T8 (the korrsol is vintmorn).

## Proofs

R8. It is not the case that: If x |> y then y |> x.

  (1) [S2] Take the case x = vexyuk, y = tezreld, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 9 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T11. If x |> y then (x # z) |> (y # z) for every grixmi z.

  (1) [D4] Let y lie in the umbhob of x.
  (2) [A9] Compatibility applies the operation to both sides at once.
  (3) Nothing else is needed, since z was arbitrary.

Checked over 27 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T9. If y lies in the umbhob of x, then the umbhob of y is contained in the umbhob of x.

  (1) [D4] Let y satisfy x |> y and let z satisfy y |> z.
  (2) [A7] Transitivity gives x |> z.
  (3) [D4] So every member of the umbhob of y is a member of that of x.

Checked over 27 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward vexjen pairs, vintmorn collections and a lumsib. Later chapters state
their results in these terms and do not restate the definitions.

The results now available are T11 and T9, each settled by exhaustive check rather than
by argument from analogy.

Do not carry forward R8. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x009. How many grixmis lie in the smallest vintmorn collection containing vexyuk?
  x010. How many grixmis lie in the smallest vintmorn collection containing muxlum?
Level 4.
  x017. List every grixmi in the lumsib.
  x025. List every grixmi in the vexjen.
  x028. The result above concerns umbhobs. List the umbhob of vexyuk.
Level 5.
  x031. The following fails in this system: If x |> y then y |> x. Name the earliest grixmi, in the order the grixmis were introduced, that witnesses the failure.

# Chapter 6. Neutral objects and reversal (2)

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through aztpyr grixmis, the zelmorn
and the korrsol.

Nothing here stands on its own. The arguments lean on chapters 2 and 4, and a reader who
has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about grixmis covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D10. Aztpyr grixmis. A grixmi x is aztpyr when x # x equals the hobka.

Running the definition over every grixmi leaves vexyuk and muxlum.

D6. The zelmorn. The zelmorn of the system is the collection of grixmis that shenfal
with every grixmi.

Running the definition over every grixmi leaves tezreld, vexyuk and muxlum.

D7. The korrsol. The korrsol is the collection of all rastpon grixmis.

Running the definition over every grixmi leaves tezreld and vexyuk.

## The shape of it

A useful mental split: some grixmis are inert under the operation and some are not.
tezreld and vexyuk come back unchanged when combined with themselves, and tezreld,
vexyuk and muxlum commute with everything.

The neutral grixmi vexyuk is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 3 grixmis the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R9 rests on D5 (the hobka). Remove any one of them and the statement stops making sense,
not merely stops being provable.

T1 rests on D5 (the hobka) and A4 (a neutral object for the first operation). Remove any
one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Here is (vexyuk # tezreld) # (vexyuk # tezreld), reduced without skipping anything.
    vexyuk # tezreld = tezreld   (the table for #)
    vexyuk # tezreld = tezreld   (the table for #)
    tezreld # tezreld = tezreld   (the table for #)
So (vexyuk # tezreld) # (vexyuk # tezreld) is tezreld.

Move the brackets and the work changes. Take tezreld # (vexyuk # vexyuk).
    vexyuk # vexyuk = vexyuk   (the table for #)
    tezreld # vexyuk = tezreld   (the table for #)
The value is tezreld. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
muxlum |> vexyuk hold? Read off what muxlum stands over: tezreld, vexyuk and muxlum.
vexyuk is among them, so it holds.

## A case that breaks

R9. It is not the case that: e # x equals the hobka for every grixmi x. The case that
settles it: anchor = vexyuk, x = tezreld, value = tezreld. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by a neutral object for the first operation and closure under the
first operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A4 (a neutral object for the first operation),
D1 (rastpon grixmis), D2 (grixmis that shenfal) and D5 (the hobka).

What is built on it later: T2 (the hobka lies in the zelmorn), T3 (the zelmorn is
vintmorn), T7 (the shenyuk of a zelmorn grixmi stays in the zelmorn) and T8 (the korrsol
is vintmorn).

## Proofs

R9. It is not the case that: e # x equals the hobka for every grixmi x.

  (1) [S2] Take the case anchor = vexyuk, x = tezreld, value = tezreld, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 3 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T1. There is exactly one grixmi e with e # x = x # e = x for every grixmi x.

  (1) [D5] Suppose e and f both leave every grixmi unchanged.
  (2) [A4] Then e # f = f, reading e as neutral on the left.
  (3) [A4] And e # f = e, reading f as neutral on the right.
  (4) So e = f, and the two suppositions describe the same object.

Checked over 9 cases: every object paired with every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward aztpyr grixmis, the zelmorn and the korrsol. Later chapters state their
results in these terms and do not restate the definitions.

The results now available are T1, each settled by exhaustive check rather than by
argument from analogy.

Explicitly not available: R9. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x013. Write down the korrsol in full.
  x018. Which grixmis make up the aztpyr? Name them all.
Level 5.
  x032. The following fails in this system: e # x equals the hobka for every grixmi x. Name the earliest grixmi, in the order the grixmis were introduced, that witnesses the failure.

# Chapter 7. Combining objects (2)

## Why this chapter

The present chapter develops the shenyuk of a grixmi, the system has a lumsib and where
every grixmi is rastpon breaks down.

Prerequisites are real here: chapters 1, 3, 4, 5 and 6 supply the notions the statements
below are phrased in.

One habit to adopt: when a statement below quantifies over grixmis, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D8. The shenyuk of a grixmi. The shenyuk of a grixmi x, written [x], is the smallest
vintmorn collection that contains x.

Worked out for each grixmi: tezreld to tezreld; vexyuk to vexyuk; muxlum to vexyuk and
muxlum.

## The shape of it

Picture the shenyuk as what happens when you start with one grixmi and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 3 grixmis, that stops. In this system the sizes it stops at are 1 and 2.

Think of |> as pointing downhill. The umbhob of a grixmi is everything downhill of it,
and those shadows here have sizes 1 and 3.

A useful mental split: some grixmis are inert under the operation and some are not.
tezreld and vexyuk come back unchanged when combined with themselves, and tezreld,
vexyuk and muxlum commute with everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 3 grixmis the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T10 rests on D9 (a lumsib) and A8 (comparability of every pair). The dependence is on
the content of those results, not only on their vocabulary.

R6 rests on D7 (the korrsol). The dependence is on the content of those results, not
only on their vocabulary.

T12 rests on D6 (the zelmorn). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T2 rests on D5 (the hobka) and D6 (the zelmorn). The dependence is on the content of
those results, not only on their vocabulary.

T3 rests on D6 (the zelmorn), D3 (vintmorn collections) and A2 (association of the first
operation). The dependence is on the content of those results, not only on their
vocabulary.

T8 rests on D7 (the korrsol) and D3 (vintmorn collections). The dependence is on the
content of those results, not only on their vocabulary.

## A worked case

Evaluate (tezreld # muxlum) # muxlum. Each line below is one lookup in a table.
    tezreld # muxlum = tezreld   (the table for #)
    tezreld # muxlum = tezreld   (the table for #)
That leaves tezreld, and no other reading of the notation gives anything else.

A companion case, muxlum # (muxlum # tezreld), to show what the brackets are doing.
    muxlum # tezreld = tezreld   (the table for #)
    muxlum # tezreld = tezreld   (the table for #)
The value is tezreld. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test vexyuk |> muxlum. The umbhob of vexyuk is tezreld, vexyuk and muxlum, and muxlum
lies inside it, so the relation holds.

Now compute [muxlum]. Fold muxlum against itself, then fold whatever appeared against
everything present, and stop when a round adds nothing. The result is vexyuk and muxlum,
of size 2.

## A case that breaks

R6. It is not the case that: x # x = x for every grixmi x. It fails at x = muxlum, value
= vexyuk. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by a neutral object for the first operation, association of the
first operation, closure under the first operation and comparability of every pair. A
system without them is not a system where these results are harder to prove; it is a
system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A2 (association of the first operation), A8 (comparability of every
pair), D3 (vintmorn collections) and D5 (the hobka).

What is built on it later: D11 (the glimmorn of a grixmi), T4 (the shenyuk of a grixmi
is vintmorn), T5 (the shenyuk is contained in every vintmorn collection) and T7 (the
shenyuk of a zelmorn grixmi stays in the zelmorn).

## Proofs

T10. Some grixmi lumsibs the whole system.

  (1) [A8] Every pair is comparable, so the relation orders the objects into a line.
  (2) [D9] The claim is that the line has a bottom.
  (3) The carrier is finite, so the search over candidates terminates.

Checked over 9 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

R6. It is not the case that: x # x = x for every grixmi x.

  (1) [S2] Take the case x = muxlum, value = vexyuk, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 3 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T12. Every pair of grixmis shenfals.

  (1) [D6] The zelmorn is defined by shenfaling with everything.
  (2) [D2] The claim is that x # y = y # x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 9 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T2. The hobka shenfals with every grixmi.

  (1) [D5] Let e be the hobka and x any grixmi.
  (2) [D5] Then e # x = x and x # e = x.
  (3) [D2] So e # x = x # e, which is what it means to shenfal.
  (4) [D6] Since x was arbitrary, e belongs to the zelmorn.

Checked over 3 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. If x and y both shenfal with every grixmi, then so does x # y.

  (1) [D6] Let x and y lie in the zelmorn and let z be any grixmi.
  (2) [A2] Then (x # y) # z = x # (y # z).
  (3) [D6] Move z past y, then past x, using that each shenfals with everything.
  (4) [D3] So x # y shenfals with z, and the zelmorn is vintmorn.

Checked over 9 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

T8. If x and y are both rastpon then so is x # y.

  (1) [D7] Let x and y be rastpon.
  (2) [D1] The claim asks whether (x # y) # (x # y) returns x # y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 9 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the shenyuk of a grixmi. Later chapters state their results in these terms
and do not restate the definitions.

The results now available are T10, T12, T2, T3 and T8, each settled by exhaustive check
rather than by argument from analogy.

Explicitly not available: R6. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x014. List the shenyuk of muxlum.
Level 4.
  x015. Let z be muxlum # vexyuk. List the shenyuk of z.
  x016. Let z be muxlum # muxlum. List the shenyuk of z.
  x027. Name the grixmis that make up the korrsol, which is what the result above is a claim about.
  x029. Name the lumsib of the system.
Level 5.
  x030. The following fails in this system: x # x = x for every grixmi x. Name the earliest grixmi, in the order the grixmis were introduced, that witnesses the failure.

# Chapter 8. Collections that close on themselves

## Why this chapter

Work through this chapter with the tables in front of you. It covers the glimmorn of a
grixmi, the shenyuk of a grixmi is vintmorn and the shenyuk of a zelmorn grixmi stays in
the zelmorn, and each claim can be checked by hand.

Prerequisites are real here: chapters 5, 6 and 7 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over grixmis, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D11. The glimmorn of a grixmi. The glimmorn of a grixmi x is the number of grixmis in
its shenyuk [x].

Worked out for each grixmi: tezreld to 1; vexyuk to 1; muxlum to 2.

## The shape of it

Picture the shenyuk as what happens when you start with one grixmi and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 3 grixmis, that stops. In this system the sizes it stops at are 1 and 2.

Two questions sort the grixmis quickly. Does combining a grixmi with itself change it?
For tezreld and vexyuk it does not. Does it matter which side it goes on? For tezreld,
vexyuk and muxlum it does not.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 3 grixmis the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T4 rests on D8 (the shenyuk of a grixmi) and D3 (vintmorn collections). Remove any one
of them and the statement stops making sense, not merely stops being provable.

T7 rests on D8 (the shenyuk of a grixmi), D6 (the zelmorn) and T3 (the zelmorn is
vintmorn). Remove any one of them and the statement stops making sense, not merely stops
being provable.

## A worked case

Evaluate (vexyuk # vexyuk) # (vexyuk # muxlum). Each line below is one lookup in a
table.
    vexyuk # vexyuk = vexyuk   (the table for #)
    vexyuk # muxlum = muxlum   (the table for #)
    vexyuk # muxlum = muxlum   (the table for #)
The expression comes to muxlum.

Move the brackets and the work changes. Take vexyuk # (vexyuk # vexyuk).
    vexyuk # vexyuk = vexyuk   (the table for #)
    vexyuk # vexyuk = vexyuk   (the table for #)
The value is vexyuk, not muxlum.

One decision about the relation, since deciding is as much a skill as computing. Does
tezreld |> vexyuk hold? Read off what tezreld stands over: tezreld. vexyuk is not among
them, so it fails.

Now compute [muxlum]. Fold muxlum against itself, then fold whatever appeared against
everything present, and stop when a round adds nothing. The result is vexyuk and muxlum,
of size 2.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of association of the first operation and
closure under the first operation. Those are properties of this system, not of systems
in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside D3 (vintmorn collections), D6 (the zelmorn), D8 (the shenyuk of a grixmi)
and T3 (the zelmorn is vintmorn).

What is built on it later: D12 (the bratez), T5 (the shenyuk is contained in every
vintmorn collection), T6 (a grixmi is rastpon exactly when its glimmorn is one) and R5
(where the glimmorn divides the number of grixmis breaks down).

## Proofs

T4. For every grixmi x, the collection [x] is vintmorn.

  (1) [D8] [x] is built by taking x and closing under #.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 27 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

T7. If x lies in the zelmorn then every grixmi of [x] lies in the zelmorn.

  (1) [T3] The zelmorn is vintmorn.
  (2) [D8] [x] is the smallest vintmorn collection containing x.
  (3) A smallest such collection sits inside any other, and the zelmorn is one.

Checked over 9 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the glimmorn of a grixmi. Later chapters state their results in these
terms and do not restate the definitions.

The results now available are T4 and T7, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x019. How many grixmis lie in [vexyuk]?
  x020. How many grixmis lie in [muxlum]?
Level 5.
  x021. Let z be (tezreld # tezreld) # vexyuk. What is the glimmorn of z?
  x022. Let z be (muxlum # vexyuk) # vexyuk. What is the glimmorn of z?
  x023. Let z be (tezreld # vexyuk) # tezreld. What is the glimmorn of z?

# Chapter 9. Collections that close on themselves (2)

## Why this chapter

The results collected here were not found in this order. The bratez, where the glimmorn
divides the number of grixmis breaks down and where some grixmi reaches every other
breaks down came first, and the rest was assembled around that once the pattern was
visible.

Nothing here stands on its own. The arguments lean on chapters 4, 7 and 8, and a reader
who has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 3
grixmis that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D12. The bratez. The bratez of the system is the collection of grixmis whose glimmorn is
largest.

Running the definition over every grixmi leaves muxlum.

## The shape of it

The right picture for shenyuk is a spreading stain rather than a list. Drop one grixmi
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
grixmis depending on where it started.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R5 rests on D11 (the glimmorn of a grixmi) and T4 (the shenyuk of a grixmi is vintmorn).
The dependence is on the content of those results, not only on their vocabulary.

R7 rests on D8 (the shenyuk of a grixmi) and D11 (the glimmorn of a grixmi). The
dependence is on the content of those results, not only on their vocabulary.

T5 rests on D8 (the shenyuk of a grixmi) and T4 (the shenyuk of a grixmi is vintmorn).
The dependence is on the content of those results, not only on their vocabulary.

T6 rests on D1 (rastpon grixmis), D11 (the glimmorn of a grixmi) and T4 (the shenyuk of
a grixmi is vintmorn). The dependence is on the content of those results, not only on
their vocabulary.

## A worked case

Here is (vexyuk # vexyuk) # tezreld, reduced without skipping anything.
    vexyuk # vexyuk = vexyuk   (the table for #)
    vexyuk # tezreld = tezreld   (the table for #)
So (vexyuk # vexyuk) # tezreld is tezreld.

A companion case, vexyuk # (tezreld # vexyuk), to show what the brackets are doing.
    tezreld # vexyuk = tezreld   (the table for #)
    vexyuk # tezreld = tezreld   (the table for #)
The value is tezreld. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test tezreld |> vexyuk. The umbhob of tezreld is tezreld, and vexyuk lies outside it, so
the relation fails.

## A case that breaks

R5. It is not the case that: For every grixmi x, the glimmorn of x divides 3. It fails
at x = muxlum, reach = 2, size = 3. One case is enough, and this is the earliest one.

R7. It is not the case that: There is a grixmi whose shenyuk is the whole system. It
fails at largest_span = 2, size = 3. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside D1 (rastpon grixmis), D11 (the glimmorn of a grixmi), D8 (the shenyuk of
a grixmi) and T4 (the shenyuk of a grixmi is vintmorn).

## Proofs

R5. It is not the case that: For every grixmi x, the glimmorn of x divides 3.

  (1) [S2] Take the case x = muxlum, reach = 2, size = 3, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 3 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

R7. It is not the case that: There is a grixmi whose shenyuk is the whole system.

  (1) [S2] Take the case largest_span = 2, size = 3, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 3 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T5. If S is vintmorn and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 15 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T6. x # x = x holds if and only if [x] contains x alone.

  (1) [D1] If x # x = x then {x} is already closed under #.
  (2) [T4] So [x] = {x} and the glimmorn is one.
  (3) [D11] Conversely a span of one object must contain x # x, which is then x.

Checked over 3 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the bratez. Later chapters state their results in these terms and do not
restate the definitions.

The results now available are T5 and T6, each settled by exhaustive check rather than by
argument from analogy.

Do not carry forward R5 and R7. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x024. Which grixmis make up the bratez? Name them all.
Level 5.
  x026. The following fails in this system: For every grixmi x, the glimmorn of x divides 3. Name the earliest grixmi, in the order the grixmis were introduced, that witnesses the failure.
