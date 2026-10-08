# Chapter 1. The objects and their notation

## Why this chapter

Anyone using this system to keep track of something will meet the Hobnak signature, the
Hobnak combination tables and closure under the first operation early, whether or not
they go looking.

One habit to adopt: when a statement below quantifies over rastvashs, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## The tables in full

The table for ?. Read the left argument down the side and the right argument across the top.

         |   lumpyr   lumnyr  opalbra  rastumb  fexrast
-------------------------------------------------------
  lumpyr |   lumpyr   lumpyr   lumpyr   lumpyr   lumpyr
  lumnyr |   lumnyr   lumpyr   lumpyr   lumpyr   lumpyr
 opalbra |  opalbra   lumnyr   lumpyr   lumpyr   lumpyr
 rastumb |  rastumb  opalbra   lumnyr   lumpyr   lumpyr
 fexrast |  fexrast  rastumb  opalbra   lumnyr   lumpyr

Every pair standing in the >> relation, grouped by left argument.

  lumpyr >> lumpyr
  lumnyr >> lumnyr
  opalbra >> opalbra
  rastumb >> rastumb
  fexrast >> fexrast

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A1. Closure under the first operation. For all rastvashs x and y, x ? y is again a
rastvash.

## The shape of it

A useful mental split: some rastvashs are inert under the operation and some are not.
lumpyr come back unchanged when combined with themselves, and none commutes with
everything.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R1 rests on S2 (the Hobnak combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R2 rests on S2 (the Hobnak combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

R5 rests on S2 (the Hobnak combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R6 rests on S2 (the Hobnak combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

## A worked case

Evaluate (lumpyr ? rastumb) ? fexrast. Each line below is one lookup in a table.
    lumpyr ? rastumb = lumpyr   (the table for ?)
    lumpyr ? fexrast = lumpyr   (the table for ?)
So (lumpyr ? rastumb) ? fexrast is lumpyr.

Move the brackets and the work changes. Take rastumb ? (fexrast ? lumpyr).
    fexrast ? lumpyr = fexrast   (the table for ?)
    rastumb ? fexrast = lumpyr   (the table for ?)
The value is lumpyr. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
lumpyr >> lumnyr hold? Read off what lumpyr stands over: lumpyr. lumnyr is not among
them, so it fails.

## A case that breaks

R1. It is not the case that: For all rastvashs x, y, z: (x ? y) ? z = x ? (y ? z). It
fails at x = lumnyr, y = lumpyr, z = lumnyr, left = lumpyr, right = lumnyr. One case is
enough, and this is the earliest one.

R2. It is not the case that: For all rastvashs x and y: x ? y = y ? x. It fails at x =
lumpyr, y = lumnyr, left = lumpyr, right = lumnyr. One case is enough, and this is the
earliest one.

R5. It is not the case that: For every rastvash x: x ? x = x. It fails at x = lumnyr,
value = lumpyr. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

What is built on it later: A2 (reflexivity of the relation), A3 (antisymmetry of the
relation), A4 (transitivity of the relation) and A5 (agreement of the relation with the
first operation).

## Proofs

R1. It is not the case that: For all rastvashs x, y, z: (x ? y) ? z = x ? (y ? z).

  (1) [S2] Take the case x = lumnyr, y = lumpyr, z = lumnyr, left = lumpyr, right = lumnyr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R2. It is not the case that: For all rastvashs x and y: x ? y = y ? x.

  (1) [S2] Take the case x = lumpyr, y = lumnyr, left = lumpyr, right = lumnyr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R5. It is not the case that: For every rastvash x: x ? x = x.

  (1) [S2] Take the case x = lumnyr, value = lumpyr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R6. It is not the case that: For all rastvashs x, y, z: if x ? y = x ? z then y = z.

  (1) [S2] Take the case x = lumpyr, y = lumpyr, z = lumnyr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R1, R2, R5 and R6. These were tested and failed, and the failing
cases are recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 1.
  x001. Reduce lumnyr ? lumnyr to a single rastvash.
  x002. Work out the value of rastumb ? rastumb.
  x003. Reduce opalbra ? opalbra to a single rastvash.
  x004. Work out the value of rastumb ? opalbra.
  x005. What rastvash does fexrast ? fexrast name?
  x006. Reduce lumnyr ? opalbra to a single rastvash.
Level 2.
  x007. Reduce (opalbra ? rastumb) ? fexrast to a single rastvash.
  x008. Reduce (rastumb ? rastumb) ? opalbra to a single rastvash.
  x009. Reduce (opalbra ? opalbra) ? rastumb to a single rastvash.
  x010. Reduce (lumnyr ? fexrast) ? lumnyr to a single rastvash.
  x011. Work out the value of (rastumb ? rastumb) ? lumnyr.
  x013. What is lumnyr combined with itself 3 times under ??
  x014. What is opalbra combined with itself 3 times under ??
  x015. Solve x ? fexrast = lumpyr for x, naming every solution.
  x016. Which rastvashs x satisfy x ? rastumb = lumnyr? List them all.
Level 3.
  x012. What rastvash does (rastumb ? rastumb) ? (opalbra ? fexrast) name?
Level 5.
  x017. The following fails in this system: For all rastvashs x, y, z: (x ? y) ? z = x ? (y ? z). Name the earliest rastvash, in the order the rastvashs were introduced, that witnesses the failure.
  x018. The following fails in this system: For all rastvashs x and y: x ? y = y ? x. Name the earliest rastvash, in the order the rastvashs were introduced, that witnesses the failure.
  x020. The following fails in this system: For all rastvashs x, y, z: if x ? y = x ? z then y = z. Name the earliest rastvash, in the order the rastvashs were introduced, that witnesses the failure.
