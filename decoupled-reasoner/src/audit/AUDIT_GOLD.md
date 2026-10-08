# Independent gold, collisions, and opposite-instance pairs

An attempt to break the sequential depth curve from the operator-graph
experiment. Four checks were run. Checks 1, 2 and 4 passed. Check 3 failed: the
result did not survive it, although the narrow question inside check 3, whether
one generation can be credited on two items with opposite gold, came back clean.

The short version. The gold answers are right: a second interpreter written from
the page prose, sharing no code with the generator, re-derived all 7800 of them
and disagreed on none. The grader is exact match with no slack, and 591 pairs of
items with near identical surface and opposite gold produced zero double
credits, so the hedging artifact that killed the rule families cannot happen
here. But the same pairs show that the 0.480 and 0.500 at depths two and three
are a coin flip. The induction step never writes the associativity clause, so
the planner is not told which way a chain folds; and when it is told, through the
gold operator table, it scores the same. Every plan at depth four and beyond has
exactly three steps, and every item scored correct there was scored on a plan
shorter than its question.

## What was audited, and where it came from

The table under audit matches `results/opgraph_trace.json` on the training box,
produced by `scripts/opgraph_eval.py` with `--opgraph-ckpt runs/opgraph.pt`.
Re-running the plan conditions on that checkpoint reproduced it item for item:
1.000, 0.480, 0.500, 0.020, 0.013 for `plan_execute` at depths 1, 2, 3, 4 and 8,
against 150 items per cell.

One number in the audited table does not match its own source. `oracle_ops` at
depth three is 0.507 in `opgraph_trace.json`, not 0.500, and the rerun also gives
0.507 (76 of 150 against 75 of 150). The claim that `plan_execute` equals
`oracle_ops` to three decimals at every depth is therefore already false in the
file the table came from, by one item.

The box has since moved on. `results/opgraph_report.txt`, the current shipped
report, is built from `opgraph_a.json` and `opgraph_b.json` with
`--opgraph-ckpt runs/opgraph2.pt`, and reads 1.000, 1.000, 1.000, 0.020, 0.013
on the same rows. So the audited depth two and depth three cells are stale as
well as artefactual. Everything below was run on both checkpoints, because the
difference between them turns out to be the whole story at those depths.

## Check 1, independent gold generation: passed

`src/audit/refprose.py` is a second reader of the same pages. It takes only two
strings from the generator, the text of each page and the text of each question,
and rebuilds the answer from the English: the rule sentence, the modulus
sentence, the associativity sentence, the unit conversion sentences, the
adjustment lines and the cutoff sentence, each by its own regular expression,
then its own expression parser and evaluator over the question. It never imports
an `Operator`, a `Plan`, or the generator's evaluator.

| what | count |
|---|---|
| items re-derived | 7800 (26 cells, 150 items, both page wordings) |
| gold answers disagreeing | 0 |
| pages the reader could not parse | 0 |
| worked examples on a page it could not reproduce | 0 |

Every kind is covered: sequential, sequential_paren, breadth, novel,
same_page_pair and units, at every depth in the shipped grid, in both the trained
wording and the paraphrase. A generator that grades itself is the failure mode
this check exists for, and it is not present.

Two places where the prose is thinner than the gold, neither of which moves a
number:

The style 0 page says results are "reduced modulo m" and to "divide it by m and
keep only the remainder", and never says the remainder is non-negative. Under the
other remainder convention, sign of the dividend rather than of the divisor, 754
of the 7800 items change answer, including 12 of the 150 sequential items at
depth one. The page is only unambiguous because its first sentence says the
operator "produces a whole number". That sentence is carrying the whole sign
convention.

The style 1 page says "Take the remainder on division by m at the end", which
reads as one reduction on the reported value, while the generator reduces after
every application. The two readings coincide for the linear, square and
difference rules, which are congruent modulo m, and part company for the guarded
rule, whose comparison is not preserved by reduction. It changes 46 of the 3900
style 1 items, at most 11 in any one cell. The paraphrase pass is graded against
a gold its own wording does not quite state.

## Check 2, collisions: passed, and it empties depths four and up

