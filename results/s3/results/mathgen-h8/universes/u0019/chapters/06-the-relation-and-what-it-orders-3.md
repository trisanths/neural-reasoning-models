# Chapter 7. The relation and what it orders (3)

## Why this chapter

So far the opalmis have been objects to be pushed around. This chapter starts asking
what they are like. We take up the nakyuk of a opalmi, there is at most one hobsol and
no grixhob pairs exist.

Prerequisites are real here: chapters 3 and 5 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over opalmis, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D8. The nakyuk of a opalmi. The nakyuk of a opalmi x, written [x], is the smallest
brarast collection that contains x.

Worked out for each opalmi: keldsib to keldsib; duthzam to duthzam; hobfex to duthzam,
hobfex, iskxil and qenxil; iskxil to duthzam, hobfex, iskxil and qenxil; qenxil to
duthzam and qenxil.

## The shape of it

The right picture for nakyuk is a spreading stain rather than a list. Drop one opalmi
in, apply the operation to whatever is wet, repeat. The stain here reaches 1, 2 and 4
opalmis depending on where it started.

The relation is easiest to see as a height. Each opalmi casts a espafex over what it
covers, and the sizes of those shadows here are 1 and 5. Sizes repeat, so the objects do
not line up in single file.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T10 rests on D9 (a hobsol) and A6 (antisymmetry of the relation). Remove any one of them
and the statement stops making sense, not merely stops being provable.

T11 rests on D13 (grixhob pairs) and A6 (antisymmetry of the relation). Remove any one
of them and the statement stops making sense, not merely stops being provable.

## A worked case

Take (hobfex - iskxil) - duthzam and work it out one step at a time.
    hobfex - iskxil = duthzam   (the table for -)
    duthzam - duthzam = duthzam   (the table for -)
That leaves duthzam, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is iskxil - (duthzam - hobfex) for contrast.
    duthzam - hobfex = hobfex   (the table for -)
    iskxil - hobfex = duthzam   (the table for -)
That gives duthzam, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
keldsib <~ qenxil hold? Read off what keldsib stands over: keldsib, duthzam, hobfex,
iskxil and qenxil. qenxil is among them, so it holds.

A second case, this time a nakyuk. Start from hobfex. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is duthzam, hobfex,
iskxil and qenxil, so the vexisk of hobfex is 4.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of opalmis that come back
unchanged from themselves: keldsib and duthzam. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of antisymmetry of the relation and closure
under the first operation. Those are properties of this system, not of systems in
general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A6 (antisymmetry of the relation), D13 (grixhob pairs), D3 (brarast
collections) and D9 (a hobsol).

What is built on it later: D11 (the vexisk of a opalmi), T4 (the nakyuk of a opalmi is
brarast), T5 (the nakyuk is contained in every brarast collection) and T7 (the nakyuk of
a zamlorn opalmi stays in the zamlorn).

## Proofs

T10. No two distinct opalmis can both be hobsols.

  (1) [D9] Let f and h both be floors.
  (2) [D9] Then f <~ h, since h is any object, and h <~ f likewise.
  (3) [A6] Antisymmetry forces f = h.

Checked over 25 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T11. No two distinct opalmis lie in each other's espafex.

  (1) [D13] Suppose x and y form a tight pair.
  (2) [A6] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the nakyuk of a opalmi. Later chapters state their results in these terms
and do not restate the definitions.

The results now available are T10 and T11, each settled by exhaustive check rather than
by argument from analogy.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x028. List the nakyuk of hobfex.
  x029. List the nakyuk of iskxil.
  x030. List the nakyuk of qenxil.
Level 4.
  x031. Let z be duthzam - iskxil. List the nakyuk of z.
  x048. This result is about the hobsol. List every opalmi in it.
