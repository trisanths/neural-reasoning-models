# H8, the answer-source split, measured

The generator in `src/mathgen/` labels every exercise `stated_in_a_chapter` when
the textbook prints its answer somewhere and `derived_by_computation` when it
does not. H8 in `PREREGISTERED.md` predicts the first family lands near 0.514
and the second near 0.000, and forbids any figure pooled across the label.

This file records one evaluation of one checkpoint. The checkpoint is
`~/mgeval-ckpt/final.pt`, the RL policy the falsification lane used, byte
identical to `~/falsify/final.pt` on the dev box. The tokenizer is
`~/data/tokenizer_v2.json`. Every number comes from a per-rollout jsonl that is
kept, and every path is named beside the number it produced.

Two facts from the falsification lanes bound how any of this may be read. The
environment grader in `src/rl/env.py` accepts a prediction that CONTAINS the
gold string within six tokens of slack, and one rule family reached 0.985 under
it by naming both candidates. And the checkpoint's apparent rule-reading is
sentence-frame matching: an idiom sharing no content word with the trained one
scored 0.840 while one keeping every content word and changing only the frame
scored 0.030. So a low mathgen score has two possible causes that have nothing
to do with answer source, and the gate below is what separates them.

## The gate

Before any mathgen number, the same harness scored the two `src/skillacq/`
families whose values are on record: `substitution_rule` 0.969 greedy and
0.828 at temperature one, `threshold_rule` 1.000 greedy and 0.922. The same
code path loads the model, runs the retrieval environment, grades and
aggregates; only the episodes file changes.

Both budgets were run, because the mathgen pages need a wider rollout window
than a skillacq page and a budget change must not be mistaken for a capability
change. Narrow is `configs/mg3-gate.yaml` (max_len 640, 96 new tokens), the
budget the recorded controls were measured under. Wide is
`configs/mg3-gate-wide.yaml` (max_len 2048, 192 new tokens), the mathgen budget.

Greedy is one rollout per question. `t1` is temperature 1.0 with four samples
per question, reported as the mean over all rollouts. `floor` is one over the
item's own candidate count: five for `substitution_rule`, two for
`threshold_rule`. `forced` is the strict grader, which requires the set of
candidates named by the answer to equal the gold set exactly, so naming a
second candidate counts wrong. `hedge` is the rate of naming more candidates
than the answer has.

Narrow budget, `~/mg3/roll_gate.jsonl` scored into `~/mg3/strict_gate_narrow.json`:

| family | decode | nQ | nR | floor | shipped | forced | first | hedge | none | rounds | any_ret | well_formed | degen |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| substitution_rule | greedy | 500 | 500 | 0.200 | 0.972 | 0.950 | 0.954 | 0.022 | 0.018 | 1.00 | 1.000 | 0.988 | 0.000 |
| substitution_rule | t1 x4 | 500 | 2000 | 0.200 | 0.874 | 0.875 | 0.887 | 0.016 | 0.103 | 0.98 | 0.981 | 0.949 | 0.000 |
| threshold_rule | greedy | 500 | 500 | 0.500 | 0.998 | 0.008 | 0.466 | 0.990 | 0.000 | 1.00 | 1.000 | 1.000 | 0.000 |
| threshold_rule | t1 x4 | 500 | 2000 | 0.500 | 0.902 | 0.061 | 0.453 | 0.851 | 0.042 | 0.98 | 0.982 | 0.947 | 0.000 |

Wide budget, `~/mg3/roll_gate_wide.jsonl` scored into `~/mg3/strict_gate_wide.json`:

| family | decode | nQ | nR | floor | shipped | forced | first | hedge | none | rounds | any_ret | well_formed | degen |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| substitution_rule | greedy | 500 | 500 | 0.200 | 0.974 | 0.954 | 0.958 | 0.020 | 0.018 | 1.00 | 1.000 | 0.988 | 0.000 |
| substitution_rule | t1 x4 | 500 | 2000 | 0.200 | 0.870 | 0.873 | 0.879 | 0.013 | 0.107 | 0.98 | 0.982 | 0.951 | 0.002 |
| threshold_rule | greedy | 500 | 500 | 0.500 | 0.998 | 0.008 | 0.466 | 0.990 | 0.000 | 1.00 | 1.000 | 1.000 | 0.000 |
| threshold_rule | t1 x4 | 500 | 2000 | 0.500 | 0.887 | 0.051 | 0.439 | 0.849 | 0.051 | 0.98 | 0.979 | 0.953 | 0.001 |

