# Chapter 5. The relation and what it orders (2)

## Why this chapter

Work through this chapter with the tables in front of you. It covers duthlum pairs,
vexjen collections and a wrenvor, and each claim can be checked by hand.

Prerequisites are real here: chapters 1 and 3 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over ovimorns, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D14. Duthlum pairs. Two distinct ovimorns x and y form a duthlum pair when x :: y and y
:: x both hold, that is, when each lies in the vexvint of the other.

In this system that picks out rastmi, bradri, wrenkorr, tezkeld and muxvor, that is, all
of them.

D3. Vexjen collections. A collection S of ovimorns is vexjen when x : y belongs to S for
every pair x, y drawn from S.

D9. A wrenvor. A ovimorn f is a wrenvor when f :: y holds for every ovimorn y, that is,
when the vexvint of f is the whole system.

Running the definition over every ovimorn leaves rastmi, bradri, wrenkorr, tezkeld and
muxvor.

## The shape of it

The right picture for wrenmi is a spreading stain rather than a list. Drop one ovimorn
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 5
ovimorns depending on where it started.

Think of :: as pointing downhill. The vexvint of a ovimorn is everything downhill of it,
and those shadows here have sizes 5.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 ovimorns the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T13 rests on D4 (the vexvint of a ovimorn) and A8 (transitivity of the relation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

T15 rests on D4 (the vexvint of a ovimorn) and A10 (agreement of the relation with the
first operation). Remove any one of them and the statement stops making sense, not
merely stops being provable.

T18 rests on D4 (the vexvint of a ovimorn). Remove any one of them and the statement
stops making sense, not merely stops being provable.

## A worked case

Here is (rastmi : bradri) : wrenkorr, reduced without skipping anything.
    rastmi : bradri = bradri   (the table for :)
    bradri : wrenkorr = tezkeld   (the table for :)
The expression comes to tezkeld.

A companion case, bradri : (wrenkorr : rastmi), to show what the brackets are doing.
    wrenkorr : rastmi = wrenkorr   (the table for :)
    bradri : wrenkorr = tezkeld   (the table for :)
The value is tezkeld. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test muxvor :: tezkeld. The vexvint of muxvor is rastmi, bradri, wrenkorr, tezkeld and
muxvor, and tezkeld lies inside it, so the relation holds.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of agreement of the relation with the first
operation, closure under the first operation and transitivity of the relation. Those are
properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A1 (closure under the first operation), A10
(agreement of the relation with the first operation), A8 (transitivity of the relation)
and D4 (the vexvint of a ovimorn).

These results are used again in D8 (the wrenmi of a ovimorn), T5 (the glimdri is
vexjen), T6 (the wrenmi of a ovimorn is vexjen) and T11 (the nakjen is vexjen).

## Proofs

T13. If y lies in the vexvint of x, then the vexvint of y is contained in the vexvint of x.

  (1) [D4] Let y satisfy x :: y and let z satisfy y :: z.
  (2) [A8] Transitivity gives x :: z.
  (3) [D4] So every member of the vexvint of y is a member of that of x.

Checked over 125 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T15. If x :: y then (x : z) :: (y : z) for every ovimorn z.

  (1) [D4] Let y lie in the vexvint of x.
  (2) [A10] Compatibility applies the operation to both sides at once.
  (3) Nothing else is needed, since z was arbitrary.

Checked over 125 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T18. If x :: y then y :: x.

  (1) [D4] Symmetry would mean y lies in the vexvint of x exactly when x lies in that of y.
  (2) The listed pairs settle it directly.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward duthlum pairs, vexjen collections and a wrenvor. Later chapters state
their results in these terms and do not restate the definitions.

Established here and safe to use: T13, T15 and T18.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x015. How many ovimorns lie in the smallest vexjen collection containing bradri?
  x016. How many ovimorns lie in the smallest vexjen collection containing wrenkorr?
