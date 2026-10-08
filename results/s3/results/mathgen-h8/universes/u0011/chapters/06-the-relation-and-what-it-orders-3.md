# Chapter 7. The relation and what it orders (3)

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is the quilnak of a
aztfal, there is at most one tarntez and no grixespa pairs exist.

Prerequisites are real here: chapters 3 and 5 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over aztfals, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D8. The quilnak of a aztfal. The quilnak of a aztfal x, written [x], is the smallest
vintpon collection that contains x.

Worked out for each aztfal: korrhob to korrhob; pyrnak to pyrnak; korrglim to korrglim;
lornjen to lornjen; nakqen to nakqen; aztclo to aztclo.

## The shape of it

Picture the quilnak as what happens when you start with one aztfal and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 6 aztfals, that stops. In this system the sizes it stops at are 1.

Think of << as pointing downhill. The tezmi of a aztfal is everything downhill of it,
and those shadows here have sizes 1, 2, 3, 4 and 6.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 aztfals the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T11 rests on D9 (a tarntez) and A8 (antisymmetry of the relation). The dependence is on
the content of those results, not only on their vocabulary.

T13 rests on D13 (grixespa pairs) and A8 (antisymmetry of the relation). The dependence
is on the content of those results, not only on their vocabulary.

## A worked case

Here is (nakqen & aztclo) & korrhob, reduced without skipping anything.
    nakqen & aztclo = aztclo   (the table for &)
    aztclo & korrhob = aztclo   (the table for &)
The expression comes to aztclo.

A companion case, aztclo & (korrhob & nakqen), to show what the brackets are doing.
    korrhob & nakqen = nakqen   (the table for &)
    aztclo & nakqen = aztclo   (the table for &)
The value is aztclo. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test korrglim << pyrnak. The tezmi of korrglim is korrhob and korrglim, and pyrnak lies
outside it, so the relation fails.

Now compute [aztclo]. Fold aztclo against itself, then fold whatever appeared against
everything present, and stop when a round adds nothing. The result is aztclo, of size 1.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of aztfals that come back
unchanged from themselves: korrhob, pyrnak, korrglim, lornjen, nakqen and aztclo.
Assuming more of them than that is the mistake to avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by antisymmetry of the relation and closure under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A8 (antisymmetry of the relation), D13 (grixespa pairs), D3 (vintpon
collections) and D9 (a tarntez).

These results are used again in D11 (the duthnyr of a aztfal), T4 (the quilnak of a
aztfal is vintpon), T5 (the quilnak is contained in every vintpon collection) and T8
(the quilnak of a nakpyr aztfal stays in the nakpyr).

## Proofs

T11. No two distinct aztfals can both be tarntezs.

  (1) [D9] Let f and h both be floors.
  (2) [D9] Then f << h, since h is any object, and h << f likewise.
  (3) [A8] Antisymmetry forces f = h.

Checked over 36 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T13. No two distinct aztfals lie in each other's tezmi.

  (1) [D13] Suppose x and y form a tight pair.
  (2) [A8] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the quilnak of a aztfal. Later chapters state their results in these terms
and do not restate the definitions.

Established here and safe to use: T11 and T13.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x037. Name the aztfals that make up the tarntez, which is what the result above is a claim about.
