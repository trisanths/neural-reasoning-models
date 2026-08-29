# E0, the re-keying rescue ladder

Run 2026-08-28 on the g6e dev box. No training.

Checkpoint `s3://decoupled-reasoner-009398924577/runs/final/rlsimple-503-921/final.pt`,
tokenizer_v2, gold minimal pages, retrieval presentation, graded by the rule
`src/rl/env.py` scores with. Every cell is one hundred questions with four
sampled continuations each at temperature 1.0, so four hundred chains stand
behind every number and a 0.000 is worth reading. Driver `src/disc/rekey.py`,
which reads the same `ta6-d{1,2,3,4}-minimal-ret.jsonl` files the depth curve
was measured on and never regenerates a question.

## The answer, first

R1 rescues. The same depth-two questions go from 0.0000 to 0.2050 pass@1 and
from 0.0000 to 0.5600 pass@4 when the environment hands the gold intermediate
back as the key to a fresh sub-question.

| depth two | pass@1 | 95 percent interval | pass@4 |
|---|---|---|---|
| R0, as generated | 0.0000 | 0.0000 to 0.0095 | 0.0000 |
| R1, gold intermediate re-keyed | 0.2050 | 0.1683 to 0.2473 | 0.5600 |

That is 82 correct chains out of 400 against 0 out of 400, on the same
questions, the same pages, the same retriever and the same grader.

Chance floors, which no accuracy here should be read without. Each office's
table maps six keys to six desks, so `alphabet_size` is 6 and a guesser that
commits to one desk per step scores 0.1667 on a step and 0.1667 to the power d
on a chain: 0.0278 at depth two, 0.0046 at depth three, 0.0008 at depth four.
A guesser drawing uniformly from the whole 36-token notation family, which is
the set the answer extractor scans, would score 0.0278 per step instead. The
higher floor is the one used here.

Against that, R1 at depth two is 0.2050 on a chain floor of 0.0278, and its
step rate is 0.4575 on a step floor of 0.1667. R0 at depth two is 0.0000, which
is below its own chance floor, because the policy usually emits no desk name at
all rather than a wrong one.

We are in the first branch. The substrate can execute a lookup keyed by a
value it was handed. It cannot route its own output back in as a key. The
failure is control and presentation, not the representation of the lookup.

## Grader caveat, and the forced-choice regrade

The falsification lane has shown that `hits_target` in `src/rl/env.py` accepts
any prediction containing the gold with six tokens of slack, so a policy that
names two candidates scores correct whichever one is right. On the rule-family
work that inflated one family from 0.009 to 0.985.

Every number in this file is therefore reported twice. The shipped column is
`hits_target`, the rule the environment trains against. The forced-choice
column takes the first universe token the answer names as the answer and
counts naming more than one as wrong. The hedge rate is the fraction of
answers naming more than one desk, which is the quantity that would make the
two columns diverge.

The rescue is not hedging. On a fresh roll-out of every rung at depths one and
two under both graders, the two columns agree to within half a percentage
point everywhere, and the depth-two rescue is identical under both.

| rung, depth two | shipped | forced choice | hedge rate |
|---|---|---|---|
| R0 | 0.0000 | 0.0000 | 0.0025 |
| R1 | 0.2050 | 0.2050 | 0.0050 |
| R1o | 0.1875 | 0.1875 | 0.0050 |
| R1w | 0.0025 | 0.0025 | 0.0000 |
| R2 | 0.2150 | 0.2200 | 0.0025 |
| R2w | 0.0025 | 0.0025 | 0.0000 |
| R3 | 0.0000 | 0.0000 | 0.0000 |

At depth one the largest gap on any rung is 0.005, in both directions: R0 loses
0.0050 and R2w gains 0.0050. The highest hedge rate anywhere in the ladder is
0.0100, on R0 at depth one, where 4 answers in 400 named two desks.

The counts behind that are the reason. Answers name zero or one desk almost
always: R1 at depth two step one splits 200 answers naming one desk, 198
naming none, and 2 naming two. There is no hedging population to inflate.

This task cannot hedge the way `threshold_rule` does. Its answer is a single
desk name emitted at the end of a stretch of word salad, and the question form
admits no if-then phrasing that would name two candidates. The grader's slack
is real and it is worth removing, but on this instrument it moves nothing.

The dual-graded run is an independent roll-out, not a regrade of the stored
chains, so it doubles as a reproducibility check on the ladder. R1 at depth two
came back at 0.2050 both times. R1o's step one came back at 0.3825 both times
against R1w's 0.0050, so the page-position effect reproduces exactly. R2 at
depth two moved from 0.2450 to 0.2150, which is the one cell that shifted by
more than sampling noise would comfortably cover, and it is the rung whose
chains break on the model's own output.

