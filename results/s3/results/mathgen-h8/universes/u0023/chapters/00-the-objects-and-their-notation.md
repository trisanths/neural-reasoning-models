# Chapter 1. The objects and their notation

## Why this chapter

What follows was pieced together backwards. The last item of it, the Bravor signature,
the Bravor combination tables and closure under the first operation, was noticed before
anyone had a reason to expect it.

The standard of proof here is exhaustion. A universal claim about vintzams covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## The tables in full

The table for :. Read the left argument down the side and the right argument across the top.

          |  hurnvash   duthsib   drishen    pyryuk     aztka    ovijen
-----------------------------------------------------------------------
 hurnvash |  hurnvash  hurnvash  hurnvash  hurnvash  hurnvash  hurnvash
  duthsib |   duthsib  hurnvash  hurnvash  hurnvash  hurnvash  hurnvash
  drishen |   drishen   duthsib  hurnvash  hurnvash  hurnvash  hurnvash
   pyryuk |    pyryuk   drishen   duthsib  hurnvash  hurnvash  hurnvash
    aztka |     aztka    pyryuk   drishen   duthsib  hurnvash  hurnvash
   ovijen |    ovijen     aztka    pyryuk   drishen   duthsib  hurnvash

Every pair standing in the :: relation, grouped by left argument.

  hurnvash :: hurnvash, duthsib, drishen, pyryuk, aztka and ovijen
  duthsib :: hurnvash
  drishen :: hurnvash
  pyryuk :: hurnvash
  aztka :: hurnvash
  ovijen :: hurnvash

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A1. Closure under the first operation. For all vintzams x and y, x : y is again a
vintzam.

## The shape of it

Two questions sort the vintzams quickly. Does combining a vintzam with itself change it?
For hurnvash it does not. Does it matter which side it goes on? It always does.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R1 rests on S2 (the Bravor combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

R2 rests on S2 (the Bravor combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R5 rests on S2 (the Bravor combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R6 rests on S2 (the Bravor combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

## A worked case

Evaluate (hurnvash : pyryuk) : drishen. Each line below is one lookup in a table.
    hurnvash : pyryuk = hurnvash   (the table for :)
    hurnvash : drishen = hurnvash   (the table for :)
The expression comes to hurnvash.

Move the brackets and the work changes. Take pyryuk : (drishen : hurnvash).
    drishen : hurnvash = drishen   (the table for :)
    pyryuk : drishen = duthsib   (the table for :)
That gives duthsib, against hurnvash above.

Test aztka :: aztka. The qennyr of aztka is hurnvash, and aztka lies outside it, so the
relation fails.

## A case that breaks

R1. It is not the case that: For all vintzams x, y, z: (x : y) : z = x : (y : z). It
fails at x = duthsib, y = hurnvash, z = duthsib, left = hurnvash, right = duthsib. One
case is enough, and this is the earliest one.

R2. It is not the case that: For all vintzams x and y: x : y = y : x. The case that
settles it: x = hurnvash, y = duthsib, left = hurnvash, right = duthsib. Anyone carrying
this claim over from a more familiar system will be wrong here, and wrong in a way that
propagates.

R5. It is not the case that: For every vintzam x: x : x = x. The case that settles it: x
= duthsib, value = hurnvash. Anyone carrying this claim over from a more familiar system
will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

These results are used again in R3 (the system does not have a neutral object for the
first operation), R4 (the system does not have reversal under the first operation), R7
(the system does not have an absorbing object for the first operation) and R8 (the
system does not have reflexivity of the relation).

## Proofs

R1. It is not the case that: For all vintzams x, y, z: (x : y) : z = x : (y : z).

  (1) [S2] Take the case x = duthsib, y = hurnvash, z = duthsib, left = hurnvash, right = duthsib, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R2. It is not the case that: For all vintzams x and y: x : y = y : x.

  (1) [S2] Take the case x = hurnvash, y = duthsib, left = hurnvash, right = duthsib, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R5. It is not the case that: For every vintzam x: x : x = x.

  (1) [S2] Take the case x = duthsib, value = hurnvash, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R6. It is not the case that: For all vintzams x, y, z: if x : y = x : z then y = z.

  (1) [S2] Take the case x = hurnvash, y = hurnvash, z = duthsib, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R1, R2, R5 and R6. A later argument that quietly assumes one
of these is wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 1.
  x001. What vintzam does ovijen : drishen name?
  x002. Reduce drishen : pyryuk to a single vintzam.
  x003. Evaluate pyryuk : duthsib.
  x004. What vintzam does ovijen : ovijen name?
  x005. Work out the value of drishen : ovijen.
Level 2.
  x006. Reduce (duthsib : aztka) : drishen to a single vintzam.
  x007. Evaluate duthsib^3.
  x008. What is duthsib combined with itself 2 times under :?
  x009. Evaluate ovijen^2.
  x010. Which vintzams x satisfy x : drishen = duthsib? List them all.
  x011. Solve x : duthsib = duthsib for x, naming every solution.
  x012. Which vintzams x satisfy x : duthsib = drishen? List them all.
  x013. Solve x : drishen = hurnvash for x, naming every solution.
Level 5.
  x014. The following fails in this system: For all vintzams x, y, z: (x : y) : z = x : (y : z). Name the earliest vintzam, in the order the vintzams were introduced, that witnesses the failure.
  x015. The following fails in this system: For all vintzams x and y: x : y = y : x. Name the earliest vintzam, in the order the vintzams were introduced, that witnesses the failure.
  x017. The following fails in this system: For every vintzam x: x : x = x. Name the earliest vintzam, in the order the vintzams were introduced, that witnesses the failure.
  x018. The following fails in this system: For all vintzams x, y, z: if x : y = x : z then y = z. Name the earliest vintzam, in the order the vintzams were introduced, that witnesses the failure.
