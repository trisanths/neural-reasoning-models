# Chapter 7. Neutral objects and reversal (2)

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through driumb reldjens, the vashreld
and the umbka.

Prerequisites are real here: chapters 2 and 5 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over reldjens, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D10. Driumb reldjens. A reldjen x is driumb when x <> x equals the lornumb.

Running the definition over every reldjen leaves kagel and iskbra.

D6. The vashreld. The vashreld of the system is the collection of reldjens that korrfex
with every reldjen.

In this system that picks out nakopal, kagel, korrreld and iskbra, that is, all of them.

D7. The umbka. The umbka is the collection of all duthnyr reldjens.

Running the definition over every reldjen leaves nakopal and kagel.

## The shape of it

Two questions sort the reldjens quickly. Does combining a reldjen with itself change it?
For nakopal and kagel it does not. Does it matter which side it goes on? For nakopal,
kagel, korrreld and iskbra it does not.

The neutral reldjen kagel is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 reldjens the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R12 rests on D5 (the lornumb). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T1 rests on D5 (the lornumb) and A4 (a neutral object for the first operation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Take korrreld <> nakopal # iskbra and work it out one step at a time.
    nakopal # iskbra = iskbra   (the table for #)
    korrreld <> iskbra = korrreld   (the table for <>)
So korrreld <> nakopal # iskbra is korrreld.

Move the brackets and the work changes. Take nakopal <> (iskbra <> korrreld).
    iskbra <> korrreld = korrreld   (the table for <>)
    nakopal <> korrreld = nakopal   (the table for <>)
The value is nakopal, not korrreld.

Test korrreld :: korrreld. The drivor of korrreld is korrreld and iskbra, and korrreld
lies inside it, so the relation holds.

## A case that breaks

R12. It is not the case that: e <> x equals the lornumb for every reldjen x. The case
that settles it: anchor = kagel, x = nakopal, value = nakopal. Anyone carrying this
claim over from a more familiar system will be wrong here, and wrong in a way that
propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation
and closure under the first operation. Those are properties of this system, not of
systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A4 (a neutral object for the first operation),
D1 (duthnyr reldjens), D2 (reldjens that korrfex) and D5 (the lornumb).

What is built on it later: T2 (the lornumb lies in the vashreld), T3 (the vashreld is
zammorn), T8 (the nakgrix of a vashreld reldjen stays in the vashreld) and T9 (the umbka
is zammorn).

## Proofs

R12. It is not the case that: e <> x equals the lornumb for every reldjen x.

  (1) [S2] Take the case anchor = kagel, x = nakopal, value = nakopal, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 4 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T1. There is exactly one reldjen e with e <> x = x <> e = x for every reldjen x.

  (1) [D5] Suppose e and f both leave every reldjen unchanged.
  (2) [A4] Then e <> f = f, reading e as neutral on the left.
  (3) [A4] And e <> f = e, reading f as neutral on the right.
  (4) So e = f, and the two suppositions describe the same object.

Checked over 16 cases: every object paired with every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward driumb reldjens, the vashreld and the umbka. Later chapters state their
results in these terms and do not restate the definitions.

The results now available are T1, each settled by exhaustive check rather than by
argument from analogy.

Do not carry forward R12. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x016. Write down the umbka in full.
  x021. Write down the driumb in full.
Level 5.
  x034. The following fails in this system: e <> x equals the lornumb for every reldjen x. Name the earliest reldjen, in the order the reldjens were introduced, that witnesses the failure.
