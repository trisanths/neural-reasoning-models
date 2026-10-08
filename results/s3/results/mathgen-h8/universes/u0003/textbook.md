# The Espadri system

The Espadri system is small enough to hold in the hand and strange enough to be worth
the trouble. It has 6 wrenhobs, two operations, and one relation, and nothing else.

The wrenhobs are written iskglim, lornhob, tuisk, kaglim, xilfal and ovipyr. The first
operation is written ;. The second is written |= and binds more tightly, so x ; y |= z
means x ; (y |= z). The relation is written >-; where it holds between two wrenhobs we
say the left one dominates the right one. Both operations associate to the left when
written without brackets, and brackets override that. Repeated combination is
abbreviated: x^3 means x ; x ; x.

Readers arriving from arithmetic should put it down at the door. The operations below
are defined by their tables and by nothing else. Several arithmetic habits survive the
crossing and several do not, and the text is careful to say which is which.

# Chapter 1. The objects and their notation

## Why this chapter

The results collected here were not found in this order. The Espadri signature, the
Espadri combination tables and closure under the first operation came first, and the
rest was assembled around that once the pattern was visible.

The standard of proof here is exhaustion. A universal claim about wrenhobs covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## The tables in full

The table for ;. Read the left argument down the side and the right argument across the top.

         |  iskglim  lornhob    tuisk   kaglim   xilfal   ovipyr
----------------------------------------------------------------
 iskglim |  iskglim  lornhob    tuisk   kaglim   xilfal   ovipyr
 lornhob |  lornhob    tuisk   kaglim   xilfal   ovipyr   ovipyr
   tuisk |    tuisk   kaglim   xilfal   ovipyr   ovipyr   ovipyr
  kaglim |   kaglim   xilfal   ovipyr   ovipyr   ovipyr   ovipyr
  xilfal |   xilfal   ovipyr   ovipyr   ovipyr   ovipyr   ovipyr
  ovipyr |   ovipyr   ovipyr   ovipyr   ovipyr   ovipyr   ovipyr

The table for |=. Read the left argument down the side and the right argument across the top.

         |  iskglim  lornhob    tuisk   kaglim   xilfal   ovipyr
----------------------------------------------------------------
 iskglim |  iskglim  lornhob    tuisk   kaglim   xilfal   ovipyr
 lornhob |  iskglim  lornhob    tuisk   kaglim   xilfal   ovipyr
   tuisk |  iskglim  lornhob    tuisk   kaglim   xilfal   ovipyr
  kaglim |  iskglim  lornhob    tuisk   kaglim   xilfal   ovipyr
  xilfal |  iskglim  lornhob    tuisk   kaglim   xilfal   ovipyr
  ovipyr |  iskglim  lornhob    tuisk   kaglim   xilfal   ovipyr

Every pair standing in the >- relation, grouped by left argument.

  iskglim >- iskglim, lornhob, tuisk, kaglim, xilfal and ovipyr
  lornhob >- lornhob, tuisk, kaglim, xilfal and ovipyr
  tuisk >- tuisk, kaglim, xilfal and ovipyr
  kaglim >- kaglim, xilfal and ovipyr
  xilfal >- xilfal and ovipyr
  ovipyr >- ovipyr

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A1. Closure under the first operation. For all wrenhobs x and y, x ; y is again a
wrenhob.

A2. Association of the first operation. For all wrenhobs x, y, z: (x ; y) ; z = x ; (y ;
z).

A3. Commutation of the first operation. For all wrenhobs x and y: x ; y = y ; x.

## The shape of it

