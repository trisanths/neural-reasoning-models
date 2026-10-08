# Chapter 1. The objects and their notation

## Why this chapter

We turn to the Vexumb signature, the Vexumb combination tables and closure under the
first operation. The treatment is self contained given the material already established.

One habit to adopt: when a statement below quantifies over grixbras, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## The tables in full

The table for @. Read the left argument down the side and the right argument across the top.

          |      mika    fexnyr   hobglim   umbtarn  mornthra
-------------------------------------------------------------
     mika |      mika      mika      mika      mika      mika
   fexnyr |    fexnyr      mika      mika      mika      mika
  hobglim |   hobglim    fexnyr      mika      mika      mika
  umbtarn |   umbtarn   hobglim    fexnyr      mika      mika
 mornthra |  mornthra   umbtarn   hobglim    fexnyr      mika

The table for !. Read the left argument down the side and the right argument across the top.

          |      mika    fexnyr   hobglim   umbtarn  mornthra
-------------------------------------------------------------
     mika |      mika    fexnyr   hobglim   umbtarn  mornthra
   fexnyr |    fexnyr    fexnyr   hobglim   umbtarn  mornthra
  hobglim |   hobglim   hobglim   hobglim   umbtarn  mornthra
  umbtarn |   umbtarn   umbtarn   umbtarn   umbtarn  mornthra
 mornthra |  mornthra  mornthra  mornthra  mornthra  mornthra

Every pair standing in the %% relation, grouped by left argument.

  mika %% mika
  fexnyr %% fexnyr
  hobglim %% hobglim
  umbtarn %% umbtarn
  mornthra %% mornthra

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A1. Closure under the first operation. For all grixbras x and y, x @ y is again a
grixbra.

## The shape of it

A useful mental split: some grixbras are inert under the operation and some are not.
mika come back unchanged when combined with themselves, and none commutes with
everything.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R1 rests on S2 (the Vexumb combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R2 rests on S2 (the Vexumb combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

R5 rests on S2 (the Vexumb combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R6 rests on S2 (the Vexumb combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

## A worked case

Take hobglim @ mornthra ! mika and work it out one step at a time.
    mornthra ! mika = mornthra   (the table for !)
    hobglim @ mornthra = mika   (the table for @)
That leaves mika, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is mornthra @ (mika @ hobglim) for contrast.
    mika @ hobglim = mika   (the table for @)
    mornthra @ mika = mornthra   (the table for @)
That gives mornthra, against mika above.

Test mika %% hobglim. The yukvash of mika is mika, and hobglim lies outside it, so the
relation fails.

## A case that breaks

R1. It is not the case that: For all grixbras x, y, z: (x @ y) @ z = x @ (y @ z). The
case that settles it: x = fexnyr, y = mika, z = fexnyr, left = mika, right = fexnyr.
Anyone carrying this claim over from a more familiar system will be wrong here, and
wrong in a way that propagates.

R2. It is not the case that: For all grixbras x and y: x @ y = y @ x. The case that
settles it: x = mika, y = fexnyr, left = mika, right = fexnyr. Anyone carrying this
claim over from a more familiar system will be wrong here, and wrong in a way that
propagates.

R5. It is not the case that: For every grixbra x: x @ x = x. The case that settles it: x
= fexnyr, value = mika. Anyone carrying this claim over from a more familiar system will
be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

What is built on it later: A2 (closure under the second operation), A3 (association of
the second operation), A4 (commutation of the second operation) and A5 (a neutral object
for the second operation).

## Proofs

R1. It is not the case that: For all grixbras x, y, z: (x @ y) @ z = x @ (y @ z).

  (1) [S2] Take the case x = fexnyr, y = mika, z = fexnyr, left = mika, right = fexnyr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R2. It is not the case that: For all grixbras x and y: x @ y = y @ x.

  (1) [S2] Take the case x = mika, y = fexnyr, left = mika, right = fexnyr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R5. It is not the case that: For every grixbra x: x @ x = x.

  (1) [S2] Take the case x = fexnyr, value = mika, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R6. It is not the case that: For all grixbras x, y, z: if x @ y = x @ z then y = z.

  (1) [S2] Take the case x = mika, y = mika, z = fexnyr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R1, R2, R5 and R6. These were tested and failed, and the failing
cases are recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 1.
  x001. Work out the value of fexnyr @ hobglim.
  x002. Work out the value of umbtarn @ fexnyr.
  x003. What grixbra does umbtarn @ mornthra name?
Level 2.
  x004. Work out the value of umbtarn @ mornthra ! umbtarn.
  x005. What grixbra does hobglim @ hobglim ! umbtarn name?
  x006. What grixbra does (fexnyr @ mornthra) @ umbtarn name?
  x007. Reduce (mornthra @ hobglim) @ mornthra to a single grixbra.
  x008. Reduce (fexnyr @ fexnyr) @ hobglim to a single grixbra.
  x009. Evaluate umbtarn^3.
  x010. Evaluate mornthra^3.
  x011. What is fexnyr combined with itself 3 times under @?
  x012. Which grixbras x satisfy x @ fexnyr = mika? List them all.
  x013. Which grixbras x satisfy x @ hobglim = fexnyr? List them all.
  x014. Which grixbras x satisfy x @ umbtarn = mika? List them all.
  x015. Solve x @ hobglim = hobglim for x, naming every solution.
Level 3.
  x016. Evaluate hobglim @ mornthra ! fexnyr, minding which operation binds tighter.
  x017. Evaluate mornthra @ umbtarn ! mika, minding which operation binds tighter.
  x018. Evaluate hobglim @ mornthra ! mornthra, minding which operation binds tighter.
Level 5.
  x019. The following fails in this system: For all grixbras x, y, z: (x @ y) @ z = x @ (y @ z). Name the earliest grixbra, in the order the grixbras were introduced, that witnesses the failure.
  x020. The following fails in this system: For all grixbras x and y: x @ y = y @ x. Name the earliest grixbra, in the order the grixbras were introduced, that witnesses the failure.
  x022. The following fails in this system: For every grixbra x: x @ x = x. Name the earliest grixbra, in the order the grixbras were introduced, that witnesses the failure.
  x023. The following fails in this system: For all grixbras x, y, z: if x @ y = x @ z then y = z. Name the earliest grixbra, in the order the grixbras were introduced, that witnesses the failure.
