# Chapter 7. Combining objects (3)

## Why this chapter

Anyone using this system to keep track of something will meet where every vintzam lies
in the falwren breaks down, where every vintzam is shenfal breaks down and the vextarn
is reldjen early, whether or not they go looking.

Nothing here stands on its own. The arguments lean on chapters 4 and 6, and a reader who
has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over vintzams, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

Two questions sort the vintzams quickly. Does combining a vintzam with itself change it?
For hurnvash it does not. Does it matter which side it goes on? It always does.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R13 rests on D5 (the falwren). The dependence is on the content of those results, not
only on their vocabulary.

R14 rests on D6 (the vextarn). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T5 rests on D6 (the vextarn) and D3 (reldjen collections). The dependence is on the
content of those results, not only on their vocabulary.

## A worked case

Take (ovijen : duthsib) : drishen and work it out one step at a time.
    ovijen : duthsib = aztka   (the table for :)
    aztka : drishen = drishen   (the table for :)
That leaves drishen, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is duthsib : (drishen : ovijen) for contrast.
    drishen : ovijen = hurnvash   (the table for :)
    duthsib : hurnvash = duthsib   (the table for :)
That gives duthsib, against drishen above.

Test drishen :: aztka. The qennyr of drishen is hurnvash, and aztka lies outside it, so
the relation fails.

## A case that breaks

R13. It is not the case that: Every pair of vintzams tuwrens. The case that settles it:
x = hurnvash, y = duthsib, left = hurnvash, right = duthsib. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

R14. It is not the case that: x : x = x for every vintzam x. It fails at x = duthsib,
value = hurnvash. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by closure under the first operation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside D3 (reldjen collections), D5 (the falwren) and D6 (the vextarn).

## Proofs

R13. It is not the case that: Every pair of vintzams tuwrens.

  (1) [S2] Take the case x = hurnvash, y = duthsib, left = hurnvash, right = duthsib, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

R14. It is not the case that: x : x = x for every vintzam x.

  (1) [S2] Take the case x = duthsib, value = hurnvash, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T5. If x and y are both shenfal then so is x : y.

  (1) [D6] Let x and y be shenfal.
  (2) [D1] The claim asks whether (x : y) : (x : y) returns x : y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 36 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Established here and safe to use: T5.

Do not carry forward R13 and R14. These were tested and failed, and the failing cases
are recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x051. This result is about the vextarn. List every vintzam in it.
Level 5.
  x052. The following fails in this system: Every pair of vintzams tuwrens. Name the earliest vintzam, in the order the vintzams were introduced, that witnesses the failure.
  x053. The following fails in this system: x : x = x for every vintzam x. Name the earliest vintzam, in the order the vintzams were introduced, that witnesses the failure.
