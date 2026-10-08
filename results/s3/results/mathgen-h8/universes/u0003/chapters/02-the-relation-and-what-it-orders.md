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
