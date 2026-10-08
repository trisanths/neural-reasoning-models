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
