# Retrieval quality for the MMLU web cell

The published cell 4 put live web pages in front of LFM2-350M and moved MMLU
accuracy from 0.4300 to 0.4500 on 200 items. The contamination split said why
the move was small: on the 20 items whose pages carried the gold answer the
model scored 0.7500, and on the 168 whose pages carried neither the item nor
the answer it scored 0.4226, which is its closed book score. The pages were not
helping because the answer was not in them.

This is the work of raising that hit rate. Diagnosis first, then one lever at a
time, then the same 200 items rescored.

What came out of it:

- The answer present rate in the context the model reads went from 0.120 to
  0.310 under a whole token detector, and the published answer label, which
  excludes contexts carrying the exam question itself, from 0.100 to 0.210.
- Most of that was not a search problem. Of the 176 items whose context missed
  the answer, 48 had it in a page search had already returned and the packer
  threw away. Passage selection at the same 6,000 character budget recovers 22
  of those on the original cached pages, at no spend.
- Overall accuracy went 0.4450 to 0.4850 on identical pages, McNemar exact two
  sided p = 0.115, against 0.4300 closed book.
- The 0.7500 that motivated this work is not what it looked like. Those 20
  items score 0.7000 closed book. Across three retrieval runs, the answer
  bearing cell beats the same items without pages by one item, zero items and
  one item. The gap between the answer cell and the neither cell is item
  selection, not the value of the page.
- The cell that speaks to reasoning has not moved in three configurations:
  0.4226, 0.4125, 0.4242, against 0.4300 closed book.
- The highest raw hit rate in the sweep, Exa's auto search type at 0.400, is
  test set leakage. A third of its contexts contain the MMLU question itself
  and its clean rate is the worst measured.

Everything below carries its n, its measured chance floor where an accuracy is
involved, and a Wilson 95 percent interval. The contamination cells are never
pooled.

## What the answer present rate was measuring

The published label used a raw character substring test: normalise the page
text and the gold option to lowercase alphanumeric words, and ask whether the
gold string appears anywhere in the page. Two sampled items show what that
buys.

`mmlu/formal_logic/48` has gold `~H`, which normalises to the single letter
`h`. Every page containing a standalone `h` counts as carrying the answer.
`mmlu/abstract_algebra/176` has gold `-19`, which normalises to `19` and
matches inside the year 1976. Seven of the 200 items have a gold answer too
short for any character test to separate a statement from a coincidence.

Constraining the same match to whole token boundaries removes those. On the
published configuration it moves the count of items whose context carries the
answer from 27 to 24. A third test, `soft`, asks for every content word of the
gold answer inside one 240 character window, which catches a page that
paraphrases or re-punctuates. All three are computed and written out
everywhere below; none is silently substituted for another.

Hand check, 16 items read in full at seeds 7 and 11 from
`src/extern/retsample.py`. Among the hits, the two false positives above, and
9 of 27 had all three distractors present in the same context as well, which
is a page reciting an option list rather than stating a fact. Among the
misses, 8 of 8 sampled were items whose gold answer no page can state:
professional law fact patterns whose answer is a conclusion about that
scenario, formal logic translations, and arithmetic results. That is not a
detector failure and it is not a retriever failure. It is a ceiling.

## Step 1, where the answer went

Cache only, from `results/extern/exa_cache`, no new searches. Written by
`src/extern/retdiag.py` to `results/extern/retdiag.json`.

The cache holds 200 entries for the 200 items, none missing and none empty,
997 pages in all. The mean page is 39,901 characters and 827 of the 997 pages
are longer than the entire 6,000 character context budget.

Recall over the full text of the cached pages, five results per query, token
detector:

| k | recall@k | 95% CI |
|---|---|---|
| 1 | 0.150 | [0.107, 0.206] |
| 3 | 0.245 | [0.191, 0.309] |
| 5 | 0.270 | [0.213, 0.335] |

The soft detector on the same pages reads 0.195, 0.345, 0.390. k of 10 and 20
cannot be read from this cache, which only ever stored five results per query;
they are measured live in step 2.

