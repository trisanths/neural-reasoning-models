# What the 0.65 between the parser and the 167M reader is made of

On the eight structure shapes the key-position axis reaches, `xxl167`
(167,376,384 parameters, 110,271 steps) reads 0.3938 exact key-first on 2,016
items and 0.3392 value-first on 1,984. The hand-written parser of
`src/norm/parse.py` reads 2,016 of 2,016 and 1,984 of 1,984 on the same items.
The gap is 0.6062 key-first and 0.6608 value-first. This is what is inside it.

The eight shapes are the `new keys` group of `src/role/rshapes.py`: `lookup`,
`inverse`, `iterate`, `compose`, `exclusion`, `sum_chain`, `precedence`,
`priority`. Their rule lines state a key that appears nowhere else on the page,
so the wording of the line is the only channel carrying which word is the key.
On the other six shapes the two renderings are byte identical and the axis
cannot show anything either way. Nothing below is pooled across key position or
across shape.

The parser is a generous baseline and not a like-for-like one. It is handed the
frame id and the reader is not, which `src/norm/neval.py` states where the
baseline is defined. The floor at the other end is the modal-by-shape
baseline, a reader told the shape and then guessing its canonical filling:
0.0942 key-first and 0.0706 value-first over the eight shapes, and 0.0000 for a
single modal target over the whole split.

## The committed records cannot make this classification, and what they can do

`results/system/eval/xxl167/records_mode_greedy.jsonl.gz` carries ten fields per
item: `fid`, `shape`, `tag`, `exact`, `malformed`, `refused`, `wrong`,
`answer`, `gold_answer`, `reason`. It does not carry the structure the reader
emitted.

Four of the six categories the decision needs cannot be recovered from that.
`malformed` and `refused` are there directly. `exact` is there. But `wrong`
is a single flag covering wrong kind, wrong binding and wrong content
together, and separating them requires the emitted structure. The records can
also answer one question that is worth having on its own, because `answer` and
`gold_answer` are both present: how often a wrong structure executes to the
right answer.

So the structures were emitted again, from the same checkpoint through the same
`src/norm/neval.emit` at the same decode settings, by `src/norm/gap.py`. The
pass is gated on reproducing the committed record file item by item on `exact`,
`malformed`, `refused`, `wrong` and `answer` before any count is taken off it.
The gate reads 7,000 of 7,000 agree for `xxl167` greedy and 7,000 of 7,000 for
`xxl167` sampled, and the same for `l45` and `xl93`. The recovered exact rates
reproduce `src/system/THRESHOLD.md` to the digit, 794 of 2,016 and 673 of 1,984.

The last of the six categories is empty by construction and is counted anyway.
A structure equal to gold executes under the same interpreter to gold's own
answer, so `right structure, wrong answer downstream` cannot occur: 0 of 2,016
and 0 of 1,984, interval [0.0000, 0.0019] on each.

## The six outcomes, greedy, never pooled

Shares of all items in the cell. The failure column beside each is the same
count over that cell's failures rather than over its items, since the question
is what the gap is made of.

Key-first, n=2,016, exact 794 = 0.3938 [0.3727, 0.4154], 1,222 failures.

| outcome | items | share of items | 95% CI | share of the 1,222 failures |
| --- | ---: | ---: | --- | ---: |
| malformed | 11 | 0.0055 | [0.0030, 0.0097] | 0.0090 |
| refused | 114 | 0.0565 | [0.0473, 0.0675] | 0.0933 |
| wrong kind | 128 | 0.0635 | [0.0537, 0.0750] | 0.1047 |
| wrong binding | 587 | 0.2912 | [0.2718, 0.3114] | 0.4804 |
| wrong content | 382 | 0.1895 | [0.1730, 0.2072] | 0.3126 |
| downstream | 0 | 0.0000 | [0.0000, 0.0019] | 0.0000 |

Value-first, n=1,984, exact 673 = 0.3392 [0.3187, 0.3603], 1,311 failures.

