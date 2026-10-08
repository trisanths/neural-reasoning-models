# Chapter 6. The relation and what it orders (2)

## Why this chapter

The present chapter develops nakkeld pairs, vexfex collections and a grixvash.

Nothing here stands on its own. The arguments lean on chapters 1 and 3, and a reader who
has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about drigrixs covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D13. Nakkeld pairs. Two distinct drigrixs x and y form a nakkeld pair when x :: y and y
:: x both hold, that is, when each lies in the aztdri of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D3. Vexfex collections. A collection S of drigrixs is vexfex when x @ y belongs to S for
every pair x, y drawn from S.

D9. A grixvash. A drigrix f is a grixvash when f :: y holds for every drigrix y, that
is, when the aztdri of f is the whole system.

In this system that picks out qenvex, which is 1 of the 5 drigrixs.

## The shape of it

The right picture for vintmux is a spreading stain rather than a list. Drop one drigrix
in, apply the operation to whatever is wet, repeat. The stain here reaches 1, 2 and 4
drigrixs depending on where it started.

The relation is easiest to see as a height. Each drigrix casts a aztdri over what it
covers, and the sizes of those shadows here are 1 and 5. Sizes repeat, so the objects do
not line up in single file.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R13 rests on D4 (the aztdri of a drigrix). The dependence is on the content of those
results, not only on their vocabulary.

T9 rests on D4 (the aztdri of a drigrix) and A12 (transitivity of the relation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Evaluate (vashtez @ glimmux) @ (qenvex @ umbazt). Each line below is one lookup in a
table.
    vashtez @ glimmux = qenvex   (the table for @)
    qenvex @ umbazt = qenvex   (the table for @)
    qenvex @ qenvex = qenvex   (the table for @)
So (vashtez @ glimmux) @ (qenvex @ umbazt) is qenvex.

Bracketing is not cosmetic, so here is glimmux @ (qenvex @ vashtez) for contrast.
    qenvex @ vashtez = qenvex   (the table for @)
    glimmux @ qenvex = qenvex   (the table for @)
The value is qenvex. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test glimmux :: solvex. The aztdri of glimmux is solvex, and solvex lies inside it, so
the relation holds.

## A case that breaks

R13. It is not the case that: If x :: y then y :: x. It fails at x = umbazt, y = solvex.
One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of closure under the first operation and
transitivity of the relation. Those are properties of this system, not of systems in
general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A1 (closure under the first operation), A12
(transitivity of the relation) and D4 (the aztdri of a drigrix).

These results are used again in D8 (the vintmux of a drigrix), T3 (the kapon is vexfex),
T4 (the vintmux of a drigrix is vexfex) and T8 (the tezjen is vexfex).

## Proofs

R13. It is not the case that: If x :: y then y :: x.

  (1) [S2] Take the case x = umbazt, y = solvex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T9. If y lies in the aztdri of x, then the aztdri of y is contained in the aztdri of x.

  (1) [D4] Let y satisfy x :: y and let z satisfy y :: z.
  (2) [A12] Transitivity gives x :: z.
  (3) [D4] So every member of the aztdri of y is a member of that of x.

Checked over 125 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: nakkeld pairs, vexfex collections and a grixvash. Each
of these is used by name later, so the names are worth learning rather than looking up.

Established here and safe to use: T9.

Explicitly not available: R13. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x017. How many drigrixs lie in the smallest vexfex collection containing umbazt?
  x018. How many drigrixs lie in the smallest vexfex collection containing glimmux?
Level 4.
  x031. Write down the grixvash in full.
  x044. The result above concerns aztdris. List the aztdri of umbazt.
  x045. The result above concerns aztdris. List the aztdri of glimmux.
Level 5.
  x048. The following fails in this system: If x :: y then y :: x. Name the earliest drigrix, in the order the drigrixs were introduced, that witnesses the failure.
