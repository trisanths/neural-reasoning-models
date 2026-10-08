# Chapter 4. The second operation and how the two interact

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is closure under the
second operation, association of the second operation and commutation of the second
operation.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

One habit to adopt: when a statement below quantifies over reldjens, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A6. Closure under the second operation. For all reldjens x and y, x # y is again a
reldjen.

A7. Association of the second operation. For all reldjens x, y, z: (x # y) # z = x # (y
# z).

A8. Commutation of the second operation. For all reldjens x and y: x # y = y # x.

A9. A neutral object for the second operation. There is a reldjen nakopal with nakopal #
x = x for every x.

## The shape of it

The interesting content of a two operation system sits in the gap between them: which
one distributes over which, and which reldjens are fixed by both.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 reldjens the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R4 rests on S2 (the Mornyuk combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R5 rests on S2 (the Mornyuk combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R6 rests on S2 (the Mornyuk combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Here is (nakopal <> korrreld) <> (iskbra <> kagel), reduced without skipping anything.
    nakopal <> korrreld = nakopal   (the table for <>)
    iskbra <> kagel = iskbra   (the table for <>)
    nakopal <> iskbra = nakopal   (the table for <>)
That leaves nakopal, and no other reading of the notation gives anything else.

A companion case, korrreld <> (iskbra <> nakopal), to show what the brackets are doing.
    iskbra <> nakopal = nakopal   (the table for <>)
    korrreld <> nakopal = nakopal   (the table for <>)
That gives nakopal, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
nakopal :: nakopal hold? Read off what nakopal stands over: nakopal, kagel, korrreld and
iskbra. nakopal is among them, so it holds.

## A case that breaks

R4. It is not the case that: For every reldjen x: x # x = x. It fails at x = kagel,
value = korrreld. One case is enough, and this is the earliest one.

R5. It is not the case that: For all reldjens x, y, z: x # (y <> z) = (x # y) <> (x #
z), and the same on the right. The case that settles it: x = kagel, y = nakopal, z =
kagel, left = kagel, right = korrreld. Anyone carrying this claim over from a more
familiar system will be wrong here, and wrong in a way that propagates.

R6. It is not the case that: For all reldjens x and y: x <> (x # y) = x and x # (x <> y)
= x. It fails at x = kagel, y = kagel, value = korrreld. One case is enough, and this is
the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: S2 (the Mornyuk combination tables).

These results are used again in T15 (the second operation keeps the vashreld intact).

## Proofs

R4. It is not the case that: For every reldjen x: x # x = x.

  (1) [S2] Take the case x = kagel, value = korrreld, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R5. It is not the case that: For all reldjens x, y, z: x # (y <> z) = (x # y) <> (x # z), and the same on the right.

  (1) [S2] Take the case x = kagel, y = nakopal, z = kagel, left = kagel, right = korrreld, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R6. It is not the case that: For all reldjens x and y: x <> (x # y) = x and x # (x <> y) = x.

  (1) [S2] Take the case x = kagel, y = kagel, value = korrreld, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R4, R5 and R6. These were tested and failed, and the failing cases
are recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 5.
  x011. The following fails in this system: For every reldjen x: x # x = x. Name the earliest reldjen, in the order the reldjens were introduced, that witnesses the failure.
