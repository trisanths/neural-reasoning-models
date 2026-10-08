# Kill-test verdict

Generated 2026-08-26T02:34:45Z from 250 naturalized items and 3 A seeds, 3 C seeds.

## Gate metric: naturalized reading, contains-answer, clean variant

Regime A per seed: 101: 0.2280, 102: 0.1960, 103: 0.1920
Regime A mean 0.2053, std 0.0197.

Regime C per seed: 201: 0.0000, 202: 0.0000, 203: 0.0000
Regime C mean 0.0000, std 0.0000.

C to A ratio of means: 0.0000.
Bootstrap 95 percent interval over items and seeds: [0.0000, 0.0000] (10000 replicates, 0 dropped for a zero regime A mean).

For reference, exact match on the same variant: A mean 0.0027, C mean 0.0000, ratio 0.0000.

## Pre-registered rule (SPEC.md section 7)

Compare regime C against regime A at the 350M class on the naturalized reading suite. If C reaches at least 90 percent of A's score, the strict form survives and Phase 2 tests it. Between 60 and 90 percent, the strict form is weakened: Phase 2 uses a frequency-ordered resident knowledge diet plus teacher distillation. Below 60 percent, the strict form is dead; Phase 2 tests only the weakened form and the writeup says so plainly.

## Outcome

The ratio 0.0000 is below 0.6. The strict form is dead; Phase 2 tests only the weakened form.

## Knowledge probe leakage flags

The leakage rule applies to regime C only; regime A trained on real text and is expected to score above chance.
Clear on every regime C checkpoint; their probe scores are consistent with chance.

## Retrieval loop usage on held-out worlds

Mean served rounds per question in the interactive loop: killtest-c-201: 0.89, killtest-c-202: 0.77, killtest-c-203: 0.76. Values near zero mean the model answered mostly without retrieving, so heldout and noise numbers reflect closed-book behavior.

## Provenance

- killtest-a-101: step 26700, /home/ec2-user/runs/killtest-a-101/ckpt-0026700.pt
- killtest-a-102: step 26700, /home/ec2-user/runs/killtest-a-102/ckpt-0026700.pt
- killtest-a-103: step 26700, /home/ec2-user/runs/killtest-a-103/ckpt-0026700.pt
- killtest-c-201: step 26700, /home/ec2-user/runs/killtest-c-201/ckpt-0026700.pt
- killtest-c-202: step 26700, /home/ec2-user/runs/killtest-c-202/ckpt-0026700.pt
- killtest-c-203: step 26700, /home/ec2-user/runs/killtest-c-203/ckpt-0026700.pt
