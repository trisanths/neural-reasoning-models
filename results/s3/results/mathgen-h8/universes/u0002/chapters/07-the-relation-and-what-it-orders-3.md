# Chapter 8. The relation and what it orders (3)

## Why this chapter

The practical content of this chapter is there is at most one nakpyr, the system has a
nakpyr and no mishen pairs exist. It is the part that shows up in use.

Prerequisites are real here: chapters 3 and 6 supply the notions the statements below
are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
zelbras that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

The relation is easiest to see as a height. Each zelbra casts a opalpyr over what it
shadows, and the sizes of those shadows here are 1, 2, 3 and 4. No two are the same
size, so the objects line up in a single file.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T7 rests on D8 (a nakpyr) and A8 (antisymmetry of the relation). Remove any one of them
and the statement stops making sense, not merely stops being provable.

T8 rests on D8 (a nakpyr) and A10 (comparability of every pair). The dependence is on
the content of those results, not only on their vocabulary.

T9 rests on D11 (mishen pairs) and A8 (antisymmetry of the relation). Remove any one of
them and the statement stops making sense, not merely stops being provable.

## A worked case

Evaluate (cloxil * tarnnyr) * (iskmi * isktez). Each line below is one lookup in a
table.
    cloxil * tarnnyr = cloxil   (the table for *)
    iskmi * isktez = cloxil   (the table for *)
    cloxil * cloxil = tarnnyr   (the table for *)
So (cloxil * tarnnyr) * (iskmi * isktez) is tarnnyr.

Bracketing is not cosmetic, so here is tarnnyr * (iskmi * cloxil) for contrast.
    iskmi * cloxil = isktez   (the table for *)
    tarnnyr * isktez = tarnnyr   (the table for *)
That gives tarnnyr, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
iskmi <~ cloxil hold? Read off what iskmi stands over: iskmi. cloxil is not among them,
so it fails.

## A case that breaks

A quick guard against a common slip: isktez * iskmi is tarnnyr while iskmi * isktez is
cloxil. Order is not decoration in this system.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of antisymmetry of the relation and
comparability of every pair. Those are properties of this system, not of systems in
general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A10 (comparability of every pair), A8
(antisymmetry of the relation), D11 (mishen pairs) and D8 (a nakpyr).

## Proofs

T7. No two distinct zelbras can both be nakpyrs.

  (1) [D8] Let f and h both be floors.
  (2) [D8] Then f <~ h, since h is any object, and h <~ f likewise.
  (3) [A8] Antisymmetry forces f = h.

Checked over 16 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T8. Some zelbra nakpyrs the whole system.

  (1) [A10] Every pair is comparable, so the relation orders the objects into a line.
  (2) [D8] The claim is that the line has a bottom.
  (3) The carrier is finite, so the search over candidates terminates.

Checked over 16 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T9. No two distinct zelbras lie in each other's opalpyr.

  (1) [D11] Suppose x and y form a tight pair.
  (2) [A8] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 16 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Established here and safe to use: T7, T8 and T9.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x040. Name the zelbras that make up the nakpyr, which is what the result above is a claim about.
