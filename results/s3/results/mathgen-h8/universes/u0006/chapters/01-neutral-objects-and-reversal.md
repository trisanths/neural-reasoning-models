# Chapter 2. Neutral objects and reversal

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is the system does
not have a neutral object for the first operation, the system does not have reversal
under the first operation and the system does not have an absorbing object for the first
operation.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

The standard of proof here is exhaustion. A universal claim about grixbras covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

The neutral grixbra is the one that does nothing. That sounds trivial and is not: almost
every result in this chapter is an argument about what doing nothing forces.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R3 rests on S2 (the Vexumb combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R4 rests on S2 (the Vexumb combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

R7 rests on S2 (the Vexumb combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

## A worked case

Take (mika @ mornthra) @ (hobglim @ fexnyr) and work it out one step at a time.
    mika @ mornthra = mika   (the table for @)
    hobglim @ fexnyr = fexnyr   (the table for @)
    mika @ fexnyr = mika   (the table for @)
So (mika @ mornthra) @ (hobglim @ fexnyr) is mika.

Bracketing is not cosmetic, so here is mornthra @ (hobglim @ mika) for contrast.
    hobglim @ mika = hobglim   (the table for @)
    mornthra @ hobglim = hobglim   (the table for @)
That gives hobglim, against mika above.

One decision about the relation, since deciding is as much a skill as computing. Does
hobglim %% fexnyr hold? Read off what hobglim stands over: hobglim. fexnyr is not among
them, so it fails.

## A case that breaks

R3. There is no grixbra e with e @ x = x @ e = x for every grixbra x. It fails at reason
= no two sided identity exists. One case is enough, and this is the earliest one.

R4. Some grixbra x admits no grixbra y for which x @ y and y @ x both land on a neutral
object. The case that settles it: reason = no identity, so inverses are not defined.
Anyone carrying this claim over from a more familiar system will be wrong here, and
wrong in a way that propagates.

R7. There is no grixbra z with z @ x = x @ z = z for every grixbra x. The case that
settles it: reason = no absorbing element. Anyone carrying this claim over from a more
familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside S2 (the Vexumb combination tables).

## Proofs

R3. There is no grixbra e with e @ x = x @ e = x for every grixbra x.

  (1) [S2] Take the case reason = no two sided identity exists, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R4. Some grixbra x admits no grixbra y for which x @ y and y @ x both land on a neutral object.

  (1) [S2] Take the case reason = no identity, so inverses are not defined, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R7. There is no grixbra z with z @ x = x @ z = z for every grixbra x.

  (1) [S2] Take the case reason = no absorbing element, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R3, R4 and R7. A later argument that quietly assumes one of
these is wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 5.
  x021. The following fails in this system: Some grixbra x admits no grixbra y for which x @ y and y @ x both land on a neutral object. Name the earliest grixbra, in the order the grixbras were introduced, that witnesses the failure.
