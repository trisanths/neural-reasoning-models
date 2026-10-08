# Chapter 3. The relation and what it orders

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through the qennyr of a vintzam, the
system does not have transitivity of the relation and the system does not have
comparability of every pair.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
vintzams that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D4. The qennyr of a vintzam. The qennyr of a vintzam x is the collection of vintzams y
for which x :: y holds.

Worked out for each vintzam: hurnvash to hurnvash, duthsib, drishen, pyryuk, aztka and
ovijen; duthsib to hurnvash; drishen to hurnvash; pyryuk to hurnvash; aztka to hurnvash;
ovijen to hurnvash.

## The shape of it

The relation is easiest to see as a height. Each vintzam casts a qennyr over what it
yields to, and the sizes of those shadows here are 1 and 6. Sizes repeat, so the objects
do not line up in single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 vintzams the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R10 rests on S2 (the Bravor combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R11 rests on S2 (the Bravor combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R12 rests on S2 (the Bravor combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R8 rests on S2 (the Bravor combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R9 rests on S2 (the Bravor combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Evaluate (ovijen : aztka) : pyryuk. Each line below is one lookup in a table.
    ovijen : aztka = duthsib   (the table for :)
    duthsib : pyryuk = hurnvash   (the table for :)
That leaves hurnvash, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is aztka : (pyryuk : ovijen) for contrast.
    pyryuk : ovijen = hurnvash   (the table for :)
    aztka : hurnvash = aztka   (the table for :)
The value is aztka, not hurnvash.

Test drishen :: ovijen. The qennyr of drishen is hurnvash, and ovijen lies outside it,
so the relation fails.

## A case that breaks

R10. It is not the case that: For all vintzams x, y, z: if x :: y and y :: z then x ::
z. It fails at x = duthsib, y = hurnvash, z = duthsib. One case is enough, and this is
the earliest one.

R11. It is not the case that: For all vintzams x and y, at least one of x :: y and y ::
x holds. It fails at x = duthsib, y = duthsib. One case is enough, and this is the
earliest one.

R12. It is not the case that: For all vintzams x, y, z: if x :: y then (z : x) :: (z :
y) and (x : z) :: (y : z). The case that settles it: x = hurnvash, y = hurnvash, z =
duthsib, side = left. Anyone carrying this claim over from a more familiar system will
be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside S2 (the Bravor combination tables).

These results are used again in D8 (a nyrmux), D11 (tezreld pairs) and T6 (the relation
reads the same in both directions).

## Proofs

R10. It is not the case that: For all vintzams x, y, z: if x :: y and y :: z then x :: z.

  (1) [S2] Take the case x = duthsib, y = hurnvash, z = duthsib, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R11. It is not the case that: For all vintzams x and y, at least one of x :: y and y :: x holds.

  (1) [S2] Take the case x = duthsib, y = duthsib, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R12. It is not the case that: For all vintzams x, y, z: if x :: y then (z : x) :: (z : y) and (x : z) :: (y : z).

  (1) [S2] Take the case x = hurnvash, y = hurnvash, z = duthsib, side = left, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R8. It is not the case that: For every vintzam x: x :: x.

  (1) [S2] Take the case x = duthsib, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R9. It is not the case that: For all vintzams x and y: if x :: y and y :: x then x = y.

  (1) [S2] Take the case x = hurnvash, y = duthsib, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the qennyr of a vintzam. Later chapters state their results in these terms
and do not restate the definitions.

Do not carry forward R10, R11, R12, R8 and R9. These were tested and failed, and the
failing cases are recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x026. List the qennyr of hurnvash.
  x027. Which vintzams y satisfy duthsib :: y? Name them all.
  x028. Which vintzams y satisfy drishen :: y? Name them all.
  x029. Which vintzams y satisfy pyryuk :: y? Name them all.
  x030. Which vintzams y satisfy aztka :: y? Name them all.
  x031. Which vintzams y satisfy ovijen :: y? Name them all.
Level 5.
  x019. The following fails in this system: For every vintzam x: x :: x. Name the earliest vintzam, in the order the vintzams were introduced, that witnesses the failure.
  x020. The following fails in this system: For all vintzams x and y: if x :: y and y :: x then x = y. Name the earliest vintzam, in the order the vintzams were introduced, that witnesses the failure.
  x021. The following fails in this system: For all vintzams x, y, z: if x :: y and y :: z then x :: z. Name the earliest vintzam, in the order the vintzams were introduced, that witnesses the failure.
  x022. The following fails in this system: For all vintzams x, y, z: if x :: y then (z : x) :: (z : y) and (x : z) :: (y : z). Name the earliest vintzam, in the order the vintzams were introduced, that witnesses the failure.
