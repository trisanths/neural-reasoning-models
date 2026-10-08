# Chapter 11. Collections that close on themselves (2)

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through the duthquil, the nyrpon of a
drilorn tezka stays in the drilorn and some tezka reaches every other.

Nothing here stands on its own. The arguments lean on chapters 5, 7, 8, 9 and 10, and a
reader who has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 3
tezkas that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D13. The duthquil. The duthquil of the system is the collection of tezkas whose pyryuk
is largest.

Running the definition over every tezka leaves vorzel and opalfex.

## The shape of it

The right picture for nyrpon is a spreading stain rather than a list. Drop one tezka in,
apply the operation to whatever is wet, repeat. The stain here reaches 1 and 3 tezkas
depending on where it started.

A useful mental split: some tezkas are inert under the operation and some are not.
lumwren come back unchanged when combined with themselves, and lumwren, vorzel and
opalfex commute with everything.

Neutrality is a strong condition disguised as a weak one. It fixes a single tezka and,
through that, constrains everything that can combine with it.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 3 tezkas the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T10 rests on D8 (the nyrpon of a tezka), D6 (the drilorn) and T5 (the drilorn is
qenduth). The dependence is on the content of those results, not only on their
vocabulary.

T17 rests on D8 (the nyrpon of a tezka) and D12 (the pyryuk of a tezka). Remove any one
of them and the statement stops making sense, not merely stops being provable.

T4 rests on D10 (hobthra tezkas), D11 (the tezzam of a tezka) and T3 (a tezka has only
one tezzam). The dependence is on the content of those results, not only on their
vocabulary.

T7 rests on D8 (the nyrpon of a tezka) and T6 (the nyrpon of a tezka is qenduth). The
dependence is on the content of those results, not only on their vocabulary.

T8 rests on D1 (xilvash tezkas), D12 (the pyryuk of a tezka) and T6 (the nyrpon of a
tezka is qenduth). Remove any one of them and the statement stops making sense, not
merely stops being provable.

T9 rests on D12 (the pyryuk of a tezka) and T6 (the nyrpon of a tezka is qenduth).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

## A worked case

Here is lumwren >< vorzel | opalfex, reduced without skipping anything.
    vorzel | opalfex = opalfex   (the table for |)
    lumwren >< opalfex = opalfex   (the table for ><)
The expression comes to opalfex.

Bracketing is not cosmetic, so here is vorzel >< (opalfex >< lumwren) for contrast.
    opalfex >< lumwren = opalfex   (the table for ><)
    vorzel >< opalfex = lumwren   (the table for ><)
The value is lumwren, not opalfex.

Test vorzel <~ lumwren. The tarnopal of vorzel is lumwren, vorzel and opalfex, and
lumwren lies inside it, so the relation holds.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of tezkas that come back
unchanged from themselves: lumwren. Assuming more of them than that is the mistake to
avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation, closure under the first operation and reversal under
the first operation. Those are properties of this system, not of systems in general.

That is not a rhetorical caution. Take the same 3 objects, the same symbols, and a
different table, and T17 and T9 stop holding. The notation survives the substitution and
the mathematics does not.

## Neighbouring results

The material this chapter borrows from: D1 (xilvash tezkas), D10 (hobthra tezkas), D11
(the tezzam of a tezka) and D12 (the pyryuk of a tezka).

## Proofs

T10. If x lies in the drilorn then every tezka of [x] lies in the drilorn.

  (1) [T5] The drilorn is qenduth.
  (2) [D8] [x] is the smallest qenduth collection containing x.
  (3) A smallest such collection sits inside any other, and the drilorn is one.

Checked over 9 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

T17. There is a tezka whose nyrpon is the whole system.

  (1) [D8] Compute [x] for each tezka in turn.
  (2) [D12] The claim is that some pyryuk equals 3.
  (3) The search runs over finitely many objects, so it settles.

Checked over 3 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T4. If x >< x is the yukvex then the tezzam of x is x itself.

  (1) [D10] Let x be hobthra, so x >< x is the yukvex.
  (2) [D11] That is exactly the condition for x to be a partner of x.
  (3) [T3] Partners are unique, so no other object can be one.

Checked over 3 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T7. If S is qenduth and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 6 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T8. x >< x = x holds if and only if [x] contains x alone.

  (1) [D1] If x >< x = x then {x} is already closed under ><.
  (2) [T6] So [x] = {x} and the pyryuk is one.
  (3) [D12] Conversely a span of one object must contain x >< x, which is then x.

Checked over 3 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T9. For every tezka x, the pyryuk of x divides 3.

  (1) [T6] [x] is a qenduth collection.
  (2) [D12] Its size is the pyryuk of x.
  (3) The claim is that this size always divides 3.

Checked over 3 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the duthquil. Each of these is used by name later, so
the names are worth learning rather than looking up.

The results now available are T10, T17, T4, T7, T8 and T9, each settled by exhaustive
check rather than by argument from analogy.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x034. Which tezkas make up the duthquil? Name them all.
  x035. What is the largest pyryuk any tezka has?
  x037. Which tezka, taken earliest in the listed order, has pyryuk equal to 3?
