# Chapter 9. Collections that close on themselves

## Why this chapter

What follows was pieced together backwards. The last item of it, the muxhob of a jenxil,
the voropal of a jenxil is espagrix and the shenfal, was noticed before anyone had a
reason to expect it.

Nothing here stands on its own. The arguments lean on chapters 4 and 6, and a reader who
has skipped them will find the derivations opaque rather than difficult.

One habit to adopt: when a statement below quantifies over jenxils, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Some of what follows is negative. A claim that fails is set out with the case that
breaks it, because knowing which habits do not carry over is worth as much as knowing
which do.

## What is defined here

D9. The muxhob of a jenxil. The muxhob of a jenxil x is the number of jenxils in its
voropal [x].

Worked out for each jenxil: reldvint to 1; wrenmux to 2; zellum to 2.

D10. The shenfal. The shenfal of the system is the collection of jenxils whose muxhob is
largest.

Running the definition over every jenxil leaves wrenmux and zellum.

## The shape of it

Picture the voropal as what happens when you start with one jenxil and keep folding it
against itself and against whatever appears, until nothing new appears. Because there
are only 3 jenxils, that stops. In this system the sizes it stops at are 1 and 2.

None of these images are load bearing. They are here because a reader who can see the
shape makes fewer lookups, not because any argument below depends on seeing it. Every
proof goes through the tables.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

T1 rests on D7 (the voropal of a jenxil) and D3 (espagrix collections). The dependence
is on the content of those results, not only on their vocabulary.

R12 rests on D7 (the voropal of a jenxil) and D9 (the muxhob of a jenxil). Remove any
one of them and the statement stops making sense, not merely stops being provable.

R9 rests on D9 (the muxhob of a jenxil) and T1 (the voropal of a jenxil is espagrix).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

T2 rests on D7 (the voropal of a jenxil) and T1 (the voropal of a jenxil is espagrix).
Remove any one of them and the statement stops making sense, not merely stops being
provable.

T3 rests on D1 (yukwren jenxils), D9 (the muxhob of a jenxil) and T1 (the voropal of a
jenxil is espagrix). Remove any one of them and the statement stops making sense, not
merely stops being provable.

## A worked case

Take (wrenmux % wrenmux) % wrenmux and work it out one step at a time.
    wrenmux % wrenmux = reldvint   (the table for %)
    reldvint % wrenmux = reldvint   (the table for %)
That leaves reldvint, and no other reading of the notation gives anything else.

Move the brackets and the work changes. Take wrenmux % (wrenmux % wrenmux).
    wrenmux % wrenmux = reldvint   (the table for %)
    wrenmux % reldvint = wrenmux   (the table for %)
The value is wrenmux, not reldvint.

Test zellum =< wrenmux. The rastqen of zellum is zellum, and wrenmux lies outside it, so
the relation fails.

Now compute [reldvint]. Fold reldvint against itself, then fold whatever appeared
against everything present, and stop when a round adds nothing. The result is reldvint,
of size 1.

## A case that breaks

R12. It is not the case that: There is a jenxil whose voropal is the whole system. It
fails at largest_span = 2, size = 3. One case is enough, and this is the earliest one.

R9. It is not the case that: For every jenxil x, the muxhob of x divides 3. It fails at
x = wrenmux, reach = 2, size = 3. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by closure under the first operation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

The material this chapter borrows from: D1 (yukwren jenxils), D3 (espagrix collections)
and D7 (the voropal of a jenxil).

## Proofs

T1. For every jenxil x, the collection [x] is espagrix.

  (1) [D7] [x] is built by taking x and closing under %.
  (2) [D3] Closing under an operation is exactly the sealing condition.
  (3) The carrier is finite, so the closure stops after finitely many rounds.

Checked over 27 cases: every object, then every pair inside its span. The check is exhaustive, so the statement is settled rather than supported.

R12. It is not the case that: There is a jenxil whose voropal is the whole system.

  (1) [S2] Take the case largest_span = 2, size = 3, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 3 cases: every object and its span. The check is exhaustive, so the statement is settled rather than supported.

R9. It is not the case that: For every jenxil x, the muxhob of x divides 3.

  (1) [S2] Take the case x = wrenmux, reach = 2, size = 3, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 3 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

T2. If S is espagrix and contains x, then S contains all of [x].

  (1) [D7] Every member of [x] is reached from x by finitely many applications of the operation.
  (2) [D3] A sealed S containing x is closed under each of those applications.
  (3) So each member of [x] is in S, by induction on the number of applications.

Checked over 12 cases: every sealed collection against every object. The check is exhaustive, so the statement is settled rather than supported.

T3. x % x = x holds if and only if [x] contains x alone.

  (1) [D1] If x % x = x then {x} is already closed under %.
  (2) [T1] So [x] = {x} and the muxhob is one.
  (3) [D9] Conversely a span of one object must contain x % x, which is then x.

Checked over 3 cases: every object. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Carry forward the muxhob of a jenxil and the shenfal. Later chapters state their results
in these terms and do not restate the definitions.

Established here and safe to use: T1, T2 and T3.

Do not carry forward R12 and R9. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 3.
  x022. How many jenxils lie in [wrenmux]?
  x023. How many jenxils lie in [zellum]?
Level 4.
  x025. Write down the shenfal in full.
Level 5.
  x024. Let z be (reldvint % reldvint) % wrenmux. What is the muxhob of z?
  x026. The following fails in this system: For every jenxil x, the muxhob of x divides 3. Name the earliest jenxil, in the order the jenxils were introduced, that witnesses the failure.
