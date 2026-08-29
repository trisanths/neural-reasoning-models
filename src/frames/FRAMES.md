# A frame generator, and what the checkpoint does across 13 of its frames

**The generator works and the known pattern reproduces.** Sentence frames are
sampled from a grammar rather than hand written, 156 of them, with the gold
answers, candidate counts, page counts and prompt lengths held fixed across
all of them. On `substitution_rule`, forced choice, greedy, n=200 per cell,
chance 0.200: the frame that reproduces the trained wording scores 0.940, its
two single-edit neighbours score 0.890 and 0.600, and every frame past a shape
distance of 0.19 scores 0.170 down to 0.000.

Two things the hand-written ablation could not say come out of this.

On these families the vocabulary is not cheap. `src/disc/TEMPLATE.md` measured
nouns at 0.13 and sentence shape at 0.94 on the chain task. Here a frame that
holds the sentence shape and swaps only the domain words (`depot__native`,
shape distance 0.035, lexical distance 0.600) drops from 0.940 to 0.100, and a
frame that holds the words and moves the shape (`routing__relative`, shape
0.194, lexical 0.136) drops to 0.170. Both axes break it, and both correlate
with accuracy at about the same strength.

The retrieval protocol is frame-bound too, not only the rule application. On
the two frames whose question is an imperative, the policy emits no
`<|retrieve|>` at all in 200 of 200 greedy rollouts, on all three families,
and answers with an invented capitalised word that is in no candidate set
(`Vramdra` 123 times of 200, `Polgux` 27). It is not answering badly from a
retrieved page. It never asks.

Nothing here was trained. One checkpoint,
`s3://decoupled-reasoner-009398924577/runs/final/rlsimple-503-921/final.pt`.

## 1. What a frame is

A frame is a lexicon crossed with a shape.

A lexicon (`src/frames/lexicon.py`) is words and no structure: for
`substitution_rule` it names the entity, the key role, the value role, the
site, the section heading, and five inflected forms of the verbs that carry
the mapping. Thirteen of them, from `routing` through `depot`, `registry`,
`forge` and `abstract`.

A shape (`src/frames/forms.py`) is structure and no domain words. It fixes how
a mapping row is written (passive, active, conditional, colon table, pipe
table, imperative, relative clause, value first, `x pairs with y`), where the
key sits relative to the value, how the three pages are ordered and titled,
where the fallback clause sits, and how the question is posed (arrival
narrative, direct wh, imperative, `Consider ...`, postposed wh). Twelve of
them.

13 x 12 = 156 frames, and frame count is a knob: `--frames` takes any subset,
and adding a lexicon or a shape multiplies the space rather than adding to it.

The frames render the systems in `src/skillacq/simple.py` untouched. A `Frame`
is a `src.disc.renderers.SimpleRenderer`, so episodes are built by the
published `renderers.simple_episode`. The random draw order that decides which
problems survive rejection, the distractor page, the twin page and the
candidate list are the published instrument's, not a lookalike.

The grammar point (`routing` lexicon, `native` shape) reproduces
`src/skillacq/simple.py` byte for byte in all three families. That is checked,
not asserted: 300 episodes over the smoke seeds and 75 over the sweep seeds,
zero differences in page text or question text.

## 2. How far apart two frames are

Reported as two numbers, because the effect being measured is exactly the
difference between them.

`src/frames/distance.py` delexicalises rendered text: invented words become
role tags (`NAME`, `KEY`, `VAL`), digits become `NUM`, closed-class English
stays as itself, every remaining open-class word becomes `W`. What is left is
a skeleton and a bag of words.

    shape distance   Levenshtein over the skeleton, over the longer length
    lexical distance 1 minus Jaccard overlap of the open-class words

The skeleton does not depend on the seed, which a test pins. Both measures run
on rendered text, so they apply to a hand-written renderer that knows nothing
about the generator. That is what makes the calibration below mean something.

### The metric against renderers whose accuracies are already known

`src/disc/TEMPLATE.md` section 4 gives forced-choice accuracies for nine
hand-written chain renderers in the retrieval-free `table_only` condition,
chance 0.028. Running the metric over those same nine, anchored on `routing`:

