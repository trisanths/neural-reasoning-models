# Training on the diversity corpus, and re-measuring the four failures

One fine-tuning run from `rlsimple-503-921` on
`s3://decoupled-reasoner-009398924577/data/corpus/v1/`, then every diagnostic
that has failed on this project re-measured on the new checkpoint and on the
original one under the same harness.

The question the run asks is whether the four measured limits are properties of
the training corpus or of the substrate. If held-out frame accuracy rises, if
the model starts following a page that contradicts its template, if the plan
length ceiling moves from three to forty-eight, and if the emitted symbol count
reaches two, the limits were data. If they do not move, the substrate claim has
evidence for the first time.

## Status

Numbers land in this file as they finish. Every section names the file its
numbers were read from.

## What was trained

Base checkpoint `~/rlckpt/rlsimple-503-921-final.pt`, byte identical in size to
`s3://.../runs/final/rlsimple-503-921/final.pt` (4,505,562,047 bytes).
Tokenizer `~/data/tokenizer_v2.json`.

Budget, matching the eight opgraph arms in `PREREGISTERED.md` (`--steps 8000
--batch-size 32 --lr 2e-5 --warmup 200`), which is the standard the plan length
and symbol count results were measured under:

    8,000 optimizer steps
    batch 32 sequences, run as micro-batch 8 with 4 gradient accumulations
    AdamW, lr 2e-5, betas 0.9/0.95, weight decay 0.0, grad clip 1.0
    200 warmup steps, cosine decay to a tenth
    bfloat16 autocast, one L40S

Batch 32 is reached by accumulation rather than by one forward, because a
32 x 1024 forward on this model puts the vocabulary logits alone at 4.3 GB in
float32. Nothing else deviates.

## The training stream

`src/corpus/sft.py` renders the corpus into the trace the episode environment
writes for a correct rollout, which is the trace
`src/frames/sweep.py:build_trace` writes and the one `src/rl/env.py` replays at
evaluation time:

    <|world|> preamble <|q|> question
    [ <|retrieve|> query <|result|> page ] x rounds
    <|a|> answer <|eot|>

The prompt comes from `src/rl/env.py:build_prompt`, so it carries the world
header. Without that header this checkpoint issues no retrieval round, emits no
answer marker and runs to the token cap. Loss falls on the markers, the query
and the answer; the served page carries none, which is how
`src/rl/grpo.py` masks it. Two loss terms, each normalized by its own token
count, so a frame whose question tokenizes longer cannot change how hard the
answer is trained.

Two choices in the renderer are worth stating because they could have gone the
other way.

The query is the tail of the question, not its head. Corpus questions carry a
variable-length lead-in whose only job is to hold prompt token counts equal
across frames. A query built from the head of the question would be padding in
some frames and content in others, so its retrieval quality would vary with the
frame, which is the axis being measured. Measured over a sample of 580 items,
the answering page is surfaced on 0.573 of relation questions by a tail query
against 0.555 by a head query, 0.870 against 0.866 on external and 0.960 both
ways on mathgen; the tail is chosen for the frame-independence, not for the
0.018.

Rounds run until a served page carries the gold answer, or the documents are
exhausted, or the round cap. An example is kept when the gold was served, or
the documents were exhausted, or the question is `derived_by_computation`,
whose answer is on no page by construction. Relation episodes carry two or
three pages against a cap of four, so they always exhaust and are always kept.

Realised counts, from `~/retrain/pack/*.summary.json`:

| component | file | examples | tokens | dropped unserved | dropped long |
| --- | --- | ---: | ---: | ---: | ---: |
| relation | relation_train.jsonl | 128,000 | 48,192,842 | 1,338 | 290 |
| plan, stepwise | plan_train_step.jsonl | 48,000 | 7,017,078 | 0 | 0 |
| plan, whole | plan_train_whole.jsonl | 32,000 | 9,142,884 | 0 | 0 |
| external | external_train.jsonl | 24,001 | 3,960,914 | 1,845 | 0 |
| mathgen | mathgen_train.jsonl | 21,971 | 8,707,788 | 1,933 | 94 |
| total | | 253,972 | 77,021,506 | | |

8,000 steps at 32 sequences is 256,000 sequences, so the run is 1.008 passes
over the pack. Episodes are drawn by a fixed stride over each file so the
sample spans every family and frame rather than the head of the file; the
stride and the realised counts are in the per-component summaries.

