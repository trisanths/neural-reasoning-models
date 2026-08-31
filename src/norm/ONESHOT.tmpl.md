# Intelligence per example

Built {{BUILT}} from `results/norm/oneshot/report.json`. Every table below is
rendered by `src/norm/opdoc.py` out of the record files named at the end.
Freshness at build time: {{FRESH}}. `opdoc` refuses to build when any record
file is newer than the report, so no table here is a rescore of an older run.

The measurement. A person reads one page and can then use what it says. A
gradient trained model needs many examples, because that is how gradients work.
A library based system should need one, because that is how definitions work.
This lane invents operations the system has never seen, states each one on a
single page of text, and asks both systems to use it.

The answer. One page is enough for the library system and it is enough on the
first page: 1.0000 strict on each of the four operation families, and structure
exact at 1.0000 as well, unchanged when the same operation is stated on two
pages and on four. The network, handed the same page in its context and taking
no gradient step, scores 0.0000 on the two directory one clause family against a
floor of 0.3735, 0.0194 on three directories and one clause against 0.3086,
0.1200 on two directories and two clauses against 0.3567, and 0.0173 on three
directories and two clauses against 0.2879, which is below its own guessing
floor in every one. Across the whole item set it is structure exact
on 0 of 6,736 items under greedy decoding and 0 of 6,736 under sampled.
Given labelled examples of the one operation it will be tested on, and an output
vocabulary extended for free so it can write an operation down at all, it climbs
the ladder below rather than arriving at the first example.

## The operation, and why it is new to everything here

The corpus holds four relation structures out: `two_key`, `exclusion`,
`priority_list` and `agreement`. This lane builds operations of the fourth kind.
An agreement operation reads one item in two or more directories and decides
what to answer from whether those readings agree.

Nothing in this project could state one before. `src/norm/shapes.py` has no
shape for it, `src/norm/render.py` cannot write it, `src/norm/parse.py` cannot
read it, and the normalizer's target vocabulary in `src/norm/ntok.py` has no
token for an operator definition at all. The interpreter could always run one,
because `src/norm/lang.py` has had the `OpDef` kind and `src/norm/interp.py` the
`call` operation since they were written, and that asymmetry is the architecture:
the language is fixed, the library grows.

What a definition page may state is fixed and small. An operation names itself,
says which directories it reads and in what order, and gives an ordered list of
clauses, each a condition on the readings and a result. Conditions are: all the
readings agree, no two agree, these two agree, these two differ. Results are:
the reading from that directory, the reading just found shared, a word the page
states outright. `src/norm/oplang.py:enumerate_space` writes out every operation
statable with one clause over two or three directories. There are 144 of them
once the duplicates between the two enumerations are removed, 42 over two
directories and 102 over three. The measurement runs over the whole set rather
than over a chosen example.

An operation whose answer is always what one directory states is dropped. Such a
page defines a new operator that computes an old one, and acquiring it would
prove nothing. 94 of the 285 drawn skeletons were dropped that way and the count
is in `results/norm/oneshot/items.meta.json`.

## What the reader knows, and what it does not

`src/norm/opread.py` is handed the episode text and the frame id and nothing
else. Not the shape, not the operation, not which pages matter. It knows the
definition grammar: three of the four wording modes, the fixed condition
vocabulary, the fixed result vocabulary. It knows no operation. The operator's
name, its arity, which directories it reads, in what order, which conditions it
tests, in what order, what each clause answers and what it answers when no
clause fires are all read off the page, and no branch below names a particular
operation.

The directories themselves are ordinary corpus pages. They are written by
`src/corpus/frames_default.py` through `Frame.page`, so they are byte identical
to what the corpus writes for a two directory agreement instance, and the
normalizer has read thousands of them, in all 768 frames. Only the definition
page and the question are new.

The definition page has a grammar of its own, in `src/norm/opsay.py`, and it is
smaller than the corpus grammar: four wording modes rather than 768 frames, with
the nouns taken from the frame's own lexicon and the question form following the
frame's question axis. Four modes is the whole of the wording variation a
definition page gets here, and one of the four is never read.

## The acquisition curve

Each row is one operation family, never pooled with another. `L` is the library
system: read the page, put the operation in an episode scoped library, run the
plan, with no gradient step anywhere in that path. `S1` and `S2` are the
shortcut readers that take the first and the last line stating the question's
key, which is the baseline that matters for an agreement page because two
directories both state the key. `parser` is `src/norm/parse.py`, the project's
hand written parser for the fourteen corpus shapes.

{{T_ACQ}}

