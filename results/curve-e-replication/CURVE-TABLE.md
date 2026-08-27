# Scaling curve: eval battery across model sizes

Generated 2026-08-27T22:12:48Z. 150m rows come from results/curve-150m/results150.json, the 350m rows are the killtest seed means from runs/killtest/evals/results.json, the 700m rows are from the block-2 grading in runs/curve/evals-e501/results-e501-700m.json, and the 1300m rows are new: curve-1300m-a (train seed 111) and curve-1300m-c (train seed 211) final checkpoints at step 26700, graded on the block-3 box with the same battery and full sizes. This completes the pre-registered A/C curve at 150m/350m/700m/1300m.

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
| curve-1300m-a | 1300m | A | prose | 0.2800 | 0.3000 | 0.1160 | 0.5000 | true | 0.7161 | docs-in-context | n/a | n/a |
| curve-1300m-c | 1300m | C | episode trace | 0.0000 | 0.0000 | 0.0000 | 0.2213 | false | 0.7269 | interactive | 0.9386 | -0.3039 |

## Regime E at 350m, three seeds

The three regime E seeds are graded in E-REPLICATION.md (seed 501 in runs/curve/evals-e501/E-VERDICT.md); their rows are repeated here for side reading. Regime E is not part of the A/C scaling curve.

| model | params | regime | elicitation | nat contains clean | contradiction | ocr | probes acc | leakage flag | heldout acc | heldout mode | mean rounds | noise slope |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| curve-350me-501 | 350m | E | prose | 0.1680 | 0.1640 | 0.1000 | 0.2828 | false | 0.6746 | docs-in-context | n/a | n/a |
| curve-350me-501 | 350m | E | episode trace | 0.0160 | 0.0160 | 0.0200 | n/a | n/a | 0.8250 | interactive | 0.9235 | -0.2591 |
| curve-350me-502 | 350m | E | prose | 0.1640 | 0.1600 | 0.0520 | 0.2459 | false | 0.6608 | docs-in-context | n/a | n/a |
| curve-350me-502 | 350m | E | episode trace | 0.0040 | 0.0040 | 0.0120 | n/a | n/a | 0.7615 | interactive | 0.8902 | -0.2525 |
| curve-350me-503 | 350m | E | prose | 0.1800 | 0.1760 | 0.0560 | 0.2869 | false | 0.6370 | docs-in-context | n/a | n/a |
| curve-350me-503 | 350m | E | episode trace | 0.0240 | 0.0240 | 0.0160 | n/a | n/a | 0.8332 | interactive | 1.0246 | -0.2867 |
| curve-350me (mean of 3) | 350m | E | prose | 0.1707 | 0.1667 | 0.0693 | 0.2719 | false (0/3) | 0.6575 | docs-in-context | n/a | n/a |
| curve-350me (mean of 3) | 350m | E | episode trace | 0.0147 | 0.0147 | 0.0160 | n/a | n/a | 0.8066 | interactive | 0.9461 | -0.2661 |

## Notes

- Regime A naturalized contains across sizes: 0.1080 at 150m, 0.2053 at 350m (seed mean), 0.2280 at 700m, 0.2800 at 1300m.
- Regime C naturalized contains stays at 0.0000 at 1300m (150m, 350m, and 700m as well); its interactive heldout moves 0.7502 at 150m, 0.6957 at 350m, 0.7442 at 700m, 0.7269 at 1300m.
- Regime A docs-in-context heldout: 0.6634 at 150m, 0.6619 at 350m, 0.6707 at 700m, 0.7161 at 1300m.
- Probes leakage for A: 0.4795 at 150m, 0.4822 at 350m (mean), 0.5123 at 700m, 0.5000 at 1300m, rising through 700m and then flat; C stays near chance, 0.2213 at 1300m, against the 0.3332 threshold.
- Noise slope, regime C: -0.3250 at 150m, -0.2911 at 350m (mean), -0.2697 at 700m, -0.3039 at 1300m.
- Regime E three-seed result: reading gate FAIL on all seeds (prose contains mean 0.1707, ratio 0.831 vs the 0.90 criterion), fact gate PASS on all seeds (probes mean 0.2719 under 0.3332); details in E-REPLICATION.md.

