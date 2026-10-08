# Chapter 9. Combining objects (2)

## Why this chapter

We turn to where every wrenhob is drimi breaks down, every wrenhob lies in the vintvint
and the zamthra lies in the vintvint. The treatment is self contained given the material
already established.

Nothing here stands on its own. The arguments lean on chapters 1, 5, 6 and 7, and a
reader who has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over wrenhobs, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

Two questions sort the wrenhobs quickly. Does combining a wrenhob with itself change it?
For iskglim and ovipyr it does not. Does it matter which side it goes on? For iskglim,
lornhob, tuisk, kaglim, xilfal and ovipyr it does not.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 wrenhobs the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R9 rests on D7 (the lornglim). The dependence is on the content of those results, not
only on their vocabulary.

T14 rests on D6 (the vintvint). The dependence is on the content of those results, not
only on their vocabulary.

T2 rests on D5 (the zamthra) and D6 (the vintvint). Remove any one of them and the
statement stops making sense, not merely stops being provable.

T3 rests on D6 (the vintvint), D3 (yukxil collections) and A2 (association of the first
operation). Remove any one of them and the statement stops making sense, not merely
stops being provable.

T8 rests on D7 (the lornglim) and D3 (yukxil collections). Remove any one of them and
the statement stops making sense, not merely stops being provable.

## A worked case

Evaluate xilfal ; tuisk |= lornhob. Each line below is one lookup in a table.
    tuisk |= lornhob = lornhob   (the table for |=)
    xilfal ; lornhob = ovipyr   (the table for ;)
So xilfal ; tuisk |= lornhob is ovipyr.

Bracketing is not cosmetic, so here is tuisk ; (lornhob ; xilfal) for contrast.
    lornhob ; xilfal = ovipyr   (the table for ;)
    tuisk ; ovipyr = ovipyr   (the table for ;)
That gives ovipyr, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test xilfal >- ovipyr. The solzam of xilfal is xilfal and ovipyr, and ovipyr lies inside
it, so the relation holds.

## A case that breaks

R9. It is not the case that: x ; x = x for every wrenhob x. The case that settles it: x
= lornhob, value = tuisk. Anyone carrying this claim over from a more familiar system
will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation and closure under the first operation. Those are
properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A2 (association of the first operation), D3 (yukxil collections), D5 (the
zamthra) and D6 (the vintvint).

What is built on it later: T7 (the mimux of a vintvint wrenhob stays in the vintvint)
and T15 (the second operation keeps the vintvint intact).

## Proofs

R9. It is not the case that: x ; x = x for every wrenhob x.

  (1) [S2] Take the case x = lornhob, value = tuisk, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T14. Every pair of wrenhobs fexisks.

  (1) [D6] The vintvint is defined by fexisking with everything.
  (2) [D2] The claim is that x ; y = y ; x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T2. The zamthra fexisks with every wrenhob.

  (1) [D5] Let e be the zamthra and x any wrenhob.
  (2) [D5] Then e ; x = x and x ; e = x.
  (3) [D2] So e ; x = x ; e, which is what it means to fexisk.
  (4) [D6] Since x was arbitrary, e belongs to the vintvint.

Checked over 6 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. If x and y both fexisk with every wrenhob, then so does x ; y.

  (1) [D6] Let x and y lie in the vintvint and let z be any wrenhob.
  (2) [A2] Then (x ; y) ; z = x ; (y ; z).
  (3) [D6] Move z past y, then past x, using that each fexisks with everything.
  (4) [D3] So x ; y fexisks with z, and the vintvint is yukxil.

Checked over 36 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

T8. If x and y are both drimi then so is x ; y.

  (1) [D7] Let x and y be drimi.
  (2) [D1] The claim asks whether (x ; y) ; (x ; y) returns x ; y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 36 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Established here and safe to use: T14, T2, T3 and T8.

Explicitly not available: R9. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x044. Name the wrenhobs that make up the lornglim, which is what the result above is a claim about.
Level 5.
  x045. The following fails in this system: x ; x = x for every wrenhob x. Name the earliest wrenhob, in the order the wrenhobs were introduced, that witnesses the failure.
