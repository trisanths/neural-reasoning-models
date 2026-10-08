# Chapter 8. The relation and what it orders (3)

## Why this chapter

Work through this chapter with the tables in front of you. It covers there is at most
one drisol, the system has a drisol and no aztgel pairs exist, and each claim can be
checked by hand.

Nothing here stands on its own. The arguments lean on chapters 3 and 6, and a reader who
has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over shenopals, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

Think of :: as pointing downhill. The muxsib of a shenopal is everything downhill of it,
and those shadows here have sizes 1, 2, 3, 4 and 5.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T6 rests on D8 (a drisol) and A8 (antisymmetry of the relation). The dependence is on
the content of those results, not only on their vocabulary.

T7 rests on D8 (a drisol) and A10 (comparability of every pair). The dependence is on
the content of those results, not only on their vocabulary.

T8 rests on D11 (aztgel pairs) and A8 (antisymmetry of the relation). The dependence is
on the content of those results, not only on their vocabulary.

## A worked case

Evaluate (opallorn % qenthra) % (pontu % vorpon). Each line below is one lookup in a
table.
    opallorn % qenthra = opallorn   (the table for %)
    pontu % vorpon = qenthra   (the table for %)
    opallorn % qenthra = opallorn   (the table for %)
That leaves opallorn, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is qenthra % (pontu % opallorn) for contrast.
    pontu % opallorn = pontu   (the table for %)
    qenthra % pontu = opallorn   (the table for %)
The value is opallorn. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test qenthra :: vorpon. The muxsib of qenthra is qenthra, grixlum, vorpon and pontu, and
vorpon lies inside it, so the relation holds.

## A case that breaks

A quick guard against a common slip: qenthra % pontu is opallorn while pontu % qenthra
is vorpon. Order is not decoration in this system.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by antisymmetry of the relation and comparability of every pair. A
system without them is not a system where these results are harder to prove; it is a
system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A10 (comparability of every pair), A8 (antisymmetry of the relation), D11
(aztgel pairs) and D8 (a drisol).

## Proofs

T6. No two distinct shenopals can both be drisols.

  (1) [D8] Let f and h both be floors.
  (2) [D8] Then f :: h, since h is any object, and h :: f likewise.
  (3) [A8] Antisymmetry forces f = h.

Checked over 25 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T7. Some shenopal drisols the whole system.

  (1) [A10] Every pair is comparable, so the relation orders the objects into a line.
  (2) [D8] The claim is that the line has a bottom.
  (3) The carrier is finite, so the search over candidates terminates.

Checked over 25 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T8. No two distinct shenopals lie in each other's muxsib.

  (1) [D11] Suppose x and y form a tight pair.
  (2) [A8] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

The results now available are T6, T7 and T8, each settled by exhaustive check rather
than by argument from analogy.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x057. Name the shenopals that make up the drisol, which is what the result above is a claim about.