The gate passes. Under the shipped grader and the budget the controls were
recorded at, `substitution_rule` comes back 0.972 greedy against 0.969 on
record and `threshold_rule` 0.998 against 1.000. At temperature one the two
are 0.874 against 0.828 and 0.902 against 0.922. Widening the budget to the
mathgen window moves nothing: 0.974 and 0.998 greedy. Any mathgen number that
follows is not a budget artifact and is not a broken harness.

The strict column is the second half of the gate, and it reproduces a known
result rather than a new one. `threshold_rule` has two candidates and the
policy names both in 99.0% of greedy answers, so 0.998 shipped becomes 0.008
forced, against 0.009 recorded by the earlier forced-choice regrade of the same
family. `substitution_rule` hedges in 2.0% of answers and holds at 0.954. The
strict grader here is therefore calibrated against a number the project already
has, which is what lets it be used on mathgen items that have no such record.

Chance-corrected, `(acc - floor)/(1 - floor)`: `substitution_rule` greedy is
0.968 shipped and 0.943 forced. `threshold_rule` greedy is 0.996 shipped and
-0.984 forced, that is, below its own floor, because a policy that always names
both candidates never satisfies a forced choice.

Retrieval is healthy everywhere in the gate: one round on essentially every
rollout, well-formed queries on 0.95 to 1.00, and no degenerate queries.

## What a hand-written program gets off the same pages

`scripts/mg_trivial_baseline.py` reads the same episodes files the policy is
served, finds the tables page among the documents, rebuilds the algebra from
the printed grid, and answers. It touches no model. Two tiers:

    parser   the question is parsed as well. The prompt is scanned for one
             expression over the printed element names and glyphs; prompts that
             bind a variable or write no expression are declined. Nothing is
             read from the answer key except the gold used to score.
    recipe   the structured recipe is taken from the answer key, so this tier
             answers every question kind. It bounds what a program reading only
             the chunks can do with the question already parsed.

25 universes, 1111 exercises, 593 `stated_in_a_chapter` and 518
`derived_by_computation`. The parser found the tables page in all 25 own
libraries and all 25 sibling libraries, and in none of the blank ones.
Rollouts are `~/mg3/roll_trivial.jsonl`, scored into `~/mg3/strict_trivial.json`.

| condition | tier | answer_source | n | attempted | correct | floor | shipped | forced | acc on attempted |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| own | recipe | stated_in_a_chapter | 593 | 593 | 593 | 0.141 | 1.000 | 1.000 | 1.000 |
| own | recipe | derived_by_computation | 518 | 518 | 518 | 0.154 | 1.000 | 1.000 | 1.000 |
| own | parser | stated_in_a_chapter | 593 | 0 | 0 | 0.141 | 0.000 | 0.000 | n/a |
| own | parser | derived_by_computation | 518 | 157 | 151 | 0.154 | 0.292 | 0.292 | 0.962 |
| sibling | recipe | stated_in_a_chapter | 593 | 529 | 113 | 0.141 | 0.191 | 0.103 | 0.214 |
| sibling | recipe | derived_by_computation | 518 | 479 | 60 | 0.154 | 0.116 | 0.097 | 0.125 |
| sibling | parser | derived_by_computation | 518 | 157 | 19 | 0.154 | 0.037 | 0.037 | 0.121 |
| blank | either | either | 1111 | 0 | 0 | 0.141/0.154 | 0.000 | 0.000 | n/a |

The recipe tier is 1.000 on both families. Every one of these 1111 exercises is
fully determined by the text on the pages the policy is served, and a program
of a few hundred lines recovers all of it from the printed grid. Whatever a low
policy score means here, it does not mean the questions are unanswerable from
the evidence.

