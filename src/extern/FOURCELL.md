# The four cell MMLU table

Every cell states its n, its measured chance floor and a Wilson 95 percent interval. Cells 3 and 4 share a scoring method and may be compared directly. Cell 2 is generation scored and its control is row 1b, the same model on the same items with retrieval unavailable.

| cell | model                    | condition             | scoring        | n   | floor  | accuracy [95% CI]     | note            |
| ---- | ------------------------ | --------------------- | -------------- | --- | ------ | --------------------- | --------------- |
| 1    | ours corpus-v1-8k (375M) | closed book           | log likelihood | 200 | 0.2500 | 0.2750 [0.218, 0.341] | -               |
| 1b   | ours corpus-v1-8k (375M) | closed book (control) | generation     | 400 | 0.2500 | 0.0100 [0.004, 0.025] | -               |
| 2    | ours corpus-v1-8k (375M) | live web retrieval    | generation     | 400 | 0.2500 | 0.0100 [0.004, 0.025] | 73 searches     |
| 3    | LFM2-350M                | closed book           | log likelihood | 200 | 0.2500 | 0.4300 [0.363, 0.499] | published 43.43 |
| 4    | LFM2-350M                | same pages in context | log likelihood | 200 | 0.2500 | 0.4500 [0.383, 0.519] | 179 searches    |

## Contamination split, cell 2, ours

Never pooled. A page carrying the answer makes the item a lookup; the row that speaks to reasoning is `neither`. The rows cover only the items that actually received served text; an item served nothing has no pages to be contaminated by and folding those in would inflate `neither` with items retrieval never touched.

| retrieved pages contained | n  | floor  | accuracy [95% CI]     |
| ------------------------- | -- | ------ | --------------------- |
| verbatim                  | 2  | 0.2500 | 0.0000 [0.000, 0.658] |
| answer                    | 4  | 0.2500 | 0.0000 [0.000, 0.490] |
| neither                   | 82 | 0.2500 | 0.0000 [0.000, 0.045] |

## Contamination split, cell 4, LFM2-350M

Never pooled. A page carrying the answer makes the item a lookup; the row that speaks to reasoning is `neither`.

| retrieved pages contained | n   | floor  | accuracy [95% CI]     |
| ------------------------- | --- | ------ | --------------------- |
| verbatim                  | 12  | 0.2500 | 0.3333 [0.138, 0.609] |
| answer                    | 20  | 0.2500 | 0.7500 [0.531, 0.888] |
| neither                   | 168 | 0.2500 | 0.4226 [0.350, 0.498] |

## Cell 2, the stages behind one flat accuracy

The reader emitted `<|retrieve|>` on **102 of 400** passes, a rate of 0.2550 with a 95 percent interval of [0.215, 0.300]. That is the headline number and the accuracy is its shadow. The counter is the emission itself and is the same event with a serving surface attached and without one; an earlier counter inferred it from the stop reason and read low in the web pass. The section further down reconciles the two figures that produced.

Four stages sit behind one flat accuracy and only the last is about comprehension.

| stage                      | web pass | no-index control |
| -------------------------- | -------- | ---------------- |
| emitted the retrieve token | 0.2550   | 0.2550           |
| query returned a chunk     | 0.2200   | -                |
| chunk entered the trace    | 0.2200   | -                |
| mean rounds served         | 0.43     | -                |
| mean served characters     | 878.4    | -                |
| named no option at all     | 0.9550   | 0.9550           |

A policy failure and a comprehension failure imply different fixes, and this table no longer picks one. The reader does ask, on one pass in four, and chunks do reach its trace. What does not follow is an answer: it names no option on the items where pages arrived, with them or without them. The paired control in the cell 2 section below is what settles that, not this split.

## Retrieval spend

Cell 2: 73 live Exa searches and 255 cache hits. Cell 4: 179 live searches. Wall clock across both retrieval cells: 98.1 minutes. Every retrieved page is cached on disk under `results/extern/exa_cache`, keyed by query, so a rerun replays without spending again, and every cache entry is checked for non-empty page text by `src/extern/cache_audit.py` before anything is scored against it.


