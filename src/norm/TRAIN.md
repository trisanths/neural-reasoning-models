# The normalizer

One network with one job: turn surface text into a typed structure of
`src/norm/lang.py`. It never executes anything, never sees a gold answer and is
never told what a page means. Everything the structure is later used for
happens in `src/norm/interp.py`, which is a program.

The claim under test is that this job needs no world knowledge and should
therefore be far smaller than a language model. That is measured here across
four sizes rather than asserted, and the answer is mixed: a 1.73M parameter
network is already exact on eight of the fourteen structure shapes, and no size
tried reaches the hand written parser on the frames the parser was written for.

## 1. Why this trains

The structure comes first and the text is derived from it. `src/norm/gen.py`
draws a structure, `src/norm/render.py` writes it into one of the corpus's 768
sentence frames, and the pair is training data. The target is exact by
construction, there is no labelling step, and the loss is an ordinary cross
entropy over a translation. Nothing is a reward and nothing is a search. Data
is unlimited: 1,200,000 pairs were drawn for this and drawing more costs
minutes of CPU.

## 2. The frame split

Three disjoint kinds of frame are withheld, so that a held-out item is new in a
named way rather than new in general.

| group | what is withheld | frames |
|---|---|---|
| `train` | nothing | 490 |
| `qframe` | the corpus's own held-out band, every eighth frame, which is exactly `wh` question form with the scope first. Both axis values appear in training, never together | 70 |
| `lexicon` | every frame of the `signal` lexicon. Its English nouns are in the input word list and the network never reads a sentence written with them | 70 |
| `mode` | every frame in `relative_clause`. The network never reads a rule stated in that sentence shape | 98 |
| `mixed` | two or three of the above at once | 40 |

Structures are drawn fresh per example, so an evaluation item is new on its
structure as well as on its frame. Written by `src/norm/ndata.py:split_frames`;
manifest at `~/decoupled-reasoner/data/norm/manifest.json`.

## 3. The token seam

Neither side is a subword tokenizer.

Input: English words, single digits and single punctuation marks. The English
word list is the union of every frame's own reserved set, 923 tokens with the
slots. An invented word is alphabetic and outside that list, by construction of
`Lexicon`, so the two are disjoint. Invented words are bound to numbered copy
slots `W0..W63` in order of first appearance and their surface strings travel
beside the ids. The network never sees a nonce spelling and never spells one
back.

Output: a closed vocabulary of 155 tokens. Definition kinds, field markers, the
thirteen plan operations, canonical temporary names, the 64 slots, the digits.
An integer is written `#` then its digits, so a number the page states is
copied digit by digit.

`serialize` and `deserialize` are exact inverses on every program the fourteen
renderable shapes produce in every frame group, and
`src/norm/tests/test_ntok.py` is the gate on that.

## 4. The sizes

An encoder-decoder transformer, `src/norm/nmodel.py`. Nothing is pretrained.
Same data, same 30,000 steps, same batch budget of 32,768 padded tokens, same
seed, cosine schedule.

| size | d_model | heads | enc/dec layers | d_ff | total params | non-embedding | wall |
|---|---|---|---|---|---|---|---|
| `xs` | 64 | 2 | 2 / 2 | 256 | 404,608 | 232,192 | pending |
| `s` | 128 | 4 | 3 / 3 | 512 | 1,729,280 | 1,384,448 | 907 s |
| `m` | 256 | 8 | 4 / 4 | 1024 | 8,051,200 | 7,361,536 | 2,184 s |
| `l` | 512 | 8 | 6 / 6 | 2048 | 45,483,008 | 44,103,680 | training |

The 350M checkpoint this project trained is 43x the `m` normalizer and 7.7x the
`l` one.

## 5. How a result is counted

Structure level exact match against the structure that wrote the text. A
structure that is nearly right is wrong, because the interpreter executes it
exactly. Four outcomes, counted apart, never pooled across shape:

    exact       the emitted structure equals the gold structure
    malformed   the token stream is not a structure, so nothing reaches the
                interpreter
    refused     the interpreter is handed the structure and declines it
    wrong       the structure executes and is not the gold structure

