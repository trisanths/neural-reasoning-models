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
