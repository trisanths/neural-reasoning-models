# Chapter 11. Collections that close on themselves (2)

## Why this chapter

Work through this chapter with the tables in front of you. It covers the nyrvex, where
the migel divides the number of glimyuks breaks down and where some glimyuk reaches
every other breaks down, and each claim can be checked by hand.

Prerequisites are real here: chapters 5, 8 and 10 supply the notions the statements
below are phrased in.

One habit to adopt: when a statement below quantifies over glimyuks, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D12. The nyrvex. The nyrvex of the system is the collection of glimyuks whose migel is
largest.

In this system that picks out kamorn, which is 1 of the 6 glimyuks.

## The shape of it

Picture the xilvor as what happens when you start with one glimyuk and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 6 glimyuks, that stops. In this system the sizes it stops at are 1, 2, 3 and 5.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R6 rests on D11 (the migel of a glimyuk) and T4 (the xilvor of a glimyuk is tuopal). The
dependence is on the content of those results, not only on their vocabulary.

R8 rests on D8 (the xilvor of a glimyuk) and D11 (the migel of a glimyuk). The
dependence is on the content of those results, not only on their vocabulary.

T5 rests on D8 (the xilvor of a glimyuk) and T4 (the xilvor of a glimyuk is tuopal). The
dependence is on the content of those results, not only on their vocabulary.

T6 rests on D1 (sibtez glimyuks), D11 (the migel of a glimyuk) and T4 (the xilvor of a
glimyuk is tuopal). Remove any one of them and the statement stops making sense, not
merely stops being provable.

## A worked case

Here is muxreld & quilisk : ovifal, reduced without skipping anything.
    quilisk : ovifal = quilisk   (the table for :)
    muxreld & quilisk = kanyr   (the table for &)
So muxreld & quilisk : ovifal is kanyr.

Move the brackets and the work changes. Take quilisk & (ovifal & muxreld).
    ovifal & muxreld = kanyr   (the table for &)
    quilisk & kanyr = kanyr   (the table for &)
The value is kanyr. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
muxreld >- muxreld hold? Read off what muxreld stands over: muxreld, quilisk, ovifal and
kanyr. muxreld is among them, so it holds.

## A case that breaks

R6. It is not the case that: For every glimyuk x, the migel of x divides 6. It fails at
x = kamorn, reach = 5, size = 6. One case is enough, and this is the earliest one.

R8. It is not the case that: There is a glimyuk whose xilvor is the whole system. The
case that settles it: largest_span = 5, size = 6. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: D1 (sibtez glimyuks), D11 (the migel of a
glimyuk), D8 (the xilvor of a glimyuk) and T4 (the xilvor of a glimyuk is tuopal).

## Proofs

R6. It is not the case that: For every glimyuk x, the migel of x divides 6.

  (1) [S2] Take the case x = kamorn, reach = 5, size = 6, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

R8. It is not the case that: There is a glimyuk whose xilvor is the whole system.

  (1) [S2] Take the case largest_span = 5, size = 6, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T5. If S is tuopal and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 90 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T6. x & x = x holds if and only if [x] contains x alone.

  (1) [D1] If x & x = x then {x} is already closed under &.
  (2) [T4] So [x] = {x} and the migel is one.
  (3) [D11] Conversely a span of one object must contain x & x, which is then x.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the nyrvex. Later chapters state their results in these terms and do not
restate the definitions.

The results now available are T5 and T6, each settled by exhaustive check rather than by
argument from analogy.

Do not carry forward R6 and R8. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x042. List every glimyuk in the nyrvex.
  x043. What is the largest migel any glimyuk has?
Level 5.
  x044. The following fails in this system: For every glimyuk x, the migel of x divides 6. Name the earliest glimyuk, in the order the glimyuks were introduced, that witnesses the failure.
