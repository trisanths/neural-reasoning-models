# Chapter 9. Collections that close on themselves

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is the vexisk of a
opalmi, the nakyuk of a opalmi is brarast and the nakyuk of a zamlorn opalmi stays in
the zamlorn.

Nothing here stands on its own. The arguments lean on chapters 5, 6, 7 and 8, and a
reader who has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
opalmis that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D11. The vexisk of a opalmi. The vexisk of a opalmi x is the number of opalmis in its
nakyuk [x].

Worked out for each opalmi: keldsib to 1; duthzam to 1; hobfex to 4; iskxil to 4; qenxil
to 2.

## The shape of it

The right picture for nakyuk is a spreading stain rather than a list. Drop one opalmi
in, apply the operation to whatever is wet, repeat. The stain here reaches 1, 2 and 4
opalmis depending on where it started.

Two questions sort the opalmis quickly. Does combining a opalmi with itself change it?
For keldsib and duthzam it does not. Does it matter which side it goes on? For keldsib,
duthzam, hobfex, iskxil and qenxil it does not.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T4 rests on D8 (the nakyuk of a opalmi) and D3 (brarast collections). Remove any one of
them and the statement stops making sense, not merely stops being provable.

T7 rests on D8 (the nakyuk of a opalmi), D6 (the zamlorn) and T3 (the zamlorn is
brarast). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Here is (qenxil - duthzam) - keldsib, reduced without skipping anything.
    qenxil - duthzam = qenxil   (the table for -)
    qenxil - keldsib = keldsib   (the table for -)
That leaves keldsib, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take duthzam - (keldsib - qenxil).
    keldsib - qenxil = keldsib   (the table for -)
    duthzam - keldsib = keldsib   (the table for -)
The value is keldsib. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test duthzam <~ qenxil. The espafex of duthzam is duthzam, and qenxil lies outside it,
so the relation fails.

Now compute [hobfex]. Fold hobfex against itself, then fold whatever appeared against
everything present, and stop when a round adds nothing. The result is duthzam, hobfex,
iskxil and qenxil, of size 4.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by association of the first operation and closure under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside D3 (brarast collections), D6 (the zamlorn), D8 (the nakyuk of a opalmi)
and T3 (the zamlorn is brarast).

These results are used again in D12 (the duthpon), T5 (the nakyuk is contained in every
brarast collection), T6 (a opalmi is qenpyr exactly when its vexisk is one) and R7
(where the vexisk divides the number of opalmis breaks down).

## Proofs

T4. For every opalmi x, the collection [x] is brarast.

  (1) [D8] [x] is built by taking x and closing under -.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 125 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

T7. If x lies in the zamlorn then every opalmi of [x] lies in the zamlorn.

  (1) [T3] The zamlorn is brarast.
  (2) [D8] [x] is the smallest brarast collection containing x.
  (3) A smallest such collection sits inside any other, and the zamlorn is one.

Checked over 25 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the vexisk of a opalmi. Each of these is used by name
later, so the names are worth learning rather than looking up.

Established here and safe to use: T4 and T7.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x034. How many opalmis lie in [duthzam]?
  x035. How many opalmis lie in [hobfex]?
  x036. How many opalmis lie in [iskxil]?
  x037. What is the vexisk of qenxil?
Level 5.
  x038. Let z be (duthzam - keldsib) - hobfex. What is the vexisk of z?
  x039. Let z be (hobfex - hobfex) - hobfex. What is the vexisk of z?
  x040. Let z be (hobfex - keldsib) - keldsib. What is the vexisk of z?
  x041. Let z be (keldsib - hobfex) - keldsib. What is the vexisk of z?
