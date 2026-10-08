# Chapter 5. Combining objects

## Why this chapter

What follows was pieced together backwards. The last item of it, duthnyr reldjens,
reldjens that korrfex and the lornumb, was noticed before anyone had a reason to expect
it.

Nothing here stands on its own. The arguments lean on chapters 1 and 2, and a reader who
has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over reldjens, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D1. Duthnyr reldjens. A reldjen x is called duthnyr when x <> x = x.

Running the definition over every reldjen leaves nakopal and kagel.

D2. Reldjens that korrfex. Two reldjens x and y are said to korrfex when x <> y = y <>
x.

D5. The lornumb. The reldjen kagel is called the lornumb of the system. It is the unique
reldjen that leaves every reldjen unchanged under <>.

Here that is kagel.

## The shape of it

Two questions sort the reldjens quickly. Does combining a reldjen with itself change it?
For nakopal and kagel it does not. Does it matter which side it goes on? For nakopal,
kagel, korrreld and iskbra it does not.

Neutrality is a strong condition disguised as a weak one. It fixes a single reldjen and,
through that, constrains everything that can combine with it.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

This chapter is groundwork. The derivations that use it start in the next one.

## A worked case

Here is nakopal <> kagel # iskbra, reduced without skipping anything.
    kagel # iskbra = nakopal   (the table for #)
    nakopal <> nakopal = nakopal   (the table for <>)
So nakopal <> kagel # iskbra is nakopal.

Move the brackets and the work changes. Take kagel <> (iskbra <> nakopal).
    iskbra <> nakopal = nakopal   (the table for <>)
    kagel <> nakopal = nakopal   (the table for <>)
That gives nakopal, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
nakopal :: nakopal hold? Read off what nakopal stands over: nakopal, kagel, korrreld and
iskbra. nakopal is among them, so it holds.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of reldjens that come back
unchanged from themselves: nakopal and kagel. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation
and closure under the first operation. Those are properties of this system, not of
systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A1 (closure under the first operation) and A4 (a
neutral object for the first operation).

These results are used again in D6 (the vashreld), D7 (the umbka), D10 (driumb reldjens)
and T1 (the lornumb is the only one of its kind).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

Carry forward duthnyr reldjens, reldjens that korrfex and the lornumb. Later chapters
state their results in these terms and do not restate the definitions.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 2.
  x015. Name the lornumb of the system.
Level 3.
  x013. Which reldjens make up the duthnyr? Name them all.