Both plan targets are trained, the whole-plan one that saturated at three steps
and the stepwise one, because which of them lifts the ceiling is the question.

Artifacts: pack `~/retrain/pack/mix1.*`, per-component packs beside it,
training log `~/retrain/logs/train.jsonl`, checkpoint
`~/retrain/corpus-v1-8k.pt`.

## One constant was raised

`src/opgraph/plan.py:MAX_STEPS` went from 32 to 128. `parse_plan` refuses
anything longer than that constant, so with it at 32 every emitted plan past 32
steps would have counted as a parse failure rather than as a long plan, and the
corpus trains to 48. Nothing else in `src/opgraph/` changed. The oracle check
below confirms the raise: the corpus's own gold plans parse and execute at
1.000 at every length from 1 to 96.

## The instruments

Five measurements, all through `src/corpus/evalrun.py` or the shipped
`src/frames/cli.py`, both checkpoints under identical settings. Greedy and
sampled are run everywhere, because greedy alone has produced false zeros on
this project. Rollouts are kept per item and aggregation is a separate pass
over the file that is kept.

The harness gate. `scripts/mg_threeway_eval.py --suite gate` on the two
`src/skillacq/` families whose values are on record, scored by
`scripts/mg_strict_rescore.py`. One code path loads the model, runs the
retrieval environment, grades and aggregates; only the episodes file changes.
The budget is `configs/mg3-gate.yaml`, the one the recorded controls were
measured under.

The transposed rule. `src/corpus/transposed.py`, described above. The
generation condition serves the transposed pages through the retrieval loop,
with a numeric grader that uses digit boundaries rather than the project's
usual letter boundaries, which would match 51 inside 351. The likelihood
condition puts the pages in the prompt and scores the five candidates by summed
negative log likelihood after an `<|a|>` marker, so a policy that generates
nothing usable still expresses a preference and a zero in generation can be
told apart from a zero in what the model prefers.

Frames. `src/frames/cli.py eval` and `score`, unchanged, over two episode sets:
the twenty frames the sweep already evaluates, and twelve more chosen to span
the shape-distance range. Held-out means the corpus never trained that frame:
the external component uses `split_frames("both")["train"]`, 72 of 156, so
thirteen of the twenty sweep frames are seen and seven are not, and all twelve
of the extended set are held out. A held-out frame's distance is the smallest
distance to any of the 72, with shape and lexicon reported apart, because a
lexicon swap and a shape swap cost different amounts and one scalar would mix
them. The extended twelve include three frames at shape distance 0.000 to 0.073
with lexical distance 0.55 to 0.66, which is a lexicon change with the geometry
held, and three imperative-question frames at shape 0.315 with lexical distance
0.125 to 0.235, which is the reverse.

`--max-new-tokens` is 192, not the 96 the sweep recorded. Four rounds of a
24-token query cost 104 model-emitted tokens before the answer, and the
environment counts every emission against the budget, so 96 cannot fit four
rounds and an answer. Both checkpoints are run at 192, so the comparison is
matched; the sweep's own numbers are not directly comparable to these and are
not quoted as if they were.

Plan length and symbol count. `src/corpus/evalrun.py plan` continues a prompt
that already ends in `<|a|>`, the shape the plan component is written in, over
the corpus's own held-out plan band and over an extrapolation set at 56, 64,
72, 80 and 96 steps that nothing trains on. Emitted step count and emitted
distinct symbols are read off the text with a regex before any parse, because a
plan the parser rejects still has an emitted length and that length is the
measurement.

Relation type. `src/corpus/evalrun.py gen` over the relation held-out band, all
sixteen structures at 100 episodes each, and over a training-band anchor at the
twelve trained structures, with the episodes the training pack drew excluded
from the anchor. Scored per family by `src/frames/score.py`, which asserts the
hedging canary at 0.000 forced on every cell before any number is read.

## Trivial-program baselines

Three of the four measurements have a program that reads what the model reads
and answers.

Frames, `python -m src.frames.cli parsers`. A frame-aware regex scores 0.992
forced on `substitution_rule` and 1.000 on `exception_rule` in every one of the
twelve extended frames, and the same regex with the native wording baked in
scores 0.000 on all twelve. The 0.992 cap is an upstream defect in
`src/skillacq/SubstitutionRule`, which can draw one key twice with two values,
and it caps every reader in every frame equally. The task is mechanically
solvable in every wording, so a model that collapses off frame is not being
defeated by a harder problem. Artifact `~/retrain/frames/parsers_ext.json`.

