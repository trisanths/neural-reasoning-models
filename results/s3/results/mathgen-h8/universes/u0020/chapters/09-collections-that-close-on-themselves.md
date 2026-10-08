# Chapter 10. Collections that close on themselves

## Why this chapter

The practical content of this chapter is the duthfal of a shenopal, the thrafex of a
shenopal is quilglim and the tarnvor. It is the part that shows up in use.

Nothing here stands on its own. The arguments lean on chapters 5 and 7, and a reader who
has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
shenopals that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D9. The duthfal of a shenopal. The duthfal of a shenopal x is the number of shenopals in
its thrafex [x].

Worked out for each shenopal: opallorn to 1; qenthra to 2; grixlum to 2; vorpon to 2;
pontu to 2.

D10. The tarnvor. The tarnvor of the system is the collection of shenopals whose duthfal
is largest.

In this system that picks out qenthra, grixlum, vorpon and pontu, which is 4 of the 5
shenopals.

## The shape of it

The right picture for thrafex is a spreading stain rather than a list. Drop one shenopal
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
shenopals depending on where it started.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 shenopals the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T1 rests on D7 (the thrafex of a shenopal) and D3 (quilglim collections). Remove any one
of them and the statement stops making sense, not merely stops being provable.

R11 rests on D9 (the duthfal of a shenopal) and T1 (the thrafex of a shenopal is
quilglim). The dependence is on the content of those results, not only on their
vocabulary.

R14 rests on D7 (the thrafex of a shenopal) and D9 (the duthfal of a shenopal). The
dependence is on the content of those results, not only on their vocabulary.

T2 rests on D7 (the thrafex of a shenopal) and T1 (the thrafex of a shenopal is
quilglim). Remove any one of them and the statement stops making sense, not merely stops
being provable.

T3 rests on D1 (grixka shenopals), D9 (the duthfal of a shenopal) and T1 (the thrafex of
a shenopal is quilglim). The dependence is on the content of those results, not only on
their vocabulary.

## A worked case

Evaluate (opallorn % grixlum) % (qenthra % vorpon). Each line below is one lookup in a
table.
    opallorn % grixlum = opallorn   (the table for %)
    qenthra % vorpon = opallorn   (the table for %)
    opallorn % opallorn = opallorn   (the table for %)
That leaves opallorn, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is grixlum % (qenthra % opallorn) for contrast.
    qenthra % opallorn = qenthra   (the table for %)
    grixlum % qenthra = qenthra   (the table for %)
The value is qenthra, not opallorn.

One decision about the relation, since deciding is as much a skill as computing. Does
pontu :: qenthra hold? Read off what pontu stands over: pontu. qenthra is not among
them, so it fails.

A second case, this time a thrafex. Start from opallorn. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is opallorn, so the
duthfal of opallorn is 1.

## A case that breaks

R11. It is not the case that: For every shenopal x, the duthfal of x divides 5. It fails
at x = qenthra, reach = 2, size = 5. One case is enough, and this is the earliest one.

R14. It is not the case that: There is a shenopal whose thrafex is the whole system. The
case that settles it: largest_span = 2, size = 5. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside D1 (grixka shenopals), D3 (quilglim collections) and D7 (the thrafex of a
shenopal).

## Proofs

T1. For every shenopal x, the collection [x] is quilglim.

  (1) [D7] [x] is built by taking x and closing under %.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 125 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

R11. It is not the case that: For every shenopal x, the duthfal of x divides 5.

  (1) [S2] Take the case x = qenthra, reach = 2, size = 5, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

R14. It is not the case that: There is a shenopal whose thrafex is the whole system.

  (1) [S2] Take the case largest_span = 2, size = 5, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T2. If S is quilglim and contains x, then S contains all of [x].

  (1) [D7] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 45 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. x % x = x holds if and only if [x] contains x alone.

  (1) [D1] If x % x = x then {x} is already closed under %.
  (2) [T1] So [x] = {x} and the duthfal is one.
  (3) [D9] Conversely a span of one object must contain x % x, which is then x.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the duthfal of a shenopal and the tarnvor. Later chapters state their
results in these terms and do not restate the definitions.

Established here and safe to use: T1, T2 and T3.

Do not carry forward R11 and R14. These were tested and failed, and the failing cases
are recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x042. What is the duthfal of qenthra?
  x043. How many shenopals lie in [grixlum]?
  x044. How many shenopals lie in [vorpon]?
  x045. What is the duthfal of pontu?
Level 4.
  x050. Write down the tarnvor in full.
  x051. What is the largest duthfal any shenopal has?
Level 5.
  x046. Let z be pontu % qenthra & grixlum. What is the duthfal of z?
  x047. Let z be vorpon % opallorn & grixlum. What is the duthfal of z?
  x048. Let z be (vorpon % grixlum) % pontu. What is the duthfal of z?
  x049. Let z be qenthra % grixlum & pontu. What is the duthfal of z?
  x052. The following fails in this system: For every shenopal x, the duthfal of x divides 5. Name the earliest shenopal, in the order the shenopals were introduced, that witnesses the failure.