<!-- appended sections follow; fourcell.py preserves everything below -->

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

### The answer cell against the same items closed book

The split compares item sets, not treatments. An item whose answer is findable
on the web is also an item this model tends to know, and the closed book run on
these 200 items settles which effect the split was showing.

| arm | cell | n | with pages | closed book, same items | closed only | retrieval only | McNemar p |
| --- | ---- | --- | --- | --- | --- | --- | --- |
| published | answer | 20 | 0.7500 | 0.7000 | 0 | 1 | 1.000 |
| control | answer | 21 | 0.6667 | 0.6667 | 1 | 1 | 1.000 |
| new | answer | 42 | 0.6429 | 0.6190 | 2 | 3 | 1.000 |
| new | all | 200 | 0.4850 | 0.4300 | 9 | 20 | 0.061 |

The 20 items behind the published 0.7500 score 0.7000 without any pages at all.
The distance between the answer cell and the neither cell is which items land
in each, not what the page did. The split still has to be kept, because it
keeps a lookup result from being reported as a reasoning result, but the effect
of retrieval has to be read from the paired columns.

## Cell 2 at n=400: the reader driving its own retrieval loop

The pass behind the published cell 2 was killed at 10 items and its finding was read off 20 passes. This run is 400 items, seed 1234, drawn by the same seeded shuffle the rest of the table uses, on the GPU rather than the CPU that made the first attempt too slow to finish. The prompt is built by `src/rl/env.py:build_prompt` with the world header, `<|world|> domain: corporate <|q|> ...`, and the builder asserts the header into the token stream: without it this checkpoint issues no retrieval rounds and runs to the token cap. `max_new_tokens` is 256.

### How often the policy asks

`emitted <|retrieve|>` counts the token the policy wrote. It is the same event in every arm and does not depend on whether a query finished or a page came back.

| arm                                        | emitted / n | rate [95% CI]         |
| ------------------------------------------ | ----------- | --------------------- |
| web index, greedy, 256 tokens              | 102/400     | 0.2550 [0.215, 0.300] |
| no index, greedy, 256 tokens               | 102/400     | 0.2550 [0.215, 0.300] |
| no index, sampled T=1.0, 256 tokens        | 104/400     | 0.2600 [0.219, 0.305] |
| no index, sampled T=0.8 p=0.95, 256 tokens | 98/400      | 0.2450 [0.205, 0.289] |
| web index, greedy, 64 tokens               | 102/400     | 0.2550 [0.215, 0.300] |

The rate is 0.2550 and it does not move: the web arm and the no-index arm agree item by item on 400 of 400, because greedy decoding is deterministic and nothing before the first `<|retrieve|>` depends on whether a serving surface is attached. Sampling at T=1.0 and at T=0.8 puts it in the same place, so this is not a greedy artefact. One item in four is not a policy that never asks.

### Reconciling 0.05 against 0.255

The two figures are both from this harness and they disagree because they are not the same measurement.

`src/extern/retrieval_ours.py` scored the event as `n_rounds > 0 or stop_reason == "max_rounds"`, and those conditions mean different things depending on whether an index is attached. With no index, `<|retrieve|>` hits the index-is-None guard in `src/evals/interactive.py` and ends the trajectory before a query token is written, so `stop_reason` is `max_rounds` and every emission is counted. With a web index the loop keeps decoding to collect the query text, and if the new-token budget runs out mid query it breaks with `stop_reason` still `max_new_tokens` and no round recorded, so that emission is counted as zero. The same policy therefore reads lower in the web pass than in the no-index pass.

| arm                                        | n   | emitted the retrieve token | legacy issued_query | query served a chunk |
| ------------------------------------------ | --- | -------------------------- | ------------------- | -------------------- |
| web index, greedy, 256 tokens              | 400 | 0.2550                     | 0.2250              | 0.2200               |
| no index, greedy, 256 tokens               | 400 | 0.2550                     | 0.2550              | 0.0000               |
| no index, sampled T=1.0, 256 tokens        | 400 | 0.2600                     | 0.2600              | 0.0000               |
| no index, sampled T=0.8 p=0.95, 256 tokens | 400 | 0.2450                     | 0.2450              | 0.0000               |
| web index, greedy, 64 tokens               | 400 | 0.2550                     | 0.2125              | 0.2075               |

