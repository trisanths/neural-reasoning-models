# Chapter 8. The relation and what it orders (3)

## Why this chapter

The present chapter develops the tuclo of a wrenclo, there is at most one falkeld and no
grixreld pairs exist.

Prerequisites are real here: chapters 3 and 5 supply the notions the statements below
are phrased in.

The standard of proof here is exhaustion. A universal claim about wrenclos covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

## What is defined here

D8. The tuclo of a wrenclo. The tuclo of a wrenclo x, written [x], is the smallest
mornvint collection that contains x.

Worked out for each wrenclo: glimfex to glimfex; bratu to glimfex and bratu; vorkeld to
glimfex and vorkeld; falzam to glimfex and falzam.

## The shape of it

Picture the tuclo as what happens when you start with one wrenclo and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 4 wrenclos, that stops. In this system the sizes it stops at are 1 and 2.

The relation is easiest to see as a height. Each wrenclo casts a reldxil over what it
covers, and the sizes of those shadows here are 0 and 4. Sizes repeat, so the objects do
not line up in single file.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T14 rests on D9 (a falkeld) and A7 (antisymmetry of the relation). The dependence is on
the content of those results, not only on their vocabulary.

T15 rests on D14 (grixreld pairs) and A7 (antisymmetry of the relation). Remove any one
of them and the statement stops making sense, not merely stops being provable.

## A worked case

Evaluate (falzam # glimfex) # (vorkeld # bratu). Each line below is one lookup in a
table.
    falzam # glimfex = falzam   (the table for #)
    vorkeld # bratu = falzam   (the table for #)
    falzam # falzam = glimfex   (the table for #)
So (falzam # glimfex) # (vorkeld # bratu) is glimfex.

Move the brackets and the work changes. Take glimfex # (vorkeld # falzam).
    vorkeld # falzam = bratu   (the table for #)
    glimfex # bratu = bratu   (the table for #)
The value is bratu, not glimfex.

One decision about the relation, since deciding is as much a skill as computing. Does
vorkeld <~ falzam hold? Read off what vorkeld stands over: nothing at all. falzam is not
among them, so it fails.

A second case, this time a tuclo. Start from falzam. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is glimfex and falzam,
so the iskkorr of falzam is 2.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by antisymmetry of the relation and closure under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A7 (antisymmetry of the relation), D14 (grixreld pairs), D3 (mornvint
collections) and D9 (a falkeld).

These results are used again in D12 (the iskkorr of a wrenclo), T6 (the tuclo of a
wrenclo is mornvint), T7 (the tuclo is contained in every mornvint collection) and T10
(the tuclo of a tunak wrenclo stays in the tunak).

## Proofs

T14. No two distinct wrenclos can both be falkelds.

  (1) [D9] Let f and h both be floors.
  (2) [D9] Then f <~ h, since h is any object, and h <~ f likewise.
  (3) [A7] Antisymmetry forces f = h.

Checked over 16 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T15. No two distinct wrenclos lie in each other's reldxil.

  (1) [D14] Suppose x and y form a tight pair.
  (2) [A7] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 16 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the tuclo of a wrenclo. Each of these is used by name
later, so the names are worth learning rather than looking up.

The results now available are T14 and T15, each settled by exhaustive check rather than
by argument from analogy.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x020. Name every wrenclo in [bratu].
  x021. List the tuclo of vorkeld.
  x022. List the tuclo of falzam.
Level 4.
  x023. Let z be bratu # falzam. List the tuclo of z.
  x024. Let z be falzam # falzam. List the tuclo of z.
  x025. Let z be bratu # glimfex. List the tuclo of z.
  x039. Name the wrenclos that make up the falkeld, which is what the result above is a claim about.
