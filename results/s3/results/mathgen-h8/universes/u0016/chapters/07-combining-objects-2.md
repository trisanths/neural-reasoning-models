# Chapter 8. Combining objects (2)

## Why this chapter

What follows was pieced together backwards. The last item of it, every mornglim lies in
the falespa, every mornglim is iskzam and the vexbra lies in the falespa, was noticed
before anyone had a reason to expect it.

Prerequisites are real here: chapters 1, 4, 5 and 6 supply the notions the statements
below are phrased in.

The standard of proof here is exhaustion. A universal claim about mornglims covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

A useful mental split: some mornglims are inert under the operation and some are not.
oviazt, kapon, nyrrast and xilwren come back unchanged when combined with themselves,
and oviazt, kapon, nyrrast and xilwren commute with everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 mornglims the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T14 rests on D6 (the falespa). The dependence is on the content of those results, not
only on their vocabulary.

T15 rests on D7 (the xilka). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T2 rests on D5 (the vexbra) and D6 (the falespa). The dependence is on the content of
those results, not only on their vocabulary.

T3 rests on D6 (the falespa), D3 (tezdri collections) and A2 (association of the first
operation). The dependence is on the content of those results, not only on their
vocabulary.

T9 rests on D7 (the xilka) and D3 (tezdri collections). The dependence is on the content
of those results, not only on their vocabulary.

## A worked case

Here is (kapon | xilwren) | (nyrrast | oviazt), reduced without skipping anything.
    kapon | xilwren = xilwren   (the table for |)
    nyrrast | oviazt = nyrrast   (the table for |)
    xilwren | nyrrast = xilwren   (the table for |)
So (kapon | xilwren) | (nyrrast | oviazt) is xilwren.

A companion case, xilwren | (nyrrast | kapon), to show what the brackets are doing.
    nyrrast | kapon = xilwren   (the table for |)
    xilwren | xilwren = xilwren   (the table for |)
That gives xilwren, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test kapon <~ xilwren. The nakhurn of kapon is kapon and xilwren, and xilwren lies
inside it, so the relation holds.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of mornglims that come back
unchanged from themselves: oviazt, kapon, nyrrast and xilwren. Assuming more of them
than that is the mistake to avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation and closure under the first operation. Those are
properties of this system, not of systems in general.

That is not a rhetorical caution. Take the same 4 objects, the same symbols, and a
different table, and T15 stop holding. The notation survives the substitution and the
mathematics does not.

## Neighbouring results

The material this chapter borrows from: A2 (association of the first operation), D3
(tezdri collections), D5 (the vexbra) and D6 (the falespa).

These results are used again in T8 (the clobra of a falespa mornglim stays in the
falespa).

## Proofs

T14. Every pair of mornglims zelvexs.

  (1) [D6] The falespa is defined by zelvexing with everything.
  (2) [D2] The claim is that x | y = y | x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 16 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T15. x | x = x for every mornglim x.

  (1) [D1] Being iskzam is the condition x | x = x.
  (2) [D7] The claim is that the xilka is the whole system.
  (3) Only the diagonal of the table is involved.

Checked over 4 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T2. The vexbra zelvexs with every mornglim.

  (1) [D5] Let e be the vexbra and x any mornglim.
  (2) [D5] Then e | x = x and x | e = x.
  (3) [D2] So e | x = x | e, which is what it means to zelvex.
  (4) [D6] Since x was arbitrary, e belongs to the falespa.

Checked over 4 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. If x and y both zelvex with every mornglim, then so does x | y.

  (1) [D6] Let x and y lie in the falespa and let z be any mornglim.
  (2) [A2] Then (x | y) | z = x | (y | z).
  (3) [D6] Move z past y, then past x, using that each zelvexs with everything.
  (4) [D3] So x | y zelvexs with z, and the falespa is tezdri.

Checked over 16 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

T9. If x and y are both iskzam then so is x | y.

  (1) [D7] Let x and y be iskzam.
  (2) [D1] The claim asks whether (x | y) | (x | y) returns x | y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 16 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Established here and safe to use: T14, T15, T2, T3 and T9.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x028. This result is about the xilka. List every mornglim in it.
