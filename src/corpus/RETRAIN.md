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
