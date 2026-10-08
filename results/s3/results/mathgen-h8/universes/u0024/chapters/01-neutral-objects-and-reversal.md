# Chapter 2. Neutral objects and reversal

## Why this chapter

So far the rastvashs have been objects to be pushed around. This chapter starts asking
what they are like. We take up the system does not have a neutral object for the first
operation, the system does not have reversal under the first operation and the system
does not have an absorbing object for the first operation.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
rastvashs that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

Neutrality is a strong condition disguised as a weak one. It fixes a single rastvash
and, through that, constrains everything that can combine with it.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 rastvashs the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R3 rests on S2 (the Hobnak combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

R4 rests on S2 (the Hobnak combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R7 rests on S2 (the Hobnak combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Here is (lumpyr ? rastumb) ? (lumnyr ? opalbra), reduced without skipping anything.
    lumpyr ? rastumb = lumpyr   (the table for ?)
    lumnyr ? opalbra = lumpyr   (the table for ?)
    lumpyr ? lumpyr = lumpyr   (the table for ?)
So (lumpyr ? rastumb) ? (lumnyr ? opalbra) is lumpyr.

Move the brackets and the work changes. Take rastumb ? (lumnyr ? lumpyr).
    lumnyr ? lumpyr = lumnyr   (the table for ?)
    rastumb ? lumnyr = opalbra   (the table for ?)
The value is opalbra, not lumpyr.

One decision about the relation, since deciding is as much a skill as computing. Does
lumpyr >> rastumb hold? Read off what lumpyr stands over: lumpyr. rastumb is not among
them, so it fails.

## A case that breaks

R3. There is no rastvash e with e ? x = x ? e = x for every rastvash x. The case that
settles it: reason = no two sided identity exists. Anyone carrying this claim over from
a more familiar system will be wrong here, and wrong in a way that propagates.

R4. Some rastvash x admits no rastvash y for which x ? y and y ? x both land on a
neutral object. It fails at reason = no identity, so inverses are not defined. One case
is enough, and this is the earliest one.

R7. There is no rastvash z with z ? x = x ? z = z for every rastvash x. It fails at
reason = no absorbing element. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside S2 (the Hobnak combination tables).

## Proofs

R3. There is no rastvash e with e ? x = x ? e = x for every rastvash x.

  (1) [S2] Take the case reason = no two sided identity exists, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R4. Some rastvash x admits no rastvash y for which x ? y and y ? x both land on a neutral object.

  (1) [S2] Take the case reason = no identity, so inverses are not defined, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R7. There is no rastvash z with z ? x = x ? z = z for every rastvash x.

  (1) [S2] Take the case reason = no absorbing element, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R3, R4 and R7. These were tested and failed, and the failing cases
are recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 5.
  x019. The following fails in this system: Some rastvash x admits no rastvash y for which x ? y and y ? x both land on a neutral object. Name the earliest rastvash, in the order the rastvashs were introduced, that witnesses the failure.
