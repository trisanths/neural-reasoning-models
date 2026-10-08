# Verdict on the operator-graph depth result

The flat `oracle_plan` row at 1.000 through depth eight does not survive, and it
is not allowed to drive architecture decisions.

Two independent measurements kill it, and either would be enough.

The row is flat by construction. `oracle_plan` hands the executor a gold plan and
asks the model for nothing but induction, so its answer for a world is one bit
that every depth in that world inherits. It is a per-world induction rate
multiplied by a Python interpreter that returns the same thing on its eighth call
as on its first. Re-render the same pages, same seeds, same operators, same
questions, same gold plans and same gold answers in wordings no arm trained on,
and the same code produces flat rows at 0.087 to 0.207 on the audited checkpoint
and at 0.147 to 0.360 on the currently shipped one. Flatness carries no
information about depth. Only the level does, and the level is the induction rate
on one page template.

The level is not induction from the page. Transpose the two operand roles inside
each binary rule, keep the glyph, the constants, the modulus, the sentence
skeleton and the page's own worked examples, and recompute those examples so the
page states the swapped rule twice. Over 678 items where the page answer and the
memorised answer differ, the model answered from the page 0 times and from
training 678 times. At the operator level, 290 of 290 distinguishable binary
operators were induced with the training identity and 0 with the page's. The
currently shipped checkpoint behaves the same way: 0 of 678 toward the page,
279 of 290 operators following the training identity.

A hand written parser of 198 lines, reading only the same pages `direct_all`
reads, scores 1.000 at every depth from one to eight, on every wording and on the
transposed pages, and 1.000 toward the page and 0.000 toward the training
identity where the two differ. The pages contain everything the answer needs
under every wording. Chaining to depth eight is a property of the Python executor,
which the parser also has.

## 1. The eight checks

| # | check | result |
|---|---|---|
| 1 | independent gold generation | passed |
| 2 | collisions and short-computation coincidences | passed, and it empties depths four and up |
| 3 | opposite-instance pairs | failed |
| 4 | chance floors and answer entropy by depth | passed |
| 5 | plan leakage through packaging | passed |
| 6 | executor independence under `oracle_plan` | passed |
| 7 | surface form of the page | failed |
| 8 | permuted operator semantics | failed |

Check 1 passed. `src/audit/refprose.py` re-derives every answer from the page
prose alone and imports only `re` and `dataclasses`, no generator object. Zero
disagreements on 7800 items across 26 cells and two page wordings, zero
unreadable pages, zero worked examples it could not reproduce. Two prose gaps do
not change a number: style 0 never states that the remainder is non-negative
(754 of 7800 items would move under the other convention), and style 1 says the
remainder is taken at the end while the generator reduces after every application
(46 of 3900 items differ, at most 11 in a cell).

Check 2 passed. Collisions do not inflate depths one to three: collision-free
accuracy is 0.486 against 0.480 at depth two and 0.493 against 0.500 at depth
three on the audited checkpoint. They account for depths four and up entirely,
which is why the check is also a kill. See the plan length census in section 3.

Check 3 failed. The grader itself is clean: whole-string match after strip and
lowercase, no containment slack, and zero double credits across 591 pairs with
opposite gold. But flipping only the associativity sentence gives twin accuracies
of 0.533 and 0.507 against originals of 0.480 and 0.500, pair sums of 1.013 and
1.007, and 297 of 297 opposite-gold pairs scoring on exactly one member. On the
audited checkpoint induction emitted the `(assoc ...)` clause on 0 of 120 sampled
pages, so the planner was handed `//2` rather than `//2/left`. Handed the field,
it ignored it. The currently shipped checkpoint emits the clause 120 of 120,
writes a different plan for the twin, and scores 1.000 on both members, so this
particular failure is repaired there and the audited depth-two and depth-three
cells are stale.

Check 4 passed. The answer distribution shifts only mildly with depth, support 82
to 120 of 150 and entropy 6.11 to 6.78 bits, and the floor is highest at depth
one, where the accuracies are highest. The floor works against the reported curve
rather than for it. Numbers in section 3.

