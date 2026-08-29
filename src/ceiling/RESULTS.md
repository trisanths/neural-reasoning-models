# Result: the test ceiling is the training ceiling

Eight arms, `d<D>s<S>` for training plan-depth ceiling D and training
distinct-symbol ceiling S. Every arm starts from the same 350M base
checkpoint, draws the same worlds from the same seeds, sees four questions per
world, and trains 8000 optimizer steps at batch size 32 with lr 2e-5 and 200
warmup steps over 40000 worlds. The `d3s1` arm reproduces the published
opgraph arm: its training stream is asserted byte-identical to
`build_stream(range(n), "opgraph", 17)` before training starts.

Numbers below are the full pass, n = 100 per cell, both page wordings, greedy
and sampled decoding at temperature 0.8. Artifacts:

| path | what it holds |
|---|---|
| `results/ceiling/full_<arm>.json` | every cell summary |
| `results/ceiling/full_<arm>.records.jsonl` | every emitted plan and its structural comparison to gold |
| `results/ceiling/fast_<arm>.json` | the earlier n = 50 style 0 greedy pass |
| `results/ceiling/TABLES_fast.md` | the full table set for that pass |
| `runs/ceiling/<arm>.pt.stream.json` | the training stream statistics for each arm |

`oracle_both` is 1.000 in all 34 cells of all 8 arms, 272 cells. The harness
is sound.

Hedge rate, meaning an empty emission, is 0.000 in every cell. Decoding hit
the token budget in 0.000 of cells, so no plan length below is a truncation.
The leakage check, an emitted plan containing the gold answer as a literal,
stays at or below 0.040 and is identical across arms.

## The headline

Mean emitted plan steps and answer accuracy, sequential chains, gold operators
supplied so the measurement isolates composition. Column heading is the number
of steps the question needs. Greedy, page wording style 0, n = 100.

| arm | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 12 | 16 | 32 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| d1s1 | 1.0/1.00 | 1.0/0.05 | 1.0/0.00 | 1.0/0.01 | 1.0/0.01 | 1.0/0.01 | 1.0/0.00 | 1.0/0.02 | 1.0/0.00 | 1.0/0.00 | 1.0/0.00 |
| d2s1 | 1.0/1.00 | 2.0/1.00 | 2.0/0.02 | 1.9/0.01 | 2.0/0.03 | 2.0/0.03 | 1.8/0.01 | 2.0/0.01 | 2.0/0.03 | 2.0/0.01 | 2.0/0.01 |
| d3s1 | 1.0/1.00 | 2.0/1.00 | 3.0/1.00 | 3.0/0.01 | 3.0/0.04 | 2.7/0.03 | 3.0/0.04 | 3.0/0.02 | 3.0/0.00 | 3.0/0.02 | 3.0/0.02 |
| d4s1 | 1.0/1.00 | 2.0/1.00 | 3.0/1.00 | 4.0/1.00 | 4.0/0.04 | 4.0/0.05 | 3.6/0.02 | 3.4/0.04 | 4.0/0.01 | 4.0/0.03 | 4.0/0.02 |
| d6s1 | 1.0/1.00 | 2.0/1.00 | 3.0/1.00 | 4.0/1.00 | 5.0/1.00 | 6.0/1.00 | 6.0/0.01 | 6.0/0.04 | 5.7/0.01 | 6.0/0.03 | 6.0/0.01 |
| d8s1 | 1.0/1.00 | 2.0/1.00 | 3.0/1.00 | 4.0/1.00 | 5.0/1.00 | 6.0/1.00 | 7.0/0.99 | 8.0/0.99 | 7.7/0.05 | 8.4/0.04 | 8.6/0.01 |

The majority-answer rate, which is the empirical chance floor for these cells,
is 0.04 to 0.06. Every number above that is not 1.00 is at chance.

Every arm follows the diagonal to its own training ceiling and then flattens
on it. Accuracy is a step function: 1.00 at and below the training ceiling,
chance above it. The arm trained to depth eight answers depth eight chains at
0.99, where the published arm scores 0.02.

Sampled decoding at temperature 0.8 reproduces this cell for cell, to within
0.01 in accuracy and 0.1 in mean emitted steps. Greedy produced no false zero
here.

H12 is right about plan length, and more sharply than it predicted. The
constant of extrapolation is zero, not small: no arm generalises one step past
its training maximum. H10 is wrong about plan length. There is no wall near
three; the wall is wherever the training maximum was put.