| renderer | shape | lexical | published accuracy |
|---|---|---|---|
| routing | 0.000 | 0.000 | 0.970 |
| processing | 0.029 | 0.742 | 0.840 |
| routing_postvalue | 0.087 | 0.000 | 0.830 |
| routing_keyphrase | 0.133 | 0.000 | 0.820 |
| inventory | 0.236 | 0.781 | 0.010 |
| personnel | 0.301 | 0.833 | 0.000 |
| reaction | 0.370 | 0.833 | 0.090 |
| routing_frameb | 0.493 | 0.719 | 0.030 |
| abstract | 0.507 | 0.946 | 0.010 |

Shape distance sorts them. The four renderers scoring 0.82 and above are
exactly the four with shape distance at or below 0.133; every renderer at 0.236
or above scores 0.090 or less. Lexical distance does not sort them: at nearly
the same lexical distance, `processing` (0.742) scores 0.840 and
`routing_frameb` (0.719) scores 0.030, a gap of 0.81 that lines up with a shape
gap of 0.46. The metric recovers the published dissociation from text alone.

One property to disclose rather than hide. Two frames of the same shape do not
score exactly 0 on shape distance, because a few lexicon roles carry their own
preposition ("handled by" against "stored in") and prepositions are closed
class. Over the 936 frame pairs that share a shape, the largest shape distance
is 0.078. Two deliberate single-edit shapes sit below that (`keyphrase` at
0.026, `postvalue` at 0.070 from `native`), which is the point of having them;
they are the generated counterparts of the published `routing_keyphrase` and
`routing_postvalue` arms. Over the 11,154 pairs that do not share a shape the
median is 0.557, 7.2 times the floor.

## 3. The held-out split, quantified

`split_frames` partitions the generative parameters, not the frames. The
`both` policy holds out four lexicons and four shapes and keeps a test frame
only when it is new on both axes, so a test frame shares neither its words nor
its skeleton with anything on the train side. The native lexicon and native
shape always stay on the train side. Frames new on exactly one axis are held
out of both sides and reported as `bridge`.

Seed 20260828 gives test lexicons `abstract, assembly, kitchen, panel` and test
shapes `active, condthen, imperative, tablepipe`: 72 train, 16 test, 68 bridge.

Pairwise distances, `substitution_rule`, one seed (the skeleton is seed
invariant and the lexicons are fixed):

| bucket | pairs | shape min | shape p25 | shape median | lex min | lex p25 | lex median |
|---|---|---|---|---|---|---|---|
| within train | 2556 | 0.000 | 0.163 | 0.534 | 0.000 | 0.613 | 0.839 |
| within test | 120 | 0.000 | 0.349 | 0.605 | 0.167 | 0.625 | 0.844 |
| train to test | 1152 | 0.216 | 0.354 | 0.565 | 0.474 | 0.667 | 0.909 |

That is what held out buys: within the training side two frames can be
identical on either axis, but no test frame is within 0.216 shape or 0.474
lexical of any training frame. `split_lexicon` and `split_shape` are written
too, for holding out one axis at a time.

## 4. Parity, held constant across frames

Over all 156 frames, three families and 25 seeds, 11,700 frame-family-seed
cells: zero mismatches. Over the 13 smoke frames at 100 seeds, 3,900 cells:
zero mismatches. Checked per cell:

- gold answers agree, question by question and qid by qid, across every frame
- candidate sets are identical, so the chance floor is identical: 5 candidates
  on `substitution_rule` (0.200), 2 on `exception_rule` and `threshold_rule`
  (0.500)
- page count is 3 gold pages plus 3 distractor pages in every frame
- the invented words visible on the page are the same set in every frame
- no invented word collides with any frame's English, over every seed checked
- no answer appears in its own question, in any frame
- the whole rendered surface is distinct between any two frames

Frames may pose the question identically and differ only on the rule page.
Across the 156 frames, on average 86.7 of them duplicate another frame's
question wording; among the 13 smoke frames it is 2.7. That is deliberate,
`postvalue` against `native` being the generated version of the published
`routing_postvalue` arm, which kept routing's question word for word.
Distinctness is required of the whole surface.

