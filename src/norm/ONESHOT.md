# Intelligence per example

Built 2026-08-31 13:41 UTC from `results/norm/oneshot/report.json`. Every table below is
rendered by `src/norm/opdoc.py` out of the record files named at the end.
Freshness at build time: 25 record files, none newer than the report of 2026-08-31 13:41 UTC. `opdoc` refuses to build when any record
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
no gradient step, scores 0.0000, 0.0194, 0.1200 and 0.0173 strict on those four
families against floors of 0.3735, 0.3086, 0.3567 and 0.2879, which is below its
own guessing floor in every one. Across the whole item set it is structure exact
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

| operation family               | n   | floor  | L 1 page | L 2 pages | L 4 pages | L structure exact | S1     | S2     | parser |
| ------------------------------ | --- | ------ | -------- | --------- | --------- | ----------------- | ------ | ------ | ------ |
| two directories, one clause    | 110 | 0.3735 | 1.0000   | 1.0000    | 1.0000    | 1.0000            | 0.2636 | 0.2182 | 0.0000 |
| three directories, one clause  | 310 | 0.3086 | 1.0000   | 1.0000    | 1.0000    | 1.0000            | 0.3194 | 0.4129 | 0.0000 |
| two directories, two clauses   | 25  | 0.3567 | 1.0000   | 1.0000    | 1.0000    | 1.0000            | 0.2800 | 0.2400 | 0.0000 |
| three directories, two clauses | 405 | 0.2879 | 1.0000   | 1.0000    | 1.0000    | 1.0000            | 0.3654 | 0.3358 | 0.0000 |

The same items, answered by the network.

| network     | family                         | n   | floor  | strict greedy | strict sampled | structure exact | declined |
| ----------- | ------------------------------ | --- | ------ | ------------- | -------------- | --------------- | -------- |
| no gradient | two directories, one clause    | 110 | 0.3735 | 0.0000        | 0.0091         | 0.0000          | 0.4364   |
| no gradient | three directories, one clause  | 310 | 0.3086 | 0.0194        | 0.0161         | 0.0000          | 0.7323   |
| no gradient | two directories, two clauses   | 25  | 0.3567 | 0.1200        | 0.0000         | 0.0000          | 0.5200   |
| no gradient | three directories, two clauses | 405 | 0.2879 | 0.0173        | 0.0074         | 0.0000          | 0.5852   |

The three library columns are the curve. One page, two pages and four pages of
the same operation give the same number, because the second page carries nothing
the first did not and the library says so by construction: a repeat that agrees
changes nothing and a repeat that disagrees is a refusal.

The extra pages are read, not skipped. The library counts what it took off them,
and a four page episode is four definitions read and one operation stored.

| definition pages served | n   | definition pages the library read | operations it stored |
| ----------------------- | --- | --------------------------------- | -------------------- |
| 1                       | 850 | 1.0000                            | 1.0000               |
| 2                       | 850 | 2.0000                            | 1.0000               |
| 4                       | 850 | 4.0000                            | 1.0000               |

The same items split by the frame the pages are written in, which is the split
the normalizer trained under. The library does not read a held out frame
differently from a trained one, and this table is what says so rather than
assuming it.

| family | frame split | n   | floor  | L strict | S1 strict |
| ------ | ----------- | --- | ------ | -------- | --------- |
| a2c1   | mixed       | 10  | 0.4167 | 1.0000   | 0.3000    |
| a2c1   | mode        | 10  | 0.2667 | 1.0000   | 0.5000    |
| a2c1   | train       | 90  | 0.3806 | 1.0000   | 0.2333    |
| a2c2   | lexicon     | 5   | 0.5000 | 1.0000   | 0.2000    |
| a2c2   | mode        | 5   | 0.2500 | 1.0000   | 0.8000    |
| a2c2   | qframe      | 5   | 0.5000 | 1.0000   | 0.0000    |
| a2c2   | train       | 10  | 0.2667 | 1.0000   | 0.2000    |
| a3c1   | lexicon     | 15  | 0.3889 | 1.0000   | 0.3333    |
| a3c1   | mixed       | 15  | 0.2333 | 1.0000   | 0.4667    |
| a3c1   | mode        | 35  | 0.3143 | 1.0000   | 0.2571    |
| a3c1   | qframe      | 35  | 0.3071 | 1.0000   | 0.2571    |
| a3c1   | train       | 210 | 0.3075 | 1.0000   | 0.3286    |
| a3c2   | lexicon     | 45  | 0.3000 | 1.0000   | 0.3556    |
| a3c2   | mixed       | 25  | 0.3167 | 1.0000   | 0.4400    |
| a3c2   | mode        | 40  | 0.3167 | 1.0000   | 0.4000    |
| a3c2   | qframe      | 35  | 0.3214 | 1.0000   | 0.4571    |
| a3c2   | train       | 260 | 0.2740 | 1.0000   | 0.3423    |

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

