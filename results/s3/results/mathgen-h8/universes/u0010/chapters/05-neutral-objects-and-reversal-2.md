# Chapter 6. Neutral objects and reversal (2)

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through aztpyr grixmis, the zelmorn
and the korrsol.

Nothing here stands on its own. The arguments lean on chapters 2 and 4, and a reader who
has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about grixmis covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D10. Aztpyr grixmis. A grixmi x is aztpyr when x # x equals the hobka.

Running the definition over every grixmi leaves vexyuk and muxlum.

D6. The zelmorn. The zelmorn of the system is the collection of grixmis that shenfal
with every grixmi.

Running the definition over every grixmi leaves tezreld, vexyuk and muxlum.

D7. The korrsol. The korrsol is the collection of all rastpon grixmis.

Running the definition over every grixmi leaves tezreld and vexyuk.

## The shape of it

A useful mental split: some grixmis are inert under the operation and some are not.
tezreld and vexyuk come back unchanged when combined with themselves, and tezreld,
vexyuk and muxlum commute with everything.

The neutral grixmi vexyuk is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 3 grixmis the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R9 rests on D5 (the hobka). Remove any one of them and the statement stops making sense,
not merely stops being provable.

T1 rests on D5 (the hobka) and A4 (a neutral object for the first operation). Remove any
one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Here is (vexyuk # tezreld) # (vexyuk # tezreld), reduced without skipping anything.
    vexyuk # tezreld = tezreld   (the table for #)
    vexyuk # tezreld = tezreld   (the table for #)
    tezreld # tezreld = tezreld   (the table for #)
So (vexyuk # tezreld) # (vexyuk # tezreld) is tezreld.

Move the brackets and the work changes. Take tezreld # (vexyuk # vexyuk).
    vexyuk # vexyuk = vexyuk   (the table for #)
    tezreld # vexyuk = tezreld   (the table for #)
The value is tezreld. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
muxlum |> vexyuk hold? Read off what muxlum stands over: tezreld, vexyuk and muxlum.
vexyuk is among them, so it holds.

## A case that breaks

R9. It is not the case that: e # x equals the hobka for every grixmi x. The case that
settles it: anchor = vexyuk, x = tezreld, value = tezreld. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by a neutral object for the first operation and closure under the
first operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A4 (a neutral object for the first operation),
D1 (rastpon grixmis), D2 (grixmis that shenfal) and D5 (the hobka).

What is built on it later: T2 (the hobka lies in the zelmorn), T3 (the zelmorn is
vintmorn), T7 (the shenyuk of a zelmorn grixmi stays in the zelmorn) and T8 (the korrsol
is vintmorn).

## Proofs

R9. It is not the case that: e # x equals the hobka for every grixmi x.

  (1) [S2] Take the case anchor = vexyuk, x = tezreld, value = tezreld, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 3 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T1. There is exactly one grixmi e with e # x = x # e = x for every grixmi x.

  (1) [D5] Suppose e and f both leave every grixmi unchanged.
  (2) [A4] Then e # f = f, reading e as neutral on the left.
  (3) [A4] And e # f = e, reading f as neutral on the right.
  (4) So e = f, and the two suppositions describe the same object.

Checked over 9 cases: every object paired with every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward aztpyr grixmis, the zelmorn and the korrsol. Later chapters state their
results in these terms and do not restate the definitions.

The results now available are T1, each settled by exhaustive check rather than by
argument from analogy.

Explicitly not available: R9. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x013. Write down the korrsol in full.
  x018. Which grixmis make up the aztpyr? Name them all.
Level 5.
  x032. The following fails in this system: e # x equals the hobka for every grixmi x. Name the earliest grixmi, in the order the grixmis were introduced, that witnesses the failure.
