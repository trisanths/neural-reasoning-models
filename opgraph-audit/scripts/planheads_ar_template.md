# The autoregressive plan heads, P1 and P2

P1 writes a plan in the page's own operator symbols. P2 writes the same plan in
dedicated opcode tokens, one token per operator. Both decode causally through
the pretrained `lm_head`, both add no new parameters, and both are trained on
plans of at most three steps. Everything else in `src/opgraph/PLANHEADS.md`
holds: same base checkpoint, same reader, same worlds and seeds, same questions,
same executor, same optimizer steps, same sequences per step, same held-out
sets.

Depths one to three are in distribution. Everything past three, and all of
novel composition, is extrapolation.

## What is new here, in one paragraph

Neither head degrades with depth. Both write a plan of exactly three steps at
almost every question depth from four to thirty two, on 150 of 150 items, and
the plan is well typed and parses. The single exception is P1 at depth six,
where it writes one step. Over 34,200 scored items past the holdout, at
three temperatures and both page wordings, no plan longer than three steps was
ever produced. The compute spent is the same at depth thirty two as at depth
three: 28 forward passes and 27 generated tokens for P1, 31 and 30 for P2. So
the depth curve past three is not measuring composition capacity. It is
measuring a length prior that sits at exactly the maximum plan length in
training, and the same prior turns up again on the breadth axis as a cap on the
number of arguments a single step may take.

## The grid, and where it stops

Sequential depth runs 1 2 3 4 5 6 8 12 16 32. Thirty two is the ceiling of the
harness, not a choice: `plan.MAX_STEPS` is 32 and `parse_plan` rejects more than
`MAX_STEPS + 1` chunks, so a gold depth 32 plan fills the parser exactly and a
gold depth 40 plan raises `plan too long` before any head is involved. The world
generator itself has no limit; it produced depth 40 items fine. Nothing past 32
can be scored without changing the executor, so the extrapolation stops there
and 32 is reported as reached rather than as a target that was missed.

The generation cap is 320 tokens for both heads, raised from the shared default
of 160. A gold depth 32 plan costs up to 260 tokens in P1's spelling and 292 in
P2's, so a cap of 160 would have truncated the only correct answer and the deep
cells would have been reporting the cap. At 320, `at_generation_cap` is 0 in
every cell of the grid for both heads, so the cap never binds and no number
below is a truncation artifact.

## Harness check

`oracle_both` supplies the gold plan and the gold operators, so the executor
answers alone. `oracle_both_roundtrip` pushes the same gold plan through the
head's own plan representation and back first, which for P2 means the opcode
spelling and the mapping back.

{{harness}}

Both are 1.000 in all 34 cells of the grid, for both heads and both page
wordings. That is 40,800 gold executions with no failure, including every cell
at depth 32.

The reported forward count is checked against the model rather than against the
bookkeeping that produced it. `ForwardCounter` hooks `model.tok_emb`, which
every path through the backbone touches once per stack invocation.

{{counter}}

## Training, and the holdout it asserts

{{training}}

The holdout is asserted over the whole plan pool before the first optimizer
step. No training plan is deeper than three steps and no training plan uses two
distinct induced operator symbols. Both heads drew the same 160,000 plans in the
same order. The depth histogram matters for reading everything below: 58 percent
of training plans are one step long and none is longer than three.

No sequence was dropped for exceeding `max_len` in either arm, so the two heads
took the same number of sequences per optimizer step.

## Convergence check

The smoke run left an open question: at a matched step count an arm can look
worse because it is further from convergence. For P1 against P2 that risk is
small, since both reuse the pretrained `lm_head` and write a similar number of
tokens, but it is checked rather than assumed. Each head was trained twice, at
4000 and at 8000 steps, both under a full cosine schedule, so the shorter run is
an annealed run and not a prefix of the longer one.

{{convergence}}

Doubling the budget does not move the cliff, does not move the floor, and does
not change the shape. On the paraphrased wording it makes both heads worse, which
is the expected sign of a longer fit to the training page prose. The comparison
below is therefore about the plan representation and not about how far from
convergence each arm sits.

## Sequential depth, original page wording

Greedy decoding.

{{acc_sequential_orig_t0}}

Sampled at temperature 0.8.

{{acc_sequential_orig_t08}}

Sampled at temperature 1.0.

{{acc_sequential_orig_t1}}

The parenthesised family, which is a different tree shape over the same single
operator, gives the same picture.

{{acc_sequential_paren_orig_t0}}

The following hold at every depth on this grid.

`plan_execute` equals `oracle_ops` to three decimals in every sequential cell,
so gold operators change nothing and induction is not the sequential bottleneck.
This reproduces the earlier finding and extends it from depth eight to depth
thirty two.