The parser tier fixes the other end. It declines every `stated_in_a_chapter`
item, because those prompts name an invented definition rather than write an
expression, and it declines the derived items that bind a variable. On the 157
derived items it does attempt it is 0.962. So the expression-shaped part of the
benchmark falls to a regex over the table, and the rest needs the definitions
chapter read.

The sibling column is the coincidence rate for these items, measured rather
than assumed. A rival system wearing the same names answers 0.191 of the
`stated` items and 0.116 of the `derived` ones the same way, 0.103 and 0.097
under the forced grader. Anything a policy scores on sibling pages has to clear
that, not zero.

## The core split

`src/mathgen/rlbridge.py` writes each universe's `chunks.jsonl` as the document
store of one episode, so the pages arrive only through the retrieval channel in
`src/rl/env.py` and the policy has to query for what it needs. Exercise
sections are dropped from the retrievable library: they print prompts and no
answers, and the generator's own `answer_source` label is measured against a
textbook built without them.

25 universe seeds, 0 through 24, 1111 exercises. Every cell below is one
`answer_source` family. Nothing is pooled across the label anywhere in this
file. Rollouts are `~/mg3/roll_mathgen.jsonl` (16,665 rows), scored into
`~/mg3/strict_mathgen.json` with the per-rollout grades in
`~/mg3/graded_mathgen.jsonl`. The config is `configs/mg3-mathgen.yaml`.

Own pages, the condition H8 is about:

| answer_source | decode | nQ | nR | floor | shipped | forced | first | c_forced | pass@4 forced | hedge | none named | rounds | any_ret | well_formed | degen |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| stated_in_a_chapter | greedy | 593 | 593 | 0.141 | 0.000 | 0.000 | 0.000 | -0.164 | n/a | 0.000 | 0.995 | 0.24 | 0.243 | 0.602 | 0.000 |
| derived_by_computation | greedy | 518 | 518 | 0.154 | 0.004 | 0.004 | 0.004 | -0.178 | n/a | 0.006 | 0.956 | 0.33 | 0.326 | 0.465 | 0.000 |
| stated_in_a_chapter | t1 x4 | 593 | 2372 | 0.141 | 0.000 | 0.002 | 0.002 | -0.162 | 0.0067 | 0.001 | 0.985 | 0.26 | 0.261 | 0.737 | 0.000 |
| derived_by_computation | t1 x4 | 518 | 2072 | 0.154 | 0.003 | 0.003 | 0.003 | -0.179 | 0.0116 | 0.000 | 0.980 | 0.30 | 0.301 | 0.724 | 0.000 |

The two families side by side under the strict forced-choice grader, on the
universe's own pages: `stated_in_a_chapter` 0.000 on 593 questions against a
floor of 0.141, and `derived_by_computation` 0.004 on 518 questions against a
floor of 0.154. Greedy answers 0 and 2 questions correctly. At temperature one
with four samples the same two are 0.002 and 0.003, and best-of-four is 0.0067
and 0.0116. Both families sit below their own guessing floors, and the gap
between them, 0.004, is smaller than one question in either denominator.

By level, own pages, greedy. `stated_in_a_chapter` has no level 1 items:

| answer_source | level | nQ | floor | shipped | forced | any_ret | ans_in_ret |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| stated_in_a_chapter | 2 | 18 | 0.220 | 0.000 | 0.000 | 0.278 | 0.278 |
| stated_in_a_chapter | 3 | 305 | 0.126 | 0.000 | 0.000 | 0.456 | 0.220 |
| stated_in_a_chapter | 4 | 102 | 0.049 | 0.000 | 0.000 | 0.000 | 0.000 |
| stated_in_a_chapter | 5 | 168 | 0.217 | 0.000 | 0.000 | 0.000 | 0.000 |
| derived_by_computation | 1 | 81 | 0.211 | 0.012 | 0.012 | 0.210 | 0.136 |
| derived_by_computation | 2 | 174 | 0.135 | 0.000 | 0.000 | 0.155 | 0.144 |
| derived_by_computation | 3 | 66 | 0.109 | 0.000 | 0.000 | 0.136 | 0.091 |
| derived_by_computation | 4 | 93 | 0.097 | 0.000 | 0.000 | 0.269 | 0.226 |
| derived_by_computation | 5 | 104 | 0.222 | 0.010 | 0.010 | 0.875 | 0.490 |