The transposed rule, `python -m src.corpus.transposed parsers`. A prose reader
of the swapped page recovers all 300 transposed operators exactly on eight
probe pairs, and answers 1.000 toward the page and 0.000 toward the training
identity on all 689 items, with no parse failures. The pages carry everything
the answer needs. Artifact `~/retrain/transposed/parsers.json`.

Plan, `python -m src.corpus.planparser`. A parser reading only the question
scores 1.000 at every length from 1 to 96 and every symbol count from 1 to 5 on
the determinate subset, emitting exactly the required steps and exactly the
required distinct symbols. Artifacts
`~/retrain/plan/score_parser_heldout_whole_sample.json` and
`~/retrain/plan/score_parser_extrap_whole.json`.

Running that parser found a defect in the corpus.
`src/corpus/plans.py:render_tree` writes a binary infix expression for any node
with more than two children, and `score/4` is callable in every world, so an
item using it prints two of its four operands and the question does not
determine the gold plan. 11,887 of 32,000 whole-plan training items and 1,196
of 3,199 held-out ones are underdetermined this way, 37 per cent either side.
Every plan table below carries the determinate subset beside the full one. On
the full set no reader can exceed the determinate rate, so a number above it
would be a bug.

The relation families have no such program written. What stands in for one is
the corpus's own shortcut audit in `selftest.json`: six value-blind readers, of
which the best is `random_candidate` at 0.340 against a 0.333 floor on
`band_rule`, with none above chance on a Wilson lower bound in any of the twelve
trained families, and the `keyword_nearest` frame-aware page reader, which
scores 0.826 on `substitution`, 0.167 on `chain_rule`, 0.058 on `transitive`
and 0.000 on the other nine. Extracted to
`~/retrain/relation/shortcut_floors.json`. That is weaker than a parser and it
is named as what it is: the relation table has a floor and a page-reader
reference, not a program that solves the task.

## 1. The harness gate

Run first, and nothing below it means anything if this does not reproduce. The
two `src/skillacq/` families whose values are on record, through
`scripts/mg_threeway_eval.py --suite gate` and `scripts/mg_strict_rescore.py`,
budget `configs/mg3-gate.yaml`, on the original checkpoint.

`floor` is one over the item's own candidate count. `ship` is the environment
grader as recorded. `forced` is exactly one candidate named and it is the gold.
`c_ship` and `c_frc` are chance-corrected, `(acc - floor) / (1 - floor)`.

| cell | nQ | nR | floor | ship | forced | first | c_ship | c_frc | hedge | none | rounds | wellformed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| substitution_rule greedy | 500 | 500 | 0.200 | 0.976 | 0.954 | 0.958 | 0.970 | 0.943 | 0.022 | 0.016 | 1.00 | 0.988 |
| substitution_rule t1 x4 | 500 | 2000 | 0.200 | 0.861 | 0.866 | 0.871 | 0.826 | 0.832 | 0.009 | 0.118 | 0.98 | 0.944 |
| threshold_rule greedy | 500 | 500 | 0.500 | 0.996 | 0.008 | 0.464 | 0.992 | -0.984 | 0.988 | 0.000 | 1.00 | 1.000 |
| threshold_rule t1 x4 | 500 | 2000 | 0.500 | 0.903 | 0.060 | 0.456 | 0.807 | -0.879 | 0.853 | 0.043 | 0.98 | 0.949 |

Against the record: `substitution_rule` 0.976 greedy against 0.969 on record
and 0.972 in the `src/mathgen/EVAL.md` re-run; `threshold_rule` 0.996 against
1.000 and 0.998. At temperature one, 0.861 against 0.828 and 0.874, and 0.903
against 0.922 and 0.902. The strict column reproduces the known forced-choice
regrade as well: `threshold_rule` names both of its two candidates on 0.988 of
greedy answers so 0.996 shipped becomes 0.008 forced, against 0.008 and 0.009
on record, and `substitution_rule` holds at 0.954 against 0.950 and 0.954.

The gate passes on all four cells and on both graders. Retrieval is healthy:
one round on essentially every rollout, well-formed queries on 0.94 to 1.00, no
degenerate queries.

