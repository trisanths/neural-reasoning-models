# Chapter 8. Combining objects (3)

## Why this chapter

The results collected here were not found in this order. There is at most one wrenreld,
no quilmi pairs exist and where every grixbra lies in the quilquil breaks down came
first, and the rest was assembled around that once the pattern was visible.

Prerequisites are real here: chapters 3, 5, 6 and 7 supply the notions the statements
below are phrased in.

The standard of proof here is exhaustion. A universal claim about grixbras covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

Think of %% as pointing downhill. The yukvash of a grixbra is everything downhill of it,
and those shadows here have sizes 1.

Two questions sort the grixbras quickly. Does combining a grixbra with itself change it?
For mika it does not. Does it matter which side it goes on? It always does.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T6 rests on D8 (a wrenreld) and A8 (antisymmetry of the relation). The dependence is on
the content of those results, not only on their vocabulary.

T8 rests on D11 (quilmi pairs) and A8 (antisymmetry of the relation). The dependence is
on the content of those results, not only on their vocabulary.

R12 rests on D5 (the quilquil). Remove any one of them and the statement stops making
sense, not merely stops being provable.

R13 rests on D6 (the ovitez). The dependence is on the content of those results, not
only on their vocabulary.

T4 rests on D6 (the ovitez) and D3 (umbgel collections). The dependence is on the
content of those results, not only on their vocabulary.

## A worked case

Take (mornthra @ fexnyr) @ (mika @ hobglim) and work it out one step at a time.
    mornthra @ fexnyr = umbtarn   (the table for @)
    mika @ hobglim = mika   (the table for @)
    umbtarn @ mika = umbtarn   (the table for @)
That leaves umbtarn, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take fexnyr @ (mika @ mornthra).
    mika @ mornthra = mika   (the table for @)
    fexnyr @ mika = fexnyr   (the table for @)
The value is fexnyr, not umbtarn.

One decision about the relation, since deciding is as much a skill as computing. Does
mika %% mika hold? Read off what mika stands over: mika. mika is among them, so it
holds.

## A case that breaks

R12. It is not the case that: Every pair of grixbras grixovis. It fails at x = mika, y =
fexnyr, left = mika, right = fexnyr. One case is enough, and this is the earliest one.

R13. It is not the case that: x @ x = x for every grixbra x. It fails at x = fexnyr,
value = mika. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of antisymmetry of the relation and closure
under the first operation. Those are properties of this system, not of systems in
general.

That is not a rhetorical caution. Take the same 5 objects, the same symbols, and a
different table, and T6 and T8 stop holding. The notation survives the substitution and
the mathematics does not.

## Neighbouring results

The material this chapter borrows from: A8 (antisymmetry of the relation), D11 (quilmi
pairs), D3 (umbgel collections) and D5 (the quilquil).

## Proofs

T6. No two distinct grixbras can both be wrenrelds.

  (1) [D8] Let f and h both be floors.
  (2) [D8] Then f %% h, since h is any object, and h %% f likewise.
  (3) [A8] Antisymmetry forces f = h.

Checked over 25 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T8. No two distinct grixbras lie in each other's yukvash.

  (1) [D11] Suppose x and y form a tight pair.
  (2) [A8] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

R12. It is not the case that: Every pair of grixbras grixovis.

  (1) [S2] Take the case x = mika, y = fexnyr, left = mika, right = fexnyr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

R13. It is not the case that: x @ x = x for every grixbra x.

  (1) [S2] Take the case x = fexnyr, value = mika, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T4. If x and y are both reldjen then so is x @ y.

  (1) [D6] Let x and y be reldjen.
  (2) [D1] The claim asks whether (x @ y) @ (x @ y) returns x @ y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 25 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

The results now available are T6, T8 and T4, each settled by exhaustive check rather
than by argument from analogy.

Do not carry forward R12 and R13. These were tested and failed, and the failing cases
are recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x046. This result is about the ovitez. List every grixbra in it.
Level 5.
  x047. The following fails in this system: Every pair of grixbras grixovis. Name the earliest grixbra, in the order the grixbras were introduced, that witnesses the failure.
  x048. The following fails in this system: x @ x = x for every grixbra x. Name the earliest grixbra, in the order the grixbras were introduced, that witnesses the failure.
