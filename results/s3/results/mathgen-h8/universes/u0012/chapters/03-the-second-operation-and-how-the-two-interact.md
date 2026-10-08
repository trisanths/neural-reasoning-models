# Chapter 4. The second operation and how the two interact

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through self combination under the
second operation, closure under the second operation and association of the second
operation.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about glimyuks covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A10. Self combination under the second operation. For every glimyuk x: x : x = x.

A6. Closure under the second operation. For all glimyuks x and y, x : y is again a
glimyuk.

A7. Association of the second operation. For all glimyuks x, y, z: (x : y) : z = x : (y
: z).

A8. Commutation of the second operation. For all glimyuks x and y: x : y = y : x.

A9. A neutral object for the second operation. There is a glimyuk kanyr with kanyr : x =
x for every x.

## The shape of it

The interesting content of a two operation system sits in the gap between them: which
one distributes over which, and which glimyuks are fixed by both.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R4 rests on S2 (the Nyrduth combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R5 rests on S2 (the Nyrduth combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Take (ovifal & kanyr) & (kamorn & muxreld) and work it out one step at a time.
    ovifal & kanyr = kanyr   (the table for &)
    kamorn & muxreld = quilisk   (the table for &)
    kanyr & quilisk = kanyr   (the table for &)
The expression comes to kanyr.

Bracketing is not cosmetic, so here is kanyr & (kamorn & ovifal) for contrast.
    kamorn & ovifal = kanyr   (the table for &)
    kanyr & kanyr = kanyr   (the table for &)
The value is kanyr. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test muxreld >- kanyr. The mornclo of muxreld is muxreld, quilisk, ovifal and kanyr, and
kanyr lies inside it, so the relation holds.

## A case that breaks

R4. It is not the case that: For all glimyuks x, y, z: x : (y & z) = (x : y) & (x : z),
and the same on the right. The case that settles it: x = kamorn, y = kamorn, z = kamorn,
left = kamorn, right = muxreld. Anyone carrying this claim over from a more familiar
system will be wrong here, and wrong in a way that propagates.

R5. It is not the case that: For all glimyuks x and y: x & (x : y) = x and x : (x & y) =
x. The case that settles it: x = kamorn, y = kamorn, value = muxreld. Anyone carrying
this claim over from a more familiar system will be wrong here, and wrong in a way that
propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: S2 (the Nyrduth combination tables).

These results are used again in T15 (the second operation keeps the fexsol intact).

## Proofs

R4. It is not the case that: For all glimyuks x, y, z: x : (y & z) = (x : y) & (x : z), and the same on the right.

  (1) [S2] Take the case x = kamorn, y = kamorn, z = kamorn, left = kamorn, right = muxreld, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R5. It is not the case that: For all glimyuks x and y: x & (x : y) = x and x : (x & y) = x.

  (1) [S2] Take the case x = kamorn, y = kamorn, value = muxreld, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R4 and R5. These were tested and failed, and the failing cases are
recorded above.

## Exercises

No exercises here. Every question this chapter suggested turned out to be answerable
from the question itself, so all of them were discarded.