A useful mental split: some wrenhobs are inert under the operation and some are not.
iskglim and ovipyr come back unchanged when combined with themselves, and iskglim,
lornhob, tuisk, kaglim, xilfal and ovipyr commute with everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 wrenhobs the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R2 rests on S2 (the Espadri combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R3 rests on S2 (the Espadri combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Here is lornhob ; xilfal |= ovipyr, reduced without skipping anything.
    xilfal |= ovipyr = ovipyr   (the table for |=)
    lornhob ; ovipyr = ovipyr   (the table for ;)
The expression comes to ovipyr.

Move the brackets and the work changes. Take xilfal ; (ovipyr ; lornhob).
    ovipyr ; lornhob = ovipyr   (the table for ;)
    xilfal ; ovipyr = ovipyr   (the table for ;)
That gives ovipyr, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test xilfal >- lornhob. The solzam of xilfal is xilfal and ovipyr, and lornhob lies
outside it, so the relation fails.

## A case that breaks

R2. It is not the case that: For every wrenhob x: x ; x = x. The case that settles it: x
= lornhob, value = tuisk. Anyone carrying this claim over from a more familiar system
will be wrong here, and wrong in a way that propagates.

R3. It is not the case that: For all wrenhobs x, y, z: if x ; y = x ; z then y = z. It
fails at x = lornhob, y = xilfal, z = ovipyr. One case is enough, and this is the
earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

What is built on it later: A4 (a neutral object for the first operation), A5 (an
absorbing object for the first operation), A6 (closure under the second operation) and
A7 (association of the second operation).

## Proofs

R2. It is not the case that: For every wrenhob x: x ; x = x.

  (1) [S2] Take the case x = lornhob, value = tuisk, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R3. It is not the case that: For all wrenhobs x, y, z: if x ; y = x ; z then y = z.

  (1) [S2] Take the case x = lornhob, y = xilfal, z = ovipyr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R2 and R3. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 1.
  x001. What wrenhob does tuisk ; lornhob name?
  x002. Evaluate lornhob ; xilfal.
  x003. Reduce xilfal ; lornhob to a single wrenhob.
  x004. Reduce kaglim ; lornhob to a single wrenhob.
Level 2.
  x005. What wrenhob does (tuisk ; lornhob) ; lornhob name?
  x006. Work out the value of (xilfal ; iskglim) ; tuisk.
  x008. Evaluate kaglim^2.
  x009. Evaluate lornhob^3.
  x010. Which wrenhobs x satisfy x ; kaglim = ovipyr? List them all.
  x011. Solve x ; xilfal = ovipyr for x, naming every solution.
  x012. Solve x ; xilfal = xilfal for x, naming every solution.
  x013. Which wrenhobs x satisfy x ; tuisk = kaglim? List them all.
Level 3.
  x007. What wrenhob does (kaglim ; xilfal) ; (xilfal ; iskglim) name?
  x014. Evaluate lornhob ; tuisk |= tuisk, minding which operation binds tighter.
Level 5.
  x016. The following fails in this system: For every wrenhob x: x ; x = x. Name the earliest wrenhob, in the order the wrenhobs were introduced, that witnesses the failure.
  x017. The following fails in this system: For all wrenhobs x, y, z: if x ; y = x ; z then y = z. Name the earliest wrenhob, in the order the wrenhobs were introduced, that witnesses the failure.

# Chapter 2. Neutral objects and reversal

## Why this chapter

The practical content of this chapter is a neutral object for the first operation, an
absorbing object for the first operation and the system does not have reversal under the
first operation. It is the part that shows up in use.

Prerequisites are real here: chapter 1 supply the notions the statements below are
phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
wrenhobs that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A4. A neutral object for the first operation. There is a wrenhob iskglim with iskglim ;
x = x ; iskglim = x for every x.

A5. An absorbing object for the first operation. There is a wrenhob ovipyr with ovipyr ;
x = x ; ovipyr = ovipyr for every x.

## The shape of it

Neutrality is a strong condition disguised as a weak one. It fixes a single wrenhob and,
through that, constrains everything that can combine with it.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R1 rests on S2 (the Espadri combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Here is (ovipyr ; tuisk) ; (xilfal ; iskglim), reduced without skipping anything.
    ovipyr ; tuisk = ovipyr   (the table for ;)
    xilfal ; iskglim = xilfal   (the table for ;)
    ovipyr ; xilfal = ovipyr   (the table for ;)
That leaves ovipyr, and no other reading of the notation gives anything else.

A companion case, tuisk ; (xilfal ; ovipyr), to show what the brackets are doing.
    xilfal ; ovipyr = ovipyr   (the table for ;)
    tuisk ; ovipyr = ovipyr   (the table for ;)
That gives ovipyr, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
iskglim >- ovipyr hold? Read off what iskglim stands over: iskglim, lornhob, tuisk,
kaglim, xilfal and ovipyr. ovipyr is among them, so it holds.

## A case that breaks

R1. Some wrenhob x admits no wrenhob y for which x ; y and y ; x both land on a neutral
object. The case that settles it: x = lornhob. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside S2 (the Espadri combination tables).

These results are used again in D5 (the zamthra) and T1 (the zamthra is the only one of
its kind).

## Proofs

R1. Some wrenhob x admits no wrenhob y for which x ; y and y ; x both land on a neutral object.

  (1) [S2] Take the case x = lornhob, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R1. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 5.
  x015. The following fails in this system: Some wrenhob x admits no wrenhob y for which x ; y and y ; x both land on a neutral object. Name the earliest wrenhob, in the order the wrenhobs were introduced, that witnesses the failure.

# Chapter 3. The relation and what it orders

## Why this chapter

So far the wrenhobs have been objects to be pushed around. This chapter starts asking
what they are like. We take up antisymmetry of the relation, transitivity of the
relation and comparability of every pair.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about wrenhobs covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A10. Antisymmetry of the relation. For all wrenhobs x and y: if x >- y and y >- x then x
= y.

A11. Transitivity of the relation. For all wrenhobs x, y, z: if x >- y and y >- z then x
>- z.

A12. Comparability of every pair. For all wrenhobs x and y, at least one of x >- y and y
>- x holds.

A13. Agreement of the relation with the first operation. For all wrenhobs x, y, z: if x
>- y then (z ; x) >- (z ; y) and (x ; z) >- (y ; z).

A14. Agreement of the relation with the second operation. For all wrenhobs x, y, z: if x
>- y then (z |= x) >- (z |= y) and (x |= z) >- (y |= z).

A9. Reflexivity of the relation. For every wrenhob x: x >- x.

D4. The solzam of a wrenhob. The solzam of a wrenhob x is the collection of wrenhobs y
for which x >- y holds.

Worked out for each wrenhob: iskglim to iskglim, lornhob, tuisk, kaglim, xilfal and
ovipyr; lornhob to lornhob, tuisk, kaglim, xilfal and ovipyr; tuisk to tuisk, kaglim,
xilfal and ovipyr; kaglim to kaglim, xilfal and ovipyr; xilfal to xilfal and ovipyr;
ovipyr to ovipyr.

## The shape of it

The relation is easiest to see as a height. Each wrenhob casts a solzam over what it
dominates, and the sizes of those shadows here are 1, 2, 3, 4, 5 and 6. No two are the
same size, so the objects line up in a single file.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Nothing is derived in this chapter. It lays down material that later chapters draw on.

## A worked case

Evaluate ovipyr ; tuisk |= lornhob. Each line below is one lookup in a table.
    tuisk |= lornhob = lornhob   (the table for |=)
    ovipyr ; lornhob = ovipyr   (the table for ;)
So ovipyr ; tuisk |= lornhob is ovipyr.

A companion case, tuisk ; (lornhob ; ovipyr), to show what the brackets are doing.
    lornhob ; ovipyr = ovipyr   (the table for ;)
    tuisk ; ovipyr = ovipyr   (the table for ;)
The value is ovipyr. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test xilfal >- lornhob. The solzam of xilfal is xilfal and ovipyr, and lornhob lies
outside it, so the relation fails.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: S2 (the Espadri combination tables).

What is built on it later: D9 (a nakgrix), D13 (vorzel pairs), T9 (solzams are nested
along the relation) and T10 (there is at most one nakgrix).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

New vocabulary from this chapter: the solzam of a wrenhob. Each of these is used by name
later, so the names are worth learning rather than looking up.

## Exercises

This chapter carries no exercises. Nothing in it can be asked about in a way that could
not be answered without reading it, and an exercise like that is worse than none.

# Chapter 4. The second operation and how the two interact

## Why this chapter

We turn to closure under the second operation, association of the second operation and
self combination under the second operation. The treatment is self contained given the
material already established.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about wrenhobs covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A6. Closure under the second operation. For all wrenhobs x and y, x |= y is again a
wrenhob.

A7. Association of the second operation. For all wrenhobs x, y, z: (x |= y) |= z = x |=
(y |= z).

A8. Self combination under the second operation. For every wrenhob x: x |= x = x.

## The shape of it

The interesting content of a two operation system sits in the gap between them: which
one distributes over which, and which wrenhobs are fixed by both.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 wrenhobs the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R4 rests on S2 (the Espadri combination tables). The dependence is on the content of
those results, not only on their vocabulary.

R5 rests on S2 (the Espadri combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R6 rests on S2 (the Espadri combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R7 rests on S2 (the Espadri combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take (iskglim ; tuisk) ; (xilfal ; ovipyr) and work it out one step at a time.
    iskglim ; tuisk = tuisk   (the table for ;)
    xilfal ; ovipyr = ovipyr   (the table for ;)
    tuisk ; ovipyr = ovipyr   (the table for ;)
So (iskglim ; tuisk) ; (xilfal ; ovipyr) is ovipyr.

A companion case, tuisk ; (xilfal ; iskglim), to show what the brackets are doing.
    xilfal ; iskglim = xilfal   (the table for ;)
    tuisk ; xilfal = ovipyr   (the table for ;)
The value is ovipyr. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test iskglim >- tuisk. The solzam of iskglim is iskglim, lornhob, tuisk, kaglim, xilfal
and ovipyr, and tuisk lies inside it, so the relation holds.

## A case that breaks

R4. It is not the case that: For all wrenhobs x and y: x |= y = y |= x. It fails at x =
iskglim, y = lornhob, left = lornhob, right = iskglim. One case is enough, and this is
the earliest one.

R5. There is no wrenhob that leaves every wrenhob unchanged under the second operation.
The case that settles it: reason = no two sided identity exists. Anyone carrying this
claim over from a more familiar system will be wrong here, and wrong in a way that
propagates.

R6. It is not the case that: For all wrenhobs x, y, z: x |= (y ; z) = (x |= y) ; (x |=
z), and the same on the right. It fails at x = lornhob, y = iskglim, z = iskglim, left =
lornhob, right = tuisk. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside S2 (the Espadri combination tables).

These results are used again in T15 (the second operation keeps the vintvint intact).

## Proofs

R4. It is not the case that: For all wrenhobs x and y: x |= y = y |= x.

  (1) [S2] Take the case x = iskglim, y = lornhob, left = lornhob, right = iskglim, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R5. There is no wrenhob that leaves every wrenhob unchanged under the second operation.

  (1) [S2] Take the case reason = no two sided identity exists, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R6. It is not the case that: For all wrenhobs x, y, z: x |= (y ; z) = (x |= y) ; (x |= z), and the same on the right.

  (1) [S2] Take the case x = lornhob, y = iskglim, z = iskglim, left = lornhob, right = tuisk, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R7. It is not the case that: For all wrenhobs x and y: x ; (x |= y) = x and x |= (x ; y) = x.

  (1) [S2] Take the case x = iskglim, y = lornhob, value = lornhob, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R4, R5, R6 and R7. A later argument that quietly assumes one
of these is wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 5.
  x018. The following fails in this system: For all wrenhobs x and y: x |= y = y |= x. Name the earliest wrenhob, in the order the wrenhobs were introduced, that witnesses the failure.
  x019. The following fails in this system: For all wrenhobs x and y: x ; (x |= y) = x and x |= (x ; y) = x. Name the earliest wrenhob, in the order the wrenhobs were introduced, that witnesses the failure.

# Chapter 5. Combining objects

## Why this chapter

Work through this chapter with the tables in front of you. It covers drimi wrenhobs,
wrenhobs that fexisk and the zamthra, and each claim can be checked by hand.

Prerequisites are real here: chapters 1 and 2 supply the notions the statements below
are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
wrenhobs that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D1. Drimi wrenhobs. A wrenhob x is called drimi when x ; x = x.

Running the definition over every wrenhob leaves iskglim and ovipyr.

D2. Wrenhobs that fexisk. Two wrenhobs x and y are said to fexisk when x ; y = y ; x.

D5. The zamthra. The wrenhob iskglim is called the zamthra of the system. It is the
unique wrenhob that leaves every wrenhob unchanged under ;.

Here that is iskglim.

## The shape of it

Two questions sort the wrenhobs quickly. Does combining a wrenhob with itself change it?
For iskglim and ovipyr it does not. Does it matter which side it goes on? For iskglim,
lornhob, tuisk, kaglim, xilfal and ovipyr it does not.

Neutrality is a strong condition disguised as a weak one. It fixes a single wrenhob and,
through that, constrains everything that can combine with it.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Nothing is derived in this chapter. It lays down material that later chapters draw on.

## A worked case

Take lornhob ; xilfal |= ovipyr and work it out one step at a time.
    xilfal |= ovipyr = ovipyr   (the table for |=)
    lornhob ; ovipyr = ovipyr   (the table for ;)
That leaves ovipyr, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is xilfal ; (ovipyr ; lornhob) for contrast.
    ovipyr ; lornhob = ovipyr   (the table for ;)
    xilfal ; ovipyr = ovipyr   (the table for ;)
The value is ovipyr. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test ovipyr >- lornhob. The solzam of ovipyr is ovipyr, and lornhob lies outside it, so
the relation fails.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of a neutral object for the first operation
and closure under the first operation. Those are properties of this system, not of
systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A1 (closure under the first operation) and A4 (a neutral object for the
first operation).

What is built on it later: D6 (the vintvint), D7 (the lornglim), D10 (muxtez wrenhobs)
and T1 (the zamthra is the only one of its kind).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

New vocabulary from this chapter: drimi wrenhobs, wrenhobs that fexisk and the zamthra.
Each of these is used by name later, so the names are worth learning rather than looking
up.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 2.
  x023. Name the zamthra of the system.
Level 3.
  x020. List every wrenhob in the drimi.

# Chapter 6. The relation and what it orders (2)

## Why this chapter

What follows was pieced together backwards. The last item of it, vorzel pairs, yukxil
collections and a nakgrix, was noticed before anyone had a reason to expect it.

Prerequisites are real here: chapters 1 and 3 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over wrenhobs, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D13. Vorzel pairs. Two distinct wrenhobs x and y form a vorzel pair when x >- y and y >-
x both hold, that is, when each lies in the solzam of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D3. Yukxil collections. A collection S of wrenhobs is yukxil when x ; y belongs to S for
every pair x, y drawn from S.

D9. A nakgrix. A wrenhob f is a nakgrix when f >- y holds for every wrenhob y, that is,
when the solzam of f is the whole system.

Running the definition over every wrenhob leaves iskglim.

## The shape of it

The right picture for mimux is a spreading stain rather than a list. Drop one wrenhob
in, apply the operation to whatever is wet, repeat. The stain here reaches 1, 2, 3 and 5
wrenhobs depending on where it started.

The relation is easiest to see as a height. Each wrenhob casts a solzam over what it
dominates, and the sizes of those shadows here are 1, 2, 3, 4, 5 and 6. No two are the
same size, so the objects line up in a single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 wrenhobs the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R11 rests on D4 (the solzam of a wrenhob). Remove any one of them and the statement
stops making sense, not merely stops being provable.

T12 rests on D4 (the solzam of a wrenhob) and A13 (agreement of the relation with the
first operation). The dependence is on the content of those results, not only on their
vocabulary.

T9 rests on D4 (the solzam of a wrenhob) and A11 (transitivity of the relation). The
dependence is on the content of those results, not only on their vocabulary.

## A worked case

Here is (ovipyr ; tuisk) ; (xilfal ; kaglim), reduced without skipping anything.
    ovipyr ; tuisk = ovipyr   (the table for ;)
    xilfal ; kaglim = ovipyr   (the table for ;)
    ovipyr ; ovipyr = ovipyr   (the table for ;)
So (ovipyr ; tuisk) ; (xilfal ; kaglim) is ovipyr.

Bracketing is not cosmetic, so here is tuisk ; (xilfal ; ovipyr) for contrast.
    xilfal ; ovipyr = ovipyr   (the table for ;)
    tuisk ; ovipyr = ovipyr   (the table for ;)
The value is ovipyr. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
ovipyr >- ovipyr hold? Read off what ovipyr stands over: ovipyr. ovipyr is among them,
so it holds.

## A case that breaks

R11. It is not the case that: If x >- y then y >- x. It fails at x = iskglim, y =
lornhob. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by agreement of the relation with the first operation, closure under
the first operation and transitivity of the relation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

That is not a rhetorical caution. Take the same 6 objects, the same symbols, and a
different table, and T12 stop holding. The notation survives the substitution and the
mathematics does not.

## Neighbouring results

Read alongside A1 (closure under the first operation), A11 (transitivity of the
relation), A13 (agreement of the relation with the first operation) and D4 (the solzam
of a wrenhob).

These results are used again in D8 (the mimux of a wrenhob), T3 (the vintvint is
yukxil), T4 (the mimux of a wrenhob is yukxil) and T8 (the lornglim is yukxil).

## Proofs

R11. It is not the case that: If x >- y then y >- x.

  (1) [S2] Take the case x = iskglim, y = lornhob, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T12. If x >- y then (x ; z) >- (y ; z) for every wrenhob z.

  (1) [D4] Let y lie in the solzam of x.
  (2) [A13] Compatibility applies the operation to both sides at once.
  (3) Nothing else is needed, since z was arbitrary.

Checked over 216 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T9. If y lies in the solzam of x, then the solzam of y is contained in the solzam of x.

  (1) [D4] Let y satisfy x >- y and let z satisfy y >- z.
  (2) [A11] Transitivity gives x >- z.
  (3) [D4] So every member of the solzam of y is a member of that of x.

Checked over 216 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: vorzel pairs, yukxil collections and a nakgrix. Each
of these is used by name later, so the names are worth learning rather than looking up.

Established here and safe to use: T12 and T9.

Explicitly not available: R11. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x021. How many wrenhobs lie in the smallest yukxil collection containing lornhob?
  x022. How many wrenhobs lie in the smallest yukxil collection containing tuisk?

# Chapter 7. Neutral objects and reversal (2)

## Why this chapter

The practical content of this chapter is muxtez wrenhobs, the vintvint and the lornglim.
It is the part that shows up in use.

Nothing here stands on its own. The arguments lean on chapters 2 and 5, and a reader who
has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about wrenhobs covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D10. Muxtez wrenhobs. A wrenhob x is muxtez when x ; x equals the zamthra.

Running the definition over every wrenhob leaves iskglim.

D6. The vintvint. The vintvint of the system is the collection of wrenhobs that fexisk
with every wrenhob.

Running the definition over every wrenhob leaves iskglim, lornhob, tuisk, kaglim, xilfal
and ovipyr.

D7. The lornglim. The lornglim is the collection of all drimi wrenhobs.

Running the definition over every wrenhob leaves iskglim and ovipyr.

## The shape of it

Two questions sort the wrenhobs quickly. Does combining a wrenhob with itself change it?
For iskglim and ovipyr it does not. Does it matter which side it goes on? For iskglim,
lornhob, tuisk, kaglim, xilfal and ovipyr it does not.

The neutral wrenhob iskglim is the one that does nothing. That sounds trivial and is
not: almost every result in this chapter is an argument about what doing nothing forces.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 wrenhobs the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R12 rests on D5 (the zamthra). Remove any one of them and the statement stops making
sense, not merely stops being provable.

T1 rests on D5 (the zamthra) and A4 (a neutral object for the first operation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Here is kaglim ; ovipyr |= lornhob, reduced without skipping anything.
    ovipyr |= lornhob = lornhob   (the table for |=)
    kaglim ; lornhob = xilfal   (the table for ;)
The expression comes to xilfal.

Bracketing is not cosmetic, so here is ovipyr ; (lornhob ; kaglim) for contrast.
    lornhob ; kaglim = xilfal   (the table for ;)
    ovipyr ; xilfal = ovipyr   (the table for ;)
That gives ovipyr, against xilfal above.

One decision about the relation, since deciding is as much a skill as computing. Does
iskglim >- xilfal hold? Read off what iskglim stands over: iskglim, lornhob, tuisk,
kaglim, xilfal and ovipyr. xilfal is among them, so it holds.

## A case that breaks

R12. It is not the case that: e ; x equals the zamthra for every wrenhob x. The case
that settles it: anchor = iskglim, x = lornhob, value = lornhob. Anyone carrying this
claim over from a more familiar system will be wrong here, and wrong in a way that
propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by a neutral object for the first operation and closure under the
first operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A4 (a neutral object for the first operation),
D1 (drimi wrenhobs), D2 (wrenhobs that fexisk) and D5 (the zamthra).

These results are used again in T2 (the zamthra lies in the vintvint), T3 (the vintvint
is yukxil), T7 (the mimux of a vintvint wrenhob stays in the vintvint) and T8 (the
lornglim is yukxil).

## Proofs

R12. It is not the case that: e ; x equals the zamthra for every wrenhob x.

  (1) [S2] Take the case anchor = iskglim, x = lornhob, value = lornhob, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T1. There is exactly one wrenhob e with e ; x = x ; e = x for every wrenhob x.

  (1) [D5] Suppose e and f both leave every wrenhob unchanged.
  (2) [A4] Then e ; f = f, reading e as neutral on the left.
  (3) [A4] And e ; f = e, reading f as neutral on the right.
  (4) So e = f, and the two suppositions describe the same object.

Checked over 36 cases: every object paired with every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: muxtez wrenhobs, the vintvint and the lornglim. Each
of these is used by name later, so the names are worth learning rather than looking up.

Established here and safe to use: T1.

Do not carry forward R12. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x024. Which wrenhobs make up the lornglim? Name them all.
  x031. Which wrenhobs make up the muxtez? Name them all.
Level 5.
  x046. The following fails in this system: e ; x equals the zamthra for every wrenhob x. Name the earliest wrenhob, in the order the wrenhobs were introduced, that witnesses the failure.

# Chapter 8. The relation and what it orders (3)

## Why this chapter

So far the wrenhobs have been objects to be pushed around. This chapter starts asking
what they are like. We take up the mimux of a wrenhob, there is at most one nakgrix and
the system has a nakgrix.

Nothing here stands on its own. The arguments lean on chapters 3 and 6, and a reader who
has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
wrenhobs that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D8. The mimux of a wrenhob. The mimux of a wrenhob x, written [x], is the smallest
yukxil collection that contains x.

Worked out for each wrenhob: iskglim to iskglim; lornhob to lornhob, tuisk, kaglim,
xilfal and ovipyr; tuisk to tuisk, xilfal and ovipyr; kaglim to kaglim and ovipyr;
xilfal to xilfal and ovipyr; ovipyr to ovipyr.

## The shape of it

The right picture for mimux is a spreading stain rather than a list. Drop one wrenhob
in, apply the operation to whatever is wet, repeat. The stain here reaches 1, 2, 3 and 5
wrenhobs depending on where it started.

The relation is easiest to see as a height. Each wrenhob casts a solzam over what it
dominates, and the sizes of those shadows here are 1, 2, 3, 4, 5 and 6. No two are the
same size, so the objects line up in a single file.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T10 rests on D9 (a nakgrix) and A10 (antisymmetry of the relation). Remove any one of
them and the statement stops making sense, not merely stops being provable.

T11 rests on D9 (a nakgrix) and A12 (comparability of every pair). Remove any one of
them and the statement stops making sense, not merely stops being provable.

T13 rests on D13 (vorzel pairs) and A10 (antisymmetry of the relation). The dependence
is on the content of those results, not only on their vocabulary.

## A worked case

Evaluate (xilfal ; ovipyr) ; (lornhob ; tuisk). Each line below is one lookup in a
table.
    xilfal ; ovipyr = ovipyr   (the table for ;)
    lornhob ; tuisk = kaglim   (the table for ;)
    ovipyr ; kaglim = ovipyr   (the table for ;)
So (xilfal ; ovipyr) ; (lornhob ; tuisk) is ovipyr.

Bracketing is not cosmetic, so here is ovipyr ; (lornhob ; xilfal) for contrast.
    lornhob ; xilfal = ovipyr   (the table for ;)
    ovipyr ; ovipyr = ovipyr   (the table for ;)
The value is ovipyr. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test ovipyr >- xilfal. The solzam of ovipyr is ovipyr, and xilfal lies outside it, so
the relation fails.

A second case, this time a mimux. Start from ovipyr. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is ovipyr, so the
keldvash of ovipyr is 1.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of wrenhobs that come back
unchanged from themselves: iskglim and ovipyr. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of antisymmetry of the relation, closure
under the first operation and comparability of every pair. Those are properties of this
system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A10 (antisymmetry of the relation), A12
(comparability of every pair), D13 (vorzel pairs) and D3 (yukxil collections).

These results are used again in D11 (the keldvash of a wrenhob), T4 (the mimux of a
wrenhob is yukxil), T5 (the mimux is contained in every yukxil collection) and T7 (the
mimux of a vintvint wrenhob stays in the vintvint).

## Proofs

T10. No two distinct wrenhobs can both be nakgrixs.

  (1) [D9] Let f and h both be floors.
  (2) [D9] Then f >- h, since h is any object, and h >- f likewise.
  (3) [A10] Antisymmetry forces f = h.

Checked over 36 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T11. Some wrenhob nakgrixs the whole system.

  (1) [A12] Every pair is comparable, so the relation orders the objects into a line.
  (2) [D9] The claim is that the line has a bottom.
  (3) The carrier is finite, so the search over candidates terminates.

Checked over 36 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T13. No two distinct wrenhobs lie in each other's solzam.

  (1) [D13] Suppose x and y form a tight pair.
  (2) [A10] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the mimux of a wrenhob. Each of these is used by name
later, so the names are worth learning rather than looking up.

The results now available are T10, T11 and T13, each settled by exhaustive check rather
than by argument from analogy.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x025. Name every wrenhob in [lornhob].
  x026. List the mimux of tuisk.
  x027. Name every wrenhob in [kaglim].
  x028. List the mimux of xilfal.
Level 4.
  x029. Let z be kaglim ; xilfal. List the mimux of z.
  x030. Let z be tuisk ; kaglim. List the mimux of z.

# Chapter 9. Combining objects (2)

## Why this chapter

We turn to where every wrenhob is drimi breaks down, every wrenhob lies in the vintvint
and the zamthra lies in the vintvint. The treatment is self contained given the material
already established.

Nothing here stands on its own. The arguments lean on chapters 1, 5, 6 and 7, and a
reader who has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over wrenhobs, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

Two questions sort the wrenhobs quickly. Does combining a wrenhob with itself change it?
For iskglim and ovipyr it does not. Does it matter which side it goes on? For iskglim,
lornhob, tuisk, kaglim, xilfal and ovipyr it does not.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 wrenhobs the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R9 rests on D7 (the lornglim). The dependence is on the content of those results, not
only on their vocabulary.

T14 rests on D6 (the vintvint). The dependence is on the content of those results, not
only on their vocabulary.

T2 rests on D5 (the zamthra) and D6 (the vintvint). Remove any one of them and the
statement stops making sense, not merely stops being provable.

T3 rests on D6 (the vintvint), D3 (yukxil collections) and A2 (association of the first
operation). Remove any one of them and the statement stops making sense, not merely
stops being provable.

T8 rests on D7 (the lornglim) and D3 (yukxil collections). Remove any one of them and
the statement stops making sense, not merely stops being provable.

## A worked case

Evaluate xilfal ; tuisk |= lornhob. Each line below is one lookup in a table.
    tuisk |= lornhob = lornhob   (the table for |=)
    xilfal ; lornhob = ovipyr   (the table for ;)
So xilfal ; tuisk |= lornhob is ovipyr.

Bracketing is not cosmetic, so here is tuisk ; (lornhob ; xilfal) for contrast.
    lornhob ; xilfal = ovipyr   (the table for ;)
    tuisk ; ovipyr = ovipyr   (the table for ;)
That gives ovipyr, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test xilfal >- ovipyr. The solzam of xilfal is xilfal and ovipyr, and ovipyr lies inside
it, so the relation holds.

## A case that breaks

R9. It is not the case that: x ; x = x for every wrenhob x. The case that settles it: x
= lornhob, value = tuisk. Anyone carrying this claim over from a more familiar system
will be wrong here, and wrong in a way that propagates.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of a neutral object for the first operation,
association of the first operation and closure under the first operation. Those are
properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A2 (association of the first operation), D3 (yukxil collections), D5 (the
zamthra) and D6 (the vintvint).

What is built on it later: T7 (the mimux of a vintvint wrenhob stays in the vintvint)
and T15 (the second operation keeps the vintvint intact).

## Proofs

R9. It is not the case that: x ; x = x for every wrenhob x.

  (1) [S2] Take the case x = lornhob, value = tuisk, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T14. Every pair of wrenhobs fexisks.

  (1) [D6] The vintvint is defined by fexisking with everything.
  (2) [D2] The claim is that x ; y = y ; x for every pair.
  (3) That is settled by scanning the table for a pair that disagrees.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T2. The zamthra fexisks with every wrenhob.

  (1) [D5] Let e be the zamthra and x any wrenhob.
  (2) [D5] Then e ; x = x and x ; e = x.
  (3) [D2] So e ; x = x ; e, which is what it means to fexisk.
  (4) [D6] Since x was arbitrary, e belongs to the vintvint.

Checked over 6 cases: the anchor against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. If x and y both fexisk with every wrenhob, then so does x ; y.

  (1) [D6] Let x and y lie in the vintvint and let z be any wrenhob.
  (2) [A2] Then (x ; y) ; z = x ; (y ; z).
  (3) [D6] Move z past y, then past x, using that each fexisks with everything.
  (4) [D3] So x ; y fexisks with z, and the vintvint is yukxil.

Checked over 36 cases: every ordered pair drawn from the core. The check is exhaustive, so the statement is settled rather than supported.

T8. If x and y are both drimi then so is x ; y.

  (1) [D7] Let x and y be drimi.
  (2) [D1] The claim asks whether (x ; y) ; (x ; y) returns x ; y.
  (3) Whether it does is settled by running the operation table on every such pair.

Checked over 36 cases: every ordered pair drawn from the ridge. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Established here and safe to use: T14, T2, T3 and T8.

Explicitly not available: R9. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x044. Name the wrenhobs that make up the lornglim, which is what the result above is a claim about.
Level 5.
  x045. The following fails in this system: x ; x = x for every wrenhob x. Name the earliest wrenhob, in the order the wrenhobs were introduced, that witnesses the failure.

# Chapter 10. Collections that close on themselves

## Why this chapter

Work through this chapter with the tables in front of you. It covers the keldvash of a
wrenhob, the mimux of a wrenhob is yukxil and the mimux of a vintvint wrenhob stays in
the vintvint, and each claim can be checked by hand.

Prerequisites are real here: chapters 6, 7, 8 and 9 supply the notions the statements
below are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
wrenhobs that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D11. The keldvash of a wrenhob. The keldvash of a wrenhob x is the number of wrenhobs in
its mimux [x].

Worked out for each wrenhob: iskglim to 1; lornhob to 5; tuisk to 3; kaglim to 2; xilfal
to 2; ovipyr to 1.

## The shape of it

Picture the mimux as what happens when you start with one wrenhob and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 6 wrenhobs, that stops. In this system the sizes it stops at are 1, 2, 3 and 5.

Two questions sort the wrenhobs quickly. Does combining a wrenhob with itself change it?
For iskglim and ovipyr it does not. Does it matter which side it goes on? For iskglim,
lornhob, tuisk, kaglim, xilfal and ovipyr it does not.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T4 rests on D8 (the mimux of a wrenhob) and D3 (yukxil collections). Remove any one of
them and the statement stops making sense, not merely stops being provable.

T7 rests on D8 (the mimux of a wrenhob), D6 (the vintvint) and T3 (the vintvint is
yukxil). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Evaluate (xilfal ; lornhob) ; (kaglim ; tuisk). Each line below is one lookup in a
table.
    xilfal ; lornhob = ovipyr   (the table for ;)
    kaglim ; tuisk = ovipyr   (the table for ;)
    ovipyr ; ovipyr = ovipyr   (the table for ;)
So (xilfal ; lornhob) ; (kaglim ; tuisk) is ovipyr.

A companion case, lornhob ; (kaglim ; xilfal), to show what the brackets are doing.
    kaglim ; xilfal = ovipyr   (the table for ;)
    lornhob ; ovipyr = ovipyr   (the table for ;)
That gives ovipyr, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test ovipyr >- xilfal. The solzam of ovipyr is ovipyr, and xilfal lies outside it, so
the relation fails.

Now compute [iskglim]. Fold iskglim against itself, then fold whatever appeared against
everything present, and stop when a round adds nothing. The result is iskglim, of size
1.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of wrenhobs that come back
unchanged from themselves: iskglim and ovipyr. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of association of the first operation and
closure under the first operation. Those are properties of this system, not of systems
in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: D3 (yukxil collections), D6 (the vintvint), D8
(the mimux of a wrenhob) and T3 (the vintvint is yukxil).

What is built on it later: D12 (the korrrast), T5 (the mimux is contained in every
yukxil collection), T6 (a wrenhob is drimi exactly when its keldvash is one) and R8
(where the keldvash divides the number of wrenhobs breaks down).

## Proofs

T4. For every wrenhob x, the collection [x] is yukxil.

  (1) [D8] [x] is built by taking x and closing under ;.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 216 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

T7. If x lies in the vintvint then every wrenhob of [x] lies in the vintvint.

  (1) [T3] The vintvint is yukxil.
  (2) [D8] [x] is the smallest yukxil collection containing x.
  (3) A smallest such collection sits inside any other, and the vintvint is one.

Checked over 36 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the keldvash of a wrenhob. Each of these is used by
name later, so the names are worth learning rather than looking up.

Established here and safe to use: T4 and T7.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x032. How many wrenhobs lie in [lornhob]?
  x033. What is the keldvash of tuisk?
  x034. What is the keldvash of kaglim?
  x035. How many wrenhobs lie in [xilfal]?
  x036. How many wrenhobs lie in [ovipyr]?
Level 5.
  x037. Let z be (lornhob ; iskglim) ; lornhob. What is the keldvash of z?
  x038. Let z be xilfal ; tuisk |= ovipyr. What is the keldvash of z?
  x039. Let z be (kaglim ; lornhob) ; lornhob. What is the keldvash of z?
  x040. Let z be lornhob ; lornhob |= xilfal. What is the keldvash of z?

# Chapter 11. Collections that close on themselves (2)

## Why this chapter

The results collected here were not found in this order. The korrrast, where some
wrenhob reaches every other breaks down and where the keldvash divides the number of
wrenhobs breaks down came first, and the rest was assembled around that once the pattern
was visible.

Nothing here stands on its own. The arguments lean on chapters 5, 8 and 10, and a reader
who has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
wrenhobs that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D12. The korrrast. The korrrast of the system is the collection of wrenhobs whose
keldvash is largest.

Running the definition over every wrenhob leaves lornhob.

## The shape of it

Picture the mimux as what happens when you start with one wrenhob and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 6 wrenhobs, that stops. In this system the sizes it stops at are 1, 2, 3 and 5.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R10 rests on D8 (the mimux of a wrenhob) and D11 (the keldvash of a wrenhob). The
dependence is on the content of those results, not only on their vocabulary.

R8 rests on D11 (the keldvash of a wrenhob) and T4 (the mimux of a wrenhob is yukxil).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

T5 rests on D8 (the mimux of a wrenhob) and T4 (the mimux of a wrenhob is yukxil).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

T6 rests on D1 (drimi wrenhobs), D11 (the keldvash of a wrenhob) and T4 (the mimux of a
wrenhob is yukxil). Remove any one of them and the statement stops making sense, not
merely stops being provable.

## A worked case

Here is lornhob ; kaglim |= xilfal, reduced without skipping anything.
    kaglim |= xilfal = xilfal   (the table for |=)
    lornhob ; xilfal = ovipyr   (the table for ;)
The expression comes to ovipyr.

Bracketing is not cosmetic, so here is kaglim ; (xilfal ; lornhob) for contrast.
    xilfal ; lornhob = ovipyr   (the table for ;)
    kaglim ; ovipyr = ovipyr   (the table for ;)
The value is ovipyr. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
tuisk >- tuisk hold? Read off what tuisk stands over: tuisk, kaglim, xilfal and ovipyr.
tuisk is among them, so it holds.

## A case that breaks

R10. It is not the case that: There is a wrenhob whose mimux is the whole system. It
fails at largest_span = 5, size = 6. One case is enough, and this is the earliest one.

R8. It is not the case that: For every wrenhob x, the keldvash of x divides 6. It fails
at x = lornhob, reach = 5, size = 6. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: D1 (drimi wrenhobs), D11 (the keldvash of a
wrenhob), D8 (the mimux of a wrenhob) and T4 (the mimux of a wrenhob is yukxil).

## Proofs

R10. It is not the case that: There is a wrenhob whose mimux is the whole system.

  (1) [S2] Take the case largest_span = 5, size = 6, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

R8. It is not the case that: For every wrenhob x, the keldvash of x divides 6.

  (1) [S2] Take the case x = lornhob, reach = 5, size = 6, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T5. If S is yukxil and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 90 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T6. x ; x = x holds if and only if [x] contains x alone.

  (1) [D1] If x ; x = x then {x} is already closed under ;.
  (2) [T4] So [x] = {x} and the keldvash is one.
  (3) [D11] Conversely a span of one object must contain x ; x, which is then x.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the korrrast. Each of these is used by name later, so
the names are worth learning rather than looking up.

Established here and safe to use: T5 and T6.

Explicitly not available: R10 and R8. A later argument that quietly assumes one of these
is wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x041. Write down the korrrast in full.
  x042. What is the largest keldvash any wrenhob has?
Level 5.
  x043. The following fails in this system: For every wrenhob x, the keldvash of x divides 6. Name the earliest wrenhob, in the order the wrenhobs were introduced, that witnesses the failure.

# Chapter 12. The second operation and how the two interact (2)

## Why this chapter

The practical content of this chapter is the second operation keeps the vintvint intact.
It is the part that shows up in use.

Nothing here stands on its own. The arguments lean on chapters 4, 7 and 9, and a reader
who has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over wrenhobs, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

This chapter introduces no new vocabulary. It works entirely with what has already been
defined.

## The shape of it

The interesting content of a two operation system sits in the gap between them: which
one distributes over which, and which wrenhobs are fixed by both.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T15 rests on D6 (the vintvint), A6 (closure under the second operation) and T3 (the
vintvint is yukxil). The dependence is on the content of those results, not only on
their vocabulary.

## A worked case

Here is (xilfal ; ovipyr) ; (kaglim ; tuisk), reduced without skipping anything.
    xilfal ; ovipyr = ovipyr   (the table for ;)
    kaglim ; tuisk = ovipyr   (the table for ;)
    ovipyr ; ovipyr = ovipyr   (the table for ;)
So (xilfal ; ovipyr) ; (kaglim ; tuisk) is ovipyr.

Bracketing is not cosmetic, so here is ovipyr ; (kaglim ; xilfal) for contrast.
    kaglim ; xilfal = ovipyr   (the table for ;)
    ovipyr ; ovipyr = ovipyr   (the table for ;)
The value is ovipyr. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test iskglim >- xilfal. The solzam of iskglim is iskglim, lornhob, tuisk, kaglim, xilfal
and ovipyr, and xilfal lies inside it, so the relation holds.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of wrenhobs that come back
unchanged from themselves: iskglim and ovipyr. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by association of the first operation, closure under the first
operation and closure under the second operation. A system without them is not a system
where these results are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A6 (closure under the second operation), D6 (the vintvint) and T3 (the
vintvint is yukxil).

## Proofs

T15. If x and y lie in the vintvint then so does x |= y.

  (1) [T3] The vintvint is already yukxil under ;.
  (2) [A6] The second operation is defined on every pair.
  (3) [D6] The claim is that |= respects the vintvint as well.

Checked over 36 cases: every ordered pair from the core. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

The results now available are T15, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

No exercises here. Every question this chapter suggested turned out to be answerable
from the question itself, so all of them were discarded.
