# Chapter 4. The second operation and how the two interact

## Why this chapter

Anyone using this system to keep track of something will meet closure under the second
operation, association of the second operation and commutation of the second operation
early, whether or not they go looking.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about grixbras covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A2. Closure under the second operation. For all grixbras x and y, x ! y is again a
grixbra.

A3. Association of the second operation. For all grixbras x, y, z: (x ! y) ! z = x ! (y
! z).

A4. Commutation of the second operation. For all grixbras x and y: x ! y = y ! x.

A5. A neutral object for the second operation. There is a grixbra mika with mika ! x = x
for every x.

A6. Self combination under the second operation. For every grixbra x: x ! x = x.

## The shape of it

With two operations the question stops being what each does and becomes how they
interfere. ! binds tighter, so the interference shows up whenever a bracket is left off.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 grixbras the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R8 rests on S2 (the Vexumb combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R9 rests on S2 (the Vexumb combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

## A worked case

Take (fexnyr @ hobglim) @ (mornthra @ mika) and work it out one step at a time.
    fexnyr @ hobglim = mika   (the table for @)
    mornthra @ mika = mornthra   (the table for @)
    mika @ mornthra = mika   (the table for @)
The expression comes to mika.

Bracketing is not cosmetic, so here is hobglim @ (mornthra @ fexnyr) for contrast.
    mornthra @ fexnyr = umbtarn   (the table for @)
    hobglim @ umbtarn = mika   (the table for @)
That gives mika, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test umbtarn %% mornthra. The yukvash of umbtarn is umbtarn, and mornthra lies outside
it, so the relation fails.

## A case that breaks

R8. It is not the case that: For all grixbras x, y, z: x ! (y @ z) = (x ! y) @ (x ! z),
and the same on the right. It fails at x = fexnyr, y = mika, z = mika, left = fexnyr,
right = mika. One case is enough, and this is the earliest one.

R9. It is not the case that: For all grixbras x and y: x @ (x ! y) = x and x ! (x @ y) =
x. It fails at x = fexnyr, y = mika, value = mika. One case is enough, and this is the
earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside S2 (the Vexumb combination tables).

## Proofs

R8. It is not the case that: For all grixbras x, y, z: x ! (y @ z) = (x ! y) @ (x ! z), and the same on the right.

  (1) [S2] Take the case x = fexnyr, y = mika, z = mika, left = fexnyr, right = mika, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R9. It is not the case that: For all grixbras x and y: x @ (x ! y) = x and x ! (x @ y) = x.

  (1) [S2] Take the case x = fexnyr, y = mika, value = mika, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R8 and R9. These were tested and failed, and the failing cases are
recorded above.

## Exercises

This chapter carries no exercises. Nothing in it can be asked about in a way that could
not be answered without reading it, and an exercise like that is worse than none.
