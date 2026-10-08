# Chapter 8. Combining objects (3)

## Why this chapter

So far the ovimorns have been objects to be pushed around. This chapter starts asking
what they are like. We take up the wrenmi of a ovimorn, the system has a wrenvor and
where every ovimorn is tarnkorr breaks down.

Prerequisites are real here: chapters 1, 3, 4, 5 and 6 supply the notions the statements
below are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
ovimorns that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D8. The wrenmi of a ovimorn. The wrenmi of a ovimorn x, written [x], is the smallest
vexjen collection that contains x.

Worked out for each ovimorn: rastmi to rastmi; bradri to rastmi, bradri, wrenkorr,
tezkeld and muxvor; wrenkorr to rastmi, bradri, wrenkorr, tezkeld and muxvor; tezkeld to
rastmi, bradri, wrenkorr, tezkeld and muxvor; muxvor to rastmi, bradri, wrenkorr,
tezkeld and muxvor.

## The shape of it

The right picture for wrenmi is a spreading stain rather than a list. Drop one ovimorn
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 5
ovimorns depending on where it started.

The relation is easiest to see as a height. Each ovimorn casts a vexvint over what it
governs, and the sizes of those shadows here are 5. Sizes repeat, so the objects do not
line up in single file.

A useful mental split: some ovimorns are inert under the operation and some are not.
rastmi come back unchanged when combined with themselves, and rastmi, bradri, wrenkorr,
tezkeld and muxvor commute with everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 ovimorns the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T14 rests on D9 (a wrenvor) and A9 (comparability of every pair). Remove any one of them
and the statement stops making sense, not merely stops being provable.

R4 rests on D7 (the nakjen). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T11 rests on D7 (the nakjen) and D3 (vexjen collections). The dependence is on the
content of those results, not only on their vocabulary.

T16 rests on D6 (the glimdri). The dependence is on the content of those results, not
only on their vocabulary.

T2 rests on D5 (the wrenglim) and D6 (the glimdri). The dependence is on the content of
those results, not only on their vocabulary.

T5 rests on D6 (the glimdri), D3 (vexjen collections) and A2 (association of the first
operation). Remove any one of them and the statement stops making sense, not merely
stops being provable.

## A worked case

Here is (muxvor : bradri) : (wrenkorr : tezkeld), reduced without skipping anything.
    muxvor : bradri = rastmi   (the table for :)
    wrenkorr : tezkeld = rastmi   (the table for :)
    rastmi : rastmi = rastmi   (the table for :)
The expression comes to rastmi.

Move the brackets and the work changes. Take bradri : (wrenkorr : muxvor).
    wrenkorr : muxvor = bradri   (the table for :)
    bradri : bradri = wrenkorr   (the table for :)
The value is wrenkorr, not rastmi.

Test rastmi :: rastmi. The vexvint of rastmi is rastmi, bradri, wrenkorr, tezkeld and
muxvor, and rastmi lies inside it, so the relation holds.

A second case, this time a wrenmi. Start from wrenkorr. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is rastmi, bradri,
wrenkorr, tezkeld and muxvor, so the korropal of wrenkorr is 5.

## A case that breaks

R4. It is not the case that: x : x = x for every ovimorn x. It fails at x = bradri,
value = wrenkorr. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by a neutral object for the first operation, association of the
first operation, closure under the first operation and comparability of every pair. A
system without them is not a system where these results are harder to prove; it is a
system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A2 (association of the first operation), A9 (comparability of every
pair), D3 (vexjen collections) and D5 (the wrenglim).

These results are used again in D12 (the korropal of a ovimorn), T6 (the wrenmi of a
ovimorn is vexjen), T7 (the wrenmi is contained in every vexjen collection) and T10 (the
wrenmi of a glimdri ovimorn stays in the glimdri).

## Proofs

T14. Some ovimorn wrenvors the whole system.

  (1) [A9] Every pair is comparable, so the relation orders the objects into a line.
  (2) [D9] The claim is that the line has a bottom.
  (3) The carrier is finite, so the search over candidates terminates.

Checked over 25 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

R4. It is not the case that: x : x = x for every ovimorn x.

  (1) [S2] Take the case x = bradri, value = wrenkorr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T11. If x and y are both tarnkorr then so is x : y.

  (1) [D7] Let x and y be tarnkorr.
  (2) [D1] The claim asks whether (x : y) : (x : y) returns x : y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 25 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

T16. Every pair of ovimorns naklorns.

  (1) [D6] The glimdri is defined by naklorning with everything.
  (2) [D2] The claim is that x : y = y : x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T2. The wrenglim naklorns with every ovimorn.

  (1) [D5] Let e be the wrenglim and x any ovimorn.
  (2) [D5] Then e : x = x and x : e = x.
  (3) [D2] So e : x = x : e, which is what it means to naklorn.
  (4) [D6] Since x was arbitrary, e belongs to the glimdri.

Checked over 5 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T5. If x and y both naklorn with every ovimorn, then so does x : y.

  (1) [D6] Let x and y lie in the glimdri and let z be any ovimorn.
  (2) [A2] Then (x : y) : z = x : (y : z).
  (3) [D6] Move z past y, then past x, using that each naklorns with everything.
  (4) [D3] So x : y naklorns with z, and the glimdri is vexjen.

Checked over 25 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the wrenmi of a ovimorn. Each of these is used by name
later, so the names are worth learning rather than looking up.

Established here and safe to use: T14, T11, T16, T2 and T5.

Do not carry forward R4. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x019. List the wrenmi of bradri.
  x020. List the wrenmi of wrenkorr.
  x021. Name every ovimorn in [tezkeld].
  x022. Name every ovimorn in [muxvor].
Level 4.
  x023. Let z be rastmi : wrenkorr. List the wrenmi of z.
  x024. Let z be wrenkorr : wrenkorr. List the wrenmi of z.
  x025. Let z be bradri : bradri. List the wrenmi of z.
  x043. This result is about the nakjen. List every ovimorn in it.