Token length, measured with the project tokenizer, as a ratio to the native
frame in the same family:

| quantity | range over the 13 smoke frames |
|---|---|
| prompt tokens, mean | 0.894 to 1.106 |
| page tokens, mean | 0.735 to 1.072 |
| questions dropped at the 384-token prompt cap | 0 of 600, every frame |

The two shortest are the table-shaped frames, `routing__tablecolon` at 0.735
and `abstract__tablepipe` at 0.769 on page tokens; everything else sits inside
0.93 to 1.07. Prompt length is not a rival explanation here for a reason worth
stating: episodes carry `n_context: 0`, so the prompt holds the world preamble
and the question only, 25 to 35 tokens, and the pages arrive through
retrieval. Nothing was dropped by the cap that cost the published `personnel`
run 150 of its 250 episodes.

## 5. The smoke evaluation

Thirteen frames, chosen to span the shape and lexical axes and to place a
generated counterpart beside each arm of the published ablation. 100 episodes
per cell, 2 questions per episode, n=200 rollouts per cell, greedy and
temperature 0.7, `textbook` evidence condition, one model load per pass.

Columns: `shape` and `lex` are distances to `routing__native` in that family.
`forced` requires exactly one distinct candidate named and that it be the
gold. `served` is the share of rollouts where a page carrying the gold came
back from retrieval, and `frcdSv` is forced choice among only those, which is
accuracy with the answering page demonstrably in context. `parseF` and
`parseN` are the two trivial programs of section 7. Families are never pooled.

### substitution_rule, 5 candidates, chance 0.200

| frame | side | shape | lex | forced | hedge | none | served | frcdSv | T0.7 forced | shipped | parseF | parseN |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| routing__native | train | 0.000 | 0.000 | **0.940** | 0.035 | 0.025 | 0.995 | 0.945 | 0.940 | 0.975 | 0.992 | 0.992 |
| routing__keyphrase | train | 0.026 | 0.000 | **0.890** | 0.070 | 0.005 | 0.995 | 0.894 | 0.870 | 0.960 | 0.992 | 0.992 |
| routing__postvalue | train | 0.070 | 0.000 | **0.600** | 0.245 | 0.090 | 0.990 | 0.606 | 0.830 | 0.845 | 0.992 | 0.197 |
| depot__native | train | 0.035 | 0.600 | **0.100** | 0.060 | 0.445 | 0.570 | 0.175 | 0.160 | 0.160 | 0.992 | 0.000 |
| registry__native | train | 0.044 | 0.645 | **0.145** | 0.165 | 0.105 | 0.900 | 0.161 | 0.260 | 0.305 | 0.992 | 0.000 |
| routing__relative | train | 0.194 | 0.136 | **0.170** | 0.055 | 0.015 | 0.990 | 0.172 | 0.175 | 0.200 | 0.992 | 0.197 |
| routing__active | bridge | 0.252 | 0.136 | **0.040** | 0.015 | 0.420 | 0.580 | 0.069 | 0.080 | 0.055 | 0.992 | 0.197 |
| panel__active | test | 0.252 | 0.656 | **0.025** | 0.005 | 0.230 | 0.775 | 0.032 | 0.025 | 0.030 | 0.992 | 0.000 |
| registry__imperative | bridge | 0.474 | 0.941 | **0.000** | 0.000 | 1.000 | 0.000 | n/a | 0.010 | 0.000 | 0.992 | 0.000 |
| assembly__imperative | test | 0.526 | 0.912 | **0.000** | 0.000 | 1.000 | 0.000 | n/a | 0.000 | 0.000 | 0.992 | 0.000 |
| routing__tablecolon | train | 0.614 | 0.615 | **0.005** | 0.010 | 0.895 | 0.610 | 0.008 | 0.020 | 0.010 | 0.992 | 0.197 |
| abstract__tablepipe | test | 0.632 | 0.833 | **0.000** | 0.000 | 1.000 | 0.610 | 0.000 | 0.000 | 0.000 | 0.992 | 0.000 |
| kitchen__condthen | test | 0.636 | 0.971 | **0.050** | 0.000 | 0.630 | 0.420 | 0.119 | 0.045 | 0.050 | 0.992 | 0.000 |

