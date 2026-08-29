# Result: the test ceiling is the training ceiling

Fast pass, n = 50 per cell, page wording style 0, greedy decoding. Artifacts:
`results/ceiling/fast_<arm>.json` for the cell summaries,
`results/ceiling/fast_<arm>.records.jsonl` for every emitted plan,
`results/ceiling/TABLES_fast.md` for the full table set. Arms are named
`d<D>s<S>` for training plan-depth ceiling D and training distinct-symbol
ceiling S. The `d3s1` arm reproduces the published opgraph arm; its training
stream is asserted byte-identical before training starts.

`oracle_both` is 1.000 in all 88 cells, so the harness is sound.

## The headline

Mean emitted plan steps, sequential chains, gold operators supplied so the
measurement isolates composition. The column heading is the number of steps
the question needs.

| arm | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 12 | 16 | 32 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| d1s1 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| d2s1 | 1.00 | 2.00 | 2.00 | 1.86 | 2.00 | 2.00 | 1.78 | 2.00 | 2.00 | 1.96 | 2.00 |
| d3s1 | 1.00 | 2.00 | 3.00 | 3.00 | 3.00 | 2.80 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 |
| d4s1 | 1.00 | 2.00 | 3.00 | 4.00 | 4.00 | 4.00 | 3.58 | 3.45 | 4.00 | 4.00 | 4.00 |
| d6s1 | 1.00 | 2.00 | 3.00 | 4.00 | 5.00 | 6.00 | 6.00 | 5.92 | 5.64 | 6.13 | 6.10 |
| d8s1 | 1.00 | 2.00 | 3.00 | 4.00 | 5.00 | 6.00 | 7.00 | 8.00 | 7.71 | 8.51 | 8.55 |

Every arm follows the diagonal to its own training ceiling and then flattens
on it. Decoding hit the token budget in 0.000 of cells, so no length here is
a truncation. Largest plan any arm ever wrote: 1, 2, 3, 4, 10, 10 for the six
arms in order, so the two deep arms occasionally overshoot by two steps and
never by more.

Answer accuracy, same condition, with a majority-answer floor of 0.04 to 0.06
and n = 50 per cell:

| arm | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 12 | 16 | 32 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| d1s1 | 1.000 | 0.060 | 0.000 | 0.020 | 0.020 | 0.000 | 0.000 | 0.020 | 0.000 | 0.000 | 0.000 |
| d2s1 | 1.000 | 1.000 | 0.020 | 0.000 | 0.000 | 0.040 | 0.000 | 0.000 | 0.040 | 0.020 | 0.000 |
| d3s1 | 1.000 | 1.000 | 1.000 | 0.000 | 0.020 | 0.040 | 0.060 | 0.020 | 0.000 | 0.020 | 0.040 |
| d4s1 | 1.000 | 1.000 | 1.000 | 1.000 | 0.020 | 0.040 | 0.000 | 0.020 | 0.000 | 0.060 | 0.020 |
| d6s1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 0.020 | 0.000 | 0.020 | 0.000 |
| d8s1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.980 | 1.000 | 0.060 | 0.040 | 0.020 |

Accuracy is a step function: 1.000 at and below the training ceiling, chance
above it. The arm trained to depth eight answers depth eight chains at 1.000,
where the published arm scores 0.020.

H12 is right about plan length, and more sharply than it predicted. The
constant of extrapolation is zero, not small: no arm generalises even one step
past what it was trained on. H10 is wrong about plan length. There is no wall
near three; the wall is wherever the training maximum was put. Nothing in the
range tested locates a horizon, so no saturation point can be reported. The
deepest arm here is eight and it holds 1.000 at eight.

## What breaks past the ceiling

Beyond its ceiling the model does not write a long plan badly. It writes a
plan of exactly its ceiling length, well typed, parseable, and structurally
unrelated to the question.

Sequential, gold operators, rates over n = 50. Parse rate and well typed rate
are identical in every cell, and are 1.000 through depth eight for every arm.
The two deep arms lose parseability only at the extreme depths: d8s1 parses
0.880 at 12, 0.820 at 16, 0.660 at 32.

Exact gold plan rate, shape match rate and operand multiset match rate all sit
at 1.000 at and below the ceiling and 0.000 above it, with one exception: d8s1
matches operands at 1.000 at depths seven and eight where its exact plan rate
is 0.980 and 1.000. So operand reading, ordering and register wiring survive
exactly as far as plan length does and not one step further. Beyond the
ceiling a plan too short to hold the question's operands cannot match them,
which is why the operand curve tracks the length curve rather than failing
separately.

The leakage check, an emitted plan containing the gold answer as a literal,
stays at or below 0.040 everywhere and is identical across arms.

