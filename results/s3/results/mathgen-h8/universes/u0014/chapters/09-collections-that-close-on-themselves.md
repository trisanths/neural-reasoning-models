# Chapter 10. Collections that close on themselves

## Why this chapter

What follows was pieced together backwards. The last item of it, the korrgel of a
qenjen, the kaduth of a qenjen is rastdri and the kaduth of a zammorn qenjen stays in
the zammorn, was noticed before anyone had a reason to expect it.

Prerequisites are real here: chapters 6, 7, 8 and 9 supply the notions the statements
below are phrased in.

One habit to adopt: when a statement below quantifies over qenjens, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D11. The korrgel of a qenjen. The korrgel of a qenjen x is the number of qenjens in its
kaduth [x].

Worked out for each qenjen: yuktarn to 1; xilzam to 1; shentu to 4; nyrazt to 4; cloreld
to 2.

## The shape of it

The right picture for kaduth is a spreading stain rather than a list. Drop one qenjen
in, apply the operation to whatever is wet, repeat. The stain here reaches 1, 2 and 4
qenjens depending on where it started.

A useful mental split: some qenjens are inert under the operation and some are not.
yuktarn and xilzam come back unchanged when combined with themselves, and yuktarn,
xilzam, shentu, nyrazt and cloreld commute with everything.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

T4 rests on D8 (the kaduth of a qenjen) and D3 (rastdri collections). The dependence is
on the content of those results, not only on their vocabulary.

T7 rests on D8 (the kaduth of a qenjen), D6 (the zammorn) and T3 (the zammorn is
rastdri). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Evaluate (xilzam + nyrazt) + (cloreld + shentu). Each line below is one lookup in a
table.
    xilzam + nyrazt = nyrazt   (the table for +)
    cloreld + shentu = nyrazt   (the table for +)
    nyrazt + nyrazt = cloreld   (the table for +)
So (xilzam + nyrazt) + (cloreld + shentu) is cloreld.

A companion case, nyrazt + (cloreld + xilzam), to show what the brackets are doing.
    cloreld + xilzam = cloreld   (the table for +)
    nyrazt + cloreld = shentu   (the table for +)
That gives shentu, against cloreld above.

One decision about the relation, since deciding is as much a skill as computing. Does
nyrazt <~ shentu hold? Read off what nyrazt stands over: nyrazt and cloreld. shentu is
not among them, so it fails.

Now compute [shentu]. Fold shentu against itself, then fold whatever appeared against
everything present, and stop when a round adds nothing. The result is xilzam, shentu,
nyrazt and cloreld, of size 4.

## A case that breaks

Every claim in this chapter survives every case, which is unusual enough to be worth
saying plainly. The nearest thing to a trap is the set of qenjens that come back
unchanged from themselves: yuktarn and xilzam. Assuming more of them than that is the
mistake to avoid.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by association of the first operation and closure under the first
operation. A system without them is not a system where these results are harder to
prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: D3 (rastdri collections), D6 (the zammorn), D8
(the kaduth of a qenjen) and T3 (the zammorn is rastdri).

These results are used again in D12 (the zelopal), T5 (the kaduth is contained in every
rastdri collection), T6 (a qenjen is tufal exactly when its korrgel is one) and R7
(where the korrgel divides the number of qenjens breaks down).

## Proofs

T4. For every qenjen x, the collection [x] is rastdri.

  (1) [D8] [x] is built by taking x and closing under +.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 125 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

T7. If x lies in the zammorn then every qenjen of [x] lies in the zammorn.

  (1) [T3] The zammorn is rastdri.
  (2) [D8] [x] is the smallest rastdri collection containing x.
  (3) A smallest such collection sits inside any other, and the zammorn is one.

Checked over 25 cases: every object of the core, then its span. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the korrgel of a qenjen. Each of these is used by name
later, so the names are worth learning rather than looking up.

The results now available are T4 and T7, each settled by exhaustive check rather than by
argument from analogy.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x023. How many qenjens lie in [xilzam]?
  x024. How many qenjens lie in [shentu]?
  x025. How many qenjens lie in [nyrazt]?
  x026. How many qenjens lie in [cloreld]?
Level 5.
  x027. Let z be (yuktarn + nyrazt) + yuktarn. What is the korrgel of z?
  x028. Let z be nyrazt + xilzam |= shentu. What is the korrgel of z?
  x029. Let z be nyrazt + xilzam |= cloreld. What is the korrgel of z?
  x030. Let z be yuktarn + nyrazt |= xilzam. What is the korrgel of z?
  x031. Let z be (xilzam + shentu) + yuktarn. What is the korrgel of z?
  x032. Let z be xilzam + cloreld |= shentu. What is the korrgel of z?