| outcome | items | share of items | 95% CI | share of the 1,311 failures |
| --- | ---: | ---: | --- | ---: |
| malformed | 4 | 0.0020 | [0.0008, 0.0052] | 0.0031 |
| refused | 144 | 0.0726 | [0.0620, 0.0848] | 0.1098 |
| wrong kind | 174 | 0.0877 | [0.0760, 0.1010] | 0.1327 |
| wrong binding | 608 | 0.3065 | [0.2866, 0.3271] | 0.4638 |
| wrong content | 381 | 0.1920 | [0.1753, 0.2100] | 0.2906 |
| downstream | 0 | 0.0000 | [0.0000, 0.0019] | 0.0000 |

Sampled decoding reproduces this. Key-first 0.3943 exact with binding at
0.2847, value-first 0.3397 with binding at 0.2969, every other cell within
0.003 of its greedy value. The decomposition is not a greedy artifact.

The definitions are in `src/norm/gapclass.py` and matter for reading the table.
`wrong kind` means the definition kinds, their key arities or the plan's
operations are not gold's. `wrong binding` means those all match and the
emitted structure holds exactly gold's own symbols in a different arrangement,
tested as a multiset over every scalar in the structure. That test is coarser
than a field-by-field comparison on purpose: a table read backwards carries its
default and its question key backwards too, and a field comparison put those
items in `wrong content`. Under the stricter comparison binding reads 0.2693
and 0.2848 rather than 0.2912 and 0.3065, so the choice of test moves the
number by about two points and does not change which category is largest.

## Per shape

Structure size is the mean over the cell's gold programs and is in the table
because it turns out to sort the failure modes.

### Key-first

| shape | n | defs | steps | entries | exact | malformed | refused | wrong kind | wrong binding | wrong content |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `lookup` | 252 | 1.0 | 1.0 | 4.0 | 0.5238 | 0.0079 | 0.0000 | 0.0000 | 0.4286 | 0.0397 |
| `inverse` | 252 | 1.0 | 1.0 | 4.0 | 0.5794 | 0.0000 | 0.0000 | 0.4206 | 0.0000 | 0.0000 |
| `priority` | 252 | 1.0 | 1.0 | 4.0 | 0.6310 | 0.0357 | 0.0000 | 0.0000 | 0.1746 | 0.1587 |
| `exclusion` | 252 | 1.0 | 1.0 | 4.0 | 0.4841 | 0.0000 | 0.1310 | 0.0000 | 0.3849 | 0.0000 |
| `iterate` | 252 | 1.0 | 4.5 | 6.7 | 0.4286 | 0.0000 | 0.0000 | 0.0000 | 0.5238 | 0.0476 |
| `precedence` | 252 | 2.0 | 1.0 | 8.0 | 0.3929 | 0.0000 | 0.1230 | 0.0000 | 0.3135 | 0.1706 |
| `compose` | 252 | 3.5 | 3.5 | 14.0 | 0.0873 | 0.0000 | 0.1984 | 0.0873 | 0.3770 | 0.2500 |
| `sum_chain` | 252 | 7.0 | 9.6 | 28.2 | 0.0238 | 0.0000 | 0.0000 | 0.0000 | 0.1270 | 0.8492 |
| all eight | 2016 | | | | 0.3938 | 0.0055 | 0.0565 | 0.0635 | 0.2912 | 0.1895 |

### Value-first

| shape | n | defs | steps | entries | exact | malformed | refused | wrong kind | wrong binding | wrong content |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `lookup` | 248 | 1.0 | 1.0 | 4.0 | 0.4113 | 0.0000 | 0.0000 | 0.0000 | 0.5806 | 0.0081 |
| `inverse` | 248 | 1.0 | 1.0 | 4.0 | 0.4113 | 0.0000 | 0.0000 | 0.5887 | 0.0000 | 0.0000 |
| `priority` | 248 | 1.0 | 1.0 | 4.0 | 0.6048 | 0.0000 | 0.0000 | 0.0000 | 0.1613 | 0.2339 |
| `exclusion` | 248 | 1.0 | 1.0 | 4.0 | 0.1734 | 0.0000 | 0.4073 | 0.0000 | 0.4194 | 0.0000 |
| `iterate` | 248 | 1.0 | 4.5 | 6.7 | 0.5000 | 0.0000 | 0.0000 | 0.0000 | 0.4879 | 0.0121 |
| `precedence` | 248 | 2.0 | 1.0 | 8.0 | 0.5242 | 0.0161 | 0.0645 | 0.0121 | 0.2621 | 0.1210 |
| `compose` | 248 | 3.5 | 3.5 | 14.0 | 0.0645 | 0.0000 | 0.0927 | 0.1008 | 0.4234 | 0.3185 |
| `sum_chain` | 248 | 7.0 | 9.6 | 28.2 | 0.0242 | 0.0000 | 0.0161 | 0.0000 | 0.1169 | 0.8427 |
| all eight | 1984 | | | | 0.3392 | 0.0020 | 0.0726 | 0.0877 | 0.3065 | 0.1920 |

