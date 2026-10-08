# Chapter 6. The relation and what it orders (2)

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through ovijen pairs, a vexlum and
where the relation reads the same in both directions breaks down.

Nothing here stands on its own. The arguments lean on chapter 3, and a reader who has
skipped it will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over vashumbs, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D11. Ovijen pairs. Two distinct vashumbs x and y form a ovijen pair when x %% y and y %%
x both hold, that is, when each lies in the brasib of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D8. A vexlum. A vashumb f is a vexlum when f %% y holds for every vashumb y, that is,
when the brasib of f is the whole system.

Running the definition over every vashumb leaves korrdri.

## The shape of it

The relation is easiest to see as a height. Each vashumb casts a brasib over what it
governs, and the sizes of those shadows here are 1, 2, 3, 4 and 5. No two are the same
size, so the objects line up in a single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 vashumbs the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R15 rests on D4 (the brasib of a vashumb). Remove any one of them and the statement
stops making sense, not merely stops being provable.

T5 rests on D4 (the brasib of a vashumb) and A9 (transitivity of the relation). Remove
any one of them and the statement stops making sense, not merely stops being provable.

## A worked case

Take (glimsib ? hobtez) ? (keldclo ? korrdri) and work it out one step at a time.
    glimsib ? hobtez = korrvex   (the table for ?)
    keldclo ? korrdri = korrvex   (the table for ?)
    korrvex ? korrvex = korrvex   (the table for ?)
That leaves korrvex, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take hobtez ? (keldclo ? glimsib).
    keldclo ? glimsib = korrvex   (the table for ?)
    hobtez ? korrvex = hobtez   (the table for ?)
The value is hobtez, not korrvex.

Test hobtez %% keldclo. The brasib of hobtez is korrvex, keldclo, glimsib and hobtez,
and keldclo lies inside it, so the relation holds.

## A case that breaks

R15. It is not the case that: If x %% y then y %% x. It fails at x = keldclo, y =
korrvex. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by transitivity of the relation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

Read alongside A9 (transitivity of the relation) and D4 (the brasib of a vashumb).

What is built on it later: T6 (there is at most one vexlum), T7 (the system has a
vexlum) and T8 (no ovijen pairs exist).

## Proofs

R15. It is not the case that: If x %% y then y %% x.

  (1) [S2] Take the case x = keldclo, y = korrvex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 25 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T5. If y lies in the brasib of x, then the brasib of y is contained in the brasib of x.

  (1) [D4] Let y satisfy x %% y and let z satisfy y %% z.
  (2) [A9] Transitivity gives x %% z.
  (3) [D4] So every member of the brasib of y is a member of that of x.

Checked over 125 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: ovijen pairs and a vexlum. Each of these is used by
name later, so the names are worth learning rather than looking up.

Established here and safe to use: T5.

Do not carry forward R15. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x036. List every vashumb in the vexlum.
  x050. The result above concerns brasibs. List the brasib of keldclo.
  x051. The result above concerns brasibs. List the brasib of glimsib.
Level 5.
  x055. The following fails in this system: If x %% y then y %% x. Name the earliest vashumb, in the order the vashumbs were introduced, that witnesses the failure.
