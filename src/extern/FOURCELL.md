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
| items that asked, strict                    | 102 | 0        | 0             | 0    | 102     | 1.000     |
| chunks reached the context, strict          | 88  | 0        | 0             | 0    | 88      | 1.000     |
| chunks reached the context, named an option | 88  | 0        | 0             | 0    | 88      | 1.000     |

The first row is the weakest of the four and it is the one to distrust. On the 298 items where the policy never asks, the two arms are the same trajectory: greedy decoding is deterministic and the index is never consulted, and 298 of 298 agree token for token on answer text, generated length and stop reason. Those items cannot disagree, so counting them inflates the denominator without adding information. The informative comparison is the 102 items that asked.

On those there is not one discordant pair either, and on the 88 where a chunk actually entered the trace the reader named an option zero times, with the pages and without them. Retrieval moved nothing, and the split cannot be read as a treatment effect because there is no effect to attribute.

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

When the policy asks, it asks at once: `<|retrieve|>` is the very first token generated on 84 of the 102 items that ask, and the latest it ever arrives is token 19. The behaviour is close to bimodal. Either the first token is a retrieval request, or the model writes about eight tokens of free text and stops. It does not read the question and then decide.

The web arm ends on `<|eot|>` on 380 of 400 items, so nothing here is a truncation artefact: served chunk tokens never count against `max_new_tokens`, and a trajectory that asked for a page still stops on its own after about 54 emitted tokens without opening an answer span. The no-index arm cannot say anything about what happens after a query, because its trajectories end at the guard after about one token; only the web arm reaches that part of the trace.

On 2 items of the 256 token web arm, and 4 across both web arms, the policy wrote `<|retrieve|>` and then `<|result|>` with no query text between them. An empty query is a degenerate query rather than a search that failed, so it is recorded and never sent: the API rejects an empty query string with an HTTP 400, and the original runner had no guard, so it would have ended the run there.

### What this changes in the reading above

`src/extern/fourcell.py` emits, whenever a cell 2 record file is present, a section saying the reader never requests any retrieved text and that the failure is therefore a policy failure rather than a comprehension failure. At 400 items it requests on 0.2550 [0.215, 0.300] of them and gets real pages into its context on 88. The policy fires less often than a reader that always retrieves, and it fires. What does not happen is anything downstream: on those items the reader names no option, with or without pages, and on the items where it does name one it is indistinguishable from guessing. Calling this a policy failure rather than a comprehension failure was resting on a counter that undercounted the policy, and the corrected counter does not support the claim. What the run supports is narrower: this checkpoint cannot produce an MMLU answer, and its retrieval behaviour is not what stands between it and one.

### Retrieval spend, cell 2

Live Exa searches: 73. Cache hits: 255. Queries the 256 token web arm sent: 173, of which 73 live and 98 cache hits. Empty queries never sent, both web arms: 4. API errors: 0. Cache hits that returned no page text: 0. Every served query came back with pages carrying text, the thinnest of them 9,209 characters, so nothing was scored against an empty cache entry. Wall clock 11.5 minutes for all five arms on one L40S.

Record file `results/extern/bench/cell2_ours_mmlu_retrieval_n400.json`, written 2026-09-02 04:19 UTC. Cache audit `src/extern/cache_audit.py`, grader check `src/extern/gradecheck.py`, runner `src/extern/cell2.py`.

## GSM8K with method retrieval

`src/extern/gsm_retrieval.py` set the design and `src/extern/gsm4.py` runs it over both readers. The query is built from the problem's method rather than its wording: numbers and proper names are stripped and what is left is the operation being asked for, which is what a worked example would be indexed under. The gold number cannot appear in that query, so a page it finds was not found by carrying the answer. The raw problem text is kept beside it as the contaminated control, which shows what lookup would buy.

The retrieved material is identical between the two readers by construction: the query comes from the same function over the same item list in the same order, and the page cache is keyed on the query. Each context block is hashed per item and the hashes are compared across the record files below.

