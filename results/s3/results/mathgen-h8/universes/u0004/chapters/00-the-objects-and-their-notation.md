# Chapter 1. The objects and their notation

## Why this chapter

Anyone using this system to keep track of something will meet the Qenshen signature, the
Qenshen combination tables and closure under the first operation early, whether or not
they go looking.

The standard of proof here is exhaustion. A universal claim about wrenclos covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## The tables in full

The table for #. Read the left argument down the side and the right argument across the top.

         |  glimfex    bratu  vorkeld   falzam
----------------------------------------------
 glimfex |  glimfex    bratu  vorkeld   falzam
   bratu |    bratu  glimfex   falzam  vorkeld
 vorkeld |  vorkeld   falzam  glimfex    bratu
  falzam |   falzam  vorkeld    bratu  glimfex

Every pair standing in the <~ relation, grouped by left argument.

  glimfex <~ glimfex, bratu, vorkeld and falzam
  bratu <~ nothing
  vorkeld <~ nothing
  falzam <~ nothing

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A1. Closure under the first operation. For all wrenclos x and y, x # y is again a
wrenclo.

A2. Association of the first operation. For all wrenclos x, y, z: (x # y) # z = x # (y #
z).

A3. Commutation of the first operation. For all wrenclos x and y: x # y = y # x.

A6. Cancellation in the first operation. For all wrenclos x, y, z: if x # y = x # z then
y = z.

## The shape of it

A useful mental split: some wrenclos are inert under the operation and some are not.
glimfex come back unchanged when combined with themselves, and glimfex, bratu, vorkeld
and falzam commute with everything.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R1 rests on S2 (the Qenshen combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take (glimfex # falzam) # vorkeld and work it out one step at a time.
    glimfex # falzam = falzam   (the table for #)
    falzam # vorkeld = bratu   (the table for #)
That leaves bratu, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take falzam # (vorkeld # glimfex).
    vorkeld # glimfex = vorkeld   (the table for #)
    falzam # vorkeld = bratu   (the table for #)
The value is bratu. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test bratu <~ falzam. The reldxil of bratu is empty, and falzam lies outside it, so the
relation fails.

## A case that breaks

R1. It is not the case that: For every wrenclo x: x # x = x. It fails at x = bratu,
value = glimfex. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

These results are used again in A4 (a neutral object for the first operation), A5
(reversal under the first operation), A7 (antisymmetry of the relation) and A8
(transitivity of the relation).

## Proofs

R1. It is not the case that: For every wrenclo x: x # x = x.

  (1) [S2] Take the case x = bratu, value = glimfex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R1. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 1.
  x001. What wrenclo does bratu # bratu name?
  x002. Reduce vorkeld # falzam to a single wrenclo.
  x003. Evaluate bratu # falzam.
Level 2.
  x004. What wrenclo does (vorkeld # falzam) # glimfex name?
  x005. Evaluate falzam^2.
  x006. Evaluate bratu # falzam'.
  x007. Evaluate vorkeld # falzam'.
  x008. Which wrenclos x satisfy x # falzam = falzam? List them all.
  x009. Solve x # bratu = bratu for x, naming every solution.
  x010. Solve x # bratu = falzam for x, naming every solution.
Level 5.
  x011. The following fails in this system: For every wrenclo x: x # x = x. Name the earliest wrenclo, in the order the wrenclos were introduced, that witnesses the failure.
