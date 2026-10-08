# Chapter 5. The relation and what it orders (2)

## Why this chapter

So far the lumpons have been objects to be pushed around. This chapter starts asking
what they are like. We take up cloka pairs, lumvex collections and a aztlum.

Nothing here stands on its own. The arguments lean on chapters 1 and 3, and a reader who
has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over lumpons, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D14. Cloka pairs. Two distinct lumpons x and y form a cloka pair when x >- y and y >- x
both hold, that is, when each lies in the yukglim of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D3. Lumvex collections. A collection S of lumpons is lumvex when x - y belongs to S for
every pair x, y drawn from S.

D9. A aztlum. A lumpon f is a aztlum when f >- y holds for every lumpon y, that is, when
the yukglim of f is the whole system.

Running the definition over every lumpon leaves glimtez.

## The shape of it

Picture the umbquil as what happens when you start with one lumpon and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 6 lumpons, that stops. In this system the sizes it stops at are 1, 2, 3 and 6.

The relation is easiest to see as a height. Each lumpon casts a yukglim over what it
precedes, and the sizes of those shadows here are 1, 2, 3, 4, 5 and 6. No two are the
same size, so the objects line up in a single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 lumpons the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R5 rests on D4 (the yukglim of a lumpon). Remove any one of them and the statement stops
making sense, not merely stops being provable.

T13 rests on D4 (the yukglim of a lumpon) and A9 (transitivity of the relation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Here is (duthwren - glimtez) - nakkorr, reduced without skipping anything.
    duthwren - glimtez = duthwren   (the table for -)
    duthwren - nakkorr = mornhob   (the table for -)
That leaves mornhob, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is glimtez - (nakkorr - duthwren) for contrast.
    nakkorr - duthwren = mornhob   (the table for -)
    glimtez - mornhob = mornhob   (the table for -)
The value is mornhob. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test kaka >- kaka. The yukglim of kaka is kaka and mornhob, and kaka lies inside it, so
the relation holds.

## A case that breaks

R5. It is not the case that: If x >- y then y >- x. The case that settles it: x =
glimtez, y = glimkorr. Anyone carrying this claim over from a more familiar system will
be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation and
transitivity of the relation. Those are properties of this system, not of systems in
general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A1 (closure under the first operation), A9
(transitivity of the relation) and D4 (the yukglim of a lumpon).

What is built on it later: D8 (the umbquil of a lumpon), T5 (the glimfex is lumvex), T6
(the umbquil of a lumpon is lumvex) and T11 (the opalkeld is lumvex).

## Proofs

R5. It is not the case that: If x >- y then y >- x.

  (1) [S2] Take the case x = glimtez, y = glimkorr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T13. If y lies in the yukglim of x, then the yukglim of y is contained in the yukglim of x.

  (1) [D4] Let y satisfy x >- y and let z satisfy y >- z.
  (2) [A9] Transitivity gives x >- z.
  (3) [D4] So every member of the yukglim of y is a member of that of x.

Checked over 216 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward cloka pairs, lumvex collections and a aztlum. Later chapters state their
results in these terms and do not restate the definitions.

The results now available are T13, each settled by exhaustive check rather than by
argument from analogy.

Do not carry forward R5. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x022. How many lumpons lie in the smallest lumvex collection containing glimkorr?
  x023. How many lumpons lie in the smallest lumvex collection containing nakkorr?