Depths three and four are re-rolling under both graders now.

## The rungs

R0 is depth d exactly as generated.

R1 is the re-keying rescue. After each step the environment takes the gold
intermediate, writes a fresh depth-one question with it, and gives that
sub-question the evidence a depth-one episode gets: the preamble and the one
table its office owns. A depth-d problem becomes d depth-one problems in every
respect, which is the condition `p1^d` is a prediction about.

R1w is R1 with the whole depth-d page set behind every sub-question. Only the
re-keying is oracle supplied, and picking which of the d tables to read stays
with the model. It is not matched to the depth-one anchor, whose page set holds
two pages.

R1o holds R1w's page count fixed and moves the table the step needs to position
one, which tells a page-position effect apart from a page-count effect.

R2 is R1 with the model's own previous answer as the key instead of the gold
one. R2w is its wide-page variant. The token is the last whole-word occurrence
of any token of the episode's universe in the answer text, canonicalised to
lower case; a chain whose answer names no token of the universe breaks there
and scores zero.

R3 is depth d as generated with one sentence appended to the question,
"Name the desk at each office in turn before giving the answer." The
environment does nothing. That is the whole difference from R0: R0 never asks
for the intermediate, R3 asks for it and supplies nothing. R3n appends a
sentence of the same length that asks for nothing, so the cost of appending a
sentence is separable from the cost of the instruction it carries.

Two accuracies are kept apart on every rung and never merged. chain is every
step of the chain right, which is what `p1^d` predicts and the only number
comparable to R0. final is the last answer right, which on R1 and R1w is the
depth-one anchor by construction, because the key for the last step was handed
over.

## The control reproduces

`src/disc/minrepro.py sweep`, the unchanged command that produced the depth
curve, run again before the ladder:

| depth | pass@1 | pass@4 | mean rounds |
|---|---|---|---|
| 1 | 0.5375 | 0.950 | 0.988 |
| 2 | 0.0000 | 0.000 | 0.733 |
| 3 | 0.0000 | 0.000 | 0.560 |
| 4 | 0.0000 | 0.000 | 0.537 |

Every digit matches the record, including the answer-class breakdown and the
falling round count. The harness has not moved.

The ladder driver's own R0 anchor at depth one is 0.4850 rather than 0.5375,
because it batches four hundred rollouts in a different order and therefore
draws different continuations. On the same hundred questions that difference is
194 correct against 215, which is sampling variation. Every prediction below is
stated against both anchors.

## The full ladder

chain pass@1, with its 95 percent Wilson interval, and chain pass@4. Depths are
never pooled and rungs are never pooled.

| rung | d1 | d2 | d3 | d4 |
|---|---|---|---|---|
| R0 | 0.4850 / 0.920 | 0.0000 / 0.000 | 0.0000 / 0.000 | 0.0000 / 0.000 |
| R1 | 0.4850 / 0.910 | 0.2050 / 0.560 | 0.1050 / 0.330 | 0.0475 / 0.180 |
| R1w | 0.4625 / 0.930 | 0.0025 / 0.010 | 0.0000 / 0.000 | 0.0000 / 0.000 |
| R2 | 0.4625 / 0.900 | 0.2450 / 0.670 | 0.1075 / 0.360 | 0.0400 / 0.140 |
| R2w | 0.4700 / 0.920 | 0.0000 / 0.000 | 0.0000 / 0.000 | 0.0000 / 0.000 |
| R3 | 0.0050 / 0.020 | 0.0000 / 0.000 | 0.0000 / 0.000 | 0.0000 / 0.000 |

Intervals on the rescued cells: R1 depth two 0.1683 to 0.2473, depth three
0.0786 to 0.1389, depth four 0.0306 to 0.0730. R2 depth two 0.2054 to 0.2894,
depth three 0.0808 to 0.1417, depth four 0.0248 to 0.0640. Every zero cell has
an upper bound of 0.0095.

## R1 tracks the compounding prediction

| depth | predicted from 0.5375 | predicted from this run's 0.4850 | product of measured step rates | observed |
|---|---|---|---|---|
| 2 | 0.289 | 0.235 | 0.222 | 0.2050 |
| 3 | 0.155 | 0.114 | 0.104 | 0.1050 |
| 4 | 0.083 | 0.055 | 0.049 | 0.0475 |