Binary operators reduce modulo 100 or 1000, so an answer landing on a number some
shorter computation already produced is structurally likely. Measured on the
sequential set, 150 items per depth:

| depth | answer equals an intermediate | equals a truncation of the chain, any k | equals the best single truncation depth | equals an operand |
|---|---|---|---|---|
| 2 | 0.027 | 0.040 | 0.040 | 0.000 |
| 3 | 0.027 | 0.047 | 0.027 | 0.007 |
| 4 | 0.033 | 0.060 | 0.047 | 0.020 |
| 6 | 0.087 | 0.067 | 0.033 | 0.007 |
| 8 | 0.073 | 0.153 | 0.060 | 0.000 |

Operand collisions are near zero, which is the rejection sampling working. The
truncation rate climbs with depth exactly as the modulus makes it, reaching 15.3
percent at depth eight for a model free to stop anywhere.

Accuracy on the collision-free subset, `plan_execute` on the audited checkpoint,
where a collision is the answer coinciding with an intermediate, a truncation or
an operand:

| depth | collision-free | full cell |
|---|---|---|
| 2 | 69/142 = 0.486 | 0.480 |
| 3 | 70/142 = 0.493 | 0.500 |
| 4 | 3/135 = 0.022 | 0.020 |
| 8 | 0/123 = 0.000 | 0.013 |

Depths two and three do not move. Depth eight goes to zero.

The stronger version of this check comes from what the model actually writes.
Training never showed a plan longer than three steps, and the plan lengths at
evaluation are:

| depth | plans of length 3 | plans of the length the question needs | correct items whose plan was too short |
|---|---|---|---|
| 4 | 150/150 | 0/150 | 3 of 3 |
| 8 | 150/150 | 0/150 | 2 of 2 |

So every item graded correct at depth four and depth eight was graded on a plan
that consumed four of the question's five or nine operands. A worked example from
depth eight, correct, with a gold plan of eight steps:

```
Evaluate 11 & 9 & 5 & 9 & 5 & 10 & 3 & 7 & 2.
plan: t1 = & 11 9 ; t2 = & t1 5 ; t3 = & t2 2 ; ans t3
```

Measured before looking at any output, a three-step plan over the first three
operands and one more scores, on the sequential population:

| depth | first four operands, page associativity | first three and the last | best over every choice of the fourth operand and both directions | reported plan_execute |
|---|---|---|---|---|
| 4 | 0.047 | 0.047 | 0.113 | 0.020 |
| 8 | 0.060 | 0.020 | 0.133 | 0.013 |

The reported accuracy at depth four and depth eight is at or below what the
model's own degenerate strategy would score. Those cells carry no evidence of
composition and should be read as zero, not as 0.020 and 0.013.

## Check 3, opposite-instance pairs: failed

For every item a twin world was built whose page for the operator in that
question is byte identical except for the sentence stating which way a run of the
operator associates. Same rule, same coefficients, same modulus, same worked
examples, same question, same operands. At depth one the twin's answer is
identical, which is the control. At depth two and above it is almost always
different: folding the chain the other way lands on the same number in only 0.7
to 2.7 percent of items. The twin's gold comes from the independent reader, not
from the generator.

The narrow question this check was written for, whether one generation can be
credited on two items with opposite gold, comes back clean.

| | audited checkpoint | current checkpoint |
|---|---|---|
| pairs whose two members have different gold | 591 | 591 |
| pairs graded correct on both | 0 | 297 |
| pairs where the two plans are byte identical | 750/750 | 152/750 |
| byte-identical plans graded correct on both | 0 | 0 |

Grading is `_norm(prediction) == _norm(gold)`, a whole-string match after
stripping and lowercasing, with no containment and no token slack. Two different
gold strings cannot both match one output. The 297 both-correct pairs on the
current checkpoint are not double credits: the plans differ, because that
checkpoint reads the sentence and folds accordingly.

The check fails on the next thing the same pairs show, which is where the depth
two and depth three numbers come from.

