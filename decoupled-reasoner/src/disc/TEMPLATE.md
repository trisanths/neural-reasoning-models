# The renderer swap: what survives a change of wording

**No. Once hedging is disallowed, the rule-acquisition result does not survive a
change of surface form.** On `substitution_rule`, the family whose native
wording is the surface the RL stage trained on, forced-choice accuracy is 0.970
in the native wording and 0.015 to 0.045 in three other ordinary English idioms,
against a 0.200 chance floor. On `exception_rule` it is 1.000 native against
0.106 to 0.606, with a 0.500 coin-flip floor that every distant renderer falls
below. `threshold_rule` is a grader artifact and is reported separately.

The chain task gives the same answer with retrieval removed, and adds the
mechanism: what carries the result is the sentence frame, not the vocabulary.

## What baseline this uses

Not the recorded 0.680, whose provenance could not be found. A falsification
lane re-ran `scripts/skill_rule_test.py` on the shipped checkpoint
`s3://decoupled-reasoner-009398924577/runs/final/rlsimple-503-921/final.pt` and
got 0.958 at n=500 and 0.968 at n=1000 on textbook evidence. The `native`
renderer here, built independently, gives 0.966 pooled at the same temperature.
The two agree, so the reference arm is the re-measured number.

## What the shipped grader counts

The environment grader accepts any prediction containing the gold with six
tokens of slack. `threshold_rule` offers two candidate labels, so an answer
naming both is scored correct whichever is right. That reproduces here
independently: `native` on `threshold_rule` names both labels in 100% of greedy
answers, and 1.000 under the shipped grader becomes 0.000 under forced choice.
At temperature 0.7 the same cells read 0.964 hedge, 0.988 shipped, 0.024 forced.
The lane's figures were 94.3% hedge and 0.985 to 0.009. Same phenomenon, same
size, separate harness.

`exception_rule` and `substitution_rule` never hedge in any renderer. They carry
the surface-form question.

## 1. The instrument

`src/disc/renderers.py` puts a renderer between the task and its words. A seed
builds the system; a renderer decides only how it is spelled.

The rule families are the three in `src/skillacq/simple.py`. Four renderers
share one seeded system: same thresholds, same labels, same table entries, same
problem values, same evidence conditions.

The chain task is `src/disc/minrepro.py`'s. Nine renderers share one seeded
`MinSystem`. Four of them form a two by two over the words used and the frame
they sit in.

| Renderer | Table line | Question at depth one |
|---|---|---|
| `routing` | A {k} is handled by the {v} desk. | A {s} request arrives at the {M} office. Which desk handles it? |
| `processing` | A {k} is processed by the {v} unit. | A {s} item arrives at the {M} stage. Which unit processes it? |
| `routing_frameb` | The {M} office sends {k} to {v}. | Send {s} through the {M} office. Which desk results? |
| `abstract` | The {M} map sends {k} to {v}. | Apply the {M} map to {s}. Which token results? |

`routing` is the RL training surface. `processing` keeps `routing`'s frame and
replaces every content word. `routing_frameb` keeps `routing`'s content words
and moves them into `abstract`'s frame. Three more (`inventory`, `personnel`,
`reaction`) are distant English idioms; two (`routing_keyphrase`,
`routing_postvalue`) are single edits from `routing`.

`scripts/template_ablation.py parity` reports zero mismatches over 20 seeds and
both depths: `routing` reproduces `minrepro.generate_episode` byte for byte, and
every renderer agrees with every other on question id, gold answer, starting
token and stage list, with the nine question wordings pairwise distinct.

## 2. The rule families under forced choice

`scripts/template_rescore.py` rescores per-rollout dumps. `shipped` is the
environment grader. `forced` requires exactly one distinct candidate named and
that it be the gold. `first` is the lenient tie-break where the first candidate
named wins. `hedge` names more than one, `none` names no candidate at all.
`chance` is uniform over the episode's candidate set; `chncPg` is uniform over
the invented words on the served pages. Textbook evidence, greedy, n=66, 66 and
68. Families are never pooled.

| Renderer | Family | shipped | forced | hedge | none | chance | chncPg |
|---|---|---|---|---|---|---|---|
| native | exception_rule | 1.000 | **1.000** | 0.000 | 0.000 | 0.500 | 0.750 |
| personnel | exception_rule | 0.606 | **0.606** | 0.000 | 0.152 | 0.500 | 0.269 |
| abstract | exception_rule | 0.258 | **0.258** | 0.000 | 0.530 | 0.500 | 0.197 |
| inventory | exception_rule | 0.106 | **0.106** | 0.000 | 0.864 | 0.500 | 0.045 |
| native | substitution_rule | 0.985 | **0.970** | 0.015 | 0.015 | 0.200 | 0.111 |
| personnel | substitution_rule | 0.045 | **0.045** | 0.000 | 0.894 | 0.200 | 0.057 |
| abstract | substitution_rule | 0.045 | **0.045** | 0.000 | 0.652 | 0.200 | 0.053 |
| inventory | substitution_rule | 0.015 | **0.015** | 0.000 | 0.939 | 0.200 | 0.054 |
| native | threshold_rule | 1.000 | 0.000 | 1.000 | 0.000 | 0.500 | 0.333 |
| personnel | threshold_rule | 0.794 | 0.191 | 0.603 | 0.103 | 0.500 | 0.259 |
| abstract | threshold_rule | 0.397 | 0.191 | 0.206 | 0.235 | 0.500 | 0.211 |
| inventory | threshold_rule | 0.441 | 0.132 | 0.309 | 0.441 | 0.500 | 0.098 |

