# Chapter 1. The objects and their notation

## Why this chapter

Here is the question this chapter answers: once the combining is settled, what can be
said about the objects themselves? The route runs through the Vintfex signature, the
Vintfex combination tables and closure under the first operation.

A note on method before starting. Everything asserted below was checked against every
case the statement quantifies over, not argued from a pattern in a few examples. With 5
shenopals that is cheap, and it means a claim in this book is either settled or absent.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## The tables in full

The table for %. Read the left argument down the side and the right argument across the top.

          |  opallorn   qenthra   grixlum    vorpon     pontu
-------------------------------------------------------------
 opallorn |  opallorn  opallorn  opallorn  opallorn  opallorn
  qenthra |   qenthra  opallorn  opallorn  opallorn  opallorn
  grixlum |   grixlum   qenthra  opallorn  opallorn  opallorn
   vorpon |    vorpon   grixlum   qenthra  opallorn  opallorn
    pontu |     pontu    vorpon   grixlum   qenthra  opallorn

The table for &. Read the left argument down the side and the right argument across the top.

          |  opallorn   qenthra   grixlum    vorpon     pontu
-------------------------------------------------------------
 opallorn |  opallorn   qenthra   grixlum    vorpon     pontu
  qenthra |   qenthra   qenthra   grixlum    vorpon     pontu
  grixlum |   grixlum   grixlum   grixlum    vorpon     pontu
   vorpon |    vorpon    vorpon    vorpon    vorpon     pontu
    pontu |     pontu     pontu     pontu     pontu     pontu

Every pair standing in the :: relation, grouped by left argument.

  opallorn :: opallorn, qenthra, grixlum, vorpon and pontu
  qenthra :: qenthra, grixlum, vorpon and pontu
  grixlum :: grixlum, vorpon and pontu
  vorpon :: vorpon and pontu
  pontu :: pontu

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A1. Closure under the first operation. For all shenopals x and y, x % y is again a
shenopal.

## The shape of it

Two questions sort the shenopals quickly. Does combining a shenopal with itself change
it? For opallorn it does not. Does it matter which side it goes on? It always does.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R1 rests on S2 (the Vintfex combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R2 rests on S2 (the Vintfex combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R5 rests on S2 (the Vintfex combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R6 rests on S2 (the Vintfex combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take pontu % grixlum & vorpon and work it out one step at a time.
    grixlum & vorpon = vorpon   (the table for &)
    pontu % vorpon = qenthra   (the table for %)
That leaves qenthra, and no other reading of the notation gives anything else.

A companion case, grixlum % (vorpon % pontu), to show what the brackets are doing.
    vorpon % pontu = opallorn   (the table for %)
    grixlum % opallorn = grixlum   (the table for %)
That gives grixlum, against qenthra above.

Test pontu :: pontu. The muxsib of pontu is pontu, and pontu lies inside it, so the
relation holds.

## A case that breaks

R1. It is not the case that: For all shenopals x, y, z: (x % y) % z = x % (y % z). The
case that settles it: x = qenthra, y = opallorn, z = qenthra, left = opallorn, right =
qenthra. Anyone carrying this claim over from a more familiar system will be wrong here,
and wrong in a way that propagates.

R2. It is not the case that: For all shenopals x and y: x % y = y % x. The case that
settles it: x = opallorn, y = qenthra, left = opallorn, right = qenthra. Anyone carrying
this claim over from a more familiar system will be wrong here, and wrong in a way that
propagates.

R5. It is not the case that: For every shenopal x: x % x = x. The case that settles it:
x = qenthra, value = opallorn. Anyone carrying this claim over from a more familiar
system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Unusually, nothing in this chapter distinguishes this system from its near neighbours.
Take that as a warning about how much a familiar looking statement can be worth.

## Neighbouring results

These results are used again in A2 (closure under the second operation), A3 (association
of the second operation), A4 (commutation of the second operation) and A5 (a neutral
object for the second operation).

## Proofs

R1. It is not the case that: For all shenopals x, y, z: (x % y) % z = x % (y % z).

  (1) [S2] Take the case x = qenthra, y = opallorn, z = qenthra, left = opallorn, right = qenthra, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R2. It is not the case that: For all shenopals x and y: x % y = y % x.

  (1) [S2] Take the case x = opallorn, y = qenthra, left = opallorn, right = qenthra, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R5. It is not the case that: For every shenopal x: x % x = x.

  (1) [S2] Take the case x = qenthra, value = opallorn, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R6. It is not the case that: For all shenopals x, y, z: if x % y = x % z then y = z.

  (1) [S2] Take the case x = opallorn, y = opallorn, z = qenthra, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 125 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Explicitly not available: R1, R2, R5 and R6. A later argument that quietly assumes one
of these is wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 1.
  x001. Reduce qenthra % pontu to a single shenopal.
  x002. Reduce pontu % vorpon to a single shenopal.
  x003. Reduce grixlum % grixlum to a single shenopal.
  x004. Evaluate qenthra % grixlum.
  x005. Evaluate grixlum % pontu.
  x006. Work out the value of grixlum % vorpon.
  x007. Work out the value of qenthra % qenthra.
Level 2.
  x008. What shenopal does vorpon % pontu & qenthra name?
  x009. What shenopal does (grixlum % grixlum) % grixlum name?
  x010. Work out the value of (vorpon % grixlum) % qenthra.
  x011. Evaluate grixlum^2.
  x012. What is pontu combined with itself 3 times under %?
  x013. What is qenthra combined with itself 3 times under %?
  x014. Which shenopals x satisfy x % grixlum = grixlum? List them all.
  x015. Solve x % vorpon = qenthra for x, naming every solution.
  x016. Solve x % qenthra = grixlum for x, naming every solution.
  x017. Which shenopals x satisfy x % pontu = opallorn? List them all.
  x018. Solve x % vorpon = opallorn for x, naming every solution.
Level 3.
  x019. Evaluate grixlum % grixlum & grixlum, minding which operation binds tighter.
Level 5.
  x020. The following fails in this system: For all shenopals x, y, z: (x % y) % z = x % (y % z). Name the earliest shenopal, in the order the shenopals were introduced, that witnesses the failure.
  x021. The following fails in this system: For all shenopals x and y: x % y = y % x. Name the earliest shenopal, in the order the shenopals were introduced, that witnesses the failure.
  x023. The following fails in this system: For every shenopal x: x % x = x. Name the earliest shenopal, in the order the shenopals were introduced, that witnesses the failure.
  x024. The following fails in this system: For all shenopals x, y, z: if x % y = x % z then y = z. Name the earliest shenopal, in the order the shenopals were introduced, that witnesses the failure.
