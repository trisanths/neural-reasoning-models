# Chapter 2. Neutral objects and reversal

## Why this chapter

Anyone using this system to keep track of something will meet the system does not have a
neutral object for the first operation, the system does not have reversal under the
first operation and the system does not have an absorbing object for the first operation
early, whether or not they go looking.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
vintzams that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

The neutral vintzam is the one that does nothing. That sounds trivial and is not: almost
every result in this chapter is an argument about what doing nothing forces.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R3 rests on S2 (the Bravor combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R4 rests on S2 (the Bravor combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

R7 rests on S2 (the Bravor combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Take (hurnvash : pyryuk) : (duthsib : aztka) and work it out one step at a time.
    hurnvash : pyryuk = hurnvash   (the table for :)
    duthsib : aztka = hurnvash   (the table for :)
    hurnvash : hurnvash = hurnvash   (the table for :)
The expression comes to hurnvash.

Bracketing is not cosmetic, so here is pyryuk : (duthsib : hurnvash) for contrast.
    duthsib : hurnvash = duthsib   (the table for :)
    pyryuk : duthsib = drishen   (the table for :)
That gives drishen, against hurnvash above.

One decision about the relation, since deciding is as much a skill as computing. Does
pyryuk :: aztka hold? Read off what pyryuk stands over: hurnvash. aztka is not among
them, so it fails.

## A case that breaks

R3. There is no vintzam e with e : x = x : e = x for every vintzam x. It fails at reason
= no two sided identity exists. One case is enough, and this is the earliest one.

R4. Some vintzam x admits no vintzam y for which x : y and y : x both land on a neutral
object. The case that settles it: reason = no identity, so inverses are not defined.
Anyone carrying this claim over from a more familiar system will be wrong here, and
wrong in a way that propagates.

R7. There is no vintzam z with z : x = x : z = z for every vintzam x. It fails at reason
= no absorbing element. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: S2 (the Bravor combination tables).

## Proofs

R3. There is no vintzam e with e : x = x : e = x for every vintzam x.

  (1) [S2] Take the case reason = no two sided identity exists, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R4. Some vintzam x admits no vintzam y for which x : y and y : x both land on a neutral object.

  (1) [S2] Take the case reason = no identity, so inverses are not defined, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R7. There is no vintzam z with z : x = x : z = z for every vintzam x.

  (1) [S2] Take the case reason = no absorbing element, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R3, R4 and R7. These were tested and failed, and the failing cases
are recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 5.
  x016. The following fails in this system: Some vintzam x admits no vintzam y for which x : y and y : x both land on a neutral object. Name the earliest vintzam, in the order the vintzams were introduced, that witnesses the failure.
