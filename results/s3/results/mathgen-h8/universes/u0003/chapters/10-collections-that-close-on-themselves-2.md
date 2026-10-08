# Chapter 11. Collections that close on themselves (2)

## Why this chapter

The results collected here were not found in this order. The korrrast, where some
wrenhob reaches every other breaks down and where the keldvash divides the number of
wrenhobs breaks down came first, and the rest was assembled around that once the pattern
was visible.

Nothing here stands on its own. The arguments lean on chapters 5, 8 and 10, and a reader
who has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
wrenhobs that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D12. The korrrast. The korrrast of the system is the collection of wrenhobs whose
keldvash is largest.

Running the definition over every wrenhob leaves lornhob.

## The shape of it

Picture the mimux as what happens when you start with one wrenhob and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 6 wrenhobs, that stops. In this system the sizes it stops at are 1, 2, 3 and 5.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R10 rests on D8 (the mimux of a wrenhob) and D11 (the keldvash of a wrenhob). The
dependence is on the content of those results, not only on their vocabulary.

R8 rests on D11 (the keldvash of a wrenhob) and T4 (the mimux of a wrenhob is yukxil).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

T5 rests on D8 (the mimux of a wrenhob) and T4 (the mimux of a wrenhob is yukxil).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

T6 rests on D1 (drimi wrenhobs), D11 (the keldvash of a wrenhob) and T4 (the mimux of a
wrenhob is yukxil). Remove any one of them and the statement stops making sense, not
merely stops being provable.

## A worked case

Here is lornhob ; kaglim |= xilfal, reduced without skipping anything.
    kaglim |= xilfal = xilfal   (the table for |=)
    lornhob ; xilfal = ovipyr   (the table for ;)
The expression comes to ovipyr.

Bracketing is not cosmetic, so here is kaglim ; (xilfal ; lornhob) for contrast.
    xilfal ; lornhob = ovipyr   (the table for ;)
    kaglim ; ovipyr = ovipyr   (the table for ;)
The value is ovipyr. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
tuisk >- tuisk hold? Read off what tuisk stands over: tuisk, kaglim, xilfal and ovipyr.
tuisk is among them, so it holds.

## A case that breaks

R10. It is not the case that: There is a wrenhob whose mimux is the whole system. It
fails at largest_span = 5, size = 6. One case is enough, and this is the earliest one.

R8. It is not the case that: For every wrenhob x, the keldvash of x divides 6. It fails
at x = lornhob, reach = 5, size = 6. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: D1 (drimi wrenhobs), D11 (the keldvash of a
wrenhob), D8 (the mimux of a wrenhob) and T4 (the mimux of a wrenhob is yukxil).

## Proofs

R10. It is not the case that: There is a wrenhob whose mimux is the whole system.

  (1) [S2] Take the case largest_span = 5, size = 6, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

R8. It is not the case that: For every wrenhob x, the keldvash of x divides 6.

  (1) [S2] Take the case x = lornhob, reach = 5, size = 6, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T5. If S is yukxil and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 90 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T6. x ; x = x holds if and only if [x] contains x alone.

  (1) [D1] If x ; x = x then {x} is already closed under ;.
  (2) [T4] So [x] = {x} and the keldvash is one.
  (3) [D11] Conversely a span of one object must contain x ; x, which is then x.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the korrrast. Each of these is used by name later, so
the names are worth learning rather than looking up.

Established here and safe to use: T5 and T6.

Explicitly not available: R10 and R8. A later argument that quietly assumes one of these
is wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x041. Write down the korrrast in full.
  x042. What is the largest keldvash any wrenhob has?
Level 5.
  x043. The following fails in this system: For every wrenhob x, the keldvash of x divides 6. Name the earliest wrenhob, in the order the wrenhobs were introduced, that witnesses the failure.
