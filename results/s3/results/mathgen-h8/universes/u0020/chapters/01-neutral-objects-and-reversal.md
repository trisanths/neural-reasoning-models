# Chapter 2. Neutral objects and reversal

## Why this chapter

We turn to the system does not have a neutral object for the first operation, the system
does not have reversal under the first operation and the system does not have an
absorbing object for the first operation. The treatment is self contained given the
material already established.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about shenopals covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

The neutral shenopal is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R3 rests on S2 (the Vintfex combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R4 rests on S2 (the Vintfex combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R7 rests on S2 (the Vintfex combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take (qenthra % grixlum) % (vorpon % pontu) and work it out one step at a time.
    qenthra % grixlum = opallorn   (the table for %)
    vorpon % pontu = opallorn   (the table for %)
    opallorn % opallorn = opallorn   (the table for %)
The expression comes to opallorn.

Bracketing is not cosmetic, so here is grixlum % (vorpon % qenthra) for contrast.
    vorpon % qenthra = grixlum   (the table for %)
    grixlum % grixlum = opallorn   (the table for %)
The value is opallorn. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
vorpon :: grixlum hold? Read off what vorpon stands over: vorpon and pontu. grixlum is
not among them, so it fails.

## A case that breaks

R3. There is no shenopal e with e % x = x % e = x for every shenopal x. It fails at
reason = no two sided identity exists. One case is enough, and this is the earliest one.

R4. Some shenopal x admits no shenopal y for which x % y and y % x both land on a
neutral object. The case that settles it: reason = no identity, so inverses are not
defined. Anyone carrying this claim over from a more familiar system will be wrong here,
and wrong in a way that propagates.

R7. There is no shenopal z with z % x = x % z = z for every shenopal x. The case that
settles it: reason = no absorbing element. Anyone carrying this claim over from a more
familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside S2 (the Vintfex combination tables).

## Proofs

R3. There is no shenopal e with e % x = x % e = x for every shenopal x.

  (1) [S2] Take the case reason = no two sided identity exists, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R4. Some shenopal x admits no shenopal y for which x % y and y % x both land on a neutral object.

  (1) [S2] Take the case reason = no identity, so inverses are not defined, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R7. There is no shenopal z with z % x = x % z = z for every shenopal x.

  (1) [S2] Take the case reason = no absorbing element, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R3, R4 and R7. A later argument that quietly assumes one of
these is wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 5.
  x022. The following fails in this system: Some shenopal x admits no shenopal y for which x % y and y % x both land on a neutral object. Name the earliest shenopal, in the order the shenopals were introduced, that witnesses the failure.
