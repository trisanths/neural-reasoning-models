# Chapter 7. Combining objects (2)

## Why this chapter

The results collected here were not found in this order. The wrenvash of a duthpon,
where every duthpon is keldkeld breaks down and every duthpon lies in the iskvex came
first, and the rest was assembled around that once the pattern was visible.

Nothing here stands on its own. The arguments lean on chapters 1, 4, 5 and 6, and a
reader who has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
duthpons that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D8. The wrenvash of a duthpon. The wrenvash of a duthpon x, written [x], is the smallest
tarnquil collection that contains x.

Worked out for each duthpon: nakvint to nakvint; rastrast to rastrast; espanyr to
espanyr and vorwren; yuksol to yuksol; vorwren to vorwren; vashtarn to rastrast and
vashtarn.

## The shape of it

The right picture for wrenvash is a spreading stain rather than a list. Drop one duthpon
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
duthpons depending on where it started.

A useful mental split: some duthpons are inert under the operation and some are not.
nakvint, rastrast, yuksol and vorwren come back unchanged when combined with themselves,
and nakvint, rastrast, espanyr, yuksol, vorwren and vashtarn commute with everything.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R6 rests on D7 (the iskmux). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T12 rests on D6 (the iskvex). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T2 rests on D5 (the zelthra) and D6 (the iskvex). The dependence is on the content of
those results, not only on their vocabulary.

T3 rests on D6 (the iskvex), D3 (tarnquil collections) and A2 (association of the first
operation). The dependence is on the content of those results, not only on their
vocabulary.

T9 rests on D7 (the iskmux) and D3 (tarnquil collections). The dependence is on the
content of those results, not only on their vocabulary.

## A worked case

Take (yuksol - nakvint) - rastrast and work it out one step at a time.
    yuksol - nakvint = nakvint   (the table for -)
    nakvint - rastrast = nakvint   (the table for -)
The expression comes to nakvint.

Move the brackets and the work changes. Take nakvint - (rastrast - yuksol).
    rastrast - yuksol = yuksol   (the table for -)
    nakvint - yuksol = nakvint   (the table for -)
The value is nakvint. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test vorwren >> yuksol. The wrensib of vorwren is nakvint, espanyr and vorwren, and
yuksol lies outside it, so the relation fails.

Now compute [yuksol]. Fold yuksol against itself, then fold whatever appeared against
everything present, and stop when a round adds nothing. The result is yuksol, of size 1.

## A case that breaks

R6. It is not the case that: x - x = x for every duthpon x. The case that settles it: x
= espanyr, value = vorwren. Anyone carrying this claim over from a more familiar system
will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation and closure under the first operation. Those are
properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A2 (association of the first operation), D3 (tarnquil collections), D5
(the zelthra) and D6 (the iskvex).

What is built on it later: D11 (the geljen of a duthpon), T4 (the wrenvash of a duthpon
is tarnquil), T5 (the wrenvash is contained in every tarnquil collection) and T8 (the
wrenvash of a iskvex duthpon stays in the iskvex).

## Proofs

R6. It is not the case that: x - x = x for every duthpon x.

  (1) [S2] Take the case x = espanyr, value = vorwren, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T12. Every pair of duthpons shenshens.

  (1) [D6] The iskvex is defined by shenshening with everything.
  (2) [D2] The claim is that x - y = y - x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T2. The zelthra shenshens with every duthpon.

  (1) [D5] Let e be the zelthra and x any duthpon.
  (2) [D5] Then e - x = x and x - e = x.
  (3) [D2] So e - x = x - e, which is what it means to shenshen.
  (4) [D6] Since x was arbitrary, e belongs to the iskvex.

Checked over 6 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. If x and y both shenshen with every duthpon, then so does x - y.

  (1) [D6] Let x and y lie in the iskvex and let z be any duthpon.
  (2) [A2] Then (x - y) - z = x - (y - z).
  (3) [D6] Move z past y, then past x, using that each shenshens with everything.
  (4) [D3] So x - y shenshens with z, and the iskvex is tarnquil.

Checked over 36 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

T9. If x and y are both keldkeld then so is x - y.

  (1) [D7] Let x and y be keldkeld.
  (2) [D1] The claim asks whether (x - y) - (x - y) returns x - y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 36 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the wrenvash of a duthpon. Later chapters state their results in these
terms and do not restate the definitions.

The results now available are T12, T2, T3 and T9, each settled by exhaustive check
rather than by argument from analogy.

Do not carry forward R6. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x025. List the wrenvash of espanyr.
  x026. List the wrenvash of vashtarn.
Level 4.
  x027. Let z be vorwren - vashtarn. List the wrenvash of z.
  x028. Let z be yuksol - espanyr. List the wrenvash of z.
  x041. This result is about the iskvex. List every duthpon in it.
  x044. This result is about the iskmux. List every duthpon in it.
Level 5.
  x047. The following fails in this system: x - x = x for every duthpon x. Name the earliest duthpon, in the order the duthpons were introduced, that witnesses the failure.
