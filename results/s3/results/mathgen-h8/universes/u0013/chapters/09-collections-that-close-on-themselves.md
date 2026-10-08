# Chapter 10. Collections that close on themselves

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is the falisk of a
xilzam, the ponwren of a xilzam is hurnkeld and the ponwren of a sibnak xilzam stays in
the sibnak.

Nothing here stands on its own. The arguments lean on chapters 6, 7, 8 and 9, and a
reader who has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
xilzams that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D11. The falisk of a xilzam. The falisk of a xilzam x is the number of xilzams in its
ponwren [x].

Worked out for each xilzam: muxovi to 1; nyrfex to 3; ovimux to 2; shennak to 1.

## The shape of it

The right picture for ponwren is a spreading stain rather than a list. Drop one xilzam
in, apply the operation to whatever is wet, repeat. The stain here reaches 1, 2 and 3
xilzams depending on where it started.

A useful mental split: some xilzams are inert under the operation and some are not.
muxovi and shennak come back unchanged when combined with themselves, and muxovi,
nyrfex, ovimux and shennak commute with everything.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T4 rests on D8 (the ponwren of a xilzam) and D3 (hurnkeld collections). Remove any one
of them and the statement stops making sense, not merely stops being provable.

T7 rests on D8 (the ponwren of a xilzam), D6 (the sibnak) and T3 (the sibnak is
hurnkeld). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Here is (nyrfex & muxovi) & (shennak & ovimux), reduced without skipping anything.
    nyrfex & muxovi = nyrfex   (the table for &)
    shennak & ovimux = shennak   (the table for &)
    nyrfex & shennak = shennak   (the table for &)
The expression comes to shennak.

Move the brackets and the work changes. Take muxovi & (shennak & nyrfex).
    shennak & nyrfex = shennak   (the table for &)
    muxovi & shennak = shennak   (the table for &)
The value is shennak. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
nyrfex <| muxovi hold? Read off what nyrfex stands over: nyrfex, ovimux and shennak.
muxovi is not among them, so it fails.

A second case, this time a ponwren. Start from muxovi. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is muxovi, so the
falisk of muxovi is 1.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of xilzams that come back
unchanged from themselves: muxovi and shennak. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by association of the first operation and closure under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: D3 (hurnkeld collections), D6 (the sibnak), D8
(the ponwren of a xilzam) and T3 (the sibnak is hurnkeld).

These results are used again in D12 (the vashquil), T5 (the ponwren is contained in
every hurnkeld collection), T6 (a xilzam is thrami exactly when its falisk is one) and
R8 (where the falisk divides the number of xilzams breaks down).

## Proofs

T4. For every xilzam x, the collection [x] is hurnkeld.

  (1) [D8] [x] is built by taking x and closing under &.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 64 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

T7. If x lies in the sibnak then every xilzam of [x] lies in the sibnak.

  (1) [T3] The sibnak is hurnkeld.
  (2) [D8] [x] is the smallest hurnkeld collection containing x.
  (3) A smallest such collection sits inside any other, and the sibnak is one.

Checked over 16 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the falisk of a xilzam. Each of these is used by name
later, so the names are worth learning rather than looking up.

Established here and safe to use: T4 and T7.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x028. How many xilzams lie in [nyrfex]?
  x029. How many xilzams lie in [shennak]?
Level 5.
  x030. Let z be (nyrfex & muxovi) & nyrfex. What is the falisk of z?
  x031. Let z be nyrfex & muxovi $ muxovi. What is the falisk of z?
  x032. Let z be (nyrfex & nyrfex) & muxovi. What is the falisk of z?
  x033. Let z be (shennak & shennak) & ovimux. What is the falisk of z?
