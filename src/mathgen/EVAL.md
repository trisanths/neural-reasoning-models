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