That accounts for part of the gap and not for most of it. The legacy counter loses 0.0300 at a 256 token budget and 0.0425 at the 64 token budget that truncated the original trajectory. It does not reach 0.05.

`src/extern/bench.py:load_mmlu` shuffles the test split under the seed and truncates, so the first 200 items of this draw are the 200 items the closed-book lane scored. On that subset, decoded the same way, the emission rate is 0.2550 [0.200, 0.320]. The 0.255 reproduces exactly.

The other side does not. The record file for the killed run is gone and the only surviving evidence is one line of `logs/extern/cell2.log`, `10/100 1517s eta 13653s live=1 cached=1`. On the same first 10 items this run sends 2 queries and serves 2, which matches that line exactly: one live call and one cache hit. The legacy counter on those 10 items is 2/10, and pooled across both passes the way a 20 pass figure implies it is 5/20. No counter over those items gives 0.05. One over twenty does, and one is the live search count on that log line. The 0.05 is a spend number read as a policy number, and cache hits are invisible to it by construction.

So the 0.255 side is right about the policy. The 0.05 was never a rate at which the model asked for anything.

### Accuracy, and why the floor is out of reach

Generation scored: forced choice over the option strings with a bare letter honoured. A model that names no option scores zero, so the 0.25 floor is attainable only by a policy that picks, and this one mostly does not. These rows are not comparable to the log likelihood cells above and are never subtracted from them.

| arm                                        | n   | floor  | strict [95% CI]       | named an option | accuracy given it named one [95% CI] |
| ------------------------------------------ | --- | ------ | --------------------- | --------------- | ------------------------------------ |
| web index, greedy, 256 tokens              | 400 | 0.2500 | 0.0100 [0.004, 0.025] | 18/400          | 0.2222 [0.090, 0.452]                |
| no index, greedy, 256 tokens               | 400 | 0.2500 | 0.0100 [0.004, 0.025] | 18/400          | 0.2222 [0.090, 0.452]                |
| no index, sampled T=1.0, 256 tokens        | 400 | 0.2500 | 0.0050 [0.001, 0.018] | 11/400          | 0.1818 [0.051, 0.477]                |
| no index, sampled T=0.8 p=0.95, 256 tokens | 400 | 0.2500 | 0.0100 [0.004, 0.025] | 20/400          | 0.2000 [0.081, 0.416]                |
| web index, greedy, 64 tokens               | 400 | 0.2500 | 0.0100 [0.004, 0.025] | 18/400          | 0.2222 [0.090, 0.452]                |

The decomposition is the result. The reader names an option on 18 of 400 items, and on those it is at chance: 0.2222 [0.090, 0.452] against a 0.2500 floor. The flat 0.0100 is a formatting failure stacked on top of a chance level reader, and the two have to be reported apart.

The grader was exercised before the number was believed, because 0.0100 against a 0.2500 floor is the shape a broken grader makes. Handed a bare gold letter it scores 1.0000 on all 400 items, a gold letter with a period 1.0000, the gold option text 0.9775, a sentence naming the gold text 1.0000, a wrong letter 0.0000, and empty or nonsense output `named_none` 1.0000. `src/extern/gradecheck.py` reruns it.

### The paired control

Every retrieval condition is compared against the same model on the same items with retrieval unavailable, item by item.

| comparison                                  | n   | web only | no index only | both | neither | McNemar p |
| ------------------------------------------- | --- | -------- | ------------- | ---- | ------- | --------- |
| all items, strict                           | 400 | 0        | 0             | 4    | 396     | 1.000     |
| chunks reached the context, strict          | 88  | 0        | 0             | 0    | 88      | 1.000     |
| chunks reached the context, named an option | 88  | 0        | 0             | 0    | 88      | 1.000     |