## The symbol ceiling does not move with the depth ceiling

Novel composition needs two operators defined on separate pages. Distinct
operator symbols emitted, where the question needs two:

| arm | 2 | 3 | 4 | 5 | 6 | 8 | 12 | 16 |
|---|---|---|---|---|---|---|---|---|
| d1s1 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| d3s1 | 1.00 | 1.02 | 1.00 | 1.02 | 1.00 | 1.00 | 1.00 | 1.02 |
| d8s1 | 1.02 | 1.00 | 1.00 | 1.00 | 1.00 | 1.02 | 1.00 | 1.00 |
| d3s2 | 1.00 | 1.08 | 1.02 | 1.02 | 1.04 | 1.04 | 1.02 | 1.02 |
| d3s3 | 1.02 | 1.00 | 1.00 | 1.00 | 1.02 | 1.00 | 1.00 | 1.04 |

Structure right with the symbols collapsed onto fewer names than the question
needs runs at 0.92 to 1.00 inside each arm's depth range and drops to 0.000
outside it, where the structure is wrong too. Novel accuracy is at chance for
every arm at every depth: the best cell in the whole table is 0.120, most are
0.000 to 0.060, against a floor of 0.04 to 0.06.

So the depth ceiling and the symbol ceiling are two separate failures. Raising
the plan length ceiling to eight fixes chains of eight and leaves novel
composition exactly where it was.

## The symbol sweep, and what it does not show

`d3s2` and `d3s3` were trained with plans naming two and three distinct
symbols, holding the depth ceiling at three. Their multi-symbol training used
a chain across two pages, a unit conversion feeding the assessment procedure
and at three symbols the procedure's decision on top, so that two binary
operators are never combined in training and the novel evaluation stays held
out.

Neither arm moves novel composition. Both still emit about one distinct symbol
where two are needed, and both score at chance. H12's second prediction, that
the novel failure disappears as soon as training contains two-distinct-symbol
plans, is not supported by this manipulation.

The honest limit of that statement: the two-symbol plans these arms saw were a
fixed chain over operators of different arity from different page kinds. They
show the model that a plan may name several symbols, not that two
interchangeable binary operators must be told apart by which one the question
wrote. An arm trained on mixed binary-operator plans would test the stronger
form, and is not run here.

## Relational breadth does not move, and the reason is worth reading

Breadth 1 to 6, all arms, both `oracle_plan` and `oracle_ops`: 1.000 at
breadth 1, 2 and 3, and 0.000 at 4, 5 and 6. Identical for every arm including
d8s1 and d3s3. Raising a plan-length ceiling does not move breadth, so the
induction reading survives.

`plan_execute` at breadth 4 to 6 reads 0.24 to 0.42, above both oracles, which
is impossible for a real capability and is an artifact. Reading the records
for `d3s1` at breadth 4, n = 50 each:

* `plan_execute` 0.260, every plan well typed, reason histogram 13 ok and 37
  wrong value
* `oracle_ops` 0.000, well typed 0.000, all 50 fail at execution
* `oracle_plan` 0.000, exact gold plan 1.000, all 50 fail at execution

The emitted plan is `t1 = score 57 true true false ; ans t1` where the gold
plan is `t1 = score 57 true true true false ; ans t1`. The model writes three
condition flags, its trained breadth. Against the gold five-argument operator
that plan is not well typed and cannot run. The gold plan against the induced
operator cannot run either, because the induced operator has three flags too.
Under `plan_execute` the model's short plan meets the model's short operator,
the arities agree, it executes, and it happens to be right whenever the
dropped conditions did not change the answer. Those numbers are two matched
errors cancelling. They are not evidence of composition and should not be
quoted as a breadth curve.

That also says something about breadth itself. The induced operator stops at
three conditions, and training drew breadth from one, two and three. The
breadth failure at four looks like the same distributional ceiling as the
depth failure, sitting on the induction side rather than the plan side. This
sweep did not vary the breadth ceiling, which is why it did not move. Varying
it is the obvious next experiment.

## What this means for the architecture work

Four architecture experiments are evaluating past a training maximum of three
on the assumption that what they measure is a property of the mechanism. On
this evidence the wall they are measuring is the training distribution. An arm
that changes nothing but the training ceiling moves the wall from three to
eight and holds 1.000 there. Any depth curve from those experiments that stops
near three is measuring the same artifact and cannot separate architectures
until the training ceiling is raised past the evaluation range.

The part of the cliff that is not distributional is symbol selection. Neither
raising the depth ceiling nor the multi-symbol training tried here moves novel
composition off chance. That is where an architecture claim could still have
something to measure.
