# Chapter 10. Collections that close on themselves (2)

## Why this chapter

The present chapter develops the falpyr, where some driwren reaches every other breaks
down and the ovimorn is contained in every reldshen collection.

Nothing here stands on its own. The arguments lean on chapters 4, 7 and 9, and a reader
who has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about driwrens covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D12. The falpyr. The falpyr of the system is the collection of driwrens whose korrquil
is largest.

In this system that picks out nakquil, soltarn, muxsib, braovi, yukzel and thraisk, that
is, all of them.

## The shape of it

Picture the ovimorn as what happens when you start with one driwren and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 6 driwrens, that stops. In this system the sizes it stops at are 1.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 driwrens the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R4 rests on D8 (the ovimorn of a driwren) and D11 (the korrquil of a driwren). The
dependence is on the content of those results, not only on their vocabulary.

T5 rests on D8 (the ovimorn of a driwren) and T4 (the ovimorn of a driwren is reldshen).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

T6 rests on D1 (opalfal driwrens), D11 (the korrquil of a driwren) and T4 (the ovimorn
of a driwren is reldshen). The dependence is on the content of those results, not only
on their vocabulary.

T7 rests on D11 (the korrquil of a driwren) and T4 (the ovimorn of a driwren is
reldshen). Remove any one of them and the statement stops making sense, not merely stops
being provable.

## A worked case

Evaluate (muxsib * thraisk) * (braovi * nakquil). Each line below is one lookup in a
table.
    muxsib * thraisk = thraisk   (the table for *)
    braovi * nakquil = braovi   (the table for *)
    thraisk * braovi = thraisk   (the table for *)
So (muxsib * thraisk) * (braovi * nakquil) is thraisk.

Bracketing is not cosmetic, so here is thraisk * (braovi * muxsib) for contrast.
    braovi * muxsib = thraisk   (the table for *)
    thraisk * thraisk = thraisk   (the table for *)
That gives thraisk, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test soltarn << thraisk. The zelfex of soltarn is nakquil and soltarn, and thraisk lies
outside it, so the relation fails.

## A case that breaks

R4. It is not the case that: There is a driwren whose ovimorn is the whole system. The
case that settles it: largest_span = 1, size = 6. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside D1 (opalfal driwrens), D11 (the korrquil of a driwren), D8 (the ovimorn
of a driwren) and T4 (the ovimorn of a driwren is reldshen).

## Proofs

R4. It is not the case that: There is a driwren whose ovimorn is the whole system.

  (1) [S2] Take the case largest_span = 1, size = 6, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T5. If S is reldshen and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 270 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T6. x * x = x holds if and only if [x] contains x alone.

  (1) [D1] If x * x = x then {x} is already closed under *.
  (2) [T4] So [x] = {x} and the korrquil is one.
  (3) [D11] Conversely a span of one object must contain x * x, which is then x.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T7. For every driwren x, the korrquil of x divides 6.

  (1) [T4] [x] is a reldshen collection.
  (2) [D11] Its size is the korrquil of x.
  (3) The claim is that this size always divides 6.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the falpyr. Later chapters state their results in these terms and do not
restate the definitions.

The results now available are T5, T6 and T7, each settled by exhaustive check rather
than by argument from analogy.

Do not carry forward R4. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x030. Write down the falpyr in full.
  x032. What is the largest korrquil any driwren has?
