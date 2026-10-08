# Chapter 6. Neutral objects and reversal (2)

## Why this chapter

Work through this chapter with the tables in front of you. It covers muxlum driwrens,
the iskkeld and the kami, and each claim can be checked by hand.

Prerequisites are real here: chapters 2 and 4 supply the notions the statements below
are phrased in.

The standard of proof here is exhaustion. A universal claim about driwrens covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D10. Muxlum driwrens. A driwren x is muxlum when x * x equals the keldtu.

Running the definition over every driwren leaves nakquil.

D6. The iskkeld. The iskkeld of the system is the collection of driwrens that rastumb
with every driwren.

Running the definition over every driwren leaves nakquil, soltarn, muxsib, braovi,
yukzel and thraisk.

D7. The kami. The kami is the collection of all opalfal driwrens.

Running the definition over every driwren leaves nakquil, soltarn, muxsib, braovi,
yukzel and thraisk.

## The shape of it

Two questions sort the driwrens quickly. Does combining a driwren with itself change it?
For nakquil, soltarn, muxsib, braovi, yukzel and thraisk it does not. Does it matter
which side it goes on? For nakquil, soltarn, muxsib, braovi, yukzel and thraisk it does
not.

Neutrality is a strong condition disguised as a weak one. It fixes a single driwren and,
through that, constrains everything that can combine with it.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R6 rests on D5 (the keldtu). The dependence is on the content of those results, not only
on their vocabulary.

T1 rests on D5 (the keldtu) and A4 (a neutral object for the first operation). The
dependence is on the content of those results, not only on their vocabulary.

## A worked case

Take (yukzel * braovi) * (muxsib * thraisk) and work it out one step at a time.
    yukzel * braovi = thraisk   (the table for *)
    muxsib * thraisk = thraisk   (the table for *)
    thraisk * thraisk = thraisk   (the table for *)
The expression comes to thraisk.

Move the brackets and the work changes. Take braovi * (muxsib * yukzel).
    muxsib * yukzel = yukzel   (the table for *)
    braovi * yukzel = thraisk   (the table for *)
The value is thraisk. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test yukzel << soltarn. The zelfex of yukzel is nakquil, soltarn, muxsib and yukzel, and
soltarn lies inside it, so the relation holds.

## A case that breaks

R6. It is not the case that: e * x equals the keldtu for every driwren x. The case that
settles it: anchor = nakquil, x = soltarn, value = soltarn. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation
and closure under the first operation. Those are properties of this system, not of
systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A4 (a neutral object for the first operation), D1 (opalfal driwrens), D2
(driwrens that rastumb) and D5 (the keldtu).

What is built on it later: T2 (the keldtu lies in the iskkeld), T3 (the iskkeld is
reldshen), T8 (the ovimorn of a iskkeld driwren stays in the iskkeld) and T9 (the kami
is reldshen).

## Proofs

R6. It is not the case that: e * x equals the keldtu for every driwren x.

  (1) [S2] Take the case anchor = nakquil, x = soltarn, value = soltarn, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T1. There is exactly one driwren e with e * x = x * e = x for every driwren x.

  (1) [D5] Suppose e and f both leave every driwren unchanged.
  (2) [A4] Then e * f = f, reading e as neutral on the left.
  (3) [A4] And e * f = e, reading f as neutral on the right.
  (4) So e = f, and the two suppositions describe the same object.

Checked over 36 cases: every object paired with every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: muxlum driwrens, the iskkeld and the kami. Each of
these is used by name later, so the names are worth learning rather than looking up.

Established here and safe to use: T1.

Explicitly not available: R6. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x018. Write down the iskkeld in full.
  x019. Which driwrens make up the kami? Name them all.
  x022. List every driwren in the muxlum.
Level 5.
  x039. The following fails in this system: e * x equals the keldtu for every driwren x. Name the earliest driwren, in the order the driwrens were introduced, that witnesses the failure.
