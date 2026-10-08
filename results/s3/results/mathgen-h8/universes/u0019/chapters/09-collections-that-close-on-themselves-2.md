# Chapter 10. Collections that close on themselves (2)

## Why this chapter

What follows was pieced together backwards. The last item of it, the duthpon, where the
vexisk divides the number of opalmis breaks down and where some opalmi reaches every
other breaks down, was noticed before anyone had a reason to expect it.

Nothing here stands on its own. The arguments lean on chapters 4, 7 and 9, and a reader
who has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over opalmis, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D12. The duthpon. The duthpon of the system is the collection of opalmis whose vexisk is
largest.

Running the definition over every opalmi leaves hobfex and iskxil.

## The shape of it

The right picture for nakyuk is a spreading stain rather than a list. Drop one opalmi
in, apply the operation to whatever is wet, repeat. The stain here reaches 1, 2 and 4
opalmis depending on where it started.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 5 opalmis the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R7 rests on D11 (the vexisk of a opalmi) and T4 (the nakyuk of a opalmi is brarast).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

R9 rests on D8 (the nakyuk of a opalmi) and D11 (the vexisk of a opalmi). Remove any one
of them and the statement stops making sense, not merely stops being provable.

T5 rests on D8 (the nakyuk of a opalmi) and T4 (the nakyuk of a opalmi is brarast).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

T6 rests on D1 (qenpyr opalmis), D11 (the vexisk of a opalmi) and T4 (the nakyuk of a
opalmi is brarast). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Take (qenxil - keldsib) - (iskxil - duthzam) and work it out one step at a time.
    qenxil - keldsib = keldsib   (the table for -)
    iskxil - duthzam = iskxil   (the table for -)
    keldsib - iskxil = keldsib   (the table for -)
So (qenxil - keldsib) - (iskxil - duthzam) is keldsib.

Bracketing is not cosmetic, so here is keldsib - (iskxil - qenxil) for contrast.
    iskxil - qenxil = hobfex   (the table for -)
    keldsib - hobfex = keldsib   (the table for -)
That gives keldsib, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

One decision about the relation, since deciding is as much a skill as computing. Does
duthzam <~ hobfex hold? Read off what duthzam stands over: duthzam. hobfex is not among
them, so it fails.

## A case that breaks

R7. It is not the case that: For every opalmi x, the vexisk of x divides 5. The case
that settles it: x = hobfex, reach = 4, size = 5. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

R9. It is not the case that: There is a opalmi whose nakyuk is the whole system. It
fails at largest_span = 4, size = 5. One case is enough, and this is the earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

Read alongside D1 (qenpyr opalmis), D11 (the vexisk of a opalmi), D8 (the nakyuk of a
opalmi) and T4 (the nakyuk of a opalmi is brarast).

## Proofs

R7. It is not the case that: For every opalmi x, the vexisk of x divides 5.

  (1) [S2] Take the case x = hobfex, reach = 4, size = 5, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

R9. It is not the case that: There is a opalmi whose nakyuk is the whole system.

  (1) [S2] Take the case largest_span = 4, size = 5, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 5 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T5. If S is brarast and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 35 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T6. x - x = x holds if and only if [x] contains x alone.

  (1) [D1] If x - x = x then {x} is already closed under -.
  (2) [T4] So [x] = {x} and the vexisk is one.
  (3) [D11] Conversely a span of one object must contain x - x, which is then x.

Checked over 5 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: the duthpon. Each of these is used by name later, so
the names are worth learning rather than looking up.

The results now available are T5 and T6, each settled by exhaustive check rather than by
argument from analogy.

Do not carry forward R7 and R9. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x042. List every opalmi in the duthpon.
  x043. What is the largest vexisk any opalmi has?
Level 5.
  x044. The following fails in this system: For every opalmi x, the vexisk of x divides 5. Name the earliest opalmi, in the order the opalmis were introduced, that witnesses the failure.
