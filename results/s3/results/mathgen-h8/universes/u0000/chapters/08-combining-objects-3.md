# Chapter 9. Combining objects (3)

## Why this chapter

What follows was pieced together backwards. The last item of it, where every vashumb
lies in the yukfex breaks down, where every vashumb is tarnmux breaks down and the
mimorn is hurnisk, was noticed before anyone had a reason to expect it.

Prerequisites are real here: chapters 5 and 7 supply the notions the statements below
are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
vashumbs that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

Two questions sort the vashumbs quickly. Does combining a vashumb with itself change it?
For korrvex it does not. Does it matter which side it goes on? It always does.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R12 rests on D5 (the yukfex). The dependence is on the content of those results, not
only on their vocabulary.

R13 rests on D6 (the mimorn). The dependence is on the content of those results, not
only on their vocabulary.

T4 rests on D6 (the mimorn) and D3 (hurnisk collections). The dependence is on the
content of those results, not only on their vocabulary.

## A worked case

Evaluate korrdri ? keldclo & korrvex. Each line below is one lookup in a table.
    keldclo & korrvex = keldclo   (the table for &)
    korrdri ? keldclo = hobtez   (the table for ?)
That leaves hobtez, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is keldclo ? (korrvex ? korrdri) for contrast.
    korrvex ? korrdri = korrvex   (the table for ?)
    keldclo ? korrvex = keldclo   (the table for ?)
That gives keldclo, against hobtez above.

One decision about the relation, since deciding is as much a skill as computing. Does
glimsib %% hobtez hold? Read off what glimsib stands over: korrvex, keldclo and glimsib.
hobtez is not among them, so it fails.

## A case that breaks

R12. It is not the case that: Every pair of vashumbs yukdris. It fails at x = korrvex, y
= keldclo, left = korrvex, right = keldclo. One case is enough, and this is the earliest
one.

R13. It is not the case that: x ? x = x for every vashumb x. It fails at x = keldclo,
value = korrvex. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: D3 (hurnisk collections), D5 (the yukfex) and D6
(the mimorn).

## Proofs

R12. It is not the case that: Every pair of vashumbs yukdris.

  (1) [S2] Take the case x = korrvex, y = keldclo, left = korrvex, right = keldclo, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

R13. It is not the case that: x ? x = x for every vashumb x.

  (1) [S2] Take the case x = keldclo, value = korrvex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T4. If x and y are both tarnmux then so is x ? y.

  (1) [D6] Let x and y be tarnmux.
  (2) [D1] The claim asks whether (x ? y) ? (x ? y) returns x ? y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 25 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

The results now available are T4, each settled by exhaustive check rather than by
argument from analogy.

Do not carry forward R12 and R13. These were tested and failed, and the failing cases
are recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x049. This result is about the mimorn. List every vashumb in it.
Level 5.
  x053. The following fails in this system: Every pair of vashumbs yukdris. Name the earliest vashumb, in the order the vashumbs were introduced, that witnesses the failure.
  x054. The following fails in this system: x ? x = x for every vashumb x. Name the earliest vashumb, in the order the vashumbs were introduced, that witnesses the failure.
