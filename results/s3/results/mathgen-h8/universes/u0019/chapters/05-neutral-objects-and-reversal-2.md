# Chapter 6. Neutral objects and reversal (2)

## Why this chapter

The practical content of this chapter is gelpyr opalmis, the zamlorn and the tarnsol. It
is the part that shows up in use.

Nothing here stands on its own. The arguments lean on chapters 2 and 4, and a reader who
has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
opalmis that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D10. Gelpyr opalmis. A opalmi x is gelpyr when x - x equals the sibisk.

In this system that picks out duthzam and qenxil, which is 2 of the 5 opalmis.

D6. The zamlorn. The zamlorn of the system is the collection of opalmis that siblum with
every opalmi.

Running the definition over every opalmi leaves keldsib, duthzam, hobfex, iskxil and
qenxil.

D7. The tarnsol. The tarnsol is the collection of all qenpyr opalmis.

Running the definition over every opalmi leaves keldsib and duthzam.

## The shape of it

Two questions sort the opalmis quickly. Does combining a opalmi with itself change it?
For keldsib and duthzam it does not. Does it matter which side it goes on? For keldsib,
duthzam, hobfex, iskxil and qenxil it does not.

Neutrality is a strong condition disguised as a weak one. It fixes a single opalmi and,
through that, constrains everything that can combine with it.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R11 rests on D5 (the sibisk). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T1 rests on D5 (the sibisk) and A4 (a neutral object for the first operation). The
dependence is on the content of those results, not only on their vocabulary.

## A worked case

Evaluate (qenxil - duthzam) - (hobfex - iskxil). Each line below is one lookup in a
table.
    qenxil - duthzam = qenxil   (the table for -)
    hobfex - iskxil = duthzam   (the table for -)
    qenxil - duthzam = qenxil   (the table for -)
The expression comes to qenxil.

Bracketing is not cosmetic, so here is duthzam - (hobfex - qenxil) for contrast.
    hobfex - qenxil = iskxil   (the table for -)
    duthzam - iskxil = iskxil   (the table for -)
The value is iskxil, not qenxil.

Test iskxil <~ duthzam. The espafex of iskxil is duthzam, and duthzam lies inside it, so
the relation holds.

## A case that breaks

R11. It is not the case that: e - x equals the sibisk for every opalmi x. The case that
settles it: anchor = duthzam, x = keldsib, value = keldsib. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of a neutral object for the first operation
and closure under the first operation. Those are properties of this system, not of
systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A4 (a neutral object for the first operation), D1 (qenpyr opalmis), D2
(opalmis that siblum) and D5 (the sibisk).

These results are used again in T2 (the sibisk lies in the zamlorn), T3 (the zamlorn is
brarast), T7 (the nakyuk of a zamlorn opalmi stays in the zamlorn) and T8 (the tarnsol
is brarast).

## Proofs

R11. It is not the case that: e - x equals the sibisk for every opalmi x.

  (1) [S2] Take the case anchor = duthzam, x = keldsib, value = keldsib, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T1. There is exactly one opalmi e with e - x = x - e = x for every opalmi x.

  (1) [D5] Suppose e and f both leave every opalmi unchanged.
  (2) [A4] Then e - f = f, reading e as neutral on the left.
  (3) [A4] And e - f = e, reading f as neutral on the right.
  (4) So e = f, and the two suppositions describe the same object.

Checked over 25 cases: every object paired with every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward gelpyr opalmis, the zamlorn and the tarnsol. Later chapters state their
results in these terms and do not restate the definitions.

Established here and safe to use: T1.

Explicitly not available: R11. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x027. Which opalmis make up the tarnsol? Name them all.
  x033. Which opalmis make up the gelpyr? Name them all.
Level 5.
  x051. The following fails in this system: e - x equals the sibisk for every opalmi x. Name the earliest opalmi, in the order the opalmis were introduced, that witnesses the failure.
