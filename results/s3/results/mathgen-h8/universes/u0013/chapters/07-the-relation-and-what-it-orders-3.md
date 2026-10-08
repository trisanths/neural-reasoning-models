# Chapter 8. The relation and what it orders (3)

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through the ponwren of a xilzam, there
is at most one umbmux and the system has a umbmux.

Prerequisites are real here: chapters 3 and 6 supply the notions the statements below
are phrased in.

The standard of proof here is exhaustion. A universal claim about xilzams covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

## What is defined here

D8. The ponwren of a xilzam. The ponwren of a xilzam x, written [x], is the smallest
hurnkeld collection that contains x.

Worked out for each xilzam: muxovi to muxovi; nyrfex to nyrfex, ovimux and shennak;
ovimux to ovimux and shennak; shennak to shennak.

## The shape of it

Picture the ponwren as what happens when you start with one xilzam and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 4 xilzams, that stops. In this system the sizes it stops at are 1, 2 and 3.

The relation is easiest to see as a height. Each xilzam casts a mivint over what it
yields to, and the sizes of those shadows here are 1, 2, 3 and 4. No two are the same
size, so the objects line up in a single file.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T10 rests on D9 (a umbmux) and A10 (antisymmetry of the relation). The dependence is on
the content of those results, not only on their vocabulary.

T11 rests on D9 (a umbmux) and A12 (comparability of every pair). Remove any one of them
and the statement stops making sense, not merely stops being provable.

T13 rests on D13 (duthtu pairs) and A10 (antisymmetry of the relation). Remove any one
of them and the statement stops making sense, not merely stops being provable.

## A worked case

Evaluate (shennak & nyrfex) & (muxovi & ovimux). Each line below is one lookup in a
table.
    shennak & nyrfex = shennak   (the table for &)
    muxovi & ovimux = ovimux   (the table for &)
    shennak & ovimux = shennak   (the table for &)
So (shennak & nyrfex) & (muxovi & ovimux) is shennak.

A companion case, nyrfex & (muxovi & shennak), to show what the brackets are doing.
    muxovi & shennak = shennak   (the table for &)
    nyrfex & shennak = shennak   (the table for &)
That gives shennak, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test muxovi <| ovimux. The mivint of muxovi is muxovi, nyrfex, ovimux and shennak, and
ovimux lies inside it, so the relation holds.

Now compute [ovimux]. Fold ovimux against itself, then fold whatever appeared against
everything present, and stop when a round adds nothing. The result is ovimux and
shennak, of size 2.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of antisymmetry of the relation, closure
under the first operation and comparability of every pair. Those are properties of this
system, not of systems in general.

That is not a rhetorical caution. Take the same 4 objects, the same symbols, and a
different table, and T10 and T13 stop holding. The notation survives the substitution
and the mathematics does not.

## Neighbouring results

Read alongside A10 (antisymmetry of the relation), A12 (comparability of every pair),
D13 (duthtu pairs) and D3 (hurnkeld collections).

These results are used again in D11 (the falisk of a xilzam), T4 (the ponwren of a
xilzam is hurnkeld), T5 (the ponwren is contained in every hurnkeld collection) and T7
(the ponwren of a sibnak xilzam stays in the sibnak).

## Proofs

T10. No two distinct xilzams can both be umbmuxs.

  (1) [D9] Let f and h both be floors.
  (2) [D9] Then f <| h, since h is any object, and h <| f likewise.
  (3) [A10] Antisymmetry forces f = h.

Checked over 16 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T11. Some xilzam umbmuxs the whole system.

  (1) [A12] Every pair is comparable, so the relation orders the objects into a line.
  (2) [D9] The claim is that the line has a bottom.
  (3) The carrier is finite, so the search over candidates terminates.

Checked over 16 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T13. No two distinct xilzams lie in each other's mivint.

  (1) [D13] Suppose x and y form a tight pair.
  (2) [A10] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 16 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the ponwren of a xilzam. Each of these is used by name
later, so the names are worth learning rather than looking up.

Established here and safe to use: T10, T11 and T13.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x022. List the ponwren of nyrfex.
  x023. List the ponwren of ovimux.
Level 4.
  x024. Let z be ovimux & nyrfex. List the ponwren of z.
  x025. Let z be nyrfex & ovimux. List the ponwren of z.
  x041. Name the xilzams that make up the umbmux, which is what the result above is a claim about.
