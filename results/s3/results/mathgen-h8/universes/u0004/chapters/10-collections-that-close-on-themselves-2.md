# Chapter 11. Collections that close on themselves (2)

## Why this chapter

The practical content of this chapter is the wrennak, where some wrenclo reaches every
other breaks down and the tuclo of a tunak wrenclo stays in the tunak. It is the part
that shows up in use.

Prerequisites are real here: chapters 4, 6, 7, 8, 9 and 10 supply the notions the
statements below are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
wrenclos that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D13. The wrennak. The wrennak of the system is the collection of wrenclos whose iskkorr
is largest.

Running the definition over every wrenclo leaves bratu, vorkeld and falzam.

## The shape of it

The right picture for tuclo is a spreading stain rather than a list. Drop one wrenclo
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
wrenclos depending on where it started.

Two questions sort the wrenclos quickly. Does combining a wrenclo with itself change it?
For glimfex it does not. Does it matter which side it goes on? For glimfex, bratu,
vorkeld and falzam it does not.

The neutral wrenclo glimfex is the one that does nothing. That sounds trivial and is
not: almost every result in this chapter is an argument about what doing nothing forces.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R7 rests on D8 (the tuclo of a wrenclo) and D12 (the iskkorr of a wrenclo). The
dependence is on the content of those results, not only on their vocabulary.

T10 rests on D8 (the tuclo of a wrenclo), D6 (the tunak) and T5 (the tunak is mornvint).
The dependence is on the content of those results, not only on their vocabulary.

T4 rests on D10 (vintdri wrenclos), D11 (the thramorn of a wrenclo) and T3 (a wrenclo
has only one thramorn). Remove any one of them and the statement stops making sense, not
merely stops being provable.

T7 rests on D8 (the tuclo of a wrenclo) and T6 (the tuclo of a wrenclo is mornvint). The
dependence is on the content of those results, not only on their vocabulary.

T8 rests on D1 (opalhurn wrenclos), D12 (the iskkorr of a wrenclo) and T6 (the tuclo of
a wrenclo is mornvint). The dependence is on the content of those results, not only on
their vocabulary.

T9 rests on D12 (the iskkorr of a wrenclo) and T6 (the tuclo of a wrenclo is mornvint).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

## A worked case

Here is (falzam # bratu) # vorkeld, reduced without skipping anything.
    falzam # bratu = vorkeld   (the table for #)
    vorkeld # vorkeld = glimfex   (the table for #)
The expression comes to glimfex.

Bracketing is not cosmetic, so here is bratu # (vorkeld # falzam) for contrast.
    vorkeld # falzam = bratu   (the table for #)
    bratu # bratu = glimfex   (the table for #)
That gives glimfex, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
vorkeld <~ vorkeld hold? Read off what vorkeld stands over: nothing at all. vorkeld is
not among them, so it fails.

## A case that breaks

R7. It is not the case that: There is a wrenclo whose tuclo is the whole system. The
case that settles it: largest_span = 2, size = 4. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation, closure under the first operation and reversal under
the first operation. Those are properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: D1 (opalhurn wrenclos), D10 (vintdri wrenclos),
D11 (the thramorn of a wrenclo) and D12 (the iskkorr of a wrenclo).

## Proofs

R7. It is not the case that: There is a wrenclo whose tuclo is the whole system.

  (1) [S2] Take the case largest_span = 2, size = 4, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 4 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T10. If x lies in the tunak then every wrenclo of [x] lies in the tunak.

  (1) [T5] The tunak is mornvint.
  (2) [D8] [x] is the smallest mornvint collection containing x.
  (3) A smallest such collection sits inside any other, and the tunak is one.

Checked over 16 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

T4. If x # x is the ponjen then the thramorn of x is x itself.

  (1) [D10] Let x be vintdri, so x # x is the ponjen.
  (2) [D11] That is exactly the condition for x to be a partner of x.
  (3) [T3] Partners are unique, so no other object can be one.

Checked over 4 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T7. If S is mornvint and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 20 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T8. x # x = x holds if and only if [x] contains x alone.

  (1) [D1] If x # x = x then {x} is already closed under #.
  (2) [T6] So [x] = {x} and the iskkorr is one.
  (3) [D12] Conversely a span of one object must contain x # x, which is then x.

Checked over 4 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T9. For every wrenclo x, the iskkorr of x divides 4.

  (1) [T6] [x] is a mornvint collection.
  (2) [D12] Its size is the iskkorr of x.
  (3) The claim is that this size always divides 4.

Checked over 4 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the wrennak. Each of these is used by name later, so
the names are worth learning rather than looking up.

The results now available are T10, T4, T7, T8 and T9, each settled by exhaustive check
rather than by argument from analogy.

Explicitly not available: R7. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x035. Which wrenclos make up the wrennak? Name them all.
  x036. What is the largest iskkorr any wrenclo has?
