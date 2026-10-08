# Chapter 1. The objects and their notation

## Why this chapter

What follows was pieced together backwards. The last item of it, the Opalopal signature,
the Opalopal combination tables and closure under the first operation, was noticed
before anyone had a reason to expect it.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
xilzams that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## The tables in full

The table for &. Read the left argument down the side and the right argument across the top.

         |   muxovi   nyrfex   ovimux  shennak
----------------------------------------------
  muxovi |   muxovi   nyrfex   ovimux  shennak
  nyrfex |   nyrfex   ovimux  shennak  shennak
  ovimux |   ovimux  shennak  shennak  shennak
 shennak |  shennak  shennak  shennak  shennak

The table for $. Read the left argument down the side and the right argument across the top.

         |   muxovi   nyrfex   ovimux  shennak
----------------------------------------------
  muxovi |   muxovi   nyrfex   ovimux  shennak
  nyrfex |   muxovi   nyrfex   ovimux  shennak
  ovimux |   muxovi   nyrfex   ovimux  shennak
 shennak |   muxovi   nyrfex   ovimux  shennak

Every pair standing in the <| relation, grouped by left argument.

  muxovi <| muxovi, nyrfex, ovimux and shennak
  nyrfex <| nyrfex, ovimux and shennak
  ovimux <| ovimux and shennak
  shennak <| shennak

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A1. Closure under the first operation. For all xilzams x and y, x & y is again a xilzam.

A2. Association of the first operation. For all xilzams x, y, z: (x & y) & z = x & (y &
z).

A3. Commutation of the first operation. For all xilzams x and y: x & y = y & x.

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

R2 rests on S2 (the Opalopal combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R3 rests on S2 (the Opalopal combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Here is shennak & ovimux $ nyrfex, reduced without skipping anything.
    ovimux $ nyrfex = nyrfex   (the table for $)
    shennak & nyrfex = shennak   (the table for &)
That leaves shennak, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is ovimux & (nyrfex & shennak) for contrast.
    nyrfex & shennak = shennak   (the table for &)
    ovimux & shennak = shennak   (the table for &)
That gives shennak, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
nyrfex <| ovimux hold? Read off what nyrfex stands over: nyrfex, ovimux and shennak.
ovimux is among them, so it holds.

## A case that breaks

R2. It is not the case that: For every xilzam x: x & x = x. It fails at x = nyrfex,
value = ovimux. One case is enough, and this is the earliest one.

R3. It is not the case that: For all xilzams x, y, z: if x & y = x & z then y = z. The
case that settles it: x = nyrfex, y = ovimux, z = shennak. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

What is built on it later: A4 (a neutral object for the first operation), A5 (an
absorbing object for the first operation), A6 (closure under the second operation) and
A7 (association of the second operation).

## Proofs

R2. It is not the case that: For every xilzam x: x & x = x.

  (1) [S2] Take the case x = nyrfex, value = ovimux, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R3. It is not the case that: For all xilzams x, y, z: if x & y = x & z then y = z.

  (1) [S2] Take the case x = nyrfex, y = ovimux, z = shennak, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R2 and R3. A later argument that quietly assumes one of these
is wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 1.
  x001. Evaluate nyrfex & nyrfex.
  x002. Work out the value of nyrfex & ovimux.
Level 2.
  x003. Evaluate (nyrfex & ovimux) & nyrfex.
  x004. Evaluate ovimux & ovimux $ ovimux.
  x005. Evaluate nyrfex^2.
  x006. What is nyrfex combined with itself 3 times under &?
  x007. What is ovimux combined with itself 3 times under &?
  x008. Solve x & shennak = shennak for x, naming every solution.
Level 3.
  x009. Evaluate ovimux & nyrfex $ nyrfex, minding which operation binds tighter.
Level 5.
  x011. The following fails in this system: For every xilzam x: x & x = x. Name the earliest xilzam, in the order the xilzams were introduced, that witnesses the failure.
  x012. The following fails in this system: For all xilzams x, y, z: if x & y = x & z then y = z. Name the earliest xilzam, in the order the xilzams were introduced, that witnesses the failure.
