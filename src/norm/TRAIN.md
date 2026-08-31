# The normalizer

One network with one job: turn surface text into a typed structure of
`src/norm/lang.py`. It never executes anything, never sees a gold answer and is
never told what a page means. Everything the structure is later used for
happens in `src/norm/interp.py`, which is a program.

The claim under test is that this job needs no world knowledge and should
therefore be far smaller than a language model. That is measured here across
four sizes rather than asserted, and the answer is mixed. A 1.73M parameter
network is already exact on eight of the fourteen structure shapes. On the
shapes it is not exact on, no size tried reaches the hand written parser, which
is at 1.000 on all fourteen.

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

On the input side, English words, single digits and single punctuation marks. The English
word list is the union of every frame's own reserved set, 923 tokens with the
slots. An invented word is alphabetic and outside that list, by construction of
`Lexicon`, so the two are disjoint. Invented words are bound to numbered copy
slots `W0..W63` in order of first appearance and their surface strings travel
beside the ids. The network never sees a nonce spelling and never spells one
back.

On the output side, a closed vocabulary of 155 tokens. Definition kinds, field markers, the
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

| size | d_model | heads | enc/dec layers | d_ff | lr | total params | non-embedding |
|---|---|---|---|---|---|---|---|
| `xs` | 64 | 2 | 2 / 2 | 256 | 1.5e-3 | 404,608 | 232,192 |
| `s` | 128 | 4 | 3 / 3 | 512 | 1.0e-3 | 1,729,280 | 1,384,448 |
| `s15` | 128 | 4 | 3 / 3 | 512 | 1.5e-3 | 1,729,280 | 1,384,448 |
| `m` | 256 | 8 | 4 / 4 | 1024 | 6.0e-4 | 8,051,200 | 7,361,536 |
| `l` | 512 | 8 | 6 / 6 | 2048 | 4.0e-4 | 45,483,008 | 44,103,680 |

No learning rate search was run. The rates above are one guess per size, and
section 7 shows what that cost: `s` at 1.0e-3 reached a higher training loss
than `xs` at 1.5e-3 at every step past 3,000, with four times the parameters,
so `s15` repeats `s` at the smaller model's rate. The curve below therefore
mixes capacity with optimisation, and says so wherever the two are hard to
separate.

The language model this project trained, `~/retrain/corpus-v1-8k.pt`, holds
375,440,384 parameters, 341,885,952 of them outside the embedding tables. That
is 46.6x the `m` normalizer and 8.3x the `l` one. It is not doing the same job:
it reads, reasons and answers, where the normalizer only reads and
`src/norm/interp.py` does the rest. The comparison is between whole systems,
and the normalizer's half of one is the part measured here.

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

There is no finite option count for a structure, so the floor is the best
constant guess: `modal` is the most frequent training target emitted for
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
near ceiling.

The `qframe` band is the weakest of the four withheld groups and its 0.9143
says why. `src/norm/nband.py` asks which training frame reads each held-out
item and how far that frame is from the item's own, at
`results/norm/nsearch/band.json`:

| split | read by a training frame one axis away | refused by all 490 |
|---|---|---|
| `qframe` | 128 of 140, differing on `scope_pos` alone | 12 |
| `lexicon` | 0 | 140 |
| `mode` | 0 | 140 |
| `mixed` | 0 | 140 |

The band is `wh` question form with the scope first, and `wh` with the scope
last is in training, so the combination is new and each half of it is not. A
number on `qframe` is a small generalisation step and should be read as one.
The other three splits are the real thing: no training frame reads a single
item of them, so every point the network scores there is a point the trivial
program cannot reach.

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

### The 1.73M point is an anomaly and it is not the learning rate

`xs` at 0.40M parameters reaches a lower training loss than `s` at 1.73M at
every step past 2,000, and scores higher on the training frames. A four times
larger model losing to a smaller one is a bug in the run, not a fact about the
task, so it was attacked two ways before anything below was written.

Training loss at three common steps, from `results/norm/train/log_<tag>.jsonl`:

| run | size | lr | seed | step 2,400 | step 9,600 | step 30,000 |
|---|---|---|---|---|---|---|
| `xs` | 0.40M | 1.5e-3 | 1 | 0.1872 | 0.0751 | 0.0181 |
| `s` | 1.73M | 1.0e-3 | 1 | 0.2215 | 0.1081 | 0.0371 |
| `s15` | 1.73M | 1.5e-3 | 1 | 0.2504 | 0.1936 | stopped at 9,600 |
| `s_seed2` | 1.73M | 1.0e-3 | 2 | 0.2118 | stopped at 2,400 | |
| `m` | 8.05M | 6.0e-4 | 1 | 0.1986 | 0.0742 | 0.0155 |