Against this run's own anchor the prediction is right at depth three and depth
four and about eight percent high at depth two. Against the recorded 0.5375 the
prediction is high at every depth, by the amount the two anchors differ.
Compounding, which was dead as a description of the broken system, is a good
description of the rescued one.

## The step rate does not decay with depth

R1, step accuracy and the accuracy conditional on the retriever having served
the step's own table:

| depth | step 0 | step 1 | step 2 | step 3 |
|---|---|---|---|---|
| accuracy | 0.4850 | 0.4575 | 0.4700 | 0.4650 |
| given the page | 0.907 | 0.915 | 0.895 | 0.886 |

The fourth lookup in a chain is as good as the first. Nothing about being deep
in a chain costs the substrate anything, once the key arrives as a question
token and the page is reachable.

## Where a depth-one answer comes from

Every rung records which page the retriever served. At depth one the answer
decomposes exactly:

  the retriever serves the table on 0.512 of rollouts;
  given the table, the answer is right on 0.946;
  without the table, the answer is right on 0.000, in 195 of 195 rollouts.

So 0.5375 is not a lookup that half works. It is a lookup that works nine times
in ten behind a retriever that finds the page half the time. The model's queries
are word salad, and BM25 over word salad picks the preamble about as often as
it picks the table.

## Why R0 is zero, measured rather than inferred

The page that holds the final answer is the last table. Counting how often the
retriever serves it, over four hundred rollouts:

| depth | served the last table | mean rounds | served the first table | served the preamble |
|---|---|---|---|---|
| 2 | 1 | 0.69 | 115 | 161 |
| 3 | 3 | 0.58 | 89 | 141 |
| 4 | 5 | 0.53 | 68 | 138 |

Once in four hundred at depth two. The claim on record that the second table is
never fetched is now a count rather than an inference.

Two things cause it and they compound. The policy issues fewer queries as the
problem deepens, which is H7. And when it does query, BM25 over its gibberish
hands back the preamble or the first table, because every page shares the
generic vocabulary and the earlier page wins the near-tie.

## R1w, where re-keying alone does not rescue

R1w hands over the gold key and leaves the whole page set in place. Its step
zero is intact and every later step collapses:

| depth | step 0 | step 1 | step 2 | step 3 |
|---|---|---|---|---|
| 2 | 0.4500 | 0.0050 | | |
| 3 | 0.4300 | 0.0050 | 0.0075 | |
| 4 | 0.4425 | 0.0050 | 0.0075 | 0.0175 |

This is not a halting failure. Under R1w the policy retrieves on 0.98 of
rollouts at every step, the depth-one rate, because each sub-question looks like
a depth-one question. It is a retrieval-selection failure: at depth four step 1
the table the question names is served 3 times in 400, and when it is served the
answer is right 2 times out of 3.

R1o settles what about the page set does the damage. It keeps every page R1w
has and moves the table the step needs to position one behind the preamble.
Page count is held fixed and only position moves.

| depth two | step 0 | step 1 | chain pass@1 | chain pass@4 |
|---|---|---|---|---|
| R1w, tables in chain order | 0.4500 | 0.0050 | 0.0025 | 0.010 |
| R1o, the step's table first | 0.4425 | 0.3825 | 0.1875 | 0.590 |
| R1, only the step's table | 0.4850 | 0.4575 | 0.2050 | 0.560 |

Step one goes from 0.0050 to 0.3825 by reordering three pages. The gold page is
served on 0.417 of R1o's step-one rollouts against 0.007 of R1w's, and the
accuracy given the page is 0.916 either way.

So the mechanism is document position. The policy's query carries almost no
information, every page shares the generic vocabulary of the family, the BM25
scores are a near-tie, and the tie goes to the earlier page. `minimal_pages`
emits the tables in chain order, so the table needed at step i always sits
behind the table needed at step 0 and loses. R1's rescue is re-keying plus a
page the retriever can reach, and the second half of that is a two-line change
to page order rather than anything about the model.

## R2, the self-driven chain

R2 splices the model's own answer instead of the gold one. It recovers as much
as R1 does, and slightly more at depth two.

| depth | chain pass@1 | chain pass@4 | chains that broke | keys that drifted off the gold stage |
|---|---|---|---|---|
| 2 | 0.2450 | 0.670 | 0.492 | 0.040 |
| 3 | 0.1075 | 0.360 | 0.710 | 0.062 |
| 4 | 0.0400 | 0.140 | 0.848 | 0.087 |