## Two things the six-way sort hides, measured across it

The first is the transposition test: is every binding-bearing definition in the
emitted structure gold's with key and value reversed. That is positional
binding in its cleanest form, and it lands in three different outcomes, because
a reader that transposes a table and then writes `invert` where gold writes
`lookup` is scored `wrong kind` while doing the same thing as one that
transposes and writes `lookup`.

The second is whether a wrong structure executes to gold's answer anyway. A
reader scored 0.3938 on structures is not 0.3938 on answers.

### Key-first, over the 1,222 failures

| shape | failures | share of the gap | tables transposed | answer matches gold | mean share of entries wrong | at most two entries wrong |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `lookup` | 120/252 | 0.0982 | 118 = 0.9833 | 25 = 0.2083 | 1.0000 | 0 = 0.0000 |
| `inverse` | 106/252 | 0.0867 | 101 = 0.9528 | 101 = 0.9528 | 0.9528 | 0 = 0.0000 |
| `priority` | 93/252 | 0.0761 | 82 = 0.8817 | 2 = 0.0215 | 0.9705 | 0 = 0.0000 |
| `exclusion` | 130/252 | 0.1064 | 0 = 0.0000 | 0 = 0.0000 | 0.6788 | 47 = 0.3615 |
| `iterate` | 144/252 | 0.1178 | 0 = 0.0000 | 47 = 0.3264 | 0.4432 | 1 = 0.0069 |
| `precedence` | 153/252 | 0.1252 | 1 = 0.0065 | 0 = 0.0000 | 0.6887 | 0 = 0.0000 |
| `compose` | 230/252 | 0.1882 | 22 = 0.0957 | 60 = 0.2609 | 0.7422 | 5 = 0.0217 |
| `sum_chain` | 246/252 | 0.2013 | 0 = 0.0000 | 31 = 0.1260 | 0.6406 | 9 = 0.0366 |
| all eight | 1222/2016 | 1.0000 | 324 = 0.2651 [0.2412, 0.2906] | 266 = 0.2177 | 0.6865 | 62 = 0.0512 |

### Value-first, over the 1,311 failures

| shape | failures | share of the gap | tables transposed | answer matches gold | mean share of entries wrong | at most two entries wrong |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `lookup` | 146/248 | 0.1114 | 146 = 1.0000 | 38 = 0.2603 | 1.0000 | 0 = 0.0000 |
| `inverse` | 146/248 | 0.1114 | 146 = 1.0000 | 146 = 1.0000 | 1.0000 | 0 = 0.0000 |
| `priority` | 98/248 | 0.0748 | 98 = 1.0000 | 0 = 0.0000 | 1.0000 | 0 = 0.0000 |
| `exclusion` | 205/248 | 0.1564 | 0 = 0.0000 | 0 = 0.0000 | 0.6354 | 127 = 0.6195 |
| `iterate` | 124/248 | 0.0946 | 0 = 0.0000 | 46 = 0.3710 | 0.4581 | 0 = 0.0000 |
| `precedence` | 118/248 | 0.0900 | 4 = 0.0339 | 0 = 0.0000 | 0.8289 | 0 = 0.0000 |
| `compose` | 232/248 | 0.1770 | 25 = 0.1078 | 77 = 0.3319 | 0.6930 | 2 = 0.0086 |
| `sum_chain` | 242/248 | 0.1846 | 0 = 0.0000 | 27 = 0.1116 | 0.5925 | 13 = 0.0537 |
| all eight | 1311/1984 | 1.0000 | 419 = 0.3196 [0.2949, 0.3453] | 334 = 0.2548 | 0.6697 | 142 = 0.1086 |

