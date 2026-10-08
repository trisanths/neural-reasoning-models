# Chapter 8. The relation and what it orders (3)

## Why this chapter

Work through this chapter with the tables in front of you. It covers there is at most
one vexlum, the system has a vexlum and no ovijen pairs exist, and each claim can be
checked by hand.

Prerequisites are real here: chapters 3 and 6 supply the notions the statements below
are phrased in.

The standard of proof here is exhaustion. A universal claim about vashumbs covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

Think of %% as pointing downhill. The brasib of a vashumb is everything downhill of it,
and those shadows here have sizes 1, 2, 3, 4 and 5.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T6 rests on D8 (a vexlum) and A8 (antisymmetry of the relation). The dependence is on
the content of those results, not only on their vocabulary.

T7 rests on D8 (a vexlum) and A10 (comparability of every pair). Remove any one of them
and the statement stops making sense, not merely stops being provable.

T8 rests on D11 (ovijen pairs) and A8 (antisymmetry of the relation). Remove any one of
them and the statement stops making sense, not merely stops being provable.

## A worked case

Take (glimsib ? korrvex) ? (hobtez ? korrdri) and work it out one step at a time.
    glimsib ? korrvex = glimsib   (the table for ?)
    hobtez ? korrdri = korrvex   (the table for ?)
    glimsib ? korrvex = glimsib   (the table for ?)
The expression comes to glimsib.

Bracketing is not cosmetic, so here is korrvex ? (hobtez ? glimsib) for contrast.
    hobtez ? glimsib = keldclo   (the table for ?)
    korrvex ? keldclo = korrvex   (the table for ?)
That gives korrvex, against glimsib above.

One decision about the relation, since deciding is as much a skill as computing. Does
korrdri %% hobtez hold? Read off what korrdri stands over: korrvex, keldclo, glimsib,
hobtez and korrdri. hobtez is among them, so it holds.

## A case that breaks

A quick guard against a common slip: hobtez ? glimsib is keldclo while glimsib ? hobtez
is korrvex. Order is not decoration in this system.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by antisymmetry of the relation and comparability of every pair. A
system without them is not a system where these results are harder to prove; it is a
system where they are false.

That is not a rhetorical caution. Take the same 5 objects, the same symbols, and a
different table, and T6 and T8 stop holding. The notation survives the substitution and
the mathematics does not.

## Neighbouring results

Read alongside A10 (comparability of every pair), A8 (antisymmetry of the relation), D11
(ovijen pairs) and D8 (a vexlum).

## Proofs

T6. No two distinct vashumbs can both be vexlums.

  (1) [D8] Let f and h both be floors.
  (2) [D8] Then f %% h, since h is any object, and h %% f likewise.
  (3) [A8] Antisymmetry forces f = h.

Checked over 25 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T7. Some vashumb vexlums the whole system.

  (1) [A10] Every pair is comparable, so the relation orders the objects into a line.
  (2) [D8] The claim is that the line has a bottom.
  (3) The carrier is finite, so the search over candidates terminates.

Checked over 25 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T8. No two distinct vashumbs lie in each other's brasib.

  (1) [D11] Suppose x and y form a tight pair.
  (2) [A8] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

The results now available are T6, T7 and T8, each settled by exhaustive check rather
than by argument from analogy.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x052. Name the vashumbs that make up the vexlum, which is what the result above is a claim about.