There is not one discordant pair anywhere in the table. On the 88 items where a chunk actually entered the trace the reader named an option zero times, with the pages and without them. Retrieval moved nothing, and the split cannot be read as a treatment effect because there is no effect to attribute.

### Contamination split, on the items where pages arrived

Labelled on the chunks actually served. The split is reported over the 88 items that received text, not over all 400: an item that was served nothing has no pages to be contaminated by, and folding those into `neither` would inflate that row with items retrieval never touched.

| served chunks contained | n   | floor  | accuracy [95% CI]     | named an option |
| ----------------------- | --- | ------ | --------------------- | --------------- |
| verbatim                | 2   | 0.2500 | 0.0000 [0.000, 0.658] | 0               |
| answer                  | 4   | 0.2500 | 0.0000 [0.000, 0.490] | 0               |
| neither                 | 82  | 0.2500 | 0.0000 [0.000, 0.045] | 0               |
| nothing served          | 312 | 0.2500 | 0.0128 [0.005, 0.032] | 18              |

Every item this cell scores correctly is an item where retrieval served nothing at all.

### Where the trajectories end

| arm                                        | n   | eot | answer_boundary | max_rounds | max_new_tokens | mean tokens generated when it asked |
| ------------------------------------------ | --- | --- | --------------- | ---------- | -------------- | ----------------------------------- |
| web index, greedy, 256 tokens              | 400 | 380 | 3               | 5          | 12             | 54.4                                |
| no index, greedy, 256 tokens               | 400 | 291 | 2               | 102        | 5              | 1.1                                 |
| no index, sampled T=1.0, 256 tokens        | 400 | 291 | 5               | 104        | 0              | 1.3                                 |
| no index, sampled T=0.8 p=0.95, 256 tokens | 400 | 300 | 2               | 98         | 0              | 1.4                                 |
| web index, greedy, 64 tokens               | 400 | 366 | 2               | 4          | 28             | 36.5                                |

The web arm ends on `<|eot|>` on 380 of 400 items, so nothing here is a truncation artefact: served chunk tokens never count against `max_new_tokens`, and a trajectory that asked for a page still stops on its own after about 54 emitted tokens without opening an answer span. The no-index arm cannot say anything about what happens after a query, because its trajectories end at the guard after about one token; only the web arm reaches that part of the trace.

On 2 items of the 256 token web arm, and 4 across both web arms, the policy wrote `<|retrieve|>` and then `<|result|>` with no query text between them. An empty query is a degenerate query rather than a search that failed, so it is recorded and never sent: the API rejects an empty query string with an HTTP 400, and the original runner had no guard, so it would have ended the run there.

### What this changes in the reading above

The published cell 2 text says the reader never requests any retrieved text. At 400 items it requests on 0.2550 [0.215, 0.300] of them and gets real pages into its context on 88. The policy fires less often than a reader that always retrieves, and it fires. What does not happen is anything downstream: on those items the reader names no option, with or without pages, and on the items where it does name one it is indistinguishable from guessing. Calling this a policy failure rather than a comprehension failure was resting on a counter that undercounted the policy, and the corrected counter does not support the claim. What the run supports is narrower: this checkpoint cannot produce an MMLU answer, and its retrieval behaviour is not what stands between it and one.

### Retrieval spend, cell 2

Live Exa searches: 73. Cache hits: 255. Queries the 256 token web arm sent: 173, of which 73 live and 98 cache hits. Empty queries never sent, both web arms: 4. API errors: 0. Cache hits that returned no page text: 0. Every served query came back with pages carrying text, the thinnest of them 9,209 characters, so nothing was scored against an empty cache entry. Wall clock 11.5 minutes for all five arms on one L40S.

Record file `results/extern/bench/cell2_ours_mmlu_retrieval_n400.json`, written 2026-09-02 04:19 UTC. Cache audit `src/extern/cache_audit.py`, grader check `src/extern/gradecheck.py`, runner `src/extern/cell2.py`.

