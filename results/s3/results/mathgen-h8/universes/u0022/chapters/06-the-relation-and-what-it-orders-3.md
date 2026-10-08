# Chapter 7. The relation and what it orders (3)

## Why this chapter

The results collected here were not found in this order. The ovimorn of a driwren, there
is at most one keldumb and no jenfex pairs exist came first, and the rest was assembled
around that once the pattern was visible.

Nothing here stands on its own. The arguments lean on chapters 3 and 5, and a reader who
has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about driwrens covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

## What is defined here

D8. The ovimorn of a driwren. The ovimorn of a driwren x, written [x], is the smallest
reldshen collection that contains x.

Worked out for each driwren: nakquil to nakquil; soltarn to soltarn; muxsib to muxsib;
braovi to braovi; yukzel to yukzel; thraisk to thraisk.

## The shape of it

The right picture for ovimorn is a spreading stain rather than a list. Drop one driwren
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 driwrens
depending on where it started.

Think of << as pointing downhill. The zelfex of a driwren is everything downhill of it,
and those shadows here have sizes 1, 2, 3, 4 and 6.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 driwrens the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T11 rests on D9 (a keldumb) and A8 (antisymmetry of the relation). Remove any one of
them and the statement stops making sense, not merely stops being provable.

T13 rests on D13 (jenfex pairs) and A8 (antisymmetry of the relation). The dependence is
on the content of those results, not only on their vocabulary.

## A worked case

Evaluate (soltarn * muxsib) * nakquil. Each line below is one lookup in a table.
    soltarn * muxsib = yukzel   (the table for *)
    yukzel * nakquil = yukzel   (the table for *)
The expression comes to yukzel.

Move the brackets and the work changes. Take muxsib * (nakquil * soltarn).
    nakquil * soltarn = soltarn   (the table for *)
    muxsib * soltarn = yukzel   (the table for *)
That gives yukzel, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test soltarn << nakquil. The zelfex of soltarn is nakquil and soltarn, and nakquil lies
inside it, so the relation holds.

A second case, this time a ovimorn. Start from yukzel. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is yukzel, so the
korrquil of yukzel is 1.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of antisymmetry of the relation and closure
under the first operation. Those are properties of this system, not of systems in
general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A8 (antisymmetry of the relation), D13 (jenfex
pairs), D3 (reldshen collections) and D9 (a keldumb).

What is built on it later: D11 (the korrquil of a driwren), T4 (the ovimorn of a driwren
is reldshen), T5 (the ovimorn is contained in every reldshen collection) and T8 (the
ovimorn of a iskkeld driwren stays in the iskkeld).

## Proofs

T11. No two distinct driwrens can both be keldumbs.

  (1) [D9] Let f and h both be floors.
  (2) [D9] Then f << h, since h is any object, and h << f likewise.
  (3) [A8] Antisymmetry forces f = h.

Checked over 36 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T13. No two distinct driwrens lie in each other's zelfex.

  (1) [D13] Suppose x and y form a tight pair.
  (2) [A8] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the ovimorn of a driwren. Each of these is used by
name later, so the names are worth learning rather than looking up.

Established here and safe to use: T11 and T13.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x020. Let z be muxsib * soltarn. List the ovimorn of z.
  x037. This result is about the keldumb. List every driwren in it.