The same items, answered by the network.

{{T_ACQ_NET}}

The three library columns are the curve. One page, two pages and four pages of
the same operation give the same number, because the second page carries nothing
the first did not and the library says so by construction: a repeat that agrees
changes nothing and a repeat that disagrees is a refusal.

The extra pages are read, not skipped. The library counts what it took off them,
and a four page episode is four definitions read and one operation stored.

{{T_PAGES}}

The same items split by the frame the pages are written in, which is the split
the normalizer trained under. The library does not read a held out frame
differently from a trained one, and this table is what says so rather than
assuming it.

{{T_SPLIT}}

## The same measurement against the network

The ladder items are their own set: the five question keys of eight operations,
each asked in twenty combinations of frame, wording and page order drawn from
frames the normalizer never trained on. Both systems answer the same 800 rows.

The network is given more than the library, on purpose. It gets labelled pairs
rather than a page, so each example carries the answer structure. It gets
examples of the very operation it will be tested on. It gets an output
vocabulary extended by the eleven operator tokens of `src/norm/optok.py`, whose
rows are appended after every token the checkpoint already had, so it is handed
for free a notation it would otherwise have had to be retrained to have. Its
training keys are disjoint from the five the items ask about, and half of every
batch is replay from the original training file so the run measures acquisition
rather than a trade.

One row per operation, because eight operations averaged into one number would
hide which of them moved. `network best on its own ladder` is the highest strict
score any of that operation's fine tuned checkpoints reached, and `at k` says
how many examples that took.

{{T_LADDER}}

The k curve behind that last column, for the four operations a ladder was run
for. This is the cell where the network has every advantage: k labelled examples of exactly
this operation, tested on the same operation in wordings it did not train on.

{{T_LADDER_OWN}}

The same ladder run again from the family trained network rather than from the
shipped one. That network has already read a thousand examples of other
operations of this family and already has the notation, so k here buys this
operation and nothing else, which is the friendliest reading of the question a
gradient learner can be given.

{{T_SECOND}}

The metric this lane is named for, read off those tables.

{{T_COST}}

## Depth

One acquired operation applied n times over, on directories closed under their
own values so an answer can be fed back in. The library's plan is a list and
execution is a loop over it, so depth 16 costs what depth 1 costs and there is
no step cap in `src/norm/interp.py` to reach. Items are aligned: only the
question keys whose option set stays larger than one at every depth are counted,
so the five rows are the same items and not five different ones.

{{T_DEPTH}}

Past the ceiling. The corpus stops at plan length 48 and the network's own
ladder stops well before that. Running the same acquired operation 64 times over
is a plan of 192 steps when the operation reads two directories and 256 when it
reads three, and the only thing it costs is the time in the last column,
measured over twenty runs of each plan.

{{T_DEEP}}

## Composing two operations from two pages

Two operations, each defined on its own page, the second reading the answers of
the first. The plan is the reads for the first operation and a call, then the
reads for the second and a second call, so six steps when both read two
directories and eight when both read three.

{{T_COMPOSE}}

An accuracy says the network is wrong. This says what it wrote instead. A
composition item needs a structure holding two operator definitions and a plan
that calls two different operators, and the counts are averaged over the
emissions that read back as a structure at all.

{{T_DIAG}}

## The page that contradicts the training

The decisive negative this project already recorded is that the trained
checkpoint followed its training identity on 678 of 678 transposed pages and the
page on 0 of 678. The test here is the same shape. The directory pages are
written exactly as the corpus precedence pages are written, where the first
named page wins, and the definition says the second one does. Both directions
are built, because a system that answers the first directory under both is
following training and a system that answers what the page says under both is
following the page, and one direction alone cannot tell those apart.

{{T_CONTRA}}

The library follows the page in both directions. It does so by construction and
the point of running it is that construction and behaviour are two different
claims. Neither shortcut reader follows the page in both directions: taking the
last matching line agrees with the page whenever the page happens to say the
last directory wins, and disagrees with it otherwise.

## What refuses, and what happens when the page is attacked

A system that answers 1.0000 everywhere is a bug until it has been attacked.
Seven attacks and two controls, all in `results/norm/oneshot/attack.json` and
`report.json`. One of them renames every invented word in the episode at once,
directory names, keys, values, stated words and the operator's own name, so the
renamed episode is the same operation written in a vocabulary nothing has seen.
Another cuts the last case off the definition, which leaves an operation that is
not defined and must be refused rather than completed from anywhere else.

{{T_CONTROLS}}

