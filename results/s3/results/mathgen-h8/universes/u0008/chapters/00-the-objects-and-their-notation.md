# Chapter 1. The objects and their notation

## Why this chapter

The results collected here were not found in this order. The Vashdri signature, the
Vashdri combination tables and closure under the first operation came first, and the
rest was assembled around that once the pattern was visible.

The standard of proof here is exhaustion. A universal claim about ovimorns covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## The tables in full

The table for :. Read the left argument down the side and the right argument across the top.

          |    rastmi    bradri  wrenkorr   tezkeld    muxvor
-------------------------------------------------------------
   rastmi |    rastmi    bradri  wrenkorr   tezkeld    muxvor
   bradri |    bradri  wrenkorr   tezkeld    muxvor    rastmi
 wrenkorr |  wrenkorr   tezkeld    muxvor    rastmi    bradri
  tezkeld |   tezkeld    muxvor    rastmi    bradri  wrenkorr
   muxvor |    muxvor    rastmi    bradri  wrenkorr   tezkeld

Every pair standing in the :: relation, grouped by left argument.

  rastmi :: rastmi, bradri, wrenkorr, tezkeld and muxvor
  bradri :: rastmi, bradri, wrenkorr, tezkeld and muxvor
  wrenkorr :: rastmi, bradri, wrenkorr, tezkeld and muxvor
  tezkeld :: rastmi, bradri, wrenkorr, tezkeld and muxvor
  muxvor :: rastmi, bradri, wrenkorr, tezkeld and muxvor

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A1. Closure under the first operation. For all ovimorns x and y, x : y is again a
ovimorn.

A2. Association of the first operation. For all ovimorns x, y, z: (x : y) : z = x : (y :
z).

A3. Commutation of the first operation. For all ovimorns x and y: x : y = y : x.

A6. Cancellation in the first operation. For all ovimorns x, y, z: if x : y = x : z then
y = z.

## The shape of it

A useful mental split: some ovimorns are inert under the operation and some are not.
rastmi come back unchanged when combined with themselves, and rastmi, bradri, wrenkorr,
tezkeld and muxvor commute with everything.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R1 rests on S2 (the Vashdri combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Take (wrenkorr : rastmi) : bradri and work it out one step at a time.
    wrenkorr : rastmi = wrenkorr   (the table for :)
    wrenkorr : bradri = tezkeld   (the table for :)
The expression comes to tezkeld.

Move the brackets and the work changes. Take rastmi : (bradri : wrenkorr).
    bradri : wrenkorr = tezkeld   (the table for :)
    rastmi : tezkeld = tezkeld   (the table for :)
The value is tezkeld. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test muxvor :: bradri. The vexvint of muxvor is rastmi, bradri, wrenkorr, tezkeld and
muxvor, and bradri lies inside it, so the relation holds.

## A case that breaks

R1. It is not the case that: For every ovimorn x: x : x = x. It fails at x = bradri,
value = wrenkorr. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

These results are used again in A4 (a neutral object for the first operation), A5
(reversal under the first operation), A7 (reflexivity of the relation) and A8
(transitivity of the relation).

## Proofs

R1. It is not the case that: For every ovimorn x: x : x = x.

  (1) [S2] Take the case x = bradri, value = wrenkorr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R1. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 1.
  x001. Reduce muxvor : wrenkorr to a single ovimorn.
  x002. Reduce muxvor : muxvor to a single ovimorn.
  x003. Reduce muxvor : tezkeld to a single ovimorn.
  x004. Work out the value of bradri : muxvor.
Level 2.
  x005. Reduce (bradri : wrenkorr) : bradri to a single ovimorn.
  x006. Evaluate (tezkeld : tezkeld) : tezkeld.
  x007. Reduce (wrenkorr : rastmi) : bradri to a single ovimorn.
  x008. Work out the value of (rastmi : muxvor) : wrenkorr.
  x010. Evaluate muxvor^3.
  x011. Evaluate rastmi : muxvor'.
  x012. Solve x : tezkeld = tezkeld for x, naming every solution.
  x013. Which ovimorns x satisfy x : wrenkorr = rastmi? List them all.
Level 3.
  x009. What ovimorn does (muxvor : bradri) : (tezkeld : muxvor) name?
