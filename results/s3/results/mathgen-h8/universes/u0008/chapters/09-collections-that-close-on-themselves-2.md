# Chapter 10. Collections that close on themselves (2)

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is the kajen, the
wrenmi of a glimdri ovimorn stays in the glimdri and some ovimorn reaches every other.

Prerequisites are real here: chapters 4, 6, 7, 8 and 9 supply the notions the statements
below are phrased in.

One habit to adopt: when a statement below quantifies over ovimorns, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D13. The kajen. The kajen of the system is the collection of ovimorns whose korropal is
largest.

In this system that picks out bradri, wrenkorr, tezkeld and muxvor, which is 4 of the 5
ovimorns.

## The shape of it

The right picture for wrenmi is a spreading stain rather than a list. Drop one ovimorn
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 5
ovimorns depending on where it started.

A useful mental split: some ovimorns are inert under the operation and some are not.
rastmi come back unchanged when combined with themselves, and rastmi, bradri, wrenkorr,
tezkeld and muxvor commute with everything.

The neutral ovimorn rastmi is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T10 rests on D8 (the wrenmi of a ovimorn), D6 (the glimdri) and T5 (the glimdri is
vexjen). The dependence is on the content of those results, not only on their
vocabulary.

T17 rests on D8 (the wrenmi of a ovimorn) and D12 (the korropal of a ovimorn). The
dependence is on the content of those results, not only on their vocabulary.

T4 rests on D10 (opaltez ovimorns), D11 (the oviovi of a ovimorn) and T3 (a ovimorn has
only one oviovi). Remove any one of them and the statement stops making sense, not
merely stops being provable.

T7 rests on D8 (the wrenmi of a ovimorn) and T6 (the wrenmi of a ovimorn is vexjen).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

T8 rests on D1 (tarnkorr ovimorns), D12 (the korropal of a ovimorn) and T6 (the wrenmi
of a ovimorn is vexjen). Remove any one of them and the statement stops making sense,
not merely stops being provable.

T9 rests on D12 (the korropal of a ovimorn) and T6 (the wrenmi of a ovimorn is vexjen).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

## A worked case

Take (tezkeld : wrenkorr) : (rastmi : muxvor) and work it out one step at a time.
    tezkeld : wrenkorr = rastmi   (the table for :)
    rastmi : muxvor = muxvor   (the table for :)
    rastmi : muxvor = muxvor   (the table for :)
The expression comes to muxvor.

A companion case, wrenkorr : (rastmi : tezkeld), to show what the brackets are doing.
    rastmi : tezkeld = tezkeld   (the table for :)
    wrenkorr : tezkeld = rastmi   (the table for :)
That gives rastmi, against muxvor above.

One decision about the relation, since deciding is as much a skill as computing. Does
wrenkorr :: muxvor hold? Read off what wrenkorr stands over: rastmi, bradri, wrenkorr,
tezkeld and muxvor. muxvor is among them, so it holds.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by a neutral object for the first operation, association of the
first operation, closure under the first operation and reversal under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

That is not a rhetorical caution. Take the same 5 objects, the same symbols, and a
different table, and T17 and T9 stop holding. The notation survives the substitution and
the mathematics does not.

## Neighbouring results

The material this chapter borrows from: D1 (tarnkorr ovimorns), D10 (opaltez ovimorns),
D11 (the oviovi of a ovimorn) and D12 (the korropal of a ovimorn).

## Proofs

T10. If x lies in the glimdri then every ovimorn of [x] lies in the glimdri.

  (1) [T5] The glimdri is vexjen.
  (2) [D8] [x] is the smallest vexjen collection containing x.
  (3) A smallest such collection sits inside any other, and the glimdri is one.

Checked over 25 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

T17. There is a ovimorn whose wrenmi is the whole system.

  (1) [D8] Compute [x] for each ovimorn in turn.
  (2) [D12] The claim is that some korropal equals 5.
  (3) The search runs over finitely many objects, so it settles.

Checked over 5 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T4. If x : x is the wrenglim then the oviovi of x is x itself.

  (1) [D10] Let x be opaltez, so x : x is the wrenglim.
  (2) [D11] That is exactly the condition for x to be a partner of x.
  (3) [T3] Partners are unique, so no other object can be one.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T7. If S is vexjen and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 10 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T8. x : x = x holds if and only if [x] contains x alone.

  (1) [D1] If x : x = x then {x} is already closed under :.
  (2) [T6] So [x] = {x} and the korropal is one.
  (3) [D12] Conversely a span of one object must contain x : x, which is then x.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T9. For every ovimorn x, the korropal of x divides 5.

  (1) [T6] [x] is a vexjen collection.
  (2) [D12] Its size is the korropal of x.
  (3) The claim is that this size always divides 5.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the kajen. Later chapters state their results in these terms and do not
restate the definitions.

The results now available are T10, T17, T4, T7, T8 and T9, each settled by exhaustive
check rather than by argument from analogy.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x041. Write down the kajen in full.
  x042. What is the largest korropal any ovimorn has?
  x044. Name a ovimorn whose wrenmi is the whole system. Give the earliest such ovimorn in the order the ovimorns were introduced.
