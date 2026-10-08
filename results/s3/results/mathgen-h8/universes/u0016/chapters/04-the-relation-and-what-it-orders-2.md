# Chapter 5. The relation and what it orders (2)

## Why this chapter

So far the mornglims have been objects to be pushed around. This chapter starts asking
what they are like. We take up dripon pairs, tezdri collections and a duthvor.

Nothing here stands on its own. The arguments lean on chapters 1 and 3, and a reader who
has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
mornglims that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D13. Dripon pairs. Two distinct mornglims x and y form a dripon pair when x <~ y and y
<~ x both hold, that is, when each lies in the nakhurn of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D3. Tezdri collections. A collection S of mornglims is tezdri when x | y belongs to S
for every pair x, y drawn from S.

D9. A duthvor. A mornglim f is a duthvor when f <~ y holds for every mornglim y, that
is, when the nakhurn of f is the whole system.

Running the definition over every mornglim leaves oviazt.

## The shape of it

Picture the clobra as what happens when you start with one mornglim and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 4 mornglims, that stops. In this system the sizes it stops at are 1.

The relation is easiest to see as a height. Each mornglim casts a nakhurn over what it
dominates, and the sizes of those shadows here are 1, 2 and 4. Sizes repeat, so the
objects do not line up in single file.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R5 rests on D4 (the nakhurn of a mornglim). The dependence is on the content of those
results, not only on their vocabulary.

T10 rests on D4 (the nakhurn of a mornglim) and A9 (transitivity of the relation). The
dependence is on the content of those results, not only on their vocabulary.

T12 rests on D4 (the nakhurn of a mornglim) and A10 (agreement of the relation with the
first operation). Remove any one of them and the statement stops making sense, not
merely stops being provable.

## A worked case

Here is (kapon | oviazt) | nyrrast, reduced without skipping anything.
    kapon | oviazt = kapon   (the table for |)
    kapon | nyrrast = xilwren   (the table for |)
So (kapon | oviazt) | nyrrast is xilwren.

Bracketing is not cosmetic, so here is oviazt | (nyrrast | kapon) for contrast.
    nyrrast | kapon = xilwren   (the table for |)
    oviazt | xilwren = xilwren   (the table for |)
The value is xilwren. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
xilwren <~ kapon hold? Read off what xilwren stands over: xilwren. kapon is not among
them, so it fails.

## A case that breaks

R5. It is not the case that: If x <~ y then y <~ x. It fails at x = oviazt, y = kapon.
One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of agreement of the relation with the first
operation, closure under the first operation and transitivity of the relation. Those are
properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A1 (closure under the first operation), A10
(agreement of the relation with the first operation), A9 (transitivity of the relation)
and D4 (the nakhurn of a mornglim).

What is built on it later: D8 (the clobra of a mornglim), T3 (the falespa is tezdri), T4
(the clobra of a mornglim is tezdri) and T9 (the xilka is tezdri).

## Proofs

R5. It is not the case that: If x <~ y then y <~ x.

  (1) [S2] Take the case x = oviazt, y = kapon, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 16 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T10. If y lies in the nakhurn of x, then the nakhurn of y is contained in the nakhurn of x.

  (1) [D4] Let y satisfy x <~ y and let z satisfy y <~ z.
  (2) [A9] Transitivity gives x <~ z.
  (3) [D4] So every member of the nakhurn of y is a member of that of x.

Checked over 64 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T12. If x <~ y then (x | z) <~ (y | z) for every mornglim z.

  (1) [D4] Let y lie in the nakhurn of x.
  (2) [A10] Compatibility applies the operation to both sides at once.
  (3) Nothing else is needed, since z was arbitrary.

Checked over 64 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward dripon pairs, tezdri collections and a duthvor. Later chapters state their
results in these terms and do not restate the definitions.

Established here and safe to use: T10 and T12.

Explicitly not available: R5. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x011. How many mornglims lie in the smallest tezdri collection containing kapon?
  x012. How many mornglims lie in the smallest tezdri collection containing nyrrast?
Level 4.
  x018. List every mornglim in the duthvor.
  x029. The result above concerns nakhurns. List the nakhurn of oviazt.
  x030. The result above concerns nakhurns. List the nakhurn of kapon.
  x031. The result above concerns nakhurns. List the nakhurn of nyrrast.
Level 5.
  x033. The following fails in this system: If x <~ y then y <~ x. Name the earliest mornglim, in the order the mornglims were introduced, that witnesses the failure.
