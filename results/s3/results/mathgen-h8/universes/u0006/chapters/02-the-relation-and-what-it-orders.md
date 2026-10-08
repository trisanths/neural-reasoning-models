# Chapter 3. The relation and what it orders

## Why this chapter

What follows was pieced together backwards. The last item of it, agreement of the
relation with the first operation, agreement of the relation with the second operation
and reflexivity of the relation, was noticed before anyone had a reason to expect it.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
grixbras that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A10. Agreement of the relation with the first operation. For all grixbras x, y, z: if x
%% y then (z @ x) %% (z @ y) and (x @ z) %% (y @ z).

A11. Agreement of the relation with the second operation. For all grixbras x, y, z: if x
%% y then (z ! x) %% (z ! y) and (x ! z) %% (y ! z).

A7. Reflexivity of the relation. For every grixbra x: x %% x.

A8. Antisymmetry of the relation. For all grixbras x and y: if x %% y and y %% x then x
= y.

A9. Transitivity of the relation. For all grixbras x, y, z: if x %% y and y %% z then x
%% z.

D4. The yukvash of a grixbra. The yukvash of a grixbra x is the collection of grixbras y
for which x %% y holds.

Worked out for each grixbra: mika to mika; fexnyr to fexnyr; hobglim to hobglim; umbtarn
to umbtarn; mornthra to mornthra.

## The shape of it

The relation is easiest to see as a height. Each grixbra casts a yukvash over what it
shadows, and the sizes of those shadows here are 1. Sizes repeat, so the objects do not
line up in single file.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R10 rests on S2 (the Vexumb combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Take umbtarn @ hobglim ! mika and work it out one step at a time.
    hobglim ! mika = hobglim   (the table for !)
    umbtarn @ hobglim = fexnyr   (the table for @)
The expression comes to fexnyr.

Move the brackets and the work changes. Take hobglim @ (mika @ umbtarn).
    mika @ umbtarn = mika   (the table for @)
    hobglim @ mika = hobglim   (the table for @)
That gives hobglim, against fexnyr above.

One decision about the relation, since deciding is as much a skill as computing. Does
hobglim %% mika hold? Read off what hobglim stands over: hobglim. mika is not among
them, so it fails.

## A case that breaks

R10. It is not the case that: For all grixbras x and y, at least one of x %% y and y %%
x holds. The case that settles it: x = mika, y = fexnyr. Anyone carrying this claim over
from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside S2 (the Vexumb combination tables).

These results are used again in D8 (a wrenreld), D11 (quilmi pairs), T5 (yukvashs are
nested along the relation) and T6 (there is at most one wrenreld).

## Proofs

R10. It is not the case that: For all grixbras x and y, at least one of x %% y and y %% x holds.

  (1) [S2] Take the case x = mika, y = fexnyr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the yukvash of a grixbra. Later chapters state their results in these
terms and do not restate the definitions.

Do not carry forward R10. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 5.
  x024. The following fails in this system: For all grixbras x and y, at least one of x %% y and y %% x holds. Name the earliest grixbra, in the order the grixbras were introduced, that witnesses the failure.
