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
