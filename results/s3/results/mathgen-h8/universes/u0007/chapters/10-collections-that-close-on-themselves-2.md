# Chapter 11. Collections that close on themselves (2)

## Why this chapter

Work through this chapter with the tables in front of you. It covers the reldumb, the
muxmi of a aztrast thrafex stays in the aztrast and some thrafex reaches every other,
and each claim can be checked by hand.

Nothing here stands on its own. The arguments lean on chapters 5, 7, 8, 9 and 10, and a
reader who has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 3
thrafexs that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D13. The reldumb. The reldumb of the system is the collection of thrafexs whose driglim
is largest.

Running the definition over every thrafex leaves qenmorn and hobzel.

## The shape of it

The right picture for muxmi is a spreading stain rather than a list. Drop one thrafex
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 3
thrafexs depending on where it started.

Two questions sort the thrafexs quickly. Does combining a thrafex with itself change it?
For tuespa it does not. Does it matter which side it goes on? For tuespa, qenmorn and
hobzel it does not.

The neutral thrafex tuespa is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 3 thrafexs the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T10 rests on D8 (the muxmi of a thrafex), D6 (the aztrast) and T5 (the aztrast is
umbbra). Remove any one of them and the statement stops making sense, not merely stops
being provable.

T17 rests on D8 (the muxmi of a thrafex) and D12 (the driglim of a thrafex). Remove any
one of them and the statement stops making sense, not merely stops being provable.

T4 rests on D10 (iskrast thrafexs), D11 (the nyrzel of a thrafex) and T3 (a thrafex has
only one nyrzel). Remove any one of them and the statement stops making sense, not
merely stops being provable.

T7 rests on D8 (the muxmi of a thrafex) and T6 (the muxmi of a thrafex is umbbra). The
dependence is on the content of those results, not only on their vocabulary.

T8 rests on D1 (solka thrafexs), D12 (the driglim of a thrafex) and T6 (the muxmi of a
thrafex is umbbra). Remove any one of them and the statement stops making sense, not
merely stops being provable.

T9 rests on D12 (the driglim of a thrafex) and T6 (the muxmi of a thrafex is umbbra).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

## A worked case

Evaluate hobzel =| hobzel ~ tuespa. Each line below is one lookup in a table.
    hobzel ~ tuespa = hobzel   (the table for ~)
    hobzel =| hobzel = qenmorn   (the table for =|)
So hobzel =| hobzel ~ tuespa is qenmorn.

Bracketing is not cosmetic, so here is hobzel =| (tuespa =| hobzel) for contrast.
    tuespa =| hobzel = hobzel   (the table for =|)
    hobzel =| hobzel = qenmorn   (the table for =|)
The value is qenmorn. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test tuespa =< hobzel. The vextarn of tuespa is tuespa, qenmorn and hobzel, and hobzel
lies inside it, so the relation holds.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of thrafexs that come back
unchanged from themselves: tuespa. Assuming more of them than that is the mistake to
avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by a neutral object for the first operation, association of the
first operation, closure under the first operation and reversal under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

That is not a rhetorical caution. Take the same 3 objects, the same symbols, and a
different table, and T17 and T9 stop holding. The notation survives the substitution and
the mathematics does not.

## Neighbouring results

Read alongside D1 (solka thrafexs), D10 (iskrast thrafexs), D11 (the nyrzel of a
thrafex) and D12 (the driglim of a thrafex).

## Proofs

T10. If x lies in the aztrast then every thrafex of [x] lies in the aztrast.

  (1) [T5] The aztrast is umbbra.
  (2) [D8] [x] is the smallest umbbra collection containing x.
  (3) A smallest such collection sits inside any other, and the aztrast is one.

Checked over 9 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

T17. There is a thrafex whose muxmi is the whole system.

  (1) [D8] Compute [x] for each thrafex in turn.
  (2) [D12] The claim is that some driglim equals 3.
  (3) The search runs over finitely many objects, so it settles.

Checked over 3 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T4. If x =| x is the nyrrast then the nyrzel of x is x itself.

  (1) [D10] Let x be iskrast, so x =| x is the nyrrast.
  (2) [D11] That is exactly the condition for x to be a partner of x.
  (3) [T3] Partners are unique, so no other object can be one.

Checked over 3 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T7. If S is umbbra and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 6 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T8. x =| x = x holds if and only if [x] contains x alone.

  (1) [D1] If x =| x = x then {x} is already closed under =|.
  (2) [T6] So [x] = {x} and the driglim is one.
  (3) [D12] Conversely a span of one object must contain x =| x, which is then x.

Checked over 3 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T9. For every thrafex x, the driglim of x divides 3.

  (1) [T6] [x] is a umbbra collection.
  (2) [D12] Its size is the driglim of x.
  (3) The claim is that this size always divides 3.

Checked over 3 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the reldumb. Later chapters state their results in these terms and do not
restate the definitions.

Established here and safe to use: T10, T17, T4, T7, T8 and T9.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x033. Which thrafexs make up the reldumb? Name them all.
  x034. What is the largest driglim any thrafex has?
  x036. Name a thrafex whose muxmi is the whole system. Give the earliest such thrafex in the order the thrafexs were introduced.
