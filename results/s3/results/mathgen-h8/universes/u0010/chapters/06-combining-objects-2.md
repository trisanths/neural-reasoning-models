# Chapter 7. Combining objects (2)

## Why this chapter

The present chapter develops the shenyuk of a grixmi, the system has a lumsib and where
every grixmi is rastpon breaks down.

Prerequisites are real here: chapters 1, 3, 4, 5 and 6 supply the notions the statements
below are phrased in.

One habit to adopt: when a statement below quantifies over grixmis, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D8. The shenyuk of a grixmi. The shenyuk of a grixmi x, written [x], is the smallest
vintmorn collection that contains x.

Worked out for each grixmi: tezreld to tezreld; vexyuk to vexyuk; muxlum to vexyuk and
muxlum.

## The shape of it

Picture the shenyuk as what happens when you start with one grixmi and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 3 grixmis, that stops. In this system the sizes it stops at are 1 and 2.

Think of |> as pointing downhill. The umbhob of a grixmi is everything downhill of it,
and those shadows here have sizes 1 and 3.

A useful mental split: some grixmis are inert under the operation and some are not.
tezreld and vexyuk come back unchanged when combined with themselves, and tezreld,
vexyuk and muxlum commute with everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 3 grixmis the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T10 rests on D9 (a lumsib) and A8 (comparability of every pair). The dependence is on
the content of those results, not only on their vocabulary.

R6 rests on D7 (the korrsol). The dependence is on the content of those results, not
only on their vocabulary.

T12 rests on D6 (the zelmorn). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T2 rests on D5 (the hobka) and D6 (the zelmorn). The dependence is on the content of
those results, not only on their vocabulary.

T3 rests on D6 (the zelmorn), D3 (vintmorn collections) and A2 (association of the first
operation). The dependence is on the content of those results, not only on their
vocabulary.

T8 rests on D7 (the korrsol) and D3 (vintmorn collections). The dependence is on the
content of those results, not only on their vocabulary.

## A worked case

Evaluate (tezreld # muxlum) # muxlum. Each line below is one lookup in a table.
    tezreld # muxlum = tezreld   (the table for #)
    tezreld # muxlum = tezreld   (the table for #)
That leaves tezreld, and no other reading of the notation gives anything else.

A companion case, muxlum # (muxlum # tezreld), to show what the brackets are doing.
    muxlum # tezreld = tezreld   (the table for #)
    muxlum # tezreld = tezreld   (the table for #)
The value is tezreld. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test vexyuk |> muxlum. The umbhob of vexyuk is tezreld, vexyuk and muxlum, and muxlum
lies inside it, so the relation holds.

Now compute [muxlum]. Fold muxlum against itself, then fold whatever appeared against
everything present, and stop when a round adds nothing. The result is vexyuk and muxlum,
of size 2.

## A case that breaks

R6. It is not the case that: x # x = x for every grixmi x. It fails at x = muxlum, value
= vexyuk. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by a neutral object for the first operation, association of the
first operation, closure under the first operation and comparability of every pair. A
system without them is not a system where these results are harder to prove; it is a
system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A2 (association of the first operation), A8 (comparability of every
pair), D3 (vintmorn collections) and D5 (the hobka).

What is built on it later: D11 (the glimmorn of a grixmi), T4 (the shenyuk of a grixmi
is vintmorn), T5 (the shenyuk is contained in every vintmorn collection) and T7 (the
shenyuk of a zelmorn grixmi stays in the zelmorn).

## Proofs

T10. Some grixmi lumsibs the whole system.

  (1) [A8] Every pair is comparable, so the relation orders the objects into a line.
  (2) [D9] The claim is that the line has a bottom.
  (3) The carrier is finite, so the search over candidates terminates.

Checked over 9 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

R6. It is not the case that: x # x = x for every grixmi x.

  (1) [S2] Take the case x = muxlum, value = vexyuk, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 3 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T12. Every pair of grixmis shenfals.

  (1) [D6] The zelmorn is defined by shenfaling with everything.
  (2) [D2] The claim is that x # y = y # x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 9 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T2. The hobka shenfals with every grixmi.

  (1) [D5] Let e be the hobka and x any grixmi.
  (2) [D5] Then e # x = x and x # e = x.
  (3) [D2] So e # x = x # e, which is what it means to shenfal.
  (4) [D6] Since x was arbitrary, e belongs to the zelmorn.

Checked over 3 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. If x and y both shenfal with every grixmi, then so does x # y.

  (1) [D6] Let x and y lie in the zelmorn and let z be any grixmi.
  (2) [A2] Then (x # y) # z = x # (y # z).
  (3) [D6] Move z past y, then past x, using that each shenfals with everything.
  (4) [D3] So x # y shenfals with z, and the zelmorn is vintmorn.

Checked over 9 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

T8. If x and y are both rastpon then so is x # y.

  (1) [D7] Let x and y be rastpon.
  (2) [D1] The claim asks whether (x # y) # (x # y) returns x # y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 9 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the shenyuk of a grixmi. Later chapters state their results in these terms
and do not restate the definitions.

The results now available are T10, T12, T2, T3 and T8, each settled by exhaustive check
rather than by argument from analogy.

Explicitly not available: R6. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x014. List the shenyuk of muxlum.
Level 4.
  x015. Let z be muxlum # vexyuk. List the shenyuk of z.
  x016. Let z be muxlum # muxlum. List the shenyuk of z.
  x027. Name the grixmis that make up the korrsol, which is what the result above is a claim about.
  x029. Name the lumsib of the system.
Level 5.
  x030. The following fails in this system: x # x = x for every grixmi x. Name the earliest grixmi, in the order the grixmis were introduced, that witnesses the failure.