The first three are safe. The fourth is the dangerous one, and the ratio
between them is reported on every row.

`exact` is the strict score. The lenient companion is `answer_ok`: the emitted
structure executes to the same text the gold structure does on the question the
page asks. The hedge rate is `malformed + refused`.

The floor. There is no finite option count for a structure, so the floor is the
best constant guess: `modal` is the most frequent training target emitted for
every item, and `modal_shape` is the most frequent target for the item's own
shape, handed to the baseline for free off the evaluation split. Slot ids are
positional, so `modal_shape` is not near zero on fixed arity shapes. For
`answer_ok` the floor is a real option count, `answer_chance_floor`, from the
values the gold plan's last step could have returned.

## 6. The trivial programs

`src/norm/parse.py` is the hand written reference parser. It is handed the
frame id and the normalizer is not, so `parser_exact` in every table below is a
generous baseline: 1.0000 on every split, including the withheld ones, because
it holds the templates for all 768 frames.

The fair trivial program is that parser searched over only the 490 training
frames, keeping the first reading that succeeds, which is exactly the knowledge
the network is trained on. `src/norm/nsearch.py`, n=280 per split, at
`results/norm/nsearch/summary.json`:

| split | exact_first | refused |
|---|---|---|
| `train_frames_eval` | 1.0000 | 0.0000 |
| `qframe` | 0.9143 | 0.0857 |
| `lexicon` | 0.0000 | 1.0000 |
| `mode` | 0.0000 | 1.0000 |
| `mixed` | 0.0000 | 1.0000 |

That is the boundary the network has to cross and the bar it has to clear. On
training frames and on the held-out question band the parser search is at or
near ceiling. On the withheld lexicon and the withheld statement mode it has no
pattern set and refuses every item, and everything the network scores there is
score the trivial program cannot get.

## 7. Exact match against parameters

Greedy, 2,800 items per split, 200 per shape, from
`results/norm/eval/<size>/summary.json`. Never pooled.

### Training frames

| shape | s (1.73M) | m (8.05M) | modal_shape floor | parser |
|---|---|---|---|---|
| `exclusion` | 1.000 | 1.000 | 0.140 | 1.000 |
| `inverse` | 1.000 | 1.000 | 0.150 | 1.000 |
| `iterate` | 1.000 | 1.000 | 0.030 | 1.000 |
| `lookup` | 1.000 | 1.000 | 0.125 | 1.000 |
| `lookup_general` | 1.000 | 1.000 | 0.570 | 1.000 |
| `pair` | 1.000 | 1.000 | 0.140 | 1.000 |
| `precedence` | 1.000 | 1.000 | 0.160 | 1.000 |
| `priority` | 1.000 | 1.000 | 0.070 | 1.000 |
| `band_then_lookup` | 0.860 | 1.000 | 0.010 | 1.000 |
| `classify` | 0.775 | 0.980 | 0.010 | 1.000 |
| `lookup_then_band` | 0.540 | 0.910 | 0.005 | 1.000 |
| `apply_n` | 0.470 | 0.900 | 0.005 | 1.000 |
| `compose` | 0.430 | 0.535 | 0.035 | 1.000 |
| `sum_chain` | 0.115 | 0.380 | 0.005 | 1.000 |

### Held-out question band

| shape | s | m |
|---|---|---|
| the eight shapes at 1.000 above | 1.000 | 1.000, except `iterate` 0.995 |
| `band_then_lookup` | 0.805 | 0.995 |
| `classify` | 0.715 | 0.975 |
| `lookup_then_band` | 0.470 | 0.910 |
| `apply_n` | 0.480 | 0.870 |
| `compose` | 0.360 | 0.500 |
| `sum_chain` | 0.100 | 0.300 |

The parser searched over the training frames is at 0.9143 pooled on this split
with 0.0857 refused, so on the eight ceiling shapes the network matches it and
on the other six it does not.

### Held-out lexicon and held-out statement mode

