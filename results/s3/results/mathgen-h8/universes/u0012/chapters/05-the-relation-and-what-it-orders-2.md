# Chapter 6. The relation and what it orders (2)

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is keldthra pairs,
tuopal collections and a mornisk.

Nothing here stands on its own. The arguments lean on chapters 1 and 3, and a reader who
has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
glimyuks that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D13. Keldthra pairs. Two distinct glimyuks x and y form a keldthra pair when x >- y and
y >- x both hold, that is, when each lies in the mornclo of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D3. Tuopal collections. A collection S of glimyuks is tuopal when x & y belongs to S for
every pair x, y drawn from S.

D9. A mornisk. A glimyuk f is a mornisk when f >- y holds for every glimyuk y, that is,
when the mornclo of f is the whole system.

In this system that picks out fexvash, which is 1 of the 6 glimyuks.

## The shape of it

The right picture for xilvor is a spreading stain rather than a list. Drop one glimyuk
in, apply the operation to whatever is wet, repeat. The stain here reaches 1, 2, 3 and 5
glimyuks depending on where it started.

Think of >- as pointing downhill. The mornclo of a glimyuk is everything downhill of it,
and those shadows here have sizes 1, 2, 3, 4, 5 and 6.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 glimyuks the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R9 rests on D4 (the mornclo of a glimyuk). The dependence is on the content of those
results, not only on their vocabulary.

T12 rests on D4 (the mornclo of a glimyuk) and A15 (agreement of the relation with the
first operation). The dependence is on the content of those results, not only on their
vocabulary.

T9 rests on D4 (the mornclo of a glimyuk) and A13 (transitivity of the relation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Here is (fexvash & ovifal) & (kanyr & quilisk), reduced without skipping anything.
    fexvash & ovifal = ovifal   (the table for &)
    kanyr & quilisk = kanyr   (the table for &)
    ovifal & kanyr = kanyr   (the table for &)
The expression comes to kanyr.

A companion case, ovifal & (kanyr & fexvash), to show what the brackets are doing.
    kanyr & fexvash = kanyr   (the table for &)
    ovifal & kanyr = kanyr   (the table for &)
The value is kanyr. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
muxreld >- kanyr hold? Read off what muxreld stands over: muxreld, quilisk, ovifal and
kanyr. kanyr is among them, so it holds.

## A case that breaks

R9. It is not the case that: If x >- y then y >- x. The case that settles it: x =
fexvash, y = kamorn. Anyone carrying this claim over from a more familiar system will be
wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of agreement of the relation with the first
operation, closure under the first operation and transitivity of the relation. Those are
properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A1 (closure under the first operation), A13
(transitivity of the relation), A15 (agreement of the relation with the first operation)
and D4 (the mornclo of a glimyuk).

These results are used again in D8 (the xilvor of a glimyuk), T3 (the fexsol is tuopal),
T4 (the xilvor of a glimyuk is tuopal) and T8 (the hobkorr is tuopal).

## Proofs

R9. It is not the case that: If x >- y then y >- x.

  (1) [S2] Take the case x = fexvash, y = kamorn, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T12. If x >- y then (x & z) >- (y & z) for every glimyuk z.

  (1) [D4] Let y lie in the mornclo of x.
  (2) [A15] Compatibility applies the operation to both sides at once.
  (3) Nothing else is needed, since z was arbitrary.

Checked over 216 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T9. If y lies in the mornclo of x, then the mornclo of y is contained in the mornclo of x.

  (1) [D4] Let y satisfy x >- y and let z satisfy y >- z.
  (2) [A13] Transitivity gives x >- z.
  (3) [D4] So every member of the mornclo of y is a member of that of x.

Checked over 216 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: keldthra pairs, tuopal collections and a mornisk. Each
of these is used by name later, so the names are worth learning rather than looking up.

Established here and safe to use: T12 and T9.

Do not carry forward R9. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x016. How many glimyuks lie in the smallest tuopal collection containing kamorn?
  x017. How many glimyuks lie in the smallest tuopal collection containing muxreld?
Level 4.
  x032. Write down the mornisk in full.
  x046. The result above concerns mornclos. List the mornclo of fexvash.
  x047. The result above concerns mornclos. List the mornclo of kamorn.
  x048. The result above concerns mornclos. List the mornclo of muxreld.
Level 5.
  x051. The following fails in this system: If x >- y then y >- x. Name the earliest glimyuk, in the order the glimyuks were introduced, that witnesses the failure.
