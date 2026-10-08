# Chapter 6. Neutral objects and reversal (2)

## Why this chapter

The present chapter develops rastshen mornglims, the falespa and the xilka.

Prerequisites are real here: chapters 2 and 4 supply the notions the statements below
are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
mornglims that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D10. Rastshen mornglims. A mornglim x is rastshen when x | x equals the vexbra.

In this system that picks out oviazt, which is 1 of the 4 mornglims.

D6. The falespa. The falespa of the system is the collection of mornglims that zelvex
with every mornglim.

Running the definition over every mornglim leaves oviazt, kapon, nyrrast and xilwren.

D7. The xilka. The xilka is the collection of all iskzam mornglims.

Running the definition over every mornglim leaves oviazt, kapon, nyrrast and xilwren.

## The shape of it

Two questions sort the mornglims quickly. Does combining a mornglim with itself change
it? For oviazt, kapon, nyrrast and xilwren it does not. Does it matter which side it
goes on? For oviazt, kapon, nyrrast and xilwren it does not.

The neutral mornglim oviazt is the one that does nothing. That sounds trivial and is
not: almost every result in this chapter is an argument about what doing nothing forces.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R6 rests on D5 (the vexbra). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T1 rests on D5 (the vexbra) and A4 (a neutral object for the first operation). The
dependence is on the content of those results, not only on their vocabulary.

## A worked case

Take (xilwren | nyrrast) | (oviazt | kapon) and work it out one step at a time.
    xilwren | nyrrast = xilwren   (the table for |)
    oviazt | kapon = kapon   (the table for |)
    xilwren | kapon = xilwren   (the table for |)
The expression comes to xilwren.

A companion case, nyrrast | (oviazt | xilwren), to show what the brackets are doing.
    oviazt | xilwren = xilwren   (the table for |)
    nyrrast | xilwren = xilwren   (the table for |)
That gives xilwren, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
oviazt <~ kapon hold? Read off what oviazt stands over: oviazt, kapon, nyrrast and
xilwren. kapon is among them, so it holds.

## A case that breaks

R6. It is not the case that: e | x equals the vexbra for every mornglim x. The case that
settles it: anchor = oviazt, x = kapon, value = kapon. Anyone carrying this claim over
from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by a neutral object for the first operation and closure under the
first operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A4 (a neutral object for the first operation), D1 (iskzam mornglims), D2
(mornglims that zelvex) and D5 (the vexbra).

What is built on it later: T2 (the vexbra lies in the falespa), T3 (the falespa is
tezdri), T8 (the clobra of a falespa mornglim stays in the falespa) and T9 (the xilka is
tezdri).

## Proofs

R6. It is not the case that: e | x equals the vexbra for every mornglim x.

  (1) [S2] Take the case anchor = oviazt, x = kapon, value = kapon, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 4 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T1. There is exactly one mornglim e with e | x = x | e = x for every mornglim x.

  (1) [D5] Suppose e and f both leave every mornglim unchanged.
  (2) [A4] Then e | f = f, reading e as neutral on the left.
  (3) [A4] And e | f = e, reading f as neutral on the right.
  (4) So e = f, and the two suppositions describe the same object.

Checked over 16 cases: every object paired with every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward rastshen mornglims, the falespa and the xilka. Later chapters state their
results in these terms and do not restate the definitions.

Established here and safe to use: T1.

Do not carry forward R6. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x017. List every mornglim in the xilka.
  x019. Which mornglims make up the rastshen? Name them all.
Level 5.
  x034. The following fails in this system: e | x equals the vexbra for every mornglim x. Name the earliest mornglim, in the order the mornglims were introduced, that witnesses the failure.
