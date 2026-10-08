# Chapter 9. Combining objects (3)

## Why this chapter

The practical content of this chapter is where every lumpon is pontez breaks down, the
opalkeld is lumvex and every lumpon lies in the glimfex. It is the part that shows up in
use.

Nothing here stands on its own. The arguments lean on chapters 1, 4, 5 and 6, and a
reader who has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over lumpons, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

Two questions sort the lumpons quickly. Does combining a lumpon with itself change it?
For glimtez it does not. Does it matter which side it goes on? For glimtez, glimkorr,
nakkorr, duthwren, kaka and mornhob it does not.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R4 rests on D7 (the opalkeld). The dependence is on the content of those results, not
only on their vocabulary.

T11 rests on D7 (the opalkeld) and D3 (lumvex collections). The dependence is on the
content of those results, not only on their vocabulary.

T17 rests on D6 (the glimfex). The dependence is on the content of those results, not
only on their vocabulary.

T2 rests on D5 (the tuka) and D6 (the glimfex). The dependence is on the content of
those results, not only on their vocabulary.

T5 rests on D6 (the glimfex), D3 (lumvex collections) and A2 (association of the first
operation). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Take (duthwren - mornhob) - glimtez and work it out one step at a time.
    duthwren - mornhob = nakkorr   (the table for -)
    nakkorr - glimtez = nakkorr   (the table for -)
The expression comes to nakkorr.

A companion case, mornhob - (glimtez - duthwren), to show what the brackets are doing.
    glimtez - duthwren = duthwren   (the table for -)
    mornhob - duthwren = nakkorr   (the table for -)
The value is nakkorr. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test mornhob >- duthwren. The yukglim of mornhob is mornhob, and duthwren lies outside
it, so the relation fails.

## A case that breaks

R4. It is not the case that: x - x = x for every lumpon x. The case that settles it: x =
glimkorr, value = nakkorr. Anyone carrying this claim over from a more familiar system
will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation and closure under the first operation. Those are
properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A2 (association of the first operation), D3 (lumvex collections), D5 (the
tuka) and D6 (the glimfex).

These results are used again in T10 (the umbquil of a glimfex lumpon stays in the
glimfex).

## Proofs

R4. It is not the case that: x - x = x for every lumpon x.

  (1) [S2] Take the case x = glimkorr, value = nakkorr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T11. If x and y are both pontez then so is x - y.

  (1) [D7] Let x and y be pontez.
  (2) [D1] The claim asks whether (x - y) - (x - y) returns x - y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 36 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

T17. Every pair of lumpons vorhurns.

  (1) [D6] The glimfex is defined by vorhurning with everything.
  (2) [D2] The claim is that x - y = y - x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T2. The tuka vorhurns with every lumpon.

  (1) [D5] Let e be the tuka and x any lumpon.
  (2) [D5] Then e - x = x and x - e = x.
  (3) [D2] So e - x = x - e, which is what it means to vorhurn.
  (4) [D6] Since x was arbitrary, e belongs to the glimfex.

Checked over 6 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T5. If x and y both vorhurn with every lumpon, then so does x - y.

  (1) [D6] Let x and y lie in the glimfex and let z be any lumpon.
  (2) [A2] Then (x - y) - z = x - (y - z).
  (3) [D6] Move z past y, then past x, using that each vorhurns with everything.
  (4) [D3] So x - y vorhurns with z, and the glimfex is lumvex.

Checked over 36 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

The results now available are T11, T17, T2 and T5, each settled by exhaustive check
rather than by argument from analogy.

Explicitly not available: R4. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x054. This result is about the glimfex. List every lumpon in it.
  x057. Name the lumpons that make up the opalkeld, which is what the result above is a claim about.
