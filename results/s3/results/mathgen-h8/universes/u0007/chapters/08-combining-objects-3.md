# Chapter 9. Combining objects (3)

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through the muxmi of a thrafex, the
system has a ponjen and where every thrafex is solka breaks down.

Prerequisites are real here: chapters 1, 3, 5, 6 and 7 supply the notions the statements
below are phrased in.

One habit to adopt: when a statement below quantifies over thrafexs, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D8. The muxmi of a thrafex. The muxmi of a thrafex x, written [x], is the smallest
umbbra collection that contains x.

Worked out for each thrafex: tuespa to tuespa; qenmorn to tuespa, qenmorn and hobzel;
hobzel to tuespa, qenmorn and hobzel.

## The shape of it

The right picture for muxmi is a spreading stain rather than a list. Drop one thrafex
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 3
thrafexs depending on where it started.

The relation is easiest to see as a height. Each thrafex casts a vextarn over what it
supports, and the sizes of those shadows here are 3. Sizes repeat, so the objects do not
line up in single file.

A useful mental split: some thrafexs are inert under the operation and some are not.
tuespa come back unchanged when combined with themselves, and tuespa, qenmorn and hobzel
commute with everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 3 thrafexs the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T14 rests on D9 (a ponjen) and A14 (comparability of every pair). Remove any one of them
and the statement stops making sense, not merely stops being provable.

R6 rests on D7 (the tumux). Remove any one of them and the statement stops making sense,
not merely stops being provable.

T11 rests on D7 (the tumux) and D3 (umbbra collections). The dependence is on the
content of those results, not only on their vocabulary.

T16 rests on D6 (the aztrast). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T2 rests on D5 (the nyrrast) and D6 (the aztrast). The dependence is on the content of
those results, not only on their vocabulary.

T5 rests on D6 (the aztrast), D3 (umbbra collections) and A2 (association of the first
operation). Remove any one of them and the statement stops making sense, not merely
stops being provable.

## A worked case

Evaluate qenmorn =| hobzel ~ tuespa. Each line below is one lookup in a table.
    hobzel ~ tuespa = hobzel   (the table for ~)
    qenmorn =| hobzel = tuespa   (the table for =|)
The expression comes to tuespa.

Move the brackets and the work changes. Take hobzel =| (tuespa =| qenmorn).
    tuespa =| qenmorn = qenmorn   (the table for =|)
    hobzel =| qenmorn = tuespa   (the table for =|)
That gives tuespa, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
hobzel =< hobzel hold? Read off what hobzel stands over: tuespa, qenmorn and hobzel.
hobzel is among them, so it holds.

Now compute [tuespa]. Fold tuespa against itself, then fold whatever appeared against
everything present, and stop when a round adds nothing. The result is tuespa, of size 1.

## A case that breaks

R6. It is not the case that: x =| x = x for every thrafex x. It fails at x = qenmorn,
value = hobzel. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by a neutral object for the first operation, association of the
first operation, closure under the first operation and comparability of every pair. A
system without them is not a system where these results are harder to prove; it is a
system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A14 (comparability of every pair), A2 (association of the first
operation), D3 (umbbra collections) and D5 (the nyrrast).

These results are used again in D12 (the driglim of a thrafex), T6 (the muxmi of a
thrafex is umbbra), T7 (the muxmi is contained in every umbbra collection) and T10 (the
muxmi of a aztrast thrafex stays in the aztrast).

## Proofs

T14. Some thrafex ponjens the whole system.

  (1) [A14] Every pair is comparable, so the relation orders the objects into a line.
  (2) [D9] The claim is that the line has a bottom.
  (3) The carrier is finite, so the search over candidates terminates.

Checked over 9 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

R6. It is not the case that: x =| x = x for every thrafex x.

  (1) [S2] Take the case x = qenmorn, value = hobzel, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 3 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T11. If x and y are both solka then so is x =| y.

  (1) [D7] Let x and y be solka.
  (2) [D1] The claim asks whether (x =| y) =| (x =| y) returns x =| y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 9 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

T16. Every pair of thrafexs tutezs.

  (1) [D6] The aztrast is defined by tutezing with everything.
  (2) [D2] The claim is that x =| y = y =| x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 9 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T2. The nyrrast tutezs with every thrafex.

  (1) [D5] Let e be the nyrrast and x any thrafex.
  (2) [D5] Then e =| x = x and x =| e = x.
  (3) [D2] So e =| x = x =| e, which is what it means to tutez.
  (4) [D6] Since x was arbitrary, e belongs to the aztrast.

Checked over 3 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T5. If x and y both tutez with every thrafex, then so does x =| y.

  (1) [D6] Let x and y lie in the aztrast and let z be any thrafex.
  (2) [A2] Then (x =| y) =| z = x =| (y =| z).
  (3) [D6] Move z past y, then past x, using that each tutezs with everything.
  (4) [D3] So x =| y tutezs with z, and the aztrast is umbbra.

Checked over 9 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the muxmi of a thrafex. Later chapters state their results in these terms
and do not restate the definitions.

Established here and safe to use: T14, T11, T16, T2 and T5.

Do not carry forward R6. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x018. Name every thrafex in [qenmorn].
  x019. Name every thrafex in [hobzel].
Level 4.
  x020. Let z be qenmorn =| tuespa. List the muxmi of z.
  x021. Let z be qenmorn =| qenmorn. List the muxmi of z.
  x035. Name the thrafexs that make up the tumux, which is what the result above is a claim about.