`oracle_plan` is 1.000 at every depth from one to thirty two, under both heads,
at all three temperatures. Conditional on a correct plan the 350M substrate
induces the operators itself and the executor runs them, with no depth
degradation this grid can see, four times further out than before.

Greedy and sampled agree. The policy is close to deterministic on this task, and
the sampled columns exist so a greedy zero is never reported alone.

## The shape

{{fits}}

The cliff and the geometric decay are fitted to the same points. On the original
wording the cliff wins on residual by a factor of 7,600 for P1, 0.0003 against
2.2825, and by 2,200 for P2, 0.0010 against 2.1954. Both heads are plateau at
1.000 through depth three, then a floor of 0.021 and 0.028 that does not decline
further out to depth thirty two.

That flat floor is worth stating plainly. Accumulating per step error produces a
curve that keeps falling. This one stops falling at depth four and stays there:
P1 scores 0.020 at depth four and 0.020 at depth thirty two, P2 0.040 and 0.033,
with n = 150 in each cell. Everything past depth four costs nothing more because
there is nothing left to cost. What happens at depth four is a switch flipping
rather than a decay starting, and the two residuals say so.

## What the head actually writes

The step count separates two failures that bare accuracy folds together. A head
that writes three steps at depth sixteen has stopped early. A head that writes
sixteen wrong steps has planned wrongly.

{{steps_hist}}

Both heads write exactly three steps at every question depth from four to thirty
two, on 150 of 150 items, with one exception: P1 at depth six writes a one step
plan for 132 of 150 items. That anomaly is real and is not smoothed over; it has
no counterpart in P2 and no explanation here.

Sampling does not change it.

{{sampling}}

Over 2,850 items per cell, at temperatures 0.0, 0.8 and 1.0, on both page
wordings, on the sequential, parenthesised and novel families together, the
longest plan either head ever wrote is three steps. Not one item in 34,200
produced a fourth. The horizon is not an argmax artifact.

Here is what that looks like.

{{examples}}

At depth four both heads consume the first two operands and then reach for the
last one, closing in three steps. At depth thirty two, given a chain of thirty
three operands, both write the identical plan: the first two operands, then the
final operand, then `ans`. The head is reading the question, since it picks the
correct last operand out of thirty three, and it is applying a three step
template to it. It is not losing track partway through a long plan; it never
starts one.

## Sequential depth, paraphrased page wording

The plan prompt contains the operator signature line and the question, never the
page text. The page wording reaches these heads only through induction, and the
question text is generated from the world's glyphs, which style 1 does not
change. So `oracle_ops`, which supplies gold operators, should see the same input
under both wordings, and every paraphrase effect below should be an induction
effect. That is a claim about the harness, so it is checked.

{{wording}}

The largest accuracy difference between the two wordings under `oracle_ops` is
0.000 over every cell of the grid, for both heads at all three temperatures.

{{acc_sequential_para_t0}}

{{induction}}

Induction on the original wording is identical between the heads at 0.954 exact
text, which is what a matched pair should give. On the paraphrase it falls to
0.453 for P1 and 0.412 for P2, and page parse rate falls to 0.877 and 0.833.
That difference between the heads is not about plan representation. The plan
objective is the only thing that differs between the two fine tunes, but it
moves the shared backbone, and induction rides on the shared backbone.

`oracle_plan` on the paraphrase is flat from depth two out to depth thirty two,
between 0.373 and 0.493 for P1 and between 0.593 and 0.647 for P2, against a
gold plan at every one of those depths. So the depth flatness of
`oracle_plan` survives the wording change; what the wording change costs is a
constant, and the constant is induction.

## Novel composition

Two operator symbols, each defined alone on its own page, never trained
together. The training holdout asserts that no training plan uses two distinct
induced symbols.

{{acc_novel_orig_t0}}

{{examples_novel}}

`oracle_plan` is 1.000 at every novel depth from two to twelve under both heads,
so induction and execution both handle these worlds. `plan_execute` is 0.027 and
below. The whole of novel composition fails in plan construction.

The mechanism is visible in the diagnostics. At novel depth two P1 writes a two
step plan on every item, gets the first step right on 0.927 of them, and scores
an exact gold plan rate of 0.000. It writes the right number of steps and then
uses the first step's operator again for the second. Each head picks one symbol
and commits to it for the whole plan, which is exactly what a head trained only
on single symbol plans would do.

{{diag_p1_novel}}

{{diag_p2_novel}}

## Relational breadth

The registered prediction is that breadth does not move, because it fails at
induction. On the accuracy numbers the prediction holds.

{{acc_breadth_orig_t0}}

`oracle_plan` is 1.000 at breadth one to three and 0.000 at breadth four and
above, while `oracle_both` is 1.000 throughout. Breadth did not move. Neither
head touched it.

