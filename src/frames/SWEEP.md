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

Method, data and baselines are settled and the first arm is trained. Numbers
land here as each arm is evaluated.

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

## Coverage

Reported as it lands.
