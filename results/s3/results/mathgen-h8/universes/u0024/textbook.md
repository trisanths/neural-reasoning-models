# The Hobnak system

What follows is a complete account of the Hobnak system. It is complete in a strong
sense: the system has 5 rastvashs and finitely many facts, and every one of those facts
is settled here by inspection rather than left to argument.

The rastvashs are written lumpyr, lumnyr, opalbra, rastumb and fexrast. The first
operation is written ?. The relation is written >>; where it holds between two rastvashs
we say the left one supports the right one. Both operations associate to the left when
written without brackets, and brackets override that. Repeated combination is
abbreviated: x^3 means x ? x ? x.

A warning that will be repeated because it is the one readers ignore: nothing here is
inherited from arithmetic. Familiar names have been avoided on purpose. Where a law of
arithmetic happens to hold it is stated and checked, and where it fails a counterexample
is given.

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

# Chapter 2. Neutral objects and reversal

## Why this chapter

So far the rastvashs have been objects to be pushed around. This chapter starts asking
what they are like. We take up the system does not have a neutral object for the first
operation, the system does not have reversal under the first operation and the system
does not have an absorbing object for the first operation.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
rastvashs that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

Neutrality is a strong condition disguised as a weak one. It fixes a single rastvash
and, through that, constrains everything that can combine with it.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 rastvashs the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R3 rests on S2 (the Hobnak combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

R4 rests on S2 (the Hobnak combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R7 rests on S2 (the Hobnak combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Here is (lumpyr ? rastumb) ? (lumnyr ? opalbra), reduced without skipping anything.
    lumpyr ? rastumb = lumpyr   (the table for ?)
    lumnyr ? opalbra = lumpyr   (the table for ?)
    lumpyr ? lumpyr = lumpyr   (the table for ?)
So (lumpyr ? rastumb) ? (lumnyr ? opalbra) is lumpyr.

Move the brackets and the work changes. Take rastumb ? (lumnyr ? lumpyr).
    lumnyr ? lumpyr = lumnyr   (the table for ?)
    rastumb ? lumnyr = opalbra   (the table for ?)
The value is opalbra, not lumpyr.

One decision about the relation, since deciding is as much a skill as computing. Does
lumpyr >> rastumb hold? Read off what lumpyr stands over: lumpyr. rastumb is not among
them, so it fails.

## A case that breaks

R3. There is no rastvash e with e ? x = x ? e = x for every rastvash x. The case that
settles it: reason = no two sided identity exists. Anyone carrying this claim over from
a more familiar system will be wrong here, and wrong in a way that propagates.

R4. Some rastvash x admits no rastvash y for which x ? y and y ? x both land on a
neutral object. It fails at reason = no identity, so inverses are not defined. One case
is enough, and this is the earliest one.

R7. There is no rastvash z with z ? x = x ? z = z for every rastvash x. It fails at
reason = no absorbing element. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside S2 (the Hobnak combination tables).

## Proofs

R3. There is no rastvash e with e ? x = x ? e = x for every rastvash x.

  (1) [S2] Take the case reason = no two sided identity exists, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R4. Some rastvash x admits no rastvash y for which x ? y and y ? x both land on a neutral object.

  (1) [S2] Take the case reason = no identity, so inverses are not defined, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R7. There is no rastvash z with z ? x = x ? z = z for every rastvash x.

  (1) [S2] Take the case reason = no absorbing element, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R3, R4 and R7. These were tested and failed, and the failing cases
are recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 5.
  x019. The following fails in this system: Some rastvash x admits no rastvash y for which x ? y and y ? x both land on a neutral object. Name the earliest rastvash, in the order the rastvashs were introduced, that witnesses the failure.

# Chapter 3. The relation and what it orders

## Why this chapter

We turn to reflexivity of the relation, antisymmetry of the relation and transitivity of
the relation. The treatment is self contained given the material already established.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about rastvashs covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A2. Reflexivity of the relation. For every rastvash x: x >> x.

A3. Antisymmetry of the relation. For all rastvashs x and y: if x >> y and y >> x then x
= y.

A4. Transitivity of the relation. For all rastvashs x, y, z: if x >> y and y >> z then x
>> z.

A5. Agreement of the relation with the first operation. For all rastvashs x, y, z: if x
>> y then (z ? x) >> (z ? y) and (x ? z) >> (y ? z).

D4. The iskespa of a rastvash. The iskespa of a rastvash x is the collection of
rastvashs y for which x >> y holds.

Worked out for each rastvash: lumpyr to lumpyr; lumnyr to lumnyr; opalbra to opalbra;
rastumb to rastumb; fexrast to fexrast.

## The shape of it

Think of >> as pointing downhill. The iskespa of a rastvash is everything downhill of
it, and those shadows here have sizes 1.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R8 rests on S2 (the Hobnak combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Take (rastumb ? opalbra) ? lumnyr and work it out one step at a time.
    rastumb ? opalbra = lumnyr   (the table for ?)
    lumnyr ? lumnyr = lumpyr   (the table for ?)
That leaves lumpyr, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is opalbra ? (lumnyr ? rastumb) for contrast.
    lumnyr ? rastumb = lumpyr   (the table for ?)
    opalbra ? lumpyr = opalbra   (the table for ?)
That gives opalbra, against lumpyr above.

Test fexrast >> lumpyr. The iskespa of fexrast is fexrast, and lumpyr lies outside it,
so the relation fails.

## A case that breaks

R8. It is not the case that: For all rastvashs x and y, at least one of x >> y and y >>
x holds. The case that settles it: x = lumpyr, y = lumnyr. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside S2 (the Hobnak combination tables).

These results are used again in D8 (a kelddri), D11 (umbnyr pairs), T5 (iskespas are
nested along the relation) and T6 (there is at most one kelddri).

## Proofs

R8. It is not the case that: For all rastvashs x and y, at least one of x >> y and y >> x holds.

  (1) [S2] Take the case x = lumpyr, y = lumnyr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the iskespa of a rastvash. Later chapters state their results in these
terms and do not restate the definitions.

Do not carry forward R8. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 5.
  x021. The following fails in this system: For all rastvashs x and y, at least one of x >> y and y >> x holds. Name the earliest rastvash, in the order the rastvashs were introduced, that witnesses the failure.

# Chapter 4. Combining objects

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is pyrglim rastvashs,
rastvashs that vintzam and umbclo collections.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
rastvashs that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D1. Pyrglim rastvashs. A rastvash x is called pyrglim when x ? x = x.

Running the definition over every rastvash leaves lumpyr.

D2. Rastvashs that vintzam. Two rastvashs x and y are said to vintzam when x ? y = y ?
x.

D3. Umbclo collections. A collection S of rastvashs is umbclo when x ? y belongs to S
for every pair x, y drawn from S.

## The shape of it

The right picture for tarntarn is a spreading stain rather than a list. Drop one
rastvash in, apply the operation to whatever is wet, repeat. The stain here reaches 1
and 2 rastvashs depending on where it started.

Two questions sort the rastvashs quickly. Does combining a rastvash with itself change
it? For lumpyr it does not. Does it matter which side it goes on? It always does.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 rastvashs the table is short enough to consult every time.

## Where these results come from

Nothing is derived in this chapter. It lays down material that later chapters draw on.

## A worked case

Evaluate (fexrast ? opalbra) ? (rastumb ? lumpyr). Each line below is one lookup in a
table.
    fexrast ? opalbra = opalbra   (the table for ?)
    rastumb ? lumpyr = rastumb   (the table for ?)
    opalbra ? rastumb = lumpyr   (the table for ?)
The expression comes to lumpyr.

Bracketing is not cosmetic, so here is opalbra ? (rastumb ? fexrast) for contrast.
    rastumb ? fexrast = lumpyr   (the table for ?)
    opalbra ? lumpyr = opalbra   (the table for ?)
The value is opalbra, not lumpyr.

One decision about the relation, since deciding is as much a skill as computing. Does
opalbra >> rastumb hold? Read off what opalbra stands over: opalbra. rastumb is not
among them, so it fails.

## A case that breaks

A quick guard against a common slip: lumnyr ? opalbra is lumpyr while opalbra ? lumnyr
is lumnyr. Order is not decoration in this system.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A1 (closure under the first operation).

What is built on it later: D5 (the iskvor), D6 (the zamxil), D7 (the tarntarn of a
rastvash) and T1 (the tarntarn of a rastvash is umbclo).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

New vocabulary from this chapter: pyrglim rastvashs, rastvashs that vintzam and umbclo
collections. Each of these is used by name later, so the names are worth learning rather
than looking up.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x022. List every rastvash in the pyrglim.
  x023. How many rastvashs lie in the smallest umbclo collection containing lumnyr?
  x024. How many rastvashs lie in the smallest umbclo collection containing opalbra?

# Chapter 5. The relation and what it orders (2)

## Why this chapter

The results collected here were not found in this order. Umbnyr pairs, a kelddri and
iskespas are nested along the relation came first, and the rest was assembled around
that once the pattern was visible.

Prerequisites are real here: chapter 3 supply the notions the statements below are
phrased in.

One habit to adopt: when a statement below quantifies over rastvashs, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D11. Umbnyr pairs. Two distinct rastvashs x and y form a umbnyr pair when x >> y and y
>> x both hold, that is, when each lies in the iskespa of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D8. A kelddri. A rastvash f is a kelddri when f >> y holds for every rastvash y, that
is, when the iskespa of f is the whole system.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

## The shape of it

The relation is easiest to see as a height. Each rastvash casts a iskespa over what it
supports, and the sizes of those shadows here are 1. Sizes repeat, so the objects do not
line up in single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 rastvashs the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T5 rests on D4 (the iskespa of a rastvash) and A4 (transitivity of the relation). The
dependence is on the content of those results, not only on their vocabulary.

T7 rests on D4 (the iskespa of a rastvash) and A5 (agreement of the relation with the
first operation). The dependence is on the content of those results, not only on their
vocabulary.

T9 rests on D4 (the iskespa of a rastvash). The dependence is on the content of those
results, not only on their vocabulary.

## A worked case

Take (fexrast ? rastumb) ? lumnyr and work it out one step at a time.
    fexrast ? rastumb = lumnyr   (the table for ?)
    lumnyr ? lumnyr = lumpyr   (the table for ?)
The expression comes to lumpyr.

A companion case, rastumb ? (lumnyr ? fexrast), to show what the brackets are doing.
    lumnyr ? fexrast = lumpyr   (the table for ?)
    rastumb ? lumpyr = rastumb   (the table for ?)
The value is rastumb, not lumpyr.

Test fexrast >> rastumb. The iskespa of fexrast is fexrast, and rastumb lies outside it,
so the relation fails.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of rastvashs that come back
unchanged from themselves: lumpyr. Assuming more of them than that is the mistake to
avoid.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by agreement of the relation with the first operation and
transitivity of the relation. A system without them is not a system where these results
are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A4 (transitivity of the relation), A5 (agreement
of the relation with the first operation) and D4 (the iskespa of a rastvash).

These results are used again in T6 (there is at most one kelddri) and T8 (no umbnyr
pairs exist).

## Proofs

T5. If y lies in the iskespa of x, then the iskespa of y is contained in the iskespa of x.

  (1) [D4] Let y satisfy x >> y and let z satisfy y >> z.
  (2) [A4] Transitivity gives x >> z.
  (3) [D4] So every member of the iskespa of y is a member of that of x.

Checked over 125 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T7. If x >> y then (x ? z) >> (y ? z) for every rastvash z.

  (1) [D4] Let y lie in the iskespa of x.
  (2) [A5] Compatibility applies the operation to both sides at once.
  (3) Nothing else is needed, since z was arbitrary.

Checked over 125 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T9. If x >> y then y >> x.

  (1) [D4] Symmetry would mean y lies in the iskespa of x exactly when x lies in that of y.
  (2) The listed pairs settle it directly.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward umbnyr pairs and a kelddri. Later chapters state their results in these
terms and do not restate the definitions.

Established here and safe to use: T5, T7 and T9.

## Exercises

No exercises here. Every question this chapter suggested turned out to be answerable
from the question itself, so all of them were discarded.

# Chapter 6. Combining objects (2)

## Why this chapter

Anyone using this system to keep track of something will meet the iskvor, the zamxil and
the tarntarn of a rastvash early, whether or not they go looking.

Nothing here stands on its own. The arguments lean on chapter 4, and a reader who has
skipped it will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about rastvashs covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

## What is defined here

D5. The iskvor. The iskvor of the system is the collection of rastvashs that vintzam
with every rastvash.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D6. The zamxil. The zamxil is the collection of all pyrglim rastvashs.

Running the definition over every rastvash leaves lumpyr.

D7. The tarntarn of a rastvash. The tarntarn of a rastvash x, written [x], is the
smallest umbclo collection that contains x.

Worked out for each rastvash: lumpyr to lumpyr; lumnyr to lumpyr and lumnyr; opalbra to
lumpyr and opalbra; rastumb to lumpyr and rastumb; fexrast to lumpyr and fexrast.

## The shape of it

Picture the tarntarn as what happens when you start with one rastvash and keep folding
it against itself and against whatever appears, until nothing new appears. Because there
are only 5 rastvashs, that stops. In this system the sizes it stops at are 1 and 2.

Two questions sort the rastvashs quickly. Does combining a rastvash with itself change
it? For lumpyr it does not. Does it matter which side it goes on? It always does.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Nothing is derived in this chapter. It lays down material that later chapters draw on.

## A worked case

Take (fexrast ? rastumb) ? (lumpyr ? lumnyr) and work it out one step at a time.
    fexrast ? rastumb = lumnyr   (the table for ?)
    lumpyr ? lumnyr = lumpyr   (the table for ?)
    lumnyr ? lumpyr = lumnyr   (the table for ?)
So (fexrast ? rastumb) ? (lumpyr ? lumnyr) is lumnyr.

Move the brackets and the work changes. Take rastumb ? (lumpyr ? fexrast).
    lumpyr ? fexrast = lumpyr   (the table for ?)
    rastumb ? lumpyr = rastumb   (the table for ?)
That gives rastumb, against lumnyr above.

One decision about the relation, since deciding is as much a skill as computing. Does
fexrast >> rastumb hold? Read off what fexrast stands over: fexrast. rastumb is not
among them, so it fails.

A second case, this time a tarntarn. Start from opalbra. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is lumpyr and opalbra,
so the vexnyr of opalbra is 2.

## A case that breaks

A quick guard against a common slip: opalbra ? rastumb is lumpyr while rastumb ? opalbra
is lumnyr. Order is not decoration in this system.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: D1 (pyrglim rastvashs), D2 (rastvashs that
vintzam) and D3 (umbclo collections).

What is built on it later: D9 (the vexnyr of a rastvash), T1 (the tarntarn of a rastvash
is umbclo), T2 (the tarntarn is contained in every umbclo collection) and T4 (the zamxil
is umbclo).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

New vocabulary from this chapter: the iskvor, the zamxil and the tarntarn of a rastvash.
Each of these is used by name later, so the names are worth learning rather than looking
up.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x025. Write down the zamxil in full.
  x026. Name every rastvash in [lumnyr].
  x027. Name every rastvash in [opalbra].
  x028. List the tarntarn of rastumb.
  x029. List the tarntarn of fexrast.
Level 4.
  x030. Let z be rastumb ? rastumb. List the tarntarn of z.

# Chapter 7. Combining objects (3)

## Why this chapter

So far the rastvashs have been objects to be pushed around. This chapter starts asking
what they are like. We take up there is at most one kelddri, no umbnyr pairs exist and
where every rastvash lies in the iskvor breaks down.

Nothing here stands on its own. The arguments lean on chapters 3, 4, 5 and 6, and a
reader who has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about rastvashs covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

Think of >> as pointing downhill. The iskespa of a rastvash is everything downhill of
it, and those shadows here have sizes 1.

Two questions sort the rastvashs quickly. Does combining a rastvash with itself change
it? For lumpyr it does not. Does it matter which side it goes on? It always does.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T6 rests on D8 (a kelddri) and A3 (antisymmetry of the relation). Remove any one of them
and the statement stops making sense, not merely stops being provable.

T8 rests on D11 (umbnyr pairs) and A3 (antisymmetry of the relation). Remove any one of
them and the statement stops making sense, not merely stops being provable.

R10 rests on D5 (the iskvor). Remove any one of them and the statement stops making
sense, not merely stops being provable.

R11 rests on D6 (the zamxil). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T4 rests on D6 (the zamxil) and D3 (umbclo collections). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Here is (fexrast ? rastumb) ? lumpyr, reduced without skipping anything.
    fexrast ? rastumb = lumnyr   (the table for ?)
    lumnyr ? lumpyr = lumnyr   (the table for ?)
That leaves lumnyr, and no other reading of the notation gives anything else.

A companion case, rastumb ? (lumpyr ? fexrast), to show what the brackets are doing.
    lumpyr ? fexrast = lumpyr   (the table for ?)
    rastumb ? lumpyr = rastumb   (the table for ?)
That gives rastumb, against lumnyr above.

One decision about the relation, since deciding is as much a skill as computing. Does
lumpyr >> fexrast hold? Read off what lumpyr stands over: lumpyr. fexrast is not among
them, so it fails.

## A case that breaks

R10. It is not the case that: Every pair of rastvashs vintzams. It fails at x = lumpyr,
y = lumnyr, left = lumpyr, right = lumnyr. One case is enough, and this is the earliest
one.

R11. It is not the case that: x ? x = x for every rastvash x. The case that settles it:
x = lumnyr, value = lumpyr. Anyone carrying this claim over from a more familiar system
will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by antisymmetry of the relation and closure under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

That is not a rhetorical caution. Take the same 5 objects, the same symbols, and a
different table, and T6 and T8 stop holding. The notation survives the substitution and
the mathematics does not.

## Neighbouring results

Read alongside A3 (antisymmetry of the relation), D11 (umbnyr pairs), D3 (umbclo
collections) and D5 (the iskvor).

## Proofs

T6. No two distinct rastvashs can both be kelddris.

  (1) [D8] Let f and h both be floors.
  (2) [D8] Then f >> h, since h is any object, and h >> f likewise.
  (3) [A3] Antisymmetry forces f = h.

Checked over 25 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T8. No two distinct rastvashs lie in each other's iskespa.

  (1) [D11] Suppose x and y form a tight pair.
  (2) [A3] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

R10. It is not the case that: Every pair of rastvashs vintzams.

  (1) [S2] Take the case x = lumpyr, y = lumnyr, left = lumpyr, right = lumnyr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

R11. It is not the case that: x ? x = x for every rastvash x.

  (1) [S2] Take the case x = lumnyr, value = lumpyr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T4. If x and y are both pyrglim then so is x ? y.

  (1) [D6] Let x and y be pyrglim.
  (2) [D1] The claim asks whether (x ? y) ? (x ? y) returns x ? y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 25 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Established here and safe to use: T6, T8 and T4.

Do not carry forward R10 and R11. These were tested and failed, and the failing cases
are recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x040. This result is about the zamxil. List every rastvash in it.
Level 5.
  x041. The following fails in this system: Every pair of rastvashs vintzams. Name the earliest rastvash, in the order the rastvashs were introduced, that witnesses the failure.

# Chapter 8. Collections that close on themselves

## Why this chapter

We turn to the vexnyr of a rastvash, the tarntarn of a rastvash is umbclo and the
lumovi. The treatment is self contained given the material already established.

Nothing here stands on its own. The arguments lean on chapters 4 and 6, and a reader who
has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about rastvashs covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D9. The vexnyr of a rastvash. The vexnyr of a rastvash x is the number of rastvashs in
its tarntarn [x].

Worked out for each rastvash: lumpyr to 1; lumnyr to 2; opalbra to 2; rastumb to 2;
fexrast to 2.

D10. The lumovi. The lumovi of the system is the collection of rastvashs whose vexnyr is
largest.

Running the definition over every rastvash leaves lumnyr, opalbra, rastumb and fexrast.

## The shape of it

The right picture for tarntarn is a spreading stain rather than a list. Drop one
rastvash in, apply the operation to whatever is wet, repeat. The stain here reaches 1
and 2 rastvashs depending on where it started.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T1 rests on D7 (the tarntarn of a rastvash) and D3 (umbclo collections). The dependence
is on the content of those results, not only on their vocabulary.

R12 rests on D7 (the tarntarn of a rastvash) and D9 (the vexnyr of a rastvash). Remove
any one of them and the statement stops making sense, not merely stops being provable.

R9 rests on D9 (the vexnyr of a rastvash) and T1 (the tarntarn of a rastvash is umbclo).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

T2 rests on D7 (the tarntarn of a rastvash) and T1 (the tarntarn of a rastvash is
umbclo). The dependence is on the content of those results, not only on their
vocabulary.

T3 rests on D1 (pyrglim rastvashs), D9 (the vexnyr of a rastvash) and T1 (the tarntarn
of a rastvash is umbclo). The dependence is on the content of those results, not only on
their vocabulary.

## A worked case

Here is (fexrast ? lumpyr) ? (opalbra ? lumnyr), reduced without skipping anything.
    fexrast ? lumpyr = fexrast   (the table for ?)
    opalbra ? lumnyr = lumnyr   (the table for ?)
    fexrast ? lumnyr = rastumb   (the table for ?)
That leaves rastumb, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is lumpyr ? (opalbra ? fexrast) for contrast.
    opalbra ? fexrast = lumpyr   (the table for ?)
    lumpyr ? lumpyr = lumpyr   (the table for ?)
The value is lumpyr, not rastumb.

One decision about the relation, since deciding is as much a skill as computing. Does
fexrast >> lumnyr hold? Read off what fexrast stands over: fexrast. lumnyr is not among
them, so it fails.

Now compute [opalbra]. Fold opalbra against itself, then fold whatever appeared against
everything present, and stop when a round adds nothing. The result is lumpyr and
opalbra, of size 2.

## A case that breaks

R12. It is not the case that: There is a rastvash whose tarntarn is the whole system.
The case that settles it: largest_span = 2, size = 5. Anyone carrying this claim over
from a more familiar system will be wrong here, and wrong in a way that propagates.

R9. It is not the case that: For every rastvash x, the vexnyr of x divides 5. It fails
at x = lumnyr, reach = 2, size = 5. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: D1 (pyrglim rastvashs), D3 (umbclo collections)
and D7 (the tarntarn of a rastvash).

## Proofs

T1. For every rastvash x, the collection [x] is umbclo.

  (1) [D7] [x] is built by taking x and closing under ?.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 125 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

R12. It is not the case that: There is a rastvash whose tarntarn is the whole system.

  (1) [S2] Take the case largest_span = 2, size = 5, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

R9. It is not the case that: For every rastvash x, the vexnyr of x divides 5.

  (1) [S2] Take the case x = lumnyr, reach = 2, size = 5, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T2. If S is umbclo and contains x, then S contains all of [x].

  (1) [D7] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 45 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. x ? x = x holds if and only if [x] contains x alone.

  (1) [D1] If x ? x = x then {x} is already closed under ?.
  (2) [T1] So [x] = {x} and the vexnyr is one.
  (3) [D9] Conversely a span of one object must contain x ? x, which is then x.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the vexnyr of a rastvash and the lumovi. Each of these
is used by name later, so the names are worth learning rather than looking up.

The results now available are T1, T2 and T3, each settled by exhaustive check rather
than by argument from analogy.

Do not carry forward R12 and R9. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x031. How many rastvashs lie in [lumnyr]?
  x032. What is the vexnyr of opalbra?
  x033. How many rastvashs lie in [rastumb]?
  x034. How many rastvashs lie in [fexrast]?
Level 4.
  x037. List every rastvash in the lumovi.
  x038. What is the largest vexnyr any rastvash has?
Level 5.
  x035. Let z be (fexrast ? lumpyr) ? lumnyr. What is the vexnyr of z?
  x036. Let z be (rastumb ? opalbra) ? opalbra. What is the vexnyr of z?
  x039. The following fails in this system: For every rastvash x, the vexnyr of x divides 5. Name the earliest rastvash, in the order the rastvashs were introduced, that witnesses the failure.
