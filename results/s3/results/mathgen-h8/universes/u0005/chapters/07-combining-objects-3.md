# Chapter 8. Combining objects (3)

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is where every jenxil
lies in the glimlum breaks down, where every jenxil is yukwren breaks down and the
rastzam is espagrix.

Nothing here stands on its own. The arguments lean on chapters 4 and 6, and a reader who
has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 3
jenxils that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

Two questions sort the jenxils quickly. Does combining a jenxil with itself change it?
For reldvint it does not. Does it matter which side it goes on? It always does.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R10 rests on D5 (the glimlum). The dependence is on the content of those results, not
only on their vocabulary.

R11 rests on D6 (the rastzam). The dependence is on the content of those results, not
only on their vocabulary.

T4 rests on D6 (the rastzam) and D3 (espagrix collections). The dependence is on the
content of those results, not only on their vocabulary.

## A worked case

Evaluate (reldvint % reldvint) % (zellum % wrenmux). Each line below is one lookup in a
table.
    reldvint % reldvint = reldvint   (the table for %)
    zellum % wrenmux = wrenmux   (the table for %)
    reldvint % wrenmux = reldvint   (the table for %)
So (reldvint % reldvint) % (zellum % wrenmux) is reldvint.

Bracketing is not cosmetic, so here is reldvint % (zellum % reldvint) for contrast.
    zellum % reldvint = zellum   (the table for %)
    reldvint % zellum = reldvint   (the table for %)
That gives reldvint, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test reldvint =< reldvint. The rastqen of reldvint is reldvint, wrenmux and zellum, and
reldvint lies inside it, so the relation holds.

## A case that breaks

R10. It is not the case that: Every pair of jenxils xilwrens. The case that settles it:
x = reldvint, y = wrenmux, left = reldvint, right = wrenmux. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

R11. It is not the case that: x % x = x for every jenxil x. It fails at x = wrenmux,
value = reldvint. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: D3 (espagrix collections), D5 (the glimlum) and
D6 (the rastzam).

## Proofs

R10. It is not the case that: Every pair of jenxils xilwrens.

  (1) [S2] Take the case x = reldvint, y = wrenmux, left = reldvint, right = wrenmux, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 9 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

R11. It is not the case that: x % x = x for every jenxil x.

  (1) [S2] Take the case x = wrenmux, value = reldvint, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 3 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T4. If x and y are both yukwren then so is x % y.

  (1) [D6] Let x and y be yukwren.
  (2) [D1] The claim asks whether (x % y) % (x % y) returns x % y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 9 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Established here and safe to use: T4.

Do not carry forward R10 and R11. These were tested and failed, and the failing cases
are recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x027. This result is about the rastzam. List every jenxil in it.
Level 5.
  x028. The following fails in this system: Every pair of jenxils xilwrens. Name the earliest jenxil, in the order the jenxils were introduced, that witnesses the failure.
