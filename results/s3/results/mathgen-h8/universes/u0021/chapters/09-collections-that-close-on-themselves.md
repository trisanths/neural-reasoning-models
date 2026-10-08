# Chapter 10. Collections that close on themselves

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through the duthovi of a lumpon, a
lumpon has only one zamduth and the umbquil of a lumpon is lumvex.

Nothing here stands on its own. The arguments lean on chapters 1, 5, 7 and 8, and a
reader who has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
lumpons that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D12. The duthovi of a lumpon. The duthovi of a lumpon x is the number of lumpons in its
umbquil [x].

Worked out for each lumpon: glimtez to 1; glimkorr to 6; nakkorr to 3; duthwren to 2;
kaka to 3; mornhob to 6.

## The shape of it

Picture the umbquil as what happens when you start with one lumpon and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 6 lumpons, that stops. In this system the sizes it stops at are 1, 2, 3 and 6.

The neutral lumpon glimtez is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T3 rests on D11 (the zamduth of a lumpon), A2 (association of the first operation) and
T1 (the tuka is the only one of its kind). Remove any one of them and the statement
stops making sense, not merely stops being provable.

T6 rests on D8 (the umbquil of a lumpon) and D3 (lumvex collections). The dependence is
on the content of those results, not only on their vocabulary.

## A worked case

Take (glimkorr - duthwren) - (kaka - nakkorr) and work it out one step at a time.
    glimkorr - duthwren = kaka   (the table for -)
    kaka - nakkorr = glimtez   (the table for -)
    kaka - glimtez = kaka   (the table for -)
That leaves kaka, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take duthwren - (kaka - glimkorr).
    kaka - glimkorr = mornhob   (the table for -)
    duthwren - mornhob = nakkorr   (the table for -)
That gives nakkorr, against kaka above.

Test kaka >- duthwren. The yukglim of kaka is kaka and mornhob, and duthwren lies
outside it, so the relation fails.

A second case, this time a umbquil. Start from duthwren. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is glimtez and
duthwren, so the duthovi of duthwren is 2.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of lumpons that come back
unchanged from themselves: glimtez. Assuming more of them than that is the mistake to
avoid.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation, closure under the first operation and reversal under
the first operation. Those are properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A2 (association of the first operation), D11 (the zamduth of a lumpon),
D3 (lumvex collections) and D8 (the umbquil of a lumpon).

These results are used again in D13 (the vashopal), T4 (a iskjen lumpon is its own
zamduth), T7 (the umbquil is contained in every lumvex collection) and T8 (a lumpon is
pontez exactly when its duthovi is one).

## Proofs

T3. For every lumpon x there is exactly one zamduth of x.

  (1) [D11] Let y and z both be partners of x.
  (2) [A2] Then y = y - (x - z) = (y - x) - z.
  (3) [D11] Both bracketed products collapse to the neutral object.
  (4) So y = z.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T6. For every lumpon x, the collection [x] is lumvex.

  (1) [D8] [x] is built by taking x and closing under -.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 216 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the duthovi of a lumpon. Later chapters state their results in these terms
and do not restate the definitions.

Established here and safe to use: T3 and T6.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x042. How many lumpons lie in [glimkorr]?
  x043. How many lumpons lie in [nakkorr]?
  x044. What is the duthovi of duthwren?
  x045. What is the duthovi of kaka?
  x046. What is the duthovi of mornhob?
Level 5.
  x047. Let z be (mornhob - kaka) - mornhob. What is the duthovi of z?
  x048. Let z be (duthwren - duthwren) - duthwren. What is the duthovi of z?
  x049. Let z be (glimkorr - glimkorr) - duthwren. What is the duthovi of z?
  x050. Let z be (mornhob - glimtez) - kaka. What is the duthovi of z?
  x051. Let z be (glimkorr - duthwren) - glimtez. What is the duthovi of z?
  x052. Let z be (nakkorr - kaka) - nakkorr. What is the duthovi of z?
