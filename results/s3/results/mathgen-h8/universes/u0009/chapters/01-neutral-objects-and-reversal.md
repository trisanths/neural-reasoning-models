# Chapter 2. Neutral objects and reversal

## Why this chapter

So far the reldjens have been objects to be pushed around. This chapter starts asking
what they are like. We take up a neutral object for the first operation, an absorbing
object for the first operation and the system does not have reversal under the first
operation.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

The standard of proof here is exhaustion. A universal claim about reldjens covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A4. A neutral object for the first operation. There is a reldjen kagel with kagel <> x =
x <> kagel = x for every x.

A5. An absorbing object for the first operation. There is a reldjen nakopal with nakopal
<> x = x <> nakopal = nakopal for every x.

## The shape of it

The neutral reldjen kagel is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 reldjens the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R1 rests on S2 (the Mornyuk combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take (nakopal <> kagel) <> (korrreld <> iskbra) and work it out one step at a time.
    nakopal <> kagel = nakopal   (the table for <>)
    korrreld <> iskbra = korrreld   (the table for <>)
    nakopal <> korrreld = nakopal   (the table for <>)
That leaves nakopal, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is kagel <> (korrreld <> nakopal) for contrast.
    korrreld <> nakopal = nakopal   (the table for <>)
    kagel <> nakopal = nakopal   (the table for <>)
That gives nakopal, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test korrreld :: iskbra. The drivor of korrreld is korrreld and iskbra, and iskbra lies
inside it, so the relation holds.

## A case that breaks

R1. Some reldjen x admits no reldjen y for which x <> y and y <> x both land on a
neutral object. The case that settles it: x = nakopal. Anyone carrying this claim over
from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside S2 (the Mornyuk combination tables).

These results are used again in D5 (the lornumb) and T1 (the lornumb is the only one of
its kind).

## Proofs

R1. Some reldjen x admits no reldjen y for which x <> y and y <> x both land on a neutral object.

  (1) [S2] Take the case x = nakopal, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R1. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 5.
  x008. The following fails in this system: Some reldjen x admits no reldjen y for which x <> y and y <> x both land on a neutral object. Name the earliest reldjen, in the order the reldjens were introduced, that witnesses the failure.
