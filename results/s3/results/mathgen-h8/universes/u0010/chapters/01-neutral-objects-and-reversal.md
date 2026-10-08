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
