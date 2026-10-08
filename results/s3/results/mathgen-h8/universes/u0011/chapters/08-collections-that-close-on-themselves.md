# Chapter 9. Collections that close on themselves

## Why this chapter

Anyone using this system to keep track of something will meet the duthnyr of a aztfal,
the quilnak of a aztfal is vintpon and the quilnak of a nakpyr aztfal stays in the
nakpyr early, whether or not they go looking.

Prerequisites are real here: chapters 5, 6, 7 and 8 supply the notions the statements
below are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
aztfals that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D11. The duthnyr of a aztfal. The duthnyr of a aztfal x is the number of aztfals in its
quilnak [x].

Worked out for each aztfal: korrhob to 1; pyrnak to 1; korrglim to 1; lornjen to 1;
nakqen to 1; aztclo to 1.

## The shape of it

Picture the quilnak as what happens when you start with one aztfal and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 6 aztfals, that stops. In this system the sizes it stops at are 1.

A useful mental split: some aztfals are inert under the operation and some are not.
korrhob, pyrnak, korrglim, lornjen, nakqen and aztclo come back unchanged when combined
with themselves, and korrhob, pyrnak, korrglim, lornjen, nakqen and aztclo commute with
everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 aztfals the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T4 rests on D8 (the quilnak of a aztfal) and D3 (vintpon collections). Remove any one of
them and the statement stops making sense, not merely stops being provable.

T8 rests on D8 (the quilnak of a aztfal), D6 (the nakpyr) and T3 (the nakpyr is
vintpon). Remove any one of them and the statement stops making sense, not merely stops
being provable.

## A worked case

Take (korrglim & aztclo) & lornjen and work it out one step at a time.
    korrglim & aztclo = aztclo   (the table for &)
    aztclo & lornjen = aztclo   (the table for &)
The expression comes to aztclo.

A companion case, aztclo & (lornjen & korrglim), to show what the brackets are doing.
    lornjen & korrglim = aztclo   (the table for &)
    aztclo & aztclo = aztclo   (the table for &)
The value is aztclo. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
korrglim << pyrnak hold? Read off what korrglim stands over: korrhob and korrglim.
pyrnak is not among them, so it fails.

A second case, this time a quilnak. Start from lornjen. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is lornjen, so the
duthnyr of lornjen is 1.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of association of the first operation and
closure under the first operation. Those are properties of this system, not of systems
in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside D3 (vintpon collections), D6 (the nakpyr), D8 (the quilnak of a aztfal)
and T3 (the nakpyr is vintpon).

These results are used again in D12 (the korrfex), T5 (the quilnak is contained in every
vintpon collection), T6 (a aztfal is vorduth exactly when its duthnyr is one) and T7
(the duthnyr divides the number of aztfals).

## Proofs

T4. For every aztfal x, the collection [x] is vintpon.

  (1) [D8] [x] is built by taking x and closing under &.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 216 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

T8. If x lies in the nakpyr then every aztfal of [x] lies in the nakpyr.

  (1) [T3] The nakpyr is vintpon.
  (2) [D8] [x] is the smallest vintpon collection containing x.
  (3) A smallest such collection sits inside any other, and the nakpyr is one.

Checked over 36 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the duthnyr of a aztfal. Each of these is used by name
later, so the names are worth learning rather than looking up.

Established here and safe to use: T4 and T8.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x023. How many aztfals lie in [pyrnak]?
  x024. How many aztfals lie in [korrglim]?
  x025. What is the duthnyr of lornjen?
  x026. How many aztfals lie in [nakqen]?
  x027. What is the duthnyr of aztclo?
Level 4.
  x033. Name the aztfals that make up the nakpyr, which is what the result above is a claim about.
Level 5.
  x028. Let z be (pyrnak & korrglim) & pyrnak. What is the duthnyr of z?
  x029. Let z be (nakqen & aztclo) & nakqen. What is the duthnyr of z?
