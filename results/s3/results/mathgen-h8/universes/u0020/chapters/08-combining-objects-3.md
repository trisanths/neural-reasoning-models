# Chapter 9. Combining objects (3)

## Why this chapter

What follows was pieced together backwards. The last item of it, where every shenopal
lies in the shengel breaks down, where every shenopal is grixka breaks down and the
espanak is quilglim, was noticed before anyone had a reason to expect it.

Prerequisites are real here: chapters 5 and 7 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over shenopals, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

A useful mental split: some shenopals are inert under the operation and some are not.
opallorn come back unchanged when combined with themselves, and none commutes with
everything.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R12 rests on D5 (the shengel). The dependence is on the content of those results, not
only on their vocabulary.

R13 rests on D6 (the espanak). The dependence is on the content of those results, not
only on their vocabulary.

T4 rests on D6 (the espanak) and D3 (quilglim collections). Remove any one of them and
the statement stops making sense, not merely stops being provable.

## A worked case

Take grixlum % opallorn & pontu and work it out one step at a time.
    opallorn & pontu = pontu   (the table for &)
    grixlum % pontu = opallorn   (the table for %)
So grixlum % opallorn & pontu is opallorn.

Move the brackets and the work changes. Take opallorn % (pontu % grixlum).
    pontu % grixlum = grixlum   (the table for %)
    opallorn % grixlum = opallorn   (the table for %)
That gives opallorn, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
qenthra :: pontu hold? Read off what qenthra stands over: qenthra, grixlum, vorpon and
pontu. pontu is among them, so it holds.

## A case that breaks

R12. It is not the case that: Every pair of shenopals gelwrens. The case that settles
it: x = opallorn, y = qenthra, left = opallorn, right = qenthra. Anyone carrying this
claim over from a more familiar system will be wrong here, and wrong in a way that
propagates.

R13. It is not the case that: x % x = x for every shenopal x. The case that settles it:
x = qenthra, value = opallorn. Anyone carrying this claim over from a more familiar
system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by closure under the first operation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: D3 (quilglim collections), D5 (the shengel) and
D6 (the espanak).

## Proofs

R12. It is not the case that: Every pair of shenopals gelwrens.

  (1) [S2] Take the case x = opallorn, y = qenthra, left = opallorn, right = qenthra, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

R13. It is not the case that: x % x = x for every shenopal x.

  (1) [S2] Take the case x = qenthra, value = opallorn, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T4. If x and y are both grixka then so is x % y.

  (1) [D6] Let x and y be grixka.
  (2) [D1] The claim asks whether (x % y) % (x % y) returns x % y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 25 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Established here and safe to use: T4.

Explicitly not available: R12 and R13. A later argument that quietly assumes one of
these is wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x053. This result is about the espanak. List every shenopal in it.
Level 5.
  x058. The following fails in this system: Every pair of shenopals gelwrens. Name the earliest shenopal, in the order the shenopals were introduced, that witnesses the failure.
  x059. The following fails in this system: x % x = x for every shenopal x. Name the earliest shenopal, in the order the shenopals were introduced, that witnesses the failure.
