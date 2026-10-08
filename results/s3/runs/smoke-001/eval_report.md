# Eval report

Checkpoint: /home/ec2-user/runs/smoke-001/latest.pt (step 2000)
Held out seed: 999, episodes: 40, questions: 191

## Held out worlds

Accuracy 0.3037 against a chance rate of 0.3128.

| domain | n | accuracy |
|---|---|---|
| corporate | 58 | 0.3103 |
| kinship_temporal | 45 | 0.3333 |
| logistics | 40 | 0.3250 |
| regulatory | 48 | 0.2500 |

| question type | n | accuracy |
|---|---|---|
| lookup | 115 | 0.3565 |
| multi_hop | 46 | 0.1304 |
| yes_no | 30 | 0.3667 |

## Knowledge probes

Accuracy 0.1750 on 40 probes, chance 0.25, leakage threshold 0.4554.

Leakage flag: clear, the score is consistent with chance.
