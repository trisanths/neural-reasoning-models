# The four cell MMLU table

Every cell states its n, its measured chance floor and a Wilson 95 percent interval. Cells 3 and 4 share a scoring method and may be compared directly. Cell 2 is generation scored and its control is row 1b, the same model on the same items with retrieval unavailable.

| cell | model                    | condition             | scoring        | n   | floor  | accuracy [95% CI]     | note            |
| ---- | ------------------------ | --------------------- | -------------- | --- | ------ | --------------------- | --------------- |
| 1    | ours corpus-v1-8k (375M) | closed book           | log likelihood | 200 | 0.2500 | 0.2750 [0.218, 0.341] | -               |
| 3    | LFM2-350M                | closed book           | log likelihood | 200 | 0.2500 | 0.4300 [0.363, 0.499] | published 43.43 |
| 4    | LFM2-350M                | same pages in context | log likelihood | 200 | 0.2500 | 0.4500 [0.383, 0.519] | 179 searches    |

## Contamination split, cell 4, LFM2-350M

Never pooled. A page carrying the answer makes the item a lookup; the row that speaks to reasoning is `neither`.

| retrieved pages contained | n   | floor  | accuracy [95% CI]     |
| ------------------------- | --- | ------ | --------------------- |
| verbatim                  | 12  | 0.2500 | 0.3333 [0.138, 0.609] |
| answer                    | 20  | 0.2500 | 0.7500 [0.531, 0.888] |
| neither                   | 168 | 0.2500 | 0.4226 [0.350, 0.498] |

## Retrieval spend

Live Exa searches: 179. Cache hits: 0. Wall clock across both retrieval cells: 86.6 minutes. A retrieval condition that costs almost nothing is a retrieval condition that did not happen, so cell 2's near zero spend is itself evidence for the policy reading rather than a saving. Every retrieved page is cached on disk under `results/extern/exa_cache`, keyed by query, so the run replays without spending again.

