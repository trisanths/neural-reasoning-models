# Chapter 10. Collections that close on themselves (2)

## Why this chapter

So far the aztfals have been objects to be pushed around. This chapter starts asking
what they are like. We take up the korrfex, where some aztfal reaches every other breaks
down and the quilnak is contained in every vintpon collection.

Prerequisites are real here: chapters 4, 7 and 9 supply the notions the statements below
are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
aztfals that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D12. The korrfex. The korrfex of the system is the collection of aztfals whose duthnyr
is largest.

Running the definition over every aztfal leaves korrhob, pyrnak, korrglim, lornjen,
nakqen and aztclo.

## The shape of it

The right picture for quilnak is a spreading stain rather than a list. Drop one aztfal
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 aztfals
depending on where it started.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R4 rests on D8 (the quilnak of a aztfal) and D11 (the duthnyr of a aztfal). Remove any
one of them and the statement stops making sense, not merely stops being provable.

T5 rests on D8 (the quilnak of a aztfal) and T4 (the quilnak of a aztfal is vintpon).
The dependence is on the content of those results, not only on their vocabulary.

T6 rests on D1 (vorduth aztfals), D11 (the duthnyr of a aztfal) and T4 (the quilnak of a
aztfal is vintpon). Remove any one of them and the statement stops making sense, not
merely stops being provable.

T7 rests on D11 (the duthnyr of a aztfal) and T4 (the quilnak of a aztfal is vintpon).
The dependence is on the content of those results, not only on their vocabulary.

## A worked case

Evaluate (pyrnak & korrglim) & (korrhob & lornjen). Each line below is one lookup in a
table.
    pyrnak & korrglim = nakqen   (the table for &)
    korrhob & lornjen = lornjen   (the table for &)
    nakqen & lornjen = aztclo   (the table for &)
That leaves aztclo, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is korrglim & (korrhob & pyrnak) for contrast.
    korrhob & pyrnak = pyrnak   (the table for &)
    korrglim & pyrnak = nakqen   (the table for &)
The value is nakqen, not aztclo.

Test lornjen << korrglim. The tezmi of lornjen is korrhob, pyrnak and lornjen, and
korrglim lies outside it, so the relation fails.

## A case that breaks

R4. It is not the case that: There is a aztfal whose quilnak is the whole system. It
fails at largest_span = 1, size = 6. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: D1 (vorduth aztfals), D11 (the duthnyr of a
aztfal), D8 (the quilnak of a aztfal) and T4 (the quilnak of a aztfal is vintpon).

## Proofs

R4. It is not the case that: There is a aztfal whose quilnak is the whole system.

  (1) [S2] Take the case largest_span = 1, size = 6, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T5. If S is vintpon and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 270 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T6. x & x = x holds if and only if [x] contains x alone.

  (1) [D1] If x & x = x then {x} is already closed under &.
  (2) [T4] So [x] = {x} and the duthnyr is one.
  (3) [D11] Conversely a span of one object must contain x & x, which is then x.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T7. For every aztfal x, the duthnyr of x divides 6.

  (1) [T4] [x] is a vintpon collection.
  (2) [D11] Its size is the duthnyr of x.
  (3) The claim is that this size always divides 6.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the korrfex. Later chapters state their results in these terms and do not
restate the definitions.

The results now available are T5, T6 and T7, each settled by exhaustive check rather
than by argument from analogy.

Explicitly not available: R4. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x030. Which aztfals make up the korrfex? Name them all.
  x032. What is the largest duthnyr any aztfal has?
