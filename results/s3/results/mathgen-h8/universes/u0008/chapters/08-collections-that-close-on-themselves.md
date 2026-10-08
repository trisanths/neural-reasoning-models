# Chapter 9. Collections that close on themselves

## Why this chapter

We turn to the korropal of a ovimorn, a ovimorn has only one oviovi and the wrenmi of a
ovimorn is vexjen. The treatment is self contained given the material already
established.

Nothing here stands on its own. The arguments lean on chapters 1, 5, 7 and 8, and a
reader who has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
ovimorns that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D12. The korropal of a ovimorn. The korropal of a ovimorn x is the number of ovimorns in
its wrenmi [x].

Worked out for each ovimorn: rastmi to 1; bradri to 5; wrenkorr to 5; tezkeld to 5;
muxvor to 5.

## The shape of it

Picture the wrenmi as what happens when you start with one ovimorn and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 5 ovimorns, that stops. In this system the sizes it stops at are 1 and 5.

The neutral ovimorn rastmi is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 ovimorns the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T3 rests on D11 (the oviovi of a ovimorn), A2 (association of the first operation) and
T1 (the wrenglim is the only one of its kind). Remove any one of them and the statement
stops making sense, not merely stops being provable.

T6 rests on D8 (the wrenmi of a ovimorn) and D3 (vexjen collections). The dependence is
on the content of those results, not only on their vocabulary.

## A worked case

Evaluate (wrenkorr : tezkeld) : bradri. Each line below is one lookup in a table.
    wrenkorr : tezkeld = rastmi   (the table for :)
    rastmi : bradri = bradri   (the table for :)
So (wrenkorr : tezkeld) : bradri is bradri.

A companion case, tezkeld : (bradri : wrenkorr), to show what the brackets are doing.
    bradri : wrenkorr = tezkeld   (the table for :)
    tezkeld : tezkeld = bradri   (the table for :)
That gives bradri, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
wrenkorr :: rastmi hold? Read off what wrenkorr stands over: rastmi, bradri, wrenkorr,
tezkeld and muxvor. rastmi is among them, so it holds.

A second case, this time a wrenmi. Start from rastmi. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is rastmi, so the
korropal of rastmi is 1.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of ovimorns that come back
unchanged from themselves: rastmi. Assuming more of them than that is the mistake to
avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation, closure under the first operation and reversal under
the first operation. Those are properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A2 (association of the first operation), D11 (the oviovi of a ovimorn),
D3 (vexjen collections) and D8 (the wrenmi of a ovimorn).

What is built on it later: D13 (the kajen), T4 (a opaltez ovimorn is its own oviovi), T7
(the wrenmi is contained in every vexjen collection) and T8 (a ovimorn is tarnkorr
exactly when its korropal is one).

## Proofs

T3. For every ovimorn x there is exactly one oviovi of x.

  (1) [D11] Let y and z both be partners of x.
  (2) [A2] Then y = y : (x : z) = (y : x) : z.
  (3) [D11] Both bracketed products collapse to the neutral object.
  (4) So y = z.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T6. For every ovimorn x, the collection [x] is vexjen.

  (1) [D8] [x] is built by taking x and closing under :.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 125 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the korropal of a ovimorn. Later chapters state their results in these
terms and do not restate the definitions.

Established here and safe to use: T3 and T6.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x033. How many ovimorns lie in [bradri]?
  x034. What is the korropal of wrenkorr?
  x035. What is the korropal of tezkeld?
  x036. What is the korropal of muxvor?
Level 5.
  x037. Let z be (tezkeld : muxvor) : rastmi. What is the korropal of z?
  x038. Let z be (tezkeld : muxvor) : bradri. What is the korropal of z?
  x039. Let z be (tezkeld : wrenkorr) : bradri. What is the korropal of z?
  x040. Let z be (tezkeld : muxvor) : wrenkorr. What is the korropal of z?