What actually reached the model was less than half of that. The packer walked
the ranked pages in order and gave each whatever remained of one character
budget, so a first page longer than 6,000 characters consumed the whole budget
and pages two through five were never seen at all.

| what carried the answer | rate | 95% CI |
|---|---|---|
| some cached page, any rank | 0.270 | [0.213, 0.335] |
| the context the model read | 0.120 | [0.082, 0.172] |

So the four failure modes, assigned in order from the evidence and exclusive,
over all 200 items:

| mode | n | share of the 176 misses |
|---|---|---|
| hit, the context carried the answer | 24 | - |
| search, no returned page had it at any rank | 122 | 69% |
| rank, a page had it but that page never reached the context | 38 | 22% |
| window, the first page had it past the character cut | 10 | 6% |
| detector, the text was there and the strict test missed it | 6 | 3% |

Nearly a third of the misses were already in hand and were thrown away by the
packer. The rest is search, and search is where the ceiling lives:
professional law is 26 items of the 200 and all 26 are search failures, which
is what happens when the gold answer is a conclusion about a fact pattern
invented for the exam.

## Step 2, the levers

Fixed subset of 50 of the 200 items, `random.Random(20260831).sample`, so every
condition is scored on the same items and can be paired. Each condition asks
for 20 results with text and highlights, which lets the same searches answer
the rank cutoff question and the highlights question without a second round of
spend. 50 live searches per condition unless stated.

Metric is the answer present rate in the context the model would read, token
detector, 6,000 characters, passage packing at 20 results. `stem` is the share
whose context contains the exam question itself. `answer` is the published
label: gold present, stem absent. `clean` further requires that not every
distractor is present too.

| condition | hit | 95% CI | stem | answer | clean | recall@1 | recall@20 |
|---|---|---|---|---|---|---|---|
| question, the published query | 0.320 | [0.208, 0.458] | 0.20 | 0.140 | 0.140 | 0.10 | 0.36 |
| question plus options | 0.340 | [0.224, 0.478] | 0.16 | 0.180 | 0.180 | 0.16 | 0.40 |
| keywords of the question | 0.200 | [0.112, 0.330] | 0.08 | 0.140 | 0.140 | 0.10 | 0.26 |
| subject name plus question | 0.300 | [0.191, 0.438] | 0.18 | 0.140 | 0.140 | 0.14 | 0.34 |
| generated query | 0.220 | [0.128, 0.352] | 0.06 | 0.180 | 0.160 | 0.12 | 0.28 |
| question plus options, type auto | 0.400 | [0.276, 0.538] | 0.32 | 0.100 | 0.080 | 0.34 | 0.46 |
| question plus options, type keyword | 0.260 | [0.159, 0.396] | 0.26 | 0.040 | 0.020 | 0.18 | - |
| question plus options, reference domains only | 0.160 | [0.083, 0.285] | 0.04 | 0.140 | 0.100 | 0.08 | 0.26 |
| type auto, exam sites excluded | 0.420 | [0.294, 0.558] | 0.34 | 0.120 | 0.080 | 0.34 | 0.48 |
| type neural, exam sites excluded | 0.320 | [0.208, 0.458] | 0.14 | 0.180 | 0.180 | 0.12 | 0.38 |
| question plus options, plus question, merged | 0.320 | [0.208, 0.458] | 0.20 | 0.140 | 0.140 | 0.16 | 0.40 |
| question plus options, plus generated, merged | 0.320 | [0.208, 0.458] | 0.18 | 0.160 | 0.160 | 0.16 | 0.40 |

Reading that table.

Query formulation moves little. The question with its options is the best of
the five and beats the published question-only query by 3 items to 2 on the
paired count. Keyword extraction is worse than the raw question, which is the
opposite of what a keyword-search intuition predicts, and Exa's own keyword
mode returned a mean of 5.8 results with 3 queries returning nothing at all.

