# Capability primitive profile

Mode: integrated. 40 items per primitive, seed 0, 2920 model calls, 456.2s.

Never pooled. Every faculty carries its own sample size, its own
chance rate and its own Wilson interval.

Format warning. The requested answer format was produced on only 5% of items on average (intent 0%, gap 0%, acquisition 0%, abstraction 0%). Every grader here falls back to reading the whole reply, and binary fields are read through a synonym list, so these numbers are not pure format failures. They are still an upper bound on what this instrument can see of this model: a faculty the model cannot express is a faculty this suite cannot measure, and the profile below should be read as a floor rather than an estimate.

## Headline, one line per faculty

| faculty | generation | forced choice | reading |
|---|---|---|---|
| intent | +0.000 | not offered | mean chance-adjusted score over the five extracted fields |
| gap | -0.900 | +0.000 (0/2 above chance) | chance-adjusted blocked against solvable detection |
| acquisition | +0.000 | -0.117 (0/2 above chance) | query recall at 1 minus the verbatim-copy baseline |
| abstraction | -0.632 | -0.014 (0/6 above chance) | transfer accuracy minus the copy baseline, per structure |
| composition | sequential=0, relational=0, novel=0 | -0.020 (0/18 above chance) | greatest depth still above chance, per kind |
| memory | -0.250 | -0.056 (0/1 above chance) | mean chance-adjusted score over retain-far, interfere, update |
| verification | -0.850 | +0.042 (0/2 above chance) | chance-adjusted trap detection |

## Intent understanding

n=40, parse rate 0.000.

| field | accuracy | adjusted |
|---|---|---|
| goal | 0.000 [0.000, 0.088] n=40 | +0.000 vs chance 0.000  (at chance) |
| conflict | 0.000 [0.000, 0.088] n=40 | +0.000 vs chance 0.000  (at chance) |
| success | 0.000 [0.000, 0.088] n=40 | +0.000 vs chance 0.000  (at chance) |
| constraints_exact | 0.000 [0.000, 0.088] n=40 | +0.000 vs chance 0.000  (at chance) |
| constraints (mean overlap) | 0.000 [0.000, 0.000] n=40 | |
| uncertain (mean overlap) | 0.000 [0.000, 0.000] n=40 | |

Conflict detection split by whether the request really
contradicts itself, so a model that always reports one is
visible:

| arm | accuracy | adjusted |
|---|---|---|
| conflict | 0.000 [0.000, 0.161] n=20 | +0.000 vs chance 0.000  (at chance) |
| consistent | 0.000 [0.000, 0.161] n=20 | +0.000 vs chance 0.000  (at chance) |

## Missing-capability recognition

| measure | accuracy | adjusted |
|---|---|---|
| detection | 0.050 [0.014, 0.165] n=40 | -0.900 vs chance 0.500  (at chance) |
| gap type | 0.000 [0.000, 0.161] n=20 | -0.111 vs chance 0.100  (at chance) |
| false alarm on solvable | 0.000 [0.000, 0.161] n=20 | +0.000 vs chance 0.000  (at chance) |
| miss on blocked | 1.000 [0.839, 1.000] n=20 | +1.000 vs chance 0.000 |
| named a value it could not know | 0.000 [0.000, 0.088] n=40 | +0.000 vs chance 0.000  (at chance) |

Parse rate 0.000.

## Information acquisition

The score reads the query, not an answer.

