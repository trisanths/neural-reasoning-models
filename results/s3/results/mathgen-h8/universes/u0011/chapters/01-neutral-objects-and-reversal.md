# Chapter 2. Neutral objects and reversal

## Why this chapter

Work through this chapter with the tables in front of you. It covers a neutral object
for the first operation, an absorbing object for the first operation and the system does
not have reversal under the first operation, and each claim can be checked by hand.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
aztfals that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A4. A neutral object for the first operation. There is a aztfal korrhob with korrhob & x
= x & korrhob = x for every x.

A6. An absorbing object for the first operation. There is a aztfal aztclo with aztclo &
x = x & aztclo = aztclo for every x.

## The shape of it

Neutrality is a strong condition disguised as a weak one. It fixes a single aztfal and,
through that, constrains everything that can combine with it.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R1 rests on S2 (the Vintreld combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take (korrglim & nakqen) & (aztclo & pyrnak) and work it out one step at a time.
    korrglim & nakqen = nakqen   (the table for &)
    aztclo & pyrnak = aztclo   (the table for &)
    nakqen & aztclo = aztclo   (the table for &)
So (korrglim & nakqen) & (aztclo & pyrnak) is aztclo.

A companion case, nakqen & (aztclo & korrglim), to show what the brackets are doing.
    aztclo & korrglim = aztclo   (the table for &)
    nakqen & aztclo = aztclo   (the table for &)
That gives aztclo, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test lornjen << korrglim. The tezmi of lornjen is korrhob, pyrnak and lornjen, and
korrglim lies outside it, so the relation fails.

## A case that breaks

R1. Some aztfal x admits no aztfal y for which x & y and y & x both land on a neutral
object. It fails at x = pyrnak. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside S2 (the Vintreld combination tables).

These results are used again in D5 (the nyrvor) and T1 (the nyrvor is the only one of
its kind).

## Proofs

R1. Some aztfal x admits no aztfal y for which x & y and y & x both land on a neutral object.

  (1) [S2] Take the case x = pyrnak, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R1. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 5.
  x008. The following fails in this system: Some aztfal x admits no aztfal y for which x & y and y & x both land on a neutral object. Name the earliest aztfal, in the order the aztfals were introduced, that witnesses the failure.
