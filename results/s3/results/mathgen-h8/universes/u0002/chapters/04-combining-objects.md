# Chapter 5. Combining objects

## Why this chapter

The present chapter develops pyrtez zelbras, zelbras that vorazt and naknak collections.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over zelbras, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D1. Pyrtez zelbras. A zelbra x is called pyrtez when x * x = x.

In this system that picks out tarnnyr, which is 1 of the 4 zelbras.

D2. Zelbras that vorazt. Two zelbras x and y are said to vorazt when x * y = y * x.

D3. Naknak collections. A collection S of zelbras is naknak when x * y belongs to S for
every pair x, y drawn from S.

## The shape of it

The right picture for vintka is a spreading stain rather than a list. Drop one zelbra
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
zelbras depending on where it started.

A useful mental split: some zelbras are inert under the operation and some are not.
tarnnyr come back unchanged when combined with themselves, and none commutes with
everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 zelbras the table is short enough to consult every time.

## Where these results come from

Nothing is derived in this chapter. It lays down material that later chapters draw on.

## A worked case

Evaluate cloxil * iskmi - isktez. Each line below is one lookup in a table.
    iskmi - isktez = iskmi   (the table for -)
    cloxil * iskmi = tarnnyr   (the table for *)
That leaves tarnnyr, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take iskmi * (isktez * cloxil).
    isktez * cloxil = cloxil   (the table for *)
    iskmi * cloxil = isktez   (the table for *)
That gives isktez, against tarnnyr above.

One decision about the relation, since deciding is as much a skill as computing. Does
cloxil <~ isktez hold? Read off what cloxil stands over: cloxil, isktez and iskmi.
isktez is among them, so it holds.

## A case that breaks

A quick guard against a common slip: cloxil * isktez is tarnnyr while isktez * cloxil is
cloxil. Order is not decoration in this system.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by closure under the first operation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A1 (closure under the first operation).

What is built on it later: D5 (the zelquil), D6 (the rastmorn), D7 (the vintka of a
zelbra) and T1 (the vintka of a zelbra is naknak).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

Carry forward pyrtez zelbras, zelbras that vorazt and naknak collections. Later chapters
state their results in these terms and do not restate the definitions.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x017. Write down the pyrtez in full.
  x018. How many zelbras lie in the smallest naknak collection containing cloxil?