GSM8K is generated rather than ranked, so the chance floor is 0.0000 and an unparseable generation is counted apart from a wrong answer. Strict is the number after the `#### ` marker the shots demonstrate; flexible is the last number anywhere, which is lm-eval's flexible-extract. The two prompts are not the same prompt and the rows are never pooled or subtracted: neither format is available to both models.

### The four conditions

| model             | prompt                   | condition              | decode       | n   | floor  | strict [95% CI]       | flexible [95% CI]     | no number at all |
| ----------------- | ------------------------ | ---------------------- | ------------ | --- | ------ | --------------------- | --------------------- | ---------------- |
| ours corpus-v1-8k | native, answer prefilled | closed book            | greedy       | 200 | 0.0000 | 0.0000 [0.000, 0.019] | 0.0150 [0.005, 0.043] | 0.0500           |
| ours corpus-v1-8k | native, answer prefilled | closed book            | T=0.8,p=0.95 | 200 | 0.0000 | 0.0000 [0.000, 0.019] | 0.0150 [0.005, 0.043] | 0.0700           |
| ours corpus-v1-8k | native, answer prefilled | method retrieval       | greedy       | 200 | 0.0000 | 0.0000 [0.000, 0.019] | 0.0300 [0.014, 0.064] | 0.0500           |
| ours corpus-v1-8k | native, answer prefilled | method retrieval       | T=0.8,p=0.95 | 200 | 0.0000 | 0.0000 [0.000, 0.019] | 0.0200 [0.008, 0.050] | 0.0550           |
| ours corpus-v1-8k | native, answer prefilled | problem-text retrieval | greedy       | 200 | 0.0000 | 0.0000 [0.000, 0.019] | 0.0350 [0.017, 0.070] | 0.0550           |
| ours corpus-v1-8k | native, answer prefilled | problem-text retrieval | T=0.8,p=0.95 | 200 | 0.0000 | 0.0000 [0.000, 0.019] | 0.0300 [0.014, 0.064] | 0.0450           |
| LFM2-350M         | 8 shot CoT, bos          | closed book            | greedy       | 200 | 0.0000 | 0.3650 [0.301, 0.434] | 0.3650 [0.301, 0.434] | 0.0000           |
| LFM2-350M         | 8 shot CoT, bos          | closed book            | T=0.8,p=0.95 | 200 | 0.0000 | 0.2900 [0.232, 0.356] | 0.2900 [0.232, 0.356] | 0.0000           |
| LFM2-350M         | 8 shot CoT, bos          | method retrieval       | greedy       | 200 | 0.0000 | 0.3450 [0.283, 0.413] | 0.3450 [0.283, 0.413] | 0.0000           |
| LFM2-350M         | 8 shot CoT, bos          | method retrieval       | T=0.8,p=0.95 | 200 | 0.0000 | 0.3400 [0.278, 0.408] | 0.3400 [0.278, 0.408] | 0.0000           |
| LFM2-350M         | 8 shot CoT, bos          | problem-text retrieval | greedy       | 200 | 0.0000 | 0.3450 [0.283, 0.413] | 0.3450 [0.283, 0.413] | 0.0000           |
| LFM2-350M         | 8 shot CoT, bos          | problem-text retrieval | T=0.8,p=0.95 | 200 | 0.0000 | 0.3400 [0.278, 0.408] | 0.3400 [0.278, 0.408] | 0.0000           |

### Against the published 30.1

LFM2-350M closed book is 0.3650 [0.301, 0.434] strict on 200 items against a published 30.1. The published figure falls just outside the interval, whose lower bound is 0.3014.

This is not the MMLU situation and should not be read as one. There the harness was calibrated against the published number and matched it to within 0.43 once the start token was handled, which is the credential the rest of this work rests on. Here it reads above the published figure by 0.0640. Three differences could carry that and this run does not separate them: the score is over a 200 item sample of the test split rather than all 1,319 items, the eight shots come from the train split under a fixed seed rather than from a published shot list, and a published GSM8K number for a small instruct model is not always the eight shot completion score. What the row supports is a comparison against the retrieval rows beside it, which share every one of those choices. It is not a reproduction claim.