No saturation point can be reported, because nothing in the range tested
saturates. The deepest arm is eight and it holds 0.99 at eight. The largest
plan any arm ever wrote is 1, 2, 3, 4, 10, 10 for the six depth arms in order,
so the two deep arms overshoot their ceiling by at most two steps and never
enough to answer a depth twelve question. Locating a horizon needs arms deeper
than eight.

## The paraphrase separates the ceiling from the reading

`plan_execute` on the second page wording, where the model must induce the
operators from prose it never trained on. Greedy, n = 100.

| arm | 1 | 2 | 3 | 4 | 6 | 8 |
|---|---|---|---|---|---|---|
| d1s1 | 1.0/0.86 | 1.0/0.05 | 1.0/0.00 | 1.0/0.01 | 1.0/0.01 | 1.0/0.02 |
| d2s1 | 1.0/0.93 | 2.0/0.49 | 2.0/0.01 | 2.0/0.01 | 2.0/0.03 | 2.0/0.02 |
| d3s1 | 1.0/0.86 | 2.0/0.47 | 3.0/0.48 | 3.0/0.01 | 2.5/0.03 | 3.0/0.00 |
| d4s1 | 1.0/0.87 | 2.0/0.40 | 3.0/0.47 | 4.0/0.46 | 4.0/0.05 | 3.7/0.01 |
| d6s1 | 1.0/0.90 | 2.0/0.43 | 3.0/0.44 | 4.0/0.39 | 6.0/0.41 | 6.0/0.02 |
| d8s1 | 1.0/0.44 | 2.0/0.16 | 3.0/0.15 | 4.0/0.11 | 6.0/0.13 | 8.0/0.14 |

The emitted plan length is unchanged by the wording: every arm still writes
exactly its ceiling. Accuracy falls because induction falls. Pages parsed on
the paraphrase run 3077 to 4303 of 4400 against 4400 of 4400 on the trained
wording, and behaviourally correct operators run 3000 to 3937 of 6599 against
6298 of 6599. So the composition ceiling is a property of the plan decoder and
is wording independent, while the accuracy loss under paraphrase is induction
and nothing else. Sampled decoding again reproduces this to within 0.02.

One cost of raising the ceiling shows here. `d8s1` has the worst paraphrase
induction of any arm, 3077 of 4400 pages parsed, and its paraphrase accuracy
is a third of the shallower arms at every depth. Its plan half is unchanged;
what degraded is the reading half. Longer plan targets over a fixed step
budget appear to buy depth at the cost of induction robustness. That is worth
controlling for before treating a raised ceiling as free.

## What breaks past the ceiling

Beyond its ceiling the model does not write a long plan badly. It writes a
plan of exactly its ceiling length, well typed and parseable, unrelated to the
question. From the n = 50 pass, sequential, gold operators: parse rate and well
typed rate are identical in every cell and are 1.000 through depth eight for
every arm, degrading only at extreme depth for the deep arms, d8s1 parsing
0.880 at 12, 0.820 at 16 and 0.660 at 32.

Exact gold plan rate, shape match rate and operand multiset match rate are all
1.000 at and below the ceiling and 0.000 above it. `d8s1` is the one exception,
matching operands at 1.000 at depths seven and eight where its exact plan rate
is 0.980 and 1.000. Operand reading, ordering and register wiring survive
exactly as far as plan length does and not one step further. Past the ceiling a
plan too short to hold the question's operands cannot match them, so the
operand curve tracks the length curve rather than failing on its own.

## The symbol ceiling is a separate failure and does not move

Novel composition needs two operators defined on separate pages. Distinct
operator symbols emitted, where the question needs two, gold operators,
greedy, n = 100:

| arm | 2 | 3 | 4 | 6 | 8 | 16 |
|---|---|---|---|---|---|---|
| d1s1 | 1.00/0.06 | 1.00/0.00 | 1.00/0.00 | 1.00/0.00 | 1.00/0.02 | 1.00/0.00 |
| d3s1 | 1.00/0.02 | 1.01/0.00 | 1.00/0.02 | 1.00/0.00 | 1.00/0.02 | 1.01/0.01 |
| d6s1 | 1.00/0.03 | 1.00/0.00 | 1.00/0.03 | 1.01/0.03 | 1.02/0.01 | 1.00/0.00 |
| d8s1 | 1.03/0.05 | 1.00/0.00 | 1.02/0.03 | 1.00/0.03 | 1.01/0.03 | 1.00/0.01 |
| d3s2 | 1.00/0.04 | 1.07/0.05 | 1.02/0.01 | 1.03/0.00 | 1.03/0.01 | 1.01/0.00 |
| d3s3 | 1.01/0.05 | 1.00/0.00 | 1.00/0.02 | 1.01/0.00 | 1.03/0.01 | 1.02/0.00 |

