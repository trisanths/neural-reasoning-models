# Chapter 6. The relation and what it orders (2)

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through thrahob pairs, qenduth
collections and a hurnhob.

Prerequisites are real here: chapters 1 and 3 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over tezkas, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D14. Thrahob pairs. Two distinct tezkas x and y form a thrahob pair when x <~ y and y <~
x both hold, that is, when each lies in the tarnopal of the other.

In this system that picks out lumwren, vorzel and opalfex, that is, all of them.

D3. Qenduth collections. A collection S of tezkas is qenduth when x >< y belongs to S
for every pair x, y drawn from S.

D9. A hurnhob. A tezka f is a hurnhob when f <~ y holds for every tezka y, that is, when
the tarnopal of f is the whole system.

Running the definition over every tezka leaves lumwren, vorzel and opalfex.

## The shape of it

Picture the nyrpon as what happens when you start with one tezka and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 3 tezkas, that stops. In this system the sizes it stops at are 1 and 3.

Think of <~ as pointing downhill. The tarnopal of a tezka is everything downhill of it,
and those shadows here have sizes 3.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T13 rests on D4 (the tarnopal of a tezka) and A13 (transitivity of the relation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

T15 rests on D4 (the tarnopal of a tezka) and A15 (agreement of the relation with the
first operation). Remove any one of them and the statement stops making sense, not
merely stops being provable.

T18 rests on D4 (the tarnopal of a tezka). Remove any one of them and the statement
stops making sense, not merely stops being provable.

## A worked case

Take (vorzel >< vorzel) >< (vorzel >< lumwren) and work it out one step at a time.
    vorzel >< vorzel = opalfex   (the table for ><)
    vorzel >< lumwren = vorzel   (the table for ><)
    opalfex >< vorzel = lumwren   (the table for ><)
The expression comes to lumwren.

Bracketing is not cosmetic, so here is vorzel >< (vorzel >< vorzel) for contrast.
    vorzel >< vorzel = opalfex   (the table for ><)
    vorzel >< opalfex = lumwren   (the table for ><)
The value is lumwren. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
lumwren <~ lumwren hold? Read off what lumwren stands over: lumwren, vorzel and opalfex.
lumwren is among them, so it holds.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by agreement of the relation with the first operation, closure under
the first operation and transitivity of the relation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A1 (closure under the first operation), A13 (transitivity of the
relation), A15 (agreement of the relation with the first operation) and D4 (the tarnopal
of a tezka).

These results are used again in D8 (the nyrpon of a tezka), T5 (the drilorn is qenduth),
T6 (the nyrpon of a tezka is qenduth) and T11 (the lorngrix is qenduth).

## Proofs

T13. If y lies in the tarnopal of x, then the tarnopal of y is contained in the tarnopal of x.

  (1) [D4] Let y satisfy x <~ y and let z satisfy y <~ z.
  (2) [A13] Transitivity gives x <~ z.
  (3) [D4] So every member of the tarnopal of y is a member of that of x.

Checked over 27 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T15. If x <~ y then (x >< z) <~ (y >< z) for every tezka z.

  (1) [D4] Let y lie in the tarnopal of x.
  (2) [A15] Compatibility applies the operation to both sides at once.
  (3) Nothing else is needed, since z was arbitrary.

Checked over 27 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T18. If x <~ y then y <~ x.

  (1) [D4] Symmetry would mean y lies in the tarnopal of x exactly when x lies in that of y.
  (2) The listed pairs settle it directly.

Checked over 9 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: thrahob pairs, qenduth collections and a hurnhob. Each
of these is used by name later, so the names are worth learning rather than looking up.

The results now available are T13, T15 and T18, each settled by exhaustive check rather
than by argument from analogy.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x013. How many tezkas lie in the smallest qenduth collection containing vorzel?
  x014. How many tezkas lie in the smallest qenduth collection containing opalfex?
