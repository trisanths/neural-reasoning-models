# Chapter 2. Neutral objects and reversal

## Why this chapter

The practical content of this chapter is a neutral object for the first operation, an
absorbing object for the first operation and the system does not have reversal under the
first operation. It is the part that shows up in use.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
wrenhobs that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A4. A neutral object for the first operation. There is a wrenhob iskglim with iskglim ;
x = x ; iskglim = x for every x.

A5. An absorbing object for the first operation. There is a wrenhob ovipyr with ovipyr ;
x = x ; ovipyr = ovipyr for every x.

## The shape of it

Neutrality is a strong condition disguised as a weak one. It fixes a single wrenhob and,
through that, constrains everything that can combine with it.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R1 rests on S2 (the Espadri combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Here is (ovipyr ; tuisk) ; (xilfal ; iskglim), reduced without skipping anything.
    ovipyr ; tuisk = ovipyr   (the table for ;)
    xilfal ; iskglim = xilfal   (the table for ;)
    ovipyr ; xilfal = ovipyr   (the table for ;)
That leaves ovipyr, and no other reading of the notation gives anything else.

A companion case, tuisk ; (xilfal ; ovipyr), to show what the brackets are doing.
    xilfal ; ovipyr = ovipyr   (the table for ;)
    tuisk ; ovipyr = ovipyr   (the table for ;)
That gives ovipyr, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
iskglim >- ovipyr hold? Read off what iskglim stands over: iskglim, lornhob, tuisk,
kaglim, xilfal and ovipyr. ovipyr is among them, so it holds.

## A case that breaks

R1. Some wrenhob x admits no wrenhob y for which x ; y and y ; x both land on a neutral
object. The case that settles it: x = lornhob. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside S2 (the Espadri combination tables).

These results are used again in D5 (the zamthra) and T1 (the zamthra is the only one of
its kind).

## Proofs

R1. Some wrenhob x admits no wrenhob y for which x ; y and y ; x both land on a neutral object.

  (1) [S2] Take the case x = lornhob, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R1. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 5.
  x015. The following fails in this system: Some wrenhob x admits no wrenhob y for which x ; y and y ; x both land on a neutral object. Name the earliest wrenhob, in the order the wrenhobs were introduced, that witnesses the failure.