| operation    | n   | floor  | library | library exact | S1     | S2     | network no gradient | network family trained | network best on its own ladder | at k |
| ------------ | --- | ------ | ------- | ------------- | ------ | ------ | ------------------- | ---------------------- | ------------------------------ | ---- |
| acq/a2c1/2   | 100 | 0.5000 | 1.0000  | 1.0000        | 0.2000 | 0.2000 | 0.0100              | -                      | 0.3300                         | 64   |
| acq/a2c1/5   | 100 | 0.5000 | 1.0000  | 1.0000        | 0.0000 | 0.0000 | 0.0100              | -                      | -                              | -    |
| acq/a2c2/157 | 100 | 0.3333 | 1.0000  | 1.0000        | 0.0000 | 0.6000 | 0.0500              | -                      | -                              | -    |
| acq/a2c2/187 | 100 | 0.5000 | 1.0000  | 1.0000        | 0.0000 | 0.0000 | 0.0200              | -                      | -                              | -    |
| acq/a3c1/26  | 100 | 0.3333 | 1.0000  | 1.0000        | 0.2000 | 0.2000 | 0.0400              | -                      | 0.2600                         | 64   |
| acq/a3c1/28  | 100 | 0.2500 | 1.0000  | 1.0000        | 0.0000 | 0.8000 | 0.0300              | -                      | -                              | -    |
| acq/a3c2/144 | 100 | 0.2500 | 1.0000  | 1.0000        | 0.0000 | 0.0000 | 0.0300              | -                      | 0.0200                         | 1    |
| acq/a3c2/146 | 100 | 0.2500 | 1.0000  | 1.0000        | 0.2000 | 0.8000 | 0.0000              | -                      | -                              | -    |

The k curve behind that last column, for the four operations a ladder was run
for. This is the cell where the network has every advantage: k labelled examples of exactly
this operation, tested on the same operation in wordings it did not train on.

| pool         | operation    | k=1    | k=2    | k=4    | k=16   | k=64   | k=256 | k=1024 | no gradient |
| ------------ | ------------ | ------ | ------ | ------ | ------ | ------ | ----- | ------ | ----------- |
| acq_a2c1_2   | acq/a2c1/2   | 0.0000 | 0.0000 | 0.0100 | 0.1000 | 0.3300 | -     | -      | 0.0100      |
| acq_a3c1_26  | acq/a3c1/26  | 0.0300 | 0.0300 | 0.0300 | 0.0500 | 0.2600 | -     | -      | 0.0400      |
| acq_a3c2_144 | acq/a3c2/144 | 0.0200 | 0.0100 | 0.0100 | 0.0100 | -      | -     | -      | 0.0300      |
| acq_a2c2_157 | acq/a2c2/157 | -      | -      | -      | -      | -      | -     | -      | 0.0500      |

The same ladder run again from the family trained network rather than from the
shipped one. That network has already read a thousand examples of other
operations of this family and already has the notation, so k here buys this
operation and nothing else, which is the friendliest reading of the question a
gradient learner can be given.

