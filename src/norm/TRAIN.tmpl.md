# The normalizer

One network with one job: turn surface text into a typed structure of
`src/norm/lang.py`. It never executes anything, never sees a gold answer and is
never told what a page means. Everything the structure is later used for
happens in `src/norm/interp.py`, which is a program.

The claim under test is that this job needs no world knowledge and should
therefore be far smaller than a language model. That is measured here across
four sizes rather than asserted, and the answer is mixed. A 404,608 parameter
network with 232,192 parameters outside its embedding tables is exact on seven
of the fourteen structure shapes on the training frames and above 0.91 on five
more, in 200 items per shape. Five shapes are never read exactly by any size
tried. The hand written parser reads all fourteen exactly, so the network does
not beat the trivial program on the frames that program covers.

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

On the input side, English words, single digits and single punctuation marks.
The English word list is the union of every frame's own reserved set, 272
distinct words, which with their capitalised and upper case forms, the digits,
the punctuation and the 64 copy slots make an input vocabulary of 923. An
invented word is alphabetic and outside that list, by construction of
`Lexicon`, so the two are disjoint. Invented words are bound to numbered copy
slots `W0..W63` in order of first appearance and their surface strings travel
beside the ids. The network never sees a nonce spelling and never spells one
back.

Those 272 words are the whole of the English the network is ever shown, and
they are function words and the grammar's own verbs. Every noun on a page is
invented and arrives as a slot id. This is the concrete sense in which the job
needs no world knowledge: there is no world in the input.

On the output side, a closed vocabulary of 155 tokens. Definition kinds, field
markers, the thirteen plan operations, canonical temporary names, the 64 slots,
the digits. An integer is written `#` then its digits, so a number the page
states is copied digit by digit.

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
| `m` | 256 | 8 | 4 / 4 | 1024 | 6.0e-4 | 8,051,200 | 7,361,536 |
| `l` | 512 | 8 | 6 / 6 | 2048 | 4.0e-4 | 45,483,008 | 44,103,680 |

No learning rate search was run. The rates are one guess per size and section 7
shows what that cost: `s` reached a higher training loss than `xs` at every
step past 2,000 with four times the parameters, and two probes at the same size
did not recover it. The curve below therefore mixes capacity with optimisation,
and says so where the two cannot be separated.

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

Every split is scored on 2,800 items, 200 per shape. A per shape
rate near 0.9 carries a standard error of 0.021 and one near 0.5 carries 0.035,
so two shape rows differing by less than about 0.06 are not distinguishable
here. The pooled row, which is never a headline, carries 0.006 near 0.9.

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

SPLIT_TABLES

On the withheld statement mode a group of shapes sits at 0.535 and stays there
at every size: `inverse` 0.535 at 1.73M and 0.535 at 8.05M, `precedence` 0.535
and 0.535, `lookup` 0.530 and 0.535, `priority` 0.520 and 0.535, `iterate`
0.515 and 0.520. Twenty times the parameters moves those five shapes by at most
0.015. Whatever bounds them is not capacity.

The frame axis breakdown in each `summary.json` says what it is. Split by where
the key sits in the sentence:

| size | `mode`, key first | `mode`, value first | `lexicon`, key first | `lexicon`, value first |
|---|---|---|---|---|
| xs 0.40M | 0.6075 | 0.2304 | 0.5476 | 0.4789 |
| s 1.73M | 0.6776 | 0.2942 | 0.5551 | 0.2947 |
| m 8.05M | 0.7497 | 0.3564 | 0.7122 | 0.6579 |

n is 1,498 and 1,302 on `mode`, 1,470 and 1,330 on `lexicon`.

An unseen sentence shape read from the wrong end is barely read at all, and the
gap is 0.38, 0.38 and 0.39 at the three sizes: parameters move both halves and
close nothing between them. On the withheld lexicon the same gap does close,
from 0.26 at 1.73M to 0.05 at 8.05M. So the two withheld groups fail for
different reasons. A new lexicon is a capacity problem and the network is
solving it. A new statement mode with the key in the unfamiliar position is
not, and no size on record touches it.

### The 1.73M point is an anomaly and it is not the learning rate

`xs` at 0.40M parameters reaches a lower training loss than `s` at 1.73M at
every step past 2,000, and scores higher on the training frames. A four times
larger model losing to a smaller one ought to be a bug in the run rather than a
fact about the task, so it was attacked two ways.

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
the wrong checkpoint for one of the four splits, and the training logs say so.
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

### Exact match against examples