The `wrong kind` column of the six-way table should be read through this. Of
the 128 key-first `wrong kind` failures, 123 are exact table transpositions and
all 123 execute to gold's answer; value-first it is 171 of 174, all of them
answering correctly. `inverse` accounts for most of both. Gold writes
`invert T x` on a table keyed key to value; the reader writes `lookup T' x`
with `T'` the transpose, which is the same function. Under structure exact
match that is the wrong kind of structure, and it is not a comprehension
failure. Scored semantically rather than by exact match the eight-shape figure
would rise by 123 of 2,016 = 0.0610 key-first and 171 of 1,984 = 0.0862
value-first on this account alone.

## Is the gap concentrated or spread

Spread. No shape is above 0.6310 exact on either position, and none is closer
than 0.37 to the parser. The largest single contributor to the key-first gap is
`sum_chain` at 0.2013 of the failures and the smallest is `priority` at 0.0761,
a range of under three to one across eight shapes. Value-first runs 0.1846 to
0.0748.

Fixing the three shapes where the failure is a clean transposition would not
close it. Bringing `lookup`, `inverse` and `priority` to 1.0000 key-first
recovers 319 items and moves the eight-shape figure from 794/2016 = 0.3938 to
1113/2016 = 0.5521, still 0.45 below the parser.

What is concentrated is the failure mode rather than the loss. The eight shapes
split into two regimes and the split follows structure size.

The small shapes, one definition and one step over four entries, fail by
transposing the whole table: `lookup` 0.9833 and 1.0000 of failures, `inverse`
0.9528 and 1.0000, `priority` 0.8817 and 1.0000. On those the mean share of
entries wrong is 0.95 to 1.00, which is what a reversal looks like.

The larger shapes fail by corrupting part of a structure they otherwise have
right. `iterate` transposes on 0 of 144 key-first failures and 0 of 124
value-first ones and gets a mean 0.4432 and 0.4581 of its entries wrong, so a
typical failure misplaces four or five rows of a ten-row cycle and leaves the
rest. `sum_chain`, seven definitions and 28 entries, transposes on 0 of 246 and
0 of 242 and reads 0.0238 and 0.0242 exact against a modal-by-shape floor of
0.0040 and 0.0000. `compose` transposes
on about a tenth of its failures.

`exclusion` is the one shape that fits neither. Four entries, no transpositions
at all, and 0.3615 key-first and 0.6195 value-first of its failures have at
most two entries wrong. Its gold plan is `odd_one_out`, which the interpreter
refuses when the table does not have exactly one key away from the queried
value, so a single misplaced row turns into a refusal rather than a wrong
answer. That is where the 0.1310 and 0.4073 refusal rates come from, and it is
the design failing safe on a precision error rather than a distinct failure of
its own.

## Is the dominant mode one more data would fix

The dominant mode is right kind with wrong binding, at 0.4804 of key-first
failures and 0.4638 of value-first ones, and it is the largest category on both
positions by a factor of about 1.5 over the next one. The two modes that would
argue for more pretraining are the two smallest. Malformed output is 0.0090 and
0.0031 of failures. `wrong kind` is 0.1047 and 0.1327, of which 123 of 128 and 171 of
174 are the `invert` for `lookup` substitution described above, which is a binding
failure wearing a different plan operation and returns the right answer. The
reader is not failing to produce well-formed structures of the right kind. It
is producing them and binding the page's words into them wrongly.

Three further readings point the same way.

The transposition rate does not fall with capacity, it spreads. At 45M the
whole-table transposition appears on 0 of 514 key-first failures and 780 of
1,984 value-first ones, 0.3931. At 93M it is 3 of 607 and 758 of 1,963, 0.3861.
At 167M it is 324 of 1,222 and 419 of 1,311, 0.2651 and 0.3196. The smaller
rungs never transpose a key-first page and always might transpose a value-first
one. The 167M rung transposes both at about the same rate. Scale did not teach
it which word is the key; it stopped it from applying one convention
everywhere, which is what `src/STATE.md` claim R4 reports from the aggregate and
this is the mechanism underneath that.