Ten of the thirteen frames sit at or below the 0.200 chance floor, and they
fail in two different ways. In seven of them the dominant outcome is naming no
candidate at all, `none` running 0.420 to 1.000. In the other three the model
does name exactly one candidate and names the wrong one: `routing__relative`
names a single candidate on 0.985 of items, gets the answering page back on
0.990, and is right on 0.170, which is a five-way choice made at chance with
the page in context.

### exception_rule, 2 candidates, chance 0.500

| frame | side | shape | lex | forced | hedge | none | served | frcdSv | T0.7 forced | shipped |
|---|---|---|---|---|---|---|---|---|---|---|
| routing__native | train | 0.000 | 0.000 | **0.980** | 0.000 | 0.010 | 0.980 | 1.000 | 0.965 | 0.980 |
| routing__keyphrase | train | 0.149 | 0.071 | **0.705** | 0.000 | 0.290 | 0.705 | 1.000 | 0.835 | 0.705 |
| routing__postvalue | train | 0.060 | 0.067 | **0.965** | 0.000 | 0.025 | 0.980 | 0.985 | 0.935 | 0.965 |
| depot__native | train | 0.071 | 0.550 | **0.120** | 0.000 | 0.860 | 0.110 | 1.000 | 0.270 | 0.120 |
| registry__native | train | 0.030 | 0.526 | **0.600** | 0.000 | 0.230 | 0.600 | 1.000 | 0.420 | 0.600 |
| routing__relative | train | 0.209 | 0.333 | **0.620** | 0.000 | 0.285 | 0.785 | 0.790 | 0.625 | 0.620 |
| routing__active | bridge | 0.313 | 0.294 | **0.475** | 0.000 | 0.465 | 0.585 | 0.812 | 0.505 | 0.475 |
| panel__active | test | 0.343 | 0.739 | **0.470** | 0.000 | 0.420 | 0.555 | 0.847 | 0.265 | 0.470 |
| registry__imperative | bridge | 0.403 | 0.833 | **0.000** | 0.000 | 1.000 | 0.000 | n/a | 0.005 | 0.000 |
| assembly__imperative | test | 0.433 | 0.840 | **0.000** | 0.000 | 1.000 | 0.000 | n/a | 0.005 | 0.000 |
| routing__tablecolon | train | 0.507 | 0.471 | **0.230** | 0.000 | 0.765 | 0.710 | 0.324 | 0.270 | 0.230 |
| abstract__tablepipe | test | 0.537 | 0.818 | **0.090** | 0.000 | 0.910 | 0.565 | 0.159 | 0.100 | 0.090 |
| kitchen__condthen | test | 0.478 | 0.826 | **0.255** | 0.000 | 0.560 | 0.415 | 0.614 | 0.195 | 0.255 |

This family never hedges, in any frame, at either temperature. With a
coin-flip floor at 0.500 it has little headroom, and eight of thirteen frames
fall below it. It agrees with `substitution_rule` on ordering and carries less
of the weight.

### threshold_rule, reported apart

`src/disc/TEMPLATE.md` established this family as a grading artifact in the
native wording, and that reproduces exactly: the native frame hedges on 0.990
of greedy answers, so 0.995 under the shipped grader becomes 0.005 under
forced choice.

| frame | forced | hedge | none | shipped | T0.7 forced |
|---|---|---|---|---|---|
| routing__native | 0.005 | 0.990 | 0.000 | 0.995 | 0.010 |
| routing__keyphrase | 0.015 | 0.970 | 0.000 | 0.985 | 0.035 |
| routing__postvalue | 0.005 | 0.990 | 0.000 | 0.995 | 0.010 |
| registry__native | 0.195 | 0.585 | 0.050 | 0.780 | 0.220 |
| routing__relative | 0.295 | 0.400 | 0.090 | 0.695 | 0.215 |
| routing__active | 0.410 | 0.125 | 0.115 | 0.535 | 0.325 |
| routing__tablecolon | 0.500 | 0.000 | 0.105 | 0.500 | 0.410 |
| abstract__tablepipe | 0.385 | 0.000 | 0.320 | 0.400 | 0.335 |

