# Chapter 8. Collections that close on themselves

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through the vashnyr of a vintzam, the
zamsol of a vintzam is reldjen and the ponkorr.

Nothing here stands on its own. The arguments lean on chapters 4 and 6, and a reader who
has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
vintzams that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D9. The vashnyr of a vintzam. The vashnyr of a vintzam x is the number of vintzams in
its zamsol [x].

Worked out for each vintzam: hurnvash to 1; duthsib to 2; drishen to 2; pyryuk to 2;
aztka to 2; ovijen to 2.

D10. The ponkorr. The ponkorr of the system is the collection of vintzams whose vashnyr
is largest.

Running the definition over every vintzam leaves duthsib, drishen, pyryuk, aztka and
ovijen.

## The shape of it

The right picture for zamsol is a spreading stain rather than a list. Drop one vintzam
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
vintzams depending on where it started.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 vintzams the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T1 rests on D7 (the zamsol of a vintzam) and D3 (reldjen collections). The dependence is
on the content of those results, not only on their vocabulary.

R15 rests on D7 (the zamsol of a vintzam) and D9 (the vashnyr of a vintzam). The
dependence is on the content of those results, not only on their vocabulary.

T2 rests on D7 (the zamsol of a vintzam) and T1 (the zamsol of a vintzam is reldjen).
The dependence is on the content of those results, not only on their vocabulary.

T3 rests on D1 (shenfal vintzams), D9 (the vashnyr of a vintzam) and T1 (the zamsol of a
vintzam is reldjen). The dependence is on the content of those results, not only on
their vocabulary.

T4 rests on D9 (the vashnyr of a vintzam) and T1 (the zamsol of a vintzam is reldjen).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

## A worked case

Take (aztka : ovijen) : (hurnvash : pyryuk) and work it out one step at a time.
    aztka : ovijen = hurnvash   (the table for :)
    hurnvash : pyryuk = hurnvash   (the table for :)
    hurnvash : hurnvash = hurnvash   (the table for :)
That leaves hurnvash, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take ovijen : (hurnvash : aztka).
    hurnvash : aztka = hurnvash   (the table for :)
    ovijen : hurnvash = ovijen   (the table for :)
The value is ovijen, not hurnvash.

One decision about the relation, since deciding is as much a skill as computing. Does
aztka :: duthsib hold? Read off what aztka stands over: hurnvash. duthsib is not among
them, so it fails.

A second case, this time a zamsol. Start from hurnvash. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is hurnvash, so the
vashnyr of hurnvash is 1.

## A case that breaks

R15. It is not the case that: There is a vintzam whose zamsol is the whole system. The
case that settles it: largest_span = 2, size = 6. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: D1 (shenfal vintzams), D3 (reldjen collections)
and D7 (the zamsol of a vintzam).

## Proofs

T1. For every vintzam x, the collection [x] is reldjen.

  (1) [D7] [x] is built by taking x and closing under :.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 216 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

R15. It is not the case that: There is a vintzam whose zamsol is the whole system.

  (1) [S2] Take the case largest_span = 2, size = 6, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T2. If S is reldjen and contains x, then S contains all of [x].

  (1) [D7] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 66 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. x : x = x holds if and only if [x] contains x alone.

  (1) [D1] If x : x = x then {x} is already closed under :.
  (2) [T1] So [x] = {x} and the vashnyr is one.
  (3) [D9] Conversely a span of one object must contain x : x, which is then x.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T4. For every vintzam x, the vashnyr of x divides 6.

  (1) [T1] [x] is a reldjen collection.
  (2) [D9] Its size is the vashnyr of x.
  (3) The claim is that this size always divides 6.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the vashnyr of a vintzam and the ponkorr. Later chapters state their
results in these terms and do not restate the definitions.

The results now available are T1, T2, T3 and T4, each settled by exhaustive check rather
than by argument from analogy.

Explicitly not available: R15. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x041. How many vintzams lie in [duthsib]?
  x042. What is the vashnyr of drishen?
  x043. What is the vashnyr of pyryuk?
  x044. How many vintzams lie in [aztka]?
  x045. How many vintzams lie in [ovijen]?
Level 4.
  x048. Which vintzams make up the ponkorr? Name them all.
  x050. What is the largest vashnyr any vintzam has?
Level 5.
  x046. Let z be (hurnvash : duthsib) : pyryuk. What is the vashnyr of z?
  x047. Let z be (drishen : ovijen) : drishen. What is the vashnyr of z?
