# Chapter 6. Combining objects (2)

## Why this chapter

The practical content of this chapter is the tunak, the shenhob and combining on the
left never merges two wrenclos. It is the part that shows up in use.

Prerequisites are real here: chapters 1 and 4 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over wrenclos, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D6. The tunak. The tunak of the system is the collection of wrenclos that morntez with
every wrenclo.

In this system that picks out glimfex, bratu, vorkeld and falzam, that is, all of them.

D7. The shenhob. The shenhob is the collection of all opalhurn wrenclos.

In this system that picks out glimfex, which is 1 of the 4 wrenclos.

## The shape of it

A useful mental split: some wrenclos are inert under the operation and some are not.
glimfex come back unchanged when combined with themselves, and glimfex, bratu, vorkeld
and falzam commute with everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 wrenclos the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T12 rests on A6 (cancellation in the first operation) and D2 (wrenclos that morntez).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

## A worked case

Evaluate (glimfex # falzam) # (vorkeld # bratu). Each line below is one lookup in a
table.
    glimfex # falzam = falzam   (the table for #)
    vorkeld # bratu = falzam   (the table for #)
    falzam # falzam = glimfex   (the table for #)
That leaves glimfex, and no other reading of the notation gives anything else.

A companion case, falzam # (vorkeld # glimfex), to show what the brackets are doing.
    vorkeld # glimfex = vorkeld   (the table for #)
    falzam # vorkeld = bratu   (the table for #)
That gives bratu, against glimfex above.

Test falzam <~ vorkeld. The reldxil of falzam is empty, and vorkeld lies outside it, so
the relation fails.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of wrenclos that come back
unchanged from themselves: glimfex. Assuming more of them than that is the mistake to
avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of cancellation in the first operation and
closure under the first operation. Those are properties of this system, not of systems
in general.

To see how little the notation guarantees: rebuild the system with the same names over
different tables and T12 fail outright.

## Neighbouring results

The material this chapter borrows from: A6 (cancellation in the first operation), D1
(opalhurn wrenclos) and D2 (wrenclos that morntez).

What is built on it later: T2 (the ponjen lies in the tunak), T5 (the tunak is
mornvint), T10 (the tuclo of a tunak wrenclo stays in the tunak) and T11 (the shenhob is
mornvint).

## Proofs

T12. For every wrenclo a, the assignment x to a # x sends distinct wrenclos to distinct wrenclos.

  (1) [A6] Suppose a # x = a # y.
  (2) [A6] Cancellation on the left gives x = y.
  (3) So the assignment is injective, and being injective on a finite carrier it is onto.

Checked over 16 cases: every object translated by every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the tunak and the shenhob. Each of these is used by
name later, so the names are worth learning rather than looking up.

The results now available are T12, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x019. Which wrenclos make up the shenhob? Name them all.
