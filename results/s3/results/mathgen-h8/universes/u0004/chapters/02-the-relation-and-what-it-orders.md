# Chapter 3. The relation and what it orders

## Why this chapter

The present chapter develops antisymmetry of the relation, transitivity of the relation
and the reldxil of a wrenclo.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
wrenclos that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A7. Antisymmetry of the relation. For all wrenclos x and y: if x <~ y and y <~ x then x
= y.

A8. Transitivity of the relation. For all wrenclos x, y, z: if x <~ y and y <~ z then x
<~ z.

D4. The reldxil of a wrenclo. The reldxil of a wrenclo x is the collection of wrenclos y
for which x <~ y holds.

Worked out for each wrenclo: glimfex to glimfex, bratu, vorkeld and falzam; bratu to
nothing; vorkeld to nothing; falzam to nothing.

## The shape of it

Think of <~ as pointing downhill. The reldxil of a wrenclo is everything downhill of it,
and those shadows here have sizes 0 and 4.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R3 rests on S2 (the Qenshen combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R4 rests on S2 (the Qenshen combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R5 rests on S2 (the Qenshen combination tables). The dependence is on the content of
those results, not only on their vocabulary.

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

Test vorkeld <~ bratu. The reldxil of vorkeld is empty, and bratu lies outside it, so
the relation fails.

## A case that breaks

R3. It is not the case that: For every wrenclo x: x <~ x. The case that settles it: x =
bratu. Anyone carrying this claim over from a more familiar system will be wrong here,
and wrong in a way that propagates.

R4. It is not the case that: For all wrenclos x and y, at least one of x <~ y and y <~ x
holds. It fails at x = bratu, y = bratu. One case is enough, and this is the earliest
one.

R5. It is not the case that: For all wrenclos x, y, z: if x <~ y then (z # x) <~ (z # y)
and (x # z) <~ (y # z). It fails at x = glimfex, y = glimfex, z = bratu, side = left.
One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside S2 (the Qenshen combination tables).

These results are used again in D9 (a falkeld), D14 (grixreld pairs), T13 (reldxils are
nested along the relation) and T14 (there is at most one falkeld).

## Proofs

R3. It is not the case that: For every wrenclo x: x <~ x.

  (1) [S2] Take the case x = bratu, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R4. It is not the case that: For all wrenclos x and y, at least one of x <~ y and y <~ x holds.

  (1) [S2] Take the case x = bratu, y = bratu, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R5. It is not the case that: For all wrenclos x, y, z: if x <~ y then (z # x) <~ (z # y) and (x # z) <~ (y # z).

  (1) [S2] Take the case x = glimfex, y = glimfex, z = bratu, side = left, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the reldxil of a wrenclo. Each of these is used by
name later, so the names are worth learning rather than looking up.

Do not carry forward R3, R4 and R5. These were tested and failed, and the failing cases
are recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x017. Which wrenclos y satisfy glimfex <~ y? Name them all.
Level 5.
  x012. The following fails in this system: For every wrenclo x: x <~ x. Name the earliest wrenclo, in the order the wrenclos were introduced, that witnesses the failure.
  x013. The following fails in this system: For all wrenclos x and y, at least one of x <~ y and y <~ x holds. Name the earliest wrenclo, in the order the wrenclos were introduced, that witnesses the failure.
  x014. The following fails in this system: For all wrenclos x, y, z: if x <~ y then (z # x) <~ (z # y) and (x # z) <~ (y # z). Name the earliest wrenclo, in the order the wrenclos were introduced, that witnesses the failure.
