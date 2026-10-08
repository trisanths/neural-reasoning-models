# Chapter 2. Neutral objects and reversal

## Why this chapter

The results collected here were not found in this order. The system does not have a
neutral object for the first operation, the system does not have reversal under the
first operation and the system does not have an absorbing object for the first operation
came first, and the rest was assembled around that once the pattern was visible.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
zelbras that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

The neutral zelbra is the one that does nothing. That sounds trivial and is not: almost
every result in this chapter is an argument about what doing nothing forces.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 zelbras the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R3 rests on S2 (the Bramorn combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R4 rests on S2 (the Bramorn combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R7 rests on S2 (the Bramorn combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Take (iskmi * isktez) * (cloxil * tarnnyr) and work it out one step at a time.
    iskmi * isktez = cloxil   (the table for *)
    cloxil * tarnnyr = cloxil   (the table for *)
    cloxil * cloxil = tarnnyr   (the table for *)
That leaves tarnnyr, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take isktez * (cloxil * iskmi).
    cloxil * iskmi = tarnnyr   (the table for *)
    isktez * tarnnyr = isktez   (the table for *)
The value is isktez, not tarnnyr.

One decision about the relation, since deciding is as much a skill as computing. Does
cloxil <~ iskmi hold? Read off what cloxil stands over: cloxil, isktez and iskmi. iskmi
is among them, so it holds.

## A case that breaks

R3. There is no zelbra e with e * x = x * e = x for every zelbra x. The case that
settles it: reason = no two sided identity exists. Anyone carrying this claim over from
a more familiar system will be wrong here, and wrong in a way that propagates.

R4. Some zelbra x admits no zelbra y for which x * y and y * x both land on a neutral
object. It fails at reason = no identity, so inverses are not defined. One case is
enough, and this is the earliest one.

R7. There is no zelbra z with z * x = x * z = z for every zelbra x. It fails at reason =
no absorbing element. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside S2 (the Bramorn combination tables).

## Proofs

R3. There is no zelbra e with e * x = x * e = x for every zelbra x.

  (1) [S2] Take the case reason = no two sided identity exists, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R4. Some zelbra x admits no zelbra y for which x * y and y * x both land on a neutral object.

  (1) [S2] Take the case reason = no identity, so inverses are not defined, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R7. There is no zelbra z with z * x = x * z = z for every zelbra x.

  (1) [S2] Take the case reason = no absorbing element, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R3, R4 and R7. These were tested and failed, and the failing cases
are recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 5.
  x013. The following fails in this system: Some zelbra x admits no zelbra y for which x * y and y * x both land on a neutral object. Name the earliest zelbra, in the order the zelbras were introduced, that witnesses the failure.
