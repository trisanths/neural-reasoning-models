# Chapter 12. The second operation and how the two interact (2)

## Why this chapter

The practical content of this chapter is the second operation keeps the vintvint intact.
It is the part that shows up in use.

Nothing here stands on its own. The arguments lean on chapters 4, 7 and 9, and a reader
who has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over wrenhobs, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

The interesting content of a two operation system sits in the gap between them: which
one distributes over which, and which wrenhobs are fixed by both.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T15 rests on D6 (the vintvint), A6 (closure under the second operation) and T3 (the
vintvint is yukxil). The dependence is on the content of those results, not only on
their vocabulary.

## A worked case

Here is (xilfal ; ovipyr) ; (kaglim ; tuisk), reduced without skipping anything.
    xilfal ; ovipyr = ovipyr   (the table for ;)
    kaglim ; tuisk = ovipyr   (the table for ;)
    ovipyr ; ovipyr = ovipyr   (the table for ;)
So (xilfal ; ovipyr) ; (kaglim ; tuisk) is ovipyr.

Bracketing is not cosmetic, so here is ovipyr ; (kaglim ; xilfal) for contrast.
    kaglim ; xilfal = ovipyr   (the table for ;)
    ovipyr ; ovipyr = ovipyr   (the table for ;)
The value is ovipyr. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test iskglim >- xilfal. The solzam of iskglim is iskglim, lornhob, tuisk, kaglim, xilfal
and ovipyr, and xilfal lies inside it, so the relation holds.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of wrenhobs that come back
unchanged from themselves: iskglim and ovipyr. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by association of the first operation, closure under the first
operation and closure under the second operation. A system without them is not a system
where these results are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A6 (closure under the second operation), D6 (the vintvint) and T3 (the
vintvint is yukxil).

## Proofs

T15. If x and y lie in the vintvint then so does x |= y.

  (1) [T3] The vintvint is already yukxil under ;.
  (2) [A6] The second operation is defined on every pair.
  (3) [D6] The claim is that |= respects the vintvint as well.

Checked over 36 cases: every ordered pair from the core. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

The results now available are T15, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

No exercises here. Every question this chapter suggested turned out to be answerable
from the question itself, so all of them were discarded.
