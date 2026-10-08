# Chapter 10. Collections that close on themselves

## Why this chapter

Anyone using this system to keep track of something will meet the vorzam of a vashumb,
the reldmi of a vashumb is hurnisk and the fexpon early, whether or not they go looking.

Prerequisites are real here: chapters 5 and 7 supply the notions the statements below
are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
vashumbs that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D9. The vorzam of a vashumb. The vorzam of a vashumb x is the number of vashumbs in its
reldmi [x].

Worked out for each vashumb: korrvex to 1; keldclo to 2; glimsib to 2; hobtez to 2;
korrdri to 2.

D10. The fexpon. The fexpon of the system is the collection of vashumbs whose vorzam is
largest.

In this system that picks out keldclo, glimsib, hobtez and korrdri, which is 4 of the 5
vashumbs.

## The shape of it

The right picture for reldmi is a spreading stain rather than a list. Drop one vashumb
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
vashumbs depending on where it started.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 vashumbs the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T1 rests on D7 (the reldmi of a vashumb) and D3 (hurnisk collections). The dependence is
on the content of those results, not only on their vocabulary.

R11 rests on D9 (the vorzam of a vashumb) and T1 (the reldmi of a vashumb is hurnisk).
The dependence is on the content of those results, not only on their vocabulary.

R14 rests on D7 (the reldmi of a vashumb) and D9 (the vorzam of a vashumb). The
dependence is on the content of those results, not only on their vocabulary.

T2 rests on D7 (the reldmi of a vashumb) and T1 (the reldmi of a vashumb is hurnisk).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

T3 rests on D1 (tarnmux vashumbs), D9 (the vorzam of a vashumb) and T1 (the reldmi of a
vashumb is hurnisk). The dependence is on the content of those results, not only on
their vocabulary.

## A worked case

Evaluate (korrvex ? glimsib) ? (keldclo ? korrdri). Each line below is one lookup in a
table.
    korrvex ? glimsib = korrvex   (the table for ?)
    keldclo ? korrdri = korrvex   (the table for ?)
    korrvex ? korrvex = korrvex   (the table for ?)
The expression comes to korrvex.

Move the brackets and the work changes. Take glimsib ? (keldclo ? korrvex).
    keldclo ? korrvex = keldclo   (the table for ?)
    glimsib ? keldclo = keldclo   (the table for ?)
The value is keldclo, not korrvex.

One decision about the relation, since deciding is as much a skill as computing. Does
keldclo %% hobtez hold? Read off what keldclo stands over: korrvex and keldclo. hobtez
is not among them, so it fails.

A second case, this time a reldmi. Start from hobtez. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is korrvex and hobtez,
so the vorzam of hobtez is 2.

## A case that breaks

R11. It is not the case that: For every vashumb x, the vorzam of x divides 5. The case
that settles it: x = keldclo, reach = 2, size = 5. Anyone carrying this claim over from
a more familiar system will be wrong here, and wrong in a way that propagates.

R14. It is not the case that: There is a vashumb whose reldmi is the whole system. It
fails at largest_span = 2, size = 5. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside D1 (tarnmux vashumbs), D3 (hurnisk collections) and D7 (the reldmi of a
vashumb).

## Proofs

T1. For every vashumb x, the collection [x] is hurnisk.

  (1) [D7] [x] is built by taking x and closing under ?.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 125 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

R11. It is not the case that: For every vashumb x, the vorzam of x divides 5.

  (1) [S2] Take the case x = keldclo, reach = 2, size = 5, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

R14. It is not the case that: There is a vashumb whose reldmi is the whole system.

  (1) [S2] Take the case largest_span = 2, size = 5, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T2. If S is hurnisk and contains x, then S contains all of [x].

  (1) [D7] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 45 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. x ? x = x holds if and only if [x] contains x alone.

  (1) [D1] If x ? x = x then {x} is already closed under ?.
  (2) [T1] So [x] = {x} and the vorzam is one.
  (3) [D9] Conversely a span of one object must contain x ? x, which is then x.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the vorzam of a vashumb and the fexpon. Later chapters state their results
in these terms and do not restate the definitions.

The results now available are T1, T2 and T3, each settled by exhaustive check rather
than by argument from analogy.

Do not carry forward R11 and R14. These were tested and failed, and the failing cases
are recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x037. How many vashumbs lie in [keldclo]?
  x038. How many vashumbs lie in [glimsib]?
  x039. What is the vorzam of hobtez?
  x040. What is the vorzam of korrdri?
Level 4.
  x046. Write down the fexpon in full.
  x047. What is the largest vorzam any vashumb has?
Level 5.
  x041. Let z be (korrdri ? korrdri) ? glimsib. What is the vorzam of z?
  x042. Let z be keldclo ? korrvex & korrvex. What is the vorzam of z?
  x043. Let z be glimsib ? korrdri & korrvex. What is the vorzam of z?
  x044. Let z be (glimsib ? glimsib) ? keldclo. What is the vorzam of z?
  x045. Let z be hobtez ? hobtez & korrvex. What is the vorzam of z?
  x048. The following fails in this system: For every vashumb x, the vorzam of x divides 5. Name the earliest vashumb, in the order the vashumbs were introduced, that witnesses the failure.