| depth | plan_execute | twin plan_execute | sum | exactly one of the pair correct | identical plan text |
|---|---|---|---|---|---|
| 1 | 1.000 | 1.000 | 2.000 | 0 of 0 | 150/150 |
| 2 | 0.480 | 0.533 | 1.013 | 148 of 148 | 150/150 |
| 3 | 0.500 | 0.507 | 1.007 | 149 of 149 | 150/150 |
| 4 | 0.020 | 0.007 | 0.027 | 4 of 146 | 150/150 |
| 8 | 0.013 | 0.007 | 0.020 | 3 of 148 | 150/150 |

At depths two and three the model writes the same plan for a page that says left
to right and a page that says right to left, and the pair sums to one. Its score
is the rate at which its fixed choice happened to match the page. Its choice is
not fixed to one direction, it folded left on 79 items and right on 69 at depth
two, but it is a function of the question rather than of the page, which is why
accuracy is 0.508 on left-associating pages and 0.458 on right-associating ones
instead of 1.000 and 0.000.

Why the information never arrives. Induction on 120 binary operator pages from
the audited checkpoint:

| | audited checkpoint | current checkpoint |
|---|---|---|
| pages parsed | 120/120 | 120/120 |
| body exactly the gold body | 120/120 | 120/120 |
| carries an `(assoc ...)` clause at all | 0/120 | 120/120 |
| associativity correct | 0/120 | 120/120 |

```
gold:    (defop / (x y) (% (+ (* 2 (- x y)) 1) 100) (assoc left) (ex (7 4) 7) (ex (12 5) 15))
induced: (defop / (x y) (% (+ (* 2 (- x y)) 1) 100) (ex (7 4) 7) (ex (12 5) 15))
```

`signature_line` then hands the planner `//2` where the gold table would say
`//2/left`. The audited checkpoint's planner is not told the associativity, and
`opdef.py` predicts the consequence in its own docstring: "Leaving it off the
object costs exactly what you would expect: a coin flip on every chain of two or
more."

That also explains the induction totals in the shipped run, 6144 exact and 6144
behavioural out of 9897 operators, with the two counts identical. Both
comparisons in `run.py` require `assoc` to agree. The run covers 1650 worlds and
so about 3300 binary operators, and it reports 3753 mismatches, which is what you
get when every binary operator fails on that one field while its body is right
and a few hundred `score` operators at high breadth fail outright.

And it disposes of the supporting claim. `plan_execute` equals `oracle_ops` not
because gold operators add nothing, but because the only thing gold operators add
is the field the planner discards. `oracle_ops` is shown `//2/left` and still
scores 0.480 and 0.507. Supplying the correct associativity in the operator table
changes nothing, which is a statement about the planner ignoring its input, not
about induction being complete.

The current checkpoint is a different situation. It emits the clause on 120 of
120 pages, writes a different plan for the twin page on all 150 items at depth
two, and scores 1.000 on the original and 1.000 on the twin at depths two and
three. Its depth two and depth three numbers are real. Its depth four and depth
eight numbers are the same three-step plans: 150 of 150 plans have three steps,
0 of 150 have the length the question needs, and all three correct items at each
depth came from a short plan.

## Check 4, chance floors and answer entropy by depth: passed

The answer distribution does change with depth, but not enough to matter and not
in the direction that would rescue a flat curve.

| depth | distinct answers in 150 | entropy, bits | uniform over the stated modulus | best single constant | best single truncation depth | three-step plan | floor used |
|---|---|---|---|---|---|---|---|
| 1 | 82 | 6.11 | 0.0056 | 0.0533 | n/a | n/a | 0.0533 |
| 2 | 109 | 6.62 | 0.0057 | 0.0267 | 0.0400 | n/a | 0.0400 |
| 3 | 116 | 6.75 | 0.0054 | 0.0200 | 0.0267 | n/a | 0.0267 |
| 4 | 119 | 6.76 | 0.0057 | 0.0267 | 0.0467 | 0.0467 | 0.0467 |
| 8 | 118 | 6.78 | 0.0056 | 0.0200 | 0.0600 | 0.0600 | 0.0600 |

Depth one is the concentrated end, 82 distinct answers and 6.11 bits against 118
and 6.78 at depth eight, because a single application of a rule to two operands
between 1 and 12 cannot reach most residues. So the floor is slightly higher at
depth one, which works against the reported curve rather than for it: the depth
one numbers are the ones with the most floor under them, and they are the
largest.

