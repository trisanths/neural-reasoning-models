# Chapter 4. Combining objects

## Why this chapter

What follows was pieced together backwards. The last item of it, rastpon grixmis,
grixmis that shenfal and the hobka, was noticed before anyone had a reason to expect it.

Nothing here stands on its own. The arguments lean on chapters 1 and 2, and a reader who
has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about grixmis covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

## What is defined here

D1. Rastpon grixmis. A grixmi x is called rastpon when x # x = x.

Running the definition over every grixmi leaves tezreld and vexyuk.

D2. Grixmis that shenfal. Two grixmis x and y are said to shenfal when x # y = y # x.

D5. The hobka. The grixmi vexyuk is called the hobka of the system. It is the unique
grixmi that leaves every grixmi unchanged under #.

Here that is vexyuk.

## The shape of it

A useful mental split: some grixmis are inert under the operation and some are not.
tezreld and vexyuk come back unchanged when combined with themselves, and tezreld,
vexyuk and muxlum commute with everything.

Neutrality is a strong condition disguised as a weak one. It fixes a single grixmi and,
through that, constrains everything that can combine with it.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 3 grixmis the table is short enough to consult every time.

## Where these results come from

This chapter is groundwork. The derivations that use it start in the next one.

## A worked case

Evaluate (vexyuk # vexyuk) # (vexyuk # muxlum). Each line below is one lookup in a
table.
    vexyuk # vexyuk = vexyuk   (the table for #)
    vexyuk # muxlum = muxlum   (the table for #)
    vexyuk # muxlum = muxlum   (the table for #)
The expression comes to muxlum.

Bracketing is not cosmetic, so here is vexyuk # (vexyuk # vexyuk) for contrast.
    vexyuk # vexyuk = vexyuk   (the table for #)
    vexyuk # vexyuk = vexyuk   (the table for #)
That gives vexyuk, against muxlum above.

One decision about the relation, since deciding is as much a skill as computing. Does
muxlum |> tezreld hold? Read off what muxlum stands over: tezreld, vexyuk and muxlum.
tezreld is among them, so it holds.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of grixmis that come back
unchanged from themselves: tezreld and vexyuk. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by a neutral object for the first operation and closure under the
first operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A1 (closure under the first operation) and A4 (a neutral object for the
first operation).

These results are used again in D6 (the zelmorn), D7 (the korrsol), D10 (aztpyr grixmis)
and T1 (the hobka is the only one of its kind).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

Carry forward rastpon grixmis, grixmis that shenfal and the hobka. Later chapters state
their results in these terms and do not restate the definitions.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 2.
  x012. Name the hobka of the system.
Level 3.
  x008. List every grixmi in the rastpon.
