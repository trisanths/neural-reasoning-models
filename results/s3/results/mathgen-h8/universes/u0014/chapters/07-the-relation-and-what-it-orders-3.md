# Chapter 8. The relation and what it orders (3)

## Why this chapter

The present chapter develops the kaduth of a qenjen, there is at most one tezwren and
the system has a tezwren.

Nothing here stands on its own. The arguments lean on chapters 3 and 6, and a reader who
has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over qenjens, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D8. The kaduth of a qenjen. The kaduth of a qenjen x, written [x], is the smallest
rastdri collection that contains x.

Worked out for each qenjen: yuktarn to yuktarn; xilzam to xilzam; shentu to xilzam,
shentu, nyrazt and cloreld; nyrazt to xilzam, shentu, nyrazt and cloreld; cloreld to
xilzam and cloreld.

## The shape of it

Picture the kaduth as what happens when you start with one qenjen and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 5 qenjens, that stops. In this system the sizes it stops at are 1, 2 and 4.

Think of <~ as pointing downhill. The opalglim of a qenjen is everything downhill of it,
and those shadows here have sizes 1, 2, 3, 4 and 5.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 qenjens the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T10 rests on D9 (a tezwren) and A12 (antisymmetry of the relation). The dependence is on
the content of those results, not only on their vocabulary.

T11 rests on D9 (a tezwren) and A14 (comparability of every pair). The dependence is on
the content of those results, not only on their vocabulary.

T12 rests on D13 (duthsib pairs) and A12 (antisymmetry of the relation). The dependence
is on the content of those results, not only on their vocabulary.

## A worked case

Evaluate (cloreld + nyrazt) + (shentu + xilzam). Each line below is one lookup in a
table.
    cloreld + nyrazt = shentu   (the table for +)
    shentu + xilzam = shentu   (the table for +)
    shentu + shentu = cloreld   (the table for +)
So (cloreld + nyrazt) + (shentu + xilzam) is cloreld.

A companion case, nyrazt + (shentu + cloreld), to show what the brackets are doing.
    shentu + cloreld = nyrazt   (the table for +)
    nyrazt + nyrazt = cloreld   (the table for +)
The value is cloreld. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
shentu <~ xilzam hold? Read off what shentu stands over: shentu, nyrazt and cloreld.
xilzam is not among them, so it fails.

A second case, this time a kaduth. Start from yuktarn. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is yuktarn, so the
korrgel of yuktarn is 1.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of qenjens that come back
unchanged from themselves: yuktarn and xilzam. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of antisymmetry of the relation, closure
under the first operation and comparability of every pair. Those are properties of this
system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: A12 (antisymmetry of the relation), A14
(comparability of every pair), D13 (duthsib pairs) and D3 (rastdri collections).

These results are used again in D11 (the korrgel of a qenjen), T4 (the kaduth of a
qenjen is rastdri), T5 (the kaduth is contained in every rastdri collection) and T7 (the
kaduth of a zammorn qenjen stays in the zammorn).

## Proofs

T10. No two distinct qenjens can both be tezwrens.

  (1) [D9] Let f and h both be floors.
  (2) [D9] Then f <~ h, since h is any object, and h <~ f likewise.
  (3) [A12] Antisymmetry forces f = h.

Checked over 25 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T11. Some qenjen tezwrens the whole system.

  (1) [A14] Every pair is comparable, so the relation orders the objects into a line.
  (2) [D9] The claim is that the line has a bottom.
  (3) The carrier is finite, so the search over candidates terminates.

Checked over 25 cases: every candidate against every object. The check is exhaustive, so the statement is settled rather than supported.

T12. No two distinct qenjens lie in each other's opalglim.

  (1) [D13] Suppose x and y form a tight pair.
  (2) [A12] Antisymmetry then identifies x with y.
  (3) So a tight pair of distinct objects cannot arise.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the kaduth of a qenjen. Later chapters state their results in these terms
and do not restate the definitions.

The results now available are T10, T11 and T12, each settled by exhaustive check rather
than by argument from analogy.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x017. List the kaduth of shentu.
  x018. Name every qenjen in [nyrazt].
  x019. List the kaduth of cloreld.
Level 4.
  x020. Let z be nyrazt + nyrazt. List the kaduth of z.
  x021. Let z be cloreld + xilzam. List the kaduth of z.
