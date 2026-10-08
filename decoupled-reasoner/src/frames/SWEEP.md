# The frame-diversity sweep

Does training on more sentence frames buy accuracy on frames that were never
trained on? Five arms start from one checkpoint and differ in exactly one
thing: how many distinct wordings the same examples are rendered in.

This answers the question left open by the renderer ablation in
`src/disc/TEMPLATE.md` and the generator in `src/frames/FRAMES.md`. That work
established that the checkpoint's rule-application result is sentence-frame
matching: three of four hand-written renderers on `substitution_rule` fall
below chance, the renderer that shares no content word with the native idiom
scores 0.840 while the renderer that keeps every content word and changes only
the sentence frame scores 0.030. What it could not say is whether that is a
property of the training corpus or of the substrate.

## Status

All five arms are trained. The 1-frame arm is evaluated and reported below.
The other four and the base checkpoint are decoding now; their numbers land
here as they finish.

## Design

Everything below is constant across arms.

- base checkpoint `~/rlckpt/rlsimple-503-921-final.pt`, the same 350M policy
  the published ablation was read off
- rule systems: `src/skillacq/simple.py`, seeds 3,100,000 to 3,102,499 per
  family, disjoint from the evaluation pool at 2,900,000
- families: `substitution_rule` and `exception_rule`. `threshold_rule` is
  excluded from training and from evaluation because it is a grading artifact
  in this instrument, hedging on essentially every greedy answer
- 8,423 examples, the same 8,423 in every arm, in the same shuffled order
- 3 epochs, batch 16 sequences, 1,578 optimizer steps, AdamW at 1e-5 with 40
  warmup steps and a cosine decay to a tenth
- 43,758 supervised answer tokens in every arm, exactly

The only thing that varies is the frame each example is rendered in. Example
i of a family gets `order[i % F]` where F is the arm's frame count and `order`
is a fixed nested list: `routing__native` first, then a fixed shuffle of the
71 remaining frames on the train side of the `both` split. So the 3-frame
arm's wordings are a subset of the 10-frame arm's, and so on. Arms are F = 1,
3, 10, 30, 72.

More frames never becomes more data. The 72-frame arm sees each frame about
117 times; the 1-frame arm sees its one frame 8,423 times. The example count,
the rule systems, the gold answers and the step count do not move.

### What holding it constant took

Two asymmetries had to be removed before the arms were comparable.

The first is retrieval. A training trace is what the environment would have
written for a competent policy: `<|retrieve|>`, the question text as the
query, `<|result|>`, the chunk BM25 actually returns over that episode's own
store, then `<|a|>`, the gold word, `<|eot|>`. Loss falls only on the tokens
the policy would have emitted; the served chunk is masked out exactly as
`src/rl/grpo.py` masks it. In the native frame that query surfaces the
answering page on 100% of questions. In other frames it surfaces it on about
91%. Keeping the misses would have handed the 1-frame arm clean
demonstrations and the many-frame arms a tenth of guesswork, so a trace whose
page never carried the gold is dropped, and then the arms are intersected:
an example trains only if every arm can demonstrate it with the page in
context. 8,423 of 10,000 survive that intersection, identically in all five
arms, and every arm's traces are served at rate 1.000.

The second is tokenization. The query segment is the question in that arm's
wording, so it tokenizes to different lengths: 349k query tokens in the
3-frame arm against 401k in the 30-frame arm. A single pooled denominator
would let that bleed into how hard the answer is trained. The loss is
therefore two terms, each normalized by its own token count, answer and
query, summed with weight 1. The answer term is the same gold word in every
arm and comes out at exactly 43,758 tokens everywhere.

### Why supervised traces and not RL

The base checkpoint was made with GRPO. GRPO drops a group whose rewards are
all equal, and the distant frames are exactly where this policy scores zero
on every rollout. Under RL the many-frame arms would have trained on fewer
gradient-carrying groups than the 1-frame arm, so "more frames" would have
quietly become "less training" and the comparison would be void. Behaviour
cloning gives every example the same weight in every arm, which is the
constant the experiment needs. The cost is that these arms are not the same
kind of object as the base checkpoint, so the base is re-evaluated here under
identical settings rather than compared against the published table.

## Evaluation

One fixed eval set for every arm, so a frame is "seen" or "held out"
per arm rather than by a different set of episodes.

- 20 generated frames, 100 episodes each, 2 questions per episode, 200
  questions per frame and family
- 13 of them sit at chosen positions in the nested order, so each is seen by
  some arms and unseen by others; 5 come from the `test` side of the `both`
  split and 2 from `bridge`, so those 7 are held out from every arm
- the 4 hand-written simple renderers from `src/disc/TEMPLATE.md`
  (`native`, `abstract`, `inventory`, `personnel`), scored the same way, so
  the numbers are comparable to what is already on record
- greedy and sampled at temperature 0.7, both reported
- forced choice is the headline: exactly one candidate named and it is the
  gold. Naming more than one is a hedge and counts wrong. `first` is the
  lenient tie-break, reported beside it, never instead of it
- every accuracy carries the chance floor computed from that item set's own
  option count, its denominator, the hedge rate, and the fraction of answers
  naming no candidate at all
- the hedging canary, a stand-in answering with every candidate on every
  item, is asserted at 0.000 forced on every cell before any number is read