| pool         | operation    | k=0 (family trained) | k=1 | k=2 | k=4 |
| ------------ | ------------ | -------------------- | --- | --- | --- |
| acq_a2c1_2   | acq/a2c1/2   | -                    | -   | -   | -   |
| acq_a3c1_26  | acq/a3c1/26  | -                    | -   | -   | -   |
| acq_a3c2_144 | acq/a3c2/144 | -                    | -   | -   | -   |
| acq_a2c2_157 | acq/a2c2/157 | -                    | -   | -   | -   |

The metric this lane is named for, read off those tables.

| system  | operation             | best strict reached | floor  | examples to clear the floor | examples to reach 0.9000 |
| ------- | --------------------- | ------------------- | ------ | --------------------------- | ------------------------ |
| library | one page, no examples | 1.0000              | 0.3646 | 0                           | 0                        |
| network | acq/a2c1/2            | 0.3300              | 0.5000 | not within 64               | not within 64            |
| network | acq/a3c1/26           | 0.2600              | 0.3333 | not within 64               | not within 64            |
| network | acq/a3c2/144          | 0.0200              | 0.2500 | not within 16               | not within 16            |
| network | acq/a2c2/157          | -                   | 0.3333 | not within 0                | not within 0             |

## Depth

One acquired operation applied n times over, on directories closed under their
own values so an answer can be fed back in. The library's plan is a list and
execution is a loop over it, so depth 16 costs what depth 1 costs and there is
no step cap in `src/norm/interp.py` to reach. Items are aligned: only the
question keys whose option set stays larger than one at every depth are counted,
so the five rows are the same items and not five different ones.

| applications | n   | floor  | L strict | S1     | S2     | network no gradient greedy | network no gradient sampled | network family trained greedy | network family trained sampled |
| ------------ | --- | ------ | -------- | ------ | ------ | -------------------------- | --------------------------- | ----------------------------- | ------------------------------ |
| 1            | 555 | 0.2504 | 1.0000   | 0.3820 | 0.4378 | 0.0072                     | 0.0054                      | -                             | -                              |
| 2            | 555 | 0.3090 | 1.0000   | 0.1315 | 0.1477 | 0.0180                     | 0.0180                      | -                             | -                              |
| 4            | 555 | 0.3589 | 1.0000   | 0.1820 | 0.2162 | 0.0288                     | 0.0288                      | -                             | -                              |
| 8            | 555 | 0.3629 | 1.0000   | 0.1351 | 0.1640 | 0.0144                     | 0.0126                      | -                             | -                              |
| 16           | 555 | 0.3629 | 1.0000   | 0.1910 | 0.2288 | 0.0090                     | 0.0054                      | -                             | -                              |

Past the ceiling. The corpus stops at plan length 48 and the network's own
ladder stops well before that. Running the same acquired operation 64 times over
is a plan of 192 steps when the operation reads two directories and 256 when it
reads three, and the only thing it costs is the time in the last column,
measured over twenty runs of each plan.

| applications | n  | floor  | L strict | L structure exact | S1     | S2     | microseconds to run the plan |
| ------------ | -- | ------ | -------- | ----------------- | ------ | ------ | ---------------------------- |
| 1            | 26 | 0.1881 | 1.0000   | 1.0000            | 0.3462 | 0.5000 | 11.4                         |
| 2            | 26 | 0.2430 | 1.0000   | 1.0000            | 0.1923 | 0.1538 | 20.7                         |
| 4            | 26 | 0.3046 | 1.0000   | 1.0000            | 0.2308 | 0.1538 | 39.6                         |
| 8            | 26 | 0.3046 | 1.0000   | 1.0000            | 0.1923 | 0.1538 | 79.1                         |
| 16           | 26 | 0.3046 | 1.0000   | 1.0000            | 0.2308 | 0.1538 | 153.9                        |
| 32           | 26 | 0.3046 | 1.0000   | 1.0000            | 0.1923 | 0.1538 | 304.7                        |
| 48           | 26 | 0.3046 | 1.0000   | 1.0000            | 0.1538 | 0.1538 | 452.2                        |
| 64           | 26 | 0.3046 | 1.0000   | 1.0000            | 0.2308 | 0.1538 | 612.5                        |

## Composing two operations from two pages

Two operations, each defined on its own page, the second reading the answers of
the first. The plan is the reads for the first operation and a call, then the
reads for the second and a second call, so six steps when both read two
directories and eight when both read three.

