# Chapter 12. The second operation and how the two interact (2)

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through the second operation keeps the
vashreld intact.

Prerequisites are real here: chapters 4, 7 and 9 supply the notions the statements below
are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
reldjens that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

With two operations the question stops being what each does and becomes how they
interfere. # binds tighter, so the interference shows up whenever a bracket is left off.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T15 rests on D6 (the vashreld), A6 (closure under the second operation) and T3 (the
vashreld is zammorn). The dependence is on the content of those results, not only on
their vocabulary.

## A worked case

Here is (iskbra <> korrreld) <> (kagel <> nakopal), reduced without skipping anything.
    iskbra <> korrreld = korrreld   (the table for <>)
    kagel <> nakopal = nakopal   (the table for <>)
    korrreld <> nakopal = nakopal   (the table for <>)
That leaves nakopal, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take korrreld <> (kagel <> iskbra).
    kagel <> iskbra = iskbra   (the table for <>)
    korrreld <> iskbra = korrreld   (the table for <>)
That gives korrreld, against nakopal above.

One decision about the relation, since deciding is as much a skill as computing. Does
nakopal :: kagel hold? Read off what nakopal stands over: nakopal, kagel, korrreld and
iskbra. kagel is among them, so it holds.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by association of the first operation, closure under the first
operation and closure under the second operation. A system without them is not a system
where these results are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A6 (closure under the second operation), D6 (the
vashreld) and T3 (the vashreld is zammorn).

## Proofs

T15. If x and y lie in the vashreld then so does x # y.

  (1) [T3] The vashreld is already zammorn under <>.
  (2) [A6] The second operation is defined on every pair.
  (3) [D6] The claim is that # respects the vashreld as well.

Checked over 16 cases: every ordered pair from the core. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Established here and safe to use: T15.

## Exercises

This chapter carries no exercises. Nothing in it can be asked about in a way that could
not be answered without reading it, and an exercise like that is worse than none.
