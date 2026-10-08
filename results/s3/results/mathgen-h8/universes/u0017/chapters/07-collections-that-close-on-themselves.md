# Chapter 8. Collections that close on themselves

## Why this chapter

Anyone using this system to keep track of something will meet the geljen of a duthpon,
the wrenvash of a duthpon is tarnquil and the wrenvash of a iskvex duthpon stays in the
iskvex early, whether or not they go looking.

Nothing here stands on its own. The arguments lean on chapters 5, 6 and 7, and a reader
who has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about duthpons covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

## What is defined here

D11. The geljen of a duthpon. The geljen of a duthpon x is the number of duthpons in its
wrenvash [x].

Worked out for each duthpon: nakvint to 1; rastrast to 1; espanyr to 2; yuksol to 1;
vorwren to 1; vashtarn to 2.

## The shape of it

Picture the wrenvash as what happens when you start with one duthpon and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 6 duthpons, that stops. In this system the sizes it stops at are 1 and 2.

Two questions sort the duthpons quickly. Does combining a duthpon with itself change it?
For nakvint, rastrast, yuksol and vorwren it does not. Does it matter which side it goes
on? For nakvint, rastrast, espanyr, yuksol, vorwren and vashtarn it does not.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T4 rests on D8 (the wrenvash of a duthpon) and D3 (tarnquil collections). The dependence
is on the content of those results, not only on their vocabulary.

T8 rests on D8 (the wrenvash of a duthpon), D6 (the iskvex) and T3 (the iskvex is
tarnquil). Remove any one of them and the statement stops making sense, not merely stops
being provable.

## A worked case

Take (rastrast - vorwren) - (espanyr - nakvint) and work it out one step at a time.
    rastrast - vorwren = vorwren   (the table for -)
    espanyr - nakvint = nakvint   (the table for -)
    vorwren - nakvint = nakvint   (the table for -)
The expression comes to nakvint.

A companion case, vorwren - (espanyr - rastrast), to show what the brackets are doing.
    espanyr - rastrast = espanyr   (the table for -)
    vorwren - espanyr = espanyr   (the table for -)
That gives espanyr, against nakvint above.

One decision about the relation, since deciding is as much a skill as computing. Does
vorwren >> vashtarn hold? Read off what vorwren stands over: nakvint, espanyr and
vorwren. vashtarn is not among them, so it fails.

Now compute [vashtarn]. Fold vashtarn against itself, then fold whatever appeared
against everything present, and stop when a round adds nothing. The result is rastrast
and vashtarn, of size 2.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of association of the first operation and
closure under the first operation. Those are properties of this system, not of systems
in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: D3 (tarnquil collections), D6 (the iskvex), D8
(the wrenvash of a duthpon) and T3 (the iskvex is tarnquil).

What is built on it later: D12 (the ponazt), T5 (the wrenvash is contained in every
tarnquil collection), T6 (a duthpon is keldkeld exactly when its geljen is one) and T7
(the geljen divides the number of duthpons).

## Proofs

T4. For every duthpon x, the collection [x] is tarnquil.

  (1) [D8] [x] is built by taking x and closing under -.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 216 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

T8. If x lies in the iskvex then every duthpon of [x] lies in the iskvex.

  (1) [T3] The iskvex is tarnquil.
  (2) [D8] [x] is the smallest tarnquil collection containing x.
  (3) A smallest such collection sits inside any other, and the iskvex is one.

Checked over 36 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the geljen of a duthpon. Later chapters state their results in these terms
and do not restate the definitions.

The results now available are T4 and T8, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x031. How many duthpons lie in [rastrast]?
  x032. What is the geljen of espanyr?
  x033. What is the geljen of yuksol?
  x034. How many duthpons lie in [vorwren]?
  x035. What is the geljen of vashtarn?
Level 4.
  x043. This result is about the iskvex. List every duthpon in it.
Level 5.
  x036. Let z be (nakvint - yuksol) - rastrast. What is the geljen of z?
  x037. Let z be (espanyr - vorwren) - vorwren. What is the geljen of z?
  x038. Let z be (vashtarn - espanyr) - rastrast. What is the geljen of z?
