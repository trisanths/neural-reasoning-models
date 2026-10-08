# Chapter 3. The relation and what it orders

## Why this chapter

The results collected here were not found in this order. Agreement of the relation with
the first operation, reflexivity of the relation and antisymmetry of the relation came
first, and the rest was assembled around that once the pattern was visible.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

One habit to adopt: when a statement below quantifies over mornglims, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A10. Agreement of the relation with the first operation. For all mornglims x, y, z: if x
<~ y then (z | x) <~ (z | y) and (x | z) <~ (y | z).

A7. Reflexivity of the relation. For every mornglim x: x <~ x.

A8. Antisymmetry of the relation. For all mornglims x and y: if x <~ y and y <~ x then x
= y.

A9. Transitivity of the relation. For all mornglims x, y, z: if x <~ y and y <~ z then x
<~ z.

D4. The nakhurn of a mornglim. The nakhurn of a mornglim x is the collection of
mornglims y for which x <~ y holds.

Worked out for each mornglim: oviazt to oviazt, kapon, nyrrast and xilwren; kapon to
kapon and xilwren; nyrrast to nyrrast and xilwren; xilwren to xilwren.

## The shape of it

The relation is easiest to see as a height. Each mornglim casts a nakhurn over what it
dominates, and the sizes of those shadows here are 1, 2 and 4. Sizes repeat, so the
objects do not line up in single file.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R3 rests on S2 (the Glimzam combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take (xilwren | oviazt) | kapon and work it out one step at a time.
    xilwren | oviazt = xilwren   (the table for |)
    xilwren | kapon = xilwren   (the table for |)
That leaves xilwren, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is oviazt | (kapon | xilwren) for contrast.
    kapon | xilwren = xilwren   (the table for |)
    oviazt | xilwren = xilwren   (the table for |)
That gives xilwren, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test oviazt <~ xilwren. The nakhurn of oviazt is oviazt, kapon, nyrrast and xilwren, and
xilwren lies inside it, so the relation holds.

## A case that breaks

R3. It is not the case that: For all mornglims x and y, at least one of x <~ y and y <~
x holds. It fails at x = kapon, y = nyrrast. One case is enough, and this is the
earliest one.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: S2 (the Glimzam combination tables).

What is built on it later: D9 (a duthvor), D13 (dripon pairs), T10 (nakhurns are nested
along the relation) and T11 (there is at most one duthvor).

## Proofs

R3. It is not the case that: For all mornglims x and y, at least one of x <~ y and y <~ x holds.

  (1) [S2] Take the case x = kapon, y = nyrrast, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 64 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the nakhurn of a mornglim. Later chapters state their results in these
terms and do not restate the definitions.

Explicitly not available: R3. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x013. Which mornglims y satisfy oviazt <~ y? Name them all.
  x014. List the nakhurn of kapon.
  x015. Which mornglims y satisfy nyrrast <~ y? Name them all.
Level 5.
  x009. The following fails in this system: For all mornglims x and y, at least one of x <~ y and y <~ x holds. Name the earliest mornglim, in the order the mornglims were introduced, that witnesses the failure.
