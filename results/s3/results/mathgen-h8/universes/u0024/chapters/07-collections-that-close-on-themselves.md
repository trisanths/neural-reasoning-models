# Chapter 8. Collections that close on themselves

## Why this chapter

We turn to the vexnyr of a rastvash, the tarntarn of a rastvash is umbclo and the
lumovi. The treatment is self contained given the material already established.

Nothing here stands on its own. The arguments lean on chapters 4 and 6, and a reader who
has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about rastvashs covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D9. The vexnyr of a rastvash. The vexnyr of a rastvash x is the number of rastvashs in
its tarntarn [x].

Worked out for each rastvash: lumpyr to 1; lumnyr to 2; opalbra to 2; rastumb to 2;
fexrast to 2.

D10. The lumovi. The lumovi of the system is the collection of rastvashs whose vexnyr is
largest.

Running the definition over every rastvash leaves lumnyr, opalbra, rastumb and fexrast.

## The shape of it

The right picture for tarntarn is a spreading stain rather than a list. Drop one
rastvash in, apply the operation to whatever is wet, repeat. The stain here reaches 1
and 2 rastvashs depending on where it started.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T1 rests on D7 (the tarntarn of a rastvash) and D3 (umbclo collections). The dependence
is on the content of those results, not only on their vocabulary.

R12 rests on D7 (the tarntarn of a rastvash) and D9 (the vexnyr of a rastvash). Remove
any one of them and the statement stops making sense, not merely stops being provable.

R9 rests on D9 (the vexnyr of a rastvash) and T1 (the tarntarn of a rastvash is umbclo).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

T2 rests on D7 (the tarntarn of a rastvash) and T1 (the tarntarn of a rastvash is
umbclo). The dependence is on the content of those results, not only on their
vocabulary.

T3 rests on D1 (pyrglim rastvashs), D9 (the vexnyr of a rastvash) and T1 (the tarntarn
of a rastvash is umbclo). The dependence is on the content of those results, not only on
their vocabulary.

## A worked case

Here is (fexrast ? lumpyr) ? (opalbra ? lumnyr), reduced without skipping anything.
    fexrast ? lumpyr = fexrast   (the table for ?)
    opalbra ? lumnyr = lumnyr   (the table for ?)
    fexrast ? lumnyr = rastumb   (the table for ?)
That leaves rastumb, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is lumpyr ? (opalbra ? fexrast) for contrast.
    opalbra ? fexrast = lumpyr   (the table for ?)
    lumpyr ? lumpyr = lumpyr   (the table for ?)
The value is lumpyr, not rastumb.

One decision about the relation, since deciding is as much a skill as computing. Does
fexrast >> lumnyr hold? Read off what fexrast stands over: fexrast. lumnyr is not among
them, so it fails.

Now compute [opalbra]. Fold opalbra against itself, then fold whatever appeared against
everything present, and stop when a round adds nothing. The result is lumpyr and
opalbra, of size 2.

## A case that breaks

R12. It is not the case that: There is a rastvash whose tarntarn is the whole system.
The case that settles it: largest_span = 2, size = 5. Anyone carrying this claim over
from a more familiar system will be wrong here, and wrong in a way that propagates.

R9. It is not the case that: For every rastvash x, the vexnyr of x divides 5. It fails
at x = lumnyr, reach = 2, size = 5. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: D1 (pyrglim rastvashs), D3 (umbclo collections)
and D7 (the tarntarn of a rastvash).

## Proofs

T1. For every rastvash x, the collection [x] is umbclo.

  (1) [D7] [x] is built by taking x and closing under ?.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 125 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

R12. It is not the case that: There is a rastvash whose tarntarn is the whole system.

  (1) [S2] Take the case largest_span = 2, size = 5, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

R9. It is not the case that: For every rastvash x, the vexnyr of x divides 5.

  (1) [S2] Take the case x = lumnyr, reach = 2, size = 5, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T2. If S is umbclo and contains x, then S contains all of [x].

  (1) [D7] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 45 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. x ? x = x holds if and only if [x] contains x alone.

  (1) [D1] If x ? x = x then {x} is already closed under ?.
  (2) [T1] So [x] = {x} and the vexnyr is one.
  (3) [D9] Conversely a span of one object must contain x ? x, which is then x.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the vexnyr of a rastvash and the lumovi. Each of these
is used by name later, so the names are worth learning rather than looking up.

The results now available are T1, T2 and T3, each settled by exhaustive check rather
than by argument from analogy.

Do not carry forward R12 and R9. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x031. How many rastvashs lie in [lumnyr]?
  x032. What is the vexnyr of opalbra?
  x033. How many rastvashs lie in [rastumb]?
  x034. How many rastvashs lie in [fexrast]?
Level 4.
  x037. List every rastvash in the lumovi.
  x038. What is the largest vexnyr any rastvash has?
Level 5.
  x035. Let z be (fexrast ? lumpyr) ? lumnyr. What is the vexnyr of z?
  x036. Let z be (rastumb ? opalbra) ? opalbra. What is the vexnyr of z?
  x039. The following fails in this system: For every rastvash x, the vexnyr of x divides 5. Name the earliest rastvash, in the order the rastvashs were introduced, that witnesses the failure.