Artifacts: `~/retrain/gate/roll_gate_base.jsonl`,
`~/retrain/gate/graded_gate_base.jsonl`, `~/retrain/gate/strict_gate_base.json`,
log `~/retrain/logs/gate_base.log`.

The same gate on the new checkpoint is not a harness check, it is a result, and
it is reported here because it is the same table.

| cell | nQ | nR | floor | ship | forced | first | c_frc | hedge | none | rounds | degen |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| substitution_rule greedy | 500 | 500 | 0.200 | 0.998 | 0.998 | 0.998 | 0.998 | 0.000 | 0.000 | 1.98 | 0.984 |
| substitution_rule t1 x4 | 500 | 2000 | 0.200 | 0.995 | 0.995 | 0.995 | 0.993 | 0.000 | 0.003 | 1.98 | 0.983 |
| threshold_rule greedy | 500 | 500 | 0.500 | 0.990 | 0.990 | 0.990 | 0.980 | 0.000 | 0.000 | 2.00 | 1.000 |
| threshold_rule t1 x4 | 500 | 2000 | 0.500 | 0.987 | 0.987 | 0.987 | 0.973 | 0.000 | 0.003 | 2.00 | 0.995 |

Two things move and one of them is large. `threshold_rule` forced choice goes
from 0.008 to 0.990. The original checkpoint names both of its two candidates
on 0.988 of greedy answers, which is why its 0.996 shipped score collapses to
0.008 under a grader that requires one; the new checkpoint hedges on 0.000 and
is right on 0.990. That is the hedging failure the project has carried since
the forced-choice regrade, and it is gone. `substitution_rule` at temperature
one goes from 0.866 forced to 0.995, so the gap between greedy and sampled
closes as well.

The `degen` column is a behaviour change, not an improvement. It counts
rollouts with an empty or a repeated query. The training traces emit the same
query on every round, because the query is the tail of the question and the
question does not change between rounds, so the new policy repeats its query
and the environment's shaping term calls that degenerate on 0.98 of rollouts.
The retrieval service serves without replacement, so a repeated query still
returns a new page, and accuracy does not suffer. It does mean the shaping
term in `src/rl/env.py` would penalise this policy in RL, and anyone who
resumes RL from this checkpoint has to know that.

Artifacts: `~/retrain/gate/roll_gate_new.jsonl`,
`~/retrain/gate/graded_gate_new.jsonl`, `~/retrain/gate/strict_gate_new.json`,
log `~/retrain/logs/gate_new.log`.

## 2. The transposed rule, in the retrieval shape

689 items kept of 750 proposed: 41 dropped because the page answer and the
training answer coincide, 20 because the page answer can be copied out of the
question. On record the same construction kept 678 of 750 with 51 and 21
dropped. 294 of 300 transposed operators are distinguishable on eight probe
pairs, against 290 of 300 on record. The prose reader recovers all 300 exactly
and answers 1.000 toward the page.

Generation, the retrieval loop, `chance` is one over the item's own five
candidates:

| checkpoint | decode | n | chance | page | training | other | hedge | none | rounds | emitted tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| original | greedy | 689 | 0.200 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | 0.00 | 14.0 |
| original | t1 x4 | 2756 | 0.200 | 0.000 | 0.000 | 0.000 | 0.000 | 0.999 | 0.05 | 84.4 |
| new | greedy | 689 | 0.200 | 0.007 | 0.010 | 0.019 | 0.000 | 0.964 | 0.98 | 14.3 |
| new | t1 x4 | 2756 | 0.200 | 0.005 | 0.009 | 0.014 | 0.000 | 0.971 | 1.20 | 16.6 |

Likelihood forced choice, the pages in the prompt, five candidates scored by
summed negative log likelihood after an `<|a|>` marker. Under a uniform
preference the three distractors would take 0.600 between them:

| checkpoint | n | chance | page | training | other |
| --- | ---: | ---: | ---: | ---: | ---: |
| original | 689 | 0.200 | 0.261 | 0.235 | 0.504 |
| new | 689 | 0.200 | 0.287 | 0.247 | 0.466 |

Read this carefully, because the honest reading is not the interesting one.

Neither checkpoint answers this task by generating. The original names no
candidate on 1.000 of greedy items and never issues a retrieval round on it;
the new one retrieves once but still names no candidate on 0.964. In
preference both sit within 0.09 of the 0.200 floor, tilted very slightly
toward the page over the training identity, 0.261 against 0.235 and 0.287
against 0.247. Neither is the 0 of 678 toward the page and 678 of 678 toward
training that is on record.