The localisation underneath that number needs correcting, and this is the part
that was not predicted. `oracle_ops` hands the head a perfect operator table and
is also 0.000 at breadth four and above, on 150 of 150 items, with every failure
recorded as an execution error rather than a wrong value. Planning fails at
breadth too, independently of induction.

{{examples_breadth}}

Training draws breadth from one, two or three, so the widest `score` call a head
ever saw takes a value and three flags. At breadth four the question lists four
flags and both heads write three. At breadth six it lists six and both heads
still write three. This is the same length prior as the three step cap, applied
to argument count instead of step count.

Induction truncates in the same place. The head's four argument call is scored
well typed on 1.000 of items at breadth four, and well typed is an exact arity
match, so the induced `score` operator has arity four there as well. That is why
`oracle_plan`, holding a gold plan with five or seven arguments, raises against
the induced table on 150 of 150 items.

So breadth fails twice over, at induction and at planning, and each failure
alone is sufficient. The earlier reading, that breadth fails at induction and
not at planning, rested on `oracle_plan` against `oracle_both`; that comparison
shows induction fails but says nothing about whether planning would have
succeeded. `oracle_ops` is the comparison that answers it, and it says planning
fails as well.

{{diag_p1_breadth}}

{{diag_p2_breadth}}

The known no-op trap is present and is caught by the diagnostics rather than
hidden by them. `plan_execute` scores 0.300 for P1 and 0.433 for P2 at breadth
four, above the 0.000 those same heads score with gold operators. Those correct
answers come from a wrong plan evaluated against an equally wrong induced
operator, where the flag the head dropped happened not to change the score.
`exact_gold_plan_rate` and `first_step_correct_rate` are both 0.000 in those
cells. Accuracy alone would have read as partial success.

## Plan level diagnostics

Kept apart from accuracy and never folded into it.

P1, sequential, `plan_execute`, greedy, original wording.

{{diag_p1_sequential}}

P2, same.

{{diag_p2_sequential}}

The gap between "a plan parses" and "the answer is right" is where the remaining
failure lives, and past depth three it is the whole of it. Parse rate is 1.000 or
near it at every depth. Well typed rate is 1.000 or near it at every depth. Exact
gold plan rate is 0.000 at every depth past three. Parsed but wrong rate is 0.96
to 0.99. Nothing is malformed; everything is the wrong plan.

`prefix_of_gold_rate` rules out the gentlest reading of the three step cap. If
the head wrote the first three steps of the gold plan and stopped, the three
steps it produced would be a correct prefix and only the stopping rule would
have failed. It is 0.073 for P1 at depth four and 0.033 for P2. The head does
not truncate a correct plan; it writes a three step plan whose last step reaches
for the end of the question.

## Compute spent on plan construction

`fwd_passes` is stack invocations, `slot_decisions` is discrete symbols
committed, and `position_evals` is positions whose hidden states were newly
computed. For these two heads a forward pass is one cached decode step, so
`fwd_passes` is the prompt pass plus the tokens the item generated before its own
end of text.

The per cell numbers are in the diagnostic tables above. The summary is that
compute is flat past depth three. P1 spends 28 forward passes and generates 27
tokens at question depth 3, 4, 8, 12, 16 and 32 alike. P2 spends 31 and 30 in the
same cells. Only `position_evals` grows with depth, from 75 to 133 for P1, and
that growth is entirely the question getting longer in the prompt, not the plan
getting longer in the output.

This is the compute reading of the same fact. The head does not run out of
budget at depth four. It declines to spend more.

Every cell, greedy, original wording.

{{compute}}

P2's prompt is wider than P1's by the opcode binding column, which shows up as
28 to 30 extra position evaluations per item in every cell. That is stated below
rather than corrected for.

## What is not matched

Both of these are inherited from the shared design and neither is hidden.

P2 carries the opcode binding column in the prompt, 53 tokens against P1's 26 on
a six operator world, because it writes a plan in opcodes rather than in the
page's own symbol. The column adds no semantics: the symbol, the arity and the
associativity are the same facts P1 gets. It costs positions, and the difference
is visible in `position_evals_mean` throughout.

The two fine tunes produce two different backbones, so induction quality differs
between the heads even though the induction objective and data are identical.
On the original wording the difference is nil, 0.954 against 0.954. On the
paraphrase it is 0.453 against 0.412, and in one place it is much larger than
that: on paraphrased breadth one worlds P1's `oracle_plan` scores 0.940 and P2's
scores 0.000, which is induction failing on 150 of 150 worlds for one head and
almost none for the other. Any comparison of `oracle_plan` on the paraphrase
between the heads is reading that difference and not the plan representation.

