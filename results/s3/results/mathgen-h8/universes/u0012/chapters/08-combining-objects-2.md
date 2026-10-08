# Chapter 9. Combining objects (2)

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through where every glimyuk is sibtez
breaks down, every glimyuk lies in the fexsol and the muxclo lies in the fexsol.

Prerequisites are real here: chapters 1, 5, 6 and 7 supply the notions the statements
below are phrased in.

One habit to adopt: when a statement below quantifies over glimyuks, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

A useful mental split: some glimyuks are inert under the operation and some are not.
fexvash and kanyr come back unchanged when combined with themselves, and fexvash,
kamorn, muxreld, quilisk, ovifal and kanyr commute with everything.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R7 rests on D7 (the hobkorr). The dependence is on the content of those results, not
only on their vocabulary.

T14 rests on D6 (the fexsol). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T2 rests on D5 (the muxclo) and D6 (the fexsol). Remove any one of them and the
statement stops making sense, not merely stops being provable.

T3 rests on D6 (the fexsol), D3 (tuopal collections) and A2 (association of the first
operation). Remove any one of them and the statement stops making sense, not merely
stops being provable.

T8 rests on D7 (the hobkorr) and D3 (tuopal collections). The dependence is on the
content of those results, not only on their vocabulary.

## A worked case

Evaluate kanyr & ovifal : muxreld. Each line below is one lookup in a table.
    ovifal : muxreld = muxreld   (the table for :)
    kanyr & muxreld = kanyr   (the table for &)
The expression comes to kanyr.

Move the brackets and the work changes. Take ovifal & (muxreld & kanyr).
    muxreld & kanyr = kanyr   (the table for &)
    ovifal & kanyr = kanyr   (the table for &)
The value is kanyr. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test fexvash >- kanyr. The mornclo of fexvash is fexvash, kamorn, muxreld, quilisk,
ovifal and kanyr, and kanyr lies inside it, so the relation holds.

## A case that breaks

R7. It is not the case that: x & x = x for every glimyuk x. It fails at x = kamorn,
value = muxreld. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation and closure under the first operation. Those are
properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A2 (association of the first operation), D3 (tuopal collections), D5 (the
muxclo) and D6 (the fexsol).

These results are used again in T7 (the xilvor of a fexsol glimyuk stays in the fexsol)
and T15 (the second operation keeps the fexsol intact).

## Proofs

R7. It is not the case that: x & x = x for every glimyuk x.

  (1) [S2] Take the case x = kamorn, value = muxreld, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T14. Every pair of glimyuks shenovis.

  (1) [D6] The fexsol is defined by shenoviing with everything.
  (2) [D2] The claim is that x & y = y & x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T2. The muxclo shenovis with every glimyuk.

  (1) [D5] Let e be the muxclo and x any glimyuk.
  (2) [D5] Then e & x = x and x & e = x.
  (3) [D2] So e & x = x & e, which is what it means to shenovi.
  (4) [D6] Since x was arbitrary, e belongs to the fexsol.

Checked over 6 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. If x and y both shenovi with every glimyuk, then so does x & y.

  (1) [D6] Let x and y lie in the fexsol and let z be any glimyuk.
  (2) [A2] Then (x & y) & z = x & (y & z).
  (3) [D6] Move z past y, then past x, using that each shenovis with everything.
  (4) [D3] So x & y shenovis with z, and the fexsol is tuopal.

Checked over 36 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

T8. If x and y are both sibtez then so is x & y.

  (1) [D7] Let x and y be sibtez.
  (2) [D1] The claim asks whether (x & y) & (x & y) returns x & y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 36 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Established here and safe to use: T14, T2, T3 and T8.

Explicitly not available: R7. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x045. Name the glimyuks that make up the hobkorr, which is what the result above is a claim about.
Level 5.
  x050. The following fails in this system: x & x = x for every glimyuk x. Name the earliest glimyuk, in the order the glimyuks were introduced, that witnesses the failure.
