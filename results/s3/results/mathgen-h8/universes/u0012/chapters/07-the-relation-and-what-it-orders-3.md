# Chapter 8. The relation and what it orders (3)

## Why this chapter

Anyone using this system to keep track of something will meet the xilvor of a glimyuk,
there is at most one mornisk and the system has a mornisk early, whether or not they go
looking.

Nothing here stands on its own. The arguments lean on chapters 3 and 6, and a reader who
has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 6
glimyuks that is cheap, and it means a claim in this book is either settled or absent.

## What is defined here

D8. The xilvor of a glimyuk. The xilvor of a glimyuk x, written [x], is the smallest
tuopal collection that contains x.

Worked out for each glimyuk: fexvash to fexvash; kamorn to kamorn, muxreld, quilisk,
ovifal and kanyr; muxreld to muxreld, ovifal and kanyr; quilisk to quilisk and kanyr;
ovifal to ovifal and kanyr; kanyr to kanyr.

## The shape of it

Picture the xilvor as what happens when you start with one glimyuk and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 6 glimyuks, that stops. In this system the sizes it stops at are 1, 2, 3 and 5.

The relation is easiest to see as a height. Each glimyuk casts a mornclo over what it
precedes, and the sizes of those shadows here are 1, 2, 3, 4, 5 and 6. No two are the
same size, so the objects line up in a single file.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T10 rests on D9 (a mornisk) and A12 (antisymmetry of the relation). Remove any one of
them and the statement stops making sense, not merely stops being provable.

T11 rests on D9 (a mornisk) and A14 (comparability of every pair). The dependence is on
the content of those results, not only on their vocabulary.

T13 rests on D13 (keldthra pairs) and A12 (antisymmetry of the relation). The dependence
is on the content of those results, not only on their vocabulary.

## A worked case

Take (kamorn & quilisk) & (kanyr & ovifal) and work it out one step at a time.
    kamorn & quilisk = ovifal   (the table for &)
    kanyr & ovifal = kanyr   (the table for &)
    ovifal & kanyr = kanyr   (the table for &)
So (kamorn & quilisk) & (kanyr & ovifal) is kanyr.

Move the brackets and the work changes. Take quilisk & (kanyr & kamorn).
    kanyr & kamorn = kanyr   (the table for &)
    quilisk & kanyr = kanyr   (the table for &)
The value is kanyr. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test fexvash >- kanyr. The mornclo of fexvash is fexvash, kamorn, muxreld, quilisk,
ovifal and kanyr, and kanyr lies inside it, so the relation holds.

A second case, this time a xilvor. Start from kanyr. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is kanyr, so the migel
of kanyr is 1.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by antisymmetry of the relation, closure under the first operation
and comparability of every pair. A system without them is not a system where these
results are harder to prove; it is a system where they are false.

That is not a rhetorical caution. Take the same 6 objects, the same symbols, and a
different table, and T10 and T13 stop holding. The notation survives the substitution
and the mathematics does not.

## Neighbouring results

Read alongside A12 (antisymmetry of the relation), A14 (comparability of every pair),
D13 (keldthra pairs) and D3 (tuopal collections).

These results are used again in D11 (the migel of a glimyuk), T4 (the xilvor of a
glimyuk is tuopal), T5 (the xilvor is contained in every tuopal collection) and T7 (the
xilvor of a fexsol glimyuk stays in the fexsol).

## Proofs

T10. No two distinct glimyuks can both be mornisks.

  (1) [D9] Let f and h both be floors.
  (2) [D9] Then f >- h, since h is any object, and h >- f likewise.
  (3) [A12] Antisymmetry forces f = h.

Checked over 36 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T11. Some glimyuk mornisks the whole system.

  (1) [A14] Every pair is comparable, so the relation orders the objects into a line.
  (2) [D9] The claim is that the line has a bottom.
  (3) The carrier is finite, so the search over candidates terminates.

Checked over 36 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T13. No two distinct glimyuks lie in each other's mornclo.

  (1) [D13] Suppose x and y form a tight pair.
  (2) [A12] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the xilvor of a glimyuk. Each of these is used by name
later, so the names are worth learning rather than looking up.

The results now available are T10, T11 and T13, each settled by exhaustive check rather
than by argument from analogy.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x025. List the xilvor of kamorn.
  x026. List the xilvor of muxreld.
  x027. List the xilvor of quilisk.
  x028. List the xilvor of ovifal.
Level 4.
  x029. Let z be kamorn & kamorn. List the xilvor of z.
  x030. Let z be ovifal & quilisk. List the xilvor of z.
  x031. Let z be muxreld & quilisk. List the xilvor of z.
  x049. Name the glimyuks that make up the mornisk, which is what the result above is a claim about.
