# Chapter 6. The relation and what it orders (2)

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is mishen pairs, a
nakpyr and where the relation reads the same in both directions breaks down.

Nothing here stands on its own. The arguments lean on chapter 3, and a reader who has
skipped it will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about zelbras covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D11. Mishen pairs. Two distinct zelbras x and y form a mishen pair when x <~ y and y <~
x both hold, that is, when each lies in the opalpyr of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D8. A nakpyr. A zelbra f is a nakpyr when f <~ y holds for every zelbra y, that is, when
the opalpyr of f is the whole system.

Running the definition over every zelbra leaves tarnnyr.

## The shape of it

Think of <~ as pointing downhill. The opalpyr of a zelbra is everything downhill of it,
and those shadows here have sizes 1, 2, 3 and 4.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R14 rests on D4 (the opalpyr of a zelbra). The dependence is on the content of those
results, not only on their vocabulary.

T6 rests on D4 (the opalpyr of a zelbra) and A9 (transitivity of the relation). The
dependence is on the content of those results, not only on their vocabulary.

## A worked case

Here is (cloxil * iskmi) * (isktez * tarnnyr), reduced without skipping anything.
    cloxil * iskmi = tarnnyr   (the table for *)
    isktez * tarnnyr = isktez   (the table for *)
    tarnnyr * isktez = tarnnyr   (the table for *)
The expression comes to tarnnyr.

Move the brackets and the work changes. Take iskmi * (isktez * cloxil).
    isktez * cloxil = cloxil   (the table for *)
    iskmi * cloxil = isktez   (the table for *)
The value is isktez, not tarnnyr.

One decision about the relation, since deciding is as much a skill as computing. Does
isktez <~ iskmi hold? Read off what isktez stands over: isktez and iskmi. iskmi is among
them, so it holds.

## A case that breaks

R14. It is not the case that: If x <~ y then y <~ x. It fails at x = tarnnyr, y =
cloxil. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of transitivity of the relation. Those are
properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A9 (transitivity of the relation) and D4 (the opalpyr of a zelbra).

These results are used again in T7 (there is at most one nakpyr), T8 (the system has a
nakpyr) and T9 (no mishen pairs exist).

## Proofs

R14. It is not the case that: If x <~ y then y <~ x.

  (1) [S2] Take the case x = tarnnyr, y = cloxil, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 16 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T6. If y lies in the opalpyr of x, then the opalpyr of y is contained in the opalpyr of x.

  (1) [D4] Let y satisfy x <~ y and let z satisfy y <~ z.
  (2) [A9] Transitivity gives x <~ z.
  (3) [D4] So every member of the opalpyr of y is a member of that of x.

Checked over 64 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward mishen pairs and a nakpyr. Later chapters state their results in these
terms and do not restate the definitions.

Established here and safe to use: T6.

Explicitly not available: R14. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x027. Which zelbras make up the nakpyr? Name them all.
  x037. The result above concerns opalpyrs. List the opalpyr of tarnnyr.
  x038. The result above concerns opalpyrs. List the opalpyr of cloxil.
  x039. The result above concerns opalpyrs. List the opalpyr of isktez.
Level 5.
  x043. The following fails in this system: If x <~ y then y <~ x. Name the earliest zelbra, in the order the zelbras were introduced, that witnesses the failure.