Answer-level accuracy is far above structure-level accuracy and the difference
is binding failures that happen to come out right. A wrong structure executes to
gold's answer on 266 of 1,222 key-first failures and 334 of 1,311 value-first
ones, so answers land at 1,060 of 2,016 = 0.5258 and 1,007 of 1,984 = 0.5076
where structures land at 0.3938 and 0.3392. Anything scored on answers rather
than on structures will read this failure as smaller than it is.

The same failure has already survived four interventions on the training
signal. `src/STATE.md` claim R5 records minimal pairs, an auxiliary role head,
their combination and a reproduction arm, all at 45M, all of which moved which
convention was chosen and none of which removed the choice. More tokens of the
same distribution are a fifth intervention on the same signal.

So the honest answer to the question the pretrain decision turns on is that the
largest identifiable component of the gap is the one that does not look
data-fixable, and it is a little under half of it. Binding failures are 0.4804
and 0.4638 of failures, and if the transposition-driven `wrong kind` items are
counted with them the figure is about 0.58 and 0.59. The remainder is content
corruption concentrated in the shapes with more definitions, more entries and
longer plans, and that part is the ordinary kind of failure that more capacity
or more data plausibly moves. A 7B-token 350M pretrain would be testing the
smaller half of the gap.

## What would separate the two halves

The measurements this points at, in the order they would settle the question.

An items-per-entry curve on the corrupted half. `sum_chain` and `compose` fail
in proportion to their size, and whether that is data or capacity is answerable
by holding the shape fixed and varying entries per structure. It is a
generator change and needs no new pretrain.

A binding probe that does not go through structure exact match. Every number
above is confounded by the fact that a transposed table plus a compensating
operation scores as a different kind. Scoring the binding directly, per rule
line, would give the positional failure its own rate with its own floor.

If a pretrain is run anyway, the pre-registered prediction is available and
cheap to state: if more tokens fix the binding, `lookup`, `inverse` and
`priority` should move first and their transposition share should collapse; if
they fix capacity instead, `sum_chain` and `compose` move and the transposition
share on the small shapes stays where it is. Writing that down before the run
is what made the two-arm prediction of `src/STATE.md` claim R2 worth anything.

## Artifacts

Everything above is read from these files, and each was written after the
checkpoint it scores and before this document.

| file | what it holds |
| --- | --- |
| `results/system/eval/xxl167/records_mode_greedy.jsonl.gz` | the committed per-item record, 7,000 items, the gate this pass had to reproduce |
| `results/norm/gap/records_xxl167_mode_greedy.jsonl.gz` | the same items with the emitted structure, its category and its evidence |
| `results/norm/gap/records_xxl167_mode_sampled.jsonl.gz` | the same under sampled decoding |
| `results/norm/gap/records_l45_mode_{greedy,sampled}.jsonl.gz` | the 45M rung, for the capacity comparison |
| `results/norm/gap/records_xl93_mode_greedy.jsonl.gz` | the 93M rung |
| `results/norm/gap/xxl167_mode.json` | the per-mode summary and the gate counts |
| `results/norm/gap/class_xxl167_mode_greedy.json` | every count and interval in this document |
| `results/norm/gap/class_{xxl167_mode_sampled,l45_mode_greedy,l45_mode_sampled,xl93_mode_greedy}.json` | the same for the other passes |

The checkpoints are `results/system/train/ckpt_xxl167.pt`,
`results/system/train/ckpt_xl93.pt` and `results/norm/train/ckpt_l.pt`. The
items are `data/norm/mode`, the held-out sentence mode `relative_clause`, all
7,000 of them, of which 4,000 are on the eight shapes.

## How to reproduce

    uv run python -m src.norm.gap --ckpt results/system/train/ckpt_xxl167.pt \
        --tag xxl167 --modes greedy,sampled
    uv run python -m src.norm.gapclass --tag xxl167 --mode greedy

`src/norm/gap.py` prints the gate counts and says so loudly when the
re-emission does not reproduce the committed records. `src/norm/gapclass.py`
recomputes the parser column and the modal-by-shape floor from the same eval
split rather than copying them from another document.
