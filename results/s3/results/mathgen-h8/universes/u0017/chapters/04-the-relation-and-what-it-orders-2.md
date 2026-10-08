# Chapter 5. The relation and what it orders (2)

## Why this chapter

The present chapter develops iskmorn pairs, tarnquil collections and a pyrlorn.

Nothing here stands on its own. The arguments lean on chapters 1 and 3, and a reader who
has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over duthpons, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D13. Iskmorn pairs. Two distinct duthpons x and y form a iskmorn pair when x >> y and y
>> x both hold, that is, when each lies in the wrensib of the other.

Running the definition over every duthpon leaves rastrast, espanyr, vorwren and
vashtarn.

D3. Tarnquil collections. A collection S of duthpons is tarnquil when x - y belongs to S
for every pair x, y drawn from S.

D9. A pyrlorn. A duthpon f is a pyrlorn when f >> y holds for every duthpon y, that is,
when the wrensib of f is the whole system.

Running the definition over every duthpon leaves rastrast and vashtarn.

## The shape of it

The right picture for wrenvash is a spreading stain rather than a list. Drop one duthpon
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
duthpons depending on where it started.

Think of >> as pointing downhill. The wrensib of a duthpon is everything downhill of it,
and those shadows here have sizes 1, 2, 3 and 6.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 duthpons the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R8 rests on D4 (the wrensib of a duthpon). Remove any one of them and the statement
stops making sense, not merely stops being provable.

T10 rests on D4 (the wrensib of a duthpon) and A7 (transitivity of the relation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

T11 rests on D4 (the wrensib of a duthpon) and A8 (agreement of the relation with the
first operation). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Evaluate (rastrast - espanyr) - nakvint. Each line below is one lookup in a table.
    rastrast - espanyr = espanyr   (the table for -)
    espanyr - nakvint = nakvint   (the table for -)
That leaves nakvint, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take espanyr - (nakvint - rastrast).
    nakvint - rastrast = nakvint   (the table for -)
    espanyr - nakvint = nakvint   (the table for -)
That gives nakvint, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
rastrast >> vashtarn hold? Read off what rastrast stands over: nakvint, rastrast,
espanyr, yuksol, vorwren and vashtarn. vashtarn is among them, so it holds.

## A case that breaks

R8. It is not the case that: If x >> y then y >> x. It fails at x = rastrast, y =
nakvint. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of agreement of the relation with the first
operation, closure under the first operation and transitivity of the relation. Those are
properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A1 (closure under the first operation), A7
(transitivity of the relation), A8 (agreement of the relation with the first operation)
and D4 (the wrensib of a duthpon).

What is built on it later: D8 (the wrenvash of a duthpon), T3 (the iskvex is tarnquil),
T4 (the wrenvash of a duthpon is tarnquil) and T9 (the iskmux is tarnquil).

## Proofs

R8. It is not the case that: If x >> y then y >> x.

  (1) [S2] Take the case x = rastrast, y = nakvint, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T10. If y lies in the wrensib of x, then the wrensib of y is contained in the wrensib of x.

  (1) [D4] Let y satisfy x >> y and let z satisfy y >> z.
  (2) [A7] Transitivity gives x >> z.
  (3) [D4] So every member of the wrensib of y is a member of that of x.

Checked over 216 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T11. If x >> y then (x - z) >> (y - z) for every duthpon z.

  (1) [D4] Let y lie in the wrensib of x.
  (2) [A8] Compatibility applies the operation to both sides at once.
  (3) Nothing else is needed, since z was arbitrary.

Checked over 216 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: iskmorn pairs, tarnquil collections and a pyrlorn.
Each of these is used by name later, so the names are worth learning rather than looking
up.

The results now available are T10 and T11, each settled by exhaustive check rather than
by argument from analogy.

Do not carry forward R8. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x016. How many duthpons lie in the smallest tarnquil collection containing rastrast?
  x017. How many duthpons lie in the smallest tarnquil collection containing espanyr?
Level 4.
  x029. Which duthpons make up the pyrlorn? Name them all.
  x040. Which duthpons make up the iskmorn? Name them all.
  x045. The result above concerns wrensibs. List the wrensib of rastrast.
  x046. The result above concerns wrensibs. List the wrensib of espanyr.
Level 5.
  x048. The following fails in this system: If x >> y then y >> x. Name the earliest duthpon, in the order the duthpons were introduced, that witnesses the failure.