The reason is that the record's number was measured on `opgraph2.pt`, an arm
fine-tuned on `src/opgraph/` worlds in the opgraph prompt shapes, and neither
checkpoint here is that. The corpus does not train operator-page induction: its
plan component hands the scheduler a signature line, `%/2/left */2/right ...`,
and never a page that defines what `%` does. So this cell measures a lane the
corpus does not cover, on checkpoints that cannot attempt it, and the movement
in it is a tenth of a standard deviation of nothing. Section 6 runs the same
transposed pages through the two shipped opgraph conditions on the opgraph arms
themselves, which is where the recorded number lives.

Artifacts: `~/retrain/transposed/ep.jsonl` and `.audit.json`,
`~/retrain/transposed/all_base.jsonl`, `~/retrain/transposed/all_new.jsonl`,
scores `~/retrain/transposed/score_base.json` and `score_new.json`,
parser baseline `~/retrain/transposed/parsers.json`, grader oracle check
`~/retrain/transposed/score_oracle.json`.

## 3. Sentence frame, against distance

Forced choice, 200 questions per cell, chance from each cell's own option
count, on the twenty-frame set the sweep already evaluates. A frame is seen
when it is one of the 72 the corpus trained on. Held-out frames are bucketed by
the smallest shape distance to any of those 72; lexical distance is 0.53 to
0.83 in every held-out bucket, so every one of them is a lexicon change as
well as whatever shape change it carries.

`substitution_rule`, greedy, chance 0.200:

| bucket | frames | n | original forced | new forced | new none | new served |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| seen by the corpus | 13 | 2600 | 0.140 | 0.990 | 0.007 | 0.993 |
| held out, shape 0.00-0.05 | 2 | 400 | 0.085 | 1.000 | 0.000 | 1.000 |
| held out, shape 0.12-0.22 | 1 | 200 | 0.025 | 0.985 | 0.010 | 1.000 |
| held out, shape 0.22-0.30 | 3 | 600 | 0.022 | 0.747 | 0.008 | 1.000 |
| held out, shape 0.30+ | 1 | 200 | 0.000 | 0.995 | 0.000 | 1.000 |

`exception_rule`, greedy, chance 0.500:

| bucket | frames | n | original forced | new forced | new none | new served |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| seen by the corpus | 13 | 2600 | 0.427 | 0.827 | 0.129 | 0.827 |
| held out, shape 0.00-0.05 | 1 | 200 | 0.310 | 0.505 | 0.035 | 0.515 |
| held out, shape 0.05-0.12 | 1 | 200 | 0.000 | 0.990 | 0.000 | 0.990 |
| held out, shape 0.12-0.22 | 2 | 400 | 0.463 | 0.980 | 0.000 | 0.980 |
| held out, shape 0.22-0.30 | 1 | 200 | 0.070 | 0.715 | 0.275 | 0.715 |
| held out, shape 0.30+ | 2 | 400 | 0.535 | 0.990 | 0.005 | 0.990 |

Macro over the twenty frames within a family, both aggregation orders, greedy:

| checkpoint | family | cells | macro acc | macro chance | A, corrected macro | B, mean of corrected |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| original | substitution_rule | 20 | 0.104 | 0.200 | -0.120 | -0.120 |
| original | exception_rule | 20 | 0.396 | 0.500 | -0.208 | -0.208 |
| new | substitution_rule | 20 | 0.955 | 0.200 | 0.943 | 0.943 |
| new | exception_rule | 20 | 0.845 | 0.500 | 0.691 | 0.690 |

At temperature 0.7 the same table reads -0.109 and -0.307 for the original and
0.941 and 0.634 for the new one, so nothing here is a greedy artifact.

The original checkpoint reproduces its recorded shape exactly. Its one high
cell is `routing__native`, 0.940 forced on `substitution_rule`, which is the
0.940 the frame ablation records; every other frame in the set is at or below
its floor, and the macro over twenty frames is below chance in both families.
`assembly__imperative` is the imperative-question frame the ablation reports as
emitting no retrieve token: the original serves the answering page on 0.000 of
its 200 rollouts in both families and names no candidate on 1.000 of them.

