# Chapter 10. Collections that close on themselves

## Why this chapter

The present chapter develops the driglim of a thrafex, a thrafex has only one nyrzel and
the muxmi of a thrafex is umbbra.

Nothing here stands on its own. The arguments lean on chapters 1, 6, 8 and 9, and a
reader who has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 3
thrafexs that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D12. The driglim of a thrafex. The driglim of a thrafex x is the number of thrafexs in
its muxmi [x].

Worked out for each thrafex: tuespa to 1; qenmorn to 3; hobzel to 3.

## The shape of it

The right picture for muxmi is a spreading stain rather than a list. Drop one thrafex
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 3
thrafexs depending on where it started.

Neutrality is a strong condition disguised as a weak one. It fixes a single thrafex and,
through that, constrains everything that can combine with it.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 3 thrafexs the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T3 rests on D11 (the nyrzel of a thrafex), A2 (association of the first operation) and
T1 (the nyrrast is the only one of its kind). The dependence is on the content of those
results, not only on their vocabulary.

T6 rests on D8 (the muxmi of a thrafex) and D3 (umbbra collections). The dependence is
on the content of those results, not only on their vocabulary.

## A worked case

Here is (tuespa =| hobzel) =| (hobzel =| hobzel), reduced without skipping anything.
    tuespa =| hobzel = hobzel   (the table for =|)
    hobzel =| hobzel = qenmorn   (the table for =|)
    hobzel =| qenmorn = tuespa   (the table for =|)
The expression comes to tuespa.

Move the brackets and the work changes. Take hobzel =| (hobzel =| tuespa).
    hobzel =| tuespa = hobzel   (the table for =|)
    hobzel =| hobzel = qenmorn   (the table for =|)
That gives qenmorn, against tuespa above.

Test tuespa =< qenmorn. The vextarn of tuespa is tuespa, qenmorn and hobzel, and qenmorn
lies inside it, so the relation holds.

A second case, this time a muxmi. Start from tuespa. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is tuespa, so the
driglim of tuespa is 1.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by a neutral object for the first operation, association of the
first operation, closure under the first operation and reversal under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A2 (association of the first operation), D11 (the nyrzel of a thrafex),
D3 (umbbra collections) and D8 (the muxmi of a thrafex).

These results are used again in D13 (the reldumb), T4 (a iskrast thrafex is its own
nyrzel), T7 (the muxmi is contained in every umbbra collection) and T8 (a thrafex is
solka exactly when its driglim is one).

## Proofs

T3. For every thrafex x there is exactly one nyrzel of x.

  (1) [D11] Let y and z both be partners of x.
  (2) [A2] Then y = y =| (x =| z) = (y =| x) =| z.
  (3) [D11] Both bracketed products collapse to the neutral object.
  (4) So y = z.

Checked over 9 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T6. For every thrafex x, the collection [x] is umbbra.

  (1) [D8] [x] is built by taking x and closing under =|.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 27 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the driglim of a thrafex. Each of these is used by
name later, so the names are worth learning rather than looking up.

Established here and safe to use: T3 and T6.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x026. How many thrafexs lie in [qenmorn]?
  x027. What is the driglim of hobzel?
Level 5.
  x028. Let z be qenmorn =| hobzel ~ tuespa. What is the driglim of z?
  x029. Let z be hobzel =| tuespa ~ hobzel. What is the driglim of z?
  x030. Let z be hobzel =| tuespa ~ tuespa. What is the driglim of z?
  x031. Let z be hobzel =| qenmorn ~ hobzel. What is the driglim of z?
  x032. Let z be (hobzel =| hobzel) =| tuespa. What is the driglim of z?
