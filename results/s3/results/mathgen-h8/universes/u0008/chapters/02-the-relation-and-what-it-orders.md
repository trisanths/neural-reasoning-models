# Chapter 3. The relation and what it orders

## Why this chapter

So far the ovimorns have been objects to be pushed around. This chapter starts asking
what they are like. We take up agreement of the relation with the first operation,
reflexivity of the relation and transitivity of the relation.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about ovimorns covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A10. Agreement of the relation with the first operation. For all ovimorns x, y, z: if x
:: y then (z : x) :: (z : y) and (x : z) :: (y : z).

A7. Reflexivity of the relation. For every ovimorn x: x :: x.

A8. Transitivity of the relation. For all ovimorns x, y, z: if x :: y and y :: z then x
:: z.

A9. Comparability of every pair. For all ovimorns x and y, at least one of x :: y and y
:: x holds.

D4. The vexvint of a ovimorn. The vexvint of a ovimorn x is the collection of ovimorns y
for which x :: y holds.

Worked out for each ovimorn: rastmi to rastmi, bradri, wrenkorr, tezkeld and muxvor;
bradri to rastmi, bradri, wrenkorr, tezkeld and muxvor; wrenkorr to rastmi, bradri,
wrenkorr, tezkeld and muxvor; tezkeld to rastmi, bradri, wrenkorr, tezkeld and muxvor;
muxvor to rastmi, bradri, wrenkorr, tezkeld and muxvor.

## The shape of it

The relation is easiest to see as a height. Each ovimorn casts a vexvint over what it
governs, and the sizes of those shadows here are 5. Sizes repeat, so the objects do not
line up in single file.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R3 rests on S2 (the Vashdri combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take (tezkeld : rastmi) : muxvor and work it out one step at a time.
    tezkeld : rastmi = tezkeld   (the table for :)
    tezkeld : muxvor = wrenkorr   (the table for :)
The expression comes to wrenkorr.

Bracketing is not cosmetic, so here is rastmi : (muxvor : tezkeld) for contrast.
    muxvor : tezkeld = wrenkorr   (the table for :)
    rastmi : wrenkorr = wrenkorr   (the table for :)
The value is wrenkorr. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
muxvor :: wrenkorr hold? Read off what muxvor stands over: rastmi, bradri, wrenkorr,
tezkeld and muxvor. wrenkorr is among them, so it holds.

## A case that breaks

R3. It is not the case that: For all ovimorns x and y: if x :: y and y :: x then x = y.
The case that settles it: x = rastmi, y = bradri. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: S2 (the Vashdri combination tables).

What is built on it later: D9 (a wrenvor), D14 (duthlum pairs), T13 (vexvints are nested
along the relation) and T14 (the system has a wrenvor).

## Proofs

R3. It is not the case that: For all ovimorns x and y: if x :: y and y :: x then x = y.

  (1) [S2] Take the case x = rastmi, y = bradri, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the vexvint of a ovimorn. Later chapters state their results in these
terms and do not restate the definitions.

Do not carry forward R3. These were tested and failed, and the failing cases are
recorded above.

## Exercises

This chapter carries no exercises. Nothing in it can be asked about in a way that could
not be answered without reading it, and an exercise like that is worse than none.
