# Chapter 3. The relation and what it orders

## Why this chapter

Work through this chapter with the tables in front of you. It covers reflexivity of the
relation, transitivity of the relation and comparability of every pair, and each claim
can be checked by hand.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

One habit to adopt: when a statement below quantifies over grixmis, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A6. Reflexivity of the relation. For every grixmi x: x |> x.

A7. Transitivity of the relation. For all grixmis x, y, z: if x |> y and y |> z then x
|> z.

A8. Comparability of every pair. For all grixmis x and y, at least one of x |> y and y
|> x holds.

A9. Agreement of the relation with the first operation. For all grixmis x, y, z: if x |>
y then (z # x) |> (z # y) and (x # z) |> (y # z).

D4. The umbhob of a grixmi. The umbhob of a grixmi x is the collection of grixmis y for
which x |> y holds.

Worked out for each grixmi: tezreld to tezreld; vexyuk to tezreld, vexyuk and muxlum;
muxlum to tezreld, vexyuk and muxlum.

## The shape of it

The relation is easiest to see as a height. Each grixmi casts a umbhob over what it
refines, and the sizes of those shadows here are 1 and 3. Sizes repeat, so the objects
do not line up in single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 3 grixmis the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R4 rests on S2 (the Hurnglim combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take (vexyuk # tezreld) # vexyuk and work it out one step at a time.
    vexyuk # tezreld = tezreld   (the table for #)
    tezreld # vexyuk = tezreld   (the table for #)
The expression comes to tezreld.

Bracketing is not cosmetic, so here is tezreld # (vexyuk # vexyuk) for contrast.
    vexyuk # vexyuk = vexyuk   (the table for #)
    tezreld # vexyuk = tezreld   (the table for #)
That gives tezreld, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
muxlum |> muxlum hold? Read off what muxlum stands over: tezreld, vexyuk and muxlum.
muxlum is among them, so it holds.

## A case that breaks

R4. It is not the case that: For all grixmis x and y: if x |> y and y |> x then x = y.
It fails at x = vexyuk, y = muxlum. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: S2 (the Hurnglim combination tables).

These results are used again in D9 (a lumsib), D13 (vexjen pairs), T9 (umbhobs are
nested along the relation) and T10 (the system has a lumsib).

## Proofs

R4. It is not the case that: For all grixmis x and y: if x |> y and y |> x then x = y.

  (1) [S2] Take the case x = vexyuk, y = muxlum, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 27 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the umbhob of a grixmi. Each of these is used by name
later, so the names are worth learning rather than looking up.

Do not carry forward R4. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x011. Which grixmis y satisfy vexyuk |> y? Name them all.
Level 5.
  x007. The following fails in this system: For all grixmis x and y: if x |> y and y |> x then x = y. Name the earliest grixmi, in the order the grixmis were introduced, that witnesses the failure.