The generated query is the interesting negative. Its queries were written for
each stem in advance, from the stem alone, with the options and the gold
answer withheld, and they are stored at `data/extern/gen_queries.json`. They
read like better search queries than the raw exam sentence and they retrieve
worse pages: recall@20 of 0.28 against 0.40. Rewriting the question drops the
exact phrasing that neural search uses to find the source the question was
written from. Note also what the condition would cost if it were adopted: the
writer was a large model with its own knowledge of the subject, which is the
opposite of the arrangement the project is testing.

The auto search type is the trap. It has the highest raw hit rate in the
table, 0.400, and the worst clean rate, 0.080. Its stem rate is 0.32, meaning
a third of its contexts contain the exam question itself, because auto routes
these queries to something keyword-like that lands on flashcard and quiz
mirrors of MMLU. Excluding 43 known exam-mirror domains does not fix it: stem
stays at 0.34. That configuration is not retrieving facts, it is finding the
test set, and pooling it into an accuracy would have been the most misleading
number available in this work.

Domain targeting to Wikipedia and comparable reference sources is a clear
loss, 0.160 against 0.340. The restriction forces the search into a small
whitelist and the neural ranker returns worse pages within it.

Merging two formulations at two searches per item buys nothing. All three
merges land at 0.320, below the single best query at 0.340, because
round-robining a weaker ranked list into the pool displaces good passages
under a fixed budget.

The rank cutoff, from the 20 result fetches, question plus options, token
detector on full page text: 0.16 at k=1, 0.26 at k=3, 0.34 at k=5, 0.38 at
k=10, 0.40 at k=20. Nearly all of the gain is in by k=10, and k=20 is worth
0.02 over k=10.

### Packing, which is the lever that matters

Same pages, same 6,000 character budget, only the choice of which characters
reach the model. On the 50 item subset with the question plus options query at
20 results:

| packing | answer present |
|---|---|
| sequential, the published packer, 5 results | 0.140 |
| even split across pages | 0.160 |
| Exa highlights | 0.180 |
| passages scored against the question alone | 0.200 |
| passages scored against question and all options | 0.340 |

And on all 200 items with the original cached pages, which isolates packing
from every other change since the pages are identical: sequential 0.120, even
0.145, passages 0.230. That is 22 items recovered at zero additional spend.

One item shows the whole of it. `mmlu/medical_genetics/62` asks what
pseudocholinesterase deficiency causes increased sensitivity to. The first
ranked page is the StatPearls chapter on the condition, and the sequential
packer spends all 6,000 characters on that page's opening: the site name, the
NCBI database picker, the list of every database from Assembly to Taxonomy, the
publisher's address. The passage packer, given the same 20 pages, returns the
GARD entry's summary, which lists "Succinylcholine Sensitivity" among the
condition's other names and then states what it causes. Same search, same
budget, and one of the two contexts contains the answer.

Exa's highlights do fix the truncation problem, and at 12,000 and 18,000
characters they reach 0.28 and 0.30, but at 6,000 they carry less than
passage selection does because three highlights per page of five sentences
each is a thin slice of a 40,000 character page.

Context length is not a lever once passage selection is in place. The
option-aware selector reads 0.340 at 3,000, 6,000, 12,000 and 18,000
characters alike: the windows that carry the answer are already at the top of
its ranking, so a larger budget adds text without adding hits. The
question-only selector does climb with budget, 0.180 to 0.300, which is
another way of seeing that the option terms are what find the relevant window.

That last point deserves stating plainly, because it is the one place where
the metric could flatter itself. The passage selector scores windows against
the question and every option, and the gold answer is one of those options, so
part of the lift is the selector finding text that repeats an option string.
It is symmetric across options and the evidence says it is not merely pulling
in option lists: on the winning configuration the clean rate equals the answer
rate at 0.180, meaning that when the gold answer is present the distractors
usually are not. Whether the selected passage helps the model is a separate
question, and that is what step 3 measures.

## Spend

