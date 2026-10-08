# Chapter 1. The objects and their notation

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is the Keldmux
signature, the Keldmux combination tables and closure under the first operation.

The standard of proof here is exhaustion. A universal claim about thrafexs covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## The tables in full

The table for =|. Read the left argument down the side and the right argument across the top.

         |   tuespa  qenmorn   hobzel
-------------------------------------
  tuespa |   tuespa  qenmorn   hobzel
 qenmorn |  qenmorn   hobzel   tuespa
  hobzel |   hobzel   tuespa  qenmorn

The table for ~. Read the left argument down the side and the right argument across the top.

         |   tuespa  qenmorn   hobzel
-------------------------------------
  tuespa |   tuespa  qenmorn   hobzel
 qenmorn |  qenmorn  qenmorn   hobzel
  hobzel |   hobzel   hobzel   hobzel

Every pair standing in the =< relation, grouped by left argument.

  tuespa =< tuespa, qenmorn and hobzel
  qenmorn =< tuespa, qenmorn and hobzel
  hobzel =< tuespa, qenmorn and hobzel

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A1. Closure under the first operation. For all thrafexs x and y, x =| y is again a
thrafex.

A2. Association of the first operation. For all thrafexs x, y, z: (x =| y) =| z = x =|
(y =| z).

A3. Commutation of the first operation. For all thrafexs x and y: x =| y = y =| x.

A6. Cancellation in the first operation. For all thrafexs x, y, z: if x =| y = x =| z
then y = z.

## The shape of it

Two questions sort the thrafexs quickly. Does combining a thrafex with itself change it?
For tuespa it does not. Does it matter which side it goes on? For tuespa, qenmorn and
hobzel it does not.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R1 rests on S2 (the Keldmux combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Here is hobzel =| tuespa ~ tuespa, reduced without skipping anything.
    tuespa ~ tuespa = tuespa   (the table for ~)
    hobzel =| tuespa = hobzel   (the table for =|)
So hobzel =| tuespa ~ tuespa is hobzel.

Move the brackets and the work changes. Take tuespa =| (tuespa =| hobzel).
    tuespa =| hobzel = hobzel   (the table for =|)
    tuespa =| hobzel = hobzel   (the table for =|)
That gives hobzel, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test hobzel =< tuespa. The vextarn of hobzel is tuespa, qenmorn and hobzel, and tuespa
lies inside it, so the relation holds.

## A case that breaks

R1. It is not the case that: For every thrafex x: x =| x = x. It fails at x = qenmorn,
value = hobzel. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

What is built on it later: A4 (a neutral object for the first operation), A5 (reversal
under the first operation), A7 (closure under the second operation) and A8 (association
of the second operation).

## Proofs

R1. It is not the case that: For every thrafex x: x =| x = x.

  (1) [S2] Take the case x = qenmorn, value = hobzel, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 27 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R1. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 1.
  x001. What thrafex does hobzel =| qenmorn name?
  x002. What thrafex does qenmorn =| qenmorn name?
Level 2.
  x003. Reduce hobzel =| qenmorn ~ qenmorn to a single thrafex.
  x004. Reduce qenmorn =| tuespa ~ qenmorn to a single thrafex.
  x005. Reduce (tuespa =| qenmorn) =| qenmorn to a single thrafex.
  x006. What is qenmorn combined with itself 2 times under =|?
  x007. Evaluate hobzel^3.
  x008. Evaluate hobzel^2.
  x009. Evaluate tuespa =| hobzel'.
  x010. Solve x =| hobzel = tuespa for x, naming every solution.
  x011. Solve x =| qenmorn = qenmorn for x, naming every solution.
