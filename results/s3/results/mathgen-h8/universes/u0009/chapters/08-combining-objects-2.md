# Chapter 9. Combining objects (2)

## Why this chapter

Work through this chapter with the tables in front of you. It covers where every reldjen
is duthnyr breaks down, every reldjen lies in the vashreld and the lornumb lies in the
vashreld, and each claim can be checked by hand.

Nothing here stands on its own. The arguments lean on chapters 1, 5, 6 and 7, and a
reader who has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over reldjens, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

A useful mental split: some reldjens are inert under the operation and some are not.
nakopal and kagel come back unchanged when combined with themselves, and nakopal, kagel,
korrreld and iskbra commute with everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 reldjens the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R9 rests on D7 (the umbka). The dependence is on the content of those results, not only
on their vocabulary.

T14 rests on D6 (the vashreld). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T2 rests on D5 (the lornumb) and D6 (the vashreld). Remove any one of them and the
statement stops making sense, not merely stops being provable.

T3 rests on D6 (the vashreld), D3 (zammorn collections) and A2 (association of the first
operation). The dependence is on the content of those results, not only on their
vocabulary.

T9 rests on D7 (the umbka) and D3 (zammorn collections). The dependence is on the
content of those results, not only on their vocabulary.

## A worked case

Take kagel <> korrreld # iskbra and work it out one step at a time.
    korrreld # iskbra = kagel   (the table for #)
    kagel <> kagel = kagel   (the table for <>)
So kagel <> korrreld # iskbra is kagel.

Bracketing is not cosmetic, so here is korrreld <> (iskbra <> kagel) for contrast.
    iskbra <> kagel = iskbra   (the table for <>)
    korrreld <> iskbra = korrreld   (the table for <>)
The value is korrreld, not kagel.

One decision about the relation, since deciding is as much a skill as computing. Does
korrreld :: iskbra hold? Read off what korrreld stands over: korrreld and iskbra. iskbra
is among them, so it holds.

## A case that breaks

R9. It is not the case that: x <> x = x for every reldjen x. It fails at x = korrreld,
value = nakopal. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation and closure under the first operation. Those are
properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A2 (association of the first operation), D3 (zammorn collections), D5
(the lornumb) and D6 (the vashreld).

What is built on it later: T8 (the nakgrix of a vashreld reldjen stays in the vashreld)
and T15 (the second operation keeps the vashreld intact).

## Proofs

R9. It is not the case that: x <> x = x for every reldjen x.

  (1) [S2] Take the case x = korrreld, value = nakopal, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 4 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T14. Every pair of reldjens korrfexs.

  (1) [D6] The vashreld is defined by korrfexing with everything.
  (2) [D2] The claim is that x <> y = y <> x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 16 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T2. The lornumb korrfexs with every reldjen.

  (1) [D5] Let e be the lornumb and x any reldjen.
  (2) [D5] Then e <> x = x and x <> e = x.
  (3) [D2] So e <> x = x <> e, which is what it means to korrfex.
  (4) [D6] Since x was arbitrary, e belongs to the vashreld.

Checked over 4 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. If x and y both korrfex with every reldjen, then so does x <> y.

  (1) [D6] Let x and y lie in the vashreld and let z be any reldjen.
  (2) [A2] Then (x <> y) <> z = x <> (y <> z).
  (3) [D6] Move z past y, then past x, using that each korrfexs with everything.
  (4) [D3] So x <> y korrfexs with z, and the vashreld is zammorn.

Checked over 16 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

T9. If x and y are both duthnyr then so is x <> y.

  (1) [D7] Let x and y be duthnyr.
  (2) [D1] The claim asks whether (x <> y) <> (x <> y) returns x <> y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 16 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Established here and safe to use: T14, T2, T3 and T9.

Do not carry forward R9. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x032. Name the reldjens that make up the umbka, which is what the result above is a claim about.
Level 5.
  x033. The following fails in this system: x <> x = x for every reldjen x. Name the earliest reldjen, in the order the reldjens were introduced, that witnesses the failure.