| measure | value | adjusted |
|---|---|---|
| direct: source selection | 0.000 [0.000, 0.088] n=40 | -0.333 vs chance 0.250  (at chance) |
| direct: recall@1 | 0.000 [0.000, 0.088] n=40 | +0.000 vs chance 0.000  (at chance) |
| direct: recall@3 | 0.325 [0.201, 0.480] n=40 | +0.325 vs chance 0.000 |
| direct: copy baseline@1 | 0.000 [0.000, 0.088] n=40 | +0.000 vs chance 0.000  (at chance) |
| direct: empty query | 0.000 [0.000, 0.088] n=40 | +0.000 vs chance 0.000  (at chance) |
| recursive: source selection | 0.000 [0.000, 0.088] n=40 | -0.333 vs chance 0.250  (at chance) |
| recursive: recall@1 | 0.075 [0.026, 0.199] n=40 | +0.075 vs chance 0.000 |
| recursive: recall@3 | 0.200 [0.105, 0.348] n=40 | +0.200 vs chance 0.000 |
| recursive: copy baseline@1 | 0.000 [0.000, 0.088] n=40 | +0.000 vs chance 0.000  (at chance) |
| recursive: empty query | 0.000 [0.000, 0.088] n=40 | +0.000 vs chance 0.000  (at chance) |
| recursive: second-hop recall@1 (reads the served page, contaminated) | 0.075 [0.026, 0.199] n=40 | +0.075 vs chance 0.000 |

## Abstraction construction

Transfer cost, same surface minus transfer: +0.000.

| condition | accuracy | copy baseline | beats copy |
|---|---|---|---|
| same_surface | 0.000 [0.000, 0.088] n=40 | 0.650 [0.495, 0.779] n=40 | no |
| transfer | 0.000 [0.000, 0.088] n=40 | 0.650 [0.495, 0.779] n=40 | no |

| condition and rule | accuracy | copy | margin |
|---|---|---|---|
| same_surface/greater | 0.000 [0.000, 0.243] n=12 | 0.500 [0.254, 0.746] n=12 | -0.500 |
| same_surface/lesser | 0.000 [0.000, 0.243] n=12 | 0.583 [0.320, 0.807] n=12 | -0.583 |
| same_surface/parity | 0.000 [0.000, 0.194] n=16 | 0.812 [0.570, 0.934] n=16 | -0.812 |
| transfer/greater | 0.000 [0.000, 0.243] n=12 | 0.500 [0.254, 0.746] n=12 | -0.500 |
| transfer/lesser | 0.000 [0.000, 0.243] n=12 | 0.583 [0.320, 0.807] n=12 | -0.583 |
| transfer/parity | 0.000 [0.000, 0.194] n=16 | 0.812 [0.570, 0.934] n=16 | -0.812 |

## Composition depth, three curves, never pooled

### sequential

Depth still above chance: k*=0, step-conditioned k*=0.

Per-step probe accuracy 0.002 [0.000, 0.009] n=600; items whose every step was answered correctly on its own: 0.005.

| k | accuracy | adjusted | step-clean accuracy |
|---|---|---|---|
| 1 | 0.000 [0.000, 0.088] n=40 | -0.143 vs chance 0.125  (at chance) | 0.000 [0.000, 0.793] n=1 |
| 2 | 0.000 [0.000, 0.088] n=40 | -0.143 vs chance 0.125  (at chance) | n/a |
| 3 | 0.000 [0.000, 0.088] n=40 | -0.143 vs chance 0.125  (at chance) | n/a |
| 4 | 0.000 [0.000, 0.088] n=40 | -0.143 vs chance 0.125  (at chance) | n/a |
| 5 | 0.000 [0.000, 0.088] n=40 | -0.143 vs chance 0.125  (at chance) | n/a |

### relational

Depth still above chance: k*=0.

Per-step probe accuracy 0.002 [0.000, 0.009] n=600; items whose every step was answered correctly on its own: 0.000.

| k | accuracy | adjusted | step-clean accuracy |
|---|---|---|---|
| 1 | 0.000 [0.000, 0.088] n=40 | -0.143 vs chance 0.125  (at chance) | n/a |
| 2 | 0.000 [0.000, 0.088] n=40 | -0.143 vs chance 0.125  (at chance) | n/a |
| 3 | 0.000 [0.000, 0.088] n=40 | -0.143 vs chance 0.125  (at chance) | n/a |
| 4 | 0.000 [0.000, 0.088] n=40 | -0.143 vs chance 0.125  (at chance) | n/a |
| 5 | 0.000 [0.000, 0.088] n=40 | -0.143 vs chance 0.125  (at chance) | n/a |