Frame distance is the metric calibrated in `src/frames/FRAMES.md`: shape
distance is Levenshtein over the delexicalised skeleton, lexical distance is
one minus Jaccard overlap of the open-class words. For each arm, an eval
frame's distance is the smallest distance to anything that arm trained on.
That is what makes the result a curve against distance rather than a single
held-out number.

The five `test` frames stay genuinely far from every arm. Even for the
72-frame arm their minimum shape distance is 0.22 to 0.37, against a metric
noise floor of 0.078 over same-shape pairs.

## Trivial-program baseline

`python -m src.frames.cli parsers --dir ~/sweep/eval/gen`, over all 20
generated eval frames, both load-bearing families, 600 questions per cell
(the parsers read all six problems per episode where the model is asked two):

| parser | family | cells | forced, min | forced, max |
|---|---|---|---|---|
| frame_aware | substitution_rule | 20 | 0.992 | 0.992 |
| frame_aware | exception_rule | 20 | 1.000 | 1.000 |
| native_tuned | substitution_rule | 20 | 0.000 | 0.992 |
| native_tuned | exception_rule | 20 | 0.000 | 1.000 |

A fifty-line regex handed the frame reads every one of the 20 frames at
ceiling. The task is mechanically solvable in every wording, so a model that
collapses off frame is not being defeated by a harder problem. The 0.992 cap
on `substitution_rule` is an upstream defect in `src/skillacq/SubstitutionRule`
which can draw one key twice with two values; it caps every reader in every
frame equally. The same regex with the native wording baked in scores at
ceiling on the native frame and 0.000 on all 19 others, which is the
program-shaped version of the hypothesis under test.

Artifact: `~/sweep/res/parsers_gen.json`.

## First arm: one frame, 8,423 examples

Greedy, forced choice, 200 questions per frame and family, chance from each
item set's own option count.

| group | frames | n | forced | first | chance | none | served |
|---|---|---|---|---|---|---|---|
| substitution_rule, seen | 1 | 200 | 1.000 | 1.000 | 0.200 | 0.000 | 1.000 |
| substitution_rule, held out | 19 | 3800 | 0.468 | 0.468 | 0.200 | 0.180 | 0.980 |
| exception_rule, seen | 1 | 200 | 1.000 | 1.000 | 0.500 | 0.000 | 1.000 |
| exception_rule, held out | 19 | 3800 | 0.357 | 0.357 | 0.500 | 0.568 | 0.669 |

On its own frame the arm is at ceiling on both families. On the 19 frames it
never saw, `substitution_rule` sits at 0.468 against a 0.200 floor and
`exception_rule` at 0.357 against a 0.500 floor, which is below chance.

The single number hides the shape of it. Bucketed by the eval frame's shape
distance from the one frame this arm trained on:

| shape distance | frames | n | substitution forced | exception forced |
|---|---|---|---|---|
| 0.00, identical | 1 | 200 | 1.000 | 1.000 |
| 0.00-0.10 | 6 / 3 | 1200 / 600 | 0.919 | 0.815 |
| 0.10-0.25 | 3 / 5 | 600 / 1000 | 0.347 | 0.403 |
| 0.25-0.40 | 2 / 4 | 400 / 800 | 0.372 | 0.292 |
| 0.40-0.55 | 1 / 6 | 200 / 1200 | 0.885 | 0.188 |
| 0.55+ | 7 / 1 | 1400 / 200 | 0.102 | 0.025 |

Chance is 0.200 for `substitution_rule` and 0.500 for `exception_rule` in
every row. Frame counts differ between the families because the same 20 eval
frames sit at different shape distances when the distance is measured on each
family's own rendered page.

Two things in that table matter more than the averages.

Changing every content word costs almost nothing while the skeleton holds.
`kitchen__native`, `archive__native` and `depot__native` share the native
skeleton and share almost no vocabulary with it: lexical distance 0.53 to
0.65, shape distance 0.03 to 0.04. They score 0.910, 0.935 and 0.965 on
`substitution_rule` against the native frame's 1.000. Move the skeleton
instead and the same lexical distance is fatal: `depot__relative` is at
lexical 0.65 like the others but shape 0.19, and it scores 0.330.

The failure is mostly not a wrong answer. Across the 19 held-out frames
`exception_rule` names no candidate at all on 0.568 of questions, rising to
0.94 on `observatory__valuefirst`. `substitution_rule` holds its none-rate
near zero out to shape 0.27 and then breaks: 1.000 on `abstract__tablepipe`,
0.575 on `depot__tablecolon`, 0.545 on `abstract__conditional`. The model
stops answering rather than answering wrongly.

Retrieval and rule reading come apart, and the separation is family-specific.
On `substitution_rule` the answering page is served on 0.980 of held-out
questions, so `acc_forced_when_served` tracks `acc_forced` almost exactly and
the collapse is entirely a reading failure with the page in context. On
`exception_rule` served drops to 0.669, so part of that family's held-out
number is the policy failing to retrieve at all.

One frame breaks the monotonicity and should not be smoothed over.
`assembly__imperative` sits at shape 0.53 and lexical 0.91 from native, and
scores 0.885 on `substitution_rule` while frames at half that distance score
0.33. Whatever the metric orders, it does not order everything.

Artifacts: `~/sweep/res/score_arm001-gen-greedy.json`,
`~/sweep/res/report.json`, dumps under `~/sweep/dumps/arm001-gen-greedy/`.

## Coverage

Reported as it lands.
