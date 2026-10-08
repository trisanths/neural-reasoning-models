# Chapter 12. Collections that close on themselves (2)

## Why this chapter

Anyone using this system to keep track of something will meet the tezyuk, the thrapon of
a tezka naksol stays in the tezka and some naksol reaches every other early, whether or
not they go looking.

Prerequisites are real here: chapters 5, 7, 8, 9, 10 and 11 supply the notions the
statements below are phrased in.

The standard of proof here is exhaustion. A universal claim about naksols covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

## What is defined here

D13. The tezyuk. The tezyuk of the system is the collection of naksols whose gelvex is
largest.

In this system that picks out vexlorn and pyrxil, which is 2 of the 6 naksols.

## The shape of it

The right picture for thrapon is a spreading stain rather than a list. Drop one naksol
in, apply the operation to whatever is wet, repeat. The stain here reaches 1, 2, 3 and 6
naksols depending on where it started.

A useful mental split: some naksols are inert under the operation and some are not.
wrenpyr come back unchanged when combined with themselves, and wrenpyr, vexlorn, vexnak,
glimzam, reldxil and pyrxil commute with everything.

The neutral naksol wrenpyr is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 naksols the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T10 rests on D8 (the thrapon of a naksol), D6 (the tezka) and T5 (the tezka is hobreld).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

T18 rests on D8 (the thrapon of a naksol) and D12 (the gelvex of a naksol). The
dependence is on the content of those results, not only on their vocabulary.

T4 rests on D10 (mornpon naksols), D11 (the bralum of a naksol) and T3 (a naksol has
only one bralum). Remove any one of them and the statement stops making sense, not
merely stops being provable.

T7 rests on D8 (the thrapon of a naksol) and T6 (the thrapon of a naksol is hobreld).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

T8 rests on D1 (aztumb naksols), D12 (the gelvex of a naksol) and T6 (the thrapon of a
naksol is hobreld). Remove any one of them and the statement stops making sense, not
merely stops being provable.

T9 rests on D12 (the gelvex of a naksol) and T6 (the thrapon of a naksol is hobreld).
The dependence is on the content of those results, not only on their vocabulary.

## A worked case

Take (reldxil % vexnak) % (glimzam % pyrxil) and work it out one step at a time.
    reldxil % vexnak = wrenpyr   (the table for %)
    glimzam % pyrxil = vexnak   (the table for %)
    wrenpyr % vexnak = vexnak   (the table for %)
So (reldxil % vexnak) % (glimzam % pyrxil) is vexnak.

Move the brackets and the work changes. Take vexnak % (glimzam % reldxil).
    glimzam % reldxil = vexlorn   (the table for %)
    vexnak % vexlorn = glimzam   (the table for %)
That gives glimzam, against vexnak above.

Test pyrxil >- vexnak. The tufex of pyrxil is pyrxil, and vexnak lies outside it, so the
relation fails.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation, closure under the first operation and reversal under
the first operation. Those are properties of this system, not of systems in general.

That is not a rhetorical caution. Take the same 6 objects, the same symbols, and a
different table, and T18 stop holding. The notation survives the substitution and the
mathematics does not.

## Neighbouring results

The material this chapter borrows from: D1 (aztumb naksols), D10 (mornpon naksols), D11
(the bralum of a naksol) and D12 (the gelvex of a naksol).

## Proofs

T10. If x lies in the tezka then every naksol of [x] lies in the tezka.

  (1) [T5] The tezka is hobreld.
  (2) [D8] [x] is the smallest hobreld collection containing x.
  (3) A smallest such collection sits inside any other, and the tezka is one.

Checked over 36 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

T18. There is a naksol whose thrapon is the whole system.

  (1) [D8] Compute [x] for each naksol in turn.
  (2) [D12] The claim is that some gelvex equals 6.
  (3) The search runs over finitely many objects, so it settles.

Checked over 6 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T4. If x % x is the muxisk then the bralum of x is x itself.

  (1) [D10] Let x be mornpon, so x % x is the muxisk.
  (2) [D11] That is exactly the condition for x to be a partner of x.
  (3) [T3] Partners are unique, so no other object can be one.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T7. If S is hobreld and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 24 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T8. x % x = x holds if and only if [x] contains x alone.

  (1) [D1] If x % x = x then {x} is already closed under %.
  (2) [T6] So [x] = {x} and the gelvex is one.
  (3) [D12] Conversely a span of one object must contain x % x, which is then x.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T9. For every naksol x, the gelvex of x divides 6.

  (1) [T6] [x] is a hobreld collection.
  (2) [D12] Its size is the gelvex of x.
  (3) The claim is that this size always divides 6.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the tezyuk. Later chapters state their results in these terms and do not
restate the definitions.

The results now available are T10, T18, T4, T7, T8 and T9, each settled by exhaustive
check rather than by argument from analogy.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x051. Which naksols make up the tezyuk? Name them all.
  x052. What is the largest gelvex any naksol has?
  x054. Name a naksol whose thrapon is the whole system. Give the earliest such naksol in the order the naksols were introduced.
