# Chapter 12. The second operation and how the two interact (2)

## Why this chapter

So far the qenjens have been objects to be pushed around. This chapter starts asking
what they are like. We take up the second operation keeps the zammorn intact.

Prerequisites are real here: chapters 4, 7 and 9 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over qenjens, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

The interesting content of a two operation system sits in the gap between them: which
one distributes over which, and which qenjens are fixed by both.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T14 rests on D6 (the zammorn), A6 (closure under the second operation) and T3 (the
zammorn is rastdri). The dependence is on the content of those results, not only on
their vocabulary.

## A worked case

Here is (nyrazt + yuktarn) + (xilzam + shentu), reduced without skipping anything.
    nyrazt + yuktarn = yuktarn   (the table for +)
    xilzam + shentu = shentu   (the table for +)
    yuktarn + shentu = yuktarn   (the table for +)
So (nyrazt + yuktarn) + (xilzam + shentu) is yuktarn.

Move the brackets and the work changes. Take yuktarn + (xilzam + nyrazt).
    xilzam + nyrazt = nyrazt   (the table for +)
    yuktarn + nyrazt = yuktarn   (the table for +)
The value is yuktarn. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test nyrazt <~ cloreld. The opalglim of nyrazt is nyrazt and cloreld, and cloreld lies
inside it, so the relation holds.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of qenjens that come back
unchanged from themselves: yuktarn and xilzam. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of association of the first operation,
closure under the first operation and closure under the second operation. Those are
properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A6 (closure under the second operation), D6 (the zammorn) and T3 (the
zammorn is rastdri).

## Proofs

T14. If x and y lie in the zammorn then so does x |= y.

  (1) [T3] The zammorn is already rastdri under +.
  (2) [A6] The second operation is defined on every pair.
  (3) [D6] The claim is that |= respects the zammorn as well.

Checked over 25 cases: every ordered pair from the core. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

The results now available are T14, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

No exercises here. Every question this chapter suggested turned out to be answerable
from the question itself, so all of them were discarded.
