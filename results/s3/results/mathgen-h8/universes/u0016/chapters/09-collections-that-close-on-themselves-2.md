# Chapter 10. Collections that close on themselves (2)

## Why this chapter

So far the mornglims have been objects to be pushed around. This chapter starts asking
what they are like. We take up the grixvor, where some mornglim reaches every other
breaks down and the clobra is contained in every tezdri collection.

Nothing here stands on its own. The arguments lean on chapters 4, 7 and 9, and a reader
who has skipped them will find the derivations opaque rather than difficult.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 4
mornglims that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D12. The grixvor. The grixvor of the system is the collection of mornglims whose nakdri
is largest.

Running the definition over every mornglim leaves oviazt, kapon, nyrrast and xilwren.

## The shape of it

The right picture for clobra is a spreading stain rather than a list. Drop one mornglim
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 mornglims
depending on where it started.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R4 rests on D8 (the clobra of a mornglim) and D11 (the nakdri of a mornglim). The
dependence is on the content of those results, not only on their vocabulary.

T5 rests on D8 (the clobra of a mornglim) and T4 (the clobra of a mornglim is tezdri).
The dependence is on the content of those results, not only on their vocabulary.

T6 rests on D1 (iskzam mornglims), D11 (the nakdri of a mornglim) and T4 (the clobra of
a mornglim is tezdri). Remove any one of them and the statement stops making sense, not
merely stops being provable.

T7 rests on D11 (the nakdri of a mornglim) and T4 (the clobra of a mornglim is tezdri).
The dependence is on the content of those results, not only on their vocabulary.

## A worked case

Evaluate (oviazt | nyrrast) | (kapon | xilwren). Each line below is one lookup in a
table.
    oviazt | nyrrast = nyrrast   (the table for |)
    kapon | xilwren = xilwren   (the table for |)
    nyrrast | xilwren = xilwren   (the table for |)
That leaves xilwren, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is nyrrast | (kapon | oviazt) for contrast.
    kapon | oviazt = kapon   (the table for |)
    nyrrast | kapon = xilwren   (the table for |)
The value is xilwren. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
oviazt <~ oviazt hold? Read off what oviazt stands over: oviazt, kapon, nyrrast and
xilwren. oviazt is among them, so it holds.

## A case that breaks

R4. It is not the case that: There is a mornglim whose clobra is the whole system. The
case that settles it: largest_span = 1, size = 4. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by closure under the first operation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside D1 (iskzam mornglims), D11 (the nakdri of a mornglim), D8 (the clobra of
a mornglim) and T4 (the clobra of a mornglim is tezdri).

## Proofs

R4. It is not the case that: There is a mornglim whose clobra is the whole system.

  (1) [S2] Take the case largest_span = 1, size = 4, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 4 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T5. If S is tezdri and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 52 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T6. x | x = x holds if and only if [x] contains x alone.

  (1) [D1] If x | x = x then {x} is already closed under |.
  (2) [T4] So [x] = {x} and the nakdri is one.
  (3) [D11] Conversely a span of one object must contain x | x, which is then x.

Checked over 4 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T7. For every mornglim x, the nakdri of x divides 4.

  (1) [T4] [x] is a tezdri collection.
  (2) [D11] Its size is the nakdri of x.
  (3) The claim is that this size always divides 4.

Checked over 4 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the grixvor. Later chapters state their results in these terms and do not
restate the definitions.

Established here and safe to use: T5, T6 and T7.

Do not carry forward R4. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 4.
  x026. List every mornglim in the grixvor.
  x027. What is the largest nakdri any mornglim has?