`substitution_rule` is the family that discriminates. Five candidates put the
chance floor at 0.200 and the page-word floor at 0.111. Native sits at 0.970;
all three distant wordings sit at 0.015 to 0.045, well under both floors.

`exception_rule` has two candidates, so a coin flip scores 0.500 and a reader
picking a random invented word off the native page scores 0.750. Native's 1.000
clears that; every distant renderer lands below the coin flip. The drop is real
but the family has little headroom to measure it in.

The failures are not near misses. In the distant renderers the dominant outcome
is `none`: 0.53 to 0.94 of answers name no candidate of either family at all.

## 3. The twin-system control

A second system of the same family sits in the same store, differing only in its
invented names and values. The question names the reading and the classification,
so the right page is identifiable in principle. `own` and `twin` are the share of
answers naming each system's words. Greedy.

| Renderer | Family | forced (textbook) | forced (twin) | own | twin |
|---|---|---|---|---|---|
| native | exception_rule | 1.000 | 0.682 | 0.682 | 0.288 |
| native | substitution_rule | 0.970 | 0.939 | 0.955 | 0.045 |
| native | threshold_rule | 0.000 | 0.000 | 0.971 | 0.000 |

The control bites, and it bites unevenly. On `exception_rule` native falls from
1.000 to 0.682 and names the twin's words in 28.8% of answers: the model picks a
rule line off a page without reliably telling which system's page it is.
`substitution_rule` barely moves, 0.970 to 0.939 with 4.5% twin-naming, so
there the model does identify the page.

This matters for the template question because it is the family that survives
the twin control, `substitution_rule`, that shows the largest renderer effect
(0.970 native against 0.015 to 0.045). The wording effect is therefore not a
page-identification effect wearing a disguise. The chain task settles the same
point more directly in section 4.

In the distant renderers the twin condition adds little, because they rarely
name any candidate: `abstract` on `substitution_rule` names its own words in
0.318 of answers and the twin's in 0.000. They are not confusing the two
systems; they are producing no candidate.

## 4. The chain task, with retrieval removed

Depth one, greedy, n=100 per renderer. `table_only` drops the preamble, leaving
one document in the store, so whatever the policy asks for is the answering
page and page identification cannot fail. Chance is 0.028 over the six-token
alphabet.

| Renderer | forced (gold pages) | forced (table_only) | none (table_only) |
|---|---|---|---|
| `routing` | 0.800 | **0.970** | 0.000 |
| `processing` | 0.730 | **0.840** | 0.020 |
| `routing_postvalue` | 0.670 | **0.830** | 0.080 |
| `routing_keyphrase` | 0.560 | **0.820** | 0.000 |
| `reaction` | 0.010 | **0.090** | 0.310 |
| `routing_frameb` | 0.000 | **0.030** | 0.890 |
| `inventory` | 0.010 | **0.010** | 0.550 |
| `abstract` | 0.000 | **0.010** | 0.890 |
| `personnel` | 0.000 | **0.000** | 0.860 |

Two things follow.

The effect is not retrieval and not page identification. With a one-document
store the ordering is unchanged and the spread widens.

What carries the result is the frame, not the vocabulary. `processing` shares no
content word with `routing` and scores 0.840. `routing_frameb` shares every
content word with `routing`, moves them into `abstract`'s frame, and scores
0.030. Swapping the nouns costs 0.13; keeping the nouns and swapping the
sentence shape costs 0.94.

Depth two is 0.000 in every renderer and both page conditions, so the
composition wall SLATE reports is not a wording artifact.

## 5. What this does to SLATE section 3

SLATE recorded a swing from at most 0.19 to 0.84 at depth one between an
abstract notation and the routing idiom, with presentation moving at the same
time. Under matched presentation the gap is 0.960 forced (`routing` 0.970,
`abstract` 0.010) in the retrieval-free condition. Template accounts for the
entire recorded gap and then some; nothing is left for presentation to explain.

## 6. Caveats

One checkpoint. Every number is `rlsimple-503-921`.

The temperature-0.7 run drew on a 250-episode set in which the `personnel`
renderer lost 150 episodes to the 384-token prompt cap, leaving its sample the
shortest 40%. The greedy runs quoted in sections 2 and 3 use a 100-episode set
where all four renderers keep exactly 200 questions, so the cross-renderer
comparison there is unfiltered. Prefer the greedy tables for renderer contrasts.

The renderers are hand written, chosen to be lexically distant rather than
sampled. The two single-edit arms and the `processing` / `routing_frameb`
dissociation constrain the explanation considerably, but a different set could
land differently.

`exception_rule` has a 0.500 coin-flip floor and a 0.750 page-word floor in the
native wording, so it discriminates poorly. `substitution_rule` carries most of
the weight of the conclusion.
