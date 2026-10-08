# Chapter 12. The second operation and how the two interact (2)

## Why this chapter

We turn to the second operation keeps the drilorn intact. The treatment is self
contained given the material already established.

Nothing here stands on its own. The arguments lean on chapters 4, 7 and 9, and a reader
who has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over tezkas, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

The interesting content of a two operation system sits in the gap between them: which
one distributes over which, and which tezkas are fixed by both.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 3 tezkas the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T19 rests on D6 (the drilorn), A7 (closure under the second operation) and T5 (the
drilorn is qenduth). Remove any one of them and the statement stops making sense, not
merely stops being provable.

## A worked case

Evaluate (lumwren >< opalfex) >< (opalfex >< lumwren). Each line below is one lookup in
a table.
    lumwren >< opalfex = opalfex   (the table for ><)
    opalfex >< lumwren = opalfex   (the table for ><)
    opalfex >< opalfex = vorzel   (the table for ><)
The expression comes to vorzel.

Bracketing is not cosmetic, so here is opalfex >< (opalfex >< lumwren) for contrast.
    opalfex >< lumwren = opalfex   (the table for ><)
    opalfex >< opalfex = vorzel   (the table for ><)
That gives vorzel, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
lumwren <~ opalfex hold? Read off what lumwren stands over: lumwren, vorzel and opalfex.
opalfex is among them, so it holds.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of association of the first operation,
closure under the first operation and closure under the second operation. Those are
properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A7 (closure under the second operation), D6 (the
drilorn) and T5 (the drilorn is qenduth).

## Proofs

T19. If x and y lie in the drilorn then so does x | y.

  (1) [T5] The drilorn is already qenduth under ><.
  (2) [A7] The second operation is defined on every pair.
  (3) [D6] The claim is that | respects the drilorn as well.

Checked over 9 cases: every ordered pair from the core. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

The results now available are T19, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

This chapter carries no exercises. Nothing in it can be asked about in a way that could
not be answered without reading it, and an exercise like that is worse than none.
