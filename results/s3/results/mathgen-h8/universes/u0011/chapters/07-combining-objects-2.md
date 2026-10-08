# Chapter 8. Combining objects (2)

## Why this chapter

What follows was pieced together backwards. The last item of it, every aztfal lies in
the nakpyr, every aztfal is vorduth and the nyrvor lies in the nakpyr, was noticed
before anyone had a reason to expect it.

Prerequisites are real here: chapters 1, 4, 5 and 6 supply the notions the statements
below are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
aztfals that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

A useful mental split: some aztfals are inert under the operation and some are not.
korrhob, pyrnak, korrglim, lornjen, nakqen and aztclo come back unchanged when combined
with themselves, and korrhob, pyrnak, korrglim, lornjen, nakqen and aztclo commute with
everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 aztfals the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T14 rests on D6 (the nakpyr). The dependence is on the content of those results, not
only on their vocabulary.

T15 rests on D7 (the iskopal). The dependence is on the content of those results, not
only on their vocabulary.

T2 rests on D5 (the nyrvor) and D6 (the nakpyr). The dependence is on the content of
those results, not only on their vocabulary.

T3 rests on D6 (the nakpyr), D3 (vintpon collections) and A2 (association of the first
operation). The dependence is on the content of those results, not only on their
vocabulary.

T9 rests on D7 (the iskopal) and D3 (vintpon collections). The dependence is on the
content of those results, not only on their vocabulary.

## A worked case

Evaluate (aztclo & lornjen) & (korrglim & korrhob). Each line below is one lookup in a
table.
    aztclo & lornjen = aztclo   (the table for &)
    korrglim & korrhob = korrglim   (the table for &)
    aztclo & korrglim = aztclo   (the table for &)
The expression comes to aztclo.

Bracketing is not cosmetic, so here is lornjen & (korrglim & aztclo) for contrast.
    korrglim & aztclo = aztclo   (the table for &)
    lornjen & aztclo = aztclo   (the table for &)
That gives aztclo, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
lornjen << nakqen hold? Read off what lornjen stands over: korrhob, pyrnak and lornjen.
nakqen is not among them, so it fails.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of aztfals that come back
unchanged from themselves: korrhob, pyrnak, korrglim, lornjen, nakqen and aztclo.
Assuming more of them than that is the mistake to avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation and closure under the first operation. Those are
properties of this system, not of systems in general.

That is not a rhetorical caution. Take the same 6 objects, the same symbols, and a
different table, and T15 stop holding. The notation survives the substitution and the
mathematics does not.

## Neighbouring results

Read alongside A2 (association of the first operation), D3 (vintpon collections), D5
(the nyrvor) and D6 (the nakpyr).

What is built on it later: T8 (the quilnak of a nakpyr aztfal stays in the nakpyr).

## Proofs

T14. Every pair of aztfals muxzels.

  (1) [D6] The nakpyr is defined by muxzeling with everything.
  (2) [D2] The claim is that x & y = y & x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T15. x & x = x for every aztfal x.

  (1) [D1] Being vorduth is the condition x & x = x.
  (2) [D7] The claim is that the iskopal is the whole system.
  (3) Only the diagonal of the table is involved.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T2. The nyrvor muxzels with every aztfal.

  (1) [D5] Let e be the nyrvor and x any aztfal.
  (2) [D5] Then e & x = x and x & e = x.
  (3) [D2] So e & x = x & e, which is what it means to muxzel.
  (4) [D6] Since x was arbitrary, e belongs to the nakpyr.

Checked over 6 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. If x and y both muxzel with every aztfal, then so does x & y.

  (1) [D6] Let x and y lie in the nakpyr and let z be any aztfal.
  (2) [A2] Then (x & y) & z = x & (y & z).
  (3) [D6] Move z past y, then past x, using that each muxzels with everything.
  (4) [D3] So x & y muxzels with z, and the nakpyr is vintpon.

Checked over 36 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

T9. If x and y are both vorduth then so is x & y.

  (1) [D7] Let x and y be vorduth.
  (2) [D1] The claim asks whether (x & y) & (x & y) returns x & y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 36 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Established here and safe to use: T14, T15, T2, T3 and T9.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x031. Name the aztfals that make up the nakpyr, which is what the result above is a claim about.
  x034. This result is about the iskopal. List every aztfal in it.
