# Chapter 10. Collections that close on themselves

## Why this chapter

We turn to the migel of a glimyuk, the xilvor of a glimyuk is tuopal and the xilvor of a
fexsol glimyuk stays in the fexsol. The treatment is self contained given the material
already established.

Nothing here stands on its own. The arguments lean on chapters 6, 7, 8 and 9, and a
reader who has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
glimyuks that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D11. The migel of a glimyuk. The migel of a glimyuk x is the number of glimyuks in its
xilvor [x].

Worked out for each glimyuk: fexvash to 1; kamorn to 5; muxreld to 3; quilisk to 2;
ovifal to 2; kanyr to 1.

## The shape of it

Picture the xilvor as what happens when you start with one glimyuk and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 6 glimyuks, that stops. In this system the sizes it stops at are 1, 2, 3 and 5.

Two questions sort the glimyuks quickly. Does combining a glimyuk with itself change it?
For fexvash and kanyr it does not. Does it matter which side it goes on? For fexvash,
kamorn, muxreld, quilisk, ovifal and kanyr it does not.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 glimyuks the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T4 rests on D8 (the xilvor of a glimyuk) and D3 (tuopal collections). The dependence is
on the content of those results, not only on their vocabulary.

T7 rests on D8 (the xilvor of a glimyuk), D6 (the fexsol) and T3 (the fexsol is tuopal).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

## A worked case

Evaluate (kanyr & ovifal) & (muxreld & kamorn). Each line below is one lookup in a
table.
    kanyr & ovifal = kanyr   (the table for &)
    muxreld & kamorn = quilisk   (the table for &)
    kanyr & quilisk = kanyr   (the table for &)
That leaves kanyr, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take ovifal & (muxreld & kanyr).
    muxreld & kanyr = kanyr   (the table for &)
    ovifal & kanyr = kanyr   (the table for &)
That gives kanyr, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test kanyr >- muxreld. The mornclo of kanyr is kanyr, and muxreld lies outside it, so
the relation fails.

A second case, this time a xilvor. Start from quilisk. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is quilisk and kanyr,
so the migel of quilisk is 2.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by association of the first operation and closure under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: D3 (tuopal collections), D6 (the fexsol), D8
(the xilvor of a glimyuk) and T3 (the fexsol is tuopal).

What is built on it later: D12 (the nyrvex), T5 (the xilvor is contained in every tuopal
collection), T6 (a glimyuk is sibtez exactly when its migel is one) and R6 (where the
migel divides the number of glimyuks breaks down).

## Proofs

T4. For every glimyuk x, the collection [x] is tuopal.

  (1) [D8] [x] is built by taking x and closing under &.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 216 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

T7. If x lies in the fexsol then every glimyuk of [x] lies in the fexsol.

  (1) [T3] The fexsol is tuopal.
  (2) [D8] [x] is the smallest tuopal collection containing x.
  (3) A smallest such collection sits inside any other, and the fexsol is one.

Checked over 36 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the migel of a glimyuk. Later chapters state their results in these terms
and do not restate the definitions.

The results now available are T4 and T7, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x034. What is the migel of kamorn?
  x035. How many glimyuks lie in [muxreld]?
  x036. How many glimyuks lie in [quilisk]?
  x037. What is the migel of ovifal?
  x038. How many glimyuks lie in [kanyr]?
Level 5.
  x039. Let z be kamorn & kamorn : kanyr. What is the migel of z?
  x040. Let z be kanyr & muxreld : fexvash. What is the migel of z?
  x041. Let z be kamorn & kamorn : quilisk. What is the migel of z?
