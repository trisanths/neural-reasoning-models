# Chapter 2. Neutral objects and reversal

## Why this chapter

The present chapter develops the system does not have a neutral object for the first
operation, the system does not have reversal under the first operation and the system
does not have an absorbing object for the first operation.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 3
jenxils that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

The neutral jenxil is the one that does nothing. That sounds trivial and is not: almost
every result in this chapter is an argument about what doing nothing forces.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 3 jenxils the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R3 rests on S2 (the Tarnsib combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R4 rests on S2 (the Tarnsib combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R7 rests on S2 (the Tarnsib combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Evaluate (reldvint % wrenmux) % (zellum % wrenmux). Each line below is one lookup in a
table.
    reldvint % wrenmux = reldvint   (the table for %)
    zellum % wrenmux = wrenmux   (the table for %)
    reldvint % wrenmux = reldvint   (the table for %)
So (reldvint % wrenmux) % (zellum % wrenmux) is reldvint.

Move the brackets and the work changes. Take wrenmux % (zellum % reldvint).
    zellum % reldvint = zellum   (the table for %)
    wrenmux % zellum = reldvint   (the table for %)
That gives reldvint, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test wrenmux =< zellum. The rastqen of wrenmux is wrenmux and zellum, and zellum lies
inside it, so the relation holds.

## A case that breaks

R3. There is no jenxil e with e % x = x % e = x for every jenxil x. It fails at reason =
no two sided identity exists. One case is enough, and this is the earliest one.

R4. Some jenxil x admits no jenxil y for which x % y and y % x both land on a neutral
object. The case that settles it: reason = no identity, so inverses are not defined.
Anyone carrying this claim over from a more familiar system will be wrong here, and
wrong in a way that propagates.

R7. There is no jenxil z with z % x = x % z = z for every jenxil x. It fails at reason =
no absorbing element. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: S2 (the Tarnsib combination tables).

## Proofs

R3. There is no jenxil e with e % x = x % e = x for every jenxil x.

  (1) [S2] Take the case reason = no two sided identity exists, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 27 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R4. Some jenxil x admits no jenxil y for which x % y and y % x both land on a neutral object.

  (1) [S2] Take the case reason = no identity, so inverses are not defined, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 27 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R7. There is no jenxil z with z % x = x % z = z for every jenxil x.

  (1) [S2] Take the case reason = no absorbing element, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 27 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R3, R4 and R7. A later argument that quietly assumes one of
these is wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 5.
  x012. The following fails in this system: Some jenxil x admits no jenxil y for which x % y and y % x both land on a neutral object. Name the earliest jenxil, in the order the jenxils were introduced, that witnesses the failure.