| system                         | n   | floor  | strict | lenient | declined | structure exact |
| ------------------------------ | --- | ------ | ------ | ------- | -------- | --------------- |
| library, two pages             | 240 | 0.3915 | 1.0000 | 1.0000  | 0.0000   | 1.0000          |
| shortcut, first line           | 240 | 0.3915 | 0.1375 | 0.1375  | 0.0000   | -               |
| shortcut, last line            | 240 | 0.3915 | 0.1792 | 0.1792  | 0.0000   | -               |
| corpus parser                  | 240 | 0.3915 | 0.0000 | 0.0000  | 1.0000   | -               |
| network, no gradient (greedy)  | 240 | 0.3915 | 0.0125 | 0.0125  | 0.5125   | 0.0000          |
| network, no gradient (sampled) | 240 | 0.3915 | 0.0167 | 0.0167  | 0.5208   | 0.0000          |

An accuracy says the network is wrong. This says what it wrote instead. A
composition item needs a structure holding two operator definitions and a plan
that calls two different operators, and the counts are averaged over the
emissions that read back as a structure at all.

| row                  | n   | malformed | operator definitions | calls  | distinct operators called | directories | plan steps |
| -------------------- | --- | --------- | -------------------- | ------ | ------------------------- | ----------- | ---------- |
| what the item needs  | 240 | -         | 2.0000               | 2.0000 | 2.0000                    | 5.5370      | 7.5370     |
| network, no gradient | 135 | 105       | 0.0000               | 0.0000 | 0.0000                    | 2.3630      | 3.7630     |

## The page that contradicts the training

The decisive negative this project already recorded is that the trained
checkpoint followed its training identity on 678 of 678 transposed pages and the
page on 0 of 678. The test here is the same shape. The directory pages are
written exactly as the corpus precedence pages are written, where the first
named page wins, and the definition says the second one does. Both directions
are built, because a system that answers the first directory under both is
following training and a system that answers what the page says under both is
following the page, and one direction alone cannot tell those apart.

| page says   | system                         | n   | floor  | follows page | follows training | neither |
| ----------- | ------------------------------ | --- | ------ | ------------ | ---------------- | ------- |
| page_first  | library                        | 230 | 0.2703 | 1.0000       | 1.0000           | 0.0000  |
| page_first  | shortcut, first line           | 230 | 0.2703 | 1.0000       | 1.0000           | 0.0000  |
| page_first  | shortcut, last line            | 230 | 0.2703 | 0.0000       | 0.0000           | 1.0000  |
| page_first  | corpus parser                  | 230 | 0.2703 | 0.0000       | 0.0000           | 1.0000  |
| page_first  | network, no gradient (greedy)  | 230 | 0.2703 | 0.0000       | 0.0000           | 1.0000  |
| page_first  | network, no gradient (sampled) | 230 | 0.2703 | 0.0000       | 0.0000           | 1.0000  |
| page_second | library                        | 230 | 0.2754 | 1.0000       | 0.0000           | 0.0000  |
| page_second | shortcut, first line           | 230 | 0.2754 | 0.0000       | 0.9087           | 0.0913  |
| page_second | shortcut, last line            | 230 | 0.2754 | 1.0000       | 0.0000           | 0.0000  |
| page_second | corpus parser                  | 230 | 0.2754 | 0.0000       | 0.0000           | 1.0000  |
| page_second | network, no gradient (greedy)  | 230 | 0.2754 | 0.0130       | 0.0000           | 0.9870  |
| page_second | network, no gradient (sampled) | 230 | 0.2754 | 0.0130       | 0.0000           | 0.9870  |

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

