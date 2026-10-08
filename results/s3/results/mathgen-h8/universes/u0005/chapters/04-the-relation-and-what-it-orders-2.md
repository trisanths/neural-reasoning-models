# Chapter 5. The relation and what it orders (2)

## Why this chapter

Anyone using this system to keep track of something will meet iskclo pairs, a wrenwren
and where the relation reads the same in both directions breaks down early, whether or
not they go looking.

Prerequisites are real here: chapter 3 supply the notions the statements below are
phrased in.

One habit to adopt: when a statement below quantifies over jenxils, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D11. Iskclo pairs. Two distinct jenxils x and y form a iskclo pair when x =< y and y =<
x both hold, that is, when each lies in the rastqen of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D8. A wrenwren. A jenxil f is a wrenwren when f =< y holds for every jenxil y, that is,
when the rastqen of f is the whole system.

In this system that picks out reldvint, which is 1 of the 3 jenxils.

## The shape of it

Think of =< as pointing downhill. The rastqen of a jenxil is everything downhill of it,
and those shadows here have sizes 1, 2 and 3.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R13 rests on D4 (the rastqen of a jenxil). The dependence is on the content of those
results, not only on their vocabulary.

T5 rests on D4 (the rastqen of a jenxil) and A4 (transitivity of the relation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Take (reldvint % wrenmux) % wrenmux and work it out one step at a time.
    reldvint % wrenmux = reldvint   (the table for %)
    reldvint % wrenmux = reldvint   (the table for %)
The expression comes to reldvint.

A companion case, wrenmux % (wrenmux % reldvint), to show what the brackets are doing.
    wrenmux % reldvint = wrenmux   (the table for %)
    wrenmux % wrenmux = reldvint   (the table for %)
The value is reldvint. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test reldvint =< zellum. The rastqen of reldvint is reldvint, wrenmux and zellum, and
zellum lies inside it, so the relation holds.

## A case that breaks

R13. It is not the case that: If x =< y then y =< x. The case that settles it: x =
reldvint, y = wrenmux. Anyone carrying this claim over from a more familiar system will
be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by transitivity of the relation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A4 (transitivity of the relation) and D4 (the rastqen of a jenxil).

These results are used again in T6 (there is at most one wrenwren), T7 (the system has a
wrenwren) and T8 (no iskclo pairs exist).

## Proofs

R13. It is not the case that: If x =< y then y =< x.

  (1) [S2] Take the case x = reldvint, y = wrenmux, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 9 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T5. If y lies in the rastqen of x, then the rastqen of y is contained in the rastqen of x.

  (1) [D4] Let y satisfy x =< y and let z satisfy y =< z.
  (2) [A4] Transitivity gives x =< z.
  (3) [D4] So every member of the rastqen of y is a member of that of x.

Checked over 27 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward iskclo pairs and a wrenwren. Later chapters state their results in these
terms and do not restate the definitions.

Established here and safe to use: T5.

Explicitly not available: R13. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

This chapter carries no exercises. Nothing in it can be asked about in a way that could
not be answered without reading it, and an exercise like that is worse than none.