Forced accuracy rises as the frame moves away from the trained one, because
distant frames stop naming both labels. That is the hedge rate falling, not
the rule being applied better; the shipped column falls from 0.995 to 0.400
down these rows while the forced column rises from 0.005 to 0.500. Any pooling
that includes this family would move the headline in the wrong direction, which is why it is here and not above.

## 6. What the smoke says

The pattern to reproduce was: high on frames resembling the trained idiom, at
or below chance on distant ones. It reproduces. `routing__native` at 0.940
forced against the published 0.970 for the hand-written `native` renderer on
the same family, and 0.975 shipped against the published 0.985. The seed range
is the same, though every seed is used for every family here rather than every
third, so the item sets are not identical.

Three things go beyond reproduction.

Retrieval is not the explanation on the frames where it can be ruled out.
`routing__relative` holds the domain words (lexical 0.136) and moves the
sentence geometry, gets the answering page back in 0.990 of rollouts, and
still scores 0.172 forced with the page in context, below the 0.200 floor. The
model reads a page it asked for and does not apply the rule on it.

Both axes cost, unlike the chain task. Spearman correlation of forced accuracy
against distance over the 13 frames, greedy: on `substitution_rule`, -0.805
against shape and -0.796 against lexical; on `exception_rule`, -0.735 and
-0.900. On the chain task the lexical axis was nearly free (`processing`
0.840). Here `depot__native` swaps only the words and falls to 0.100. The
difference between the two tasks is that the chain measurement was made in a
one-document store where page identification cannot fail, and these episodes
carry six pages, so a lexicon swap costs retrieval as well as reading. The
`served` column shows both costs: `depot__native` serves the answering page
only 0.570 of the time, and conditional on serving it still scores 0.175.

The retrieval protocol itself is frame-bound. Both imperative-question frames
produce `any_retrieval` 0.000 and `mean_rounds` 0.00 over 200 greedy rollouts
on all three families. The question "Process an nakxil item through the Yukqen
stage. Name the unit." does not cause the policy to ask for anything. It
answers `Vramdra` (123 of 200), `Polgux` (27), `Gramgrum` (16), words that
appear on no page and in no candidate set. At temperature 0.7 it retrieves on
0.010 to 0.025 of rollouts and accuracy stays at 0.000 to 0.010. This is not
visible in the accuracy column alone and would have been read as ordinary
failure without the retrieval counters.

Sampled decoding does not rescue any distant frame, and it changes one near
one. `routing__postvalue` goes from 0.600 greedy to 0.830 sampled, because
greedy hedged on 0.245 of its answers and sampling hedges on 0.060. Of the
cells at or below their chance floor under greedy, two cross it under sampling
and neither goes far: `registry__native` on `substitution_rule`, 0.145 to
0.260 against a 0.200 floor, and `routing__active` on `exception_rule`, 0.475
to 0.505 against 0.500.

## 7. The trivial-program baselines

Two hand-written parsers read the same pages (`src/frames/parsers.py`). Both
are handed the question's key rather than parsing it out of the question,
which makes them stronger than a text-only program and is the conservative
direction for the second.

The frame-aware parser reads the rule with the frame's own regex. It scores
0.992 on `substitution_rule` and 1.000 on `exception_rule` in every one of the
13 frames, including all four held-out ones. Every frame states its rule as
mechanically as the native frame does, so a model that collapses off frame is
not being defeated by a harder task.

The 0.008 shortfall is upstream and frame independent.
`skillacq.SubstitutionRule` draws its four keys independently and sometimes
draws the same key twice with two different values, at which point the page
lists both rows and the recorded gold is the second. That is 5 items in 600,
in every frame equally, and it caps the substitution family at 0.992 for any
reader.

