# Stage B: the pretrain comparison, and what it answers

Every document in `decoupled-reasoner/` predates this result. The last commit of
the original repository is 2026-09-04T04:40Z; the Stage B checkpoint was written
at 2026-09-04T06:12Z and its evaluation artifacts a few minutes later. The
unattended driver that was supposed to record it had died, so the repository
still says the comparison is outstanding. It is not. The artifacts are in
`results/s3/runs/e3-350m/eval/` and this document reads them.

## What the comparison was for

Stage A is a 350M-class model trained from scratch on regime_e3 for 26,700
steps and 6,999,244,800 tokens, 18.64 tokens per parameter, cosine fully
annealed, final loss 2.5409, zero restarts. The question was whether a larger
and more diverse pretrain moves the reading failures that the program had been
attributing to data volume.

Stage A alone could not answer that, because the older corpus-v1-8k checkpoint
it would be compared against had already had supervised fine-tuning and this one
had not. Stage B removes that asymmetry: the identical fine-tuning pack is
applied to both checkpoints, so the pair differs only in the pretrain beneath
it. In the artifacts the new pretrain is `e3sft` and the reference is `ref`.

`src/norm/GAP.md` registered the prediction that would separate two explanations
before either arm ran. If tokens fix binding, `lookup`, `inverse` and
`priority` move first and their transposition share collapses. If tokens fix
capacity, `sum_chain` and `compose` move and the small shapes' transposition
share stays.

## MMLU does not move

Five-shot, completion format, seed 1234, 375,440,384 parameters, floor 0.2500.

| arm | n=500 | n=1000 |
|---|---:|---:|
| Stage A, pretrain only (`e3final`) | 0.2720 | 0.2510 |
| Stage B, pretrain plus SFT (`e3sft`) | 0.2700 | 0.2490 |

The fine-tuning changes MMLU by 0.0020 at n=500 and by 0.0020 at n=1000, in the
direction of the floor. Both arms sit on the floor at both sample sizes.

## The shape-level comparison is a wash

Each cell is forced-choice accuracy over 200 items.

| condition set | shapes | Stage B | reference | mean delta | better | worse | within 0.01 |
|---|---:|---:|---:|---:|---:|---:|---:|
| rule shapes, greedy | 40 | 0.8841 | 0.9000 | -0.0159 | 4 | 3 | 33 |
| rule shapes, t=0.7 | 40 | 0.8824 | 0.8850 | -0.0026 | 9 | 4 | 27 |
| held-out shapes | 28 | 0.6191 | 0.5748 | +0.0443 | 9 | 7 | 12 |

Thirty-three of forty rule shapes land within 0.01 of each other. The held-out
mean is the only one that moves, and almost all of it comes from two shapes.

## What moved, and why it is not reasoning

The four largest movements in either direction all pair with a large change in
how often the model emits an answer the grader can parse.

| shape | Stage B | reference | delta | none rate, Stage B | none rate, reference |
|---|---:|---:|---:|---:|---:|
| `priority_list`, greedy | 0.825 | 0.330 | +0.495 | 0.010 | 0.545 |
| `abstract__active, exception_rule` | 0.525 | 0.985 | -0.460 | 0.220 | 0.000 |
| `panel__active, exception_rule` | 0.525 | 0.975 | -0.450 | 0.125 | 0.000 |
| `abstract__tablepipe, exception_rule` | 0.990 | 0.715 | +0.275 | 0.010 | 0.275 |
| `two_key`, greedy | 0.350 | 0.075 | +0.275 | 0.565 | 0.875 |

Across all 108 shape-conditions in the three sets, the correlation between the
accuracy delta and the none-rate delta is -0.9070. Where the none rate moves by
more than 0.05, in 13 conditions, the mean absolute accuracy delta is 0.2496.
Everywhere else it is 0.0073, a factor of thirty-four.

Restricting to the 71 shape-conditions where both arms emit a parseable answer
on at least 98 percent of items, the mean delta is **-0.0009**, and exactly two
conditions move by more than 0.05: `lookup_then_band` at -0.055 and
`transitive` at -0.055, both against the new pretrain.

So the pretrain swap changed the model's answer policy and left its reasoning
where it was. On the shapes where both models actually answer, seven billion
tokens of a wider corpus are worth one part in a thousand, with the sign
against them.

## The registered prediction gets a third answer

Neither branch of the `GAP.md` prediction is satisfied.

`priority_list` is on the binding list and it did move, by 0.495. But its none
rate fell from 0.545 to 0.010 at the same time, so what improved is that the
model now emits an answer on that shape rather than that it now binds roles
correctly. The other two shapes named on that branch did not move: `inverse_chain`
went 0.275 to 0.265 with its none rate staying near 0.48, and `transitive` went
0.270 to 0.215.

The capacity branch did not fire either. `chain_rule` went 0.420 to 0.440
against a 0.250 floor, inside noise and still near chance at two hops.
`exclusion` is 0.000 in both arms.

The prediction was written to distinguish a data fix from a capacity fix. The
answer is that this was neither, and the instrument was not built to see the
third possibility: that the pretrain moves output formatting and nothing else.
That is recorded here rather than folded into either branch.

## What this closes

The undertraining hypothesis was already dead on Stage A, where MMLU read at
chance across six checkpoints at up to 18.64 tokens per parameter. Stage B
closes the remaining objection, which was that Stage A had no fine-tuning while
the model it was compared against had. With fine-tuning held identical, the
better pretrain is worth -0.0009 on the shapes that can be read cleanly.

Nothing here says a larger pretrain cannot help. It says that going from the
corpus-v1-8k pretrain to a 7-billion-token diverse one, at 350M parameters, did
not, and that the gap this program keeps measuring is not a token-count gap.

## Reading the artifacts

In `results/s3/runs/e3-350m/eval/`:

- `mmlu_e3sft_n500.json`, `mmlu_e3sft_n1000.json` and the `e3final` pair are the
  MMLU runs above.
- `score_e3sft-greedy.json` and `score_ref-greedy.json` are the 40 rule shapes;
  the `-t07` pair is the same at temperature 0.7.
- `score_e3sft_heldout.json` and `score_ref_heldout.json` are the 28 held-out
  conditions.
- `hops_e3sft_heldout.json` carries the per-hop breakdown.
- `sft_e3_loss.jsonl` is the Stage B training curve and `loss.jsonl` the Stage A
  pretrain curve.

Every cell carries its own chance floor, hedge rate, forced-choice score and
denominator, which is why the none rate was available to check at all.
