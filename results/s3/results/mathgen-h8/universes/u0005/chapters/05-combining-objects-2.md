# Chapter 6. Combining objects (2)

## Why this chapter

So far the jenxils have been objects to be pushed around. This chapter starts asking
what they are like. We take up the glimlum, the rastzam and the voropal of a jenxil.

Nothing here stands on its own. The arguments lean on chapter 4, and a reader who has
skipped it will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over jenxils, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D5. The glimlum. The glimlum of the system is the collection of jenxils that xilwren
with every jenxil.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D6. The rastzam. The rastzam is the collection of all yukwren jenxils.

In this system that picks out reldvint, which is 1 of the 3 jenxils.

D7. The voropal of a jenxil. The voropal of a jenxil x, written [x], is the smallest
espagrix collection that contains x.

Worked out for each jenxil: reldvint to reldvint; wrenmux to reldvint and wrenmux;
zellum to reldvint and zellum.

## The shape of it

Picture the voropal as what happens when you start with one jenxil and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 3 jenxils, that stops. In this system the sizes it stops at are 1 and 2.

A useful mental split: some jenxils are inert under the operation and some are not.
reldvint come back unchanged when combined with themselves, and none commutes with
everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 3 jenxils the table is short enough to consult every time.

## Where these results come from

Nothing is derived in this chapter. It lays down material that later chapters draw on.

## A worked case

Evaluate (wrenmux % zellum) % (reldvint % zellum). Each line below is one lookup in a
table.
    wrenmux % zellum = reldvint   (the table for %)
    reldvint % zellum = reldvint   (the table for %)
    reldvint % reldvint = reldvint   (the table for %)
That leaves reldvint, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take zellum % (reldvint % wrenmux).
    reldvint % wrenmux = reldvint   (the table for %)
    zellum % reldvint = zellum   (the table for %)
That gives zellum, against reldvint above.

One decision about the relation, since deciding is as much a skill as computing. Does
wrenmux =< wrenmux hold? Read off what wrenmux stands over: wrenmux and zellum. wrenmux
is among them, so it holds.

A second case, this time a voropal. Start from reldvint. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is reldvint, so the
muxhob of reldvint is 1.

## A case that breaks

A quick guard against a common slip: reldvint % zellum is reldvint while zellum %
reldvint is zellum. Order is not decoration in this system.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by closure under the first operation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: D1 (yukwren jenxils), D2 (jenxils that xilwren)
and D3 (espagrix collections).

What is built on it later: D9 (the muxhob of a jenxil), T1 (the voropal of a jenxil is
espagrix), T2 (the voropal is contained in every espagrix collection) and T4 (the
rastzam is espagrix).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

Carry forward the glimlum, the rastzam and the voropal of a jenxil. Later chapters state
their results in these terms and do not restate the definitions.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x018. Which jenxils make up the rastzam? Name them all.
  x019. Name every jenxil in [wrenmux].
  x020. List the voropal of zellum.
Level 4.
  x021. Let z be zellum % zellum. List the voropal of z.
