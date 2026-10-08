# The Bravor system

The Bravor system is small enough to hold in the hand and strange enough to be worth the
trouble. It has 6 vintzams, one operation, and one relation, and nothing else.

The vintzams are written hurnvash, duthsib, drishen, pyryuk, aztka and ovijen. The first
operation is written :. The relation is written ::; where it holds between two vintzams
we say the left one yields to the right one. Both operations associate to the left when
written without brackets, and brackets override that. Repeated combination is
abbreviated: x^3 means x : x : x.

A warning that will be repeated because it is the one readers ignore: nothing here is
inherited from arithmetic. Familiar names have been avoided on purpose. Where a law of
arithmetic happens to hold it is stated and checked, and where it fails a counterexample
is given.

# Chapter 1. The objects and their notation

## Why this chapter

What follows was pieced together backwards. The last item of it, the Bravor signature,
the Bravor combination tables and closure under the first operation, was noticed before
anyone had a reason to expect it.

The standard of proof here is exhaustion. A universal claim about vintzams covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## The tables in full

The table for :. Read the left argument down the side and the right argument across the top.

          |  hurnvash   duthsib   drishen    pyryuk     aztka    ovijen
-----------------------------------------------------------------------
 hurnvash |  hurnvash  hurnvash  hurnvash  hurnvash  hurnvash  hurnvash
  duthsib |   duthsib  hurnvash  hurnvash  hurnvash  hurnvash  hurnvash
  drishen |   drishen   duthsib  hurnvash  hurnvash  hurnvash  hurnvash
   pyryuk |    pyryuk   drishen   duthsib  hurnvash  hurnvash  hurnvash
    aztka |     aztka    pyryuk   drishen   duthsib  hurnvash  hurnvash
   ovijen |    ovijen     aztka    pyryuk   drishen   duthsib  hurnvash

Every pair standing in the :: relation, grouped by left argument.

  hurnvash :: hurnvash, duthsib, drishen, pyryuk, aztka and ovijen
  duthsib :: hurnvash
  drishen :: hurnvash
  pyryuk :: hurnvash
  aztka :: hurnvash
  ovijen :: hurnvash

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A1. Closure under the first operation. For all vintzams x and y, x : y is again a
vintzam.

## The shape of it

