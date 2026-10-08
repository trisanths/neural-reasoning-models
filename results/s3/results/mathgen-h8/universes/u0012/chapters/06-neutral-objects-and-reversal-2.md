# Chapter 7. Neutral objects and reversal (2)

## Why this chapter

What follows was pieced together backwards. The last item of it, glimshen glimyuks, the
fexsol and the hobkorr, was noticed before anyone had a reason to expect it.

Nothing here stands on its own. The arguments lean on chapters 2 and 5, and a reader who
has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about glimyuks covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D10. Glimshen glimyuks. A glimyuk x is glimshen when x & x equals the muxclo.

In this system that picks out fexvash, which is 1 of the 6 glimyuks.

D6. The fexsol. The fexsol of the system is the collection of glimyuks that shenovi with
every glimyuk.

In this system that picks out fexvash, kamorn, muxreld, quilisk, ovifal and kanyr, that
is, all of them.

D7. The hobkorr. The hobkorr is the collection of all sibtez glimyuks.

In this system that picks out fexvash and kanyr, which is 2 of the 6 glimyuks.

## The shape of it

Two questions sort the glimyuks quickly. Does combining a glimyuk with itself change it?
For fexvash and kanyr it does not. Does it matter which side it goes on? For fexvash,
kamorn, muxreld, quilisk, ovifal and kanyr it does not.

Neutrality is a strong condition disguised as a weak one. It fixes a single glimyuk and,
through that, constrains everything that can combine with it.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R10 rests on D5 (the muxclo). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T1 rests on D5 (the muxclo) and A4 (a neutral object for the first operation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Here is ovifal & fexvash : muxreld, reduced without skipping anything.
    fexvash : muxreld = fexvash   (the table for :)
    ovifal & fexvash = ovifal   (the table for &)
So ovifal & fexvash : muxreld is ovifal.

Bracketing is not cosmetic, so here is fexvash & (muxreld & ovifal) for contrast.
    muxreld & ovifal = kanyr   (the table for &)
    fexvash & kanyr = kanyr   (the table for &)
That gives kanyr, against ovifal above.

Test quilisk >- fexvash. The mornclo of quilisk is quilisk, ovifal and kanyr, and
fexvash lies outside it, so the relation fails.

## A case that breaks

R10. It is not the case that: e & x equals the muxclo for every glimyuk x. It fails at
anchor = fexvash, x = kamorn, value = kamorn. One case is enough, and this is the
earliest one.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of a neutral object for the first operation
and closure under the first operation. Those are properties of this system, not of
systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A4 (a neutral object for the first operation), D1 (sibtez glimyuks), D2
(glimyuks that shenovi) and D5 (the muxclo).

These results are used again in T2 (the muxclo lies in the fexsol), T3 (the fexsol is
tuopal), T7 (the xilvor of a fexsol glimyuk stays in the fexsol) and T8 (the hobkorr is
tuopal).

## Proofs

R10. It is not the case that: e & x equals the muxclo for every glimyuk x.

  (1) [S2] Take the case anchor = fexvash, x = kamorn, value = kamorn, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T1. There is exactly one glimyuk e with e & x = x & e = x for every glimyuk x.

  (1) [D5] Suppose e and f both leave every glimyuk unchanged.
  (2) [A4] Then e & f = f, reading e as neutral on the left.
  (3) [A4] And e & f = e, reading f as neutral on the right.
  (4) So e = f, and the two suppositions describe the same object.

Checked over 36 cases: every object paired with every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: glimshen glimyuks, the fexsol and the hobkorr. Each of
these is used by name later, so the names are worth learning rather than looking up.

Established here and safe to use: T1.

Do not carry forward R10. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x024. Write down the hobkorr in full.
  x033. Which glimyuks make up the glimshen? Name them all.
Level 5.
  x052. The following fails in this system: e & x equals the muxclo for every glimyuk x. Name the earliest glimyuk, in the order the glimyuks were introduced, that witnesses the failure.