| check                                       | n   | rate   | where                                  |
| ------------------------------------------- | --- | ------ | -------------------------------------- |
| definition in the held out wording          | 120 | 1.0000 | definition 120                         |
| question names no defined operation         | 120 | 1.0000 | plan 120                               |
| last case of the definition moved           | 300 | 1.0000 | followed the new page, 159 golds moved |
| definition page removed                     | 300 | 1.0000 | plan 300                               |
| operation renamed on page and question      | 300 | 1.0000 | same answer                            |
| one directory row changed                   | 294 | 1.0000 | followed the new row, 142 golds moved  |
| every invented word renamed                 | 300 | 1.0000 | answered the renamed gold              |
| the last case cut off the definition        | 300 | 1.0000 | definition 300                         |
| a second operation the question never names | 300 | 1.0000 | same answer                            |

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

| system               | condition | n    | no structure produced | interpreter refused | ran the wrong structure | ran the right one |
| -------------------- | --------- | ---- | --------------------- | ------------------- | ----------------------- | ----------------- |
| library              | acq       | 2550 | 0.0000                | 0.0000              | 0.0000                  | 1.0000            |
| library              | depth     | 3246 | 0.0000                | 0.0000              | 0.0000                  | 1.0000            |
| library              | compose   | 240  | 0.0000                | 0.0000              | 0.0000                  | 1.0000            |
| library              | contra    | 460  | 0.0000                | 0.0000              | 0.0000                  | 1.0000            |
| library              | held_mode | 120  | 1.0000                | 0.0000              | 0.0000                  | 0.0000            |
| library              | unstated  | 120  | 1.0000                | 0.0000              | 0.0000                  | 0.0000            |
| network, no gradient | acq       | 2550 | 0.5541                | 0.0255              | 0.4047                  | 0.0157            |
| network, no gradient | depth     | 3246 | 0.4421                | 0.0499              | 0.4920                  | 0.0160            |
| network, no gradient | compose   | 240  | 0.4375                | 0.0750              | 0.4750                  | 0.0125            |
| network, no gradient | contra    | 460  | 0.2630                | 0.0370              | 0.6935                  | 0.0065            |
| network, no gradient | held_mode | 120  | 0.0333                | 0.1000              | 0.8167                  | 0.0500            |
| network, no gradient | unstated  | 120  | 0.3750                | 0.0583              | 0.5667                  | 0.0000            |

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

| operation                            | n   | floor  | L strict | L structure exact | S1     | S2     | parser |
| ------------------------------------ | --- | ------ | -------- | ----------------- | ------ | ------ | ------ |
| three clauses                        | 120 | 0.2975 | 1.0000   | 1.0000            | 0.4167 | 0.4083 | 0.0000 |
| four clauses                         | 120 | 0.2792 | 1.0000   | 1.0000            | 0.5000 | 0.4333 | 0.0000 |
| four directories                     | 120 | 0.2854 | 1.0000   | 1.0000            | 0.3583 | 0.4583 | 0.0000 |
| five directories                     | 120 | 0.2727 | 1.0000   | 1.0000            | 0.4167 | 0.3667 | 0.0000 |
| a directory the question never names | 120 | 0.3050 | 1.0000   | 1.0000            | 0.4417 | 0.0000 | 0.0000 |

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
on the transposed pages was not run on these items; it is at or below 0.1 strict
on most cells of `src/norm/COMPARE.md` and adding it would not change what the
tables above say.

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
    .venv/bin/python -m src.norm.opdiag --vocab base --only compose \
        --out results/norm/oneshot/diag_base_compose.json
    .venv/bin/python -m src.norm.opdiag --ckpt results/norm/oneshot/ft_family.pt \
        --vocab ext --only compose --out results/norm/oneshot/diag_family_compose.json
    .venv/bin/python -m src.norm.opreport
    .venv/bin/python -m src.norm.opdoc

`drive2.sh` and `drive3.sh` each wait for the one before it, so all three can be
started at once. Together they are about two and a half hours on one L40S.

The gates are `src/norm/tests/test_oneshot.py`. Two of them rebuild the item
files into a temporary directory and compare the uncompressed bytes against the
recorded ones, because a change that quietly redrew the items would leave the
report built from two different item sets and the network runs cost hours to
repeat.