The bos control, the same items and prompt with the start token left off, scores 0.2600 [0.204, 0.325], 0.1050 below the row above. On MMLU that token was worth several points and its absence was what put the first reproduction under the published figure. It moves this number too, in the same direction, and the two intervals overlap. The calibrated convention is to prepend it, which is what lm-eval does for a model that defines one, so the bos row is the one every comparison in this section is made against. A GSM8K number quoted off this harness without it would be the low one.

### What our reader can and cannot do here

Left to run its own loop closed book, this checkpoint emits `<|retrieve|>` as its first token on 200 of 200 GSM8K prompts, and that is the end of the trajectory: on 200 of 200 it generates nothing at all, because with no episode documents there is nothing to serve and the loop stops at the index-is-None guard. A zero read off that arm would be a fact about the harness rather than about the model.

| condition | n   | emitted the retrieve token | produced a number | rounds served | flexible [95% CI]     |
| --------- | --- | -------------------------- | ----------------- | ------------- | --------------------- |
| closed    | 200 | 200/200                    | 0/200             | 0             | 0.0000 [0.000, 0.019] |
| method    | 200 | 138/200                    | 160/200           | 137           | 0.0200 [0.008, 0.050] |
| problem   | 200 | 132/200                    | 168/200           | 129           | 0.0150 [0.005, 0.043] |

Given something to serve, the loop completes. The emission rate falls in the retrieval conditions because the pages sit in the prompt and the trajectory is no longer the same one. In those two conditions the conditions the same pages are handed to the loop as episode documents as well as placed in the context, so a retrieval request is answered out of the retrieved material instead of ending the run, and the reader then writes a number on four items in five. What it does not do is get them right.

With the `<|a|>` answer marker prefilled, so the answer channel is open before decoding starts, it produces a number on 190 of 200 prompts and scores 0.0150 [0.005, 0.043] flexible. It writes a bare number and stops. It emits no chain of reasoning, no `#### ` marker and, on the evidence of the strict column, nothing that resembles the worked format the shots demonstrate.

Shown the same eight shot chain of thought text LFM2 reads, through its own tokenizer and with the answer channel open, it scores 0.0300 [0.014, 0.064] flexible. The format was not what was missing.

So the plain statement is this. Our reader does not solve GSM8K. It parses the problems in the weak sense that it emits a number when a number is asked for, on 190 of 200 items, and closed book that number is right 3 times in 200. Both figures belong in the same sentence, because the score above is over all 200 items and not over the 190 it managed to format; that is what makes it the number the published table can be held next to, and quoting the parse rate as the accuracy would be a different and better sounding claim.

### Contamination split, per condition

Labelled on the pages actually placed in the context: the verbatim problem, its gold answer, or neither. Never pooled. Correct with the answer on the page is a lookup; correct with neither is the reasoning result.

| model             | condition              | pages contained | n   | strict [95% CI]       | flexible [95% CI]     |
| ----------------- | ---------------------- | --------------- | --- | --------------------- | --------------------- |
| ours corpus-v1-8k | method retrieval       | verbatim        | 0   | -                     | -                     |
| ours corpus-v1-8k | method retrieval       | answer          | 59  | 0.0000 [0.000, 0.061] | 0.1017 [0.047, 0.205] |
| ours corpus-v1-8k | method retrieval       | neither         | 141 | 0.0000 [0.000, 0.027] | 0.0000 [0.000, 0.027] |
| ours corpus-v1-8k | problem-text retrieval | verbatim        | 1   | 0.0000 [0.000, 0.793] | 0.0000 [0.000, 0.793] |
| ours corpus-v1-8k | problem-text retrieval | answer          | 60  | 0.0000 [0.000, 0.060] | 0.1167 [0.058, 0.222] |
| ours corpus-v1-8k | problem-text retrieval | neither         | 139 | 0.0000 [0.000, 0.027] | 0.0000 [0.000, 0.027] |
| LFM2-350M         | method retrieval       | verbatim        | 0   | -                     | -                     |
| LFM2-350M         | method retrieval       | answer          | 59  | 0.3898 [0.276, 0.517] | 0.3898 [0.276, 0.517] |
| LFM2-350M         | method retrieval       | neither         | 141 | 0.3262 [0.254, 0.407] | 0.3262 [0.254, 0.407] |
| LFM2-350M         | problem-text retrieval | verbatim        | 1   | 1.0000 [0.207, 1.000] | 1.0000 [0.207, 1.000] |
| LFM2-350M         | problem-text retrieval | answer          | 60  | 0.3667 [0.256, 0.493] | 0.3667 [0.256, 0.493] |
| LFM2-350M         | problem-text retrieval | neither         | 139 | 0.3309 [0.258, 0.413] | 0.3309 [0.258, 0.413] |