The native-tuned parser is the same code with the training frame baked in: the
regexes of `src/skillacq/simple.py` and nothing else. It scores 0.992 on the
native frame and collapses off it exactly as the model does. On the four frames that keep the routing
lexicon and change the row, the native fallback sentence still matches, so it
returns the fallback value on every item and lands at 0.197, just under the
0.200 chance floor. On every frame with a different lexicon it matches nothing and
returns an empty answer on 1.000 of items.

That comparison is the point of the baseline. On the trained frame the task is
trivially parseable and the model's 0.940 tells us nothing about reasoning: a
fifty line regex beats it. Off frame the frame-aware parser stays at 0.992
while the model goes to 0.000, so the collapse is a property of the reader and
not of the task. And a program that knows one surface fails off frame in the
same shape the model does, naming nothing at all.

## 8. Grading, floors, and the canary

Forced choice is stated as an exact single choice: the distinct candidates
named in the answer as whole words, in order of first appearance; correct when
exactly one is named and it is the gold. `first` is the lenient tie-break and
is reported beside it, never instead of it. `hedge` is more than one named,
`none` is zero named.

The hedging canary is a stand-in that answers with every candidate on every
item. Across all 39 greedy cells and all 39 sampled cells it scores 0.000
forced, 1.000 hedge, and 1.000 under the shipped containment grader. The
scorer refuses to write a record file if it ever scores above zero forced.
`src/frames/tests/test_frames.py` pins it independently on the native frame
and on a sample of others.

Two chance floors travel with every accuracy. `chance` is uniform over the
episode's own candidate set, computed from that set's size, 0.200 on
`substitution_rule` and 0.500 on the other two. `chncPg` is uniform over the
invented words visible on the served pages. The invented-word vocabulary is
built per frame and per family, never pooled: each frame's ordinary English is
constant within that frame and absent from the others, so a pooled vocabulary
classifies one frame's English as invented. Vocabulary sizes run 142 to 391
words on the greedy cells that retrieve, and 0 on the six cells that retrieve
nothing, all of them on the two imperative frames; their `chncPg` of 0.000
means undefined, not measured.

A second scorer agrees. Running the published `scripts/template_rescore.py`
over the same dumps returns the same `forced`, `first`, `hedge`, `none`,
`chance` and `chncPg` to three decimals on every cell tried.

The scorer refuses stale records. Every dump must be at least as new as the
episode file it claims to come from, or `score` exits without writing
anything, on the same reasoning as `src/primitives/cli.py`: a dump left
behind by an earlier generation of the same episode file mixes two runs and
the result looks entirely normal. The guard was tested by touching one
episode file and confirming the score refused and wrote no output; the file
was restored to its recorded mtime and its checksum is unchanged. Both score
files carry the episode and dump mtimes they were built from, under
`freshness`.

Macro-averaging over frames within one family, both aggregation orders:

    order A   (mean_i acc_i - mean_i c_i) / (1 - mean_i c_i)
    order B   mean_i [ (acc_i - c_i) / (1 - c_i) ]

| family | cells | macro acc | macro chance | A | B |
|---|---|---|---|---|---|
| substitution_rule | 13 | 0.228 | 0.200 | 0.035 | 0.035 |
| exception_rule | 13 | 0.424 | 0.500 | -0.152 | -0.152 |
| threshold_rule | 13 | 0.197 | 0.500 | -0.605 | -0.605 |

The two orders coincide within a family because the candidate count is
constant there. They diverge as soon as families are mixed, which is the case
the rule against pooling exists for. Pooling the two load-bearing families
over the same 26 cells gives A = -0.037 and B = -0.059, a factor of 1.6 apart
on a number that is near zero either way.

## 9. Caveats

One checkpoint, `rlsimple-503-921`. Everything here is that checkpoint.

Thirteen frames evaluated out of 156 generated. The sweep is what the
generator makes possible; this is the smoke that says it is worth running.

The 13 frames were chosen to span the axes and to place a generated
counterpart beside each published arm. They are not a random sample of the
frame space, and the Spearman correlations in section 6 are over those 13
chosen points, so they describe the chosen span rather than the space.

Only one evidence condition, `textbook`. The twin, `wrong_textbook` and
`no_documents` conditions are supported by the generator and were not run.

