# The four cell MMLU table

Every cell states its n, its measured chance floor and a Wilson 95 percent interval. Cells 3 and 4 share a scoring method and may be compared directly. Cell 2 is generation scored and its control is row 1b, the same model on the same items with retrieval unavailable.

| cell | model                    | condition   | scoring        | n   | floor  | accuracy [95% CI]     | note            |
| ---- | ------------------------ | ----------- | -------------- | --- | ------ | --------------------- | --------------- |
| 1    | ours corpus-v1-8k (375M) | closed book | log likelihood | 200 | 0.2500 | 0.2750 [0.218, 0.341] | -               |
| 3    | LFM2-350M                | closed book | log likelihood | 200 | 0.2500 | 0.4300 [0.363, 0.499] | published 43.43 |

