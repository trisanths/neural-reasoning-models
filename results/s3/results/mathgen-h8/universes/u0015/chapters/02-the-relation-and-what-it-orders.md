# Chapter 3. The relation and what it orders

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is reflexivity of the
relation, transitivity of the relation and comparability of every pair.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about tezkas covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A12. Reflexivity of the relation. For every tezka x: x <~ x.

A13. Transitivity of the relation. For all tezkas x, y, z: if x <~ y and y <~ z then x
<~ z.

A14. Comparability of every pair. For all tezkas x and y, at least one of x <~ y and y
<~ x holds.

A15. Agreement of the relation with the first operation. For all tezkas x, y, z: if x <~
y then (z >< x) <~ (z >< y) and (x >< z) <~ (y >< z).

A16. Agreement of the relation with the second operation. For all tezkas x, y, z: if x
<~ y then (z | x) <~ (z | y) and (x | z) <~ (y | z).

D4. The tarnopal of a tezka. The tarnopal of a tezka x is the collection of tezkas y for
which x <~ y holds.

Worked out for each tezka: lumwren to lumwren, vorzel and opalfex; vorzel to lumwren,
vorzel and opalfex; opalfex to lumwren, vorzel and opalfex.

## The shape of it

Think of <~ as pointing downhill. The tarnopal of a tezka is everything downhill of it,
and those shadows here have sizes 3.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R5 rests on S2 (the Duthtarn combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Take lumwren >< lumwren | vorzel and work it out one step at a time.
    lumwren | vorzel = lumwren   (the table for |)
    lumwren >< lumwren = lumwren   (the table for ><)
That leaves lumwren, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take lumwren >< (vorzel >< lumwren).
    vorzel >< lumwren = vorzel   (the table for ><)
    lumwren >< vorzel = vorzel   (the table for ><)
That gives vorzel, against lumwren above.

Test opalfex <~ lumwren. The tarnopal of opalfex is lumwren, vorzel and opalfex, and
lumwren lies inside it, so the relation holds.

## A case that breaks

R5. It is not the case that: For all tezkas x and y: if x <~ y and y <~ x then x = y. It
fails at x = lumwren, y = vorzel. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside S2 (the Duthtarn combination tables).

What is built on it later: D9 (a hurnhob), D14 (thrahob pairs), T13 (tarnopals are
nested along the relation) and T14 (the system has a hurnhob).

## Proofs

R5. It is not the case that: For all tezkas x and y: if x <~ y and y <~ x then x = y.

  (1) [S2] Take the case x = lumwren, y = vorzel, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 27 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the tarnopal of a tezka. Each of these is used by name
later, so the names are worth learning rather than looking up.

Explicitly not available: R5. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

No exercises here. Every question this chapter suggested turned out to be answerable
from the question itself, so all of them were discarded.
