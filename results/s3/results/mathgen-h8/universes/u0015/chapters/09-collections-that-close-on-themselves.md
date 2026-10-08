# Chapter 10. Collections that close on themselves

## Why this chapter

Anyone using this system to keep track of something will meet the pyryuk of a tezka, a
tezka has only one tezzam and the nyrpon of a tezka is qenduth early, whether or not
they go looking.

Prerequisites are real here: chapters 1, 6, 8 and 9 supply the notions the statements
below are phrased in.

One habit to adopt: when a statement below quantifies over tezkas, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D12. The pyryuk of a tezka. The pyryuk of a tezka x is the number of tezkas in its
nyrpon [x].

Worked out for each tezka: lumwren to 1; vorzel to 3; opalfex to 3.

## The shape of it

The right picture for nyrpon is a spreading stain rather than a list. Drop one tezka in,
apply the operation to whatever is wet, repeat. The stain here reaches 1 and 3 tezkas
depending on where it started.

Neutrality is a strong condition disguised as a weak one. It fixes a single tezka and,
through that, constrains everything that can combine with it.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T3 rests on D11 (the tezzam of a tezka), A2 (association of the first operation) and T1
(the yukvex is the only one of its kind). The dependence is on the content of those
results, not only on their vocabulary.

T6 rests on D8 (the nyrpon of a tezka) and D3 (qenduth collections). The dependence is
on the content of those results, not only on their vocabulary.

## A worked case

Evaluate (vorzel >< vorzel) >< (vorzel >< vorzel). Each line below is one lookup in a
table.
    vorzel >< vorzel = opalfex   (the table for ><)
    vorzel >< vorzel = opalfex   (the table for ><)
    opalfex >< opalfex = vorzel   (the table for ><)
That leaves vorzel, and no other reading of the notation gives anything else.

A companion case, vorzel >< (vorzel >< vorzel), to show what the brackets are doing.
    vorzel >< vorzel = opalfex   (the table for ><)
    vorzel >< opalfex = lumwren   (the table for ><)
The value is lumwren, not vorzel.

One decision about the relation, since deciding is as much a skill as computing. Does
lumwren <~ vorzel hold? Read off what lumwren stands over: lumwren, vorzel and opalfex.
vorzel is among them, so it holds.

A second case, this time a nyrpon. Start from lumwren. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is lumwren, so the
pyryuk of lumwren is 1.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of tezkas that come back
unchanged from themselves: lumwren. Assuming more of them than that is the mistake to
avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by a neutral object for the first operation, association of the
first operation, closure under the first operation and reversal under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A2 (association of the first operation), D11
(the tezzam of a tezka), D3 (qenduth collections) and D8 (the nyrpon of a tezka).

What is built on it later: D13 (the duthquil), T4 (a hobthra tezka is its own tezzam),
T7 (the nyrpon is contained in every qenduth collection) and T8 (a tezka is xilvash
exactly when its pyryuk is one).

## Proofs

T3. For every tezka x there is exactly one tezzam of x.

  (1) [D11] Let y and z both be partners of x.
  (2) [A2] Then y = y >< (x >< z) = (y >< x) >< z.
  (3) [D11] Both bracketed products collapse to the neutral object.
  (4) So y = z.

Checked over 9 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T6. For every tezka x, the collection [x] is qenduth.

  (1) [D8] [x] is built by taking x and closing under ><.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 27 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the pyryuk of a tezka. Each of these is used by name
later, so the names are worth learning rather than looking up.

The results now available are T3 and T6, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x026. How many tezkas lie in [vorzel]?
  x027. How many tezkas lie in [opalfex]?
Level 5.
  x028. Let z be (lumwren >< vorzel) >< lumwren. What is the pyryuk of z?
  x029. Let z be vorzel >< lumwren | opalfex. What is the pyryuk of z?
  x030. Let z be opalfex >< vorzel | opalfex. What is the pyryuk of z?
  x031. Let z be opalfex >< vorzel | vorzel. What is the pyryuk of z?
  x032. Let z be (vorzel >< vorzel) >< lumwren. What is the pyryuk of z?
  x033. Let z be vorzel >< vorzel | lumwren. What is the pyryuk of z?
