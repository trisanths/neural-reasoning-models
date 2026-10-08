# Chapter 10. Collections that close on themselves

## Why this chapter

Work through this chapter with the tables in front of you. It covers the keldvash of a
wrenhob, the mimux of a wrenhob is yukxil and the mimux of a vintvint wrenhob stays in
the vintvint, and each claim can be checked by hand.

Prerequisites are real here: chapters 6, 7, 8 and 9 supply the notions the statements
below are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
wrenhobs that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D11. The keldvash of a wrenhob. The keldvash of a wrenhob x is the number of wrenhobs in
its mimux [x].

Worked out for each wrenhob: iskglim to 1; lornhob to 5; tuisk to 3; kaglim to 2; xilfal
to 2; ovipyr to 1.

## The shape of it

Picture the mimux as what happens when you start with one wrenhob and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 6 wrenhobs, that stops. In this system the sizes it stops at are 1, 2, 3 and 5.

Two questions sort the wrenhobs quickly. Does combining a wrenhob with itself change it?
For iskglim and ovipyr it does not. Does it matter which side it goes on? For iskglim,
lornhob, tuisk, kaglim, xilfal and ovipyr it does not.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T4 rests on D8 (the mimux of a wrenhob) and D3 (yukxil collections). Remove any one of
them and the statement stops making sense, not merely stops being provable.

T7 rests on D8 (the mimux of a wrenhob), D6 (the vintvint) and T3 (the vintvint is
yukxil). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Evaluate (xilfal ; lornhob) ; (kaglim ; tuisk). Each line below is one lookup in a
table.
    xilfal ; lornhob = ovipyr   (the table for ;)
    kaglim ; tuisk = ovipyr   (the table for ;)
    ovipyr ; ovipyr = ovipyr   (the table for ;)
So (xilfal ; lornhob) ; (kaglim ; tuisk) is ovipyr.

A companion case, lornhob ; (kaglim ; xilfal), to show what the brackets are doing.
    kaglim ; xilfal = ovipyr   (the table for ;)
    lornhob ; ovipyr = ovipyr   (the table for ;)
That gives ovipyr, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test ovipyr >- xilfal. The solzam of ovipyr is ovipyr, and xilfal lies outside it, so
the relation fails.

Now compute [iskglim]. Fold iskglim against itself, then fold whatever appeared against
everything present, and stop when a round adds nothing. The result is iskglim, of size
1.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of wrenhobs that come back
unchanged from themselves: iskglim and ovipyr. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of association of the first operation and
closure under the first operation. Those are properties of this system, not of systems
in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: D3 (yukxil collections), D6 (the vintvint), D8
(the mimux of a wrenhob) and T3 (the vintvint is yukxil).

What is built on it later: D12 (the korrrast), T5 (the mimux is contained in every
yukxil collection), T6 (a wrenhob is drimi exactly when its keldvash is one) and R8
(where the keldvash divides the number of wrenhobs breaks down).

## Proofs

T4. For every wrenhob x, the collection [x] is yukxil.

  (1) [D8] [x] is built by taking x and closing under ;.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 216 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

T7. If x lies in the vintvint then every wrenhob of [x] lies in the vintvint.

  (1) [T3] The vintvint is yukxil.
  (2) [D8] [x] is the smallest yukxil collection containing x.
  (3) A smallest such collection sits inside any other, and the vintvint is one.

Checked over 36 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the keldvash of a wrenhob. Each of these is used by
name later, so the names are worth learning rather than looking up.

Established here and safe to use: T4 and T7.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x032. How many wrenhobs lie in [lornhob]?
  x033. What is the keldvash of tuisk?
  x034. What is the keldvash of kaglim?
  x035. How many wrenhobs lie in [xilfal]?
  x036. How many wrenhobs lie in [ovipyr]?
Level 5.
  x037. Let z be (lornhob ; iskglim) ; lornhob. What is the keldvash of z?
  x038. Let z be xilfal ; tuisk |= ovipyr. What is the keldvash of z?
  x039. Let z be (kaglim ; lornhob) ; lornhob. What is the keldvash of z?
  x040. Let z be lornhob ; lornhob |= xilfal. What is the keldvash of z?
