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
