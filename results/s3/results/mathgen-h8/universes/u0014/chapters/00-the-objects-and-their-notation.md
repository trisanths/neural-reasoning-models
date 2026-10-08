# Chapter 1. The objects and their notation

## Why this chapter

Anyone using this system to keep track of something will meet the Quilumb signature, the
Quilumb combination tables and closure under the first operation early, whether or not
they go looking.

The standard of proof here is exhaustion. A universal claim about qenjens covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## The tables in full

The table for +. Read the left argument down the side and the right argument across the top.

         |  yuktarn   xilzam   shentu   nyrazt  cloreld
-------------------------------------------------------
 yuktarn |  yuktarn  yuktarn  yuktarn  yuktarn  yuktarn
  xilzam |  yuktarn   xilzam   shentu   nyrazt  cloreld
  shentu |  yuktarn   shentu  cloreld   xilzam   nyrazt
  nyrazt |  yuktarn   nyrazt   xilzam  cloreld   shentu
 cloreld |  yuktarn  cloreld   nyrazt   shentu   xilzam

The table for |=. Read the left argument down the side and the right argument across the top.

         |  yuktarn   xilzam   shentu   nyrazt  cloreld
-------------------------------------------------------
 yuktarn |  yuktarn  yuktarn  yuktarn  yuktarn  yuktarn
  xilzam |  yuktarn   xilzam   xilzam   xilzam   xilzam
  shentu |  yuktarn   xilzam   shentu   shentu   shentu
  nyrazt |  yuktarn   xilzam   shentu   nyrazt   nyrazt
 cloreld |  yuktarn   xilzam   shentu   nyrazt  cloreld

Every pair standing in the <~ relation, grouped by left argument.

  yuktarn <~ yuktarn, xilzam, shentu, nyrazt and cloreld
  xilzam <~ xilzam, shentu, nyrazt and cloreld
  shentu <~ shentu, nyrazt and cloreld
  nyrazt <~ nyrazt and cloreld
  cloreld <~ cloreld

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A1. Closure under the first operation. For all qenjens x and y, x + y is again a qenjen.

A2. Association of the first operation. For all qenjens x, y, z: (x + y) + z = x + (y +
z).

A3. Commutation of the first operation. For all qenjens x and y: x + y = y + x.

## The shape of it

Two questions sort the qenjens quickly. Does combining a qenjen with itself change it?
For yuktarn and xilzam it does not. Does it matter which side it goes on? For yuktarn,
xilzam, shentu, nyrazt and cloreld it does not.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R2 rests on S2 (the Quilumb combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R3 rests on S2 (the Quilumb combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take shentu + nyrazt |= xilzam and work it out one step at a time.
    nyrazt |= xilzam = xilzam   (the table for |=)
    shentu + xilzam = shentu   (the table for +)
That leaves shentu, and no other reading of the notation gives anything else.

A companion case, nyrazt + (xilzam + shentu), to show what the brackets are doing.
    xilzam + shentu = shentu   (the table for +)
    nyrazt + shentu = xilzam   (the table for +)
The value is xilzam, not shentu.

One decision about the relation, since deciding is as much a skill as computing. Does
shentu <~ cloreld hold? Read off what shentu stands over: shentu, nyrazt and cloreld.
cloreld is among them, so it holds.

## A case that breaks

R2. It is not the case that: For every qenjen x: x + x = x. It fails at x = shentu,
value = cloreld. One case is enough, and this is the earliest one.

R3. It is not the case that: For all qenjens x, y, z: if x + y = x + z then y = z. The
case that settles it: x = yuktarn, y = yuktarn, z = xilzam. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

What is built on it later: A4 (a neutral object for the first operation), A5 (an
absorbing object for the first operation), A6 (closure under the second operation) and
A7 (association of the second operation).

## Proofs

R2. It is not the case that: For every qenjen x: x + x = x.

  (1) [S2] Take the case x = shentu, value = cloreld, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R3. It is not the case that: For all qenjens x, y, z: if x + y = x + z then y = z.

  (1) [S2] Take the case x = yuktarn, y = yuktarn, z = xilzam, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R2 and R3. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 1.
  x001. Work out the value of nyrazt + nyrazt.
  x002. Evaluate nyrazt + cloreld.
  x003. What qenjen does shentu + cloreld name?
Level 2.
  x004. Evaluate cloreld^2.
  x005. What is nyrazt combined with itself 3 times under +?
  x006. Which qenjens x satisfy x + yuktarn = yuktarn? List them all.
Level 5.
  x008. The following fails in this system: For every qenjen x: x + x = x. Name the earliest qenjen, in the order the qenjens were introduced, that witnesses the failure.
  x009. The following fails in this system: For all qenjens x, y, z: if x + y = x + z then y = z. Name the earliest qenjen, in the order the qenjens were introduced, that witnesses the failure.
