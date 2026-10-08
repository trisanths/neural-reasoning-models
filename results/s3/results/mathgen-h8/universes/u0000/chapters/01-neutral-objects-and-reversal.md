# Chapter 2. Neutral objects and reversal

## Why this chapter

We turn to the system does not have a neutral object for the first operation, the system
does not have reversal under the first operation and the system does not have an
absorbing object for the first operation. The treatment is self contained given the
material already established.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about vashumbs covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

The neutral vashumb is the one that does nothing. That sounds trivial and is not: almost
every result in this chapter is an argument about what doing nothing forces.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R3 rests on S2 (the Ponmi combination tables). The dependence is on the content of those
results, not only on their vocabulary.

R4 rests on S2 (the Ponmi combination tables). The dependence is on the content of those
results, not only on their vocabulary.

R7 rests on S2 (the Ponmi combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

## A worked case

Evaluate (korrvex ? glimsib) ? (keldclo ? korrdri). Each line below is one lookup in a
table.
    korrvex ? glimsib = korrvex   (the table for ?)
    keldclo ? korrdri = korrvex   (the table for ?)
    korrvex ? korrvex = korrvex   (the table for ?)
The expression comes to korrvex.

Move the brackets and the work changes. Take glimsib ? (keldclo ? korrvex).
    keldclo ? korrvex = keldclo   (the table for ?)
    glimsib ? keldclo = keldclo   (the table for ?)
That gives keldclo, against korrvex above.

One decision about the relation, since deciding is as much a skill as computing. Does
keldclo %% hobtez hold? Read off what keldclo stands over: korrvex and keldclo. hobtez
is not among them, so it fails.

## A case that breaks

R3. There is no vashumb e with e ? x = x ? e = x for every vashumb x. The case that
settles it: reason = no two sided identity exists. Anyone carrying this claim over from
a more familiar system will be wrong here, and wrong in a way that propagates.

R4. Some vashumb x admits no vashumb y for which x ? y and y ? x both land on a neutral
object. It fails at reason = no identity, so inverses are not defined. One case is
enough, and this is the earliest one.

R7. There is no vashumb z with z ? x = x ? z = z for every vashumb x. It fails at reason
= no absorbing element. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside S2 (the Ponmi combination tables).

## Proofs

R3. There is no vashumb e with e ? x = x ? e = x for every vashumb x.

  (1) [S2] Take the case reason = no two sided identity exists, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R4. Some vashumb x admits no vashumb y for which x ? y and y ? x both land on a neutral object.

  (1) [S2] Take the case reason = no identity, so inverses are not defined, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R7. There is no vashumb z with z ? x = x ? z = z for every vashumb x.

  (1) [S2] Take the case reason = no absorbing element, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R3, R4 and R7. These were tested and failed, and the failing cases
are recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 5.
  x018. The following fails in this system: Some vashumb x admits no vashumb y for which x ? y and y ? x both land on a neutral object. Name the earliest vashumb, in the order the vashumbs were introduced, that witnesses the failure.
