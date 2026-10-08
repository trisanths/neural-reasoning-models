# Chapter 9. Combining objects (3)

## Why this chapter

The results collected here were not found in this order. The nyrpon of a tezka, the
system has a hurnhob and where every tezka is xilvash breaks down came first, and the
rest was assembled around that once the pattern was visible.

Prerequisites are real here: chapters 1, 3, 5, 6 and 7 supply the notions the statements
below are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 3
tezkas that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D8. The nyrpon of a tezka. The nyrpon of a tezka x, written [x], is the smallest qenduth
collection that contains x.

Worked out for each tezka: lumwren to lumwren; vorzel to lumwren, vorzel and opalfex;
opalfex to lumwren, vorzel and opalfex.

## The shape of it

The right picture for nyrpon is a spreading stain rather than a list. Drop one tezka in,
apply the operation to whatever is wet, repeat. The stain here reaches 1 and 3 tezkas
depending on where it started.

Think of <~ as pointing downhill. The tarnopal of a tezka is everything downhill of it,
and those shadows here have sizes 3.

Two questions sort the tezkas quickly. Does combining a tezka with itself change it? For
lumwren it does not. Does it matter which side it goes on? For lumwren, vorzel and
opalfex it does not.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 3 tezkas the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T14 rests on D9 (a hurnhob) and A14 (comparability of every pair). Remove any one of
them and the statement stops making sense, not merely stops being provable.

R6 rests on D7 (the lorngrix). The dependence is on the content of those results, not
only on their vocabulary.

T11 rests on D7 (the lorngrix) and D3 (qenduth collections). The dependence is on the
content of those results, not only on their vocabulary.

T16 rests on D6 (the drilorn). The dependence is on the content of those results, not
only on their vocabulary.

T2 rests on D5 (the yukvex) and D6 (the drilorn). The dependence is on the content of
those results, not only on their vocabulary.

T5 rests on D6 (the drilorn), D3 (qenduth collections) and A2 (association of the first
operation). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Evaluate lumwren >< lumwren | lumwren. Each line below is one lookup in a table.
    lumwren | lumwren = lumwren   (the table for |)
    lumwren >< lumwren = lumwren   (the table for ><)
So lumwren >< lumwren | lumwren is lumwren.

Bracketing is not cosmetic, so here is lumwren >< (lumwren >< lumwren) for contrast.
    lumwren >< lumwren = lumwren   (the table for ><)
    lumwren >< lumwren = lumwren   (the table for ><)
That gives lumwren, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
opalfex <~ opalfex hold? Read off what opalfex stands over: lumwren, vorzel and opalfex.
opalfex is among them, so it holds.

A second case, this time a nyrpon. Start from lumwren. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is lumwren, so the
pyryuk of lumwren is 1.

## A case that breaks

R6. It is not the case that: x >< x = x for every tezka x. The case that settles it: x =
vorzel, value = opalfex. Anyone carrying this claim over from a more familiar system
will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by a neutral object for the first operation, association of the
first operation, closure under the first operation and comparability of every pair. A
system without them is not a system where these results are harder to prove; it is a
system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A14 (comparability of every pair), A2
(association of the first operation), D3 (qenduth collections) and D5 (the yukvex).

What is built on it later: D12 (the pyryuk of a tezka), T6 (the nyrpon of a tezka is
qenduth), T7 (the nyrpon is contained in every qenduth collection) and T10 (the nyrpon
of a drilorn tezka stays in the drilorn).

## Proofs

T14. Some tezka hurnhobs the whole system.

  (1) [A14] Every pair is comparable, so the relation orders the objects into a line.
  (2) [D9] The claim is that the line has a bottom.
  (3) The carrier is finite, so the search over candidates terminates.

Checked over 9 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

R6. It is not the case that: x >< x = x for every tezka x.

  (1) [S2] Take the case x = vorzel, value = opalfex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 3 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T11. If x and y are both xilvash then so is x >< y.

  (1) [D7] Let x and y be xilvash.
  (2) [D1] The claim asks whether (x >< y) >< (x >< y) returns x >< y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 9 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

T16. Every pair of tezkas espanaks.

  (1) [D6] The drilorn is defined by espanaking with everything.
  (2) [D2] The claim is that x >< y = y >< x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 9 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T2. The yukvex espanaks with every tezka.

  (1) [D5] Let e be the yukvex and x any tezka.
  (2) [D5] Then e >< x = x and x >< e = x.
  (3) [D2] So e >< x = x >< e, which is what it means to espanak.
  (4) [D6] Since x was arbitrary, e belongs to the drilorn.

Checked over 3 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T5. If x and y both espanak with every tezka, then so does x >< y.

  (1) [D6] Let x and y lie in the drilorn and let z be any tezka.
  (2) [A2] Then (x >< y) >< z = x >< (y >< z).
  (3) [D6] Move z past y, then past x, using that each espanaks with everything.
  (4) [D3] So x >< y espanaks with z, and the drilorn is qenduth.

Checked over 9 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the nyrpon of a tezka. Later chapters state their results in these terms
and do not restate the definitions.

Established here and safe to use: T14, T11, T16, T2 and T5.

Do not carry forward R6. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x017. List the nyrpon of vorzel.
  x018. Name every tezka in [opalfex].
Level 4.
  x019. Let z be vorzel >< opalfex. List the nyrpon of z.
  x020. Let z be vorzel >< lumwren. List the nyrpon of z.
  x021. Let z be opalfex >< vorzel. List the nyrpon of z.
  x036. This result is about the lorngrix. List every tezka in it.