The two controls are the honest limits. A definition written in the wording mode
the reader was not built for is refused at the definition stage, every time,
because a hand written reader covers the wordings it covers. That is the seam
the architecture puts a network in front of the library to close, and this lane
does not close it. A question naming an operation no page defines is refused at
the plan stage, every time, because a library that has not read a definition has
nothing to run.

## Where the wrong answers went wrong

Three failures are different problems and only the first is a reading problem:
the text was not turned into a structure at all, the interpreter refused the
structure it was given, or a well formed structure was executed and computed
something else. For the library the first column is every refusal, wherever it
happened, and the controls table above says at which step.

{{T_STATES}}

The network's failures are mostly the first and the third. Its commonest
malformed emission names a copy slot the text does not have, which is a stream
that never became a structure. Where it does emit a structure, it usually runs:
the interpreter refuses only a few percent of them, and what comes out is the
answer to a different question. On the control where no operation is defined, it
answers rather than refusing.

## Operations past the shapes the reader was built on

`enumerate_space` was only ever asked for one and two clause operations over two
and three directories, and those are what the reader was written against. These
are three and four clause operations, operations over four and five directories,
and episodes carrying a directory page the question never names, all generated
for the first time by this table. Only the library systems answer these; the
network was decoded on the main and ladder item sets and not on this one.

{{T_STRESS}}

## What each fine tune reached on its own training data

A run whose loss is still falling has not finished learning what it was shown,
so scoring it would measure the budget rather than the network. The small k runs
fit their handful of examples to a loss between 0.00009 and 0.0042 and their
scores are about generalising, not about fitting: a run that has memorised its
one example and still cannot answer a new question about that same operation is
the measurement this lane wanted. The family run at 1500 steps did not: its loss
was still coming down, from 0.36188 to 0.12185, so it was run again for four
times as long and both are reported.

The last column is the check that decides whether any of this means anything. A
network that cannot write back the targets it was trained on is a broken harness
and not a slow learner. The 1500 step family run writes back 0.0050 of its own
training examples, so its scores say nothing; the 6000 step one writes back
0.7500, so the target language, the widened vocabulary and the decoder all work,
and its 0.0000 structure exact on new questions about those same operations is a
statement about acquisition.

{{T_TRAINING}}

## What this does not show

The reader is hand written, so its 1.0000 measures that the definition grammar
is a grammar and that the reader is general over it. It does not measure that
arbitrary English can be normalized: the held out wording mode is refused on
every item, and that is the number to look at before believing anything else
here. The claim this lane supports is narrower and is the architectural one.
Once a page is normalized, using what it says costs one page, holds to a plan of
256 steps, composes, and follows the page against the training. Getting from arbitrary
wording to a normalized page is the network's job, and `src/norm/COMPARE.md`
already measures how well the network does it on the shapes it was trained for.

The neural baseline here is the normalizer of `src/norm/nmodel.py` at size `l`,
45,483,008 parameters, which is the stronger of this project's two networks on
every cell of the main comparison. The corpus checkpoint that scored 678 of 678
on the transposed pages was not run on these items. Its greedy strict score in
`results/norm/compare/report_main.json` has a median of 0.02 over that lane's 60
cells and is at or below 0.1 in 50 of them, so adding it here would not change
what the tables above say, and its serving format is the corpus episode rather
than a page of text, which is a harness this lane does not have.

The two clause space is sampled, not enumerated: 120 of 4,528. The one clause
space is complete.

## How to reproduce

    .venv/bin/python -m src.norm.opitems
    .venv/bin/python -m src.norm.opattack
    .venv/bin/python -m src.norm.oprun
    .venv/bin/python -m src.norm.oprun --items results/norm/oneshot/stress_items.jsonl.gz \
        --out results/norm/oneshot/stress_sys.jsonl.gz
    bash src/norm/drive.sh     # the data, the no gradient run and the first ladder
    bash src/norm/drive2.sh    # the ladder from the family trained network
    bash src/norm/drive3.sh    # the far end of the first ladder
    bash src/norm/drive4.sh    # the family condition, trained four times longer
    bash src/norm/finish.sh    # the diagnostics, the report and this document

`drive2.sh`, `drive3.sh` and `drive4.sh` each wait for the one before them, so
all four can be started at once. Together they are about three hours on one
L40S.

The gates are `src/norm/tests/test_oneshot.py`. Two of them rebuild the item
files into a temporary directory and compare the uncompressed bytes against the
recorded ones, because a change that quietly redrew the items would leave the
report built from two different item sets and the network runs cost hours to
repeat.

{{T_PATHS}}