The second axis the thesis cares about is examples, not parameters. Four runs
at the `s` size and the same rate differ only in how many distinct training
pairs they draw from, with the step count fixed at 30,000 so the compute is
equal and only the number of times each example is revisited changes.

| unique examples | batches | epochs over 30,000 steps |
|---|---|---|
| 30,000 | 190 | 158 |
| 120,000 | 750 | 40 |
| 480,000 | 2,991 | 10 |
| 1,200,000 | 7,461 | 4 |

LADDER_TABLE

Forty times the examples buys 0.099 on the training frames, from 0.7004 to
0.7993, and it does not buy it monotonically: the 480,000 rung sits below the
120,000 one on every column. That rung tracked above the 1,200,000 one in
training loss at every step, which is the same `s` instability as the previous
subsection showing up on a second axis. Between the rungs the run to run spread
is comparable to the effect being measured, so the training frame column of
this ladder resolves the direction and not much else.

The withheld lexicon column does not have that problem, because the effect
there is far larger than the spread and it points the wrong way. Reading a
lexicon the network has never seen is best at 120,000 examples, 0.6743, and
falls to 0.4314 at 1,200,000. Ten times the data costs 0.243 on the one split
that asks whether the network learned to read rather than to recognise. The
30,000 rung, which revisits each of its pairs 158 times and memorises them,
still reads the unseen lexicon better than the 1,200,000 rung does.

Both halves of that are the same fact from section 7: more optimisation against
the seven training lexicons is paid for out of the eighth, and it does not
matter whether the extra optimisation arrives as more steps on the same pairs
or as more pairs. A normalizer meant to read arbitrary wording should not be
trained to convergence on a fixed wording, and this lane trained every model
that way on purpose so that one recipe produced every row.

## 8. Safe failure against dangerous failure

Pooled counts, greedy, n=2,800, marked as pooled and not used as a headline.

SAFETY_TABLE

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
it. What that points at is a pointer or copy mechanism over the input, rather
than more parameters, and the size sweep is consistent with it:
`sum_chain` moves 0.115 to 0.380 for 4.7x the parameters, which is progress and
is nowhere near enough.

## 10. Attacks on the number

`src/norm/nattack.py`, `qframe` split, 1,400 items, greedy, at
`results/norm/nattack/ckpt_<size>.pt.json`. Four edits: `value` replaces one
invented word in one stated line with a word used nowhere, `delete` removes one
stated line, `truncate` cuts the question off, `strip` removes every stated
line and keeps the heads and the padding. The reference parser is the oracle
for what the edited text now says, and items it refuses are counted and dropped
rather than guessed at.

ATTACK_TABLES

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

Four things follow from the measurements rather than from taste. The network
answers a page with no question on it 88% to 90% of the time, and it has never
been shown a page it should refuse, so the training set needs unreadable pages
with refusal as the target. `shape_slip` is 7 in 10,000 and `value_slip` is
0.064, so what fails is the copy and not the parse, which is an argument for a
pointer over the input rather than for more layers. The `mode` ceiling does not
move across a twenty times parameter range and splits 0.75 against 0.36 on
where the key sits, so it wants either that sentence shape in training or an
inductive bias that does not care about word order. And the withheld lexicon
peaks mid run and falls, so a checkpoint chosen on a held-out lexicon would
report 0.06 to 0.17 more than any number here.

One thing this lane did not measure. The project's second metric is examples
per acquired operation, and the version of it that belongs to the normalizer is
examples per acquired frame: show a trained checkpoint N sentences in the
withheld statement mode and read off the N at which it reads that mode. The
`mode` split is the item set for it and the ceiling at 0.535 is the number to
beat. Nothing here fine tunes a checkpoint, so that number does not exist yet.

## 12. How to run it

All of this runs on the g6e box at `~/decoupled-reasoner`, under
`.venv/bin/python`.

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
    python scripts/norm_partition_check.py
    python -m unittest discover -s src/norm/tests -t .

Every table in this file comes out of `scripts/norm_md.py xs s m l`,
`scripts/norm_safety.py xs s m l` and `scripts/norm_attacks.py xs s m l`, so
none of them was typed by hand. `scripts/norm_sweep.sh` is the size sweep,
`scripts/norm_examples.sh` the examples ladder, `scripts/norm_after.sh` and
`scripts/norm_l_after.sh` the watchers that evaluate each checkpoint as its run
lands. Data generation is CPU and takes about four minutes; a training run is
one GPU and 15 to 90 minutes at 30,000 steps depending on size and on what else
is sharing the card.

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