### novel

Depth still above chance: k*=0.

Per-step probe accuracy 0.000 [0.000, 0.006] n=600; items whose every step was answered correctly on its own: 0.000.

| k | accuracy | adjusted | step-clean accuracy |
|---|---|---|---|
| 1 | 0.000 [0.000, 0.088] n=40 | -0.143 vs chance 0.125  (at chance) | n/a |
| 2 | 0.000 [0.000, 0.088] n=40 | -0.143 vs chance 0.125  (at chance) | n/a |
| 3 | 0.000 [0.000, 0.088] n=40 | -0.143 vs chance 0.125  (at chance) | n/a |
| 4 | 0.000 [0.000, 0.088] n=40 | -0.143 vs chance 0.125  (at chance) | n/a |
| 5 | 0.000 [0.000, 0.088] n=40 | -0.143 vs chance 0.125  (at chance) | n/a |


## Temporary knowledge

Distance cost, near minus far: +0.000.

| arm | accuracy | adjusted |
|---|---|---|
| absent | 0.000 [0.000, 0.088] n=40 | -0.250 vs chance 0.200  (at chance) |
| interfere | 0.000 [0.000, 0.088] n=40 | -0.250 vs chance 0.200  (at chance) |
| retain_far | 0.000 [0.000, 0.088] n=40 | -0.250 vs chance 0.200  (at chance) |
| retain_near | 0.000 [0.000, 0.088] n=40 | -0.250 vs chance 0.200  (at chance) |
| update | 0.000 [0.000, 0.088] n=40 | -0.250 vs chance 0.200  (at chance) |
| intrusion, answered the interfering value | 0.000 [0.000, 0.088] n=40 | +0.000 vs chance 0.000  (at chance) |
| leak, answered the voided episode's value | 0.000 [0.000, 0.046] n=80 | +0.000 vs chance 0.000  (at chance) |

Median prompt length 238 words.

## Verification and action

Detection and correction are scored apart.

| measure | value | adjusted |
|---|---|---|
| detection | 0.075 [0.035, 0.154] n=80 | -0.850 vs chance 0.500  (at chance) |
| correction, all items | 0.062 [0.027, 0.138] n=80 | -0.125 vs chance 0.167  (at chance) |
| correction given detection | 0.000 [0.000, 0.390] n=6 | -0.200 vs chance 0.167  (at chance) |
| trap recall | 0.050 [0.014, 0.165] n=40 | -0.900 vs chance 0.500  (at chance) |
| false alarm on controls | 0.025 [0.004, 0.129] n=40 | -0.950 vs chance 0.500  (at chance) |
| overcorrected a correct candidate | 0.050 [0.014, 0.165] n=40 | +0.050 vs chance 0.000 |

| trap shape | detection | correction |
|---|---|---|
| constraint | 0.050 [0.014, 0.165] n=40 | 0.000 [0.000, 0.088] n=40 |
| exception | 0.100 [0.040, 0.231] n=40 | 0.125 [0.055, 0.261] n=40 |

## Forced choice, the same items scored by preference

Producing an answer and preferring the right one are
different abilities. This channel scores the option texts by
likelihood, the way the held-out suite scores multiple
choice, so a model that cannot write the requested format is
still asked the same question. It is reported beside the
generation channel and never instead of it.