Check 5 passed. A depth-4 decision tree on twelve packaging features only, with
the associativity sentence deleted before any feature was computed and trained on
4000 training-range worlds, scores 0.4733 on 150 eval worlds against a 0.5267
majority baseline at style 0, and 0.5267 against 0.5267 at style 1. Below
baseline out of sample. No packaging channel carries the plan. The qualifier
matters more than the result: the plan prompt contains no page at all, only the
operator signature line and the question, and a 60-line parser reading exactly
those two fields reproduces the gold plan at 1.000 in all 17 cells, 2550 items.
`plan_execute` measures a syntactic transduction from a signature line and a
question, not planning over retrieved content.

Check 6 passed on every part, by instrumentation rather than inference. A
recording proxy in front of the real `run_plan` logged the `id()` of every
`Operator` invoked. Induced and gold tables share zero object ids. Under
`oracle_plan` the executor called an induced object 8850 times out of 8850 and a
gold object zero times. The gold plan carries no operand values that would make
induction unnecessary: 5400 operator steps and 0 builtin steps over 1200 plans,
1200 of 1200 ending on a temporary, 0 of 1200 containing an integer literal
absent from the question. No intermediate reaches the model: zero generate calls
under `oracle_plan` and `oracle_both`. Corrupting the induced body or emptying
the table drops `oracle_plan` from 1.000 to 0.000 at every depth. There is no
default and no silent identity.

Two sub-findings inside check 6 are not clean. The reverse-leak probe found 35
items on the paraphrase pass where a wrong induced body landed on the right value
by numerical coincidence, 7 of them scored correct, which is 0.6 per cent of that
condition. And there is a no-op family: on the breadth kind, training capped
breadth at 3, so the induced `score` operator has arity 4 in 150 of 150 worlds at
breadths 4 and 5, the model's plan writes `score` with exactly 4 arguments in 150
of 150 worlds at breadths 4, 5 and 6, and every plan therefore drops arguments.
`plan_execute` scores 0.420, 0.313 and 0.113 in those cells; all 127 correct items
came from argument-dropping plans and 81 of the 127 are items where every dropped
condition was a flag that was not set.

Check 7 failed. Re-rendering every page in three wordings no arm trained on,
with the seeds, the operators, the questions, the gold plans, the gold answers
and the page count held fixed and asserted identical, takes `oracle_plan` from
1.000 to 0.087 to 0.207 on the audited checkpoint and to 0.147 to 0.360 on the
shipped one. The re-renderer's self test is that style 0 reproduces
`src/opgraph/invent.py` byte for byte on 180 worlds and 720 pages. The parser
reads all four wordings at 1.000, which is the evidence that nothing was lost or
made ambiguous in the rewriting. Table in section 3.

Check 8 failed. Transposing the two operand roles inside each binary rule, with
everything else on the page intact and the worked examples recomputed so the page
states the swapped rule twice, gives a forced choice between the page and the
template. Over 678 items the model chose the template 678 times and the page 0
times, on both checkpoints. Table in section 3.

## 2. Claims that are now dead

### Induction works and only planning fails

Dead. The model does not induce operators from pages, it fills numerals into a
memorised template. Four slots of the same 300 binary operators behave four
different ways. Coefficients are read: a control family renumbering `a`, `b`
and `c` to 9, 11 and 13, values the generator can never draw during training,
gives 300 of 300 induced operators carrying the page's coefficients exactly. The
modulus is not read: the same control sets it to 97, where training only ever
shows 100 or 1000, and 300 of 300 induced operators write 100, in the same
sentence position, three lines above two worked examples that only make sense
modulo 97. The operand order is not read: 290 of 290. The associativity clause is
neither read nor written on the audited checkpoint: 300 of 300 dropped, on every
family and every wording.

