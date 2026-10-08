# Chapter 8. The relation and what it orders (3)

## Why this chapter

The results collected here were not found in this order. The vintmux of a drigrix, there
is at most one grixvash and no nakkeld pairs exist came first, and the rest was
assembled around that once the pattern was visible.

Prerequisites are real here: chapters 3 and 6 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over drigrixs, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D8. The vintmux of a drigrix. The vintmux of a drigrix x, written [x], is the smallest
vexfex collection that contains x.

Worked out for each drigrix: solvex to solvex; umbazt to umbazt, glimmux, vashtez and
qenvex; glimmux to glimmux and qenvex; vashtez to vashtez and qenvex; qenvex to qenvex.

## The shape of it

Picture the vintmux as what happens when you start with one drigrix and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 5 drigrixs, that stops. In this system the sizes it stops at are 1, 2 and 4.

Think of :: as pointing downhill. The aztdri of a drigrix is everything downhill of it,
and those shadows here have sizes 1 and 5.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T10 rests on D9 (a grixvash) and A11 (antisymmetry of the relation). Remove any one of
them and the statement stops making sense, not merely stops being provable.

T11 rests on D13 (nakkeld pairs) and A11 (antisymmetry of the relation). The dependence
is on the content of those results, not only on their vocabulary.

## A worked case

Evaluate (vashtez @ glimmux) @ (qenvex @ solvex). Each line below is one lookup in a
table.
    vashtez @ glimmux = qenvex   (the table for @)
    qenvex @ solvex = qenvex   (the table for @)
    qenvex @ qenvex = qenvex   (the table for @)
So (vashtez @ glimmux) @ (qenvex @ solvex) is qenvex.

Move the brackets and the work changes. Take glimmux @ (qenvex @ vashtez).
    qenvex @ vashtez = qenvex   (the table for @)
    glimmux @ qenvex = qenvex   (the table for @)
The value is qenvex. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
qenvex :: vashtez hold? Read off what qenvex stands over: solvex, umbazt, glimmux,
vashtez and qenvex. vashtez is among them, so it holds.

A second case, this time a vintmux. Start from umbazt. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is umbazt, glimmux,
vashtez and qenvex, so the mornzam of umbazt is 4.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of drigrixs that come back
unchanged from themselves: solvex and qenvex. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by antisymmetry of the relation and closure under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A11 (antisymmetry of the relation), D13 (nakkeld pairs), D3 (vexfex
collections) and D9 (a grixvash).

These results are used again in D11 (the mornzam of a drigrix), T4 (the vintmux of a
drigrix is vexfex), T5 (the vintmux is contained in every vexfex collection) and T7 (the
vintmux of a kapon drigrix stays in the kapon).

## Proofs

T10. No two distinct drigrixs can both be grixvashs.

  (1) [D9] Let f and h both be floors.
  (2) [D9] Then f :: h, since h is any object, and h :: f likewise.
  (3) [A11] Antisymmetry forces f = h.

Checked over 25 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T11. No two distinct drigrixs lie in each other's aztdri.

  (1) [D13] Suppose x and y form a tight pair.
  (2) [A11] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the vintmux of a drigrix. Later chapters state their results in these
terms and do not restate the definitions.

The results now available are T10 and T11, each settled by exhaustive check rather than
by argument from analogy.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x025. Name every drigrix in [umbazt].
  x026. Name every drigrix in [glimmux].
  x027. List the vintmux of vashtez.
Level 4.
  x028. Let z be glimmux @ umbazt. List the vintmux of z.
  x029. Let z be solvex @ umbazt. List the vintmux of z.
  x030. Let z be solvex @ vashtez. List the vintmux of z.
  x046. Name the drigrixs that make up the grixvash, which is what the result above is a claim about.