| record                    | path                                                                                      |
| ------------------------- | ----------------------------------------------------------------------------------------- |
| attack                    | /home/ec2-user/decoupled-reasoner/results/norm/oneshot/attack.json                        |
| diag_base_compose         | /home/ec2-user/decoupled-reasoner/results/norm/oneshot/diag_base_compose.json             |
| items                     | /home/ec2-user/decoupled-reasoner/results/norm/oneshot/items.jsonl.gz                     |
| ladder_items              | /home/ec2-user/decoupled-reasoner/results/norm/oneshot/ladder_items.jsonl.gz              |
| ladder_sys                | /home/ec2-user/decoupled-reasoner/results/norm/oneshot/ladder_sys.jsonl.gz                |
| n_acq_a2c1_2_k16_ladder   | /home/ec2-user/decoupled-reasoner/results/norm/oneshot/n_acq_a2c1_2_k16_ladder.jsonl.gz   |
| n_acq_a2c1_2_k1_ladder    | /home/ec2-user/decoupled-reasoner/results/norm/oneshot/n_acq_a2c1_2_k1_ladder.jsonl.gz    |
| n_acq_a2c1_2_k2_ladder    | /home/ec2-user/decoupled-reasoner/results/norm/oneshot/n_acq_a2c1_2_k2_ladder.jsonl.gz    |
| n_acq_a2c1_2_k4_ladder    | /home/ec2-user/decoupled-reasoner/results/norm/oneshot/n_acq_a2c1_2_k4_ladder.jsonl.gz    |
| n_acq_a2c1_2_k64_ladder   | /home/ec2-user/decoupled-reasoner/results/norm/oneshot/n_acq_a2c1_2_k64_ladder.jsonl.gz   |
| n_acq_a3c1_26_k16_ladder  | /home/ec2-user/decoupled-reasoner/results/norm/oneshot/n_acq_a3c1_26_k16_ladder.jsonl.gz  |
| n_acq_a3c1_26_k1_ladder   | /home/ec2-user/decoupled-reasoner/results/norm/oneshot/n_acq_a3c1_26_k1_ladder.jsonl.gz   |
| n_acq_a3c1_26_k2_ladder   | /home/ec2-user/decoupled-reasoner/results/norm/oneshot/n_acq_a3c1_26_k2_ladder.jsonl.gz   |
| n_acq_a3c1_26_k4_ladder   | /home/ec2-user/decoupled-reasoner/results/norm/oneshot/n_acq_a3c1_26_k4_ladder.jsonl.gz   |
| n_acq_a3c1_26_k64_ladder  | /home/ec2-user/decoupled-reasoner/results/norm/oneshot/n_acq_a3c1_26_k64_ladder.jsonl.gz  |
| n_acq_a3c2_144_k16_ladder | /home/ec2-user/decoupled-reasoner/results/norm/oneshot/n_acq_a3c2_144_k16_ladder.jsonl.gz |
| n_acq_a3c2_144_k1_ladder  | /home/ec2-user/decoupled-reasoner/results/norm/oneshot/n_acq_a3c2_144_k1_ladder.jsonl.gz  |
| n_acq_a3c2_144_k2_ladder  | /home/ec2-user/decoupled-reasoner/results/norm/oneshot/n_acq_a3c2_144_k2_ladder.jsonl.gz  |
| n_acq_a3c2_144_k4_ladder  | /home/ec2-user/decoupled-reasoner/results/norm/oneshot/n_acq_a3c2_144_k4_ladder.jsonl.gz  |
| n_base_l                  | /home/ec2-user/decoupled-reasoner/results/norm/oneshot/n_base_l.jsonl.gz                  |
| n_base_l_ladder           | /home/ec2-user/decoupled-reasoner/results/norm/oneshot/n_base_l_ladder.jsonl.gz           |
| n_k0_ladder               | /home/ec2-user/decoupled-reasoner/results/norm/oneshot/n_k0_ladder.jsonl.gz               |
| stress_items              | /home/ec2-user/decoupled-reasoner/results/norm/oneshot/stress_items.jsonl.gz              |
| stress_sys                | /home/ec2-user/decoupled-reasoner/results/norm/oneshot/stress_sys.jsonl.gz                |
| sys                       | /home/ec2-user/decoupled-reasoner/results/norm/oneshot/sys.jsonl.gz                       |