The page's own verification procedure catches this and nothing acts on it.
`src/opgraph/opdef.py` treats the worked examples as the operator's verification
procedure and `verify` runs on every induction. On the transposed pages 290 of
900 induced operators fail it, and they are exactly the 290 transposed binary
operators. 207 of 300 reproduce both of the page's worked example clauses
exactly, and on 197 of those the body contradicts the clauses it just copied. The
signal is computed, recorded in `induction.self_verified`, and consulted by no
condition.

The shipped induction line, 9444 of 9897 behaviourally right and 0.954 exact
text, is a template-recall rate on one page wording. On style 2, 3 and 4 the same
model parses 368, 362 and 436 of 600 pages and induces 110, 64 and 52 binary
operators of 300, of which 27, 47 and 34 agree with the page.

### `plan_execute` equalling `oracle_ops` proves gold operators change nothing

Dead twice over. It is not an equality: the two differ in 5 of the 26 cells of
the grid, by up to 0.420, and the sign is the wrong way round. On breadth,
`plan_execute` is 0.420, 0.313 and 0.113 at depths 4, 5 and 6 while `oracle_ops`
is 0.000, 0.000 and 0.000 in the same cells, because the model's plan is written
for a four-argument operator, the truncated induced operator happens to take four
arguments, and the gold operator refuses the call. Gold operators do not fail to
help there, they hurt. The shipped report repeats the pattern at 0.380, 0.307 and
0.193 against 0.000.

Where the equality does hold, on sequential, it holds because the only difference
between the two prompts is a field the scheduler does not read. On the audited
checkpoint 1170 of 1200 plans are byte-identical between the two conditions, and
the association direction the scheduler picks is independent of the truth in
both: agreement 0.467 at depth two with a chi square of 0.516 on one degree of
freedom, and 0.493 and 0.500 at depth three with chi squares of 0.021 and 0.000.
The inference the claim licenses, that induction is not a bottleneck, does not
follow from a match on a field that neither condition uses.

### `oracle_plan` diverging from `oracle_both` on breadth proves model-induced operators are in play

This one survives, and it is now established directly rather than by inference.
Check 6a instrumented object identity: 8850 of 8850 executor calls under
`oracle_plan` resolved to an induced object and 0 to a gold one, and the table
handed to the executor was 6 induced and 0 gold in 1200 of 1200 sequential
executions. The divergence in the results file, 0.000 against 1.000 at breadth
depths 4 to 6, reproduces.

It says less than it was read to say. It establishes that the objects are induced
by the model. It does not establish that they were induced from the page, and
check 8 says they were not.

### Depth costs nothing once a correct plan exists

Dead. The flat row is what the condition returns whatever happens, because it is
a per-world induction outcome multiplied by an exact interpreter. The proof that
this is the mechanism rather than a story about it is the renumbered-modulus
family, the one place in this audit where induction is nearly right rather than
exactly right or exactly wrong: the induced operator there is correct except for
the modulus, so it agrees with the page whenever no intermediate crosses 97, and
`oracle_plan` runs 0.473, 0.127, 0.080, 0.100 and 0.013 at depths 1, 2, 3, 4 and
8. Given an operator that is almost correct, depth costs a great deal. The 1.000
row is what an exactly correct operator produces, and the exactness comes from
recall.

### The trace control rules out chain of thought as the explanation

Dead. The trace arm's advantage is a property of the trained wording, not of
writing the decomposition out. At depth one on style 0 it is 0.860 against 0.480
for `direct`. On style 2 it is 0.067 against 0.127 and on style 3 it is 0.047
against 0.087, so under two of the three new wordings the arm built to beat
`direct` is worse than `direct`. Style 4 is a tie at 0.187 against 0.193. An arm
whose sign flips with the prose cannot function as a control for anything.

### Also dead, from the earlier passes and from this one

The audited 0.480 at depth two and 0.500 at depth three read as partial
composition. They are the rate at which an associativity-blind planner's fixed
fold happened to match the page: pair sums 1.013 and 1.007, 297 of 297
opposite-gold pairs scoring on exactly one member, 300 of 300 byte-identical plan
texts. They are also stale, and the currently shipped checkpoint reads 1.000 at
both depths.

