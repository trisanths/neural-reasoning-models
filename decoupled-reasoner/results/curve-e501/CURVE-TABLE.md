# Scaling curve: eval battery across model sizes

Generated 2026-08-27T07:21:04Z. 150m rows come from results/curve-150m/results150.json, the 350m rows are the killtest seed means from runs/killtest/evals/results.json, and the 700m rows are new: curve-700m-a (train seed 111) and curve-700m-c (train seed 211) final checkpoints at step 26700, graded on the block-2 box with the same battery and full sizes. The 1300m pair is still training, as are the regime E seeds 502/503; those rows land when their lanes finish.

| model | params | regime | elicitation | nat contains clean | contradiction | ocr | probes acc | leakage flag | heldout acc | heldout mode | mean rounds | noise slope |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| curve-150m-a | 150m | A | prose | 0.1080 | 0.1120 | 0.0440 | 0.4795 | true | 0.6634 | docs-in-context | n/a | n/a |
| curve-150m-b | 150m | B | prose | 0.1040 | 0.1000 | 0.0280 | 0.3033 | false | 0.8574 | docs-in-context | n/a | n/a |
| curve-150m-b | 150m | B | episode trace | 0.0440 | 0.0400 | 0.0360 | n/a | n/a | n/a | n/a | n/a | n/a |
| curve-150m-c | 150m | C | episode trace | 0.0000 | 0.0000 | 0.0000 | 0.2459 | false | 0.7502 | interactive | 0.8747 | -0.3250 |
| killtest-350m-a (mean of 3) | 350m | A | prose | 0.2053 | 0.2027 | 0.0920 | 0.4822 | true (3/3) | 0.6619 | docs-in-context | n/a | n/a |
| killtest-350m-c (mean of 3) | 350m | C | episode trace | 0.0000 | 0.0000 | 0.0013 | 0.2514 | false (0/3) | 0.6957 | interactive | 0.8077 | -0.2911 |
| curve-700m-a | 700m | A | prose | 0.2280 | 0.2280 | 0.1120 | 0.5123 | true | 0.6707 | docs-in-context | n/a | n/a |
| curve-700m-c | 700m | C | episode trace | 0.0000 | 0.0000 | 0.0000 | 0.2500 | false | 0.7442 | interactive | 0.9226 | -0.2697 |

## Regime E at 350m

curve-350me-501 is graded in E-VERDICT.md in this directory; its two rows are repeated here for side reading. Regime E is not part of the A/C scaling curve.

| model | params | regime | elicitation | nat contains clean | contradiction | ocr | probes acc | leakage flag | heldout acc | heldout mode | mean rounds | noise slope |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| curve-350me-501 | 350m | E | prose | 0.1680 | 0.1640 | 0.1000 | 0.2828 | false | 0.6746 | docs-in-context | n/a | n/a |
| curve-350me-501 | 350m | E | episode trace | 0.0160 | 0.0160 | 0.0200 | n/a | n/a | 0.8250 | interactive | 0.9235 | -0.2591 |

## Notes

- Regime A naturalized contains across sizes: 0.1080 at 150m, 0.2053 at 350m (seed mean), 0.2280 at 700m.
- Regime C naturalized contains stays at 0.0000 at 700m (150m and 350m are 0.0000 as well); its interactive heldout moves 0.7502 at 150m, 0.6957 at 350m, 0.7442 at 700m.
- Regime A docs-in-context heldout: 0.6634 at 150m, 0.6619 at 350m, 0.6707 at 700m.
- Probes: 700m A at 0.5123 (flag true), 700m C at 0.2500 (flag false), against the 0.3332 threshold.
- Noise slope, regime C: -0.3250 at 150m, -0.2911 at 350m (mean), -0.2697 at 700m; the slope flattens as size grows while clean accuracy stays near 0.58.
- Probes leakage for A grows with scale: 0.4795 at 150m, 0.4822 at 350m (mean), 0.5123 at 700m.
- curve-700m-a scores its contradiction variant equal to clean (0.2280 both), the same within-noise inversion seen at 150m and in killtest-a-103. Its clean exact match is 0.0040, matching killtest-a-101 and a-102.
- curve-700m-c mean rounds 0.9226 is higher than the 350m killtest mean 0.8077, so more of its interactive answers follow a completed retrieval round.

