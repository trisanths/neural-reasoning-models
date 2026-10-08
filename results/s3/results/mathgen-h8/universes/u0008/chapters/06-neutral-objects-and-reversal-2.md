# Chapter 7. Neutral objects and reversal (2)

## Why this chapter

The practical content of this chapter is opaltez ovimorns, the oviovi of a ovimorn and
where the wrenglim swallows everything breaks down. It is the part that shows up in use.

Prerequisites are real here: chapters 2 and 4 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over ovimorns, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D10. Opaltez ovimorns. A ovimorn x is opaltez when x : x equals the wrenglim.

Running the definition over every ovimorn leaves rastmi.

D11. The oviovi of a ovimorn. A oviovi of a ovimorn x is a ovimorn y with x : y = y : x
= rastmi.

Worked out for each ovimorn: rastmi to rastmi; bradri to muxvor; wrenkorr to tezkeld;
tezkeld to wrenkorr; muxvor to bradri.

## The shape of it

Neutrality is a strong condition disguised as a weak one. It fixes a single ovimorn and,
through that, constrains everything that can combine with it.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R5 rests on D5 (the wrenglim). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T1 rests on D5 (the wrenglim) and A4 (a neutral object for the first operation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Take (tezkeld : rastmi) : wrenkorr and work it out one step at a time.
    tezkeld : rastmi = tezkeld   (the table for :)
    tezkeld : wrenkorr = rastmi   (the table for :)
So (tezkeld : rastmi) : wrenkorr is rastmi.

Move the brackets and the work changes. Take rastmi : (wrenkorr : tezkeld).
    wrenkorr : tezkeld = rastmi   (the table for :)
    rastmi : rastmi = rastmi   (the table for :)
That gives rastmi, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
bradri :: wrenkorr hold? Read off what bradri stands over: rastmi, bradri, wrenkorr,
tezkeld and muxvor. wrenkorr is among them, so it holds.

## A case that breaks

R5. It is not the case that: e : x equals the wrenglim for every ovimorn x. It fails at
anchor = rastmi, x = bradri, value = bradri. One case is enough, and this is the
earliest one.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by a neutral object for the first operation, closure under the first
operation and reversal under the first operation. A system without them is not a system
where these results are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A4 (a neutral object for the first operation), A5 (reversal under the
first operation), D1 (tarnkorr ovimorns) and D5 (the wrenglim).

What is built on it later: T3 (a ovimorn has only one oviovi) and T4 (a opaltez ovimorn
is its own oviovi).

## Proofs

R5. It is not the case that: e : x equals the wrenglim for every ovimorn x.

  (1) [S2] Take the case anchor = rastmi, x = bradri, value = bradri, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T1. There is exactly one ovimorn e with e : x = x : e = x for every ovimorn x.

  (1) [D5] Suppose e and f both leave every ovimorn unchanged.
  (2) [A4] Then e : f = f, reading e as neutral on the left.
  (3) [A4] And e : f = e, reading f as neutral on the right.
  (4) So e = f, and the two suppositions describe the same object.

Checked over 25 cases: every object paired with every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward opaltez ovimorns and the oviovi of a ovimorn. Later chapters state their
results in these terms and do not restate the definitions.

The results now available are T1, each settled by exhaustive check rather than by
argument from analogy.

Do not carry forward R5. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x026. Write down the opaltez in full.
  x027. Which ovimorn reverses bradri under :?
  x028. Which ovimorn reverses wrenkorr under :?
  x029. Which ovimorn reverses tezkeld under :?
  x030. Which ovimorn reverses muxvor under :?
Level 5.
  x031. Let z be bradri : rastmi. Name the oviovi of z.
  x032. Let z be muxvor : muxvor. Name the oviovi of z.
  x045. The following fails in this system: e : x equals the wrenglim for every ovimorn x. Name the earliest ovimorn, in the order the ovimorns were introduced, that witnesses the failure.
