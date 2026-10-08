# Chapter 4. The second operation and how the two interact

## Why this chapter

What follows was pieced together backwards. The last item of it, a neutral object for
the second operation, spreading of the second operation over the first and closure under
the second operation, was noticed before anyone had a reason to expect it.

Nothing here stands on its own. The arguments lean on chapter 1, and a reader who has
skipped it will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over tezkas, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

These are the laws this system obeys. Each was checked against every case before it was
written down.

A10. A neutral object for the second operation. There is a tezka vorzel with vorzel | x
= x for every x.

A11. Spreading of the second operation over the first. For all tezkas x, y, z: x | (y ><
z) = (x | y) >< (x | z), and the same on the right.

A7. Closure under the second operation. For all tezkas x and y, x | y is again a tezka.

A8. Association of the second operation. For all tezkas x, y, z: (x | y) | z = x | (y |
z).

A9. Commutation of the second operation. For all tezkas x and y: x | y = y | x.

## The shape of it

With two operations the question stops being what each does and becomes how they
interfere. | binds tighter, so the interference shows up whenever a bracket is left off.

Treat the above as scaffolding. It is the fastest route into a system nobody has
intuitions about yet, and it should be discarded the moment it disagrees with a
computation.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R3 rests on S2 (the Duthtarn combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R4 rests on S2 (the Duthtarn combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Take (opalfex >< lumwren) >< (vorzel >< opalfex) and work it out one step at a time.
    opalfex >< lumwren = opalfex   (the table for ><)
    vorzel >< opalfex = lumwren   (the table for ><)
    opalfex >< lumwren = opalfex   (the table for ><)
So (opalfex >< lumwren) >< (vorzel >< opalfex) is opalfex.

Bracketing is not cosmetic, so here is lumwren >< (vorzel >< opalfex) for contrast.
    vorzel >< opalfex = lumwren   (the table for ><)
    lumwren >< lumwren = lumwren   (the table for ><)
The value is lumwren, not opalfex.

Test lumwren <~ opalfex. The tarnopal of lumwren is lumwren, vorzel and opalfex, and
opalfex lies inside it, so the relation holds.

## A case that breaks

R3. It is not the case that: For every tezka x: x | x = x. It fails at x = opalfex,
value = vorzel. One case is enough, and this is the earliest one.

R4. It is not the case that: For all tezkas x and y: x >< (x | y) = x and x | (x >< y) =
x. The case that settles it: x = vorzel, y = vorzel, value = opalfex. Anyone carrying
this claim over from a more familiar system will be wrong here, and wrong in a way that
propagates.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: S2 (the Duthtarn combination tables).

These results are used again in T19 (the second operation keeps the drilorn intact).

## Proofs

R3. It is not the case that: For every tezka x: x | x = x.

  (1) [S2] Take the case x = opalfex, value = vorzel, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 27 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R4. It is not the case that: For all tezkas x and y: x >< (x | y) = x and x | (x >< y) = x.

  (1) [S2] Take the case x = vorzel, y = vorzel, value = opalfex, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 27 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R3 and R4. These were tested and failed, and the failing cases are
recorded above.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 5.
  x011. The following fails in this system: For every tezka x: x | x = x. Name the earliest tezka, in the order the tezkas were introduced, that witnesses the failure.
