# Chapter 4. The second operation and how the two interact

## Why this chapter

We turn to closure under the second operation, association of the second operation and
self combination under the second operation. The treatment is self contained given the
material already established.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about wrenhobs covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A6. Closure under the second operation. For all wrenhobs x and y, x |= y is again a
wrenhob.

A7. Association of the second operation. For all wrenhobs x, y, z: (x |= y) |= z = x |=
(y |= z).

A8. Self combination under the second operation. For every wrenhob x: x |= x = x.

## The shape of it

The interesting content of a two operation system sits in the gap between them: which
one distributes over which, and which wrenhobs are fixed by both.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 wrenhobs the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R4 rests on S2 (the Espadri combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R5 rests on S2 (the Espadri combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R6 rests on S2 (the Espadri combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R7 rests on S2 (the Espadri combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take (iskglim ; tuisk) ; (xilfal ; ovipyr) and work it out one step at a time.
    iskglim ; tuisk = tuisk   (the table for ;)
    xilfal ; ovipyr = ovipyr   (the table for ;)
    tuisk ; ovipyr = ovipyr   (the table for ;)
So (iskglim ; tuisk) ; (xilfal ; ovipyr) is ovipyr.

A companion case, tuisk ; (xilfal ; iskglim), to show what the brackets are doing.
    xilfal ; iskglim = xilfal   (the table for ;)
    tuisk ; xilfal = ovipyr   (the table for ;)
The value is ovipyr. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test iskglim >- tuisk. The solzam of iskglim is iskglim, lornhob, tuisk, kaglim, xilfal
and ovipyr, and tuisk lies inside it, so the relation holds.

## A case that breaks

R4. It is not the case that: For all wrenhobs x and y: x |= y = y |= x. It fails at x =
iskglim, y = lornhob, left = lornhob, right = iskglim. One case is enough, and this is
the earliest one.

R5. There is no wrenhob that leaves every wrenhob unchanged under the second operation.
The case that settles it: reason = no two sided identity exists. Anyone carrying this
claim over from a more familiar system will be wrong here, and wrong in a way that
propagates.

R6. It is not the case that: For all wrenhobs x, y, z: x |= (y ; z) = (x |= y) ; (x |=
z), and the same on the right. It fails at x = lornhob, y = iskglim, z = iskglim, left =
lornhob, right = tuisk. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside S2 (the Espadri combination tables).

These results are used again in T15 (the second operation keeps the vintvint intact).

## Proofs

R4. It is not the case that: For all wrenhobs x and y: x |= y = y |= x.

  (1) [S2] Take the case x = iskglim, y = lornhob, left = lornhob, right = iskglim, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R5. There is no wrenhob that leaves every wrenhob unchanged under the second operation.

  (1) [S2] Take the case reason = no two sided identity exists, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R6. It is not the case that: For all wrenhobs x, y, z: x |= (y ; z) = (x |= y) ; (x |= z), and the same on the right.

  (1) [S2] Take the case x = lornhob, y = iskglim, z = iskglim, left = lornhob, right = tuisk, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R7. It is not the case that: For all wrenhobs x and y: x ; (x |= y) = x and x |= (x ; y) = x.

  (1) [S2] Take the case x = iskglim, y = lornhob, value = lornhob, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R4, R5, R6 and R7. A later argument that quietly assumes one
of these is wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 5.
  x018. The following fails in this system: For all wrenhobs x and y: x |= y = y |= x. Name the earliest wrenhob, in the order the wrenhobs were introduced, that witnesses the failure.
  x019. The following fails in this system: For all wrenhobs x and y: x ; (x |= y) = x and x |= (x ; y) = x. Name the earliest wrenhob, in the order the wrenhobs were introduced, that witnesses the failure.
