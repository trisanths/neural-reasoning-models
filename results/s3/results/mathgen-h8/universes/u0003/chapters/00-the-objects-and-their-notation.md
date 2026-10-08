# Chapter 1. The objects and their notation

## Why this chapter

The results collected here were not found in this order. The Espadri signature, the
Espadri combination tables and closure under the first operation came first, and the
rest was assembled around that once the pattern was visible.

The standard of proof here is exhaustion. A universal claim about wrenhobs covers at
most a few hundred cases, so it is run over all of them. Nothing below rests on an
argument from analogy with a system the reader already knows.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## The tables in full

The table for ;. Read the left argument down the side and the right argument across the top.

         |  iskglim  lornhob    tuisk   kaglim   xilfal   ovipyr
----------------------------------------------------------------
 iskglim |  iskglim  lornhob    tuisk   kaglim   xilfal   ovipyr
 lornhob |  lornhob    tuisk   kaglim   xilfal   ovipyr   ovipyr
   tuisk |    tuisk   kaglim   xilfal   ovipyr   ovipyr   ovipyr
  kaglim |   kaglim   xilfal   ovipyr   ovipyr   ovipyr   ovipyr
  xilfal |   xilfal   ovipyr   ovipyr   ovipyr   ovipyr   ovipyr
  ovipyr |   ovipyr   ovipyr   ovipyr   ovipyr   ovipyr   ovipyr

The table for |=. Read the left argument down the side and the right argument across the top.

         |  iskglim  lornhob    tuisk   kaglim   xilfal   ovipyr
----------------------------------------------------------------
 iskglim |  iskglim  lornhob    tuisk   kaglim   xilfal   ovipyr
 lornhob |  iskglim  lornhob    tuisk   kaglim   xilfal   ovipyr
   tuisk |  iskglim  lornhob    tuisk   kaglim   xilfal   ovipyr
  kaglim |  iskglim  lornhob    tuisk   kaglim   xilfal   ovipyr
  xilfal |  iskglim  lornhob    tuisk   kaglim   xilfal   ovipyr
  ovipyr |  iskglim  lornhob    tuisk   kaglim   xilfal   ovipyr

Every pair standing in the >- relation, grouped by left argument.

  iskglim >- iskglim, lornhob, tuisk, kaglim, xilfal and ovipyr
  lornhob >- lornhob, tuisk, kaglim, xilfal and ovipyr
  tuisk >- tuisk, kaglim, xilfal and ovipyr
  kaglim >- kaglim, xilfal and ovipyr
  xilfal >- xilfal and ovipyr
  ovipyr >- ovipyr

## What is defined here

The following hold in this system, without exception, and each was verified by running
through the tables in full.

A1. Closure under the first operation. For all wrenhobs x and y, x ; y is again a
wrenhob.

A2. Association of the first operation. For all wrenhobs x, y, z: (x ; y) ; z = x ; (y ;
z).

A3. Commutation of the first operation. For all wrenhobs x and y: x ; y = y ; x.

## The shape of it

A useful mental split: some wrenhobs are inert under the operation and some are not.
iskglim and ovipyr come back unchanged when combined with themselves, and iskglim,
lornhob, tuisk, kaglim, xilfal and ovipyr commute with everything.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 wrenhobs the table is short enough to consult every time.

## Where these results come from

The order matters. Each of these leans on what came before it, and the chain is short
enough to hold in mind.

R2 rests on S2 (the Espadri combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

R3 rests on S2 (the Espadri combination tables). Remove any one of them and the
statement stops making sense, not merely stops being provable.

## A worked case

Here is lornhob ; xilfal |= ovipyr, reduced without skipping anything.
    xilfal |= ovipyr = ovipyr   (the table for |=)
    lornhob ; ovipyr = ovipyr   (the table for ;)
The expression comes to ovipyr.

Move the brackets and the work changes. Take xilfal ; (ovipyr ; lornhob).
    ovipyr ; lornhob = ovipyr   (the table for ;)
    xilfal ; ovipyr = ovipyr   (the table for ;)
That gives ovipyr, the same value the first reading gave, which is a fact about these
particular arguments and not a law.

Test xilfal >- lornhob. The solzam of xilfal is xilfal and ovipyr, and lornhob lies
outside it, so the relation fails.

## A case that breaks

R2. It is not the case that: For every wrenhob x: x ; x = x. The case that settles it: x
= lornhob, value = tuisk. Anyone carrying this claim over from a more familiar system
will be wrong here, and wrong in a way that propagates.

R3. It is not the case that: For all wrenhobs x, y, z: if x ; y = x ; z then y = z. It
fails at x = lornhob, y = xilfal, z = ovipyr. One case is enough, and this is the
earliest one.

## Reach and limits

It is worth being exact about what has been shown and what has not.

These particular results happen to survive rebuilding the system over different tables
with the same names, which makes them weaker tests of understanding than the chapters
around them.

## Neighbouring results

What is built on it later: A4 (a neutral object for the first operation), A5 (an
absorbing object for the first operation), A6 (closure under the second operation) and
A7 (association of the second operation).

## Proofs

R2. It is not the case that: For every wrenhob x: x ; x = x.

  (1) [S2] Take the case x = lornhob, value = tuisk, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

R3. It is not the case that: For all wrenhobs x, y, z: if x ; y = x ; z then y = z.

  (1) [S2] Take the case x = lornhob, y = xilfal, z = ovipyr, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 216 cases: every tuple of the carrier the axiom quantifies over. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

Do not carry forward R2 and R3. These were tested and failed, and the failing cases are
recorded above.

## Exercises

Exercises, easiest first. Answers are in the key at the back.
Level 1.
  x001. What wrenhob does tuisk ; lornhob name?
  x002. Evaluate lornhob ; xilfal.
  x003. Reduce xilfal ; lornhob to a single wrenhob.
  x004. Reduce kaglim ; lornhob to a single wrenhob.
Level 2.
  x005. What wrenhob does (tuisk ; lornhob) ; lornhob name?
  x006. Work out the value of (xilfal ; iskglim) ; tuisk.
  x008. Evaluate kaglim^2.
  x009. Evaluate lornhob^3.
  x010. Which wrenhobs x satisfy x ; kaglim = ovipyr? List them all.
  x011. Solve x ; xilfal = ovipyr for x, naming every solution.
  x012. Solve x ; xilfal = xilfal for x, naming every solution.
  x013. Which wrenhobs x satisfy x ; tuisk = kaglim? List them all.
Level 3.
  x007. What wrenhob does (kaglim ; xilfal) ; (xilfal ; iskglim) name?
  x014. Evaluate lornhob ; tuisk |= tuisk, minding which operation binds tighter.
Level 5.
  x016. The following fails in this system: For every wrenhob x: x ; x = x. Name the earliest wrenhob, in the order the wrenhobs were introduced, that witnesses the failure.
  x017. The following fails in this system: For all wrenhobs x, y, z: if x ; y = x ; z then y = z. Name the earliest wrenhob, in the order the wrenhobs were introduced, that witnesses the failure.
