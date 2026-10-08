# Chapter 9. Collections that close on themselves

## Why this chapter

So far the driwrens have been objects to be pushed around. This chapter starts asking
what they are like. We take up the korrquil of a driwren, the ovimorn of a driwren is
reldshen and the ovimorn of a iskkeld driwren stays in the iskkeld.

Prerequisites are real here: chapters 5, 6, 7 and 8 supply the notions the statements
below are phrased in.

The standard of proof here is exhaustion. A universal claim about driwrens covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

## What is defined here

D11. The korrquil of a driwren. The korrquil of a driwren x is the number of driwrens in
its ovimorn [x].

Worked out for each driwren: nakquil to 1; soltarn to 1; muxsib to 1; braovi to 1;
yukzel to 1; thraisk to 1.

## The shape of it

Picture the ovimorn as what happens when you start with one driwren and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 6 driwrens, that stops. In this system the sizes it stops at are 1.

A useful mental split: some driwrens are inert under the operation and some are not.
nakquil, soltarn, muxsib, braovi, yukzel and thraisk come back unchanged when combined
with themselves, and nakquil, soltarn, muxsib, braovi, yukzel and thraisk commute with
everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 driwrens the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T4 rests on D8 (the ovimorn of a driwren) and D3 (reldshen collections). Remove any one
of them and the statement stops making sense, not merely stops being provable.

T8 rests on D8 (the ovimorn of a driwren), D6 (the iskkeld) and T3 (the iskkeld is
reldshen). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Here is (yukzel * soltarn) * thraisk, reduced without skipping anything.
    yukzel * soltarn = yukzel   (the table for *)
    yukzel * thraisk = thraisk   (the table for *)
The expression comes to thraisk.

Move the brackets and the work changes. Take soltarn * (thraisk * yukzel).
    thraisk * yukzel = thraisk   (the table for *)
    soltarn * thraisk = thraisk   (the table for *)
The value is thraisk. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
thraisk << braovi hold? Read off what thraisk stands over: nakquil, soltarn, muxsib,
braovi, yukzel and thraisk. braovi is among them, so it holds.

A second case, this time a ovimorn. Start from muxsib. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is muxsib, so the
korrquil of muxsib is 1.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of driwrens that come back
unchanged from themselves: nakquil, soltarn, muxsib, braovi, yukzel and thraisk.
Assuming more of them than that is the mistake to avoid.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of association of the first operation and
closure under the first operation. Those are properties of this system, not of systems
in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: D3 (reldshen collections), D6 (the iskkeld), D8
(the ovimorn of a driwren) and T3 (the iskkeld is reldshen).

These results are used again in D12 (the falpyr), T5 (the ovimorn is contained in every
reldshen collection), T6 (a driwren is opalfal exactly when its korrquil is one) and T7
(the korrquil divides the number of driwrens).

## Proofs

T4. For every driwren x, the collection [x] is reldshen.

  (1) [D8] [x] is built by taking x and closing under *.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 216 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

T8. If x lies in the iskkeld then every driwren of [x] lies in the iskkeld.

  (1) [T3] The iskkeld is reldshen.
  (2) [D8] [x] is the smallest reldshen collection containing x.
  (3) A smallest such collection sits inside any other, and the iskkeld is one.

Checked over 36 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the korrquil of a driwren. Each of these is used by
name later, so the names are worth learning rather than looking up.

Established here and safe to use: T4 and T8.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x023. What is the korrquil of soltarn?
  x024. What is the korrquil of muxsib?
  x025. What is the korrquil of braovi?
  x026. How many driwrens lie in [yukzel]?
  x027. How many driwrens lie in [thraisk]?
Level 4.
  x033. Name the driwrens that make up the iskkeld, which is what the result above is a claim about.
Level 5.
  x028. Let z be (yukzel * muxsib) * nakquil. What is the korrquil of z?
  x029. Let z be (yukzel * thraisk) * yukzel. What is the korrquil of z?