Two questions sort the vintzams quickly. Does combining a vintzam with itself change it?
For hurnvash it does not. Does it matter which side it goes on? It always does.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R1 rests on S2 (the Bravor combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

R2 rests on S2 (the Bravor combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R5 rests on S2 (the Bravor combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R6 rests on S2 (the Bravor combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

## A worked case

Evaluate (hurnvash : pyryuk) : drishen. Each line below is one lookup in a table.
    hurnvash : pyryuk = hurnvash   (the table for :)
    hurnvash : drishen = hurnvash   (the table for :)
The expression comes to hurnvash.

Move the brackets and the work changes. Take pyryuk : (drishen : hurnvash).
    drishen : hurnvash = drishen   (the table for :)
    pyryuk : drishen = duthsib   (the table for :)
That gives duthsib, against hurnvash above.

Test aztka :: aztka. The qennyr of aztka is hurnvash, and aztka lies outside it, so the
relation fails.

## A case that breaks

R1. It is not the case that: For all vintzams x, y, z: (x : y) : z = x : (y : z). It
fails at x = duthsib, y = hurnvash, z = duthsib, left = hurnvash, right = duthsib. One
case is enough, and this is the earliest one.

R2. It is not the case that: For all vintzams x and y: x : y = y : x. The case that
settles it: x = hurnvash, y = duthsib, left = hurnvash, right = duthsib. Anyone carrying
this claim over from a more familiar system will be wrong here, and wrong in a way that
propagates.

R5. It is not the case that: For every vintzam x: x : x = x. The case that settles it: x
= duthsib, value = hurnvash. Anyone carrying this claim over from a more familiar system
will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

These results are used again in R3 (the system does not have a neutral object for the
first operation), R4 (the system does not have reversal under the first operation), R7
(the system does not have an absorbing object for the first operation) and R8 (the
system does not have reflexivity of the relation).

## Proofs

R1. It is not the case that: For all vintzams x, y, z: (x : y) : z = x : (y : z).

  (1) [S2] Take the case x = duthsib, y = hurnvash, z = duthsib, left = hurnvash, right = duthsib, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R2. It is not the case that: For all vintzams x and y: x : y = y : x.

  (1) [S2] Take the case x = hurnvash, y = duthsib, left = hurnvash, right = duthsib, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R5. It is not the case that: For every vintzam x: x : x = x.

  (1) [S2] Take the case x = duthsib, value = hurnvash, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R6. It is not the case that: For all vintzams x, y, z: if x : y = x : z then y = z.

  (1) [S2] Take the case x = hurnvash, y = hurnvash, z = duthsib, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R1, R2, R5 and R6. A later argument that quietly assumes one
of these is wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 1.
  x001. What vintzam does ovijen : drishen name?
  x002. Reduce drishen : pyryuk to a single vintzam.
  x003. Evaluate pyryuk : duthsib.
  x004. What vintzam does ovijen : ovijen name?
  x005. Work out the value of drishen : ovijen.
Level 2.
  x006. Reduce (duthsib : aztka) : drishen to a single vintzam.
  x007. Evaluate duthsib^3.
  x008. What is duthsib combined with itself 2 times under :?
  x009. Evaluate ovijen^2.
  x010. Which vintzams x satisfy x : drishen = duthsib? List them all.
  x011. Solve x : duthsib = duthsib for x, naming every solution.
  x012. Which vintzams x satisfy x : duthsib = drishen? List them all.
  x013. Solve x : drishen = hurnvash for x, naming every solution.
Level 5.
  x014. The following fails in this system: For all vintzams x, y, z: (x : y) : z = x : (y : z). Name the earliest vintzam, in the order the vintzams were introduced, that witnesses the failure.
  x015. The following fails in this system: For all vintzams x and y: x : y = y : x. Name the earliest vintzam, in the order the vintzams were introduced, that witnesses the failure.
  x017. The following fails in this system: For every vintzam x: x : x = x. Name the earliest vintzam, in the order the vintzams were introduced, that witnesses the failure.
  x018. The following fails in this system: For all vintzams x, y, z: if x : y = x : z then y = z. Name the earliest vintzam, in the order the vintzams were introduced, that witnesses the failure.

# Chapter 2. Neutral objects and reversal

## Why this chapter

Anyone using this system to keep track of something will meet the system does not have a
neutral object for the first operation, the system does not have reversal under the
first operation and the system does not have an absorbing object for the first operation
early, whether or not they go looking.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
vintzams that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

Nothing new is named here. The chapter is about consequences of definitions already
given.

## The shape of it

The neutral vintzam is the one that does nothing. That sounds trivial and is not: almost
every result in this chapter is an argument about what doing nothing forces.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R3 rests on S2 (the Bravor combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R4 rests on S2 (the Bravor combination tables). Remove any one of them and the statement
stops making sense, not merely stops being provable.

R7 rests on S2 (the Bravor combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Take (hurnvash : pyryuk) : (duthsib : aztka) and work it out one step at a time.
    hurnvash : pyryuk = hurnvash   (the table for :)
    duthsib : aztka = hurnvash   (the table for :)
    hurnvash : hurnvash = hurnvash   (the table for :)
The expression comes to hurnvash.

Bracketing is not cosmetic, so here is pyryuk : (duthsib : hurnvash) for contrast.
    duthsib : hurnvash = duthsib   (the table for :)
    pyryuk : duthsib = drishen   (the table for :)
That gives drishen, against hurnvash above.

One decision about the relation, since deciding is as much a skill as computing. Does
pyryuk :: aztka hold? Read off what pyryuk stands over: hurnvash. aztka is not among
them, so it fails.

## A case that breaks

R3. There is no vintzam e with e : x = x : e = x for every vintzam x. It fails at reason
= no two sided identity exists. One case is enough, and this is the earliest one.

R4. Some vintzam x admits no vintzam y for which x : y and y : x both land on a neutral
object. The case that settles it: reason = no identity, so inverses are not defined.
Anyone carrying this claim over from a more familiar system will be wrong here, and
wrong in a way that propagates.

R7. There is no vintzam z with z : x = x : z = z for every vintzam x. It fails at reason
= no absorbing element. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: S2 (the Bravor combination tables).

## Proofs

R3. There is no vintzam e with e : x = x : e = x for every vintzam x.

  (1) [S2] Take the case reason = no two sided identity exists, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R4. Some vintzam x admits no vintzam y for which x : y and y : x both land on a neutral object.

  (1) [S2] Take the case reason = no identity, so inverses are not defined, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R7. There is no vintzam z with z : x = x : z = z for every vintzam x.

  (1) [S2] Take the case reason = no absorbing element, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R3, R4 and R7. These were tested and failed, and the failing cases
are recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 5.
  x016. The following fails in this system: Some vintzam x admits no vintzam y for which x : y and y : x both land on a neutral object. Name the earliest vintzam, in the order the vintzams were introduced, that witnesses the failure.

# Chapter 3. The relation and what it orders

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through the qennyr of a vintzam, the
system does not have transitivity of the relation and the system does not have
comparability of every pair.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
vintzams that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D4. The qennyr of a vintzam. The qennyr of a vintzam x is the collection of vintzams y
for which x :: y holds.

Worked out for each vintzam: hurnvash to hurnvash, duthsib, drishen, pyryuk, aztka and
ovijen; duthsib to hurnvash; drishen to hurnvash; pyryuk to hurnvash; aztka to hurnvash;
ovijen to hurnvash.

## The shape of it

The relation is easiest to see as a height. Each vintzam casts a qennyr over what it
yields to, and the sizes of those shadows here are 1 and 6. Sizes repeat, so the objects
do not line up in single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 vintzams the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R10 rests on S2 (the Bravor combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R11 rests on S2 (the Bravor combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R12 rests on S2 (the Bravor combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R8 rests on S2 (the Bravor combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R9 rests on S2 (the Bravor combination tables). The dependence is on the content of
those results, not only on their vocabulary.

## A worked case

Evaluate (ovijen : aztka) : pyryuk. Each line below is one lookup in a table.
    ovijen : aztka = duthsib   (the table for :)
    duthsib : pyryuk = hurnvash   (the table for :)
That leaves hurnvash, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is aztka : (pyryuk : ovijen) for contrast.
    pyryuk : ovijen = hurnvash   (the table for :)
    aztka : hurnvash = aztka   (the table for :)
The value is aztka, not hurnvash.

Test drishen :: ovijen. The qennyr of drishen is hurnvash, and ovijen lies outside it,
so the relation fails.

## A case that breaks

R10. It is not the case that: For all vintzams x, y, z: if x :: y and y :: z then x ::
z. It fails at x = duthsib, y = hurnvash, z = duthsib. One case is enough, and this is
the earliest one.

R11. It is not the case that: For all vintzams x and y, at least one of x :: y and y ::
x holds. It fails at x = duthsib, y = duthsib. One case is enough, and this is the
earliest one.

R12. It is not the case that: For all vintzams x, y, z: if x :: y then (z : x) :: (z :
y) and (x : z) :: (y : z). The case that settles it: x = hurnvash, y = hurnvash, z =
duthsib, side = left. Anyone carrying this claim over from a more familiar system will
be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside S2 (the Bravor combination tables).

These results are used again in D8 (a nyrmux), D11 (tezreld pairs) and T6 (the relation
reads the same in both directions).

## Proofs

R10. It is not the case that: For all vintzams x, y, z: if x :: y and y :: z then x :: z.

  (1) [S2] Take the case x = duthsib, y = hurnvash, z = duthsib, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R11. It is not the case that: For all vintzams x and y, at least one of x :: y and y :: x holds.

  (1) [S2] Take the case x = duthsib, y = duthsib, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R12. It is not the case that: For all vintzams x, y, z: if x :: y then (z : x) :: (z : y) and (x : z) :: (y : z).

  (1) [S2] Take the case x = hurnvash, y = hurnvash, z = duthsib, side = left, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R8. It is not the case that: For every vintzam x: x :: x.

  (1) [S2] Take the case x = duthsib, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R9. It is not the case that: For all vintzams x and y: if x :: y and y :: x then x = y.

  (1) [S2] Take the case x = hurnvash, y = duthsib, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the qennyr of a vintzam. Later chapters state their results in these terms
and do not restate the definitions.

Do not carry forward R10, R11, R12, R8 and R9. These were tested and failed, and the
failing cases are recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x026. List the qennyr of hurnvash.
  x027. Which vintzams y satisfy duthsib :: y? Name them all.
  x028. Which vintzams y satisfy drishen :: y? Name them all.
  x029. Which vintzams y satisfy pyryuk :: y? Name them all.
  x030. Which vintzams y satisfy aztka :: y? Name them all.
  x031. Which vintzams y satisfy ovijen :: y? Name them all.
Level 5.
  x019. The following fails in this system: For every vintzam x: x :: x. Name the earliest vintzam, in the order the vintzams were introduced, that witnesses the failure.
  x020. The following fails in this system: For all vintzams x and y: if x :: y and y :: x then x = y. Name the earliest vintzam, in the order the vintzams were introduced, that witnesses the failure.
  x021. The following fails in this system: For all vintzams x, y, z: if x :: y and y :: z then x :: z. Name the earliest vintzam, in the order the vintzams were introduced, that witnesses the failure.
  x022. The following fails in this system: For all vintzams x, y, z: if x :: y then (z : x) :: (z : y) and (x : z) :: (y : z). Name the earliest vintzam, in the order the vintzams were introduced, that witnesses the failure.

# Chapter 4. Combining objects

## Why this chapter

We turn to shenfal vintzams, vintzams that tuwren and reldjen collections. The treatment
is self contained given the material already established.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
vintzams that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D1. Shenfal vintzams. A vintzam x is called shenfal when x : x = x.

Running the definition over every vintzam leaves hurnvash.

D2. Vintzams that tuwren. Two vintzams x and y are said to tuwren when x : y = y : x.

D3. Reldjen collections. A collection S of vintzams is reldjen when x : y belongs to S
for every pair x, y drawn from S.

## The shape of it

Picture the zamsol as what happens when you start with one vintzam and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 6 vintzams, that stops. In this system the sizes it stops at are 1 and 2.

Two questions sort the vintzams quickly. Does combining a vintzam with itself change it?
For hurnvash it does not. Does it matter which side it goes on? It always does.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Nothing is derived in this chapter. It lays down material that later chapters draw on.

## A worked case

Evaluate (pyryuk : hurnvash) : (ovijen : drishen). Each line below is one lookup in a
table.
    pyryuk : hurnvash = pyryuk   (the table for :)
    ovijen : drishen = pyryuk   (the table for :)
    pyryuk : pyryuk = hurnvash   (the table for :)
So (pyryuk : hurnvash) : (ovijen : drishen) is hurnvash.

A companion case, hurnvash : (ovijen : pyryuk), to show what the brackets are doing.
    ovijen : pyryuk = drishen   (the table for :)
    hurnvash : drishen = hurnvash   (the table for :)
The value is hurnvash. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
duthsib :: duthsib hold? Read off what duthsib stands over: hurnvash. duthsib is not
among them, so it fails.

## A case that breaks

A quick guard against a common slip: pyryuk : ovijen is hurnvash while ovijen : pyryuk
is drishen. Order is not decoration in this system.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by closure under the first operation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: A1 (closure under the first operation).

These results are used again in D5 (the falwren), D6 (the vextarn), D7 (the zamsol of a
vintzam) and T1 (the zamsol of a vintzam is reldjen).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

Carry forward shenfal vintzams, vintzams that tuwren and reldjen collections. Later
chapters state their results in these terms and do not restate the definitions.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x023. List every vintzam in the shenfal.
  x024. How many vintzams lie in the smallest reldjen collection containing duthsib?
  x025. How many vintzams lie in the smallest reldjen collection containing drishen?

# Chapter 5. The relation and what it orders (2)

## Why this chapter

Everything in this chapter is checkable by inspection. The subject is tezreld pairs, a
nyrmux and the relation reads the same in both directions.

Nothing here stands on its own. The arguments lean on chapter 3, and a reader who has
skipped it will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about vintzams covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

## What is defined here

D11. Tezreld pairs. Two distinct vintzams x and y form a tezreld pair when x :: y and y
:: x both hold, that is, when each lies in the qennyr of the other.

In this system that picks out hurnvash, duthsib, drishen, pyryuk, aztka and ovijen, that
is, all of them.

D8. A nyrmux. A vintzam f is a nyrmux when f :: y holds for every vintzam y, that is,
when the qennyr of f is the whole system.

Running the definition over every vintzam leaves hurnvash.

## The shape of it

Think of :: as pointing downhill. The qennyr of a vintzam is everything downhill of it,
and those shadows here have sizes 1 and 6.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T6 rests on D4 (the qennyr of a vintzam). The dependence is on the content of those
results, not only on their vocabulary.

## A worked case

Evaluate (hurnvash : duthsib) : drishen. Each line below is one lookup in a table.
    hurnvash : duthsib = hurnvash   (the table for :)
    hurnvash : drishen = hurnvash   (the table for :)
So (hurnvash : duthsib) : drishen is hurnvash.

Move the brackets and the work changes. Take duthsib : (drishen : hurnvash).
    drishen : hurnvash = drishen   (the table for :)
    duthsib : drishen = hurnvash   (the table for :)
That gives hurnvash, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
hurnvash :: aztka hold? Read off what hurnvash stands over: hurnvash, duthsib, drishen,
pyryuk, aztka and ovijen. aztka is among them, so it holds.

## A case that breaks

A quick guard against a common slip: hurnvash : ovijen is hurnvash while ovijen :
hurnvash is ovijen. Order is not decoration in this system.

## Reach and limits

The limits of these results are sharper than they look.

To see how little the notation guarantees: rebuild the system with the same names over
different tables and T6 fail outright.

## Neighbouring results

The material this chapter borrows from: D4 (the qennyr of a vintzam).

## Proofs

T6. If x :: y then y :: x.

  (1) [D4] Symmetry would mean y lies in the qennyr of x exactly when x lies in that of y.
  (2) The listed pairs settle it directly.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward tezreld pairs and a nyrmux. Later chapters state their results in these
terms and do not restate the definitions.

The results now available are T6, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x040. Write down the nyrmux in full.
  x049. Write down the tezreld in full.

# Chapter 6. Combining objects (2)

## Why this chapter

What follows was pieced together backwards. The last item of it, the falwren, the
vextarn and the zamsol of a vintzam, was noticed before anyone had a reason to expect
it.

Nothing here stands on its own. The arguments lean on chapter 4, and a reader who has
skipped it will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over vintzams, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D5. The falwren. The falwren of the system is the collection of vintzams that tuwren
with every vintzam.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D6. The vextarn. The vextarn is the collection of all shenfal vintzams.

Running the definition over every vintzam leaves hurnvash.

D7. The zamsol of a vintzam. The zamsol of a vintzam x, written [x], is the smallest
reldjen collection that contains x.

Worked out for each vintzam: hurnvash to hurnvash; duthsib to hurnvash and duthsib;
drishen to hurnvash and drishen; pyryuk to hurnvash and pyryuk; aztka to hurnvash and
aztka; ovijen to hurnvash and ovijen.

## The shape of it

The right picture for zamsol is a spreading stain rather than a list. Drop one vintzam
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
vintzams depending on where it started.

A useful mental split: some vintzams are inert under the operation and some are not.
hurnvash come back unchanged when combined with themselves, and none commutes with
everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 vintzams the table is short enough to consult every time.

## Where these results come from

Nothing is derived in this chapter. It lays down material that later chapters draw on.

## A worked case

Take (pyryuk : ovijen) : (aztka : hurnvash) and work it out one step at a time.
    pyryuk : ovijen = hurnvash   (the table for :)
    aztka : hurnvash = aztka   (the table for :)
    hurnvash : aztka = hurnvash   (the table for :)
So (pyryuk : ovijen) : (aztka : hurnvash) is hurnvash.

A companion case, ovijen : (aztka : pyryuk), to show what the brackets are doing.
    aztka : pyryuk = duthsib   (the table for :)
    ovijen : duthsib = aztka   (the table for :)
The value is aztka, not hurnvash.

One decision about the relation, since deciding is as much a skill as computing. Does
pyryuk :: ovijen hold? Read off what pyryuk stands over: hurnvash. ovijen is not among
them, so it fails.

A second case, this time a zamsol. Start from ovijen. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is hurnvash and
ovijen, so the vashnyr of ovijen is 2.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: D1 (shenfal vintzams), D2 (vintzams that tuwren)
and D3 (reldjen collections).

These results are used again in D9 (the vashnyr of a vintzam), T1 (the zamsol of a
vintzam is reldjen), T2 (the zamsol is contained in every reldjen collection) and T5
(the vextarn is reldjen).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

New vocabulary from this chapter: the falwren, the vextarn and the zamsol of a vintzam.
Each of these is used by name later, so the names are worth learning rather than looking
up.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x032. List every vintzam in the vextarn.
  x033. List the zamsol of duthsib.
  x034. List the zamsol of drishen.
  x035. List the zamsol of pyryuk.
  x036. List the zamsol of aztka.
  x037. Name every vintzam in [ovijen].
Level 4.
  x038. Let z be drishen : hurnvash. List the zamsol of z.
  x039. Let z be drishen : aztka. List the zamsol of z.

# Chapter 7. Combining objects (3)

## Why this chapter

Anyone using this system to keep track of something will meet where every vintzam lies
in the falwren breaks down, where every vintzam is shenfal breaks down and the vextarn
is reldjen early, whether or not they go looking.

Nothing here stands on its own. The arguments lean on chapters 4 and 6, and a reader who
has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over vintzams, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

Two questions sort the vintzams quickly. Does combining a vintzam with itself change it?
For hurnvash it does not. Does it matter which side it goes on? It always does.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R13 rests on D5 (the falwren). The dependence is on the content of those results, not
only on their vocabulary.

R14 rests on D6 (the vextarn). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T5 rests on D6 (the vextarn) and D3 (reldjen collections). The dependence is on the
content of those results, not only on their vocabulary.

## A worked case

Take (ovijen : duthsib) : drishen and work it out one step at a time.
    ovijen : duthsib = aztka   (the table for :)
    aztka : drishen = drishen   (the table for :)
That leaves drishen, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is duthsib : (drishen : ovijen) for contrast.
    drishen : ovijen = hurnvash   (the table for :)
    duthsib : hurnvash = duthsib   (the table for :)
That gives duthsib, against drishen above.

Test drishen :: aztka. The qennyr of drishen is hurnvash, and aztka lies outside it, so
the relation fails.

## A case that breaks

R13. It is not the case that: Every pair of vintzams tuwrens. The case that settles it:
x = hurnvash, y = duthsib, left = hurnvash, right = duthsib. Anyone carrying this claim
over from a more familiar system will be wrong here, and wrong in a way that propagates.

R14. It is not the case that: x : x = x for every vintzam x. It fails at x = duthsib,
value = hurnvash. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by closure under the first operation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside D3 (reldjen collections), D5 (the falwren) and D6 (the vextarn).

## Proofs

R13. It is not the case that: Every pair of vintzams tuwrens.

  (1) [S2] Take the case x = hurnvash, y = duthsib, left = hurnvash, right = duthsib, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

R14. It is not the case that: x : x = x for every vintzam x.

  (1) [S2] Take the case x = duthsib, value = hurnvash, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T5. If x and y are both shenfal then so is x : y.

  (1) [D6] Let x and y be shenfal.
  (2) [D1] The claim asks whether (x : y) : (x : y) returns x : y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 36 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Established here and safe to use: T5.

Do not carry forward R13 and R14. These were tested and failed, and the failing cases
are recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x051. This result is about the vextarn. List every vintzam in it.
Level 5.
  x052. The following fails in this system: Every pair of vintzams tuwrens. Name the earliest vintzam, in the order the vintzams were introduced, that witnesses the failure.
  x053. The following fails in this system: x : x = x for every vintzam x. Name the earliest vintzam, in the order the vintzams were introduced, that witnesses the failure.

# Chapter 8. Collections that close on themselves

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through the vashnyr of a vintzam, the
zamsol of a vintzam is reldjen and the ponkorr.

Nothing here stands on its own. The arguments lean on chapters 4 and 6, and a reader who
has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
vintzams that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D9. The vashnyr of a vintzam. The vashnyr of a vintzam x is the number of vintzams in
its zamsol [x].

Worked out for each vintzam: hurnvash to 1; duthsib to 2; drishen to 2; pyryuk to 2;
aztka to 2; ovijen to 2.

D10. The ponkorr. The ponkorr of the system is the collection of vintzams whose vashnyr
is largest.

Running the definition over every vintzam leaves duthsib, drishen, pyryuk, aztka and
ovijen.

## The shape of it

The right picture for zamsol is a spreading stain rather than a list. Drop one vintzam
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
vintzams depending on where it started.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 vintzams the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T1 rests on D7 (the zamsol of a vintzam) and D3 (reldjen collections). The dependence is
on the content of those results, not only on their vocabulary.

R15 rests on D7 (the zamsol of a vintzam) and D9 (the vashnyr of a vintzam). The
dependence is on the content of those results, not only on their vocabulary.

T2 rests on D7 (the zamsol of a vintzam) and T1 (the zamsol of a vintzam is reldjen).
The dependence is on the content of those results, not only on their vocabulary.

T3 rests on D1 (shenfal vintzams), D9 (the vashnyr of a vintzam) and T1 (the zamsol of a
vintzam is reldjen). The dependence is on the content of those results, not only on
their vocabulary.

T4 rests on D9 (the vashnyr of a vintzam) and T1 (the zamsol of a vintzam is reldjen).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

## A worked case

Take (aztka : ovijen) : (hurnvash : pyryuk) and work it out one step at a time.
    aztka : ovijen = hurnvash   (the table for :)
    hurnvash : pyryuk = hurnvash   (the table for :)
    hurnvash : hurnvash = hurnvash   (the table for :)
That leaves hurnvash, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take ovijen : (hurnvash : aztka).
    hurnvash : aztka = hurnvash   (the table for :)
    ovijen : hurnvash = ovijen   (the table for :)
The value is ovijen, not hurnvash.

One decision about the relation, since deciding is as much a skill as computing. Does
aztka :: duthsib hold? Read off what aztka stands over: hurnvash. duthsib is not among
them, so it fails.

A second case, this time a zamsol. Start from hurnvash. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is hurnvash, so the
vashnyr of hurnvash is 1.

## A case that breaks

R15. It is not the case that: There is a vintzam whose zamsol is the whole system. The
case that settles it: largest_span = 2, size = 6. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: D1 (shenfal vintzams), D3 (reldjen collections)
and D7 (the zamsol of a vintzam).

## Proofs

T1. For every vintzam x, the collection [x] is reldjen.

  (1) [D7] [x] is built by taking x and closing under :.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 216 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

R15. It is not the case that: There is a vintzam whose zamsol is the whole system.

  (1) [S2] Take the case largest_span = 2, size = 6, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T2. If S is reldjen and contains x, then S contains all of [x].

  (1) [D7] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 66 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. x : x = x holds if and only if [x] contains x alone.

  (1) [D1] If x : x = x then {x} is already closed under :.
  (2) [T1] So [x] = {x} and the vashnyr is one.
  (3) [D9] Conversely a span of one object must contain x : x, which is then x.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T4. For every vintzam x, the vashnyr of x divides 6.

  (1) [T1] [x] is a reldjen collection.
  (2) [D9] Its size is the vashnyr of x.
  (3) The claim is that this size always divides 6.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the vashnyr of a vintzam and the ponkorr. Later chapters state their
results in these terms and do not restate the definitions.

The results now available are T1, T2, T3 and T4, each settled by exhaustive check rather
than by argument from analogy.

Explicitly not available: R15. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x041. How many vintzams lie in [duthsib]?
  x042. What is the vashnyr of drishen?
  x043. What is the vashnyr of pyryuk?
  x044. How many vintzams lie in [aztka]?
  x045. How many vintzams lie in [ovijen]?
Level 4.
  x048. Which vintzams make up the ponkorr? Name them all.
  x050. What is the largest vashnyr any vintzam has?
Level 5.
  x046. Let z be (hurnvash : duthsib) : pyryuk. What is the vashnyr of z?
  x047. Let z be (drishen : ovijen) : drishen. What is the vashnyr of z?
