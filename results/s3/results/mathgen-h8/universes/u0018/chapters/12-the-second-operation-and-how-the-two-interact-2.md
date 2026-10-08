# Chapter 13. The second operation and how the two interact (2)

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through the second operation keeps the
tezka intact.

Nothing here stands on its own. The arguments lean on chapters 4, 7 and 10, and a reader
who has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
naksols that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

With two operations the question stops being what each does and becomes how they
interfere. <> binds tighter, so the interference shows up whenever a bracket is left
off.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T19 rests on D6 (the tezka), A7 (closure under the second operation) and T5 (the tezka
is hobreld). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Here is vexnak % glimzam <> reldxil, reduced without skipping anything.
    glimzam <> reldxil = reldxil   (the table for <>)
    vexnak % reldxil = wrenpyr   (the table for %)
That leaves wrenpyr, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take glimzam % (reldxil % vexnak).
    reldxil % vexnak = wrenpyr   (the table for %)
    glimzam % wrenpyr = glimzam   (the table for %)
That gives glimzam, against wrenpyr above.

One decision about the relation, since deciding is as much a skill as computing. Does
vexnak >- vexlorn hold? Read off what vexnak stands over: vexnak, glimzam, reldxil and
pyrxil. vexlorn is not among them, so it fails.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of naksols that come back
unchanged from themselves: wrenpyr. Assuming more of them than that is the mistake to
avoid.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of association of the first operation,
closure under the first operation and closure under the second operation. Those are
properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A7 (closure under the second operation), D6 (the tezka) and T5 (the tezka
is hobreld).

## Proofs

T19. If x and y lie in the tezka then so does x <> y.

  (1) [T5] The tezka is already hobreld under %.
  (2) [A7] The second operation is defined on every pair.
  (3) [D6] The claim is that <> respects the tezka as well.

Checked over 36 cases: every ordered pair from the core. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Established here and safe to use: T19.

## Exercises

This chapter carries no exercises. Nothing in it can be asked about in a way that could
not be answered without reading it, and an exercise like that is worse than none.