Raising the rate to the one `xs` uses makes it worse, not better: `s15` is
above `s` at every step and was 0.1936 against 0.1081 when it was stopped at
9,600. Changing the seed changes almost nothing: `s_seed2` was 0.2118 against
0.2215 at 2,400, inside the run to run spread, and was stopped there. Two rates
and two seeds all land the 1.73M configuration below the 0.40M one, and the
budget did not stretch to a proper rate search.

So the 1.73M row of every table below is reported as measured and is an
anomaly nobody has explained. The two probes are on record with their step
counts and neither reached 30,000. Read the curve as `xs`, `m`, `l`, with `s`
sitting under all of them for a reason this lane did not find.

### Greedy against sampled

Sampled decoding at temperature 1.0 is below greedy on every split and every
size, by 0.008 to 0.029 pooled. Greedy has produced false zeros elsewhere on
this project and does not here. Both are in every `summary.json`.

### The held-out lexicon gets worse as training goes on

Every number in this file is from the final checkpoint at step 30,000. That is
the wrong checkpoint for two of the four splits, and the training logs say so.
The in-training evaluation runs every 3,000 steps on 700 items per split,
greedy, not broken out by shape, from `results/norm/train/log_<tag>.jsonl`:

| step | s train | s lexicon | m train | m lexicon |
|---|---|---|---|---|
| 9,000 | 0.6014 | 0.5386 | 0.6700 | 0.6371 |
| 12,000 | 0.6814 | 0.6200 | 0.7314 | 0.6329 |
| 15,000 | 0.7029 | 0.6143 | 0.7714 | 0.6929 |
| 18,000 | 0.7400 | 0.5957 | 0.8243 | 0.6900 |
| 21,000 | 0.7614 | 0.5171 | 0.8557 | 0.7529 |
| 24,000 | 0.7829 | 0.4757 | 0.8800 | 0.7357 |
| 27,000 | 0.8114 | 0.4743 | 0.8829 | 0.7086 |
| 30,000 | 0.8071 | 0.4543 | 0.9071 | 0.6900 |

At 1.73M the withheld lexicon peaks at 0.6200 on step 12,000 and falls to
0.4543 by step 30,000, losing 0.166 while the training frames gain 0.126. At
8.05M it peaks at 0.7529 on step 21,000 and falls to 0.6900. The network is not
running out of capacity on the new lexicon, it is being trained off it: more
optimisation against the seven training lexicons is bought with the eighth.

The withheld statement mode does not do this. It rises to 0.5229 and 0.5871 and
stays. Whatever the `relative_clause` frames need is not something the network
loses by training longer, and section 7 says what it is instead.

Nothing here is early stopped, on purpose, so that one recipe produced every
row. The consequence is that every `lexicon` number in this file understates
what the same network reaches mid-run by 0.06 to 0.17 on a 700 item eval.

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
text gets stranger, so on the frames it knows best the network has no way at
all to signal that it has misread one.

The interpreter's refusal is doing real work on the strange splits, where it
catches 4.3% of `mode` items at 1.73M and 5.8% at 8.05M. Its complaints are
specific, one per item: a table with no entry for the key and no default, a
`band` step naming bands the page does not define, a key several steps from any
row. That is the exactness of the core showing up as a caught error. It is not
a safety net on the ordinary case, where there is nothing to catch because the
emitted structure is always well typed.

## 9. What the failures are

`src/norm/ndiff.py` sorts every non-exact emission into four buckets, at
`results/norm/ndiff/<size>.json`.

`order_only` is 0.0000 on every shape, every split and every size. Nothing is
lost to a definition or a row written in a different order, so the exact match
number is not deflated by serialisation. That zero has a positive control:
`src/norm/tests/test_ndiff.py` hands the comparator a permuted table, a
permuted weights list and permuted definitions and requires all three to come
back as `order_only`, and hands it an ordered table and a changed value and
requires them not to. The comparator can see a reordering; there are none to
see.

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

