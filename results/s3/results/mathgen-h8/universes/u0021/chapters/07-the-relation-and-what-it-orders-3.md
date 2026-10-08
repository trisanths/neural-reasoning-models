# Chapter 8. The relation and what it orders (3)

## Why this chapter

The results collected here were not found in this order. The umbquil of a lumpon, there
is at most one aztlum and the system has a aztlum came first, and the rest was assembled
around that once the pattern was visible.

Prerequisites are real here: chapters 3 and 5 supply the notions the statements below
are phrased in.

The standard of proof here is exhaustion. A universal claim about lumpons covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

## What is defined here

D8. The umbquil of a lumpon. The umbquil of a lumpon x, written [x], is the smallest
lumvex collection that contains x.

Worked out for each lumpon: glimtez to glimtez; glimkorr to glimtez, glimkorr, nakkorr,
duthwren, kaka and mornhob; nakkorr to glimtez, nakkorr and kaka; duthwren to glimtez
and duthwren; kaka to glimtez, nakkorr and kaka; mornhob to glimtez, glimkorr, nakkorr,
duthwren, kaka and mornhob.

## The shape of it

Picture the umbquil as what happens when you start with one lumpon and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 6 lumpons, that stops. In this system the sizes it stops at are 1, 2, 3 and 6.

Think of >- as pointing downhill. The yukglim of a lumpon is everything downhill of it,
and those shadows here have sizes 1, 2, 3, 4, 5 and 6.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T14 rests on D9 (a aztlum) and A8 (antisymmetry of the relation). The dependence is on
the content of those results, not only on their vocabulary.

T15 rests on D9 (a aztlum) and A10 (comparability of every pair). Remove any one of them
and the statement stops making sense, not merely stops being provable.

T16 rests on D14 (cloka pairs) and A8 (antisymmetry of the relation). Remove any one of
them and the statement stops making sense, not merely stops being provable.

## A worked case

Evaluate (mornhob - kaka) - (nakkorr - glimtez). Each line below is one lookup in a
table.
    mornhob - kaka = duthwren   (the table for -)
    nakkorr - glimtez = nakkorr   (the table for -)
    duthwren - nakkorr = mornhob   (the table for -)
The expression comes to mornhob.

A companion case, kaka - (nakkorr - mornhob), to show what the brackets are doing.
    nakkorr - mornhob = glimkorr   (the table for -)
    kaka - glimkorr = mornhob   (the table for -)
The value is mornhob. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test duthwren >- glimtez. The yukglim of duthwren is duthwren, kaka and mornhob, and
glimtez lies outside it, so the relation fails.

Now compute [glimkorr]. Fold glimkorr against itself, then fold whatever appeared
against everything present, and stop when a round adds nothing. The result is glimtez,
glimkorr, nakkorr, duthwren, kaka and mornhob, of size 6.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by antisymmetry of the relation, closure under the first operation
and comparability of every pair. A system without them is not a system where these
results are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A10 (comparability of every pair), A8 (antisymmetry of the relation), D14
(cloka pairs) and D3 (lumvex collections).

These results are used again in D12 (the duthovi of a lumpon), T6 (the umbquil of a
lumpon is lumvex), T7 (the umbquil is contained in every lumvex collection) and T10 (the
umbquil of a glimfex lumpon stays in the glimfex).

## Proofs

T14. No two distinct lumpons can both be aztlums.

  (1) [D9] Let f and h both be floors.
  (2) [D9] Then f >- h, since h is any object, and h >- f likewise.
  (3) [A8] Antisymmetry forces f = h.

Checked over 36 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T15. Some lumpon aztlums the whole system.

  (1) [A10] Every pair is comparable, so the relation orders the objects into a line.
  (2) [D9] The claim is that the line has a bottom.
  (3) The carrier is finite, so the search over candidates terminates.

Checked over 36 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T16. No two distinct lumpons lie in each other's yukglim.

  (1) [D14] Suppose x and y form a tight pair.
  (2) [A8] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the umbquil of a lumpon. Each of these is used by name
later, so the names are worth learning rather than looking up.

Established here and safe to use: T14, T15 and T16.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x027. List the umbquil of glimkorr.
  x028. List the umbquil of nakkorr.
  x029. List the umbquil of duthwren.
  x030. List the umbquil of kaka.
  x031. List the umbquil of mornhob.
Level 4.
  x032. Let z be duthwren - kaka. List the umbquil of z.
  x033. Let z be nakkorr - glimkorr. List the umbquil of z.