The parser search refuses every item on both, so every number here is above the
trivial program by construction.

| shape | lexicon s | lexicon m | mode s | mode m |
|---|---|---|---|---|
| `lookup_general` | 1.000 | 1.000 | 1.000 | 1.000 |
| `pair` | 0.895 | 0.805 | 1.000 | 0.990 |
| `classify` | 0.465 | 0.900 | 0.740 | 0.885 |
| `precedence` | 0.205 | 0.895 | 0.535 | 0.535 |
| `inverse` | 0.595 | 0.820 | 0.535 | 0.535 |
| `priority` | 0.405 | 0.800 | 0.520 | 0.535 |
| `iterate` | 0.525 | 0.795 | 0.515 | 0.520 |
| `exclusion` | 0.490 | 0.740 | 0.215 | 0.180 |
| `lookup` | 0.605 | 0.710 | 0.530 | 0.535 |
| `band_then_lookup` | 0.560 | 0.705 | 0.740 | 0.785 |
| `apply_n` | 0.110 | 0.685 | 0.185 | 0.640 |
| `lookup_then_band` | 0.000 | 0.420 | 0.320 | 0.525 |
| `compose` | 0.185 | 0.280 | 0.130 | 0.155 |
| `sum_chain` | 0.000 | 0.055 | 0.025 | 0.115 |

On the withheld statement mode, six shapes do not move between 1.73M and 8.05M
parameters at all: `inverse` 0.535 both, `precedence` 0.535 both, `lookup`
0.530 to 0.535, `priority` 0.520 to 0.535, `iterate` 0.515 to 0.520,
`exclusion` 0.215 down to 0.180. Whatever bounds those numbers is not capacity.
The frame axis breakdown says what it is: on that split `key_first` scores
0.678 and `value_first` 0.294 at 1.73M. An unseen sentence shape read from the
wrong end is not read at all, and more parameters do not buy the reading.

### Greedy against sampled

Sampled decoding at temperature 1.0 is below greedy on every split and every
size, by 0.008 to 0.029 pooled. Greedy has produced false zeros elsewhere on
this project and does not here. Both are in every `summary.json`.

## 8. Safe failure against dangerous failure

Pooled counts, greedy, n=2,800, marked as pooled and not used as a headline.

| size | split | exact | malformed | refused | wrong (executes) | dangerous : safe |
|---|---|---|---|---|---|---|
| s | `train_frames_eval` | 0.7993 | 0.0004 | 0.0000 | 0.2004 | 501 : 1 |
| s | `qframe` | 0.7807 | 0.0011 | 0.0000 | 0.2182 | 198 : 1 |
| s | `lexicon` | 0.4314 | 0.0850 | 0.0379 | 0.4457 | 3.6 : 1 |
| s | `mode` | 0.4993 | 0.0043 | 0.0432 | 0.4532 | 9.5 : 1 |
| m | `train_frames_eval` | 0.9075 | 0.0000 | 0.0000 | 0.0925 | all dangerous |
| m | `qframe` | 0.8961 | 0.0000 | 0.0000 | 0.1039 | all dangerous |
| m | `lexicon` | 0.6864 | 0.0811 | 0.0014 | 0.2311 | 2.8 : 1 |
| m | `mode` | 0.5668 | 0.0086 | 0.0575 | 0.3671 | 5.6 : 1 |

This is the worst property of the design as it stands. On the frames it was
trained on, the 8.05M normalizer never once emitted something the interpreter
would decline. Every failure was a structure that runs and returns an answer
nobody downstream can tell is wrong. The safe failure rate rises only as the
text gets stranger, which is backwards: the network is most silent about its
errors exactly where it is most likely to be right.

The interpreter's refusal is doing real work on the strange splits, where it
catches 4.3% of `mode` items at 1.73M and 5.8% at 8.05M, but it is not a safety
net on the ordinary case.

## 9. What the failures are

`src/norm/ndiff.py` sorts every non-exact emission into four buckets, at
`results/norm/ndiff/<size>.json`.