| faculty | field | accuracy | adjusted |
|---|---|---|---|
| abstraction | same_surface/greater/answer | 0.500 [0.254, 0.746] n=12 | +0.000 vs chance 0.500  (at chance) |
| abstraction | same_surface/lesser/answer | 0.750 [0.468, 0.911] n=12 | +0.500 vs chance 0.500  (at chance) |
| abstraction | same_surface/parity/answer | 0.375 [0.185, 0.614] n=16 | -0.250 vs chance 0.500  (at chance) |
| abstraction | transfer/greater/answer | 0.417 [0.193, 0.680] n=12 | -0.167 vs chance 0.500  (at chance) |
| abstraction | transfer/lesser/answer | 0.417 [0.193, 0.680] n=12 | -0.167 vs chance 0.500  (at chance) |
| abstraction | transfer/parity/answer | 0.500 [0.280, 0.720] n=16 | +0.000 vs chance 0.500  (at chance) |
| acquisition | direct/source | 0.325 [0.201, 0.480] n=40 | +0.100 vs chance 0.250  (at chance) |
| acquisition | recursive/source | 0.000 [0.000, 0.088] n=40 | -0.333 vs chance 0.250  (at chance) |
| composition | novel/k1 | 0.050 [0.014, 0.165] n=40 | -0.086 vs chance 0.125  (at chance) |
| composition | novel/k2 | 0.050 [0.014, 0.165] n=40 | -0.086 vs chance 0.125  (at chance) |
| composition | novel/k3 | 0.150 [0.071, 0.291] n=40 | +0.029 vs chance 0.125  (at chance) |
| composition | novel/k4 | 0.125 [0.055, 0.261] n=40 | +0.000 vs chance 0.125  (at chance) |
| composition | novel/k5 | 0.200 [0.105, 0.348] n=40 | +0.086 vs chance 0.125  (at chance) |
| composition | novel/probe | 0.110 [0.087, 0.138] n=600 | -0.017 vs chance 0.125  (at chance) |
| composition | relational/k1 | 0.025 [0.004, 0.129] n=40 | -0.114 vs chance 0.125  (at chance) |
| composition | relational/k2 | 0.050 [0.014, 0.165] n=40 | -0.086 vs chance 0.125  (at chance) |
| composition | relational/k3 | 0.100 [0.040, 0.231] n=40 | -0.029 vs chance 0.125  (at chance) |
| composition | relational/k4 | 0.075 [0.026, 0.199] n=40 | -0.057 vs chance 0.125  (at chance) |
| composition | relational/k5 | 0.050 [0.014, 0.165] n=40 | -0.086 vs chance 0.125  (at chance) |
| composition | relational/probe | 0.533 [0.493, 0.573] n=600 | +0.067 vs chance 0.500  (at chance) |
| composition | sequential/k1 | 0.000 [0.000, 0.088] n=40 | -0.143 vs chance 0.125  (at chance) |
| composition | sequential/k2 | 0.175 [0.087, 0.320] n=40 | +0.057 vs chance 0.125  (at chance) |
| composition | sequential/k3 | 0.175 [0.087, 0.320] n=40 | +0.057 vs chance 0.125  (at chance) |
| composition | sequential/k4 | 0.225 [0.123, 0.375] n=40 | +0.114 vs chance 0.125  (at chance) |
| composition | sequential/k5 | 0.075 [0.026, 0.199] n=40 | -0.057 vs chance 0.125  (at chance) |
| composition | sequential/probe | 0.122 [0.098, 0.150] n=600 | -0.004 vs chance 0.125  (at chance) |
| gap | gap_type | 0.200 [0.081, 0.416] n=20 | +0.000 vs chance 0.200  (at chance) |
| gap | status | 0.500 [0.352, 0.648] n=40 | +0.000 vs chance 0.500  (at chance) |
| memory | answer | 0.155 [0.111, 0.212] n=200 | -0.056 vs chance 0.200  (at chance) |
| verification | answer | 0.312 [0.222, 0.421] n=80 | +0.083 vs chance 0.250  (at chance) |
| verification | check | 0.500 [0.393, 0.607] n=80 | +0.000 vs chance 0.500  (at chance) |

Scores are length normalised, the option's summed negative log likelihood divided by its token count,
because several fields here have a correct option that is systematically the longest and an unnormalised
score picks the shortest option nearly every time. The unnormalised numbers are kept in the JSON under
forced_choice._unnormalised; where the two disagree sharply, option length is doing the work.
