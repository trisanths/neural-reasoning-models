# Chapter 11. Collections that close on themselves (2)

## Why this chapter

The practical content of this chapter is the zelopal, where the korrgel divides the
number of qenjens breaks down and where some qenjen reaches every other breaks down. It
is the part that shows up in use.

Prerequisites are real here: chapters 5, 8 and 10 supply the notions the statements
below are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
qenjens that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D12. The zelopal. The zelopal of the system is the collection of qenjens whose korrgel
is largest.

In this system that picks out shentu and nyrazt, which is 2 of the 5 qenjens.

## The shape of it

Picture the kaduth as what happens when you start with one qenjen and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 5 qenjens, that stops. In this system the sizes it stops at are 1, 2 and 4.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R7 rests on D11 (the korrgel of a qenjen) and T4 (the kaduth of a qenjen is rastdri).
The dependence is on the content of those results, not only on their vocabulary.

R9 rests on D8 (the kaduth of a qenjen) and D11 (the korrgel of a qenjen). Remove any
one of them and the statement stops making sense, not merely stops being provable.

T5 rests on D8 (the kaduth of a qenjen) and T4 (the kaduth of a qenjen is rastdri). The
dependence is on the content of those results, not only on their vocabulary.

T6 rests on D1 (tufal qenjens), D11 (the korrgel of a qenjen) and T4 (the kaduth of a
qenjen is rastdri). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Here is xilzam + cloreld |= nyrazt, reduced without skipping anything.
    cloreld |= nyrazt = nyrazt   (the table for |=)
    xilzam + nyrazt = nyrazt   (the table for +)
So xilzam + cloreld |= nyrazt is nyrazt.

Move the brackets and the work changes. Take cloreld + (nyrazt + xilzam).
    nyrazt + xilzam = nyrazt   (the table for +)
    cloreld + nyrazt = shentu   (the table for +)
That gives shentu, against nyrazt above.

Test cloreld <~ xilzam. The opalglim of cloreld is cloreld, and xilzam lies outside it,
so the relation fails.

## A case that breaks

R7. It is not the case that: For every qenjen x, the korrgel of x divides 5. The case
that settles it: x = shentu, reach = 4, size = 5. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

R9. It is not the case that: There is a qenjen whose kaduth is the whole system. It
fails at largest_span = 4, size = 5. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside D1 (tufal qenjens), D11 (the korrgel of a qenjen), D8 (the kaduth of a
qenjen) and T4 (the kaduth of a qenjen is rastdri).

## Proofs

R7. It is not the case that: For every qenjen x, the korrgel of x divides 5.

  (1) [S2] Take the case x = shentu, reach = 4, size = 5, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

R9. It is not the case that: There is a qenjen whose kaduth is the whole system.

  (1) [S2] Take the case largest_span = 4, size = 5, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T5. If S is rastdri and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 35 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T6. x + x = x holds if and only if [x] contains x alone.

  (1) [D1] If x + x = x then {x} is already closed under +.
  (2) [T4] So [x] = {x} and the korrgel is one.
  (3) [D11] Conversely a span of one object must contain x + x, which is then x.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the zelopal. Later chapters state their results in these terms and do not
restate the definitions.

Established here and safe to use: T5 and T6.

Do not carry forward R7 and R9. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x033. Write down the zelopal in full.
  x034. What is the largest korrgel any qenjen has?
Level 5.
  x035. The following fails in this system: For every qenjen x, the korrgel of x divides 5. Name the earliest qenjen, in the order the qenjens were introduced, that witnesses the failure.
