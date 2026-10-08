# Chapter 7. Neutral objects and reversal (2)

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through vintdri wrenclos, the thramorn
of a wrenclo and where the ponjen swallows everything breaks down.

Nothing here stands on its own. The arguments lean on chapters 2 and 4, and a reader who
has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
wrenclos that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D10. Vintdri wrenclos. A wrenclo x is vintdri when x # x equals the ponjen.

In this system that picks out glimfex, bratu, vorkeld and falzam, that is, all of them.

D11. The thramorn of a wrenclo. A thramorn of a wrenclo x is a wrenclo y with x # y = y
# x = glimfex.

Worked out for each wrenclo: glimfex to glimfex; bratu to bratu; vorkeld to vorkeld;
falzam to falzam.

## The shape of it

Neutrality is a strong condition disguised as a weak one. It fixes a single wrenclo and,
through that, constrains everything that can combine with it.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R9 rests on D5 (the ponjen). The dependence is on the content of those results, not only
on their vocabulary.

T1 rests on D5 (the ponjen) and A4 (a neutral object for the first operation). The
dependence is on the content of those results, not only on their vocabulary.

## A worked case

Here is (glimfex # vorkeld) # bratu, reduced without skipping anything.
    glimfex # vorkeld = vorkeld   (the table for #)
    vorkeld # bratu = falzam   (the table for #)
That leaves falzam, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take vorkeld # (bratu # glimfex).
    bratu # glimfex = bratu   (the table for #)
    vorkeld # bratu = falzam   (the table for #)
That gives falzam, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test falzam <~ glimfex. The reldxil of falzam is empty, and glimfex lies outside it, so
the relation fails.

## A case that breaks

R9. It is not the case that: e # x equals the ponjen for every wrenclo x. The case that
settles it: anchor = glimfex, x = bratu, value = bratu. Anyone carrying this claim over
from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by a neutral object for the first operation, closure under the first
operation and reversal under the first operation. A system without them is not a system
where these results are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A4 (a neutral object for the first operation), A5 (reversal under the
first operation), D1 (opalhurn wrenclos) and D5 (the ponjen).

These results are used again in T3 (a wrenclo has only one thramorn) and T4 (a vintdri
wrenclo is its own thramorn).

## Proofs

R9. It is not the case that: e # x equals the ponjen for every wrenclo x.

  (1) [S2] Take the case anchor = glimfex, x = bratu, value = bratu, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 4 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T1. There is exactly one wrenclo e with e # x = x # e = x for every wrenclo x.

  (1) [D5] Suppose e and f both leave every wrenclo unchanged.
  (2) [A4] Then e # f = f, reading e as neutral on the left.
  (3) [A4] And e # f = e, reading f as neutral on the right.
  (4) So e = f, and the two suppositions describe the same object.

Checked over 16 cases: every object paired with every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward vintdri wrenclos and the thramorn of a wrenclo. Later chapters state their
results in these terms and do not restate the definitions.

Established here and safe to use: T1.

Explicitly not available: R9. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x027. Write down the vintdri in full.
Level 5.
  x028. Let z be bratu # bratu. Name the thramorn of z.
  x042. The following fails in this system: e # x equals the ponjen for every wrenclo x. Name the earliest wrenclo, in the order the wrenclos were introduced, that witnesses the failure.