Chance-corrected accuracy, with `k = (acc - p0) / (1 - p0)` and `p0` the largest
of the trivial strategies at that depth:

| condition | d1 | d2 | d3 | d4 | d8 | macro acc | correction of the macro | mean of the corrections |
|---|---|---|---|---|---|---|---|---|
| direct | 0.451 | 0.195 | 0.103 | -0.028 | -0.050 | 0.173 | 0.134 | 0.134 |
| trace | 0.817 | 0.472 | 0.240 | -0.042 | -0.064 | 0.317 | 0.285 | 0.285 |
| plan_execute | 1.000 | 0.458 | 0.486 | -0.028 | -0.050 | 0.403 | 0.374 | 0.373 |
| oracle_ops | 1.000 | 0.458 | 0.493 | -0.028 | -0.050 | 0.404 | 0.376 | 0.375 |
| oracle_plan | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

Both aggregation orders are given because they are different quantities. Here
they agree to three decimals, and only because the floor barely moves with depth,
0.027 to 0.060 across the whole curve. On a task whose floor did move they would
not agree, and the two columns should stay separate in anything that reports
this.

Every corrected value at depth four and depth eight is negative for every
condition that is not `oracle_plan`. Those cells are below floor.

## What is dead

The number 0.480 at depth two and 0.500 at depth three, read as partial
composition. They are the rate at which an associativity-blind planner's fixed
fold matched the page. Pair sums of 1.013 and 1.007, 297 of 297 opposite-gold
pairs scoring on exactly one member, and 300 of 300 pairs with byte-identical
plan text.

The claim that `plan_execute` equals `oracle_ops` at every depth and therefore
gold operators change nothing. It is off by one item at depth three in its own
source file, and where it holds it holds because induction drops the
associativity clause and the planner ignores it when handed it. The right reading
is that the plan path is insensitive to the only operator field the composition
depends on.

The claim that the model induces operators from pages, stated without
qualification. On the audited checkpoint the bodies are perfect and the
associativity clause is absent from every one of the 120 binary operator pages
sampled, and from all 750 items and all 750 twins in the rerun. By the package's
own `_same_text` and `_same_behaviour`, both of which require `assoc` to agree,
none of those operators counts as matching gold.

The residuals 0.020 at depth four and 0.013 at depth eight, read as anything.
Every plan there has three steps, none has the length the question needs, every
correct item came from a short plan, and the reported accuracy is below the
0.047 and 0.060 that the short plan strategy scores on its own.

## What survives

The gold answers. Zero disagreements in 7800 independent re-derivations.

The grader. Exact match, no slack, zero double credits across 591 opposite-gold
pairs with 750 of 750 byte-identical generations.

The shape of the curve. `oracle_plan` really is 1.000 at every depth on both
checkpoints, and depth four and beyond really is failure. The corrections make
the collapse sharper, not softer: the cells that were 0.020 and 0.013 are zero.

The claim that failure past depth three is a planning failure rather than an
induction or execution failure. It holds, with the localisation refined. Up to
depth three the failure is the associativity field, and the current checkpoint
fixes it and reaches 1.000 there on both members of every twin pair. From depth
four the failure is a hard length prior at three steps, on both checkpoints,
which is exactly the training cap.

## Files

Code, on the training box under `~/opg` and committed at `src/audit`:
`refprose.py` the independent reader, `goldcheck.py` checks 1, 2 and 4,
`floor3.py` the three-step floor, `seqrerun.py` the per-item rerun and the twin
construction, `analyze_gold.py` and `analyze_pairs.py` and `final_table.py` the
tables, `induct_dump.py` the induction comparison.

Outputs, `~/opg/results`: `audit_gold.json` and `audit_gold_items.json`,
`audit_floors.json`, `audit_floor3.json`, `audit_seq_items.json` and
`audit_seq_items_v2.json`, `audit_pairs.json` and `audit_pairs_v2.json`,
`audit_chance.json`, `audit_induction_v1.json` and `audit_induction_v2.json`.
