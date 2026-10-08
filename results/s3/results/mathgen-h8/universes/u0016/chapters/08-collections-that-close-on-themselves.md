# Chapter 9. Collections that close on themselves

## Why this chapter

The practical content of this chapter is the nakdri of a mornglim, the clobra of a
mornglim is tezdri and the clobra of a falespa mornglim stays in the falespa. It is the
part that shows up in use.

Nothing here stands on its own. The arguments lean on chapters 5, 6, 7 and 8, and a
reader who has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over mornglims, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D11. The nakdri of a mornglim. The nakdri of a mornglim x is the number of mornglims in
its clobra [x].

Worked out for each mornglim: oviazt to 1; kapon to 1; nyrrast to 1; xilwren to 1.

## The shape of it

Picture the clobra as what happens when you start with one mornglim and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 4 mornglims, that stops. In this system the sizes it stops at are 1.

Two questions sort the mornglims quickly. Does combining a mornglim with itself change
it? For oviazt, kapon, nyrrast and xilwren it does not. Does it matter which side it
goes on? For oviazt, kapon, nyrrast and xilwren it does not.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 mornglims the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T4 rests on D8 (the clobra of a mornglim) and D3 (tezdri collections). Remove any one of
them and the statement stops making sense, not merely stops being provable.

T8 rests on D8 (the clobra of a mornglim), D6 (the falespa) and T3 (the falespa is
tezdri). Remove any one of them and the statement stops making sense, not merely stops
being provable.

## A worked case

Here is (xilwren | nyrrast) | oviazt, reduced without skipping anything.
    xilwren | nyrrast = xilwren   (the table for |)
    xilwren | oviazt = xilwren   (the table for |)
That leaves xilwren, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take nyrrast | (oviazt | xilwren).
    oviazt | xilwren = xilwren   (the table for |)
    nyrrast | xilwren = xilwren   (the table for |)
That gives xilwren, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test oviazt <~ oviazt. The nakhurn of oviazt is oviazt, kapon, nyrrast and xilwren, and
oviazt lies inside it, so the relation holds.

A second case, this time a clobra. Start from nyrrast. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is nyrrast, so the
nakdri of nyrrast is 1.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by association of the first operation and closure under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: D3 (tezdri collections), D6 (the falespa), D8
(the clobra of a mornglim) and T3 (the falespa is tezdri).

These results are used again in D12 (the grixvor), T5 (the clobra is contained in every
tezdri collection), T6 (a mornglim is iskzam exactly when its nakdri is one) and T7 (the
nakdri divides the number of mornglims).

## Proofs

T4. For every mornglim x, the collection [x] is tezdri.

  (1) [D8] [x] is built by taking x and closing under |.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 64 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

T8. If x lies in the falespa then every mornglim of [x] lies in the falespa.

  (1) [T3] The falespa is tezdri.
  (2) [D8] [x] is the smallest tezdri collection containing x.
  (3) A smallest such collection sits inside any other, and the falespa is one.

Checked over 16 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the nakdri of a mornglim. Later chapters state their results in these
terms and do not restate the definitions.

Established here and safe to use: T4 and T8.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x020. What is the nakdri of kapon?
  x021. How many mornglims lie in [nyrrast]?
  x022. How many mornglims lie in [xilwren]?
Level 5.
  x023. Let z be (xilwren | xilwren) | xilwren. What is the nakdri of z?
  x024. Let z be (xilwren | oviazt) | oviazt. What is the nakdri of z?
  x025. Let z be (kapon | oviazt) | oviazt. What is the nakdri of z?
