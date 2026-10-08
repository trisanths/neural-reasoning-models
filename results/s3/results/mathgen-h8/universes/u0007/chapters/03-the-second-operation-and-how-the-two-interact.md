# Chapter 4. The second operation and how the two interact

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through a neutral object for the
second operation, self combination under the second operation and closure under the
second operation.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over thrafexs, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A10. A neutral object for the second operation. There is a thrafex tuespa with tuespa ~
x = x for every x.

A11. Self combination under the second operation. For every thrafex x: x ~ x = x.

A7. Closure under the second operation. For all thrafexs x and y, x ~ y is again a
thrafex.

A8. Association of the second operation. For all thrafexs x, y, z: (x ~ y) ~ z = x ~ (y
~ z).

A9. Commutation of the second operation. For all thrafexs x and y: x ~ y = y ~ x.

## The shape of it

With two operations the question stops being what each does and becomes how they
interfere. ~ binds tighter, so the interference shows up whenever a bracket is left off.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R3 rests on S2 (the Keldmux combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R4 rests on S2 (the Keldmux combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Here is (tuespa =| hobzel) =| (tuespa =| hobzel), reduced without skipping anything.
    tuespa =| hobzel = hobzel   (the table for =|)
    tuespa =| hobzel = hobzel   (the table for =|)
    hobzel =| hobzel = qenmorn   (the table for =|)
So (tuespa =| hobzel) =| (tuespa =| hobzel) is qenmorn.

Move the brackets and the work changes. Take hobzel =| (tuespa =| tuespa).
    tuespa =| tuespa = tuespa   (the table for =|)
    hobzel =| tuespa = hobzel   (the table for =|)
The value is hobzel, not qenmorn.

Test hobzel =< hobzel. The vextarn of hobzel is tuespa, qenmorn and hobzel, and hobzel
lies inside it, so the relation holds.

## A case that breaks

R3. It is not the case that: For all thrafexs x, y, z: x ~ (y =| z) = (x ~ y) =| (x ~
z), and the same on the right. The case that settles it: x = qenmorn, y = tuespa, z =
tuespa, left = qenmorn, right = hobzel. Anyone carrying this claim over from a more
familiar system will be wrong here, and wrong in a way that propagates.

R4. It is not the case that: For all thrafexs x and y: x =| (x ~ y) = x and x ~ (x =| y)
= x. It fails at x = tuespa, y = qenmorn, value = qenmorn. One case is enough, and this
is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside S2 (the Keldmux combination tables).

What is built on it later: T19 (the second operation keeps the aztrast intact).

## Proofs

R3. It is not the case that: For all thrafexs x, y, z: x ~ (y =| z) = (x ~ y) =| (x ~ z), and the same on the right.

  (1) [S2] Take the case x = qenmorn, y = tuespa, z = tuespa, left = qenmorn, right = hobzel, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 27 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R4. It is not the case that: For all thrafexs x and y: x =| (x ~ y) = x and x ~ (x =| y) = x.

  (1) [S2] Take the case x = tuespa, y = qenmorn, value = qenmorn, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 27 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R3 and R4. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 5.
  x012. The following fails in this system: For all thrafexs x and y: x =| (x ~ y) = x and x ~ (x =| y) = x. Name the earliest thrafex, in the order the thrafexs were introduced, that witnesses the failure.
