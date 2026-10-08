# Chapter 11. Collections that close on themselves (2)

## Why this chapter

The practical content of this chapter is the ponshen, where some reldjen reaches every
other breaks down and the nakgrix is contained in every zammorn collection. It is the
part that shows up in use.

Nothing here stands on its own. The arguments lean on chapters 5, 8 and 10, and a reader
who has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
reldjens that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D12. The ponshen. The ponshen of the system is the collection of reldjens whose solglim
is largest.

Running the definition over every reldjen leaves korrreld and iskbra.

## The shape of it

The right picture for nakgrix is a spreading stain rather than a list. Drop one reldjen
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
reldjens depending on where it started.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R10 rests on D8 (the nakgrix of a reldjen) and D11 (the solglim of a reldjen). The
dependence is on the content of those results, not only on their vocabulary.

T5 rests on D8 (the nakgrix of a reldjen) and T4 (the nakgrix of a reldjen is zammorn).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

T6 rests on D1 (duthnyr reldjens), D11 (the solglim of a reldjen) and T4 (the nakgrix of
a reldjen is zammorn). Remove any one of them and the statement stops making sense, not
merely stops being provable.

T7 rests on D11 (the solglim of a reldjen) and T4 (the nakgrix of a reldjen is zammorn).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

## A worked case

Here is kagel <> korrreld # iskbra, reduced without skipping anything.
    korrreld # iskbra = kagel   (the table for #)
    kagel <> kagel = kagel   (the table for <>)
So kagel <> korrreld # iskbra is kagel.

Move the brackets and the work changes. Take korrreld <> (iskbra <> kagel).
    iskbra <> kagel = iskbra   (the table for <>)
    korrreld <> iskbra = korrreld   (the table for <>)
The value is korrreld, not kagel.

One decision about the relation, since deciding is as much a skill as computing. Does
iskbra :: iskbra hold? Read off what iskbra stands over: iskbra. iskbra is among them,
so it holds.

## A case that breaks

R10. It is not the case that: There is a reldjen whose nakgrix is the whole system. It
fails at largest_span = 2, size = 4. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by closure under the first operation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside D1 (duthnyr reldjens), D11 (the solglim of a reldjen), D8 (the nakgrix of
a reldjen) and T4 (the nakgrix of a reldjen is zammorn).

## Proofs

R10. It is not the case that: There is a reldjen whose nakgrix is the whole system.

  (1) [S2] Take the case largest_span = 2, size = 4, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 4 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T5. If S is zammorn and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 32 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T6. x <> x = x holds if and only if [x] contains x alone.

  (1) [D1] If x <> x = x then {x} is already closed under <>.
  (2) [T4] So [x] = {x} and the solglim is one.
  (3) [D11] Conversely a span of one object must contain x <> x, which is then x.

Checked over 4 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T7. For every reldjen x, the solglim of x divides 4.

  (1) [T4] [x] is a zammorn collection.
  (2) [D11] Its size is the solglim of x.
  (3) The claim is that this size always divides 4.

Checked over 4 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the ponshen. Each of these is used by name later, so
the names are worth learning rather than looking up.

The results now available are T5, T6 and T7, each settled by exhaustive check rather
than by argument from analogy.

Explicitly not available: R10. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x030. Which reldjens make up the ponshen? Name them all.
  x031. What is the largest solglim any reldjen has?
