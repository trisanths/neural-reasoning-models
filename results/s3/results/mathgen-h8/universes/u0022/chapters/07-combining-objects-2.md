# Chapter 8. Combining objects (2)

## Why this chapter

The practical content of this chapter is every driwren lies in the iskkeld, every
driwren is opalfal and the keldtu lies in the iskkeld. It is the part that shows up in
use.

Nothing here stands on its own. The arguments lean on chapters 1, 4, 5 and 6, and a
reader who has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
driwrens that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

A useful mental split: some driwrens are inert under the operation and some are not.
nakquil, soltarn, muxsib, braovi, yukzel and thraisk come back unchanged when combined
with themselves, and nakquil, soltarn, muxsib, braovi, yukzel and thraisk commute with
everything.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T14 rests on D6 (the iskkeld). The dependence is on the content of those results, not
only on their vocabulary.

T15 rests on D7 (the kami). Remove any one of them and the statement stops making sense,
not merely stops being provable.

T2 rests on D5 (the keldtu) and D6 (the iskkeld). Remove any one of them and the
statement stops making sense, not merely stops being provable.

T3 rests on D6 (the iskkeld), D3 (reldshen collections) and A2 (association of the first
operation). The dependence is on the content of those results, not only on their
vocabulary.

T9 rests on D7 (the kami) and D3 (reldshen collections). The dependence is on the
content of those results, not only on their vocabulary.

## A worked case

Evaluate (thraisk * muxsib) * (braovi * soltarn). Each line below is one lookup in a
table.
    thraisk * muxsib = thraisk   (the table for *)
    braovi * soltarn = braovi   (the table for *)
    thraisk * braovi = thraisk   (the table for *)
That leaves thraisk, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is muxsib * (braovi * thraisk) for contrast.
    braovi * thraisk = thraisk   (the table for *)
    muxsib * thraisk = thraisk   (the table for *)
That gives thraisk, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test thraisk << muxsib. The zelfex of thraisk is nakquil, soltarn, muxsib, braovi,
yukzel and thraisk, and muxsib lies inside it, so the relation holds.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of driwrens that come back
unchanged from themselves: nakquil, soltarn, muxsib, braovi, yukzel and thraisk.
Assuming more of them than that is the mistake to avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by a neutral object for the first operation, association of the
first operation and closure under the first operation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

That is not a rhetorical caution. Take the same 6 objects, the same symbols, and a
different table, and T15 stop holding. The notation survives the substitution and the
mathematics does not.

## Neighbouring results

The material this chapter borrows from: A2 (association of the first operation), D3
(reldshen collections), D5 (the keldtu) and D6 (the iskkeld).

What is built on it later: T8 (the ovimorn of a iskkeld driwren stays in the iskkeld).

## Proofs

T14. Every pair of driwrens rastumbs.

  (1) [D6] The iskkeld is defined by rastumbing with everything.
  (2) [D2] The claim is that x * y = y * x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T15. x * x = x for every driwren x.

  (1) [D1] Being opalfal is the condition x * x = x.
  (2) [D7] The claim is that the kami is the whole system.
  (3) Only the diagonal of the table is involved.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T2. The keldtu rastumbs with every driwren.

  (1) [D5] Let e be the keldtu and x any driwren.
  (2) [D5] Then e * x = x and x * e = x.
  (3) [D2] So e * x = x * e, which is what it means to rastumb.
  (4) [D6] Since x was arbitrary, e belongs to the iskkeld.

Checked over 6 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. If x and y both rastumb with every driwren, then so does x * y.

  (1) [D6] Let x and y lie in the iskkeld and let z be any driwren.
  (2) [A2] Then (x * y) * z = x * (y * z).
  (3) [D6] Move z past y, then past x, using that each rastumbs with everything.
  (4) [D3] So x * y rastumbs with z, and the iskkeld is reldshen.

Checked over 36 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

T9. If x and y are both opalfal then so is x * y.

  (1) [D7] Let x and y be opalfal.
  (2) [D1] The claim asks whether (x * y) * (x * y) returns x * y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 36 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

The results now available are T14, T15, T2, T3 and T9, each settled by exhaustive check
rather than by argument from analogy.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x031. This result is about the iskkeld. List every driwren in it.
  x034. This result is about the kami. List every driwren in it.
