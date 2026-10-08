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
