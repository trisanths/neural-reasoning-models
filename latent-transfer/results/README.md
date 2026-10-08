# Experimental record

Raw logs and metrics pulled from both training boxes. Weights are not included
(checkpoints are 1-16 GB and live on the remotes until teardown).

## l40s_prosqa - Qwen2.5-0.5B -> 7B on ProsQA (AWS g6e.2xlarge, L40S 46GB)

Stage-0 baselines, then cross-model pipeline runs at several configurations.

  qwen05b/    0.5B stage 0            test exact 0.6900 (pre-fix generation budget)
  eval_small.json  0.5B re-scored     test exact 0.7340, by hop: 3=0.723 6=0.833
  qwen7b/     7B stage 0 (LoRA)       test exact 0.9920
  pipe_m32/   pipeline, frozen rx     test exact 0.7220
  pipe_random/ CONTROL random rx      test exact 0.7600
  pipe_fixed/ pipeline, all fixes     test exact 0.7300

FINAL (n=500):
  0.5B alone                     0.7340
  pipeline, frozen receiver      0.7220
  pipeline, adapted + scale fix  0.7300
  CONTROL random receiver        0.7600
  7B alone                       0.9920

Every pipeline variant lands within noise of the floor and the random-receiver
control scores highest, so nothing crossed between the models under any
configuration. The receiver adaptation and scale fixes that took the small-scale
experiment from 0.7485 to 0.9995 changed nothing here.

ProsQA also turned out to be the wrong instrument: the 0.5B does not degrade
with chain length (0.723 at 3 hops, 0.833 at 6), so there is no capacity deficit
for a larger model to supply.

## h200_hotpot - Qwen2.5-0.5B -> 7B on HotpotQA distractor (H200 143GB)

Chosen because the pipeline's compute saving requires a long context to
compress, and because the capacity gap there is real.

  hp_small/       0.5B stage 0             test exact 0.4820
  hp_big/         7B stage 0 (LoRA)        test exact 0.5960
  hp_pipe_m32/    pipeline, adapted rx     test exact 0.3380
  hp_pipe_random/ CONTROL random rx        test exact 0.3620

pipeline - control = -0.024, about 1.1 standard errors on n=500, so not
distinguishable: no reasoning crossed. Both arms also land BELOW the 0.5B
alone, so the handoff is actively destructive rather than merely useless.

That points at the projector, not the receiver. Calibration against the
small-scale run that reached 0.9995:

                      small-scale (worked)   HotpotQA (failed)
  projector params    0.082M                 16.06M   (195x larger)
  stage 1 + 2 steps   3850                   600      (6.4x fewer)

Roughly three orders of magnitude less training per parameter. An undertrained
projector emits vectors the small model cannot interpret, and what sits on the
far end is then irrelevant -- which is exactly why the control matches.
hp_pipe_long/ tests this directly at 8000 steps.

## Context lengths and why they decide the economics

  GSM8K       62 tok  -> pipeline costs 10.54x the small model, 2.7x cheaper than 7B-CoT
  ProsQA     326 tok  ->                 2.66x,                 7.6x cheaper
  HotpotQA  1403 tok  ->                 1.45x,                12.3x cheaper
