# Chapter 5. The relation and what it orders (2)

## Why this chapter

We turn to jenfex pairs, reldshen collections and a keldumb. The treatment is self
contained given the material already established.

Nothing here stands on its own. The arguments lean on chapters 1 and 3, and a reader who
has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about driwrens covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D13. Jenfex pairs. Two distinct driwrens x and y form a jenfex pair when x << y and y <<
x both hold, that is, when each lies in the zelfex of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D3. Reldshen collections. A collection S of driwrens is reldshen when x * y belongs to S
for every pair x, y drawn from S.

D9. A keldumb. A driwren f is a keldumb when f << y holds for every driwren y, that is,
when the zelfex of f is the whole system.

Running the definition over every driwren leaves thraisk.

## The shape of it

The right picture for ovimorn is a spreading stain rather than a list. Drop one driwren
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 driwrens
depending on where it started.

The relation is easiest to see as a height. Each driwren casts a zelfex over what it
precedes, and the sizes of those shadows here are 1, 2, 3, 4 and 6. Sizes repeat, so the
objects do not line up in single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 driwrens the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R5 rests on D4 (the zelfex of a driwren). Remove any one of them and the statement stops
making sense, not merely stops being provable.

T10 rests on D4 (the zelfex of a driwren) and A9 (transitivity of the relation). The
dependence is on the content of those results, not only on their vocabulary.

T12 rests on D4 (the zelfex of a driwren) and A10 (agreement of the relation with the
first operation). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Evaluate (nakquil * thraisk) * muxsib. Each line below is one lookup in a table.
    nakquil * thraisk = thraisk   (the table for *)
    thraisk * muxsib = thraisk   (the table for *)
So (nakquil * thraisk) * muxsib is thraisk.

Bracketing is not cosmetic, so here is thraisk * (muxsib * nakquil) for contrast.
    muxsib * nakquil = muxsib   (the table for *)
    thraisk * muxsib = thraisk   (the table for *)
That gives thraisk, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test muxsib << nakquil. The zelfex of muxsib is nakquil and muxsib, and nakquil lies
inside it, so the relation holds.

## A case that breaks

R5. It is not the case that: If x << y then y << x. It fails at x = soltarn, y =
nakquil. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by agreement of the relation with the first operation, closure under
the first operation and transitivity of the relation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

That is not a rhetorical caution. Take the same 6 objects, the same symbols, and a
different table, and T12 stop holding. The notation survives the substitution and the
mathematics does not.

## Neighbouring results

Read alongside A1 (closure under the first operation), A10 (agreement of the relation
with the first operation), A9 (transitivity of the relation) and D4 (the zelfex of a
driwren).

These results are used again in D8 (the ovimorn of a driwren), T3 (the iskkeld is
reldshen), T4 (the ovimorn of a driwren is reldshen) and T9 (the kami is reldshen).

## Proofs

R5. It is not the case that: If x << y then y << x.

  (1) [S2] Take the case x = soltarn, y = nakquil, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T10. If y lies in the zelfex of x, then the zelfex of y is contained in the zelfex of x.

  (1) [D4] Let y satisfy x << y and let z satisfy y << z.
  (2) [A9] Transitivity gives x << z.
  (3) [D4] So every member of the zelfex of y is a member of that of x.

Checked over 216 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T12. If x << y then (x * z) << (y * z) for every driwren z.

  (1) [D4] Let y lie in the zelfex of x.
  (2) [A10] Compatibility applies the operation to both sides at once.
  (3) Nothing else is needed, since z was arbitrary.

Checked over 216 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: jenfex pairs, reldshen collections and a keldumb. Each
of these is used by name later, so the names are worth learning rather than looking up.

Established here and safe to use: T10 and T12.

Explicitly not available: R5. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x010. How many driwrens lie in the smallest reldshen collection containing soltarn?
  x011. How many driwrens lie in the smallest reldshen collection containing muxsib?
Level 4.
  x021. Write down the keldumb in full.
  x035. The result above concerns zelfexs. List the zelfex of soltarn.
  x036. The result above concerns zelfexs. List the zelfex of muxsib.
Level 5.
  x038. The following fails in this system: If x << y then y << x. Name the earliest driwren, in the order the driwrens were introduced, that witnesses the failure.
