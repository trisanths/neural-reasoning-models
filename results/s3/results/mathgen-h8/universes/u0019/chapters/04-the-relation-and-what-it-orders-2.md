# Chapter 5. The relation and what it orders (2)

## Why this chapter

The results collected here were not found in this order. Grixhob pairs, brarast
collections and a hobsol came first, and the rest was assembled around that once the
pattern was visible.

Nothing here stands on its own. The arguments lean on chapters 1 and 3, and a reader who
has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about opalmis covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D13. Grixhob pairs. Two distinct opalmis x and y form a grixhob pair when x <~ y and y
<~ x both hold, that is, when each lies in the espafex of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D3. Brarast collections. A collection S of opalmis is brarast when x - y belongs to S
for every pair x, y drawn from S.

D9. A hobsol. A opalmi f is a hobsol when f <~ y holds for every opalmi y, that is, when
the espafex of f is the whole system.

In this system that picks out keldsib, which is 1 of the 5 opalmis.

## The shape of it

The right picture for nakyuk is a spreading stain rather than a list. Drop one opalmi
in, apply the operation to whatever is wet, repeat. The stain here reaches 1, 2 and 4
opalmis depending on where it started.

The relation is easiest to see as a height. Each opalmi casts a espafex over what it
covers, and the sizes of those shadows here are 1 and 5. Sizes repeat, so the objects do
not line up in single file.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R10 rests on D4 (the espafex of a opalmi). Remove any one of them and the statement
stops making sense, not merely stops being provable.

T9 rests on D4 (the espafex of a opalmi) and A7 (transitivity of the relation). The
dependence is on the content of those results, not only on their vocabulary.

## A worked case

Here is (hobfex - duthzam) - qenxil, reduced without skipping anything.
    hobfex - duthzam = hobfex   (the table for -)
    hobfex - qenxil = iskxil   (the table for -)
That leaves iskxil, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is duthzam - (qenxil - hobfex) for contrast.
    qenxil - hobfex = iskxil   (the table for -)
    duthzam - iskxil = iskxil   (the table for -)
That gives iskxil, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
duthzam <~ keldsib hold? Read off what duthzam stands over: duthzam. keldsib is not
among them, so it fails.

## A case that breaks

R10. It is not the case that: If x <~ y then y <~ x. The case that settles it: x =
keldsib, y = duthzam. Anyone carrying this claim over from a more familiar system will
be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation and
transitivity of the relation. Those are properties of this system, not of systems in
general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A1 (closure under the first operation), A7 (transitivity of the relation)
and D4 (the espafex of a opalmi).

What is built on it later: D8 (the nakyuk of a opalmi), T3 (the zamlorn is brarast), T4
(the nakyuk of a opalmi is brarast) and T8 (the tarnsol is brarast).

## Proofs

R10. It is not the case that: If x <~ y then y <~ x.

  (1) [S2] Take the case x = keldsib, y = duthzam, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T9. If y lies in the espafex of x, then the espafex of y is contained in the espafex of x.

  (1) [D4] Let y satisfy x <~ y and let z satisfy y <~ z.
  (2) [A7] Transitivity gives x <~ z.
  (3) [D4] So every member of the espafex of y is a member of that of x.

Checked over 125 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward grixhob pairs, brarast collections and a hobsol. Later chapters state
their results in these terms and do not restate the definitions.

Established here and safe to use: T9.

Do not carry forward R10. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x020. How many opalmis lie in the smallest brarast collection containing duthzam?
  x021. How many opalmis lie in the smallest brarast collection containing hobfex?
Level 4.
  x032. Which opalmis make up the hobsol? Name them all.
  x046. The result above concerns espafexs. List the espafex of keldsib.
  x047. The result above concerns espafexs. List the espafex of hobfex.
Level 5.
  x050. The following fails in this system: If x <~ y then y <~ x. Name the earliest opalmi, in the order the opalmis were introduced, that witnesses the failure.
