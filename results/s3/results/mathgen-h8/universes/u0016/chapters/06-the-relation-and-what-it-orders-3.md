# Chapter 7. The relation and what it orders (3)

## Why this chapter

Work through this chapter with the tables in front of you. It covers the clobra of a
mornglim, there is at most one duthvor and no dripon pairs exist, and each claim can be
checked by hand.

Prerequisites are real here: chapters 3 and 5 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over mornglims, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D8. The clobra of a mornglim. The clobra of a mornglim x, written [x], is the smallest
tezdri collection that contains x.

Worked out for each mornglim: oviazt to oviazt; kapon to kapon; nyrrast to nyrrast;
xilwren to xilwren.

## The shape of it

Picture the clobra as what happens when you start with one mornglim and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 4 mornglims, that stops. In this system the sizes it stops at are 1.

Think of <~ as pointing downhill. The nakhurn of a mornglim is everything downhill of
it, and those shadows here have sizes 1, 2 and 4.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T11 rests on D9 (a duthvor) and A8 (antisymmetry of the relation). The dependence is on
the content of those results, not only on their vocabulary.

T13 rests on D13 (dripon pairs) and A8 (antisymmetry of the relation). Remove any one of
them and the statement stops making sense, not merely stops being provable.

## A worked case

Evaluate (kapon | oviazt) | nyrrast. Each line below is one lookup in a table.
    kapon | oviazt = kapon   (the table for |)
    kapon | nyrrast = xilwren   (the table for |)
The expression comes to xilwren.

A companion case, oviazt | (nyrrast | kapon), to show what the brackets are doing.
    nyrrast | kapon = xilwren   (the table for |)
    oviazt | xilwren = xilwren   (the table for |)
The value is xilwren. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test xilwren <~ nyrrast. The nakhurn of xilwren is xilwren, and nyrrast lies outside it,
so the relation fails.

A second case, this time a clobra. Start from nyrrast. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is nyrrast, so the
nakdri of nyrrast is 1.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by antisymmetry of the relation and closure under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

To see how little the notation guarantees: rebuild the system with the same names over
different tables and T11 and T13 fail outright.

## Neighbouring results

Read alongside A8 (antisymmetry of the relation), D13 (dripon pairs), D3 (tezdri
collections) and D9 (a duthvor).

These results are used again in D11 (the nakdri of a mornglim), T4 (the clobra of a
mornglim is tezdri), T5 (the clobra is contained in every tezdri collection) and T8 (the
clobra of a falespa mornglim stays in the falespa).

## Proofs

T11. No two distinct mornglims can both be duthvors.

  (1) [D9] Let f and h both be floors.
  (2) [D9] Then f <~ h, since h is any object, and h <~ f likewise.
  (3) [A8] Antisymmetry forces f = h.

Checked over 16 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T13. No two distinct mornglims lie in each other's nakhurn.

  (1) [D13] Suppose x and y form a tight pair.
  (2) [A8] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 16 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the clobra of a mornglim. Later chapters state their results in these
terms and do not restate the definitions.

The results now available are T11 and T13, each settled by exhaustive check rather than
by argument from analogy.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x032. This result is about the duthvor. List every mornglim in it.