The new checkpoint is at 0.985 or better in four of the five
`substitution_rule` buckets, including the two furthest from anything it
trained on. `assembly__imperative`, where the original could not retrieve at
all, is 0.995 forced with the page served on 1.000. Held-out accuracy does not
merely rise toward seen accuracy; in three buckets it is level with it.

The exception is one bucket and it should not be smoothed over. Shape 0.22 to
0.30 on `substitution_rule` is 0.747, held down by `abstract__tablepipe` at
0.260 with the page served on 1.000 of its rollouts and no candidate named on
only 0.015. That is a reading failure with the page in context, on the one
held-out frame that is a pipe-delimited table, and it is the only cell in the
new checkpoint's `substitution_rule` table below 0.90.

Retrieval and reading come apart on `exception_rule` and the split is not about
frames. Every cell where the new checkpoint scores below 0.9 on that family has
`acc_forced` equal to `served_rate` to within 0.01, and four of the six such
cells are frames the corpus trained on. That family's residual is a retrieval
failure, not a wording failure.

Artifacts: `~/retrain/frames/score_{base,new}-{greedy,t07}.json`, dumps under
`~/retrain/frames/dump_*`, distances `~/retrain/frames/frame_distance.json`,
curve `~/retrain/frames/curve.json`. Every dump was written after the episode
files it came from; `src/frames/cli.py score` refuses to score otherwise, and
it asserts the hedging canary at 0.000 forced on all forty cells before any
number above is read.

## 4. Plan length

Two item sets. The corpus's own held-out plan band, lengths 1 to 48, which is
the grid the corpus trains on. And an extrapolation set at 56, 64, 72, 80 and
96 steps, built by `src/corpus/build.py:build_plan_records` from seeds at
760,000,000, outside every reserved range and both corpus bands, which nothing
trains on.

Everything below is the determinate subset, the items whose question determines
the gold plan. `acc` is the executed answer against gold; `planEx` is the
emitted plan string equal to the gold plan string. Both are given because the
first can be right with the second wrong, and on this data that happens a lot;
the next subsection is about how much.

New checkpoint, held-out band, greedy:

| required steps | n | acc | planEx | emitted steps, mean | emitted max | long enough |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 36 | 1.000 | 1.000 | 1.00 | 1 | 1.000 |
| 2 | 49 | 1.000 | 1.000 | 2.00 | 2 | 1.000 |
| 3 | 46 | 1.000 | 1.000 | 3.00 | 3 | 1.000 |
| 4 | 55 | 1.000 | 1.000 | 4.00 | 4 | 1.000 |
| 6 | 64 | 0.984 | 0.984 | 6.00 | 6 | 1.000 |
| 8 | 60 | 0.983 | 0.983 | 8.00 | 8 | 1.000 |
| 12 | 43 | 0.977 | 0.954 | 12.00 | 12 | 1.000 |
| 16 | 35 | 0.829 | 0.800 | 16.06 | 18 | 1.000 |
| 20 | 49 | 0.898 | 0.898 | 20.16 | 28 | 1.000 |
| 24 | 39 | 0.744 | 0.744 | 24.20 | 28 | 1.000 |
| 28 | 49 | 0.714 | 0.694 | 27.98 | 28 | 0.980 |
| 32 | 36 | 0.694 | 0.667 | 32.00 | 32 | 1.000 |
| 36 | 30 | 0.533 | 0.500 | 36.13 | 40 | 1.000 |
| 40 | 33 | 0.545 | 0.545 | 40.36 | 48 | 1.000 |
| 44 | 22 | 0.273 | 0.227 | 44.55 | 50 | 0.909 |
| 48 | 26 | 0.154 | 0.154 | 47.69 | 50 | 0.885 |

New checkpoint, extrapolation set, nothing trains past 48:

| required steps | n | acc greedy | emitted mean greedy | emitted max | long enough greedy | emitted mean t1 | long enough t1 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 56 | 40 | 0.000 | 56.20 | 88 | 0.400 | 58.08 | 0.550 |
| 64 | 15 | 0.000 | 64.33 | 90 | 0.467 | 61.13 | 0.467 |
| 72 | 33 | 0.000 | 64.67 | 95 | 0.212 | 65.06 | 0.303 |
| 80 | 52 | 0.000 | 72.85 | 96 | 0.250 | 70.96 | 0.192 |
| 96 | 38 | 0.000 | 76.50 | 95 | 0.000 | 75.82 | 0.053 |

