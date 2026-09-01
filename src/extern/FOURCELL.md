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


## Cell 4 rerun, better retrieval, same items

`src/extern/RETRIEVAL.md` has the diagnosis and the sweep. The configuration is
the question with its options as the query, neural search, 20 results, and
passage selection into the same 6,000 characters, against the published cell's
question-only query, 5 results and sequential packing. The control arm below
reads the same freshly fetched pages as the new arm and packs them the
published way, so it separates the packing change from web drift.

| arm | condition | n | floor | accuracy [95% CI] | answer label rate |
| --- | --------- | --- | ----- | ----------------- | ----------------- |
| published cell 4 | question query, 5 results, sequential | 200 | 0.2500 | 0.4500 [0.383, 0.519] | 0.100 |
| control | same new pages, sequential top 5 | 200 | 0.2500 | 0.4450 [0.378, 0.514] | 0.105 |
| new | question and options, 20 results, passages | 200 | 0.2500 | 0.4850 [0.417, 0.554] | 0.210 |

Contamination split, never pooled. The published `answer` cell's 0.7500 was 20
items; two better powered estimates put it near 0.64.

| arm | verbatim | answer | neither |
| --- | -------- | ------ | ------- |
| published | n=12, 0.3333 [0.138, 0.609] | n=20, 0.7500 [0.531, 0.888] | n=168, 0.4226 [0.350, 0.498] |
| control | n=19, 0.4737 [0.273, 0.683] | n=21, 0.6667 [0.454, 0.828] | n=160, 0.4125 [0.339, 0.490] |
| new | n=26, 0.5385 [0.355, 0.712] | n=42, 0.6429 [0.492, 0.770] | n=132, 0.4242 [0.343, 0.510] |

The new arm against the control on the same items: correct where the control is
wrong on 14, wrong where it is right on 6, McNemar exact two sided p = 0.115.
The `neither` cell has now been measured three times under three retrieval
configurations and has not moved off the closed book score of 0.4300 [0.363,
0.499].

Retrieval spend for this rerun and the sweep behind it: 652 live Exa searches
at 20 results each, cached under `results/extern/exa_sweep_cache`, namespaced
by the whole request rather than by the query string.
