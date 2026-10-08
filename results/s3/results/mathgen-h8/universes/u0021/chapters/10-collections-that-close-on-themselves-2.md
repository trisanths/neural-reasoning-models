# Chapter 11. Collections that close on themselves (2)

## Why this chapter

We turn to the vashopal, the umbquil of a glimfex lumpon stays in the glimfex and some
lumpon reaches every other. The treatment is self contained given the material already
established.

Nothing here stands on its own. The arguments lean on chapters 4, 6, 7, 8, 9 and 10, and
a reader who has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about lumpons covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

## What is defined here

D13. The vashopal. The vashopal of the system is the collection of lumpons whose duthovi
is largest.

In this system that picks out glimkorr and mornhob, which is 2 of the 6 lumpons.

## The shape of it

The right picture for umbquil is a spreading stain rather than a list. Drop one lumpon
in, apply the operation to whatever is wet, repeat. The stain here reaches 1, 2, 3 and 6
lumpons depending on where it started.

Two questions sort the lumpons quickly. Does combining a lumpon with itself change it?
For glimtez it does not. Does it matter which side it goes on? For glimtez, glimkorr,
nakkorr, duthwren, kaka and mornhob it does not.

Neutrality is a strong condition disguised as a weak one. It fixes a single lumpon and,
through that, constrains everything that can combine with it.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T10 rests on D8 (the umbquil of a lumpon), D6 (the glimfex) and T5 (the glimfex is
lumvex). The dependence is on the content of those results, not only on their
vocabulary.

T18 rests on D8 (the umbquil of a lumpon) and D12 (the duthovi of a lumpon). Remove any
one of them and the statement stops making sense, not merely stops being provable.

T4 rests on D10 (iskjen lumpons), D11 (the zamduth of a lumpon) and T3 (a lumpon has
only one zamduth). Remove any one of them and the statement stops making sense, not
merely stops being provable.

T7 rests on D8 (the umbquil of a lumpon) and T6 (the umbquil of a lumpon is lumvex).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

T8 rests on D1 (pontez lumpons), D12 (the duthovi of a lumpon) and T6 (the umbquil of a
lumpon is lumvex). The dependence is on the content of those results, not only on their
vocabulary.

T9 rests on D12 (the duthovi of a lumpon) and T6 (the umbquil of a lumpon is lumvex).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

## A worked case

Take (duthwren - glimtez) - kaka and work it out one step at a time.
    duthwren - glimtez = duthwren   (the table for -)
    duthwren - kaka = glimkorr   (the table for -)
That leaves glimkorr, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take glimtez - (kaka - duthwren).
    kaka - duthwren = glimkorr   (the table for -)
    glimtez - glimkorr = glimkorr   (the table for -)
The value is glimkorr. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
kaka >- mornhob hold? Read off what kaka stands over: kaka and mornhob. mornhob is among
them, so it holds.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation, closure under the first operation and reversal under
the first operation. Those are properties of this system, not of systems in general.

That is not a rhetorical caution. Take the same 6 objects, the same symbols, and a
different table, and T18 and T9 stop holding. The notation survives the substitution and
the mathematics does not.

## Neighbouring results

Read alongside D1 (pontez lumpons), D10 (iskjen lumpons), D11 (the zamduth of a lumpon)
and D12 (the duthovi of a lumpon).

## Proofs

T10. If x lies in the glimfex then every lumpon of [x] lies in the glimfex.

  (1) [T5] The glimfex is lumvex.
  (2) [D8] [x] is the smallest lumvex collection containing x.
  (3) A smallest such collection sits inside any other, and the glimfex is one.

Checked over 36 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

T18. There is a lumpon whose umbquil is the whole system.

  (1) [D8] Compute [x] for each lumpon in turn.
  (2) [D12] The claim is that some duthovi equals 6.
  (3) The search runs over finitely many objects, so it settles.

Checked over 6 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T4. If x - x is the tuka then the zamduth of x is x itself.

  (1) [D10] Let x be iskjen, so x - x is the tuka.
  (2) [D11] That is exactly the condition for x to be a partner of x.
  (3) [T3] Partners are unique, so no other object can be one.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T7. If S is lumvex and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 24 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T8. x - x = x holds if and only if [x] contains x alone.

  (1) [D1] If x - x = x then {x} is already closed under -.
  (2) [T6] So [x] = {x} and the duthovi is one.
  (3) [D12] Conversely a span of one object must contain x - x, which is then x.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T9. For every lumpon x, the duthovi of x divides 6.

  (1) [T6] [x] is a lumvex collection.
  (2) [D12] Its size is the duthovi of x.
  (3) The claim is that this size always divides 6.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the vashopal. Each of these is used by name later, so
the names are worth learning rather than looking up.

Established here and safe to use: T10, T18, T4, T7, T8 and T9.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x053. Write down the vashopal in full.
  x055. What is the largest duthovi any lumpon has?
  x056. This result is about the glimfex. List every lumpon in it.
  x058. Which lumpon, taken earliest in the listed order, has duthovi equal to 6?