| round | conditions | searches | results per search |
|---|---|---|---|
| smoke | 1 | 2 | 20 |
| formulation | 4 | 200 | 20 |
| search type, domains, generated | 4 | 200 | 20 |
| exam site exclusion | 2 | 100 | 20 |
| final configuration, 200 items | 1 | 150 | 20 |
| merges, context length, packers | 8 | 0 | from cache |
| step 1 diagnosis | - | 0 | from cache |

652 live searches in total, returning about 12,900 page contents and the same
number of highlight extractions. At $5 per 1,000 searches and $1 per 1,000
page contents that is about $16, and about $29 if highlights bill separately
from text. The step 1 diagnosis and every packing, context length and merge
result cost nothing, because a condition is fetched once and scored offline as
many times as needed.

The sweep cache is at `results/extern/exa_sweep_cache` on the box, 650
entries and 340 MB, gitignored. The two smoke test searches were deleted
before the sweep began, which is why the entry count is 650 and the spend
is 652. It is namespaced by the whole request rather than by the query
string, so a run with different options writes a different key and can never
be served an entry fetched under other options. Every entry records how many
results came back and how many carried text, and an entry whose stored request
does not match the request being made is treated as a miss.

## Step 3, what the hit rate bought

Same 200 MMLU items at seed 1234, same five shot completion prompt with the
reference material in front of it, same log likelihood over the letter
continuations, bos prepended, float32 on cpu, LFM2-350M. The configuration is
the question with its options, neural search, 20 results, passage packing into
6,000 characters.

Both arms below read the same fetched pages. The control arm packs them the
way the published cell did, sequentially from the top 5, so the two arms
differ in exactly one thing: which characters reached the model. The two arms
ran one after the other on two of the four cores, 48 minutes each.

| condition | answer present, token | answer label | stem | mean context |
|---|---|---|---|---|
| published cell 4 | - | 0.100 (20/200) | 0.060 (12/200) | 6,084 |
| control, same pages, sequential top 5 | 0.175 (35/200) | 0.105 (21/200) | 0.095 (19/200) | 6,069 |
| new, passage packing at 20 results | 0.310 (62/200) | 0.210 (42/200) | 0.130 (26/200) | 6,590 |

Accuracy, never pooled across the split. Measured chance floor 0.2500 on every
cell.

| arm | cell | n | accuracy | 95% CI |
|---|---|---|---|---|
| published | all | 200 | 0.4500 | [0.383, 0.519] |
| published | verbatim | 12 | 0.3333 | [0.138, 0.609] |
| published | answer | 20 | 0.7500 | [0.531, 0.888] |
| published | neither | 168 | 0.4226 | [0.350, 0.498] |
| control | all | 200 | 0.4450 | [0.378, 0.514] |
| control | verbatim | 19 | 0.4737 | [0.273, 0.683] |
| control | answer | 21 | 0.6667 | [0.454, 0.828] |
| control | neither | 160 | 0.4125 | [0.339, 0.490] |
| new | all | 200 | 0.4850 | [0.417, 0.554] |
| new | verbatim | 26 | 0.5385 | [0.355, 0.712] |
| new | answer | 42 | 0.6429 | [0.492, 0.770] |
| new | neither | 132 | 0.4242 | [0.343, 0.510] |

Closed book on the same 200 items is 0.4300 [0.363, 0.499]. Under the
published character detector the new arm reads 0.4850 overall, answer 0.6512
on n=43, neither 0.4198 on n=131, so nothing here turns on the detector
change.

Four things to take from that table.

The control arm reproduces the published cell. Pages fetched five hours later
under a different query, packed the same way, give 0.4450 against 0.4500 and
an answer label rate of 0.105 against 0.100. The published number is stable and
the difference in the new arm is not web drift.

The answer cell's 0.7500 does not survive better power. It was 20 items with an
interval from 0.531 to 0.888. Two independent estimates now sit low inside that
interval: 0.6667 on 21 items in the control and 0.6429 on 42 items in the new
arm. A page carrying the answer is worth about 0.64 to this model, not 0.75.

