# Chapter 5. The relation and what it orders (2)

## Why this chapter

So far the aztfals have been objects to be pushed around. This chapter starts asking
what they are like. We take up grixespa pairs, vintpon collections and a tarntez.

Prerequisites are real here: chapters 1 and 3 supply the notions the statements below
are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
aztfals that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D13. Grixespa pairs. Two distinct aztfals x and y form a grixespa pair when x << y and y
<< x both hold, that is, when each lies in the tezmi of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D3. Vintpon collections. A collection S of aztfals is vintpon when x & y belongs to S
for every pair x, y drawn from S.

D9. A tarntez. A aztfal f is a tarntez when f << y holds for every aztfal y, that is,
when the tezmi of f is the whole system.

In this system that picks out aztclo, which is 1 of the 6 aztfals.

## The shape of it

The right picture for quilnak is a spreading stain rather than a list. Drop one aztfal
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 aztfals
depending on where it started.

The relation is easiest to see as a height. Each aztfal casts a tezmi over what it
yields to, and the sizes of those shadows here are 1, 2, 3, 4 and 6. Sizes repeat, so
the objects do not line up in single file.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R5 rests on D4 (the tezmi of a aztfal). The dependence is on the content of those
results, not only on their vocabulary.

T10 rests on D4 (the tezmi of a aztfal) and A9 (transitivity of the relation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

T12 rests on D4 (the tezmi of a aztfal) and A10 (agreement of the relation with the
first operation). Remove any one of them and the statement stops making sense, not
merely stops being provable.

## A worked case

Evaluate (nakqen & aztclo) & lornjen. Each line below is one lookup in a table.
    nakqen & aztclo = aztclo   (the table for &)
    aztclo & lornjen = aztclo   (the table for &)
So (nakqen & aztclo) & lornjen is aztclo.

Bracketing is not cosmetic, so here is aztclo & (lornjen & nakqen) for contrast.
    lornjen & nakqen = aztclo   (the table for &)
    aztclo & aztclo = aztclo   (the table for &)
That gives aztclo, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
lornjen << pyrnak hold? Read off what lornjen stands over: korrhob, pyrnak and lornjen.
pyrnak is among them, so it holds.

## A case that breaks

R5. It is not the case that: If x << y then y << x. It fails at x = pyrnak, y = korrhob.
One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of agreement of the relation with the first
operation, closure under the first operation and transitivity of the relation. Those are
properties of this system, not of systems in general.

To see how little the notation guarantees: rebuild the system with the same names over
different tables and T12 fail outright.

## Neighbouring results

The material this chapter borrows from: A1 (closure under the first operation), A10
(agreement of the relation with the first operation), A9 (transitivity of the relation)
and D4 (the tezmi of a aztfal).

What is built on it later: D8 (the quilnak of a aztfal), T3 (the nakpyr is vintpon), T4
(the quilnak of a aztfal is vintpon) and T9 (the iskopal is vintpon).

## Proofs

R5. It is not the case that: If x << y then y << x.

  (1) [S2] Take the case x = pyrnak, y = korrhob, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T10. If y lies in the tezmi of x, then the tezmi of y is contained in the tezmi of x.

  (1) [D4] Let y satisfy x << y and let z satisfy y << z.
  (2) [A9] Transitivity gives x << z.
  (3) [D4] So every member of the tezmi of y is a member of that of x.

Checked over 216 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T12. If x << y then (x & z) << (y & z) for every aztfal z.

  (1) [D4] Let y lie in the tezmi of x.
  (2) [A10] Compatibility applies the operation to both sides at once.
  (3) Nothing else is needed, since z was arbitrary.

Checked over 216 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward grixespa pairs, vintpon collections and a tarntez. Later chapters state
their results in these terms and do not restate the definitions.

The results now available are T10 and T12, each settled by exhaustive check rather than
by argument from analogy.

Explicitly not available: R5. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x011. How many aztfals lie in the smallest vintpon collection containing pyrnak?
  x012. How many aztfals lie in the smallest vintpon collection containing korrglim?
Level 4.
  x021. Write down the tarntez in full.
  x035. The result above concerns tezmis. List the tezmi of pyrnak.
  x036. The result above concerns tezmis. List the tezmi of korrglim.
Level 5.
  x038. The following fails in this system: If x << y then y << x. Name the earliest aztfal, in the order the aztfals were introduced, that witnesses the failure.