### Is the answer label real

The label fires when the gold number appears as a bare token anywhere in 4,000 characters of web text. GSM8K answers are small integers and 4,000 characters of prose contains a lot of small integers, so before the split is read the label is checked against a seeded derangement: each item scored against another item's pages, which destroys any relationship between problem and page and leaves the page lengths and the number distribution alone.

| condition | label    | n   | real pairing [95% CI] | permuted pairing [95% CI] |
| --------- | -------- | --- | --------------------- | ------------------------- |
| method    | verbatim | 200 | 0.0000 [0.000, 0.019] | 0.0000 [0.000, 0.019]     |
| method    | answer   | 200 | 0.2950 [0.236, 0.362] | 0.2650 [0.209, 0.330]     |
| method    | neither  | 200 | 0.7050 [0.638, 0.764] | 0.7350 [0.670, 0.791]     |
| problem   | verbatim | 200 | 0.0050 [0.001, 0.028] | 0.0000 [0.000, 0.019]     |
| problem   | answer   | 200 | 0.3000 [0.241, 0.367] | 0.2800 [0.222, 0.346]     |
| problem   | neither  | 200 | 0.6950 [0.628, 0.755] | 0.7200 [0.654, 0.778]     |

The answer label fires on 59 of 200 real pairings and 53 of 200 deranged ones. Almost all of it is coincidence. The label is close to useless as evidence that a page is about the problem, and a split built on it separates two nearly arbitrary subsets. Reporting the split is still right, because a correct answer sitting beside its own number must never be counted as reasoning, but no weight goes on the difference between its rows.

What survives that is the mechanism, and it is measurable. The number our reader emits, right or wrong, is checked against its own context block and against another item's.

| condition | n with a number | number is in its own block | number is in another item's block | correct | correct with gold in the block |
| --------- | --------------- | -------------------------- | --------------------------------- | ------- | ------------------------------ |
| method    | 190             | 0.8263 [0.766, 0.874]      | 0.7105 [0.642, 0.770]             | 6       | 6                              |
| problem   | 189             | 0.8889 [0.836, 0.926]      | 0.7831 [0.719, 0.836]             | 7       | 7                              |

It reads a number off the page. Every one of the 6 answers it gets right under method retrieval is an item whose block contained the gold number, and it gets none right where the block did not. The excess over the deranged block is small because a block of that size almost always contains some number the model might have written anyway, but the direction is consistent and the correct-answer column is unambiguous. Its score under retrieval is lookup, and the reasoning cell beside it is the one in the table below reading 0.0000.

### The paired control

Each retrieval condition against the same model on the same items closed book, item by item. A contamination split alone compares item sets, not treatments, so the split above cannot separate a page effect from item selection and this table is what decides it.

| model             | condition | n   | with pages | same items closed book | retrieval only | closed only | McNemar p |
| ----------------- | --------- | --- | ---------- | ---------------------- | -------------- | ----------- | --------- |
| ours corpus-v1-8k | method    | 200 | 0.0300     | 0.0150                 | 5              | 2           | 0.453     |
| ours corpus-v1-8k | problem   | 200 | 0.0350     | 0.0150                 | 7              | 3           | 0.344     |
| LFM2-350M         | method    | 200 | 0.3450     | 0.3650                 | 12             | 16          | 0.572     |
| LFM2-350M         | problem   | 200 | 0.3450     | 0.3650                 | 11             | 15          | 0.557     |

