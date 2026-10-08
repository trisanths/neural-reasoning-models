# Chapter 6. Combining objects (2)

## Why this chapter

What follows was pieced together backwards. The last item of it, the falwren, the
vextarn and the zamsol of a vintzam, was noticed before anyone had a reason to expect
it.

Nothing here stands on its own. The arguments lean on chapter 4, and a reader who has
skipped it will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over vintzams, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

## What is defined here

D5. The falwren. The falwren of the system is the collection of vintzams that tuwren
with every vintzam.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D6. The vextarn. The vextarn is the collection of all shenfal vintzams.

Running the definition over every vintzam leaves hurnvash.

D7. The zamsol of a vintzam. The zamsol of a vintzam x, written [x], is the smallest
reldjen collection that contains x.

Worked out for each vintzam: hurnvash to hurnvash; duthsib to hurnvash and duthsib;
drishen to hurnvash and drishen; pyryuk to hurnvash and pyryuk; aztka to hurnvash and
aztka; ovijen to hurnvash and ovijen.

## The shape of it

The right picture for zamsol is a spreading stain rather than a list. Drop one vintzam
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
vintzams depending on where it started.

A useful mental split: some vintzams are inert under the operation and some are not.
hurnvash come back unchanged when combined with themselves, and none commutes with
everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 vintzams the table is short enough to consult every time.

## Where these results come from

Nothing is derived in this chapter. It lays down material that later chapters draw on.

## A worked case

Take (pyryuk : ovijen) : (aztka : hurnvash) and work it out one step at a time.
    pyryuk : ovijen = hurnvash   (the table for :)
    aztka : hurnvash = aztka   (the table for :)
    hurnvash : aztka = hurnvash   (the table for :)
So (pyryuk : ovijen) : (aztka : hurnvash) is hurnvash.

A companion case, ovijen : (aztka : pyryuk), to show what the brackets are doing.
    aztka : pyryuk = duthsib   (the table for :)
    ovijen : duthsib = aztka   (the table for :)
The value is aztka, not hurnvash.

One decision about the relation, since deciding is as much a skill as computing. Does
pyryuk :: ovijen hold? Read off what pyryuk stands over: hurnvash. ovijen is not among
them, so it fails.

A second case, this time a zamsol. Start from ovijen. Combine it with itself, add
whatever is new, and repeat until nothing is added. What survives is hurnvash and
ovijen, so the vashnyr of ovijen is 2.

## A case that breaks

No counterexample exists to anything asserted here. That is a fact about this system and
not a general one, and the next chapter is where it stops being true.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

The material this chapter borrows from: D1 (shenfal vintzams), D2 (vintzams that tuwren)
and D3 (reldjen collections).

These results are used again in D9 (the vashnyr of a vintzam), T1 (the zamsol of a
vintzam is reldjen), T2 (the zamsol is contained in every reldjen collection) and T5
(the vextarn is reldjen).

## Proofs

No proofs are needed here. Everything asserted is a definition or a table entry.

## What to carry forward

New vocabulary from this chapter: the falwren, the vextarn and the zamsol of a vintzam.
Each of these is used by name later, so the names are worth learning rather than looking
up.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x032. List every vintzam in the vextarn.
  x033. List the zamsol of duthsib.
  x034. List the zamsol of drishen.
  x035. List the zamsol of pyryuk.
  x036. List the zamsol of aztka.
  x037. Name every vintzam in [ovijen].
Level 4.
  x038. Let z be drishen : hurnvash. List the zamsol of z.
  x039. Let z be drishen : aztka. List the zamsol of z.
