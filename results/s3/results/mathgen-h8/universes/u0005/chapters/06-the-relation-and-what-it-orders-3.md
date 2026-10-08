# Chapter 7. The relation and what it orders (3)

## Why this chapter

The present chapter develops there is at most one wrenwren, the system has a wrenwren
and no iskclo pairs exist.

Nothing here stands on its own. The arguments lean on chapters 3 and 5, and a reader who
has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about jenxils covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

Think of =< as pointing downhill. The rastqen of a jenxil is everything downhill of it,
and those shadows here have sizes 1, 2 and 3.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T6 rests on D8 (a wrenwren) and A3 (antisymmetry of the relation). The dependence is on
the content of those results, not only on their vocabulary.

T7 rests on D8 (a wrenwren) and A5 (comparability of every pair). The dependence is on
the content of those results, not only on their vocabulary.

T8 rests on D11 (iskclo pairs) and A3 (antisymmetry of the relation). The dependence is
on the content of those results, not only on their vocabulary.

## A worked case

Evaluate (wrenmux % zellum) % wrenmux. Each line below is one lookup in a table.
    wrenmux % zellum = reldvint   (the table for %)
    reldvint % wrenmux = reldvint   (the table for %)
So (wrenmux % zellum) % wrenmux is reldvint.

Move the brackets and the work changes. Take zellum % (wrenmux % wrenmux).
    wrenmux % wrenmux = reldvint   (the table for %)
    zellum % reldvint = zellum   (the table for %)
The value is zellum, not reldvint.

Test wrenmux =< wrenmux. The rastqen of wrenmux is wrenmux and zellum, and wrenmux lies
inside it, so the relation holds.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of jenxils that come back
unchanged from themselves: reldvint. Assuming more of them than that is the mistake to
avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by antisymmetry of the relation and comparability of every pair. A
system without them is not a system where these results are harder to prove; it is a
system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A3 (antisymmetry of the relation), A5 (comparability of every pair), D11
(iskclo pairs) and D8 (a wrenwren).

## Proofs

T6. No two distinct jenxils can both be wrenwrens.

  (1) [D8] Let f and h both be floors.
  (2) [D8] Then f =< h, since h is any object, and h =< f likewise.
  (3) [A3] Antisymmetry forces f = h.

Checked over 9 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T7. Some jenxil wrenwrens the whole system.

  (1) [A5] Every pair is comparable, so the relation orders the objects into a line.
  (2) [D8] The claim is that the line has a bottom.
  (3) The carrier is finite, so the search over candidates terminates.

Checked over 9 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T8. No two distinct jenxils lie in each other's rastqen.

  (1) [D11] Suppose x and y form a tight pair.
  (2) [A3] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 9 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Established here and safe to use: T6, T7 and T8.

## Exercises

This chapter carries no exercises. Nothing in it can be asked about in a way that could
not be answered without reading it, and an exercise like that is worse than none.
