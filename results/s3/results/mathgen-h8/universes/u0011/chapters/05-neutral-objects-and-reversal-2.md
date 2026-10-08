# Chapter 6. Neutral objects and reversal (2)

## Why this chapter

The present chapter develops zelgel aztfals, the nakpyr and the iskopal.

Prerequisites are real here: chapters 2 and 4 supply the notions the statements below
are phrased in.

The standard of proof here is exhaustion. A universal claim about aztfals covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D10. Zelgel aztfals. A aztfal x is zelgel when x & x equals the nyrvor.

In this system that picks out korrhob, which is 1 of the 6 aztfals.

D6. The nakpyr. The nakpyr of the system is the collection of aztfals that muxzel with
every aztfal.

Running the definition over every aztfal leaves korrhob, pyrnak, korrglim, lornjen,
nakqen and aztclo.

D7. The iskopal. The iskopal is the collection of all vorduth aztfals.

Running the definition over every aztfal leaves korrhob, pyrnak, korrglim, lornjen,
nakqen and aztclo.

## The shape of it

A useful mental split: some aztfals are inert under the operation and some are not.
korrhob, pyrnak, korrglim, lornjen, nakqen and aztclo come back unchanged when combined
with themselves, and korrhob, pyrnak, korrglim, lornjen, nakqen and aztclo commute with
everything.

The neutral aztfal korrhob is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R6 rests on D5 (the nyrvor). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T1 rests on D5 (the nyrvor) and A4 (a neutral object for the first operation). The
dependence is on the content of those results, not only on their vocabulary.

## A worked case

Take (lornjen & korrglim) & (nakqen & korrhob) and work it out one step at a time.
    lornjen & korrglim = aztclo   (the table for &)
    nakqen & korrhob = nakqen   (the table for &)
    aztclo & nakqen = aztclo   (the table for &)
So (lornjen & korrglim) & (nakqen & korrhob) is aztclo.

Move the brackets and the work changes. Take korrglim & (nakqen & lornjen).
    nakqen & lornjen = aztclo   (the table for &)
    korrglim & aztclo = aztclo   (the table for &)
The value is aztclo. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test korrglim << korrglim. The tezmi of korrglim is korrhob and korrglim, and korrglim
lies inside it, so the relation holds.

## A case that breaks

R6. It is not the case that: e & x equals the nyrvor for every aztfal x. The case that
settles it: anchor = korrhob, x = pyrnak, value = pyrnak. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation
and closure under the first operation. Those are properties of this system, not of
systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A4 (a neutral object for the first operation),
D1 (vorduth aztfals), D2 (aztfals that muxzel) and D5 (the nyrvor).

What is built on it later: T2 (the nyrvor lies in the nakpyr), T3 (the nakpyr is
vintpon), T8 (the quilnak of a nakpyr aztfal stays in the nakpyr) and T9 (the iskopal is
vintpon).

## Proofs

R6. It is not the case that: e & x equals the nyrvor for every aztfal x.

  (1) [S2] Take the case anchor = korrhob, x = pyrnak, value = pyrnak, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T1. There is exactly one aztfal e with e & x = x & e = x for every aztfal x.

  (1) [D5] Suppose e and f both leave every aztfal unchanged.
  (2) [A4] Then e & f = f, reading e as neutral on the left.
  (3) [A4] And e & f = e, reading f as neutral on the right.
  (4) So e = f, and the two suppositions describe the same object.

Checked over 36 cases: every object paired with every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward zelgel aztfals, the nakpyr and the iskopal. Later chapters state their
results in these terms and do not restate the definitions.

Established here and safe to use: T1.

Explicitly not available: R6. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x019. List every aztfal in the nakpyr.
  x020. Which aztfals make up the iskopal? Name them all.
  x022. Which aztfals make up the zelgel? Name them all.
Level 5.
  x039. The following fails in this system: e & x equals the nyrvor for every aztfal x. Name the earliest aztfal, in the order the aztfals were introduced, that witnesses the failure.