Method retrieval does not help LFM2-350M. It is 0.3450 with the pages against 0.3650 on the same items closed book, 12 items gained and 16 lost, McNemar p = 0.572. Retrieving on the raw problem text, the contaminated control, does not help either. Neither does it hurt enough to call a cost. Four thousand characters of web prose in front of an eight shot chain of thought prompt is close to inert for this model on this task.

And the same comparison inside each contamination class, which is where the MMLU lane found that an 0.75 answer-present cell was item selection rather than the pages.

| model             | condition | pages contained | n   | with pages | same items closed book | retrieval only | closed only | McNemar p |
| ----------------- | --------- | --------------- | --- | ---------- | ---------------------- | -------------- | ----------- | --------- |
| ours corpus-v1-8k | method    | answer          | 59  | 0.1017     | 0.0339                 | 5              | 1           | 0.219     |
| ours corpus-v1-8k | method    | neither         | 141 | 0.0000     | 0.0071                 | 0              | 1           | 1.000     |
| ours corpus-v1-8k | problem   | verbatim        | 1   | 0.0000     | 0.0000                 | 0              | 0           | 1.000     |
| ours corpus-v1-8k | problem   | answer          | 60  | 0.1167     | 0.0333                 | 7              | 2           | 0.180     |
| ours corpus-v1-8k | problem   | neither         | 139 | 0.0000     | 0.0072                 | 0              | 1           | 1.000     |
| LFM2-350M         | method    | answer          | 59  | 0.3898     | 0.4068                 | 6              | 7           | 1.000     |
| LFM2-350M         | method    | neither         | 141 | 0.3262     | 0.3475                 | 6              | 9           | 0.607     |
| LFM2-350M         | problem   | verbatim        | 1   | 1.0000     | 1.0000                 | 0              | 0           | 1.000     |
| LFM2-350M         | problem   | answer          | 60  | 0.3667     | 0.4000                 | 4              | 6           | 0.754     |
| LFM2-350M         | problem   | neither         | 139 | 0.3309     | 0.3453                 | 7              | 9           | 0.804     |

The answer-present class repeats what the MMLU lane found. For LFM2 it reads 0.3898 with the pages and 0.4068 on the same items closed book: the class is not a treatment effect, it is a set of items, and the paired column is the only thing that could have shown that. For our reader the same class runs the other way, 0.1017 against 0.0339, and the copy control above says what is happening there. In both cases the split alone would have been read wrongly and in opposite directions.

### Verification and spend

Context blocks matching byte for byte between the two readers: method 200/200, problem 200/200. The two models read the same pages.

Live Exa searches across the GSM8K runs: 340, all of them in the fetch stage of the first run; every later run read them back. Cache hits: 1060. Wall clock 99.6 minutes on one L40S.

Cost, priced at 0.005 dollars for a neural search and 0.001 dollars per page of text, which is what Exa lists:

| job             | live searches | results per search | estimated cost |
| --------------- | ------------- | ------------------ | -------------- |
| cell 2 at n=400 | 73            | 5                  | $0.73          |
| GSM8K at n=200  | 340           | 4                  | $3.06          |
| total this pass | 413           | -                  | $3.79          |

That pricing reproduces the project's own experience on the earlier sweep: 652 searches at 20 results each comes to $16.30 under it, against the $16 to $29 that sweep was reckoned to have cost. This pass costs about 4.3 times less than that sweep, because it asks for four or five results rather than twenty and because most of what it needed was already on disk.

- `results/extern/bench/gsm4_lfm2_350m_bos_n200.json`, written 2026-09-02 05:55 UTC
- `results/extern/bench/gsm4_lfm2_350m_nobos_n200.json`, written 2026-09-02 06:08 UTC
- `results/extern/bench/gsm4_ours_native_a_n200.json`, written 2026-09-02 06:09 UTC
- `results/extern/bench/gsm4_ours_native_n200.json`, written 2026-09-02 06:13 UTC
- `results/extern/bench/gsm4_ours_shots_a_n200.json`, written 2026-09-02 06:14 UTC
- `results/extern/bench/gsm4_controls.json`, written 2026-09-02 06:17 UTC
