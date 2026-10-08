# Chapter 9. Collections that close on themselves (2)

## Why this chapter

The results collected here were not found in this order. The bratez, where the glimmorn
divides the number of grixmis breaks down and where some grixmi reaches every other
breaks down came first, and the rest was assembled around that once the pattern was
visible.

Nothing here stands on its own. The arguments lean on chapters 4, 7 and 8, and a reader
who has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 3
grixmis that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D12. The bratez. The bratez of the system is the collection of grixmis whose glimmorn is
largest.

Running the definition over every grixmi leaves muxlum.

## The shape of it

The right picture for shenyuk is a spreading stain rather than a list. Drop one grixmi
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
grixmis depending on where it started.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R5 rests on D11 (the glimmorn of a grixmi) and T4 (the shenyuk of a grixmi is vintmorn).
The dependence is on the content of those results, not only on their vocabulary.

R7 rests on D8 (the shenyuk of a grixmi) and D11 (the glimmorn of a grixmi). The
dependence is on the content of those results, not only on their vocabulary.

T5 rests on D8 (the shenyuk of a grixmi) and T4 (the shenyuk of a grixmi is vintmorn).
The dependence is on the content of those results, not only on their vocabulary.

T6 rests on D1 (rastpon grixmis), D11 (the glimmorn of a grixmi) and T4 (the shenyuk of
a grixmi is vintmorn). The dependence is on the content of those results, not only on
their vocabulary.

## A worked case

Here is (vexyuk # vexyuk) # tezreld, reduced without skipping anything.
    vexyuk # vexyuk = vexyuk   (the table for #)
    vexyuk # tezreld = tezreld   (the table for #)
So (vexyuk # vexyuk) # tezreld is tezreld.

A companion case, vexyuk # (tezreld # vexyuk), to show what the brackets are doing.
    tezreld # vexyuk = tezreld   (the table for #)
    vexyuk # tezreld = tezreld   (the table for #)
The value is tezreld. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test tezreld |> vexyuk. The umbhob of tezreld is tezreld, and vexyuk lies outside it, so
the relation fails.

## A case that breaks

R5. It is not the case that: For every grixmi x, the glimmorn of x divides 3. It fails
at x = muxlum, reach = 2, size = 3. One case is enough, and this is the earliest one.

R7. It is not the case that: There is a grixmi whose shenyuk is the whole system. It
fails at largest_span = 2, size = 3. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside D1 (rastpon grixmis), D11 (the glimmorn of a grixmi), D8 (the shenyuk of
a grixmi) and T4 (the shenyuk of a grixmi is vintmorn).

## Proofs

R5. It is not the case that: For every grixmi x, the glimmorn of x divides 3.

  (1) [S2] Take the case x = muxlum, reach = 2, size = 3, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 3 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

R7. It is not the case that: There is a grixmi whose shenyuk is the whole system.

  (1) [S2] Take the case largest_span = 2, size = 3, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 3 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T5. If S is vintmorn and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 15 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T6. x # x = x holds if and only if [x] contains x alone.

  (1) [D1] If x # x = x then {x} is already closed under #.
  (2) [T4] So [x] = {x} and the glimmorn is one.
  (3) [D11] Conversely a span of one object must contain x # x, which is then x.

Checked over 3 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the bratez. Later chapters state their results in these terms and do not
restate the definitions.

The results now available are T5 and T6, each settled by exhaustive check rather than by
argument from analogy.

Do not carry forward R5 and R7. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x024. Which grixmis make up the bratez? Name them all.
Level 5.
  x026. The following fails in this system: For every grixmi x, the glimmorn of x divides 3. Name the earliest grixmi, in the order the grixmis were introduced, that witnesses the failure.
