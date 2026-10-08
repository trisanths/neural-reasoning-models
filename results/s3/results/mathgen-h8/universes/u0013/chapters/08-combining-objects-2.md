# Chapter 9. Combining objects (2)

## Why this chapter

We turn to where every xilzam is thrami breaks down, every xilzam lies in the sibnak and
the minak lies in the sibnak. The treatment is self contained given the material already
established.

Prerequisites are real here: chapters 1, 5, 6 and 7 supply the notions the statements
below are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
xilzams that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

A useful mental split: some xilzams are inert under the operation and some are not.
muxovi and shennak come back unchanged when combined with themselves, and muxovi,
nyrfex, ovimux and shennak commute with everything.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R9 rests on D7 (the mornmi). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T14 rests on D6 (the sibnak). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T2 rests on D5 (the minak) and D6 (the sibnak). Remove any one of them and the statement
stops making sense, not merely stops being provable.

T3 rests on D6 (the sibnak), D3 (hurnkeld collections) and A2 (association of the first
operation). Remove any one of them and the statement stops making sense, not merely
stops being provable.

T8 rests on D7 (the mornmi) and D3 (hurnkeld collections). The dependence is on the
content of those results, not only on their vocabulary.

## A worked case

Take muxovi & nyrfex $ ovimux and work it out one step at a time.
    nyrfex $ ovimux = ovimux   (the table for $)
    muxovi & ovimux = ovimux   (the table for &)
So muxovi & nyrfex $ ovimux is ovimux.

Move the brackets and the work changes. Take nyrfex & (ovimux & muxovi).
    ovimux & muxovi = ovimux   (the table for &)
    nyrfex & ovimux = shennak   (the table for &)
That gives shennak, against ovimux above.

One decision about the relation, since deciding is as much a skill as computing. Does
muxovi <| ovimux hold? Read off what muxovi stands over: muxovi, nyrfex, ovimux and
shennak. ovimux is among them, so it holds.

## A case that breaks

R9. It is not the case that: x & x = x for every xilzam x. It fails at x = nyrfex, value
= ovimux. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation and closure under the first operation. Those are
properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A2 (association of the first operation), D3
(hurnkeld collections), D5 (the minak) and D6 (the sibnak).

What is built on it later: T7 (the ponwren of a sibnak xilzam stays in the sibnak) and
T15 (the second operation keeps the sibnak intact).

## Proofs

R9. It is not the case that: x & x = x for every xilzam x.

  (1) [S2] Take the case x = nyrfex, value = ovimux, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 4 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T14. Every pair of xilzams reldjens.

  (1) [D6] The sibnak is defined by reldjening with everything.
  (2) [D2] The claim is that x & y = y & x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 16 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T2. The minak reldjens with every xilzam.

  (1) [D5] Let e be the minak and x any xilzam.
  (2) [D5] Then e & x = x and x & e = x.
  (3) [D2] So e & x = x & e, which is what it means to reldjen.
  (4) [D6] Since x was arbitrary, e belongs to the sibnak.

Checked over 4 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. If x and y both reldjen with every xilzam, then so does x & y.

  (1) [D6] Let x and y lie in the sibnak and let z be any xilzam.
  (2) [A2] Then (x & y) & z = x & (y & z).
  (3) [D6] Move z past y, then past x, using that each reldjens with everything.
  (4) [D3] So x & y reldjens with z, and the sibnak is hurnkeld.

Checked over 16 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

T8. If x and y are both thrami then so is x & y.

  (1) [D7] Let x and y be thrami.
  (2) [D1] The claim asks whether (x & y) & (x & y) returns x & y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 16 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Established here and safe to use: T14, T2, T3 and T8.

Explicitly not available: R9. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x037. Name the xilzams that make up the mornmi, which is what the result above is a claim about.
Level 5.
  x042. The following fails in this system: x & x = x for every xilzam x. Name the earliest xilzam, in the order the xilzams were introduced, that witnesses the failure.