The residual 0.020 at depth four and 0.013 at depth eight read as anything at
all. Every plan there has three steps, none has the length the question needs,
every correct item came from a short plan, and the reported accuracy sits below
the 0.047 and 0.060 that a three-step plan scores on its own.

The replacement explanation the earlier pass offered for the tail, a hard length
prior at three steps inherited from the training cap, is also dead.
`runs/opgraph_step.pt` is the repair built for exactly that, asking for one step
at a time so that plan length is never a quantity the decoder has to emit. It
does not lengthen the plan. It shortens it as the question grows. Census in
section 3.

## 3. Corrected numbers

### The audited table is stale, and the headline is not

The audited table matches `results/opgraph_trace.json`, produced with
`runs/opgraph.pt`. The shipped report is built from `opgraph_a.json` and
`opgraph_b.json` with `runs/opgraph2.pt` and `runs/opgraph_step.pt`.

| depth | direct | trace | plan_execute | oracle_ops | step_plan_execute | oracle_plan |
|---|---|---|---|---|---|---|
| 1 | 0.480 | 0.860 | 1.000 | 1.000 | 1.000 | 1.000 |
| 2 | 0.227 | 0.460 | 1.000 | 1.000 | 1.000 | 1.000 |
| 3 | 0.127 | 0.267 | 1.000 | 1.000 | 1.000 | 1.000 |
| 4 | 0.020 | 0.027 | 0.020 | 0.020 | 0.020 | 1.000 |
| 5 | 0.020 | 0.000 | 0.033 | 0.033 | 0.020 | 1.000 |
| 6 | 0.007 | 0.000 | 0.020 | 0.020 | 0.013 | 1.000 |
| 7 | 0.013 | 0.033 | 0.040 | 0.040 | 0.007 | 1.000 |
| 8 | 0.013 | 0.000 | 0.020 | 0.020 | 0.027 | 1.000 |

The depth-two and depth-three cells of the audited table were repaired between
runs. `oracle_plan` at 1.000 through depth eight is identical on both
checkpoints, so the headline under attack is not the stale part.

### Chance floors at every depth

n = 150 per cell. `p0` is the largest of the trivial strategies at that depth,
which is what the correction uses.

| depth | distinct answers | entropy, bits | uniform over the stated modulus | best single constant | best truncation | best three-step plan | p0 |
|---|---|---|---|---|---|---|---|
| 1 | 82 | 6.11 | 0.0056 | 0.0533 | 0.0000 | n/a | 0.0533 |
| 2 | 109 | 6.62 | 0.0057 | 0.0267 | 0.0400 | n/a | 0.0400 |
| 3 | 116 | 6.75 | 0.0054 | 0.0200 | 0.0267 | n/a | 0.0267 |
| 4 | 119 | 6.76 | 0.0057 | 0.0267 | 0.0467 | 0.0467 | 0.0467 |
| 5 | 117 | 6.74 | 0.0060 | 0.0267 | 0.0400 | 0.0333 | 0.0400 |
| 6 | 113 | 6.67 | 0.0056 | 0.0267 | 0.0333 | 0.0333 | 0.0333 |
| 7 | 120 | 6.78 | 0.0057 | 0.0200 | 0.0400 | 0.0333 | 0.0400 |
| 8 | 118 | 6.78 | 0.0056 | 0.0200 | 0.0600 | 0.0600 | 0.0600 |

Depth one has the highest floor and the highest accuracies, so the floor moves
against the reported result rather than for it. A looser upper bound, any
truncation to any prefix scored against any of the fold directions, runs 0.000,
0.040, 0.047, 0.060, 0.080, 0.067, 0.113 and 0.153 at depths one to eight. It is
not used for the correction, because it is a maximum over strategies chosen after
seeing the answers. The same is true of the wider three-step bound at depths four
and up, 0.113, 0.093, 0.133, 0.147 and 0.133, which allows any fourth operand
rather than the one the page implies.

