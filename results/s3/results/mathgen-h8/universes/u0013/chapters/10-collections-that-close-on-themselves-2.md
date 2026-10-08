# Chapter 11. Collections that close on themselves (2)

## Why this chapter

The results collected here were not found in this order. The vashquil, where some xilzam
reaches every other breaks down and where the falisk divides the number of xilzams
breaks down came first, and the rest was assembled around that once the pattern was
visible.

Nothing here stands on its own. The arguments lean on chapters 5, 8 and 10, and a reader
who has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over xilzams, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D12. The vashquil. The vashquil of the system is the collection of xilzams whose falisk
is largest.

Running the definition over every xilzam leaves nyrfex.

## The shape of it

Picture the ponwren as what happens when you start with one xilzam and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 4 xilzams, that stops. In this system the sizes it stops at are 1, 2 and 3.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R10 rests on D8 (the ponwren of a xilzam) and D11 (the falisk of a xilzam). The
dependence is on the content of those results, not only on their vocabulary.

R8 rests on D11 (the falisk of a xilzam) and T4 (the ponwren of a xilzam is hurnkeld).
The dependence is on the content of those results, not only on their vocabulary.

T5 rests on D8 (the ponwren of a xilzam) and T4 (the ponwren of a xilzam is hurnkeld).
The dependence is on the content of those results, not only on their vocabulary.

T6 rests on D1 (thrami xilzams), D11 (the falisk of a xilzam) and T4 (the ponwren of a
xilzam is hurnkeld). Remove any one of them and the statement stops making sense, not
merely stops being provable.

## A worked case

Here is muxovi & nyrfex $ ovimux, reduced without skipping anything.
    nyrfex $ ovimux = ovimux   (the table for $)
    muxovi & ovimux = ovimux   (the table for &)
The expression comes to ovimux.

Bracketing is not cosmetic, so here is nyrfex & (ovimux & muxovi) for contrast.
    ovimux & muxovi = ovimux   (the table for &)
    nyrfex & ovimux = shennak   (the table for &)
That gives shennak, against ovimux above.

One decision about the relation, since deciding is as much a skill as computing. Does
muxovi <| shennak hold? Read off what muxovi stands over: muxovi, nyrfex, ovimux and
shennak. shennak is among them, so it holds.

## A case that breaks

R10. It is not the case that: There is a xilzam whose ponwren is the whole system. It
fails at largest_span = 3, size = 4. One case is enough, and this is the earliest one.

R8. It is not the case that: For every xilzam x, the falisk of x divides 4. It fails at
x = nyrfex, reach = 3, size = 4. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by closure under the first operation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside D1 (thrami xilzams), D11 (the falisk of a xilzam), D8 (the ponwren of a
xilzam) and T4 (the ponwren of a xilzam is hurnkeld).

## Proofs

R10. It is not the case that: There is a xilzam whose ponwren is the whole system.

  (1) [S2] Take the case largest_span = 3, size = 4, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 4 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

R8. It is not the case that: For every xilzam x, the falisk of x divides 4.

  (1) [S2] Take the case x = nyrfex, reach = 3, size = 4, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 4 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T5. If S is hurnkeld and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 28 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T6. x & x = x holds if and only if [x] contains x alone.

  (1) [D1] If x & x = x then {x} is already closed under &.
  (2) [T4] So [x] = {x} and the falisk is one.
  (3) [D11] Conversely a span of one object must contain x & x, which is then x.

Checked over 4 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the vashquil. Later chapters state their results in these terms and do not
restate the definitions.

The results now available are T5 and T6, each settled by exhaustive check rather than by
argument from analogy.

Explicitly not available: R10 and R8. A later argument that quietly assumes one of these
is wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x034. Which xilzams make up the vashquil? Name them all.
  x035. What is the largest falisk any xilzam has?
Level 5.
  x036. The following fails in this system: For every xilzam x, the falisk of x divides 4. Name the earliest xilzam, in the order the xilzams were introduced, that witnesses the failure.
