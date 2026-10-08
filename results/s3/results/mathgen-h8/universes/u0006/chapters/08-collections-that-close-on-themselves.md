# Chapter 9. Collections that close on themselves

## Why this chapter

The practical content of this chapter is the iskka of a grixbra, the kavor of a grixbra
is umbgel and the tarnvash. It is the part that shows up in use.

Prerequisites are real here: chapters 5 and 7 supply the notions the statements below
are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
grixbras that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D9. The iskka of a grixbra. The iskka of a grixbra x is the number of grixbras in its
kavor [x].

Worked out for each grixbra: mika to 1; fexnyr to 2; hobglim to 2; umbtarn to 2;
mornthra to 2.

D10. The tarnvash. The tarnvash of the system is the collection of grixbras whose iskka
is largest.

Running the definition over every grixbra leaves fexnyr, hobglim, umbtarn and mornthra.

## The shape of it

The right picture for kavor is a spreading stain rather than a list. Drop one grixbra
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
grixbras depending on where it started.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T1 rests on D7 (the kavor of a grixbra) and D3 (umbgel collections). The dependence is
on the content of those results, not only on their vocabulary.

R11 rests on D9 (the iskka of a grixbra) and T1 (the kavor of a grixbra is umbgel). The
dependence is on the content of those results, not only on their vocabulary.

R14 rests on D7 (the kavor of a grixbra) and D9 (the iskka of a grixbra). Remove any one
of them and the statement stops making sense, not merely stops being provable.

T2 rests on D7 (the kavor of a grixbra) and T1 (the kavor of a grixbra is umbgel).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

T3 rests on D1 (reldjen grixbras), D9 (the iskka of a grixbra) and T1 (the kavor of a
grixbra is umbgel). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Here is fexnyr @ mornthra ! mika, reduced without skipping anything.
    mornthra ! mika = mornthra   (the table for !)
    fexnyr @ mornthra = mika   (the table for @)
The expression comes to mika.

A companion case, mornthra @ (mika @ fexnyr), to show what the brackets are doing.
    mika @ fexnyr = mika   (the table for @)
    mornthra @ mika = mornthra   (the table for @)
The value is mornthra, not mika.

Test hobglim %% hobglim. The yukvash of hobglim is hobglim, and hobglim lies inside it,
so the relation holds.

A second case, this time a kavor. Start from fexnyr. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is mika and fexnyr, so
the iskka of fexnyr is 2.

## A case that breaks

R11. It is not the case that: For every grixbra x, the iskka of x divides 5. It fails at
x = fexnyr, reach = 2, size = 5. One case is enough, and this is the earliest one.

R14. It is not the case that: There is a grixbra whose kavor is the whole system. It
fails at largest_span = 2, size = 5. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by closure under the first operation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: D1 (reldjen grixbras), D3 (umbgel collections)
and D7 (the kavor of a grixbra).

## Proofs

T1. For every grixbra x, the collection [x] is umbgel.

  (1) [D7] [x] is built by taking x and closing under @.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 125 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

R11. It is not the case that: For every grixbra x, the iskka of x divides 5.

  (1) [S2] Take the case x = fexnyr, reach = 2, size = 5, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

R14. It is not the case that: There is a grixbra whose kavor is the whole system.

  (1) [S2] Take the case largest_span = 2, size = 5, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T2. If S is umbgel and contains x, then S contains all of [x].

  (1) [D7] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 45 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. x @ x = x holds if and only if [x] contains x alone.

  (1) [D1] If x @ x = x then {x} is already closed under @.
  (2) [T1] So [x] = {x} and the iskka is one.
  (3) [D9] Conversely a span of one object must contain x @ x, which is then x.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the iskka of a grixbra and the tarnvash. Each of these
is used by name later, so the names are worth learning rather than looking up.

Established here and safe to use: T1, T2 and T3.

Do not carry forward R11 and R14. These were tested and failed, and the failing cases
are recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x035. What is the iskka of fexnyr?
  x036. What is the iskka of hobglim?
  x037. How many grixbras lie in [umbtarn]?
  x038. How many grixbras lie in [mornthra]?
Level 4.
  x043. Which grixbras make up the tarnvash? Name them all.
  x044. What is the largest iskka any grixbra has?
Level 5.
  x039. Let z be fexnyr @ mornthra ! mornthra. What is the iskka of z?
  x040. Let z be umbtarn @ mika ! hobglim. What is the iskka of z?
  x041. Let z be fexnyr @ hobglim ! fexnyr. What is the iskka of z?
  x042. Let z be (fexnyr @ mika) @ hobglim. What is the iskka of z?
  x045. The following fails in this system: For every grixbra x, the iskka of x divides 5. Name the earliest grixbra, in the order the grixbras were introduced, that witnesses the failure.