### Chance-corrected accuracy, both aggregation orders

The two macro orders are different quantities and are given separately.

    per depth                k_d = (acc_d - p0_d) / (1 - p0_d)
    correction of the macro  (mean_d acc_d - mean_d p0_d) / (1 - mean_d p0_d)
    mean of the corrections  mean_d (acc_d - p0_d) / (1 - p0_d)

Over all eight depths of the shipped sequential row, with mean floor 0.0425:

| condition | d1 | d2 | d3 | d4 | d5 | d6 | d7 | d8 | macro acc | correction of the macro | mean of the corrections |
|---|---|---|---|---|---|---|---|---|---|---|---|
| direct | 0.451 | 0.195 | 0.103 | -0.028 | -0.021 | -0.027 | -0.028 | -0.050 | 0.113 | 0.074 | 0.074 |
| trace | 0.852 | 0.438 | 0.247 | -0.021 | -0.042 | -0.034 | -0.007 | -0.064 | 0.206 | 0.171 | 0.171 |
| plan_execute | 1.000 | 1.000 | 1.000 | -0.028 | -0.007 | -0.014 | 0.000 | -0.043 | 0.392 | 0.365 | 0.364 |
| oracle_ops | 1.000 | 1.000 | 1.000 | -0.028 | -0.007 | -0.014 | 0.000 | -0.043 | 0.392 | 0.365 | 0.364 |
| step_plan_execute | 1.000 | 1.000 | 1.000 | -0.028 | -0.021 | -0.021 | -0.034 | -0.035 | 0.386 | 0.359 | 0.358 |
| oracle_plan | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

Every cell from depth four on is at or below zero for every condition except
`oracle_plan`. The tail is not small, it is absent. The two macro orders agree to
three decimals here only because the floor barely moves with depth, 0.027 to
0.060 across the whole curve. On a task whose floor did move they would not
agree, and anything reporting this should keep the two columns separate.

On the five depths of the audited table and the audited checkpoint, the same
correction gives direct 0.451, 0.195, 0.103, -0.028, -0.050, macro 0.173 and both
aggregations 0.134; trace 0.817, 0.472, 0.240, -0.042, -0.064, macro 0.317 and
0.285; `plan_execute` 1.000, 0.458, 0.486, -0.028, -0.050, macro 0.403 with 0.374
and 0.373; `oracle_ops` 1.000, 0.458, 0.493, -0.028, -0.050, macro 0.404 with
0.376 and 0.375.

### Check 7, the same content in four wordings

Style 0 is the trained wording. Styles 2, 3 and 4 state the same rule, carry the
same modulus sentence, the same associativity sentence and the same two worked
example pairs, and are re-rendered from the world with the seed, the operator,
the four pages, the retrieval order and the question held fixed and asserted
identical. Style 1 is the shipped paraphrase. 150 items per cell.

Audited checkpoint, `runs/opgraph.pt`:

| condition | depth | style 0 | style 2 | style 3 | style 4 | style 1 |
|---|---|---|---|---|---|---|
| `direct_all` | 1 | 0.480 | 0.127 | 0.087 | 0.193 | 0.187 |
| `trace_all` | 1 | 0.860 | 0.067 | 0.047 | 0.187 | 0.187 |
| `plan_execute` | 1 | 1.000 | 0.187 | 0.207 | 0.087 | 0.600 |
| `oracle_plan` | 1 | 1.000 | 0.187 | 0.207 | 0.087 | 0.600 |
| `oracle_plan` | 2 | 1.000 | 0.153 | 0.160 | 0.093 | 0.640 |
| `oracle_plan` | 3 | 1.000 | 0.127 | 0.153 | 0.073 | 0.580 |
| `oracle_plan` | 4 | 1.000 | 0.187 | 0.187 | 0.153 | 0.587 |
| `oracle_plan` | 8 | 1.000 | 0.133 | 0.167 | 0.107 | 0.580 |

