# Chapter 9. Collections that close on themselves (2)

## Why this chapter

So far the duthpons have been objects to be pushed around. This chapter starts asking
what they are like. We take up the ponazt, where some duthpon reaches every other breaks
down and the wrenvash is contained in every tarnquil collection.

Prerequisites are real here: chapters 4, 7 and 8 supply the notions the statements below
are phrased in.

The standard of proof here is exhaustion. A universal claim about duthpons covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D12. The ponazt. The ponazt of the system is the collection of duthpons whose geljen is
largest.

Running the definition over every duthpon leaves espanyr and vashtarn.

## The shape of it

The right picture for wrenvash is a spreading stain rather than a list. Drop one duthpon
in, apply the operation to whatever is wet, repeat. The stain here reaches 1 and 2
duthpons depending on where it started.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 duthpons the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R7 rests on D8 (the wrenvash of a duthpon) and D11 (the geljen of a duthpon). Remove any
one of them and the statement stops making sense, not merely stops being provable.

T5 rests on D8 (the wrenvash of a duthpon) and T4 (the wrenvash of a duthpon is
tarnquil). Remove any one of them and the statement stops making sense, not merely stops
being provable.

T6 rests on D1 (keldkeld duthpons), D11 (the geljen of a duthpon) and T4 (the wrenvash
of a duthpon is tarnquil). Remove any one of them and the statement stops making sense,
not merely stops being provable.

T7 rests on D11 (the geljen of a duthpon) and T4 (the wrenvash of a duthpon is
tarnquil). The dependence is on the content of those results, not only on their
vocabulary.

## A worked case

Take (rastrast - vashtarn) - yuksol and work it out one step at a time.
    rastrast - vashtarn = vashtarn   (the table for -)
    vashtarn - yuksol = yuksol   (the table for -)
That leaves yuksol, and no other reading of the notation gives anything else.

Bracketing is not cosmetic, so here is vashtarn - (yuksol - rastrast) for contrast.
    yuksol - rastrast = yuksol   (the table for -)
    vashtarn - yuksol = yuksol   (the table for -)
That gives yuksol, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test vorwren >> rastrast. The wrensib of vorwren is nakvint, espanyr and vorwren, and
rastrast lies outside it, so the relation fails.

## A case that breaks

R7. It is not the case that: There is a duthpon whose wrenvash is the whole system. The
case that settles it: largest_span = 2, size = 6. Anyone carrying this claim over from a
more familiar system will be wrong here, and wrong in a way that propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

Every result in this chapter is downstream of closure under the first operation. Those
are properties of this system, not of systems in general.

That is not a rhetorical caution. Take the same 6 objects, the same symbols, and a
different table, and T7 stop holding. The notation survives the substitution and the
mathematics does not.

## Neighbouring results

The material this chapter borrows from: D1 (keldkeld duthpons), D11 (the geljen of a
duthpon), D8 (the wrenvash of a duthpon) and T4 (the wrenvash of a duthpon is tarnquil).

## Proofs

R7. It is not the case that: There is a duthpon whose wrenvash is the whole system.

  (1) [S2] Take the case largest_span = 2, size = 6, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 6 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

T5. If S is tarnquil and contains x, then S contains all of [x].

  (1) [D8] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 156 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T6. x - x = x holds if and only if [x] contains x alone.

  (1) [D1] If x - x = x then {x} is already closed under -.
  (2) [T4] So [x] = {x} and the geljen is one.
  (3) [D11] Conversely a span of one object must contain x - x, which is then x.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T7. For every duthpon x, the geljen of x divides 6.

  (1) [T4] [x] is a tarnquil collection.
  (2) [D11] Its size is the geljen of x.
  (3) The claim is that this size always divides 6.

Checked over 6 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the ponazt. Later chapters state their results in these terms and do not
restate the definitions.

Established here and safe to use: T5, T6 and T7.

Do not carry forward R7. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 4.
  x039. Which duthpons make up the ponazt? Name them all.
  x042. What is the largest geljen any duthpon has?