The original checkpoint emits no plan at all on either set. Its emitted step
count is 0.00 at every length, its accuracy and its plan-exact rate are 0.000
everywhere, and what it writes is text like `Vramgrum`, `1.` and
`1 add ops ops ops`. It has never seen the format, so it is a control on the
harness rather than a comparison of capability.

Three things are true and the first two are the answer to the question.

The step count is no longer flat. Emitted length equals required length to two
decimal places at every one of the eighteen trained lengths, from 1.00 at one
step to 47.69 at forty-eight. On record the emitted count tracked the question
to three and then sat on three exactly, so a depth-eight question got a
three-step plan. Nothing like that survives here.

It does not flatten at the new training maximum either. Past 48, where nothing
trains, mean emitted length keeps rising: 56.20 at required 56 and 64.33 at 64,
both above the training ceiling, with individual plans up to 111 steps. The
extrapolation constant on record was zero, meaning no arm generalised one step;
this one generalises about sixteen. Past 64 the emitted length falls behind the
requirement, 64.67 where 72 is needed and 76.50 where 96 is, so there is a soft
ceiling somewhere around seventy and it is not the training maximum.

Accuracy is a different question from length and it does not follow. Within the
trained band, accuracy decays smoothly from 1.000 at four steps to 0.154 at
forty-eight, which is a decay and not the step function on record, where
accuracy was 1.00 at and below the ceiling and chance above it. Past the
training band accuracy is 0.000 at every length, on both decodes: the model
writes a plan of roughly the right length and gets it wrong. The trivial
program writes the exact gold plan at 1.000 on every one of those cells, so the
loss is not in the question.

Sampled decoding agrees with greedy throughout, so none of this is a greedy
artifact.

### The collision that makes the full-set number meaningless

Items using the arity-four `score` are underdetermined, as described above.
They are also collision-prone, and the two together make their accuracy column
worthless. On the held-out band the new checkpoint's executed answer is right
on 0.642 of those items while its plan is exactly right on 0.000 of them; on
the extrapolation set the same numbers are 0.311 and 0.000. On the determinate
items the two agree: 0.851 value-correct against 0.843 plan-exact, a gap of
0.008.

So a wrong plan lands on the right value about two times in three on the
underdetermined items, and every accuracy figure that pools them is inflated by
that. Every number in this section is the determinate subset only. Anything
reported on the full set would exceed the ceiling a question-only reader can
reach, which is the pattern this project treats as a bug until proven otherwise.

## 5. Symbol count

Distinct operator symbols emitted against required, same items, determinate
subset, new checkpoint.

| required symbols | n | acc greedy | emitted symbols greedy | enough greedy | emitted symbols t1 | enough t1 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 278 | 0.982 | 1.000 | 1.000 | 1.007 | 1.000 |
| 2 | 280 | 0.868 | 2.000 | 1.000 | 2.032 | 1.000 |
| 3 | 136 | 0.699 | 3.007 | 1.000 | 3.118 | 1.000 |
| 4 | 42 | 0.262 | 4.000 | 1.000 | 4.119 | 1.000 |
| 5 | 54 | 0.926 | 4.981 | 0.982 | 4.981 | 0.982 |

On the extrapolation set, where the plans are longer than anything trained, the
emitted symbol count is still right: 1.231, 2.462, 3.424 and 5.800 where 1, 2,
3 and 5 are required, with `enough_symbols` at 1.000 in every cell.

On record every arm emitted about 1.0 distinct symbols where 2 were needed, on
novel composition, at chance. Here the emitted count equals the required count
at every width from one to five, and the model reaches for a second, third,
fourth and fifth symbol when the question needs one. The symbol-count ceiling
is gone.

Accuracy at four required symbols is 0.262, below both three and five, on 42
items. That is not a symbol-count effect: the four-symbol cell in this sample
is drawn from the longest plans, and length is what the accuracy tracks.

Artifacts: `~/retrain/plan/all_{base,new}_{heldout_whole_sample,extrap_whole}.jsonl`,
scores `~/retrain/plan/score_*`, per-item rows `~/retrain/plan/rows_*`,
record sets `~/retrain/plan/heldout_whole_sample.jsonl` and
`~/retrain/plan/extrap_whole.jsonl` with the `determinate` flag on every
record, trivial program `~/retrain/plan/parser_*` and `score_parser_*`,
oracle `~/retrain/plan/score_oracle_*`.