The audit measured that on `runs/opgraph.pt` only, which left open whether the
currently shipped checkpoint, which does read the associativity sentence and
holds `oracle_plan` at 0.860 to 0.913 under the shipped paraphrase, also loses
the page when the prose is re-rendered. It does. Same worlds, same seeds, same
questions, same gold plans, only the checkpoint moved:

| condition | depth | style 0 | style 2 | style 3 | style 4 |
|---|---|---|---|---|---|
| `oracle_plan` | 1 | 1.000 | 0.300 | 0.147 | 0.280 |
| `oracle_plan` | 2 | 1.000 | 0.307 | 0.247 | 0.327 |
| `oracle_plan` | 3 | 1.000 | 0.300 | 0.240 | 0.307 |
| `oracle_plan` | 4 | 1.000 | 0.360 | 0.187 | 0.360 |
| `oracle_plan` | 8 | 1.000 | 0.347 | 0.173 | 0.333 |
| `plan_execute` | 2 | 1.000 | 0.153 | 0.093 | 0.153 |
| `plan_execute` | 3 | 1.000 | 0.140 | 0.107 | 0.140 |
| `plan_execute` | 8 | 0.020 | 0.000 | 0.013 | 0.013 |

The `oracle_plan` row is flat inside every wording and sits at a different level
in each: 1.000, then 0.300 to 0.360, then 0.147 to 0.247, then 0.280 to 0.360.
Mean over the three new wordings and five depths, 0.281. That is the shape the
structural argument predicts, and it is what a per-world induction rate times an
exact interpreter has to look like. Induced operator text exact against gold on
the same pages: 900 of 900 at style 0, then 143, 511 and 490 of 900.

Induction is where it goes. Pages that parse as a `defop` fall from 600 of 600 at
style 0 to 368, 362 and 436 of 600. Binary operators induced fall from 300 of 300
to 110, 64 and 52, and of those, 27, 47 and 34 agree with the page on eight probe
pairs.

### Check 8, the transposed rule

Style 0 wording, same glyph, same constants, same modulus, same associativity
sentence, operand roles swapped inside the rule and the page's worked examples
recomputed so the page states the swapped rule twice. Items kept only where the
page answer and the training answer differ and the page answer cannot be echoed
out of the question. Of 750 items, 51 dropped as indistinguishable and 21 as
copyable, leaving 678.

| depth | n | `oracle_plan` toward the page | toward training |
|---|---|---|---|
| 1 | 131 | 0.000 | 1.000 |
| 2 | 136 | 0.000 | 1.000 |
| 3 | 140 | 0.000 | 1.000 |
| 4 | 135 | 0.000 | 1.000 |
| 8 | 136 | 0.000 | 1.000 |
| all | 678 | 0 / 678 | 678 / 678 |

At the operator level, 290 of the 300 transposed binary operators are
distinguishable on eight probe pairs. The induced body follows the page 0 times
and the training identity 290 times. `oracle_both` is 1.000 on all 678, so the
transposed harness computes the transposed truth correctly, and `oracle_ops`,
which never sees a page, is unchanged.

On the currently shipped `runs/opgraph2.pt` the same test gives 0 of 678 toward
the page, 279 of 290 operators following the training identity, 11 with no
operator induced for the symbol, and the associativity clause now kept on 279 of
279. The second checkpoint learned to copy one more field of the template. It did
not learn to read the page.

`plan_execute` on the transposed pages tracks the training answer at exactly the
rate the trained-wording curve tracks the gold answer: 1.000, 0.493, 0.479,
0.022, 0.015 against 1.000, 0.480, 0.500, 0.020, 0.013. The whole shipped
sequential row reappears, pointed at the wrong answer.

### The plan length census, and the death of the length-prior explanation

New in this pass. `src/audit/steplen.py`, results in
`results/audit_steplen.json`. Sequential, 150 items per cell, both plan-writing
arms of the shipped report. A question at depth d needs d steps.

