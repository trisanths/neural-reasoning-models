# Chapter 10. Collections that close on themselves

## Why this chapter

What follows was pieced together backwards. The last item of it, the iskkorr of a
wrenclo, a wrenclo has only one thramorn and the tuclo of a wrenclo is mornvint, was
noticed before anyone had a reason to expect it.

Prerequisites are real here: chapters 1, 5, 7 and 8 supply the notions the statements
below are phrased in.

The standard of proof here is exhaustion. A universal claim about wrenclos covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

## What is defined here

D12. The iskkorr of a wrenclo. The iskkorr of a wrenclo x is the number of wrenclos in
its tuclo [x].

Worked out for each wrenclo: glimfex to 1; bratu to 2; vorkeld to 2; falzam to 2.

## The shape of it

Picture the tuclo as what happens when you start with one wrenclo and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 4 wrenclos, that stops. In this system the sizes it stops at are 1 and 2.

The neutral wrenclo glimfex is the one that does nothing. That sounds trivial and is
not: almost every result in this chapter is an argument about what doing nothing forces.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T3 rests on D11 (the thramorn of a wrenclo), A2 (association of the first operation) and
T1 (the ponjen is the only one of its kind). Remove any one of them and the statement
stops making sense, not merely stops being provable.

T6 rests on D8 (the tuclo of a wrenclo) and D3 (mornvint collections). Remove any one of
them and the statement stops making sense, not merely stops being provable.

## A worked case

Here is (vorkeld # glimfex) # (falzam # bratu), reduced without skipping anything.
    vorkeld # glimfex = vorkeld   (the table for #)
    falzam # bratu = vorkeld   (the table for #)
    vorkeld # vorkeld = glimfex   (the table for #)
The expression comes to glimfex.

Move the brackets and the work changes. Take glimfex # (falzam # vorkeld).
    falzam # vorkeld = bratu   (the table for #)
    glimfex # bratu = bratu   (the table for #)
The value is bratu, not glimfex.

Test vorkeld <~ glimfex. The reldxil of vorkeld is empty, and glimfex lies outside it,
so the relation fails.

A second case, this time a tuclo. Start from bratu. Combine it with itself, add whatever
is new, and repeat until nothing is added. What survives is glimfex and bratu, so the
iskkorr of bratu is 2.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of wrenclos that come back
unchanged from themselves: glimfex. Assuming more of them than that is the mistake to
avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation, closure under the first operation and reversal under
the first operation. Those are properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A2 (association of the first operation), D11
(the thramorn of a wrenclo), D3 (mornvint collections) and D8 (the tuclo of a wrenclo).

What is built on it later: D13 (the wrennak), T4 (a vintdri wrenclo is its own
thramorn), T7 (the tuclo is contained in every mornvint collection) and T8 (a wrenclo is
opalhurn exactly when its iskkorr is one).

## Proofs

T3. For every wrenclo x there is exactly one thramorn of x.

  (1) [D11] Let y and z both be partners of x.
  (2) [A2] Then y = y # (x # z) = (y # x) # z.
  (3) [D11] Both bracketed products collapse to the neutral object.
  (4) So y = z.

Checked over 16 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T6. For every wrenclo x, the collection [x] is mornvint.

  (1) [D8] [x] is built by taking x and closing under #.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 64 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the iskkorr of a wrenclo. Later chapters state their results in these
terms and do not restate the definitions.

The results now available are T3 and T6, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x029. How many wrenclos lie in [bratu]?
  x030. How many wrenclos lie in [falzam]?
Level 5.
  x031. Let z be (glimfex # falzam) # glimfex. What is the iskkorr of z?
  x032. Let z be (glimfex # bratu) # falzam. What is the iskkorr of z?
  x033. Let z be (bratu # falzam) # falzam. What is the iskkorr of z?
  x034. Let z be (glimfex # vorkeld) # falzam. What is the iskkorr of z?