The failure mode is copying, not parsing. It is the opposite of what this
project measured in the language model, which followed its training identity on
678 of 678 transposed pages. This network reads the page and mis-transcribes
it. What that points at is a pointer or copy mechanism over the input rather than
more parameters, and the size sweep is consistent with it:
`sum_chain` moves 0.115 to 0.380 for 4.7x the parameters, which is progress and
is nowhere near enough.

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

What holds up is the size claim. A 1.73M parameter network with no pretraining
and no world knowledge is exact on eight of the fourteen structure shapes, both
on frames it was trained on and on the corpus's held-out question band, and
8.05M puts a ninth at 1.000 and three more above 0.87. The perception job
really is small: a network 47 times smaller than the checkpoint this project
trained reads nine of the fourteen shapes without an error in 200 items each.

What does not hold up is the comparison with the trivial program taken whole.
The parser is at 1.000 on all fourteen shapes of every split, and the best
normalizer matches it on nine. On `classify`, `lookup_then_band` and `apply_n`
it is within 0.10 of the parser and does not reach it. On `compose` 0.535 and
`sum_chain` 0.380 it is nowhere near. The honest statement is the one the brief
demanded: this system does not beat the hand written parser on the frames the
parser covers.

What the network buys is the two splits where the parser search refuses every
single item. There the best size on record reaches 0.6864 pooled on the
withheld lexicon and 0.5668 on the withheld statement mode, which is real,
which the trivial program cannot get at all, and which is not exact.

The cost of the design as built is that every failure on the ordinary case is a
structure that executes. A system whose argument is that its core is exact has
put the whole of its error budget in the one place that core cannot check.

## 12. How to run it

All of this is on the g6e box at `~/decoupled-reasoner`, with `.venv/bin/python`.

    python -m src.norm.ndata     --out data/norm --train 1200000 --eval 7000
    python -m src.norm.ntrain    --size s --steps 30000 --eval-every 3000 \
                                 --eval-n 700 --out results/norm/train --tag s
    python -m src.norm.nreport   --ckpt results/norm/train/ckpt_s.pt --n 2800 \
                                 --out results/norm/eval
    python -m src.norm.ndiff     --ckpt results/norm/train/ckpt_s.pt --n 2800
    python -m src.norm.nattack   --ckpt results/norm/train/ckpt_s.pt \
                                 --split qframe --n 1400
    python -m src.norm.nsearch   --n 280 --out results/norm/nsearch/summary.json
    python -m src.norm.nband     --n 140
    python -m src.norm.ncheck    --n 2800
    python scripts/norm_md.py xs s m l
    python scripts/norm_partition_check.py
    python -m unittest discover -s src/norm/tests -t .

`scripts/norm_sweep.sh` is the size sweep, `scripts/norm_examples.sh` the
examples ladder, `scripts/norm_after.sh` the watcher that evaluates each
checkpoint as its run lands. Data generation is CPU and takes about four
minutes; each training run is one GPU and 15 to 60 minutes at 30,000 steps.

No checkpoint of the 375M language model is loaded anywhere in this lane, so
the world header harness gate does not apply to any number above.

## 13. Every artifact

| what | path |
|---|---|
| frame split and data manifest | `data/norm/manifest.json` |
| training logs, one per run | `results/norm/train/log_<tag>.jsonl` |
| checkpoints | `results/norm/train/ckpt_<tag>.pt` |
| per split, per shape, per mode scores | `results/norm/eval/<tag>/summary.json` |
| per item records behind those scores | `results/norm/eval/<tag>/records_<split>_<mode>.jsonl.gz` |
| failure buckets and worked examples | `results/norm/ndiff/<tag>.json` |
| page edit attacks | `results/norm/nattack/ckpt_<tag>.pt.json` |
| the parser searched over training frames | `results/norm/nsearch/summary.json` |
| how far each withheld frame is from a training frame | `results/norm/nsearch/band.json` |
| the scoring seam gate | `results/norm/ncheck.json` |

Checkpoints are `*.pt` and the repository ignores them, so they live on the box
and nowhere else. Everything else in that table is committed.

Every `summary.json` was written by the same process that wrote the records
beside it, and every checkpoint predates its own report. Three gates stand
behind the numbers: `src/norm/ncheck.py` that the training target and the
scoring gold are the same object, `scripts/norm_partition_check.py` that the
four outcomes partition every scored row and the gold executes on every item,
and `src/norm/tests/test_ndiff.py` that the failure comparator can see a
reordering when there is one.
