# Chapter 6. The relation and what it orders (2)

## Why this chapter

We turn to quilmi pairs, a wrenreld and yukvashs are nested along the relation. The
treatment is self contained given the material already established.

Nothing here stands on its own. The arguments lean on chapter 3, and a reader who has
skipped it will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about grixbras covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

## What is defined here

D11. Quilmi pairs. Two distinct grixbras x and y form a quilmi pair when x %% y and y %%
x both hold, that is, when each lies in the yukvash of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D8. A wrenreld. A grixbra f is a wrenreld when f %% y holds for every grixbra y, that
is, when the yukvash of f is the whole system.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

## The shape of it

The relation is easiest to see as a height. Each grixbra casts a yukvash over what it
shadows, and the sizes of those shadows here are 1. Sizes repeat, so the objects do not
line up in single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 grixbras the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T5 rests on D4 (the yukvash of a grixbra) and A9 (transitivity of the relation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

T7 rests on D4 (the yukvash of a grixbra) and A10 (agreement of the relation with the
first operation). The dependence is on the content of those results, not only on their
vocabulary.

T9 rests on D4 (the yukvash of a grixbra). Remove any one of them and the statement
stops making sense, not merely stops being provable.

## A worked case

Here is (mika @ fexnyr) @ (hobglim @ mornthra), reduced without skipping anything.
    mika @ fexnyr = mika   (the table for @)
    hobglim @ mornthra = mika   (the table for @)
    mika @ mika = mika   (the table for @)
That leaves mika, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take fexnyr @ (hobglim @ mika).
    hobglim @ mika = hobglim   (the table for @)
    fexnyr @ hobglim = mika   (the table for @)
That gives mika, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
mika %% mornthra hold? Read off what mika stands over: mika. mornthra is not among them,
so it fails.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by agreement of the relation with the first operation and
transitivity of the relation. A system without them is not a system where these results
are harder to prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A10 (agreement of the relation with the first
operation), A9 (transitivity of the relation) and D4 (the yukvash of a grixbra).

These results are used again in T6 (there is at most one wrenreld) and T8 (no quilmi
pairs exist).

## Proofs

T5. If y lies in the yukvash of x, then the yukvash of y is contained in the yukvash of x.

  (1) [D4] Let y satisfy x %% y and let z satisfy y %% z.
  (2) [A9] Transitivity gives x %% z.
  (3) [D4] So every member of the yukvash of y is a member of that of x.

Checked over 125 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T7. If x %% y then (x @ z) %% (y @ z) for every grixbra z.

  (1) [D4] Let y lie in the yukvash of x.
  (2) [A10] Compatibility applies the operation to both sides at once.
  (3) Nothing else is needed, since z was arbitrary.

Checked over 125 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T9. If x %% y then y %% x.

  (1) [D4] Symmetry would mean y lies in the yukvash of x exactly when x lies in that of y.
  (2) The listed pairs settle it directly.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward quilmi pairs and a wrenreld. Later chapters state their results in these
terms and do not restate the definitions.

The results now available are T5, T7 and T9, each settled by exhaustive check rather
than by argument from analogy.

## Exercises

No exercises here. Every question this chapter suggested turned out to be answerable
from the question itself, so all of them were discarded.