The neither cell did not move. 0.4226 on 168 items in the published run,
0.4125 on 160 in the control, 0.4242 on 132 in the new arm, against 0.4300
closed book. Three retrieval configurations have now put pages in front of this
model that do not state the answer, and all three land on its closed book
score. The pages contribute nothing when the answer is not in them, and that is
now measured on pages a better retriever chose.

The total moved because the mix moved. Doubling the answer bearing share from a
tenth to a fifth, at 0.64 a hit against 0.42 otherwise, is worth about 0.04 in
the overall number, which is what happened: 0.4450 to 0.4850 on the same pages.
Paired item by item, the new arm is correct where the control is wrong on 14
items and wrong where it is right on 6, McNemar exact two sided p = 0.115. A
real effect of that size is not resolvable on 200 items, and reporting 0.4850
against 0.4500 as an improvement without that caveat would be overclaiming.

One check on the packer. The passage selector scores windows against the
question and all four options, so a context could score as answer bearing
merely by reciting the option list. It does not: of the 42 answer label items,
33 have fewer than three distractors present and score 0.6364 [0.466, 0.778],
and the 9 that carry every option score 0.6667 [0.354, 0.879]. The two are the
same within noise, so the option-aware selection is finding text about the
answer rather than text repeating the options.

## The answer present cell was measuring which items are easy

The finding this work started from was that answer bearing pages take the model
to 0.7500 while the rest leave it at its closed book score. That comparison is
between two different sets of items, and an item whose answer is findable on
the web is also an item a model tends to know. Scoring the same items closed
book separates the two, and the closed book run on these 200 items already
exists.

Retrieval against closed book, same items, same cell, paired.

| arm | cell | n | with pages | closed book, same items | closed only | retrieval only | McNemar p |
|---|---|---|---|---|---|---|---|
| published | answer | 20 | 0.7500 | 0.7000 | 0 | 1 | 1.000 |
| published | neither | 168 | 0.4226 | 0.3929 | 8 | 13 | 0.383 |
| published | verbatim | 12 | 0.3333 | 0.5000 | 2 | 0 | 0.500 |
| control | answer | 21 | 0.6667 | 0.6667 | 1 | 1 | 1.000 |
| control | neither | 160 | 0.4125 | 0.4000 | 10 | 12 | 0.832 |
| control | verbatim | 19 | 0.4737 | 0.4211 | 2 | 3 | 1.000 |
| new | answer | 42 | 0.6429 | 0.6190 | 2 | 3 | 1.000 |
| new | neither | 132 | 0.4242 | 0.3788 | 7 | 13 | 0.263 |
| new | verbatim | 26 | 0.5385 | 0.3846 | 0 | 4 | 0.125 |
| new | all | 200 | 0.4850 | 0.4300 | 9 | 20 | 0.061 |
| control | all | 200 | 0.4450 | 0.4300 | 13 | 16 | 0.711 |
| published | all | 200 | 0.4500 | 0.4300 | 10 | 14 | 0.541 |

The 20 items behind the published 0.7500 score 0.7000 closed book. The page
changed one item out of twenty. In the control arm the answer cell is 0.6667
with pages and 0.6667 without, one item each way. In the new arm, with the cell
at n=42, it is 0.6429 with and 0.6190 without, three items gained and two lost.

So the gap between 0.75 and 0.42 across the contamination split was almost
entirely item selection. Questions whose answers sit on a web page are
questions this model already answers at about 0.65, and questions whose answers
do not are questions it answers at about 0.39. Reading the split as "a page
carrying the answer is worth 0.33 accuracy" reads a property of the items as a
property of the retrieval.

That does not make the split useless. It remains the right way to keep a lookup
result from being reported as a reasoning result. But the effect of retrieval
has to be measured within items, against the same items closed book, and that
comparison says the pages are worth little in every cell. The largest paired
effect anywhere in the table is the new arm overall, 20 items gained against 9
lost, p = 0.061, and the cell contributing most of it is `neither`, where by
construction the answer is not on the page.