`order_only` is 0.0000 on every shape, every split and both sizes. Nothing is
lost to a definition or a row written in a different order, so the exact match
number is not deflated by serialisation.

Mean over the fourteen shapes on training frames at 8.05M: `exact` 0.9075,
`order_only` 0.0000, `same_answer` 0.0275, `shape_slip` 0.0007, `value_slip`
0.0643. The plan is almost never wrong. `shape_slip`, where the emitted plan's
operation sequence differs from the gold plan's, is 7 items in 10,000. What
goes wrong is the contents.

Two failures read in full, from `results/norm/ndiff/s.json`:

A `lookup_then_band` item. The plan is right, the bands are right, the six
weight rows are right except one: the page says 2 and the network wrote 29. The
question does not touch that row, so the answer is correct and the structure is
wrong. That is the whole of `same_answer` 0.46 on this shape at 1.73M.

A `sum_chain` item. Eleven plan steps, all eleven correct, including the
alternating `weigh` / `lookup` / `add` chain. Then one weight written 32 where
the page says 23, and two of the four tables with their key to value pairings
scrambled. `sum_chain` pages carry eight definitions and are the longest in the
corpus.

The failure mode is copying, not parsing. That is the opposite of the failure
mode this project measured in the 350M language model, which followed its
training identity on 678 of 678 transposed pages. This network reads the page
and mis-transcribes it. Which suggests the remedy is a pointer or copy
mechanism over the input rather than more parameters, and the size sweep
supports that: `sum_chain` goes 0.115 to 0.380 for 4.7x the parameters.

## 10. Attacks on the number

`src/norm/nattack.py`, `qframe` split, 1,400 items, greedy, at
`results/norm/nattack/ckpt_<size>.pt.json`. Each attack edits the text and the
reference parser is the oracle for what the edited text now says. Items the
oracle refuses are counted and dropped rather than guessed at.

| attack | what it does | s | m |
|---|---|---|---|
| `value` | replace one invented word in one stated line with a word used nowhere. 880 of 1,213 edits change the structure | changed 819/880, followed the edit exactly 427/880, `silently_original` 4/880 | changed 732/880, followed the edit exactly 476/880, `silently_original` 10/880 |
| `delete` | remove one stated line. 1,083 edits change the structure | malformed 526, `silently_original` 74/1,083 | malformed 550, `silently_original` 104/1,083 |
| `truncate` | cut the question off, so there is nothing to read | answered anyway 1,233/1,400 | answered anyway 1,255/1,400 |
| `strip` | remove every stated line, keep the heads and padding | answered anyway 402/1,400 | answered anyway 394/1,400 |

`silently_original` is the number that would kill the design: the page no
longer says the original structure and the network emitted it anyway. It is 4
in 880 at 1.73M and 10 in 880 at 8.05M. The network is reading.

`truncate` is the failure. With the question removed there is no structure to
emit and the only right answer is silence, and the network writes a structure
anyway on 88% of items at 1.73M and 90% at 8.05M. It has never been shown a
page it should refuse, so it has no way to refuse one. That is a training data
gap, not a capacity one, and it is the same finding as section 8 from a
different direction.

## 11. What this says about the thesis

The good part. A 1.73M parameter network with no pretraining and no world
knowledge is exact on eight of the fourteen structure shapes, on frames it was
trained on and on the corpus's own held-out question band, and 8.05M puts a
ninth at 1.000 and two more above 0.90. The perception job really is small: a
network 43 times smaller than the 350M checkpoint this project trained reads
nine of the fourteen shapes without an error in 200 items.

The problem. On the frames the hand written parser was written for, the parser
is at 1.0000 and no normalizer size tried gets there. The honest statement is
the one the brief demanded: this system does not beat the hand written parser
on the frames the parser covers. What it buys is the two splits where the
parser search refuses every single item, and there the best size is at 0.6864
and 0.5668 pooled, which is real and is not close to exact.

The cost. Every failure on the ordinary case is a structure that executes.
A design whose selling point is that the core is exact has put the whole of its
error budget in the one place the core cannot check.

