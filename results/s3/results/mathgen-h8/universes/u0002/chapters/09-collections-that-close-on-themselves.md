# Chapter 10. Collections that close on themselves

## Why this chapter

We turn to the jenfal of a zelbra, the vintka of a zelbra is naknak and the cloopal. The
treatment is self contained given the material already established.

Prerequisites are real here: chapters 5 and 7 supply the notions the statements below
are phrased in.

The standard of proof here is exhaustion. A universal claim about zelbras covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D9. The jenfal of a zelbra. The jenfal of a zelbra x is the number of zelbras in its
vintka [x].

Worked out for each zelbra: tarnnyr to 1; cloxil to 2; isktez to 2; iskmi to 2.

D10. The cloopal. The cloopal of the system is the collection of zelbras whose jenfal is
largest.

In this system that picks out cloxil, isktez and iskmi, which is 3 of the 4 zelbras.

## The shape of it

The right picture for vintka is a spreading stain rather than a list. Drop one zelbra
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
zelbras depending on where it started.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T1 rests on D7 (the vintka of a zelbra) and D3 (naknak collections). The dependence is
on the content of those results, not only on their vocabulary.

R13 rests on D7 (the vintka of a zelbra) and D9 (the jenfal of a zelbra). Remove any one
of them and the statement stops making sense, not merely stops being provable.

T2 rests on D7 (the vintka of a zelbra) and T1 (the vintka of a zelbra is naknak). The
dependence is on the content of those results, not only on their vocabulary.

T3 rests on D1 (pyrtez zelbras), D9 (the jenfal of a zelbra) and T1 (the vintka of a
zelbra is naknak). Remove any one of them and the statement stops making sense, not
merely stops being provable.

T4 rests on D9 (the jenfal of a zelbra) and T1 (the vintka of a zelbra is naknak). The
dependence is on the content of those results, not only on their vocabulary.

## A worked case

Here is (cloxil * tarnnyr) * (iskmi * isktez), reduced without skipping anything.
    cloxil * tarnnyr = cloxil   (the table for *)
    iskmi * isktez = cloxil   (the table for *)
    cloxil * cloxil = tarnnyr   (the table for *)
The expression comes to tarnnyr.

A companion case, tarnnyr * (iskmi * cloxil), to show what the brackets are doing.
    iskmi * cloxil = isktez   (the table for *)
    tarnnyr * isktez = tarnnyr   (the table for *)
That gives tarnnyr, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test iskmi <~ cloxil. The opalpyr of iskmi is iskmi, and cloxil lies outside it, so the
relation fails.

Now compute [iskmi]. Fold iskmi against itself, then fold whatever appeared against
everything present, and stop when a round adds nothing. The result is tarnnyr and iskmi,
of size 2.

## A case that breaks

R13. It is not the case that: There is a zelbra whose vintka is the whole system. The
case that settles it: largest_span = 2, size = 4. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: D1 (pyrtez zelbras), D3 (naknak collections) and
D7 (the vintka of a zelbra).

## Proofs

T1. For every zelbra x, the collection [x] is naknak.

  (1) [D7] [x] is built by taking x and closing under *.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 64 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

R13. It is not the case that: There is a zelbra whose vintka is the whole system.

  (1) [S2] Take the case largest_span = 2, size = 4, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 4 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T2. If S is naknak and contains x, then S contains all of [x].

  (1) [D7] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 24 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. x * x = x holds if and only if [x] contains x alone.

  (1) [D1] If x * x = x then {x} is already closed under *.
  (2) [T1] So [x] = {x} and the jenfal is one.
  (3) [D9] Conversely a span of one object must contain x * x, which is then x.

Checked over 4 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T4. For every zelbra x, the jenfal of x divides 4.

  (1) [T1] [x] is a naknak collection.
  (2) [D9] Its size is the jenfal of x.
  (3) The claim is that this size always divides 4.

Checked over 4 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the jenfal of a zelbra and the cloopal. Each of these
is used by name later, so the names are worth learning rather than looking up.

Established here and safe to use: T1, T2, T3 and T4.

Do not carry forward R13. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x028. How many zelbras lie in [cloxil]?
  x029. What is the jenfal of iskmi?
Level 4.
  x034. Write down the cloopal in full.
  x035. What is the largest jenfal any zelbra has?
Level 5.
  x030. Let z be (iskmi * isktez) * iskmi. What is the jenfal of z?
  x031. Let z be iskmi * isktez - isktez. What is the jenfal of z?
  x032. Let z be cloxil * isktez - isktez. What is the jenfal of z?
  x033. Let z be (iskmi * isktez) * tarnnyr. What is the jenfal of z?