Three templates place the article before the key word rather than before the
noun it agrees with, so a frame can emit "Process an nakxil item". The native
wording has the same wart ("A ovilum request arrives"), it is constant within
a frame, and it does not touch any gold answer.

`threshold_rule` remains a grading artifact under the shipped grader and is
reported apart from the two families carrying the conclusion. It has no
trivial-program baseline; the parsers cover `substitution_rule` and
`exception_rule` only.

The lexicons are hand written, thirteen of them. The shapes are hand written,
twelve of them. What is generated is the cross, and the guarantee is that
train and test frames come from one process and can be held disjoint by
construction. A larger or differently chosen set of lexicons and shapes could
land differently.

## 10. Artifacts

Every number above comes from one of these files. They live on the dev box at
`/home/ec2-user/frames` and are mirrored to
`s3://decoupled-reasoner-009398924577/scratch/frames/framesart.tgz`.

| file | what it holds |
|---|---|
| `/home/ec2-user/frames/parity_all.json` | parity over 156 frames, 25 seeds, 11,700 cells |
| `/home/ec2-user/frames/parity_smoke.json` | parity over the 13 smoke frames, 100 seeds |
| `/home/ec2-user/frames/distance_substitution.json` | distances, split distributions, chain calibration |
| `/home/ec2-user/frames/distance_exception.json` | the same for `exception_rule` |
| `/home/ec2-user/frames/smoke_frame_distances.json` | the 13 frames' distances to the native frame |
| `/home/ec2-user/frames/split_both.json` | the held-out frame test set, strict split |
| `/home/ec2-user/frames/split_lexicon.json` | lexicon-only holdout |
| `/home/ec2-user/frames/split_shape.json` | shape-only holdout |
| `/home/ec2-user/frames/eps/` | 39 episode files and their manifest |
| `/home/ec2-user/frames/eps/audit.json` | token-length parity |
| `/home/ec2-user/frames/parsers.json` | both trivial-program baselines |
| `/home/ec2-user/frames/eval_greedy.json`, `eval_t07.json` | rollout summaries |
| `/home/ec2-user/frames/dump_greedy/`, `dump_t07/` | per-rollout dumps, 39 files each |
| `/home/ec2-user/frames/score_greedy.json`, `score_t07.json` | the scored records behind every table |
| `/home/ec2-user/frames/analysis.json` | correlations and the pooled-macro demonstration |
| `/home/ec2-user/frames/parsers.log` | the parser table as printed |
| `/home/ec2-user/frames/frames.log` | the sweep log |

The smoke ran on the training box, GPU 0, claimed while idle at 0% and 0 MiB,
under `CUDA_VISIBLE_DEVICES=0`. Greedy 01:05:33 to 01:15:43 UTC, sampled
01:15:43 to 01:28:07.

## 11. Running it

    export PYTHONPATH=.
    F=routing__native,routing__keyphrase,routing__postvalue,routing__relative,\
    routing__tablecolon,depot__native,registry__native,routing__active,\
    registry__imperative,abstract__tablepipe,panel__active,kitchen__condthen,\
    assembly__imperative

    python -m src.frames.cli frames   --out $O/split_both.json
    python -m src.frames.cli parity   --episodes 25 --out $O/parity_all.json
    python -m src.frames.cli distance --calibrate --out $O/distance_substitution.json
    python -m src.frames.cli gen      --frames $F --out $O/eps --episodes 100
    python -m src.frames.cli audit    --dir $O/eps --tokenizer $TK
    python -m src.frames.cli parsers  --dir $O/eps --out $O/parsers.json
    python -m src.frames.cli eval     --dir $O/eps --checkpoint $CK --tokenizer $TK \
        --out $O/eval_greedy.json --dump-dir $O/dump_greedy --temperature 0.0 \
        --batch 32 --max-len 640 --max-prompt-tokens 384 --max-rounds 4 \
        --max-new-tokens 96 --questions-per-episode 2
    python -m src.frames.cli score    --dir $O/eps --dump-dir $O/dump_greedy \
        --out $O/score_greedy.json

    pytest src/frames/tests/test_frames.py