Every arm emits about one distinct symbol where two are needed, and every arm
is at chance. From the n = 50 pass, structure right with the symbols collapsed
onto fewer names runs 0.92 to 1.00 inside each arm's depth range and 0.000
outside it, where the structure is wrong as well. The paraphrase pass and the
sampled pass both reproduce this.

So the depth ceiling and the symbol ceiling are two different failures.
Raising the plan length ceiling to eight fixes chains of eight and leaves
novel composition exactly where it was.

## The symbol sweep does not rescue novel composition

`d3s2` and `d3s3` were trained with plans naming two and three distinct
symbols at a depth ceiling of three. Their multi-symbol training is a chain
across two pages, a unit conversion feeding the assessment procedure and at
three symbols the procedure's decision on top, so two binary operators are
never combined in training and the novel evaluation stays held out.

Neither arm moves novel composition. Both still emit about one distinct symbol
where two are needed and both score at chance. H12's second prediction, that
the novel failure disappears as soon as training contains two-distinct-symbol
plans, is not supported by this manipulation.

What the symbol training did move is the kind structurally closest to it.
On `same_page_pair`, where a plan must chain `score` then `decide`, `d3s3`
emits 2.18 distinct symbols against 1.00 for every single-symbol arm, and it
is the only arm to score above zero there at 0.03. So the model learned to
emit multi-symbol plans of the shape it was shown, and that did not generalise
to choosing between two interchangeable binary operators.

It also generalised in the wrong direction. On `units`, a one step one symbol
question, `d3s3` emits 2.94 distinct symbols and scores 0.00 where every
single-symbol arm scores 1.00, and `d3s2` emits 1.58 and scores 0.08. This is
a consequence of the design and not a surprise: the S arms replace the bare
unit question with the cross-page chain in order to hold the item count at
four, so those arms never see a unit question answered by one step. The model
writes the chain it was trained on. That is the same distributional story as
the depth ceiling, pointing the other way.

The honest limit of the symbol result: these arms show the model that a plan
may name several symbols, over operators of different arity drawn from
different page kinds. They do not show it two binary operators that must be
told apart by which one the question wrote. An arm trained on mixed
binary-operator plans would test the stronger form of H12's symbol prediction
and is not run here.

## Relational breadth does not move, and the reason is worth reading

Breadth 1 to 6, every arm, `oracle_plan` and `oracle_ops` both: 1.000 at
breadth 1, 2 and 3, and 0.000 at 4, 5 and 6, with `oracle_both` at 1.000
throughout. Identical for all eight arms including `d8s1` and `d3s3`. Raising
a plan-length ceiling does not move breadth, so the induction reading survives.

`plan_execute` at breadth 4 to 6 reads 0.24 to 0.42, above both oracles, which
is impossible for a real capability. Reading `results/ceiling/fast_d3s1.records.jsonl`
at breadth 4, n = 50 each:

* `plan_execute` 0.260, every plan well typed, 13 ok and 37 wrong value
* `oracle_ops` 0.000, well typed 0.000, all 50 fail at execution
* `oracle_plan` 0.000, exact gold plan 1.000, all 50 fail at execution

The emitted plan is `t1 = score 57 true true false ; ans t1` where gold is
`t1 = score 57 true true true false ; ans t1`. The model writes three condition
flags, its trained breadth. Against the gold five argument operator that plan
is not well typed and cannot run. The gold plan against the induced operator
cannot run either, because the induced operator has three flags too. Under
`plan_execute` the model's short plan meets the model's short operator, the
arities agree, it executes, and it is right whenever the dropped conditions did
not change the answer. Those numbers are two matched errors cancelling. They
are not a breadth curve and should not be quoted as one.

That also says something about breadth itself. The induced operator stops at
three conditions and training drew breadth from one, two and three. The
breadth failure at four looks like the same distributional ceiling as the depth
failure, sitting on the induction side rather than the plan side. This sweep
did not vary the breadth ceiling, which is why it did not move. Varying it is
the obvious next experiment.

## What this means for the architecture work

Four architecture experiments are evaluating past a training maximum of three
on the assumption that what they measure is a property of the mechanism. On
this evidence the wall they are measuring is the training distribution. An arm
that changes nothing but the training ceiling moves the wall from three to
eight and holds 0.99 there. Any depth curve that stops near three is measuring
that artifact and cannot separate architectures until the training ceiling is
raised past the evaluation range.

Two things are not distributional in this way. Symbol selection, which neither
the depth sweep nor the multi-symbol training tried here moves off chance. And
induction under a changed wording, which got worse in the deepest arm rather
than better. Those are where an architecture claim still has something to
measure.
