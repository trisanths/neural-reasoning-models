# Kill-test verdict

Generated 2026-08-28T02:13:28Z from 250 naturalized items and 6 A seeds, 6 C seeds.

## Gate metric: naturalized reading, contains-answer, clean variant

Regime A per seed: 111: 0.2800, 502: 0.1640, 503: 0.1800, 601: 0.1640, 602: 0.1120, 603: 0.1800
Regime A mean 0.1800, std 0.0550.

Regime C per seed: 211: 0.0000, 502: 0.0040, 503: 0.0240, 601: 0.0080, 602: 0.0280, 603: 0.0280
Regime C mean 0.0153, std 0.0128.

C to A ratio of means: 0.0852.
Bootstrap 95 percent interval over items and seeds: [0.0204, 0.1843] (10000 replicates, 0 dropped for a zero regime A mean).

For reference, exact match on the same variant: A mean 0.0040, C mean 0.0140, ratio 3.5000.

## Pre-registered rule (SPEC.md section 7)

Compare regime C against regime A at the 350M class on the naturalized reading suite. If C reaches at least 90 percent of A's score, the strict form survives and Phase 2 tests it. Between 60 and 90 percent, the strict form is weakened: Phase 2 uses a frequency-ordered resident knowledge diet plus teacher distillation. Below 60 percent, the strict form is dead; Phase 2 tests only the weakened form and the writeup says so plainly.

## Outcome

The ratio 0.0852 is below 0.6. The strict form is dead; Phase 2 tests only the weakened form.

## Knowledge probe leakage flags

The leakage rule applies to regime C only; regime A trained on real text and is expected to score above chance.
Clear on every regime C checkpoint; their probe scores are consistent with chance.

## Retrieval loop usage on held-out worlds

Mean served rounds per question in the interactive loop: killtest-c-211: 0.94, killtest-c-502: 0.89, killtest-c-503: 1.02, killtest-c-601: 0.80, killtest-c-602: 0.82, killtest-c-603: 1.09. Values near zero mean the model answered mostly without retrieving, so heldout and noise numbers reflect closed-book behavior.

## Provenance

- killtest-a-111: step 26700, /home/ec2-user/eval-e2/ckpts/killtest-a-111/ckpt-0026700.pt
- killtest-a-502: step 26700, /home/ec2-user/eval-e2/ckpts/killtest-a-502/ckpt-0026700.pt
- killtest-a-503: step 26700, /home/ec2-user/eval-e2/ckpts/killtest-a-503/ckpt-0026700.pt
- killtest-a-601: step 26700, /home/ec2-user/eval-e2/ckpts/killtest-a-601/ckpt-0026700.pt
- killtest-a-602: step 26700, /home/ec2-user/eval-e2/ckpts/killtest-a-602/ckpt-0026700.pt
- killtest-a-603: step 26700, /home/ec2-user/eval-e2/ckpts/killtest-a-603/ckpt-0026700.pt
- killtest-c-211: step 26700, /home/ec2-user/eval-e2/ckpts/killtest-c-211/ckpt-0026700.pt
- killtest-c-502: step 26700, /home/ec2-user/eval-e2/ckpts/killtest-c-502/ckpt-0026700.pt
- killtest-c-503: step 26700, /home/ec2-user/eval-e2/ckpts/killtest-c-503/ckpt-0026700.pt
- killtest-c-601: step 26700, /home/ec2-user/eval-e2/ckpts/killtest-c-601/ckpt-0026700.pt
- killtest-c-602: step 26700, /home/ec2-user/eval-e2/ckpts/killtest-c-602/ckpt-0026700.pt
- killtest-c-603: step 26700, /home/ec2-user/eval-e2/ckpts/killtest-c-603/ckpt-0026700.pt
