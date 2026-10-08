# Chapter 6. The relation and what it orders (2)

## Why this chapter

What follows was pieced together backwards. The last item of it, vorzel pairs, yukxil
collections and a nakgrix, was noticed before anyone had a reason to expect it.

Prerequisites are real here: chapters 1 and 3 supply the notions the statements below
are phrased in.

One habit to adopt: when a statement below quantifies over wrenhobs, check two or three
cases by hand before reading on. The tables are short and the checking is fast, and it
is the only way to build the intuition this system does not share with any other.

Not every claim in this chapter survives. The ones that do not are kept, with their
counterexamples, rather than quietly dropped.

## What is defined here

D13. Vorzel pairs. Two distinct wrenhobs x and y form a vorzel pair when x >- y and y >-
x both hold, that is, when each lies in the solzam of the other.

In this system nothing satisfies it, which is itself a fact worth carrying forward.

D3. Yukxil collections. A collection S of wrenhobs is yukxil when x ; y belongs to S for
every pair x, y drawn from S.

D9. A nakgrix. A wrenhob f is a nakgrix when f >- y holds for every wrenhob y, that is,
when the solzam of f is the whole system.

Running the definition over every wrenhob leaves iskglim.

## The shape of it

The right picture for mimux is a spreading stain rather than a list. Drop one wrenhob
in, apply the operation to whatever is wet, repeat. The stain here reaches 1, 2, 3 and 5
wrenhobs depending on where it started.

The relation is easiest to see as a height. Each wrenhob casts a solzam over what it
dominates, and the sizes of those shadows here are 1, 2, 3, 4, 5 and 6. No two are the
same size, so the objects line up in a single file.

The honest caveat on all of this: a picture is a way of remembering a table, not a
substitute for one. Where the picture and the table disagree the table wins, and in a
system with 6 wrenhobs the table is short enough to consult every time.

## Where these results come from

Each result below is reached from earlier material, and the route is worth reading
before the statement.

R11 rests on D4 (the solzam of a wrenhob). Remove any one of them and the statement
stops making sense, not merely stops being provable.

T12 rests on D4 (the solzam of a wrenhob) and A13 (agreement of the relation with the
first operation). The dependence is on the content of those results, not only on their
vocabulary.

T9 rests on D4 (the solzam of a wrenhob) and A11 (transitivity of the relation). The
dependence is on the content of those results, not only on their vocabulary.

## A worked case

Here is (ovipyr ; tuisk) ; (xilfal ; kaglim), reduced without skipping anything.
    ovipyr ; tuisk = ovipyr   (the table for ;)
    xilfal ; kaglim = ovipyr   (the table for ;)
    ovipyr ; ovipyr = ovipyr   (the table for ;)
So (ovipyr ; tuisk) ; (xilfal ; kaglim) is ovipyr.

Bracketing is not cosmetic, so here is tuisk ; (xilfal ; ovipyr) for contrast.
    xilfal ; ovipyr = ovipyr   (the table for ;)
    tuisk ; ovipyr = ovipyr   (the table for ;)
The value is ovipyr. It agrees with the first case here, and a reader should resist
reading anything general into that.

One decision about the relation, since deciding is as much a skill as computing. Does
ovipyr >- ovipyr hold? Read off what ovipyr stands over: ovipyr. ovipyr is among them,
so it holds.

## A case that breaks

R11. It is not the case that: If x >- y then y >- x. It fails at x = iskglim, y =
lornhob. One case is enough, and this is the earliest one.

## Reach and limits

The limits of these results are sharper than they look.

The load is carried by agreement of the relation with the first operation, closure under
the first operation and transitivity of the relation. A system without them is not a
system where these results are harder to prove; it is a system where they are false.

That is not a rhetorical caution. Take the same 6 objects, the same symbols, and a
different table, and T12 stop holding. The notation survives the substitution and the
mathematics does not.

## Neighbouring results

Read alongside A1 (closure under the first operation), A11 (transitivity of the
relation), A13 (agreement of the relation with the first operation) and D4 (the solzam
of a wrenhob).

These results are used again in D8 (the mimux of a wrenhob), T3 (the vintvint is
yukxil), T4 (the mimux of a wrenhob is yukxil) and T8 (the lornglim is yukxil).

## Proofs

R11. It is not the case that: If x >- y then y >- x.

  (1) [S2] Take the case x = iskglim, y = lornhob, read straight from the tables.
  (2) [S2] The two sides of the claim come apart on that case, so the claim cannot hold for every case.
  (3) One counterexample is enough. Note that the claim may still hold for many particular objects; what fails is the universal reading.

Checked over 36 cases: every ordered pair. The check is exhaustive, so the statement is settled rather than supported.

T12. If x >- y then (x ; z) >- (y ; z) for every wrenhob z.

  (1) [D4] Let y lie in the solzam of x.
  (2) [A13] Compatibility applies the operation to both sides at once.
  (3) Nothing else is needed, since z was arbitrary.

Checked over 216 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

T9. If y lies in the solzam of x, then the solzam of y is contained in the solzam of x.

  (1) [D4] Let y satisfy x >- y and let z satisfy y >- z.
  (2) [A11] Transitivity gives x >- z.
  (3) [D4] So every member of the solzam of y is a member of that of x.

Checked over 216 cases: every ordered triple. The check is exhaustive, so the statement is settled rather than supported.

## What to carry forward

New vocabulary from this chapter: vorzel pairs, yukxil collections and a nakgrix. Each
of these is used by name later, so the names are worth learning rather than looking up.

Established here and safe to use: T12 and T9.

Explicitly not available: R11. A later argument that quietly assumes one of these is
wrong, and the counterexamples above say exactly where.

## Exercises

The exercises below are graded. Each one needs something from this chapter that cannot be guessed from the question.
Level 3.
  x021. How many wrenhobs lie in the smallest yukxil collection containing lornhob?
  x022. How many wrenhobs lie in the smallest yukxil collection containing tuisk?