Macro-averaged over the level cells, both orders, own pages. The two
corrections differ and are printed apart because they have been conflated on
this project once already:

| macro cell | grader | cells | macro_acc | macro_floor | corrected_of_macro | macro_of_corrected |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| greedy, stated_in_a_chapter | shipped and forced | 4 | 0.0000 | 0.1530 | -0.1806 | -0.1887 |
| greedy, derived_by_computation | shipped and forced | 5 | 0.0044 | 0.1547 | -0.1778 | -0.1820 |
| t1, stated_in_a_chapter | shipped | 4 | 0.0002 | 0.1530 | -0.1803 | -0.1885 |
| t1, stated_in_a_chapter | forced | 4 | 0.0008 | 0.1530 | -0.1796 | -0.1877 |
| t1, derived_by_computation | shipped and forced | 5 | 0.0028 | 0.1547 | -0.1797 | -0.1843 |

`corrected_of_macro` is `(mean_acc - mean_floor)/(1 - mean_floor)`.
`macro_of_corrected` is `mean over cells of (acc_c - floor_c)/(1 - floor_c)`.
Here they differ by about 0.006 to 0.008, which is small only because every
cell is pinned at zero; the two orders are not interchangeable.

### Why the score is what it is

The retrieval columns carry the explanation and it is not the answer source.
On the gate the policy issues one query on essentially every rollout. On
mathgen it issues none on 798 of 1111 greedy rollouts, and returns an empty
string on 513 of them. It names no object from the carrier in 95.6% of derived
rollouts and 99.5% of stated ones. What it does emit is off-alphabet: asked to
name the earliest object witnessing a failure of relation symmetry, with gold
`fexvash`, it answered `Vramdra`, a word that is not in the system.

When it does retrieve, it retrieves usefully often enough to rule out a
retrieval-quality explanation for the whole gap. On derived level 5 items it
queries on 0.875 of rollouts and the served chunks contain the gold string on
0.490 of them, and the cell still scores 0.010.

The `answer_in_library` column reads 0.987 and 0.990, near one for both
families, and it is not evidence about copyability. Almost every answer is a
single invented object name, and every object name is printed in the operation
table, so a plain substring audit of the library cannot separate the two
families. That is why the generator labels `answer_source` by rendering the
sentence the textbook would print for that answer and searching the prose for
that sentence, rather than for the bare answer.

## The controls

Sibling pages come from `Structure.sibling()`: the same system name, object
names, glyphs and relation symbol over different tables, rendered as a full
textbook. Blank pages are a single page reading "This page is intentionally
blank."

| condition | answer_source | decode | nQ | nR | floor | shipped | forced | any_ret | ans_in_ret |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| own | stated_in_a_chapter | greedy | 593 | 593 | 0.141 | 0.000 | 0.000 | 0.243 | 0.121 |
| sibling | stated_in_a_chapter | greedy | 593 | 593 | 0.141 | 0.000 | 0.000 | 0.243 | 0.096 |
| blank | stated_in_a_chapter | greedy | 593 | 593 | 0.141 | 0.000 | 0.000 | 0.243 | 0.000 |
| own | derived_by_computation | greedy | 518 | 518 | 0.154 | 0.004 | 0.004 | 0.326 | 0.220 |
| sibling | derived_by_computation | greedy | 518 | 518 | 0.154 | 0.004 | 0.004 | 0.326 | 0.203 |
| blank | derived_by_computation | greedy | 518 | 518 | 0.154 | 0.000 | 0.000 | 0.326 | 0.000 |
| own | stated_in_a_chapter | t1 x4 | 593 | 2372 | 0.141 | 0.000 | 0.002 | 0.261 | 0.121 |
| sibling | stated_in_a_chapter | t1 x4 | 593 | 2372 | 0.141 | 0.001 | 0.002 | 0.270 | 0.101 |
| blank | stated_in_a_chapter | t1 x4 | 593 | 2372 | 0.141 | 0.001 | 0.002 | 0.261 | 0.000 |
| own | derived_by_computation | t1 x4 | 518 | 2072 | 0.154 | 0.003 | 0.003 | 0.301 | 0.180 |
| sibling | derived_by_computation | t1 x4 | 518 | 2072 | 0.154 | 0.001 | 0.001 | 0.296 | 0.148 |
| blank | derived_by_computation | t1 x4 | 518 | 2072 | 0.154 | 0.000 | 0.000 | 0.301 | 0.000 |

