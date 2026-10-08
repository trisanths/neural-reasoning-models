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
