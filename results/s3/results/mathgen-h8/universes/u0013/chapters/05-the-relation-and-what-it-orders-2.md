# Chapter 6. The relation and what it orders (2)

## Why this chapter

The results collected here were not found in this order. Duthtu pairs, hurnkeld
collections and a umbmux came first, and the rest was assembled around that once the
pattern was visible.

Nothing here stands on its own. The arguments lean on chapters 1 and 3, and a reader who
has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over xilzams, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D13. Duthtu pairs. Two distinct xilzams x and y form a duthtu pair when x <| y and y <|
x both hold, that is, when each lies in the mivint of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D3. Hurnkeld collections. A collection S of xilzams is hurnkeld when x & y belongs to S
for every pair x, y drawn from S.

D9. A umbmux. A xilzam f is a umbmux when f <| y holds for every xilzam y, that is, when
the mivint of f is the whole system.

Running the definition over every xilzam leaves muxovi.

## The shape of it

Picture the ponwren as what happens when you start with one xilzam and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 4 xilzams, that stops. In this system the sizes it stops at are 1, 2 and 3.

Think of <| as pointing downhill. The mivint of a xilzam is everything downhill of it,
and those shadows here have sizes 1, 2, 3 and 4.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R11 rests on D4 (the mivint of a xilzam). Remove any one of them and the statement stops
making sense, not merely stops being provable.

T12 rests on D4 (the mivint of a xilzam) and A13 (agreement of the relation with the
first operation). The dependence is on the content of those results, not only on their
vocabulary.

T9 rests on D4 (the mivint of a xilzam) and A11 (transitivity of the relation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Here is (muxovi & ovimux) & (shennak & nyrfex), reduced without skipping anything.
    muxovi & ovimux = ovimux   (the table for &)
    shennak & nyrfex = shennak   (the table for &)
    ovimux & shennak = shennak   (the table for &)
That leaves shennak, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take ovimux & (shennak & muxovi).
    shennak & muxovi = shennak   (the table for &)
    ovimux & shennak = shennak   (the table for &)
The value is shennak. It agrees with the first case here, and a reader should resist
reading anything general into that.

Test muxovi <| shennak. The mivint of muxovi is muxovi, nyrfex, ovimux and shennak, and
shennak lies inside it, so the relation holds.

## A case that breaks

R11. It is not the case that: If x <| y then y <| x. It fails at x = muxovi, y = nyrfex.
One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

The load is carried by agreement of the relation with the first operation, closure under
the first operation and transitivity of the relation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside A1 (closure under the first operation), A11 (transitivity of the
relation), A13 (agreement of the relation with the first operation) and D4 (the mivint
of a xilzam).

These results are used again in D8 (the ponwren of a xilzam), T3 (the sibnak is
hurnkeld), T4 (the ponwren of a xilzam is hurnkeld) and T8 (the mornmi is hurnkeld).

## Proofs

R11. It is not the case that: If x <| y then y <| x.

  (1) [S2] Take the case x = muxovi, y = nyrfex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 16 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T12. If x <| y then (x & z) <| (y & z) for every xilzam z.

  (1) [D4] Let y lie in the mivint of x.
  (2) [A13] Compatibility applies the operation to both sides at once.
  (3) Nothing else is needed, since z was arbitrary.

Checked over 64 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T9. If y lies in the mivint of x, then the mivint of y is contained in the mivint of x.

  (1) [D4] Let y satisfy x <| y and let z satisfy y <| z.
  (2) [A11] Transitivity gives x <| z.
  (3) [D4] So every member of the mivint of y is a member of that of x.

Checked over 64 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward duthtu pairs, hurnkeld collections and a umbmux. Later chapters state
their results in these terms and do not restate the definitions.

Established here and safe to use: T12 and T9.

Do not carry forward R11. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x016. How many xilzams lie in the smallest hurnkeld collection containing nyrfex?
Level 4.
  x026. List every xilzam in the umbmux.
  x038. The result above concerns mivints. List the mivint of muxovi.
  x039. The result above concerns mivints. List the mivint of nyrfex.
  x040. The result above concerns mivints. List the mivint of ovimux.
Level 5.
  x043. The following fails in this system: If x <| y then y <| x. Name the earliest xilzam, in the order the xilzams were introduced, that witnesses the failure.
