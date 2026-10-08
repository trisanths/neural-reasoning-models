# Chapter 6. The relation and what it orders (2)

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through aztgel pairs, a drisol and
where the relation reads the same in both directions breaks down.

Prerequisites are real here: chapter 3 supply the notions the statements below are
phrased in.

One habit to adopt: when a statement below quantifies over shenopals, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D11. Aztgel pairs. Two distinct shenopals x and y form a aztgel pair when x :: y and y
:: x both hold, that is, when each lies in the muxsib of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D8. A drisol. A shenopal f is a drisol when f :: y holds for every shenopal y, that is,
when the muxsib of f is the whole system.

In this system that picks out opallorn, which is 1 of the 5 shenopals.

## The shape of it

Think of :: as pointing downhill. The muxsib of a shenopal is everything downhill of it,
and those shadows here have sizes 1, 2, 3, 4 and 5.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R15 rests on D4 (the muxsib of a shenopal). Remove any one of them and the statement
stops making sense, not merely stops being provable.

T5 rests on D4 (the muxsib of a shenopal) and A9 (transitivity of the relation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Here is (opallorn % vorpon) % (qenthra % pontu), reduced without skipping anything.
    opallorn % vorpon = opallorn   (the table for %)
    qenthra % pontu = opallorn   (the table for %)
    opallorn % opallorn = opallorn   (the table for %)
That leaves opallorn, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take vorpon % (qenthra % opallorn).
    qenthra % opallorn = qenthra   (the table for %)
    vorpon % qenthra = grixlum   (the table for %)
The value is grixlum, not opallorn.

One decision about the relation, since deciding is as much a skill as computing. Does
opallorn :: grixlum hold? Read off what opallorn stands over: opallorn, qenthra,
grixlum, vorpon and pontu. grixlum is among them, so it holds.

## A case that breaks

R15. It is not the case that: If x :: y then y :: x. It fails at x = opallorn, y =
qenthra. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

Every result in this chapter is downstream of transitivity of the relation. Those are
properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A9 (transitivity of the relation) and D4 (the muxsib of a shenopal).

What is built on it later: T6 (there is at most one drisol), T7 (the system has a
drisol) and T8 (no aztgel pairs exist).

## Proofs

R15. It is not the case that: If x :: y then y :: x.

  (1) [S2] Take the case x = opallorn, y = qenthra, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T5. If y lies in the muxsib of x, then the muxsib of y is contained in the muxsib of x.

  (1) [D4] Let y satisfy x :: y and let z satisfy y :: z.
  (2) [A9] Transitivity gives x :: z.
  (3) [D4] So every member of the muxsib of y is a member of that of x.

Checked over 125 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: aztgel pairs and a drisol. Each of these is used by
name later, so the names are worth learning rather than looking up.

Established here and safe to use: T5.

Do not carry forward R15. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x041. List every shenopal in the drisol.
  x054. The result above concerns muxsibs. List the muxsib of opallorn.
  x055. The result above concerns muxsibs. List the muxsib of qenthra.
  x056. The result above concerns muxsibs. List the muxsib of grixlum.
Level 5.
  x060. The following fails in this system: If x :: y then y :: x. Name the earliest shenopal, in the order the shenopals were introduced, that witnesses the failure.