## What this licenses and what it does not

Established by this run.

Conditional on a correct externally supplied plan, the 350M substrate induces
the operators from the page and the executor runs them, with no depth
degradation from one step to thirty two, on 150 items a cell, under both heads
and at three temperatures. That is `oracle_plan` at 1.000 across the whole
sequential grid. It is a stronger version of what was already known, and it is
still conditional on a gold plan.

Not established, and specifically not what the depth curve past three shows.

The `plan_execute` collapse at depth four is not evidence that the substrate
cannot compose past three steps. Both heads emit a fixed three step plan at every
depth past the training maximum, never attempt a fourth, and spend constant
compute doing it. The measurement cannot distinguish "cannot compose deeper" from
"learned to stop at three", because the head never produces a plan long enough
for the first hypothesis to be tested. H10 as registered says the wall may belong
to the number of sequential discrete planning decisions; for P1 and P2 the wall
sits at exactly the largest number of decisions the training distribution
contained, which is the reading a length prior predicts and does not separate
from the reading H10 proposes.

The same caveat applies to breadth. Both heads write exactly three flags whatever
the question asks, which is the widest they were trained on.

What would separate them. `data.step_prompt` and the `opgraph_step` arm already
exist in this repo and were built for this: asking for one step at a time removes
plan length as something the decoder has to predict, so a plan of any length
becomes the same short decision taken repeatedly and the length prior has nothing
to attach to. Scoring a stepwise scheduler against P1 on this same grid would
say whether the horizon is the length prior or the composition. Until that is
run, the depth curve of an autoregressive plan head past its training maximum
should be read as a statement about the training distribution.

Also unlicensed here. Nothing in this report compares P1 or P2 to P2s, P3 or P4.
The refinement pass and slot revision measurements the brief asks for belong to
those heads and are not attempted.

## Files

Every number above comes from these artifacts.

| path | what it holds |
|---|---|
| `scripts/planheads_ar_eval.py` | the eval: the shared planners and grader, with the extended depth grid, the generation cap as an argument, and the per cell length diagnostics |
| `scripts/planheads_ar_blocks.py` | every table and every fit in this document, built from the result files |
| `scripts/planheads_ar_doc.py` | splices those blocks into `scripts/planheads_ar_template.md` to produce this file |
| `scripts/planheads_ar_template.md` | the prose, with the tables as placeholders |
| `results/ar/p1_s8000.json`, `results/ar/p2_s8000.json` | every cell of the full grid, both wordings, three temperatures |
| `results/ar/p1_s4000.json`, `results/ar/p2_s4000.json` | the sequential curve at the shorter budget |
| `results/ar/blocks.json` | the tables above as data |
| `runs/ar/p1_s8000.pt`, `runs/ar/p2_s8000.pt` | the two arms, 8000 steps, not tracked |
| `runs/ar/p1_s4000.pt`, `runs/ar/p2_s4000.pt` | the convergence controls, 4000 steps, not tracked |
| `runs/ar/*.pt.log.json` | loss curve, holdout assertion, dropped sequence counts |
| `logs/ar_train_*.log`, `logs/ar_eval_*.log` | the runs themselves |

No shared head code was modified. `planheads_ar_eval.py` imports `grade`,
`make_planner`, `GoldPlanner`, `SlotPlanHead`, `ForwardCounter` and
`mixture_for` from `src.opgraph.planheads`, so a plan is built and judged by
exactly the shared path; what it changes is the depth grid, the generation cap
and the per cell length diagnostics.

Commands, for reproduction.

```
cd ~/opg && export PYTHONPATH=$PWD
CUDA_VISIBLE_DEVICES=N uv run python scripts/planheads_train.py \
  --base ckpt/base350.pt --tokenizer /home/ec2-user/data/tokenizer_v2.json \
  --head p1 --out runs/ar/p1_s8000.pt --steps 8000 --batch-size 32 --worlds 40000
CUDA_VISIBLE_DEVICES=N uv run python scripts/planheads_ar_eval.py \
  --ckpt runs/ar/p1_s8000.pt --tokenizer /home/ec2-user/data/tokenizer_v2.json \
  --out results/ar/p1_s8000.json --n 150 --batch-size 96 --max-new 320 \
  --styles 0,1 --temperatures 0.0,0.8,1.0 --verify-counter
uv run python scripts/planheads_ar_blocks.py results/ar/blocks.json \
  results/ar/p1_s8000.json results/ar/p2_s8000.json \
  results/ar/p1_s4000.json results/ar/p2_s4000.json
python3 scripts/planheads_ar_doc.py scripts/planheads_ar_template.md \
  results/ar/blocks.json src/opgraph/PLANHEADS_AR.md
```
