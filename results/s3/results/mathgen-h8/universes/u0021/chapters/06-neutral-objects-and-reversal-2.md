# Chapter 7. Neutral objects and reversal (2)

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is iskjen lumpons,
the zamduth of a lumpon and where the tuka swallows everything breaks down.

Nothing here stands on its own. The arguments lean on chapters 2 and 4, and a reader who
has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about lumpons covers at most
a few hundred cases, so it is run over all of them. Nothing below rests on an argument
from analogy with a system the reader already knows.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D10. Iskjen lumpons. A lumpon x is iskjen when x - x equals the tuka.

Running the definition over every lumpon leaves glimtez and duthwren.

D11. The zamduth of a lumpon. A zamduth of a lumpon x is a lumpon y with x - y = y - x =
glimtez.

Worked out for each lumpon: glimtez to glimtez; glimkorr to mornhob; nakkorr to kaka;
duthwren to duthwren; kaka to nakkorr; mornhob to glimkorr.

## The shape of it

The neutral lumpon glimtez is the one that does nothing. That sounds trivial and is not:
almost every result in this chapter is an argument about what doing nothing forces.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R6 rests on D5 (the tuka). Remove any one of them and the statement stops making sense,
not merely stops being provable.

T1 rests on D5 (the tuka) and A4 (a neutral object for the first operation). The
dependence is on the content of those results, not only on their vocabulary.

## A worked case

Take (duthwren - glimtez) - mornhob and work it out one step at a time.
    duthwren - glimtez = duthwren   (the table for -)
    duthwren - mornhob = nakkorr   (the table for -)
That leaves nakkorr, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is glimtez - (mornhob - duthwren) for contrast.
    mornhob - duthwren = nakkorr   (the table for -)
    glimtez - nakkorr = nakkorr   (the table for -)
The value is nakkorr. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
glimtez >- mornhob hold? Read off what glimtez stands over: glimtez, glimkorr, nakkorr,
duthwren, kaka and mornhob. mornhob is among them, so it holds.

## A case that breaks

R6. It is not the case that: e - x equals the tuka for every lumpon x. The case that
settles it: anchor = glimtez, x = glimkorr, value = glimkorr. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation,
closure under the first operation and reversal under the first operation. Those are
properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A4 (a neutral object for the first operation), A5 (reversal under the
first operation), D1 (pontez lumpons) and D5 (the tuka).

What is built on it later: T3 (a lumpon has only one zamduth) and T4 (a iskjen lumpon is
its own zamduth).

## Proofs

R6. It is not the case that: e - x equals the tuka for every lumpon x.

  (1) [S2] Take the case anchor = glimtez, x = glimkorr, value = glimkorr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T1. There is exactly one lumpon e with e - x = x - e = x for every lumpon x.

  (1) [D5] Suppose e and f both leave every lumpon unchanged.
  (2) [A4] Then e - f = f, reading e as neutral on the left.
  (3) [A4] And e - f = e, reading f as neutral on the right.
  (4) So e = f, and the two suppositions describe the same object.

Checked over 36 cases: every object paired with every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: iskjen lumpons and the zamduth of a lumpon. Each of
these is used by name later, so the names are worth learning rather than looking up.

Established here and safe to use: T1.

Do not carry forward R6. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x034. List every lumpon in the iskjen.
  x035. Which lumpon reverses glimkorr under -?
  x036. Name the zamduth of nakkorr.
  x037. Which lumpon reverses kaka under -?
  x038. Name the zamduth of mornhob.
Level 5.
  x039. Let z be glimkorr - duthwren. Name the zamduth of z.
  x040. Let z be mornhob - duthwren. Name the zamduth of z.
  x041. Let z be duthwren - mornhob. Name the zamduth of z.
  x059. The following fails in this system: e - x equals the tuka for every lumpon x. Name the earliest lumpon, in the order the lumpons were introduced, that witnesses the failure.
