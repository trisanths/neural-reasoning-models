# Chapter 5. The relation and what it orders (2)

## Why this chapter

The results collected here were not found in this order. Umbnyr pairs, a kelddri and
iskespas are nested along the relation came first, and the rest was assembled around
that once the pattern was visible.

Prerequisites are real here: chapter 3 supply the notions the statements below are
phrased in.

One habit to adopt: when a statement below quantifies over rastvashs, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D11. Umbnyr pairs. Two distinct rastvashs x and y form a umbnyr pair when x >> y and y
>> x both hold, that is, when each lies in the iskespa of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D8. A kelddri. A rastvash f is a kelddri when f >> y holds for every rastvash y, that
is, when the iskespa of f is the whole system.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

## The shape of it

The relation is easiest to see as a height. Each rastvash casts a iskespa over what it
supports, and the sizes of those shadows here are 1. Sizes repeat, so the objects do not
line up in single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 rastvashs the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T5 rests on D4 (the iskespa of a rastvash) and A4 (transitivity of the relation). The
dependence is on the content of those results, not only on their vocabulary.

T7 rests on D4 (the iskespa of a rastvash) and A5 (agreement of the relation with the
first operation). The dependence is on the content of those results, not only on their
vocabulary.

T9 rests on D4 (the iskespa of a rastvash). The dependence is on the content of those
results, not only on their vocabulary.

## A worked case

Take (fexrast ? rastumb) ? lumnyr and work it out one step at a time.
    fexrast ? rastumb = lumnyr   (the table for ?)
    lumnyr ? lumnyr = lumpyr   (the table for ?)
The expression comes to lumpyr.

A companion case, rastumb ? (lumnyr ? fexrast), to show what the brackets are doing.
    lumnyr ? fexrast = lumpyr   (the table for ?)
    rastumb ? lumpyr = rastumb   (the table for ?)
The value is rastumb, not lumpyr.

Test fexrast >> rastumb. The iskespa of fexrast is fexrast, and rastumb lies outside it,
so the relation fails.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of rastvashs that come back
unchanged from themselves: lumpyr. Assuming more of them than that is the mistake to
avoid.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by agreement of the relation with the first operation and
transitivity of the relation. A system without them is not a system where these results
are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A4 (transitivity of the relation), A5 (agreement
of the relation with the first operation) and D4 (the iskespa of a rastvash).

These results are used again in T6 (there is at most one kelddri) and T8 (no umbnyr
pairs exist).

## Proofs

T5. If y lies in the iskespa of x, then the iskespa of y is contained in the iskespa of x.

  (1) [D4] Let y satisfy x >> y and let z satisfy y >> z.
  (2) [A4] Transitivity gives x >> z.
  (3) [D4] So every member of the iskespa of y is a member of that of x.

Checked over 125 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T7. If x >> y then (x ? z) >> (y ? z) for every rastvash z.

  (1) [D4] Let y lie in the iskespa of x.
  (2) [A5] Compatibility applies the operation to both sides at once.
  (3) Nothing else is needed, since z was arbitrary.

Checked over 125 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T9. If x >> y then y >> x.

  (1) [D4] Symmetry would mean y lies in the iskespa of x exactly when x lies in that of y.
  (2) The listed pairs settle it directly.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward umbnyr pairs and a kelddri. Later chapters state their results in these
terms and do not restate the definitions.

Established here and safe to use: T5, T7 and T9.

## Exercises

No exercises here. Every question this chapter suggested turned out to be answerable
from the question itself, so all of them were discarded.
