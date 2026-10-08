# Chapter 8. Neutral objects and reversal (2)

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through mornpon naksols, the bralum of
a naksol and where the muxisk swallows everything breaks down.

Prerequisites are real here: chapters 2 and 5 supply the notions the statements below
are phrased in.

The standard of proof here is exhaustion. A universal claim about naksols covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D10. Mornpon naksols. A naksol x is mornpon when x % x equals the muxisk.

In this system that picks out wrenpyr and glimzam, which is 2 of the 6 naksols.

D11. The bralum of a naksol. A bralum of a naksol x is a naksol y with x % y = y % x =
wrenpyr.

Worked out for each naksol: wrenpyr to wrenpyr; vexlorn to pyrxil; vexnak to reldxil;
glimzam to glimzam; reldxil to vexnak; pyrxil to vexlorn.

## The shape of it

The neutral naksol wrenpyr is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R8 rests on D5 (the muxisk). The dependence is on the content of those results, not only
on their vocabulary.

T1 rests on D5 (the muxisk) and A4 (a neutral object for the first operation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Take (vexlorn % vexnak) % (glimzam % pyrxil) and work it out one step at a time.
    vexlorn % vexnak = glimzam   (the table for %)
    glimzam % pyrxil = vexnak   (the table for %)
    glimzam % vexnak = pyrxil   (the table for %)
So (vexlorn % vexnak) % (glimzam % pyrxil) is pyrxil.

A companion case, vexnak % (glimzam % vexlorn), to show what the brackets are doing.
    glimzam % vexlorn = reldxil   (the table for %)
    vexnak % reldxil = wrenpyr   (the table for %)
That gives wrenpyr, against pyrxil above.

One decision about the relation, since deciding is as much a skill as computing. Does
reldxil >- vexlorn hold? Read off what reldxil stands over: reldxil and pyrxil. vexlorn
is not among them, so it fails.

## A case that breaks

R8. It is not the case that: e % x equals the muxisk for every naksol x. The case that
settles it: anchor = wrenpyr, x = vexlorn, value = vexlorn. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by a neutral object for the first operation, closure under the first
operation and reversal under the first operation. A system without them is not a system
where these results are harder to prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A4 (a neutral object for the first operation), A5 (reversal under the
first operation), D1 (aztumb naksols) and D5 (the muxisk).

These results are used again in T3 (a naksol has only one bralum) and T4 (a mornpon
naksol is its own bralum).

## Proofs

R8. It is not the case that: e % x equals the muxisk for every naksol x.

  (1) [S2] Take the case anchor = wrenpyr, x = vexlorn, value = vexlorn, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T1. There is exactly one naksol e with e % x = x % e = x for every naksol x.

  (1) [D5] Suppose e and f both leave every naksol unchanged.
  (2) [A4] Then e % f = f, reading e as neutral on the left.
  (3) [A4] And e % f = e, reading f as neutral on the right.
  (4) So e = f, and the two suppositions describe the same object.

Checked over 36 cases: every object paired with every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: mornpon naksols and the bralum of a naksol. Each of
these is used by name later, so the names are worth learning rather than looking up.

The results now available are T1, each settled by exhaustive check rather than by
argument from analogy.

Explicitly not available: R8. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x036. Which naksols make up the mornpon? Name them all.
  x037. Name the bralum of vexlorn.
  x038. Which naksol reverses vexnak under %?
  x039. Which naksol reverses reldxil under %?
  x040. Which naksol reverses pyrxil under %?
Level 5.
  x041. Let z be reldxil % pyrxil. Name the bralum of z.
  x042. Let z be wrenpyr % reldxil. Name the bralum of z.
  x055. The following fails in this system: e % x equals the muxisk for every naksol x. Name the earliest naksol, in the order the naksols were introduced, that witnesses the failure.
