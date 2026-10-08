# Chapter 5. Combining objects

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through reldjen grixbras, grixbras
that grixovi and umbgel collections.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about grixbras covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

## What is defined here

D1. Reldjen grixbras. A grixbra x is called reldjen when x @ x = x.

In this system that picks out mika, which is 1 of the 5 grixbras.

D2. Grixbras that grixovi. Two grixbras x and y are said to grixovi when x @ y = y @ x.

D3. Umbgel collections. A collection S of grixbras is umbgel when x @ y belongs to S for
every pair x, y drawn from S.

## The shape of it

Picture the kavor as what happens when you start with one grixbra and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 5 grixbras, that stops. In this system the sizes it stops at are 1 and 2.

A useful mental split: some grixbras are inert under the operation and some are not.
mika come back unchanged when combined with themselves, and none commutes with
everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 grixbras the table is short enough to consult every time.

## Where these results come from

This chapter is groundwork. The derivations that use it start in the next one.

## A worked case

Evaluate fexnyr @ mornthra ! umbtarn. Each line below is one lookup in a table.
    mornthra ! umbtarn = mornthra   (the table for !)
    fexnyr @ mornthra = mika   (the table for @)
The expression comes to mika.

Move the brackets and the work changes. Take mornthra @ (umbtarn @ fexnyr).
    umbtarn @ fexnyr = hobglim   (the table for @)
    mornthra @ hobglim = hobglim   (the table for @)
That gives hobglim, against mika above.

One decision about the relation, since deciding is as much a skill as computing. Does
hobglim %% mornthra hold? Read off what hobglim stands over: hobglim. mornthra is not
among them, so it fails.

## A case that breaks

A quick guard against a common slip: hobglim @ fexnyr is fexnyr while fexnyr @ hobglim
is mika. Order is not decoration in this system.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A1 (closure under the first operation).

What is built on it later: D5 (the quilquil), D6 (the ovitez), D7 (the kavor of a
grixbra) and T1 (the kavor of a grixbra is umbgel).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

New vocabulary from this chapter: reldjen grixbras, grixbras that grixovi and umbgel
collections. Each of these is used by name later, so the names are worth learning rather
than looking up.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x025. Which grixbras make up the reldjen? Name them all.
  x026. How many grixbras lie in the smallest umbgel collection containing fexnyr?
  x027. How many grixbras lie in the smallest umbgel collection containing hobglim?