| depth | `plan_execute` on `opgraph2.pt` | plans long enough | `step_plan_execute` on `opgraph_step.pt` | plans long enough |
|---|---|---|---|---|
| 4 | 3 steps: 150 | 0 / 150 | 3 steps: 150 | 0 / 150 |
| 5 | 3 steps: 150 | 0 / 150 | 1 step: 8, 3 steps: 142 | 0 / 150 |
| 6 | 1 step: 18, 3 steps: 132 | 0 / 150 | 1 step: 112, 2 steps: 12, 3 steps: 26 | 0 / 150 |
| 7 | 3 steps: 150 | 0 / 150 | 2 steps: 122, 3 steps: 28 | 0 / 150 |
| 8 | 3 steps: 150 | 0 / 150 | 2 steps: 142, 3 steps: 8 | 0 / 150 |

No plan longer than three steps was emitted anywhere, by either arm, at any
depth. The stepwise arm, whose whole design removes plan length from the
decoder's job, writes shorter plans as the question gets longer, not longer ones.
That is the opposite of what a decoding-side length prior predicts. The cap is in
what the model learned, and what is missing is the count of steps the question
requires, which no change to the decoding scheme supplies.

### The trivial program baseline

`src/audit/pageparser.py`, 198 lines, sixteen of them rule regexes. Handed
exactly what `direct_all` is handed, the four pages concatenated in the
retriever's order plus the question, and no gold operator, no gold plan, no gold
answer and no model.

| depth | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| style 0 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| style 2 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| style 3 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| style 4 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| transposed | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

One note in the parser's disfavour: with only the trained wording's four regexes
enabled it scores 1.000 on style 0 and 0.000 on the others, because it refuses
rather than guessing. It is as surface-bound as the model by construction. The
difference is that a new wording costs it four regexes, and the model cannot be
given four regexes.

## 4. What survives

The harness. `oracle_both` is 1.000 at every depth on the trained wording, on the
transposed pages and on the renumbered pages. Handed the transposed operator, the
executor returns the transposed truth. It computes what it is told to compute.

The gold answers and the grader. Zero disagreements across 7800 independent
re-derivations by a reader that shares no code with the generator. Whole-string
match, no slack, zero double credits across 591 opposite-gold pairs with 750 of
750 byte-identical generations. The failure mode that broke the earlier headline
in this project, a containment grader accepting a hedge, is not present here.

The executor's independence. Under `oracle_plan` the model-induced operator
object is what runs, 8850 calls out of 8850, and corrupting it or removing it
takes the condition to 0.000. Nothing is leaking through the plan channel, the
packaging, or the executor.

The untrained control. `base_untrained_direct` is 0.000 in every cell of every
kind at every depth, so nothing in the task is answerable without the fine tune.

That the plan is what fails, as bookkeeping. `oracle_both` is 1.000 and
everything the model writes falls apart past depth three. The statement is true
and nearly empty, because the thing that fails is a plan the model writes from a
signature line and a question, with no page in the prompt, and a 60-line parser
on the same two fields writes it perfectly.

The shape of the collapse. Depth four and beyond really is failure, and the
corrections make it sharper: every corrected cell there is at or below zero.

Nothing here says the numbers were fabricated. The instrumented rerun reproduces
the audited sequential row to the digit on two GPUs, and the style-0 rows of six
conditions come back identical. The numbers are real. What they measure is
template recall on one page wording, multiplied by an exact interpreter.

What does not survive at any strength is the reading the experiment was built to
support, that a small model can induce operators from retrieved pages and hand
them to an executor that composes them. On the evidence here the model recalls
operators it was trained on, recognises which template a page belongs to from its
surface, and copies the numerals. When the page and the template disagree, the
template wins 678 times out of 678.

## 5. The three running architecture experiments

All three fine-tune from the same base, hold induction fixed as the opgraph arm's
own examples, and evaluate on style-0 pages. Each of them states the dead reading
as its premise.

