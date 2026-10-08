# Chapter 4. Combining objects

## Why this chapter

What follows was pieced together backwards. The last item of it, yukwren jenxils,
jenxils that xilwren and espagrix collections, was noticed before anyone had a reason to
expect it.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

The standard of proof here is exhaustion. A universal claim about jenxils covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

## What is defined here

D1. Yukwren jenxils. A jenxil x is called yukwren when x % x = x.

Running the definition over every jenxil leaves reldvint.

D2. Jenxils that xilwren. Two jenxils x and y are said to xilwren when x % y = y % x.

D3. Espagrix collections. A collection S of jenxils is espagrix when x % y belongs to S
for every pair x, y drawn from S.

## The shape of it

Picture the voropal as what happens when you start with one jenxil and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 3 jenxils, that stops. In this system the sizes it stops at are 1 and 2.

A useful mental split: some jenxils are inert under the operation and some are not.
reldvint come back unchanged when combined with themselves, and none commutes with
everything.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

This chapter is groundwork. The derivations that use it start in the next one.

## A worked case

Take (zellum % wrenmux) % (zellum % wrenmux) and work it out one step at a time.
    zellum % wrenmux = wrenmux   (the table for %)
    zellum % wrenmux = wrenmux   (the table for %)
    wrenmux % wrenmux = reldvint   (the table for %)
So (zellum % wrenmux) % (zellum % wrenmux) is reldvint.

Move the brackets and the work changes. Take wrenmux % (zellum % zellum).
    zellum % zellum = reldvint   (the table for %)
    wrenmux % reldvint = wrenmux   (the table for %)
That gives wrenmux, against reldvint above.

Test wrenmux =< wrenmux. The rastqen of wrenmux is wrenmux and zellum, and wrenmux lies
inside it, so the relation holds.

## A case that breaks

A quick guard against a common slip: reldvint % wrenmux is reldvint while wrenmux %
reldvint is wrenmux. Order is not decoration in this system.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A1 (closure under the first operation).

What is built on it later: D5 (the glimlum), D6 (the rastzam), D7 (the voropal of a
jenxil) and T1 (the voropal of a jenxil is espagrix).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

Carry forward yukwren jenxils, jenxils that xilwren and espagrix collections. Later
chapters state their results in these terms and do not restate the definitions.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x015. List every jenxil in the yukwren.
  x016. How many jenxils lie in the smallest espagrix collection containing wrenmux?
  x017. How many jenxils lie in the smallest espagrix collection containing zellum?
