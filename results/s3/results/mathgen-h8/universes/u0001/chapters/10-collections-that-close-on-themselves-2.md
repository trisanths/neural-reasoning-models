# Chapter 11. Collections that close on themselves (2)

## Why this chapter

We turn to the rastdri, where the mornzam divides the number of drigrixs breaks down and
where some drigrix reaches every other breaks down. The treatment is self contained
given the material already established.

Prerequisites are real here: chapters 5, 8 and 10 supply the notions the statements
below are phrased in.

One habit to adopt: when a statement below quantifies over drigrixs, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D12. The rastdri. The rastdri of the system is the collection of drigrixs whose mornzam
is largest.

In this system that picks out umbazt, which is 1 of the 5 drigrixs.

## The shape of it

Picture the vintmux as what happens when you start with one drigrix and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 5 drigrixs, that stops. In this system the sizes it stops at are 1, 2 and 4.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R10 rests on D11 (the mornzam of a drigrix) and T4 (the vintmux of a drigrix is vexfex).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

R12 rests on D8 (the vintmux of a drigrix) and D11 (the mornzam of a drigrix). The
dependence is on the content of those results, not only on their vocabulary.

T5 rests on D8 (the vintmux of a drigrix) and T4 (the vintmux of a drigrix is vexfex).
The dependence is on the content of those results, not only on their vocabulary.

T6 rests on D1 (opalrast drigrixs), D11 (the mornzam of a drigrix) and T4 (the vintmux
of a drigrix is vexfex). The dependence is on the content of those results, not only on
their vocabulary.

## A worked case

Here is umbazt @ vashtez + qenvex, reduced without skipping anything.
    vashtez + qenvex = vashtez   (the table for +)
    umbazt @ vashtez = qenvex   (the table for @)
That leaves qenvex, and no other reading of the notation gives anything else.

A companion case, vashtez @ (qenvex @ umbazt), to show what the brackets are doing.
    qenvex @ umbazt = qenvex   (the table for @)
    vashtez @ qenvex = qenvex   (the table for @)
The value is qenvex. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test vashtez :: glimmux. The aztdri of vashtez is solvex, and glimmux lies outside it,
so the relation fails.

## A case that breaks

R10. It is not the case that: For every drigrix x, the mornzam of x divides 5. The case
that settles it: x = umbazt, reach = 4, size = 5. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

R12. It is not the case that: There is a drigrix whose vintmux is the whole system. The
case that settles it: largest_span = 4, size = 5. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: D1 (opalrast drigrixs), D11 (the mornzam of a
drigrix), D8 (the vintmux of a drigrix) and T4 (the vintmux of a drigrix is vexfex).

## Proofs

R10. It is not the case that: For every drigrix x, the mornzam of x divides 5.

  (1) [S2] Take the case x = umbazt, reach = 4, size = 5, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

R12. It is not the case that: There is a drigrix whose vintmux is the whole system.

  (1) [S2] Take the case largest_span = 4, size = 5, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T5. If S is vexfex and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 55 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T6. x @ x = x holds if and only if [x] contains x alone.

  (1) [D1] If x @ x = x then {x} is already closed under @.
  (2) [T4] So [x] = {x} and the mornzam is one.
  (3) [D11] Conversely a span of one object must contain x @ x, which is then x.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the rastdri. Later chapters state their results in these terms and do not
restate the definitions.

The results now available are T5 and T6, each settled by exhaustive check rather than by
argument from analogy.

Do not carry forward R10 and R12. These were tested and failed, and the failing cases
are recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x040. Write down the rastdri in full.
  x041. What is the largest mornzam any drigrix has?
Level 5.
  x042. The following fails in this system: For every drigrix x, the mornzam of x divides 5. Name the earliest drigrix, in the order the drigrixs were introduced, that witnesses the failure.
