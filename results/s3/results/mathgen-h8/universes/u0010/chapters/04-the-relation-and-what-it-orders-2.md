# Chapter 5. The relation and what it orders (2)

## Why this chapter

Anyone using this system to keep track of something will meet vexjen pairs, vintmorn
collections and a lumsib early, whether or not they go looking.

Prerequisites are real here: chapters 1 and 3 supply the notions the statements below
are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 3
grixmis that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D13. Vexjen pairs. Two distinct grixmis x and y form a vexjen pair when x |> y and y |>
x both hold, that is, when each lies in the umbhob of the other.

Running the definition over every grixmi leaves vexyuk and muxlum.

D3. Vintmorn collections. A collection S of grixmis is vintmorn when x # y belongs to S
for every pair x, y drawn from S.

D9. A lumsib. A grixmi f is a lumsib when f |> y holds for every grixmi y, that is, when
the umbhob of f is the whole system.

In this system that picks out vexyuk and muxlum, which is 2 of the 3 grixmis.

## The shape of it

Picture the shenyuk as what happens when you start with one grixmi and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 3 grixmis, that stops. In this system the sizes it stops at are 1 and 2.

The relation is easiest to see as a height. Each grixmi casts a umbhob over what it
refines, and the sizes of those shadows here are 1 and 3. Sizes repeat, so the objects
do not line up in single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 3 grixmis the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R8 rests on D4 (the umbhob of a grixmi). The dependence is on the content of those
results, not only on their vocabulary.

T11 rests on D4 (the umbhob of a grixmi) and A9 (agreement of the relation with the
first operation). Remove any one of them and the statement stops making sense, not
merely stops being provable.

T9 rests on D4 (the umbhob of a grixmi) and A7 (transitivity of the relation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Take (muxlum # muxlum) # muxlum and work it out one step at a time.
    muxlum # muxlum = vexyuk   (the table for #)
    vexyuk # muxlum = muxlum   (the table for #)
So (muxlum # muxlum) # muxlum is muxlum.

A companion case, muxlum # (muxlum # muxlum), to show what the brackets are doing.
    muxlum # muxlum = vexyuk   (the table for #)
    muxlum # vexyuk = muxlum   (the table for #)
That gives muxlum, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test tezreld |> vexyuk. The umbhob of tezreld is tezreld, and vexyuk lies outside it, so
the relation fails.

## A case that breaks

R8. It is not the case that: If x |> y then y |> x. It fails at x = vexyuk, y = tezreld.
One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of agreement of the relation with the first
operation, closure under the first operation and transitivity of the relation. Those are
properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A1 (closure under the first operation), A7
(transitivity of the relation), A9 (agreement of the relation with the first operation)
and D4 (the umbhob of a grixmi).

What is built on it later: D8 (the shenyuk of a grixmi), T3 (the zelmorn is vintmorn),
T4 (the shenyuk of a grixmi is vintmorn) and T8 (the korrsol is vintmorn).

## Proofs

R8. It is not the case that: If x |> y then y |> x.

  (1) [S2] Take the case x = vexyuk, y = tezreld, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 9 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T11. If x |> y then (x # z) |> (y # z) for every grixmi z.

  (1) [D4] Let y lie in the umbhob of x.
  (2) [A9] Compatibility applies the operation to both sides at once.
  (3) Nothing else is needed, since z was arbitrary.

Checked over 27 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T9. If y lies in the umbhob of x, then the umbhob of y is contained in the umbhob of x.

  (1) [D4] Let y satisfy x |> y and let z satisfy y |> z.
  (2) [A7] Transitivity gives x |> z.
  (3) [D4] So every member of the umbhob of y is a member of that of x.

Checked over 27 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward vexjen pairs, vintmorn collections and a lumsib. Later chapters state
their results in these terms and do not restate the definitions.

The results now available are T11 and T9, each settled by exhaustive check rather than
by argument from analogy.

Do not carry forward R8. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x009. How many grixmis lie in the smallest vintmorn collection containing vexyuk?
  x010. How many grixmis lie in the smallest vintmorn collection containing muxlum?
Level 4.
  x017. List every grixmi in the lumsib.
  x025. List every grixmi in the vexjen.
  x028. The result above concerns umbhobs. List the umbhob of vexyuk.
Level 5.
  x031. The following fails in this system: If x |> y then y |> x. Name the earliest grixmi, in the order the grixmis were introduced, that witnesses the failure.
