# Chapter 8. Collections that close on themselves

## Why this chapter

Work through this chapter with the tables in front of you. It covers the glimmorn of a
grixmi, the shenyuk of a grixmi is vintmorn and the shenyuk of a zelmorn grixmi stays in
the zelmorn, and each claim can be checked by hand.

Prerequisites are real here: chapters 5, 6 and 7 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over grixmis, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D11. The glimmorn of a grixmi. The glimmorn of a grixmi x is the number of grixmis in
its shenyuk [x].

Worked out for each grixmi: tezreld to 1; vexyuk to 1; muxlum to 2.

## The shape of it

Picture the shenyuk as what happens when you start with one grixmi and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 3 grixmis, that stops. In this system the sizes it stops at are 1 and 2.

Two questions sort the grixmis quickly. Does combining a grixmi with itself change it?
For tezreld and vexyuk it does not. Does it matter which side it goes on? For tezreld,
vexyuk and muxlum it does not.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 3 grixmis the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T4 rests on D8 (the shenyuk of a grixmi) and D3 (vintmorn collections). Remove any one
of them and the statement stops making sense, not merely stops being provable.

T7 rests on D8 (the shenyuk of a grixmi), D6 (the zelmorn) and T3 (the zelmorn is
vintmorn). Remove any one of them and the statement stops making sense, not merely stops
being provable.

## A worked case

Evaluate (vexyuk # vexyuk) # (vexyuk # muxlum). Each line below is one lookup in a
table.
    vexyuk # vexyuk = vexyuk   (the table for #)
    vexyuk # muxlum = muxlum   (the table for #)
    vexyuk # muxlum = muxlum   (the table for #)
The expression comes to muxlum.

Move the brackets and the work changes. Take vexyuk # (vexyuk # vexyuk).
    vexyuk # vexyuk = vexyuk   (the table for #)
    vexyuk # vexyuk = vexyuk   (the table for #)
The value is vexyuk, not muxlum.

One decision about the relation, since deciding is as much a skill as computing. Does
tezreld |> vexyuk hold? Read off what tezreld stands over: tezreld. vexyuk is not among
them, so it fails.

Now compute [muxlum]. Fold muxlum against itself, then fold whatever appeared against
everything present, and stop when a round adds nothing. The result is vexyuk and muxlum,
of size 2.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of association of the first operation and
closure under the first operation. Those are properties of this system, not of systems
in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside D3 (vintmorn collections), D6 (the zelmorn), D8 (the shenyuk of a grixmi)
and T3 (the zelmorn is vintmorn).

What is built on it later: D12 (the bratez), T5 (the shenyuk is contained in every
vintmorn collection), T6 (a grixmi is rastpon exactly when its glimmorn is one) and R5
(where the glimmorn divides the number of grixmis breaks down).

## Proofs

T4. For every grixmi x, the collection [x] is vintmorn.

  (1) [D8] [x] is built by taking x and closing under #.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 27 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

T7. If x lies in the zelmorn then every grixmi of [x] lies in the zelmorn.

  (1) [T3] The zelmorn is vintmorn.
  (2) [D8] [x] is the smallest vintmorn collection containing x.
  (3) A smallest such collection sits inside any other, and the zelmorn is one.

Checked over 9 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the glimmorn of a grixmi. Later chapters state their results in these
terms and do not restate the definitions.

The results now available are T4 and T7, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x019. How many grixmis lie in [vexyuk]?
  x020. How many grixmis lie in [muxlum]?
Level 5.
  x021. Let z be (tezreld # tezreld) # vexyuk. What is the glimmorn of z?
  x022. Let z be (muxlum # vexyuk) # vexyuk. What is the glimmorn of z?
  x023. Let z be (tezreld # vexyuk) # tezreld. What is the glimmorn of z?