Half the chains break at depth two and 85 percent by depth four, because the
answer names no token of the universe at all and there is nothing to splice.
The chains that survive are the ones that answered cleanly, and they do better
than average at the next step: R1's step-one rate is 0.4575 unconditionally,
R2's is 0.5344 against the key it was handed. That selection is the whole
reason R2 sits above R1 at depth two, and it is why R2 above R1 is not evidence
that self-driving helps.

The number that matters here is the accuracy against the key the model was
actually handed, which is its own previous output: 0.4625, 0.5344, 0.4423,
0.3542 down the four steps. The substrate executes a lookup on its own output
about as well as on a gold value.

## R3, and why its null carries little

R3 recovers nothing, as predicted. It also destroys the protocol. Mean
retrieval rounds falls from 0.98 to 0.01 at every depth: appending the
instruction stops the policy emitting `<|retrieve|>` at all, and a policy that
never retrieves cannot answer a question whose answer is only on a page.

R3 is therefore not a clean test of asking for the intermediate. It is a
measurement of how narrow the surface form this checkpoint was trained on is.

## Which branch, and what it eliminates

The first branch. The substrate can execute a lookup keyed by a value it was
handed, and cannot route its own output back in as a key. Halting is a control
failure, not a symptom of a representation failure.

The evidence, in order of strength.

R1's step-one lookup is keyed by a value that appears in no question the model
was originally given, and it succeeds at 0.4575, against 0.4850 for a lookup
keyed by a value written in the original question. Conditional on the page
being served the two are 0.915 and 0.907. The same holds at every step to
depth four.

R2's lookups are keyed by the model's own previous output, re-presented by the
environment, and they succeed at 0.5344 and 0.4423 and 0.3542 down the chain.

R0's depth-two chain never completes even once in four hundred, and the reason
is visible: the page carrying the answer is served once.

This kills H2 in its strong form. A computed value serves perfectly well as a
key once it is written into the question. What the substrate cannot do is write
it there itself. H3, no value register at all, is dead: the value survives the
round trip whenever the environment carries it.

H4, error compounding, comes back as a description of the rescued system.
R1 sits within a few percent of the product of its own step rates at depths
three and four.

H7 survives as one of two causes rather than the cause. The falling round count
is real and it is on record again here. It is not sufficient: R1w restores full
retrieval effort at every step and still scores 0.0000, because effort spent on
a retriever that returns the wrong page buys nothing.

The consequence for the slate is that the failure is now split in two and both
halves are addressable without a new representation. One half is the
continuation decision, which is where M2's runtime loop count sits. The other
half is that the query the policy writes carries almost no information, so
selecting among more than two pages fails. That second half is not composition
at all, and it was inside every depth-two number on record.

## Integrity

`audit_episodes` on all four files, and again on the exact question set the
driver rolled out. No violations of any kind: the answer never appears in the
question, is never the starting token, is never an intermediate, the stages are
distinct, and the gold is always the final stage. Maximum symbol frequency
spread across the pages is 1 at depth one and 2 elsewhere.

Leak check on the spliced sub-questions, the way this experiment could have
fooled us. Every sub-question on every rung and depth is tested with a
word-boundary match for the final answer and for its own step answer, including
the R2 sub-questions whose key the model wrote. Zero hits, across every rung
and every depth. No chain was filtered.

Shortcut baselines, chance being 0.1667:

  most frequent token, 0.08 at depths one and two, 0.053 at depth three,
    0.043 at depth four;
  keyword nearest, which finds the best matching page by the training oracle's
    own BM25 and reads the row for the key, 0.000 per chain at every depth
    beyond one; per step it is 0.000 on the narrow page sets of R1 and R2,
    because BM25 given the literal question text picks the preamble;
  answer the depth-one question, 0.000 at every depth beyond one;
  copy the starting token, 0.000 everywhere.

No prompt was dropped for length on any rung.

The R1 chain pairs sample j of step 0 with sample j of step 1, which is
arbitrary because the steps are independent rollouts. It is unbiased for
pass@1. For pass@4 it is a choice, and a different pairing would give a
different pass@4 within sampling error.

The R2 key extraction canonicalises case, so a model that writes Zelfex has its
key spliced as zelfex. That is a small help the environment gives and it is not
separately measured.

## What is not settled

R1 supplies two oracles at once, the key and a page set of two. R1w isolates
the key and shows the key alone does not rescue. Nothing here isolates the page
set from the key, because a depth-d question with only the last table is not a
well posed problem.

Everything here is one checkpoint, one notation family and one surface form, at
temperature 1.0. The greedy predictions on record, 0.71 at depth two and 0.59
at depth three, were never tested and are not tested here.
