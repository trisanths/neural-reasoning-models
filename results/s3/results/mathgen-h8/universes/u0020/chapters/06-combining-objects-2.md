# Chapter 7. Combining objects (2)

## Why this chapter

The present chapter develops the shengel, the espanak and the thrafex of a shenopal.

Prerequisites are real here: chapter 5 supply the notions the statements below are
phrased in.

One habit to adopt: when a statement below quantifies over shenopals, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D5. The shengel. The shengel of the system is the collection of shenopals that gelwren
with every shenopal.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D6. The espanak. The espanak is the collection of all grixka shenopals.

In this system that picks out opallorn, which is 1 of the 5 shenopals.

D7. The thrafex of a shenopal. The thrafex of a shenopal x, written [x], is the smallest
quilglim collection that contains x.

Worked out for each shenopal: opallorn to opallorn; qenthra to opallorn and qenthra;
grixlum to opallorn and grixlum; vorpon to opallorn and vorpon; pontu to opallorn and
pontu.

## The shape of it

The right picture for thrafex is a spreading stain rather than a list. Drop one shenopal
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
shenopals depending on where it started.

Two questions sort the shenopals quickly. Does combining a shenopal with itself change
it? For opallorn it does not. Does it matter which side it goes on? It always does.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

This chapter is groundwork. The derivations that use it start in the next one.

## A worked case

Here is pontu % qenthra & grixlum, reduced without skipping anything.
    qenthra & grixlum = grixlum   (the table for &)
    pontu % grixlum = grixlum   (the table for %)
So pontu % qenthra & grixlum is grixlum.

Bracketing is not cosmetic, so here is qenthra % (grixlum % pontu) for contrast.
    grixlum % pontu = opallorn   (the table for %)
    qenthra % opallorn = qenthra   (the table for %)
That gives qenthra, against grixlum above.

Test opallorn :: grixlum. The muxsib of opallorn is opallorn, qenthra, grixlum, vorpon
and pontu, and grixlum lies inside it, so the relation holds.

Now compute [vorpon]. Fold vorpon against itself, then fold whatever appeared against
everything present, and stop when a round adds nothing. The result is opallorn and
vorpon, of size 2.

## A case that breaks

A quick guard against a common slip: qenthra % grixlum is opallorn while grixlum %
qenthra is qenthra. Order is not decoration in this system.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: D1 (grixka shenopals), D2 (shenopals that
gelwren) and D3 (quilglim collections).

These results are used again in D9 (the duthfal of a shenopal), T1 (the thrafex of a
shenopal is quilglim), T2 (the thrafex is contained in every quilglim collection) and T4
(the espanak is quilglim).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

New vocabulary from this chapter: the shengel, the espanak and the thrafex of a
shenopal. Each of these is used by name later, so the names are worth learning rather
than looking up.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x033. Write down the espanak in full.
  x034. Name every shenopal in [qenthra].
  x035. List the thrafex of grixlum.
  x036. Name every shenopal in [vorpon].
  x037. List the thrafex of pontu.
Level 4.
  x038. Let z be qenthra % grixlum. List the thrafex of z.
  x039. Let z be qenthra % pontu. List the thrafex of z.
  x040. Let z be vorpon % grixlum. List the thrafex of z.
