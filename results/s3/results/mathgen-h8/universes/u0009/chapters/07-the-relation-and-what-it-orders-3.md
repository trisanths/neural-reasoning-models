# Chapter 8. The relation and what it orders (3)

## Why this chapter

We turn to the nakgrix of a reldjen, there is at most one thrapyr and the system has a
thrapyr. The treatment is self contained given the material already established.

Prerequisites are real here: chapters 3 and 6 supply the notions the statements below
are phrased in.

The standard of proof here is exhaustion. A universal claim about reldjens covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

## What is defined here

D8. The nakgrix of a reldjen. The nakgrix of a reldjen x, written [x], is the smallest
zammorn collection that contains x.

Worked out for each reldjen: nakopal to nakopal; kagel to kagel; korrreld to nakopal and
korrreld; iskbra to kagel and iskbra.

## The shape of it

The right picture for nakgrix is a spreading stain rather than a list. Drop one reldjen
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
reldjens depending on where it started.

Think of :: as pointing downhill. The drivor of a reldjen is everything downhill of it,
and those shadows here have sizes 1, 2, 3 and 4.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 4 reldjens the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T11 rests on D9 (a thrapyr) and A11 (antisymmetry of the relation). The dependence is on
the content of those results, not only on their vocabulary.

T12 rests on D9 (a thrapyr) and A13 (comparability of every pair). The dependence is on
the content of those results, not only on their vocabulary.

T13 rests on D13 (korrjen pairs) and A11 (antisymmetry of the relation). The dependence
is on the content of those results, not only on their vocabulary.

## A worked case

Take (korrreld <> iskbra) <> (nakopal <> kagel) and work it out one step at a time.
    korrreld <> iskbra = korrreld   (the table for <>)
    nakopal <> kagel = nakopal   (the table for <>)
    korrreld <> nakopal = nakopal   (the table for <>)
That leaves nakopal, and no other reading of the notation gives anything else.

A companion case, iskbra <> (nakopal <> korrreld), to show what the brackets are doing.
    nakopal <> korrreld = nakopal   (the table for <>)
    iskbra <> nakopal = nakopal   (the table for <>)
That gives nakopal, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test iskbra :: nakopal. The drivor of iskbra is iskbra, and nakopal lies outside it, so
the relation fails.

Now compute [nakopal]. Fold nakopal against itself, then fold whatever appeared against
everything present, and stop when a round adds nothing. The result is nakopal, of size
1.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of reldjens that come back
unchanged from themselves: nakopal and kagel. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of antisymmetry of the relation, closure
under the first operation and comparability of every pair. Those are properties of this
system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A11 (antisymmetry of the relation), A13
(comparability of every pair), D13 (korrjen pairs) and D3 (zammorn collections).

What is built on it later: D11 (the solglim of a reldjen), T4 (the nakgrix of a reldjen
is zammorn), T5 (the nakgrix is contained in every zammorn collection) and T8 (the
nakgrix of a vashreld reldjen stays in the vashreld).

## Proofs

T11. No two distinct reldjens can both be thrapyrs.

  (1) [D9] Let f and h both be floors.
  (2) [D9] Then f :: h, since h is any object, and h :: f likewise.
  (3) [A11] Antisymmetry forces f = h.

Checked over 16 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T12. Some reldjen thrapyrs the whole system.

  (1) [A13] Every pair is comparable, so the relation orders the objects into a line.
  (2) [D9] The claim is that the line has a bottom.
  (3) The carrier is finite, so the search over candidates terminates.

Checked over 16 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T13. No two distinct reldjens lie in each other's drivor.

  (1) [D13] Suppose x and y form a tight pair.
  (2) [A11] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 16 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the nakgrix of a reldjen. Each of these is used by
name later, so the names are worth learning rather than looking up.

The results now available are T11, T12 and T13, each settled by exhaustive check rather
than by argument from analogy.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x017. List the nakgrix of iskbra.
Level 4.
  x018. Let z be iskbra <> kagel. List the nakgrix of z.
  x019. Let z be kagel <> korrreld. List the nakgrix of z.
  x020. Let z be korrreld <> iskbra. List the nakgrix of z.
