| item set | decoding | n | mean retrieval rounds | stopped at `<|eot|>` | hit the token cap | answer boundary |
|---|---|---|---|---|---|---|
| the twelve shape set | greedy | 3000 | 0.548 | 2871 | 102 | 27 |
| the twelve shape set | sampled, t=0.7 top k 50 | 1200 | 0.512 | 1160 | 9 | 31 |
| the wh corner | greedy | 900 | 1.000 | 829 | 51 | 20 |
| the wh corner | sampled, t=0.7 top k 50 | 300 | 0.970 | 271 | 0 | 29 |
| the transposed grids | greedy | 1500 | 0.537 | 1400 | 100 | 0 |
| the transposed grids | sampled, t=0.7 top k 50 | 500 | 0.554 | 490 | 8 | 2 |
| the depth ladder | greedy | 560 | 0.332 | 557 | 0 | 3 |
