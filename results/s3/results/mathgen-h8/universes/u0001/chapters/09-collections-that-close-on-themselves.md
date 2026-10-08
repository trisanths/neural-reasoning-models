# Chapter 10. Collections that close on themselves

## Why this chapter

So far the drigrixs have been objects to be pushed around. This chapter starts asking
what they are like. We take up the mornzam of a drigrix, the vintmux of a drigrix is
vexfex and the vintmux of a kapon drigrix stays in the kapon.

Nothing here stands on its own. The arguments lean on chapters 6, 7, 8 and 9, and a
reader who has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
drigrixs that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D11. The mornzam of a drigrix. The mornzam of a drigrix x is the number of drigrixs in
its vintmux [x].

Worked out for each drigrix: solvex to 1; umbazt to 4; glimmux to 2; vashtez to 2;
qenvex to 1.

## The shape of it

Picture the vintmux as what happens when you start with one drigrix and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 5 drigrixs, that stops. In this system the sizes it stops at are 1, 2 and 4.

A useful mental split: some drigrixs are inert under the operation and some are not.
solvex and qenvex come back unchanged when combined with themselves, and solvex, umbazt,
glimmux, vashtez and qenvex commute with everything.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T4 rests on D8 (the vintmux of a drigrix) and D3 (vexfex collections). Remove any one of
them and the statement stops making sense, not merely stops being provable.

T7 rests on D8 (the vintmux of a drigrix), D6 (the kapon) and T3 (the kapon is vexfex).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

## A worked case

Here is (glimmux @ umbazt) @ (qenvex @ vashtez), reduced without skipping anything.
    glimmux @ umbazt = vashtez   (the table for @)
    qenvex @ vashtez = qenvex   (the table for @)
    vashtez @ qenvex = qenvex   (the table for @)
So (glimmux @ umbazt) @ (qenvex @ vashtez) is qenvex.

Move the brackets and the work changes. Take umbazt @ (qenvex @ glimmux).
    qenvex @ glimmux = qenvex   (the table for @)
    umbazt @ qenvex = qenvex   (the table for @)
The value is qenvex. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
qenvex :: vashtez hold? Read off what qenvex stands over: solvex, umbazt, glimmux,
vashtez and qenvex. vashtez is among them, so it holds.

Now compute [umbazt]. Fold umbazt against itself, then fold whatever appeared against
everything present, and stop when a round adds nothing. The result is umbazt, glimmux,
vashtez and qenvex, of size 4.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of drigrixs that come back
unchanged from themselves: solvex and qenvex. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by association of the first operation and closure under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside D3 (vexfex collections), D6 (the kapon), D8 (the vintmux of a drigrix)
and T3 (the kapon is vexfex).

What is built on it later: D12 (the rastdri), T5 (the vintmux is contained in every
vexfex collection), T6 (a drigrix is opalrast exactly when its mornzam is one) and R10
(where the mornzam divides the number of drigrixs breaks down).

## Proofs

T4. For every drigrix x, the collection [x] is vexfex.

  (1) [D8] [x] is built by taking x and closing under @.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 125 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

T7. If x lies in the kapon then every drigrix of [x] lies in the kapon.

  (1) [T3] The kapon is vexfex.
  (2) [D8] [x] is the smallest vexfex collection containing x.
  (3) A smallest such collection sits inside any other, and the kapon is one.

Checked over 25 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the mornzam of a drigrix. Later chapters state their results in these
terms and do not restate the definitions.

The results now available are T4 and T7, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x033. How many drigrixs lie in [umbazt]?
  x034. What is the mornzam of glimmux?
  x035. What is the mornzam of vashtez?
  x036. How many drigrixs lie in [qenvex]?
Level 5.
  x037. Let z be umbazt @ glimmux + vashtez. What is the mornzam of z?
  x038. Let z be vashtez @ qenvex + solvex. What is the mornzam of z?
  x039. Let z be (umbazt @ vashtez) @ qenvex. What is the mornzam of z?
