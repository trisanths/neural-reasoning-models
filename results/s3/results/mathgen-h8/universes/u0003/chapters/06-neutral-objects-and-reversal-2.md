# Chapter 7. Neutral objects and reversal (2)

## Why this chapter

The practical content of this chapter is muxtez wrenhobs, the vintvint and the lornglim.
It is the part that shows up in use.

Nothing here stands on its own. The arguments lean on chapters 2 and 5, and a reader who
has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about wrenhobs covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D10. Muxtez wrenhobs. A wrenhob x is muxtez when x ; x equals the zamthra.

Running the definition over every wrenhob leaves iskglim.

D6. The vintvint. The vintvint of the system is the collection of wrenhobs that fexisk
with every wrenhob.

Running the definition over every wrenhob leaves iskglim, lornhob, tuisk, kaglim, xilfal
and ovipyr.

D7. The lornglim. The lornglim is the collection of all drimi wrenhobs.

Running the definition over every wrenhob leaves iskglim and ovipyr.

## The shape of it

Two questions sort the wrenhobs quickly. Does combining a wrenhob with itself change it?
For iskglim and ovipyr it does not. Does it matter which side it goes on? For iskglim,
lornhob, tuisk, kaglim, xilfal and ovipyr it does not.

The neutral wrenhob iskglim is the one that does nothing. That sounds trivial and is
not: almost every result in this chapter is an argument about what doing nothing forces.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 wrenhobs the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R12 rests on D5 (the zamthra). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T1 rests on D5 (the zamthra) and A4 (a neutral object for the first operation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Here is kaglim ; ovipyr |= lornhob, reduced without skipping anything.
    ovipyr |= lornhob = lornhob   (the table for |=)
    kaglim ; lornhob = xilfal   (the table for ;)
The expression comes to xilfal.

Bracketing is not cosmetic, so here is ovipyr ; (lornhob ; kaglim) for contrast.
    lornhob ; kaglim = xilfal   (the table for ;)
    ovipyr ; xilfal = ovipyr   (the table for ;)
That gives ovipyr, against xilfal above.

One decision about the relation, since deciding is as much a skill as computing. Does
iskglim >- xilfal hold? Read off what iskglim stands over: iskglim, lornhob, tuisk,
kaglim, xilfal and ovipyr. xilfal is among them, so it holds.

## A case that breaks

R12. It is not the case that: e ; x equals the zamthra for every wrenhob x. The case
that settles it: anchor = iskglim, x = lornhob, value = lornhob. Anyone carrying this
claim over from a more familiar system will be wrong here, and wrong in a way that
propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by a neutral object for the first operation and closure under the
first operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A4 (a neutral object for the first operation),
D1 (drimi wrenhobs), D2 (wrenhobs that fexisk) and D5 (the zamthra).

These results are used again in T2 (the zamthra lies in the vintvint), T3 (the vintvint
is yukxil), T7 (the mimux of a vintvint wrenhob stays in the vintvint) and T8 (the
lornglim is yukxil).

## Proofs

R12. It is not the case that: e ; x equals the zamthra for every wrenhob x.

  (1) [S2] Take the case anchor = iskglim, x = lornhob, value = lornhob, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T1. There is exactly one wrenhob e with e ; x = x ; e = x for every wrenhob x.

  (1) [D5] Suppose e and f both leave every wrenhob unchanged.
  (2) [A4] Then e ; f = f, reading e as neutral on the left.
  (3) [A4] And e ; f = e, reading f as neutral on the right.
  (4) So e = f, and the two suppositions describe the same object.

Checked over 36 cases: every object paired with every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: muxtez wrenhobs, the vintvint and the lornglim. Each
of these is used by name later, so the names are worth learning rather than looking up.

Established here and safe to use: T1.

Do not carry forward R12. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x024. Which wrenhobs make up the lornglim? Name them all.
  x031. Which wrenhobs make up the muxtez? Name them all.
Level 5.
  x046. The following fails in this system: e ; x equals the zamthra for every wrenhob x. Name the earliest wrenhob, in the order the wrenhobs were introduced, that witnesses the failure.
