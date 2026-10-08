# Chapter 5. The relation and what it orders (2)

## Why this chapter

What follows was pieced together backwards. The last item of it, grixreld pairs,
mornvint collections and a falkeld, was noticed before anyone had a reason to expect it.

Nothing here stands on its own. The arguments lean on chapters 1 and 3, and a reader who
has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
wrenclos that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D14. Grixreld pairs. Two distinct wrenclos x and y form a grixreld pair when x <~ y and
y <~ x both hold, that is, when each lies in the reldxil of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D3. Mornvint collections. A collection S of wrenclos is mornvint when x # y belongs to S
for every pair x, y drawn from S.

D9. A falkeld. A wrenclo f is a falkeld when f <~ y holds for every wrenclo y, that is,
when the reldxil of f is the whole system.

Running the definition over every wrenclo leaves glimfex.

## The shape of it

The right picture for tuclo is a spreading stain rather than a list. Drop one wrenclo
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
wrenclos depending on where it started.

The relation is easiest to see as a height. Each wrenclo casts a reldxil over what it
covers, and the sizes of those shadows here are 0 and 4. Sizes repeat, so the objects do
not line up in single file.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R8 rests on D4 (the reldxil of a wrenclo). Remove any one of them and the statement
stops making sense, not merely stops being provable.

T13 rests on D4 (the reldxil of a wrenclo) and A8 (transitivity of the relation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Take (vorkeld # falzam) # glimfex and work it out one step at a time.
    vorkeld # falzam = bratu   (the table for #)
    bratu # glimfex = bratu   (the table for #)
That leaves bratu, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is falzam # (glimfex # vorkeld) for contrast.
    glimfex # vorkeld = vorkeld   (the table for #)
    falzam # vorkeld = bratu   (the table for #)
The value is bratu. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test glimfex <~ bratu. The reldxil of glimfex is glimfex, bratu, vorkeld and falzam, and
bratu lies inside it, so the relation holds.

## A case that breaks

R8. It is not the case that: If x <~ y then y <~ x. It fails at x = glimfex, y = bratu.
One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by closure under the first operation and transitivity of the
relation. A system without them is not a system where these results are harder to prove;
it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A1 (closure under the first operation), A8
(transitivity of the relation) and D4 (the reldxil of a wrenclo).

What is built on it later: D8 (the tuclo of a wrenclo), T5 (the tunak is mornvint), T6
(the tuclo of a wrenclo is mornvint) and T11 (the shenhob is mornvint).

## Proofs

R8. It is not the case that: If x <~ y then y <~ x.

  (1) [S2] Take the case x = glimfex, y = bratu, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 16 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T13. If y lies in the reldxil of x, then the reldxil of y is contained in the reldxil of x.

  (1) [D4] Let y satisfy x <~ y and let z satisfy y <~ z.
  (2) [A8] Transitivity gives x <~ z.
  (3) [D4] So every member of the reldxil of y is a member of that of x.

Checked over 64 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward grixreld pairs, mornvint collections and a falkeld. Later chapters state
their results in these terms and do not restate the definitions.

The results now available are T13, each settled by exhaustive check rather than by
argument from analogy.

Explicitly not available: R8. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x016. How many wrenclos lie in the smallest mornvint collection containing bratu?
Level 4.
  x026. List every wrenclo in the falkeld.
  x038. The result above concerns reldxils. List the reldxil of glimfex.
Level 5.
  x041. The following fails in this system: If x <~ y then y <~ x. Name the earliest wrenclo, in the order the wrenclos were introduced, that witnesses the failure.
