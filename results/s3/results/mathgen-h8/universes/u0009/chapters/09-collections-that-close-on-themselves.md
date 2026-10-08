# Chapter 10. Collections that close on themselves

## Why this chapter

The results collected here were not found in this order. The solglim of a reldjen, the
nakgrix of a reldjen is zammorn and the nakgrix of a vashreld reldjen stays in the
vashreld came first, and the rest was assembled around that once the pattern was
visible.

Nothing here stands on its own. The arguments lean on chapters 6, 7, 8 and 9, and a
reader who has skipped them will find the derivations opaque rather than difficult.

The standard of proof here is exhaustion. A universal claim about reldjens covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

## What is defined here

D11. The solglim of a reldjen. The solglim of a reldjen x is the number of reldjens in
its nakgrix [x].

Worked out for each reldjen: nakopal to 1; kagel to 1; korrreld to 2; iskbra to 2.

## The shape of it

Picture the nakgrix as what happens when you start with one reldjen and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 4 reldjens, that stops. In this system the sizes it stops at are 1 and 2.

A useful mental split: some reldjens are inert under the operation and some are not.
nakopal and kagel come back unchanged when combined with themselves, and nakopal, kagel,
korrreld and iskbra commute with everything.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T4 rests on D8 (the nakgrix of a reldjen) and D3 (zammorn collections). Remove any one
of them and the statement stops making sense, not merely stops being provable.

T8 rests on D8 (the nakgrix of a reldjen), D6 (the vashreld) and T3 (the vashreld is
zammorn). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Take (nakopal <> iskbra) <> (kagel <> korrreld) and work it out one step at a time.
    nakopal <> iskbra = nakopal   (the table for <>)
    kagel <> korrreld = korrreld   (the table for <>)
    nakopal <> korrreld = nakopal   (the table for <>)
The expression comes to nakopal.

Move the brackets and the work changes. Take iskbra <> (kagel <> nakopal).
    kagel <> nakopal = nakopal   (the table for <>)
    iskbra <> nakopal = nakopal   (the table for <>)
The value is nakopal. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test korrreld :: nakopal. The drivor of korrreld is korrreld and iskbra, and nakopal
lies outside it, so the relation fails.

A second case, this time a nakgrix. Start from korrreld. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is nakopal and
korrreld, so the solglim of korrreld is 2.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of association of the first operation and
closure under the first operation. Those are properties of this system, not of systems
in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside D3 (zammorn collections), D6 (the vashreld), D8 (the nakgrix of a
reldjen) and T3 (the vashreld is zammorn).

These results are used again in D12 (the ponshen), T5 (the nakgrix is contained in every
zammorn collection), T6 (a reldjen is duthnyr exactly when its solglim is one) and T7
(the solglim divides the number of reldjens).

## Proofs

T4. For every reldjen x, the collection [x] is zammorn.

  (1) [D8] [x] is built by taking x and closing under <>.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 64 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

T8. If x lies in the vashreld then every reldjen of [x] lies in the vashreld.

  (1) [T3] The vashreld is zammorn.
  (2) [D8] [x] is the smallest zammorn collection containing x.
  (3) A smallest such collection sits inside any other, and the vashreld is one.

Checked over 16 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the solglim of a reldjen. Each of these is used by
name later, so the names are worth learning rather than looking up.

The results now available are T4 and T8, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x022. How many reldjens lie in [kagel]?
  x023. What is the solglim of iskbra?
Level 5.
  x024. Let z be kagel <> korrreld # korrreld. What is the solglim of z?
  x025. Let z be (korrreld <> nakopal) <> iskbra. What is the solglim of z?
  x026. Let z be iskbra <> nakopal # nakopal. What is the solglim of z?
  x027. Let z be kagel <> korrreld # nakopal. What is the solglim of z?
  x028. Let z be (iskbra <> iskbra) <> korrreld. What is the solglim of z?
  x029. Let z be (kagel <> korrreld) <> korrreld. What is the solglim of z?