Plan heads, `src/opgraph/PLANHEADS.md`, opens on the equality of `plan_execute`
and `oracle_ops` at every depth, on the 350M substrate inducing and executing
"with no depth degradation that this grid can see", and on gold operators
changing nothing. The equality is false on breadth by up to 0.420 with the sign
reversed. The absence of depth degradation is a statement about an interpreter.

The vocabulary ladder, `src/opgraph/VOCAB.md`, opens with "the executor chains an
induced operator to depth eight without loss, and the loss is in emitting the
plan", and repeats the equality claim.

Latent recurrence, `src/latent/LATENT.md`, opens with "The only condition that
runs flat to depth eight, `oracle_plan`, never constructs the composition through
that channel, and it is handed a gold plan." The flatness is the interpreter, so
the contrast that motivates removing the vocabulary from between the steps is not
there.

None of the three has to stop, and the cost is not the same for each.

The internal comparisons are not damaged. Every rung of the ladder trains on
byte-identical induction examples and differs only in the plan representation, and
the plan heads differ only in how a plan is produced. Those experiments can still
answer whether representation X emits better plans than representation Y, holding
everything else fixed. That question is intact and worth answering.

What is damaged is the reading of any absolute number they produce. None of them
measures composition over retrieved knowledge, because the plan prompt has no page
in it and induction is template recall. Any rung that reaches 1.000 at depth three
has reached the number a 60-line parser on the signature line and the question
also reaches. Re-scope the claims from "the system composes over induced
operators" to "this plan representation transduces a signature line and a question
into a correct plan at rate r", and the experiments stay honest.

Four specific things need to change before any of them is read as evidence.

Every rung and every head needs the transposed-page control and at least one
held-out wording in its evaluation, reported next to the style-0 number. Without
them a rung's score is a template-recall score and there is no way to tell from
the table.

The plan heads need the length census run on P2s, P3 and P4 before their depth-4
to depth-8 cells are interpreted. The fixed-length slot array removes the length
constraint structurally, twelve nodes with an `active` field, which is exactly the
repair `runs/opgraph_step.pt` attempted on the decoding side and failed. This
audit's census says the model does not know how many steps the question needs; a
slot array does not supply that either, it relocates the question into the
`active` field. If P3 and P4 land at the floor at depths four and up, the finding
is about the missing step count and not about refinement, and the heads should say
so.

Rung E of the ladder is handed an obligation count read off the question's
surface, which the other rungs do not get. The ladder's own document flags this.
The census makes it decisive: the step count is the one quantity the model is
missing at depths four and up, so a lift at rung E is attributable to the
hand-supplied count rather than to the representation, and E cannot be compared
with the other rungs on level terms. Either supply the count to every rung or
read E only against itself.

Latent recurrence needs least re-scoping in its manipulation and most in its
framing. Condition D asks whether a continuous state can answer at all, which
does not depend on anything that died. Condition E emits an opcode plan for the
same executor, so it inherits the whole plan path, the missing step count and the
template-recall induction. Both should be reported against the parser baseline,
because a condition that does not beat 198 lines of regex on the same inputs is
not evidence about reasoning.

## Files

Everything is in `~/opg` on the training box, committed. The four writeups are
`src/audit/AUDIT_GOLD.md` for checks 1 to 4, `src/audit/AUDIT_LEAK.md` for checks
5 and 6, `src/audit/AUDIT_SEMANTICS.md` for checks 7 and 8, and this file.

Two runs are new in this pass. `src/audit/steplen.py` writes
`results/audit_steplen.json`, and `src/audit/verify_c7_ckpt2.py` writes
`results/verify_c7_opgraph2.json`.

Reproduction for the two new runs, with a GPU picked off `nvidia-smi` and pinned:

    CUDA_VISIBLE_DEVICES=7 PYTHONPATH=$PWD uv run python -m src.audit.steplen \
      --out results/audit_steplen.json --batch-size 24
    CUDA_VISIBLE_DEVICES=6 PYTHONPATH=$PWD uv run python -m src.audit.verify_c7_ckpt2 \
      --out results/verify_c7_opgraph2.json --batch-size 24
