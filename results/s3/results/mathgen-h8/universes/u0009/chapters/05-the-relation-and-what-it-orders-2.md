# Chapter 6. The relation and what it orders (2)

## Why this chapter

The practical content of this chapter is korrjen pairs, zammorn collections and a
thrapyr. It is the part that shows up in use.

Prerequisites are real here: chapters 1 and 3 supply the notions the statements below
are phrased in.

The standard of proof here is exhaustion. A universal claim about reldjens covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D13. Korrjen pairs. Two distinct reldjens x and y form a korrjen pair when x :: y and y
:: x both hold, that is, when each lies in the drivor of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D3. Zammorn collections. A collection S of reldjens is zammorn when x <> y belongs to S
for every pair x, y drawn from S.

D9. A thrapyr. A reldjen f is a thrapyr when f :: y holds for every reldjen y, that is,
when the drivor of f is the whole system.

Running the definition over every reldjen leaves nakopal.

## The shape of it

Picture the nakgrix as what happens when you start with one reldjen and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 4 reldjens, that stops. In this system the sizes it stops at are 1 and 2.

The relation is easiest to see as a height. Each reldjen casts a drivor over what it
yields to, and the sizes of those shadows here are 1, 2, 3 and 4. No two are the same
size, so the objects line up in a single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 reldjens the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R11 rests on D4 (the drivor of a reldjen). The dependence is on the content of those
results, not only on their vocabulary.

T10 rests on D4 (the drivor of a reldjen) and A12 (transitivity of the relation). The
dependence is on the content of those results, not only on their vocabulary.

## A worked case

Here is (nakopal <> iskbra) <> (korrreld <> kagel), reduced without skipping anything.
    nakopal <> iskbra = nakopal   (the table for <>)
    korrreld <> kagel = korrreld   (the table for <>)
    nakopal <> korrreld = nakopal   (the table for <>)
So (nakopal <> iskbra) <> (korrreld <> kagel) is nakopal.

Bracketing is not cosmetic, so here is iskbra <> (korrreld <> nakopal) for contrast.
    korrreld <> nakopal = nakopal   (the table for <>)
    iskbra <> nakopal = nakopal   (the table for <>)
That gives nakopal, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
iskbra :: kagel hold? Read off what iskbra stands over: iskbra. kagel is not among them,
so it fails.

## A case that breaks

R11. It is not the case that: If x :: y then y :: x. It fails at x = nakopal, y = kagel.
One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by closure under the first operation and transitivity of the
relation. A system without them is not a system where these results are harder to prove;
it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A1 (closure under the first operation), A12 (transitivity of the
relation) and D4 (the drivor of a reldjen).

What is built on it later: D8 (the nakgrix of a reldjen), T3 (the vashreld is zammorn),
T4 (the nakgrix of a reldjen is zammorn) and T9 (the umbka is zammorn).

## Proofs

R11. It is not the case that: If x :: y then y :: x.

  (1) [S2] Take the case x = nakopal, y = kagel, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 16 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T10. If y lies in the drivor of x, then the drivor of y is contained in the drivor of x.

  (1) [D4] Let y satisfy x :: y and let z satisfy y :: z.
  (2) [A12] Transitivity gives x :: z.
  (3) [D4] So every member of the drivor of y is a member of that of x.

Checked over 64 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: korrjen pairs, zammorn collections and a thrapyr. Each
of these is used by name later, so the names are worth learning rather than looking up.

The results now available are T10, each settled by exhaustive check rather than by
argument from analogy.

Explicitly not available: R11. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x014. How many reldjens lie in the smallest zammorn collection containing kagel?
