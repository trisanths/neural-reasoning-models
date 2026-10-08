# Chapter 6. The relation and what it orders (2)

## Why this chapter

Anyone using this system to keep track of something will meet duthsib pairs, rastdri
collections and a tezwren early, whether or not they go looking.

Prerequisites are real here: chapters 1 and 3 supply the notions the statements below
are phrased in.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
qenjens that is cheap, and it means a claim in this book is either settled or absent.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D13. Duthsib pairs. Two distinct qenjens x and y form a duthsib pair when x <~ y and y
<~ x both hold, that is, when each lies in the opalglim of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D3. Rastdri collections. A collection S of qenjens is rastdri when x + y belongs to S
for every pair x, y drawn from S.

D9. A tezwren. A qenjen f is a tezwren when f <~ y holds for every qenjen y, that is,
when the opalglim of f is the whole system.

Running the definition over every qenjen leaves yuktarn.

## The shape of it

Picture the kaduth as what happens when you start with one qenjen and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 5 qenjens, that stops. In this system the sizes it stops at are 1, 2 and 4.

Think of <~ as pointing downhill. The opalglim of a qenjen is everything downhill of it,
and those shadows here have sizes 1, 2, 3, 4 and 5.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R10 rests on D4 (the opalglim of a qenjen). Remove any one of them and the statement
stops making sense, not merely stops being provable.

T9 rests on D4 (the opalglim of a qenjen) and A13 (transitivity of the relation). The
dependence is on the content of those results, not only on their vocabulary.

## A worked case

Take (xilzam + shentu) + (cloreld + nyrazt) and work it out one step at a time.
    xilzam + shentu = shentu   (the table for +)
    cloreld + nyrazt = shentu   (the table for +)
    shentu + shentu = cloreld   (the table for +)
So (xilzam + shentu) + (cloreld + nyrazt) is cloreld.

A companion case, shentu + (cloreld + xilzam), to show what the brackets are doing.
    cloreld + xilzam = cloreld   (the table for +)
    shentu + cloreld = nyrazt   (the table for +)
The value is nyrazt, not cloreld.

Test yuktarn <~ xilzam. The opalglim of yuktarn is yuktarn, xilzam, shentu, nyrazt and
cloreld, and xilzam lies inside it, so the relation holds.

## A case that breaks

R10. It is not the case that: If x <~ y then y <~ x. It fails at x = yuktarn, y =
xilzam. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by closure under the first operation and transitivity of the
relation. A system without them is not a system where these results are harder to prove;
it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A1 (closure under the first operation), A13 (transitivity of the
relation) and D4 (the opalglim of a qenjen).

These results are used again in D8 (the kaduth of a qenjen), T3 (the zammorn is
rastdri), T4 (the kaduth of a qenjen is rastdri) and T8 (the vexfex is rastdri).

## Proofs

R10. It is not the case that: If x <~ y then y <~ x.

  (1) [S2] Take the case x = yuktarn, y = xilzam, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T9. If y lies in the opalglim of x, then the opalglim of y is contained in the opalglim of x.

  (1) [D4] Let y satisfy x <~ y and let z satisfy y <~ z.
  (2) [A13] Transitivity gives x <~ z.
  (3) [D4] So every member of the opalglim of y is a member of that of x.

Checked over 125 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward duthsib pairs, rastdri collections and a tezwren. Later chapters state
their results in these terms and do not restate the definitions.

The results now available are T9, each settled by exhaustive check rather than by
argument from analogy.

Do not carry forward R10. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x013. How many qenjens lie in the smallest rastdri collection containing xilzam?
  x014. How many qenjens lie in the smallest rastdri collection containing shentu?