Serving the correct universe is worth nothing over serving a rival one. Own and
sibling are identical to three decimals in every greedy cell, 0.000 and 0.004,
and the correct pages do not beat the blank page by as much as one question in
the stated family. Across own, sibling and blank the trivial program's forced
score on `stated_in_a_chapter` runs 1.000, 0.103, 0.000 and on
`derived_by_computation` 1.000, 0.097, 0.000. The policy's runs 0.000, 0.000,
0.000 and 0.004, 0.004, 0.000. The controls have nothing to discriminate, which
is itself the result.

## What this says about H8 and about the rule-application claim

H8 predicted `stated_in_a_chapter` near 0.514 and `derived_by_computation` near
0.000. Measured, under the strict forced-choice grader on the universe's own
pages: 0.000 on 593 questions against a 0.141 floor, and 0.004 on 518 questions
against a 0.154 floor. The prediction is refuted. The families do not differ.

H8 named three outcomes. Close together and high would have meant the
rule-application result was measuring retrieval. That is not what happened, and
this evaluation gives no support to that reading. Close together and low, which
is what happened, H8 assigned to the instrument being harder than the skillacq
families in some way that is not the answer source, with the gate distinguishing
the two cases. The gate passes at 0.974 and 0.998 under the identical harness,
model, budget and grader, and the trivial parser answers all 1111 exercises off
the same pages, so neither the harness nor the evidence is the difficulty.

What is left is the policy's own behaviour. It stops issuing retrieval queries,
returns an empty string on 46% of greedy rollouts, and names a word from the
system's carrier in under 5% of them. That is the same failure the wording
ablation found by a different route: this checkpoint's competence is attached to
the sentence frames it was trained on, and mathgen writes every question in
frames it has never seen. On this instrument the answer-source axis is not
measurable, because the policy does not engage with either family.

So this evaluation does not weaken the rule-application result by showing it was
retrieval, and it does not confirm it either. It sets a boundary on it: the
0.680 figure does not survive a change of surface form into an independently
built instrument, and the instrument is demonstrably solvable from the pages it
serves.

## Artifacts

Everything a number here came from, on the p5 box:

    ~/mg3/universes/            25 universes, seeds 0-24, plus summary.json
    ~/mg3/gate/                 skillacq gate episodes, both families
    ~/mg3/episodes/             mathgen episodes, own, sibling and blank
    ~/mg3/roll_gate.jsonl       gate rollouts, narrow budget
    ~/mg3/roll_gate_wide.jsonl  gate rollouts, mathgen budget
    ~/mg3/roll_mathgen.jsonl    16,665 policy rollouts
    ~/mg3/roll_trivial.jsonl    6,666 trivial-program rows
    ~/mg3/strict_gate_narrow.json, strict_gate_wide.json
    ~/mg3/strict_mathgen.json, graded_mathgen.jsonl
    ~/mg3/strict_trivial.json
    ~/mg3/main.log, gate.log     run logs

The p5 box is ephemeral, so the same tree is mirrored to
`s3://decoupled-reasoner-009398924577/results/mathgen-h8/`, keeping the paths
above under that prefix.

Code: `scripts/mg_threeway_eval.py` runs the rollouts,
`scripts/mg_strict_rescore.py` grades and aggregates,
`scripts/mg_trivial_baseline.py` is the parser,
`scripts/mg_eval_tables.py` prints the tables above,
`src/mathgen/rlbridge.py` serves a universe through the retrieval channel.
