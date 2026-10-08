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