It also revises what to do next. The brief for this work assumed the model's
ability to read retrieved text was not the bottleneck, on the strength of that
0.7500. The paired numbers say otherwise: even when the answer is in the
context the model reads, accuracy moves by about two points. Raising the answer
present rate further, from 0.21 toward 0.4, would be worth perhaps another two
points of accuracy on this arrangement. The larger question is why a 350M model
scored by log likelihood over four letters, given a 6,000 character reference
block that states the answer, gains so little from it.

## What is left, and what cannot be fixed

Inside the pipeline the remaining loss is small. Recall over the full text of
the fetched pages is 0.370 at 20 results and passage selection delivers 0.310
of it, so 84 percent of what search finds now reaches the model. Outside the
pipeline the loss is structural.

Of the 122 step 1 search failures, 26 are professional law, every professional
law item in the sample. Their gold answers are conclusions about fact patterns
written for the exam and no page on the web states them. Formal logic
translations, arithmetic results and option-phrased ethical conclusions behave
the same way, and 8 of 8 hand read search failures were of that kind. The
answer present rate has a ceiling on MMLU set by the item types, not by the
retriever, and the honest target is the lookup shaped subset rather than the
200.

What to do next, in this order.

Measure retrieval within items from now on. Every accuracy in this report that
compares contamination cells to each other is comparing item sets, and the only
comparison that isolates the pages is the same item with and without them. That
is one extra closed book run per item set, it already exists for these 200, and
it changed the reading of the central finding.

Then find out why the pages are worth so little when they do carry the answer.
Three candidates, all cheap to separate: the reference block sits in front of a
five shot prompt whose shots have no reference blocks, so the format may be
teaching the model to ignore it; the block is a concatenation of 900 character
windows from up to 20 sites, which is not prose; and a 350M model scored by the
log probability of one letter may simply not condition on 1,500 tokens of
preamble. Reordering the block after the shots, packing one coherent page
instead of many windows, and scoring a generated answer instead of a letter are
each a single arm on the existing pages, at no retrieval spend.

Only after that is it worth pushing the hit rate further, and the way to do it
is a reranker over the retrieved windows rather than more searches, since
search now finds more than the packer delivers and both find more than the
model uses.

## Reproducing this

Diagnosis, no network:

    .venv/bin/python -m src.extern.retdiag --out results/extern/retdiag.json
    .venv/bin/python -m src.extern.retsample --mode search --k 8 --seed 11

One sweep condition, 50 live searches:

    .venv/bin/python -m src.extern.retsweep --name f_question_options \
        --formulation question_options --num-results 20 --highlights \
        --budget 60 --subset-n 50

Any condition already fetched, scored again for free, with `--budget 0`.
Comparison table across conditions:

    .venv/bin/python -m src.extern.retcmp --ctx passages@20 \
        --baseline f_question_options

The scored arms, one at a time on two of the four cores:

    bash src/extern/score200.sh

Artifacts, all on the box under `~/decoupled-reasoner`:

| path | what it holds |
|---|---|
| `results/extern/retdiag.json` | step 1, per item page and context flags, failure mode |
| `results/extern/retsweep/*.json` | one file per condition, per item flags and the summary |
| `results/extern/retsweep/final200.json` | recall at k for the chosen configuration on all 200 |
| `results/extern/bench/cell4b_lfm2_mmlu_passages_n200.json` | the new scored arm |
| `results/extern/bench/cell4c_lfm2_mmlu_seq5_n200.json` | the matched packing control |
| `results/extern/retreport.json` | the step 3 cells |
| `results/extern/exa_sweep_cache/` | every fetched search, gitignored, 340 MB |
| `data/extern/gen_queries.json` | the 50 generated queries, written from stems alone |

Code, all under `src/extern/`: `retpack.py` packing and detection,
`retexa.py` the request options, `retquery.py` the formulations,
`retdiag.py` step 1, `retsweep.py` the sweep, `retcmp.py` the comparison,
`retrun.py` the scored arms, `retreport.py` the step 3 tables.
